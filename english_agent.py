import os
import json
import datetime
import re
import google.generativeai as genai

# 1. 환경설정 및 게시판 데이터 가져오기
GEMINI_KEY = os.getenv("SCIENCE_KEY")
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# 아빠가 적은 제목 (예: "Lesson 2")
issue_title = os.getenv("ISSUE_TITLE", "Lesson 2")
issue_body = os.getenv("ISSUE_BODY", "No data")

today_str = datetime.date.today().strftime("%Y년 %m월 %d일")
html_filename = f"english_{datetime.date.today().strftime('%Y%m%d')}.html"

# 2. 교재 지식 창고
curriculum_db = {
    "Lesson 2": {
        "title": "Such an Awesome Guitarist!",
        "grammar": "부가의문문 (isn't it?, don't you?)",
        "key_patterns": ["Do you play any musical instruments?", "Playing the guitar must be fun, isn't it?", "Do you have a moment?"],
        "vocabulary": ["musical", "awesome", "guitar", "perform", "band", "exciting"]
    },
    "Lesson 3": {
        "title": "Spending Time with Grandparents",
        "grammar": "빈도부사 (usually, often, sometimes, rarely, never)의 위치와 쓰임",
        "key_patterns": ["What do you usually do on the weekend?", "I rarely read novels."],
        "vocabulary": ["weekend", "trouble", "grandparents", "novel", "often", "rarely", "visit"]
    },
    "Lesson 4": {
        "title": "How Great the Idea Is!",
        "grammar": "감탄문과 미래시제 (will)",
        "key_patterns": ["What an exciting game that was!", "I will go on a trip."],
        "vocabulary": ["moving", "performance", "fantastic", "believe", "enjoy"]
    }
}

# 3. 타임머신 로직 (숫자를 추출해서 현재 레슨과 다음 레슨 분리!)
match = re.search(r'\d+', issue_title)
current_lesson_num = int(match.group()) if match else 2
next_lesson_num = current_lesson_num + 1

current_lesson_key = f"Lesson {current_lesson_num}"
next_lesson_key = f"Lesson {next_lesson_num}"

current_info = curriculum_db.get(current_lesson_key, curriculum_db["Lesson 2"])
next_info = curriculum_db.get(next_lesson_key, curriculum_db["Lesson 3"])

# 4. Gemini 프롬프트 (분리된 정보 전달 & 10문제 강제 할당)
prompt = f"""
너는 중학교 1학년 다니엘의 1:1 영어 코치야.
방금 끝난 수업({current_lesson_key})의 복습과, 다음 수업({next_lesson_key})의 예습 자료를 만들어야 해.

[방금 끝난 수업 (복습 및 10문제 출제용) : {current_lesson_key}]
- 주제: {current_info['title']}
- 핵심 문법: {current_info['grammar']}
- 대화록 및 피드백: {issue_body}

[다음 수업 (예습용) : {next_lesson_key}]
- 주제: {next_info['title']}
- 핵심 문법: {next_info['grammar']}
- 주요 패턴: {next_info['key_patterns']}

반드시 아래 JSON 형식에 맞춰서 응답해. 쌍따옴표 안에 순수 텍스트만 넣어.
'custom_quizzes' 배열은 방금 끝난 수업({current_lesson_key})의 문법과 단어를 활용해서 반드시 10개의 영작/빈칸 문제를 꽉 채워!
{{
  "review_original": "대화록에서 다니엘이 틀렸거나 어색하게 말한 문장 1개",
  "review_better": "선생님이 교정해준 완벽한 문장",
  "review_advice": "다니엘, [Original] 대신 [Better]처럼 말하면 자연스러워! 형식의 아빠 조언",
  "preview_english": "다음 수업({next_lesson_key}) 문법/패턴을 활용하여 다음 수업 때 써먹을 수 있는 완벽한 문장 1개",
  "preview_korean": "위 예습 문장의 한국어 뜻",
  "quiz_korean": "영작 조립 게임에 쓸 review_better 문장의 한국어 뜻",
  "quiz_words": "['I', 'started', 'this', 'hobby', 'ago.'] 처럼 조립할 단어들의 배열 문자열",
  "quiz_answer": "영작 조립 게임 정답 문장",
  "custom_quizzes": [
    {{"q": "그는 취미에 많은 시간을 보낸다 (영작해 보세요)", "hint": "spend / pursuing", "a": "He spends a lot of time pursuing his hobby."}}
  ]
}}
"""

