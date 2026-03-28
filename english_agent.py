import os
import json
import datetime
import google.generativeai as genai

# 1. 환경설정 및 게시판 데이터 가져오기
GEMINI_KEY = os.getenv("SCIENCE_KEY")
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

issue_title = os.getenv("ISSUE_TITLE", "Lesson 3")
issue_body = os.getenv("ISSUE_BODY", "No data")

today_str = datetime.date.today().strftime("%Y년 %m월 %d일")
html_filename = f"english_{datetime.date.today().strftime('%Y%m%d')}.html"

# 2. 교재 지식 창고
curriculum_db = {
    "Lesson 2": {
        "title": "Such an Awesome Guitarist!",
        "grammar": "부가의문문 (isn't it?, don't you?)",
        "key_patterns": ["You like pizza, don't you?", "Do you have a moment?"]
    },
    "Lesson 3": {
        "title": "Spending Time with Grandparents",
        "grammar": "빈도부사 (usually, often, rarely, never)",
        "key_patterns": ["What do you usually do after school?", "I never sleep late."]
    },
    "Lesson 4": {
        "title": "How Great the Idea Is!",
        "grammar": "감탄문과 미래시제 (will)",
        "key_patterns": ["What an exciting game that was!", "I will go on a trip."]
    }
}

lesson_info = curriculum_db.get(issue_title, curriculum_db.get("Lesson 3"))

# 3. Gemini 프롬프트 (데이터 구조를 아주 평면적이고 직관적으로 수정)
prompt = f"""
너는 중학교 1학년 학생의 1:1 영어 코치야.
다음 [선생님 피드백 및 대화록]과 [이번 주 교과서 진도]를 바탕으로 복습/예습 리포트를 만들어줘.

[이번 주 교과서 진도: {issue_title}]
- 주제: {lesson_info['title']}
- 핵심 문법: {lesson_info['grammar']}
- 주요 패턴: {lesson_info['key_patterns']}

[선생님 피드백 및 대화록]
{issue_body}

반드시 아래 JSON 형식표에 맞춰서 응답해. 쌍따옴표 안에 순수한 문자열(텍스트)만 들어가야 해. 객체나 배열을 중첩하지 마.
{{
  "review_original": "대화록에서 학생이 틀렸거나 어색하게 말한 영어 문장 1개",
  "review_better": "선생님이 교정해준 완벽한 영어 문장",
  "review_advice": "다니엘, [Original] 대신 [Better]처럼 말하면 훨씬 자연스러워! 처럼 아빠가 해주는 다정한 한국어 조언 1문장",
  "preview_english": "이번 주 교과서 진도를 활용해서, 다음 화상 수업 때 선생님께 써먹을 수 있는 완벽한 영어 문장 1개",
  "preview_korean": "위 preview_english 문장의 한국어 뜻",
  "quiz_korean": "영작 퀴즈로 낼 review_better 문장의 한국어 뜻",
  "quiz_words": "['I', 'started', 'this', 'hobby', 'three', 'years', 'ago.'] 처럼 조립할 영어 단어들을 섞어서 만든 배열 문자열 (반드시 대괄호와 따옴표 포함한 형태)",
  "quiz_answer": "영작 퀴즈의 정답이 되는 완벽한 영어 문장"
}}
"""

