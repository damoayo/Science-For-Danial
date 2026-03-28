import os
import json
import datetime
import sys
import google.generativeai as genai

# 1. 환경설정 및 AI 연결
GEMINI_KEY = os.getenv("SCIENCE_KEY")
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})

today = datetime.date.today()
today_str = today.strftime("%Y년 %m월 %d일")
html_filename = f"english_{today.strftime('%Y%m%d')}.html"

# 📅 1년 52주를 순환하며 매주 다른 단원을 자동으로 선택합니다.
week_number = today.isocalendar()[1]
current_unit_index = (week_number % 8) + 1  # 1단원 ~ 8단원 로테이션

# 2. 📚 [완전 자동화 DB] 전화영어 + 학교 교과서(사진 8장 추출본)
study_db = {
    1: {"phone": "Do you exercise regularly?", "school_words": ["performed", "awesome", "concert", "instrumental", "amazing"], "school_grammar": "부가의문문 (aren't they?)"},
    2: {"phone": "What do you usually do?", "school_words": ["caprese", "skewers", "tofu", "healthy", "flour"], "school_grammar": "조동사 can (can/can't)"},
    3: {"phone": "I'm interested in cooking.", "school_words": ["mistake", "teammates", "support", "proud", "text"], "school_grammar": "감정 표현 (I'm proud of you)"},
    4: {"phone": "I want to be a chef.", "school_words": ["souvenir", "view", "fee", "local", "explore"], "school_grammar": "미래 계획 (I'm going to)"},
    5: {"phone": "It's getting dark.", "school_words": ["crime scene", "guard", "suspect", "wheelchair", "painting"], "school_grammar": "비교급/최상급 (taller, smallest)"},
    6: {"phone": "Do you want to save the Earth?", "school_words": ["single-use", "leftovers", "recycling", "trash", "environment"], "school_grammar": "요청과 거절 (Can you~?)"},
    7: {"phone": "A lot of people are working hard.", "school_words": ["director", "wrangler", "editor", "charge", "create"], "school_grammar": "동명사 (interested in ~ing)"},
    8: {"phone": "I think it's fun.", "school_words": ["delicious", "spicy", "salty", "post", "shocking"], "school_grammar": "의견 묻기 (What do you think?)"}
}

current_study = study_db.get(current_unit_index, study_db[1])

# 3. 🤖 AI 프롬프트 (데이터를 바탕으로 매일 새로운 퀴즈와 단어장 무한 생성)
prompt = f"""
너는 중학교 1학년 다니엘의 영어 코치야. 오늘은 {today_str}이야.
아래의 [오늘의 학습 재료]를 바탕으로 데일리 영어 리포트 데이터를 JSON 형식으로 정확히 만들어줘.

[오늘의 학습 재료: 단원 {current_unit_index}]
- 핵심 패턴(전화영어): {current_study['phone']}
- 학교 교과서 단어: {', '.join(current_study['school_words'])}
- 학교 교과서 문법: {current_study['school_grammar']}

{{
  "intro_message": "다니엘, 오늘은 {current_unit_index}단원을 복습할 거야! 화이팅! (같은 다정한 아빠의 응원 메시지)",
  "school_summary": "위 문법({current_study['school_grammar']})에 대한 간단한 설명과 예문 2개를 <ul><li> 태그로 작성해.",
  "daily_voca": [
    {{
      "word": "학교 단어 중 1개",
      "en_meaning": "영영 사전 뜻",
      "en_example": "영어 예문",
      "ko_meaning": "한국어 뜻",
      "ko_example": "예문 한국어 해석"
    }}
  ],
  "voca_quizzes": [
    {{"q": "단어 뜻이나 빈칸 채우기 (총 8문제)", "hint": "힌트", "a": "정답"}}
  ],
  "writing_quizzes": [
    {{"q": "오늘의 문법과 패턴을 활용한 영작 (총 2문제)", "hint": "힌트", "a": "완벽한 정답"}}
  ]
}}
"""

