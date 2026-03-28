import os
import json
import datetime
import re
import google.generativeai as genai

# 1. 환경설정
GEMINI_KEY = os.getenv("SCIENCE_KEY")
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

issue_title = os.getenv("ISSUE_TITLE", "Lesson 2")
issue_body = os.getenv("ISSUE_BODY", "No data")

today_str = datetime.date.today().strftime("%Y년 %m월 %d일")
html_filename = f"english_{datetime.date.today().strftime('%Y%m%d')}.html"

# 2. 📚 진짜 PDF 교재 내용 100% 데이터베이스 (AI가 함부로 바꾸지 못하게 고정!)
curriculum_db = {
    "Lesson 2": {
        "title": "Such an Awesome Guitarist!",
        "grammar": "부가의문문 (isn't it?, don't you?)",
        "key_patterns": [
            "Do you exercise regularly? (너는 운동을 규칙적으로 하니?)",
            "Does he want to go to the concert? (그는 그 콘서트에 가고 싶어 하나요?)",
            "Do they play the piano often? (그들은 피아노를 자주 치나요?)",
            "You are from South Korea, aren't you? (너 한국에서 왔어, 그렇지 않아?)",
            "Playing basketball is fun, isn't it? (농구를 하는 건 재미있어, 그렇지 않아?)",
            "We have class in the afternoon, don't we? (우리 오후에 수업 있어, 그렇지 않아?)"
        ],
        "dialogue": [
            "Jordan: Do you play any musical instruments, Jimin?",
            "Jimin: Yes, I play the guitar, Jordan.",
            "Jordan: That's awesome! Playing the guitar must be fun, isn't it?",
            "Jimin: It is! I play in a small band with my friends. You're in a band too, aren't you?",
            "Jordan: No, I'm not. But playing in a band sounds fun! It must be exciting to perform together."
        ],
        "authentic": "Do you have time? (시간 여유 있어?) vs Do you have the time? (지금 몇 시야?) vs Do you have a moment? (잠깐 시간 돼?)"
    },
    "Lesson 3": {
        "title": "Spending Time with Grandparents",
        "grammar": "빈도부사 (usually, often, sometimes, rarely, never)",
        "key_patterns": [
            "What do you usually do after school? (너는 방과 후에 주로 무엇을 하니?)",
            "I stay at home and do homework. (나는 집에 머물고 숙제를 해.)",
            "How often do you go shopping? (얼마나 자주 쇼핑을 하니?)",
            "I often go to shopping malls. (나는 종종 쇼핑몰에 가요.)",
            "I am spending time with my grandparents. (나는 조부모님들과 시간을 보내고 있어.)"
        ],
        "dialogue": [
            "Jack: Sue, what do you usually do on the weekend?",
            "Sue: I visit my grandparents and read books with them.",
            "Jack: Oh, that's great! What are you reading these days?",
            "Sue: I'm reading a novel called Almond. How often do you read books?",
            "Jack: I rarely read novels, but this sounds quite interesting."
        ],
        "authentic": "usually (보통, 대개 - 거의 항상 일어남) vs often (자주 - usually 보다는 빈도가 낮음)"
    }
}

# 타임머신 로직
match = re.search(r'\d+', issue_title)
current_lesson_num = int(match.group()) if match else 2
next_lesson_num = current_lesson_num + 1

current_lesson_key = f"Lesson {current_lesson_num}"
next_lesson_key = f"Lesson {next_lesson_num}"

current_info = curriculum_db.get(current_lesson_key, curriculum_db["Lesson 2"])
next_info = curriculum_db.get(next_lesson_key, curriculum_db["Lesson 3"])

# 교재 HTML 변환 함수
def make_textbook_html(info):
    patterns = "".join([f"<li style='margin-bottom: 5px;'>{p}</li>" for p in info['key_patterns']])
    dialogues = "".join([f"<p style='margin: 5px 0;'><strong>{d.split(': ')[0]}:</strong> {d.split(': ')[1]}</p>" if ': ' in d else f"<p>{d}</p>" for d in info['dialogue']])
    
    return f"""
    <div style="background: #f8fafd; padding: 20px; border-radius: 12px; border: 1px solid #e1e8ed;">
        <h3 style="color: #2980b9; margin-top: 0;">✨ 핵심 패턴 (Key Patterns)</h3>
        <ul style="color: #34495e; font-weight: bold;">{patterns}</ul>
        
        <h3 style="color: #27ae60; margin-top: 20px;">🗣️ 대화 연습 (Let's Speak)</h3>
        <div style="background: #fff; padding: 15px; border-radius: 8px; border-left: 4px solid #2ecc71;">
            {dialogues}
        </div>
        
        <h3 style="color: #e67e22; margin-top: 20px;">💡 현지 표현 (Authentic Expressions)</h3>
        <p style="background: #fff3cd; padding: 10px; border-radius: 5px;">{info['authentic']}</p>
    </div>
    """