try:
    res = model.generate_content(prompt)
    clean_text = res.text.replace('```json', '').replace('```', '').strip()
    data = json.loads(clean_text)

    # 문자열로 들어온 배열 데이터를 실제 파이썬 리스트로 변환
    import ast
    quiz_words_list = ast.literal_eval(data['quiz_words'])
    
    # 자바스크립트 배열 형태로 변환 (웹사이트 게임용)
    js_words_array = json.dumps(quiz_words_list)

    # 4. 진짜 돌아가는 웹사이트용 HTML + JavaScript 생성
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>다니엘의 Daily English</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Nanum+Square+Round:wght@400;700;800&display=swap');
            body {{ font-family: 'Nanum Square Round', sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 20px; }}
            .container {{ max-width: 800px; margin: auto; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .header h1 {{ color: #2c3e50; font-size: 2.2em; }}
            .card {{ background: white; border-radius: 20px; padding: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 30px; line-height: 1.6; }}
            .tag {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; margin-bottom: 15px; font-size: 0.9em; }}
            .tag-review {{ background: #e74c3c; }}
            .tag-preview {{ background: #3498db; }}
            .comment {{ background: #fff9e6; padding: 15px; border-left: 5px solid #f1c40f; border-radius: 0 10px 10px 0; margin-top: 15px; }}
            
            /* 영작 게임 디자인 */
            .word-block {{ display: inline-block; padding: 10px 18px; margin: 5px; background: white; border: 2px solid #3498db; border-radius: 12px; cursor: pointer; font-weight: bold; color: #2980b9; transition: 0.2s; box-shadow: 0 4px 6px rgba(0,0,0,0.05); user-select: none; }}
            .word-block:hover {{ transform: translateY(-2px); background: #ebf5fb; }}
            #sentence-zone {{ min-height: 60px; padding: 20px; background: #ecf0f1; border-radius: 15px; margin-bottom: 20px; display: flex; flex-wrap: wrap; align-items: center; border: 2px dashed #bdc3c7; }}
            #word-bank {{ display: flex; flex-wrap: wrap; justify-content: center; margin-bottom: 20px; }}
            .btn-check {{ display: block; width: 100%; padding: 15px; background: #2ecc71; color: white; border: none; border-radius: 12px; font-size: 1.1em; font-weight: bold; cursor: pointer; transition: 0.3s; }}
            .btn-check:hover {{ background: #27ae60; }}
            #result-msg {{ text-align: center; font-weight: bold; margin-top: 15px; font-size: 1.1em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📚 다니엘의 10분 영어 스낵</h1>
                <p>{today_str} | {issue_title}: {lesson_info['title']}</p>
            </div>

            <div class="card">
                <span class="tag tag-review">Part 1. 오답 노트</span>
                <h2 style="margin-top:0;">어제 놓친 문장, 오늘 완벽하게!</h2>
                <p style="color: #7f8c8d; text-decoration: line-through;">Original: {data['review_original']}</p>
                <p style="font-size: 1.3em; font-weight: bold; color: #2c3e50;">✨ Better: {data['review_better']}</p>
                <p style="background: #f8d7da; padding: 10px; border-radius: 8px;">👨‍🏫 아빠의 조언: {data['review_advice']}</p>
            </div>

            <div class="card">
                <span class="tag tag-preview">Part 2. 다음 수업 치트키</span>
                <h2 style="margin-top:0;">선생님을 깜짝 놀라게 할 한마디!</h2>
                <div class="comment">
                    <p style="font-size: 1.3em; font-weight: bold; color: #2980b9; margin-bottom: 5px;">"{data['preview_english']}"</p>
                    <p style="color: #7f8c8d; margin-top: 0;">뜻: {data['preview_korean']}</p>
                </div>
            </div>

            <div class="card">
                <h2>🎮 Part 3. 오늘의 영작 짐(Gym)</h2>
                <p>아래 단어들을 클릭해서 올바른 순서로 문장을 완성해 봐!</p>
                <p style="font-weight: bold; text-align: center; color: #e67e22;">목표: "{data['quiz_korean']}"</p>
                
                <div id="sentence-zone"></div>
                <div id="word-bank"></div>
                
                <button class="btn-check" onclick="checkAnswer()">정답 확인하기</button>
                <p id="result-msg"></p>
            </div>
        </div>

        <script>
            // 파이썬이 생성한 단어 리스트와 정답을 자바스크립트로 전달!
            const words = {js_words_array};
            const correctAnswer = "{data['quiz_answer']}";
            
            const bank = document.getElementById('word-bank');
            const zone = document.getElementById('sentence-zone');
            const msg = document.getElementById('result-msg');

            // 단어 버튼 생성
            words.forEach(word => {{
                let btn = document.createElement('div');
                btn.className = 'word-block';
                btn.innerText = word;
                btn.onclick = () => moveWord(btn);
                bank.appendChild(btn);
            }});

            // 단어 클릭 시 이동 (은행 <-> 문장 영역)
            function moveWord(btn) {{
                if (btn.parentElement === bank) {{
                    zone.appendChild(btn);
                }} else {{
                    bank.appendChild(btn);
                }}
                msg.innerText = ""; // 이동할 때 메시지 초기화
            }}

            // 정답 확인 로직
            function checkAnswer() {{
                let currentSentence = Array.from(zone.children).map(b => b.innerText).join(' ');
                if (currentSentence === correctAnswer) {{
                    msg.style.color = '#2ecc71';
                    msg.innerText = "🎉 완벽해! 정답이야! (Perfect!)";
                }} else {{
                    msg.style.color = '#e74c3c';
                    msg.innerText = "🤔 앗, 순서가 조금 틀린 것 같아. 다시 시도해 봐!";
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