try:
    res = model.generate_content(prompt)
    data = json.loads(res.text.strip())
    
    js_voca_quizzes = json.dumps(data.get('voca_quizzes', []))
    js_writing_quizzes = json.dumps(data.get('writing_quizzes', []))

    voca_html = ""
    for v in data.get('daily_voca', []):
        voca_html += f"""
        <div class="voca-card" onclick="toggleVoca(this)">
            <div class="voca-en">
                <div class="word-title">{v.get('word', '')}</div>
                <div class="meaning-en">{v.get('en_meaning', '')}</div>
                <div class="example-en">👉 {v.get('en_example', '')}</div>
                <div class="click-hint">클릭하면 한글 뜻이 보여요 👆</div>
            </div>
            <div class="voca-ko" style="display: none;">
                <div class="word-title" style="color:#e67e22;">{v.get('word', '')}</div>
                <div class="meaning-ko">💡 뜻: {v.get('ko_meaning', '')}</div>
                <div class="example-ko">해석: {v.get('ko_example', '')}</div>
            </div>
        </div>
        """

    # HTML 구조 조립
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>다니엘의 자동 영어 스낵</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Nanum+Square+Round:wght@400;700;800&display=swap');
            body {{ font-family: 'Nanum Square Round', sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 20px; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: auto; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .card {{ background: white; border-radius: 20px; padding: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 30px; }}
            .tag {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; margin-bottom: 15px; font-size: 0.9em; }}
            .voca-card {{ background: #fff; padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 5px solid #3498db; box-shadow: 0 4px 6px rgba(0,0,0,0.05); cursor: pointer; transition: 0.3s; }}
            .voca-card:hover {{ background: #fdfefe; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.1); }}
            .word-title {{ font-size: 1.4em; font-weight: 800; color: #2980b9; margin-bottom: 8px; }}
            .meaning-en {{ font-weight: bold; color: #34495e; margin-bottom: 5px; }}
            .example-en {{ color: #7f8c8d; font-style: italic; }}
            .click-hint {{ font-size: 0.8em; color: #bdc3c7; text-align: right; margin-top: 10px; font-weight: bold; }}
            .meaning-ko {{ font-weight: bold; color: #d35400; margin-bottom: 5px; font-size: 1.1em; }}
            .example-ko {{ color: #555; }}
            .quiz-box {{ border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; margin-bottom: 15px; background: #fafafa; }}
            .quiz-q {{ font-weight: 800; font-size: 1.1em; margin-bottom: 15px; color: #2c3e50; }}
            .quiz-input {{ width: 100%; padding: 15px; font-size: 1.1em; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; margin-bottom: 15px; outline: none; }}
            .btn-action {{ padding: 10px 20px; border: none; background: #bdc3c7; color: #2c3e50; border-radius: 5px; cursor: pointer; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="color: #2c3e50;">🚀 다니엘의 자동 영어 스낵</h1>
                <p style="color: #7f8c8d; font-weight: bold;">{today_str} | 단원 {current_unit_index} 복습</p>
            </div>

            <div class="card" style="background: #f8fafd; border: 1px solid #e1e8ed;">
                <span class="tag" style="background: #e74c3c;">Part 1. 오늘의 미션</span>
                <h3 style="color: #2980b9;">👨‍🏫 {data.get('intro_message', '')}</h3>
                <hr style="border: 0; height: 1px; background: #dcdde1; margin: 20px 0;">
                <h3 style="color: #27ae60;">핵심 문법 & 패턴</h3>
                <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #2ecc71;">
                    <p><b>전화영어 핵심:</b> {current_study['phone']}</p>
                    {data.get('school_summary', '')}
                </div>
            </div>

            <div class="card" style="background: #f0f8ff;">
                <span class="tag" style="background: #3498db;">Part 2. 마법의 단어장</span>
                {voca_html}
            </div>

            <div class="card">
                <span class="tag" style="background: #f39c12;">Part 3. 실전 단어 퀴즈</span>
                <div id="voca-container"></div>
            </div>

            <div class="card">
                <span class="tag" style="background: #9b59b6;">Part 4. 핵심 영작 훈련</span>
                <div id="writing-container"></div>
            </div>
        </div>

        <script>
            function toggleVoca(card) {{
                const enDiv = card.querySelector('.voca-en');
                const koDiv = card.querySelector('.voca-ko');
                if (enDiv.style.display === 'none') {{
                    enDiv.style.display = 'block'; koDiv.style.display = 'none'; card.style.borderLeftColor = '#3498db';
                }} else {{
                    enDiv.style.display = 'none'; koDiv.style.display = 'block'; card.style.borderLeftColor = '#e67e22';
                }}
            }}

            function renderQuizzes(quizzes, containerId, prefix) {{
                const container = document.getElementById(containerId);
                quizzes.forEach((quiz, index) => {{
                    const html = `
                        <div class="quiz-box">
                            <div class="quiz-q">Q${{index+1}}. ${{quiz.q}}</div>
                            <input type="text" id="input_${{prefix}}_${{index}}" class="quiz-input" placeholder="정답 입력">
                            <button class="btn-action" onclick="document.getElementById('hint_${{prefix}}_${{index}}').style.display='block'">힌트</button>
                            <button class="btn-action" style="background: #2ecc71; color: white;" onclick="checkQuiz('${{prefix}}_${{index}}', '${{quiz.a.replace(/'/g, "\\'")}}')">확인</button>
                            <div id="hint_${{prefix}}_${{index}}" style="display:none; color:#e67e22; margin-top:10px;">💡 ${{quiz.hint}}</div>
                            <div id="result_${{prefix}}_${{index}}" style="display:none; margin-top:15px; font-weight:bold;"></div>
                        </div>
                    `;
                    container.innerHTML += html;
                }});
            }}

            function checkQuiz(id, correctAnswer) {{
                const userAnswer = document.getElementById(`input_${{id}}`).value.trim().toLowerCase().replace(/[.,!?]/g, '').replace(/\s+/g, '');
                const cleanCorrect = correctAnswer.toLowerCase().replace(/[.,!?]/g, '').replace(/\s+/g, '');
                const resultDiv = document.getElementById(`result_${{id}}`);
                resultDiv.style.display = 'block';
                if (userAnswer === cleanCorrect || userAnswer.includes(cleanCorrect)) {{
                    resultDiv.style.color = '#2ecc71'; resultDiv.innerHTML = "🎉 완벽해요!";
                }} else {{
                    resultDiv.style.color = '#e74c3c'; resultDiv.innerHTML = `🤔 정답: <b>${{correctAnswer}}</b>`;
                }}
            }}

            renderQuizzes({js_voca_quizzes}, 'voca-container', 'voca');
            renderQuizzes({js_writing_quizzes}, 'writing-container', 'write');
        </script>
    </body>
    </html>
    """

    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ {html_filename} 생성 완료!")

    # 🚀 디스코드 알림 발송 (완벽 수정)
    discord_url = os.getenv("DISCORD_WEBHOOK")
    if discord_url:
        import requests
        report_link = f"https://damoayo.github.io/Science-For-Danial/{html_filename}"
        discord_msg = {{
            "content": f"📣 **[다니엘의 자동 영어 스낵 도착!]**\n아빠가 준비한 오늘의 영어가 세팅됐어!\n\n📝 **오늘의 학습:** 단원 {current_unit_index} 마스터하기\n👉 **공부하러 가기:** {report_link}"
        }}
        requests.post(discord_url, json=discord_msg)
        print("🔔 디스코드 전송 완료!")

except Exception as e:
    print(f"❌ 에러 발생: {e}")
    sys.exit(1)