# 3. Gemini 프롬프트 (AI는 오직 피드백 정리와 10문제 퀴즈 생성만 담당!)
prompt = f"""
너는 중학교 1학년 다니엘의 1:1 영어 코치야.
방금 끝난 수업({current_lesson_key})의 복습을 위한 자료를 만들어야 해.

[방금 끝난 수업 : {current_lesson_key}]
- 주제: {current_info['title']}
- 핵심 문법: {current_info['grammar']}
- 대화록 및 선생님 피드백: {issue_body}

반드시 아래 JSON 형식에 맞춰서 응답해.
'custom_quizzes' 배열은 방금 끝난 수업({current_lesson_key})의 교재 내용과 대화록을 바탕으로 영작/순서배열 문제 10개를 무조건 꽉 채워서 만들어!
{{
  "review_original": "선생님 피드백에서 다니엘이 틀린 문장 (예: Three years ago.)",
  "review_better": "선생님이 교정해준 완벽한 문장 (예: I started this hobby three years ago.)",
  "review_advice": "다니엘, [Original] 대신 [Better]처럼 말하면 자연스러워! 형식의 아빠 조언",
  "custom_quizzes": [
    {{"q": "그는 취미에 많은 시간을 보낸다 (영작해 보세요)", "hint": "spend / pursuing", "a": "He spends a lot of time pursuing his hobby."}}
  ]
}}
"""

try:
    res = model.generate_content(prompt)
    clean_text = res.text.replace('```json', '').replace('```', '').strip()
    data = json.loads(clean_text)

    js_quizzes = json.dumps(data.get('custom_quizzes', []))

    # 4. 최종 HTML 조합
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>다니엘의 Daily English</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Nanum+Square+Round:wght@400;700;800&display=swap');
            body {{ font-family: 'Nanum Square Round', sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 20px; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: auto; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .card {{ background: white; border-radius: 20px; padding: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 30px; }}
            .tag {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; margin-bottom: 10px; font-size: 0.9em; }}
            .tag-review {{ background: #e74c3c; }} .tag-preview {{ background: #3498db; }} .tag-quiz {{ background: #9b59b6; }}
            
            /* 타이핑 퀴즈 UI */
            .quiz-box {{ border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; margin-bottom: 15px; background: #fafafa; }}
            .quiz-q {{ font-weight: 800; font-size: 1.1em; text-align: center; margin-bottom: 15px; color: #2c3e50; }}
            .quiz-input {{ width: 100%; padding: 15px; font-size: 1.1em; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; margin-bottom: 15px; outline: none; }}
            .quiz-input:focus {{ border-color: #3498db; box-shadow: 0 0 5px rgba(52, 152, 219, 0.5); }}
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
                <span class="tag tag-review">Part 1. 오늘의 오답 노트</span>
                <p style="color: #7f8c8d; text-decoration: line-through; margin-bottom: 5px;">❌ {data['review_original']}</p>
                <p style="font-size: 1.3em; font-weight: bold; color: #2ecc71; margin-top: 0;">✅ {data['review_better']}</p>
                <p style="background: #f8d7da; padding: 10px; border-radius: 8px; margin-bottom: 0;">👨‍🏫 아빠의 조언: {data['review_advice']}</p>
            </div>

            <div class="card">
                <span class="tag tag-review">Part 2. 교과서 완벽 복습 ({current_lesson_key})</span>
                <h2>📖 {current_info['title']}</h2>
                {make_textbook_html(current_info)}
            </div>

            <div class="card">
                <span class="tag tag-preview">Part 3. 다음 수업 엿보기 ({next_lesson_key})</span>
                <h2>🔭 {next_info['title']}</h2>
                {make_textbook_html(next_info)}
            </div>

            <div class="card">
                <span class="tag tag-quiz">Part 4. 오늘의 영작 훈련</span>
                <h2 style="text-align: center;">방금 배운 표현을 활용하여 영작해 보세요.</h2>
                <div id="quiz-container"></div>
            </div>
        </div>

        <script>
            const quizzes = {js_quizzes};
            const container = document.getElementById('quiz-container');

            quizzes.forEach((quiz, index) => {{
                const html = `
                    <div class="quiz-box">
                        <div class="quiz-q">${{quiz.q}}</div>
                        <input type="text" id="input_${{index}}" class="quiz-input" placeholder="여기에 영어로 적어보세요">
                        
                        <div id="hint_${{index}}" class="quiz-hint-box">
                            📢 힌트: ${{quiz.hint}}
                        </div>
                        
                        <div class="btn-group">
                            <button class="btn-action" onclick="document.getElementById('hint_${{index}}').style.display='block'">힌트보기</button>
                            <button class="btn-action" onclick="checkQuiz(${{index}}, '${{quiz.a.replace(/'/g, "\\'")}}')">정답확인</button>
                        </div>
                        
                        <div id="result_${{index}}" class="quiz-result"></div>
                    </div>
                `;
                container.innerHTML += html;
            }});

            function checkQuiz(index, correctAnswer) {{
                const userAnswer = document.getElementById(`input_${{index}}`).value.trim();
                const resultDiv = document.getElementById(`result_${{index}}`);
                
                resultDiv.style.display = 'block';
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