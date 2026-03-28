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

today = datetime.date.today()
today_str = today.strftime("%Y년 %m월 %d일")
html_filename = f"english_{today.strftime('%Y%m%d')}.html"

# 📅 요일 감지 (주 초반 vs 주 후반 단어장 난이도 조절)
weekday = today.weekday()
is_early_week = weekday < 3 # 월~수
week_phase_text = "주 초반(월~수)" if is_early_week else "주 후반(목~일)"
voca_instruction = "한국어 뜻과 짧은 예문" if is_early_week else "영영사전 풀이와 예문"

# 2. 📚 [1번 기둥] 전화영어 교재 지식 창고 (PDF 내용)
curriculum_db = {
    "Lesson 2": {
        "title": "Such an Awesome Guitarist!",
        "grammar": "부가의문문 (isn't it?, don't you?)",
        "key_patterns": [
            "Do you exercise regularly?", 
            "You are from South Korea, aren't you?", 
            "Playing basketball is fun, isn't it?"
        ],
        "authentic": "Do you have time? vs Do you have a moment?"
    },
    "Lesson 3": {
        "title": "Spending Time with Grandparents",
        "grammar": "빈도부사 (usually, often, sometimes, rarely, never)",
        "key_patterns": [
            "What do you usually do after school?", 
            "I often go to shopping malls.", 
            "I rarely read novels."
        ],
        "authentic": "usually (대개) vs often (자주)"
    }
}

# 제목에서 숫자 추출 (예: "Lesson 2 + 학교 Review" -> 2)
match = re.search(r'\d+', issue_title)
current_lesson_num = int(match.group()) if match else 2
current_lesson_key = f"Lesson {current_lesson_num}"
current_info = curriculum_db.get(current_lesson_key, curriculum_db["Lesson 2"])

# 전화영어 교재 HTML 조립 (이 부분이 화면에 무조건 출력됨!)
phone_english_patterns = "".join([f"<li>{p}</li>" for p in current_info['key_patterns']])

# 3. Gemini 프롬프트 (3가지 융합 지시)
prompt = f"""
너는 중학교 1학년 다니엘의 영어 코치야.
오늘은 {today_str} ({week_phase_text})이야.

[1. 전화영어 기본 교재 : {current_lesson_key}]
- 주제: {current_info['title']}
- 문법: {current_info['grammar']}

[2. 원어민 선생님 피드백 & 3. 학교 교과서 내용]
아빠가 아래에 선생님과의 대화록과 학교 교과서(Review) 텍스트를 함께 섞어서 입력했어.
{issue_body}

[특별 지시사항]
위 3가지 정보(전화영어 + 쌤 피드백 + 학교 교과서)를 완벽하게 융합해서 리포트를 만들어.
1. 'daily_voca'는 전화영어 단어와 학교 교과서 단어(예: performed, awesome 등)를 섞어서 {voca_instruction} 스타일로 5~8개 만들어줘.
2. 퀴즈는 총 10문제를 출제하되, 학교 교과서 문법(부가의문문 등)과 전화영어 단어를 섞어서 만들어줘.

반드시 아래 JSON 형식에 맞춰서 응답해.
{{
  "review_original": "대화록에서 다니엘이 틀렸거나 어색하게 말한 문장 1개",
  "review_better": "선생님이 교정해준 완벽한 문장",
  "review_advice": "짧은 아빠 조언",
  "daily_voca": [
    {{"word": "단어", "meaning": "뜻(또는 영영풀이)", "example": "예문"}}
  ],
  "quizzes": [
    {{"q": "단어 또는 영작 문제", "hint": "힌트", "a": "정답"}}
  ]
}}
"""