try:
    res = model.generate_content(prompt)
    clean_text = res.text.replace('```json', '').replace('```', '').strip()
    data = json.loads(clean_text)

    # 파이썬 리스트 변환
    import ast
    quiz_words_list = ast.literal_eval(data['quiz_words'])
    js_words_array = json.dumps(quiz_words_list)
    js_quizzes = json.dumps(data.get('custom_quizzes', []))

    # 5. HTML 생성 (타이핑 퀴즈 UI 완벽 적용)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>다니엘의 Daily English</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Nanum+Square+Round:wght@400;700;800&display=swap');
            body {{ font-family: 'Nanum Square Round', sans-serif; background: #f8fafd; color: #333; margin: 0; padding: 20px; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: auto; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .card {{ background: white; border-radius: 20px; padding: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 30px; }}
            .tag {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; margin-bottom: 10px; font-size: 0.9em; }}
            .tag-review {{ background: #e74c3c; }} .tag-preview {{ background: #3498db; }} .tag-quiz {{ background: #9b59b6; }}
            
            /* 타이핑 퀴즈 UI 디자인 (아빠가 주신 이미지 스타일 적용!) */
            .quiz-box {{ border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; margin-bottom: 15px; background: #fafafa; }}
            .quiz-q {{ font-weight: 800; font-size: 1.1em; text-align: center; margin-bottom: 15px; color: #2c3e50; }}
            .quiz-input {{ width: 100%; padding: 15px; font-size: 1.1em; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; margin-bottom: 15px; }}
            .quiz-hint-box {{ display: none; background: #f1f2f6; padding: 10px; border-left: 4px solid #e74c3c; margin-bottom: 15px; font-weight: bold; color: #555; }}
            .btn-group {{ display: flex; justify-content: center; gap: 10px; }}
            .btn-action {{ padding: 10px 20px; border: 1px solid #999; background: white; border-radius: 5px; cursor: pointer; font-weight: bold; transition: 0.2s; }}
            .btn-action:hover {{ background: #eee; }}
            .quiz-result {{ display: none; text-align: center; margin-top: 15px; font-weight: bold; font-size: 1.1em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="color: #2c3e50;">📚 다니엘의 10분 영어 스낵</h1>
                <p>{today_str} | 복습: {current_lesson_key} / 예습: {next_lesson_key}</p>
            </div>

            <div class="card">
                <span class="tag tag-review">Part 1. 오답 노트 ({current_lesson_key})</span>
                <h2>어제 놓친 문장, 오늘 완벽하게!</h2>
                <p style="color: #7f8c8d; text-decoration: line-through;">❌ {data['review_original']}</p>
                <p style="font-size: 1.3em; font-weight: bold; color: #2ecc71;">✅ {data['review_better']}</p>
                <p style="background: #f8d7da; padding: 10px; border-radius: 8px;">👨‍🏫 아빠의 조언: {data['review_advice']}</p>
            </div>

            <div class="card">
                <span class="tag tag-preview">Part 2. 다음 수업 치트키 ({next_lesson_key})</span>
                <h2>선생님을 깜짝 놀라게 할 한마디! ({next_info['title']})</h2>
                <div style="background: #fff9e6; padding: 15px; border-left: 5px solid #f1c40f; border-radius: 8px;">
                    <p style="font-size: 1.3em; font-weight: bold; color: #2980b9;">"{data['preview_english']}"</p>
                    <p style="color: #7f8c8d; margin-top: 0;">뜻: {data['preview_korean']}</p>
                </div>
            </div>

            <div class="card">
                <span class="tag tag-quiz">Part 3. 오늘의 영작 훈련</span>
                <h2 style="text-align: center;">오늘의 주요표현을 활용하여 영작해 보세요.</h2>
                <div id="quiz-container"></div>
            </div>
        </div>

        <script>
            const quizzes = {js_quizzes};
            const container = document.getElementById('quiz-container');

            quizzes.forEach((quiz, index) => {{
                // 각 퀴즈마다 HTML 박스 생성
                const html = `
                    <div class="quiz-box">
                        <div class="quiz-q">${{quiz.q}}</div>
                        <input type="text" id="input_${{index}}" class="quiz-input" placeholder="your text here">
                        
                        <div id="hint_${{index}}" class="quiz-hint-box">
                            📢 힌트: ${{quiz.hint}}
                        </div>
                        
                        <div class="btn-group">
                            <button class="btn-action" onclick="document.getElementById('hint_${{index}}').style.display='block'">힌트듣기</button>
                            <button class="btn-action" onclick="checkQuiz(${{index}}, '${{quiz.a.replace(/'/g, "\\'")}}')">정답확인</button>
                        </div>
                        
                        <div id="result_${{index}}" class="quiz-result"></div>
                    </div>
                `;
                container.innerHTML += html;
            }});

            // 정답 체크 함수
            function checkQuiz(index, correctAnswer) {{
                const userAnswer = document.getElementById(`input_${{index}}`).value.trim();
                const resultDiv = document.getElementById(`result_${{index}}`);
                
                resultDiv.style.display = 'block';
                // 소문자, 마침표 등 무시하고 대략 맞는지 검사
                const cleanUser = userAnswer.toLowerCase().replace(/[.,!?]/g, '');
                const cleanCorrect = correctAnswer.toLowerCase().replace(/[.,!?]/g, '');
                
                if (cleanUser === cleanCorrect) {{
                    resultDiv.style.color = '#2ecc71';
                    resultDiv.innerHTML = "🎉 완벽해! 정답이야!";
                }} else {{
                    resultDiv.style.color = '#e74c3c';
                    resultDiv.innerHTML = `🤔 아쉽네. 정답은 <b>${{correctAnswer}}</b> 이야!`;
                }}
            }}
        </script>
    </body>
    </html>
    """

    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ {html_filename} 생성 완료!")

except Exception as e:
    print(f"❌ 에러 발생: {e}")