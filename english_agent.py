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

# 2. 📞 [고정] 전화영어 교재 지식 창고
curriculum_db = {
    "Lesson 2": {
        "title": "Such an Awesome Guitarist!",
        "grammar": "부가의문문 (isn't it?, don't you?)",
        "key_patterns": [
            "Do you exercise regularly? (너는 운동을 규칙적으로 하니?)", 
            "You are from South Korea, aren't you? (너 한국에서 왔어, 그렇지 않아?)", 
            "Playing basketball is fun, isn't it? (농구하는 건 재미있어, 그렇지 않아?)"
        ]
    },
    "Lesson 3": {
        "title": "Spending Time with Grandparents",
        "grammar": "빈도부사 (usually, often, sometimes, rarely, never)",
        "key_patterns": [
            "What do you usually do after school? (너는 방과 후에 주로 뭐 하니?)", 
            "I often go to shopping malls. (나는 종종 쇼핑몰에 가.)", 
            "I rarely read novels. (나는 소설을 거의 읽지 않아.)"
        ]
    }
}

match = re.search(r'\d+', issue_title)
current_lesson_num = int(match.group()) if match else 2
current_lesson_key = f"Lesson {current_lesson_num}"
current_info = curriculum_db.get(current_lesson_key, curriculum_db["Lesson 2"])

# 전화영어 패턴 HTML 리스트 만들기
phone_english_patterns = "".join([f"<li style='margin-bottom: 5px;'>{p}</li>" for p in current_info['key_patterns']])

# 3. 🤖 Gemini 프롬프트 (학교 교과서 분석 및 클릭형 단어장 생성 지시)
prompt = f"""
너는 중학교 1학년 다니엘의 영어 코치야.
아래 아빠가 입력한 텍스트(issue_body) 안에는 '화상영어 선생님의 대화록'과 '학교 교과서 요약본'이 섞여 있어.

[입력 데이터]
{issue_body}

이 데이터를 바탕으로 반드시 아래 JSON 형식에 맞춰서 응답해.
{{
  "review_original": "대화록에서 다니엘이 틀리거나 어색하게 말한 문장 1개",
  "review_better": "선생님이 교정해준 완벽한 문장",
  "review_advice": "다니엘, [Original] 대신 [Better]처럼 말해보자! 형식의 짧은 아빠 조언",
  "school_summary": "입력 데이터 중 '학교 교과서(School Textbook)' 내용만 뽑아서, 문법 설명과 예문을 HTML 리스트(<ul><li>) 형태로 예쁘게 정리해줘.",
  "daily_voca": [
    {{
      "word": "단어 (학교교재+화상영어 단어 5~8개)",
      "en_meaning": "영영 사전 뜻",
      "en_example": "영어 예문",
      "ko_meaning": "한국어 뜻",
      "ko_example": "예문 한국어 해석"
    }}
  ],
  "quizzes": [
    {{"q": "부가의문문이나 단어 영작 문제 (총 10문제)", "hint": "힌트", "a": "정답"}}
  ]
}}
"""