try:
    res = model.generate_content(prompt)
    clean_text = res.text.replace('```json', '').replace('```', '').strip()
    data = json.loads(clean_text)

    js_quizzes = json.dumps(data.get('quizzes', []))

    # 단어장 HTML 조립
    voca_html = ""
    for v in data.get('daily_voca', []):
        voca_html += f"""
        <div style="background: #fff; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #3498db; box-shadow: 0 2px 5px rgba(0,0,0,0.02);">
            <div style="font-size: 1.2em; font-weight: 800; color: #2980b9; margin-bottom: 5px;">{v['word']}</div>
            <div style="color: #e67e22; font-weight: bold; margin-bottom: 5px;">{v['meaning']}</div>
            <div style="color: #7f8c8d; font-size: 0.9em; font-style: italic;">👉 {v['example']}</div>
        </div>
        """

    # 4. 최종 HTML 웹페이지 생성 (3단 합체 구조)
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
            .card {{ background: white; border-radius: 20px; padding: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 30px; }}
            .tag {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; margin-bottom: 15px; font-size: 0.9em; }}
            .quiz-box {{ border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; margin-bottom: 15px; background: #fafafa; }}
            .quiz-q {{ font-weight: 800; font-size: 1.1em; margin-bottom: 10px; color: #2c3e50; }}
            .quiz-input {{ width: 100%; padding: 12px; font-size: 1em; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; margin-bottom: 10px; }}
            .btn-action {{ padding: 8px 15px; border: none; background: #bdc3c7; color: #2c3e50; border-radius: 5px; cursor: pointer; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="color: #2c3e50; margin-bottom: 5px;">📚 다니엘의 종합 영어 스낵</h1>
                <p style="color: #7f8c8d; font-weight: bold;">{today_str} | 전화영어 + 학교내신 통합복습</p>
            </div>

            <div class="card">
                <span class="tag" style="background: #e74c3c;">Part 1. 원어민 쌤의 교정 노트</span>
                <p style="color: #95a5a6; text-decoration: line-through; margin: 5px 0;">❌ {data['review_original']}</p>
                <p style="font-size: 1.3em; font-weight: bold; color: #2ecc71; margin: 0 0 10px 0;">✅ {data['review_better']}</p>
                <p style="background: #f8d7da; padding: 10px; border-radius: 8px; margin: 0; font-size: 0.9em;">👨‍🏫 {data['review_advice']}</p>
            </div>

            <div class="card" style="background: #f4f6f7; border: 1px solid #dcdde1;">
                <span class="tag" style="background: #34495e;">Part 2. 전화영어 교재 복습 ({current_lesson_key})</span>
                <h3 style="margin-top:0; color: #2c3e50;">{current_info['title']}</h3>
                <p style="font-weight: bold; color: #8e44ad;">👉 핵심 문법: {current_info['grammar']}</p>
                <ul style="font-weight: bold; color: #2980b9;">{phone_english_patterns}</ul>
                <p style="background: #fff3cd; padding: 10px; border-radius: 5px;">💡 현지 표현: {current_info['authentic']}</p>
            </div>

            <div class="card" style="background: #f0f8ff;">
                <span class="tag" style="background: #3498db;">Part 3. 오늘의 융합 단어장</span>
                <p style="margin-top: 0; color: #2980b9; font-weight:bold;">학교 단어와 전화영어 단어를 한 번에!</p>
                {voca_html}
            </div>

            <div class="card">
                <span class="tag" style="background: #f39c12;">Part 4. 실전 10문제 훈련</span>
                <div id="quiz-container"></div>
            </div>
        </div>

        <script>
            const quizzes = {js_quizzes};
            const container = document.getElementById('quiz-container');

            quizzes.forEach((quiz, index) => {{
                const html = `
                    <div class="quiz-box">
                        <div class="quiz-q">Q${{index+1}}. ${{quiz.q}}</div>
                        <input type="text" id="input_${{index}}" class="quiz-input" placeholder="정답을 입력하세요">
                        <button class="btn-action" onclick="document.getElementById('hint_${{index}}').style.display='block'">힌트</button>
                        <button class="btn-action" style="background: #2ecc71; color: white;" onclick="checkQuiz(${{index}}, '${{quiz.a.replace(/'/g, "\\'")}}')">확인</button>
                        <div id="hint_${{index}}" style="display:none; color:#e67e22; margin-top:5px; font-weight:bold;">💡 힌트: ${{quiz.hint}}</div>
                        <div id="result_${{index}}" style="display:none; margin-top:10px; font-weight:bold;"></div>
                    </div>
                `;
                container.innerHTML += html;
            }});

            function checkQuiz(index, correctAnswer) {{
                const userAnswer = document.getElementById(`input_${{index}}`).value.trim();
                const resultDiv = document.getElementById(`result_${{index}}`);
                resultDiv.style.display = 'block';
                
                const cleanUser = userAnswer.toLowerCase().replace(/[.,!?]/g, '').replace(/\s+/g, '');
                const cleanCorrect = correctAnswer.toLowerCase().replace(/[.,!?]/g, '').replace(/\s+/g, '');
                
                if (cleanUser === cleanCorrect || cleanUser.includes(cleanCorrect)) {{
                    resultDiv.style.color = '#2ecc71';
                    resultDiv.innerHTML = "🎉 완벽해요! 정답입니다.";
                }} else {{
                    resultDiv.style.color = '#e74c3c';
                    resultDiv.innerHTML = `🤔 아쉽네요. 정답은 <b>${{correctAnswer}}</b> 입니다.`;
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