try:
    res = model.generate_content(prompt)
    clean_text = res.text.replace('```json', '').replace('```', '').strip()
    data = json.loads(clean_text)

    js_quizzes = json.dumps(data.get('quizzes', []))

    # 🔤 클릭형 단어장 HTML 조립 (아빠의 요청 완벽 반영!)
    voca_html = ""
    for v in data.get('daily_voca', []):
        voca_html += f"""
        <div class="voca-card" onclick="toggleVoca(this)">
            <div class="voca-en">
                <div class="word-title">{v['word']}</div>
                <div class="meaning-en">{v['en_meaning']}</div>
                <div class="example-en">👉 {v['en_example']}</div>
                <div class="click-hint">클릭하면 한글 뜻이 보여요 👆</div>
            </div>
            <div class="voca-ko" style="display: none;">
                <div class="word-title" style="color:#e67e22;">{v['word']}</div>
                <div class="meaning-ko">💡 뜻: {v['ko_meaning']}</div>
                <div class="example-ko">해석: {v['ko_example']}</div>
            </div>
        </div>
        """

    # 4. 최종 HTML 웹페이지 생성 (4단 완벽 구조)
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
            .card {{ background: white; border-radius: 20px; padding: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 30px; }}
            .tag {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; margin-bottom: 15px; font-size: 0.9em; }}
            
            /* 클릭형 단어장 CSS */
            .voca-card {{ background: #fff; padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 5px solid #3498db; box-shadow: 0 4px 6px rgba(0,0,0,0.05); cursor: pointer; transition: 0.3s; }}
            .voca-card:hover {{ background: #fdfefe; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.1); }}
            .word-title {{ font-size: 1.4em; font-weight: 800; color: #2980b9; margin-bottom: 8px; }}
            .meaning-en {{ font-weight: bold; color: #34495e; margin-bottom: 5px; }}
            .example-en {{ color: #7f8c8d; font-style: italic; }}
            .click-hint {{ font-size: 0.8em; color: #bdc3c7; text-align: right; margin-top: 10px; font-weight: bold; }}
            .meaning-ko {{ font-weight: bold; color: #d35400; margin-bottom: 5px; font-size: 1.1em; }}
            .example-ko {{ color: #555; }}

            /* 퀴즈 CSS */
            .quiz-box {{ border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; margin-bottom: 15px; background: #fafafa; }}
            .quiz-q {{ font-weight: 800; font-size: 1.1em; margin-bottom: 15px; color: #2c3e50; }}
            .quiz-input {{ width: 100%; padding: 15px; font-size: 1.1em; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; margin-bottom: 15px; outline: none; }}
            .btn-action {{ padding: 10px 20px; border: none; background: #bdc3c7; color: #2c3e50; border-radius: 5px; cursor: pointer; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="color: #2c3e50;">📚 다니엘의 종합 영어 스낵</h1>
                <p style="color: #7f8c8d; font-weight: bold;">{today_str} | 전화영어 + 학교내신 통합 리포트</p>
            </div>

            <div class="card">
                <span class="tag" style="background: #e74c3c;">Part 1. 원어민 쌤의 교정 노트</span>
                <p style="color: #95a5a6; text-decoration: line-through; margin-bottom: 5px;">❌ {data['review_original']}</p>
                <p style="font-size: 1.3em; font-weight: bold; color: #2ecc71; margin-top: 0;">✅ {data['review_better']}</p>
                <p style="background: #f8d7da; padding: 10px; border-radius: 8px; margin-bottom: 0;">👨‍🏫 {data['review_advice']}</p>
            </div>

            <div class="card" style="background: #f8fafd; border: 1px solid #e1e8ed;">
                <span class="tag" style="background: #34495e;">Part 2. 오늘의 진도 복습</span>
                
                <h3 style="color: #2980b9;">📞 전화영어: {current_info['title']}</h3>
                <ul style="font-weight: bold; color: #34495e;">{phone_english_patterns}</ul>
                <hr style="border: 0; height: 1px; background: #dcdde1; margin: 20px 0;">
                
                <h3 style="color: #27ae60;">🏫 학교 교과서 핵심 포인트</h3>
                <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #2ecc71;">
                    {data['school_summary']}
                </div>
            </div>

            <div class="card" style="background: #f0f8ff;">
                <span class="tag" style="background: #3498db;">Part 3. 마법의 단어장</span>
                <p style="margin-top: 0; color: #2980b9; font-weight:bold;">영영 사전을 먼저 읽고, 카드를 클릭해서 한글 뜻을 확인해 봐!</p>
                {voca_html}
            </div>

            <div class="card">
                <span class="tag" style="background: #f39c12;">Part 4. 실전 10문제 훈련</span>
                <div id="quiz-container"></div>
            </div>
        </div>

        <script>
            // 단어장 클릭 시 영/한 전환 함수
            function toggleVoca(card) {{
                const enDiv = card.querySelector('.voca-en');
                const koDiv = card.querySelector('.voca-ko');
                if (enDiv.style.display === 'none') {{
                    enDiv.style.display = 'block';
                    koDiv.style.display = 'none';
                    card.style.borderLeftColor = '#3498db';
                }} else {{
                    enDiv.style.display = 'none';
                    koDiv.style.display = 'block';
                    card.style.borderLeftColor = '#e67e22';
                }}
            }}

            // 10문제 퀴즈 세팅
            const quizzes = {js_quizzes};
            const container = document.getElementById('quiz-container');

            quizzes.forEach((quiz, index) => {{
                const html = `
                    <div class="quiz-box">
                        <div class="quiz-q">Q${{index+1}}. ${{quiz.q}}</div>
                        <input type="text" id="input_${{index}}" class="quiz-input" placeholder="여기에 정답을 입력하세요">
                        <button class="btn-action" onclick="document.getElementById('hint_${{index}}').style.display='block'">힌트 듣기</button>
                        <button class="btn-action" style="background: #2ecc71; color: white;" onclick="checkQuiz(${{index}}, '${{quiz.a.replace(/'/g, "\\'")}}')">정답 확인</button>
                        <div id="hint_${{index}}" style="display:none; color:#e67e22; margin-top:10px; font-weight:bold;">💡 힌트: ${{quiz.hint}}</div>
                        <div id="result_${{index}}" style="display:none; margin-top:15px; font-weight:bold; font-size:1.1em;"></div>
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

    # 디스코드 알림
    discord_url = os.getenv("DISCORD_WEBHOOK")
    if discord_url:
        import requests
        report_link = f"https://damoayo.github.io/Science-For-Danial/{html_filename}"
        discord_msg = {{
            "content": f"📣 **[다니엘의 종합 영어 스낵 도착!]**\n아빠가 만들어준 학교 영어 + 전화 영어 통합 리포트가 준비됐어!\n\n📝 **오늘의 진도:** {current_lesson_key} & 학교 내신\n🎮 **오늘의 미션:** 단어장 뒤집기 & 실전 10문제 풀기\n👉 **숙제하러 가기:** {report_link}"
        }}
        requests.post(discord_url, json=discord_msg)

except Exception as e:
    print(f"❌ 에러 발생: {e}")