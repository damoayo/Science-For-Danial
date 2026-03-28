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

# 📅 요일 감지 로직 (0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일)
weekday = today.weekday()
is_early_week = weekday < 3 # 월, 화, 수
week_phase_text = "주 초반(월~수)" if is_early_week else "주 후반(목~일)"

# 2. 진짜 PDF 교재 기반 지식 창고
curriculum_db = {
    "Lesson 2": {
        "title": "Such an Awesome Guitarist!",
        "grammar": "부가의문문 (isn't it?, don't you?)",
        "key_patterns": ["Do you exercise regularly?", "You are from South Korea, aren't you?", "Playing basketball is fun, isn't it?"],
        "vocabulary": ["musical", "awesome", "guitar", "perform", "band", "exciting", "regularly", "instrument"]
    },
    "Lesson 3": {
        "title": "Spending Time with Grandparents",
        "grammar": "빈도부사 (usually, often, sometimes, rarely, never)",
        "key_patterns": ["What do you usually do after school?", "I often go to shopping malls.", "I rarely read novels."],
        "vocabulary": ["weekend", "trouble", "grandparents", "novel", "often", "rarely", "visit", "never", "understand", "skip", "interesting"]
    }
}

match = re.search(r'\d+', issue_title)
current_lesson_num = int(match.group()) if match else 2
current_lesson_key = f"Lesson {current_lesson_num}"
current_info = curriculum_db.get(current_lesson_key, curriculum_db["Lesson 2"])

# 단어장 학습 스타일 지시
if is_early_week:
    voca_instruction = "오늘은 주 초반입니다. 영어 단어와 '직관적인 한국어 뜻'을 1:1로 매칭해서 제공하세요. 예문은 한국어로 아주 짧게 주세요."
else:
    voca_instruction = "오늘은 주 후반입니다. 한국어 뜻 대신, 중학교 1학년 수준의 아주 쉬운 '영영 사전식 풀이(영어)'와 문맥을 파악할 수 있는 '쉬운 영어 예문'을 제공하세요."

# 3. Gemini 프롬프트 (단어 집중 + 영작 최소화)
prompt = f"""
너는 중학교 1학년 다니엘의 1:1 영어 코치야.
오늘은 {today_str} ({week_phase_text})이야.

[오늘의 학습 진도 : {current_lesson_key}]
- 주제: {current_info['title']}
- 핵심 단어: {current_info['vocabulary']}
- 핵심 패턴: {current_info['key_patterns']}
- 대화록 및 피드백: {issue_body}

반드시 아래 JSON 형식에 맞춰서 응답해.
1. 'daily_voca'는 {voca_instruction}에 맞춰서 핵심 단어들을 설명해줘.
2. 'voca_quizzes'는 단어의 뜻을 맞추거나 빈칸을 채우는 퀴즈로 5~8문제 출제해.
3. 'writing_quizzes'는 아빠의 요청대로 피로도를 줄이기 위해 딱 2문제만 출제해.

{{
  "review_original": "대화록에서 다니엘이 틀렸거나 어색하게 말한 문장 1개",
  "review_better": "선생님이 교정해준 완벽한 문장",
  "review_advice": "다니엘, [Original] 대신 [Better]처럼 말해보자! 형식의 짧은 아빠 조언",
  "daily_voca": [
    {{"word": "단어", "meaning": "한국어 뜻(주초반) 또는 영영풀이(주후반)", "example": "짧은 예문"}}
  ],
  "voca_quizzes": [
    {{"q": "다음 단어의 뜻은? (또는 빈칸에 알맞은 단어는?)", "hint": "힌트", "a": "정답"}}
  ],
  "writing_quizzes": [
    {{"q": "나는 종종 쇼핑몰에 간다 (영작해 보세요)", "hint": "often / go shopping", "a": "I often go to shopping malls."}}
  ]
}}
"""

try:
    res = model.generate_content(prompt)
    clean_text = res.text.replace('```json', '').replace('```', '').strip()
    data = json.loads(clean_text)

    js_voca_quizzes = json.dumps(data.get('voca_quizzes', []))
    js_writing_quizzes = json.dumps(data.get('writing_quizzes', []))

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

    # 4. 최종 HTML 웹페이지 생성
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
            .quiz-input:focus {{ border-color: #3498db; outline: none; }}
            .btn-action {{ padding: 8px 15px; border: none; background: #bdc3c7; color: #2c3e50; border-radius: 5px; cursor: pointer; font-weight: bold; }}
            .btn-action:hover {{ background: #95a5a6; color: white; }}
            .quiz-result {{ display: none; margin-top: 10px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="color: #2c3e50; margin-bottom: 5px;">📚 다니엘의 10분 영어 스낵</h1>
                <p style="color: #7f8c8d; font-weight: bold;">{today_str} | {week_phase_text} 맞춤형 학습</p>
            </div>

            <div class="card">
                <span class="tag" style="background: #e74c3c;">Part 1. 오늘의 한 문장</span>
                <p style="color: #95a5a6; text-decoration: line-through; margin: 5px 0;">❌ {data['review_original']}</p>
                <p style="font-size: 1.3em; font-weight: bold; color: #2ecc71; margin: 0 0 10px 0;">✅ {data['review_better']}</p>
                <p style="background: #f8d7da; padding: 10px; border-radius: 8px; margin: 0; font-size: 0.9em;">👨‍🏫 {data['review_advice']}</p>
            </div>

            <div class="card" style="background: #f0f8ff;">
                <span class="tag" style="background: #3498db;">Part 2. 오늘의 단어장</span>
                <h3 style="margin-top: 0; color: #2980b9;">{week_phase_text} 미션: 단어 씹어먹기!</h3>
                {voca_html}
            </div>

            <div class="card">
                <span class="tag" style="background: #f39c12;">Part 3. 스피드 단어 퀴즈</span>
                <div id="voca-container"></div>
            </div>

            <div class="card">
                <span class="tag" style="background: #9b59b6;">Part 4. 핵심 영작 (2문제)</span>
                <div id="writing-container"></div>
            </div>
        </div>

        <script>
            function createQuizzes(quizzes, containerId, prefix) {{
                const container = document.getElementById(containerId);
                quizzes.forEach((quiz, index) => {{
                    const html = `
                        <div class="quiz-box">
                            <div class="quiz-q">Q${{index+1}}. ${{quiz.q}}</div>
                            <input type="text" id="input_${{prefix}}_${{index}}" class="quiz-input" placeholder="정답을 입력하세요">
                            <button class="btn-action" onclick="document.getElementById('hint_${{prefix}}_${{index}}').style.display='block'">힌트</button>
                            <button class="btn-action" style="background: #2ecc71; color: white;" onclick="checkQuiz('${{prefix}}_${{index}}', '${{quiz.a.replace(/'/g, "\\'")}}')">확인</button>
                            <div id="hint_${{prefix}}_${{index}}" style="display:none; color:#e67e22; margin-top:5px; font-weight:bold;">💡 힌트: ${{quiz.hint}}</div>
                            <div id="result_${{prefix}}_${{index}}" class="quiz-result"></div>
                        </div>
                    `;
                    container.innerHTML += html;
                }});
            }}

            function checkQuiz(id, correctAnswer) {{
                const userAnswer = document.getElementById(`input_${{id}}`).value.trim();
                const resultDiv = document.getElementById(`result_${{id}}`);
                resultDiv.style.display = 'block';
                
                const cleanUser = userAnswer.toLowerCase().replace(/[.,!?]/g, '').replace(/\s+/g, '');
                const cleanCorrect = correctAnswer.toLowerCase().replace(/[.,!?]/g, '').replace(/\s+/g, '');
                
                if (cleanUser === cleanCorrect || cleanUser.includes(cleanCorrect)) {{
                    resultDiv.style.color = '#2ecc71';
                    resultDiv.innerHTML = "🎉 정답!";
                }} else {{
                    resultDiv.style.color = '#e74c3c';
                    resultDiv.innerHTML = `🤔 아쉽네요. 정답은 <b>${{correctAnswer}}</b> 입니다.`;
                }}
            }}

            createQuizzes({js_voca_quizzes}, 'voca-container', 'v');
            createQuizzes({js_writing_quizzes}, 'writing-container', 'w');
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
            "content": f"📣 **[다니엘의 데일리 영어 도착!]**\n{week_phase_text} 맞춤 단어장과 퀴즈가 준비되었어!\n\n📝 **오늘의 학습:** {current_lesson_key} 단어 집중공략\n👉 **숙제하러 가기:** {report_link}"
        }}
        requests.post(discord_url, json=discord_msg)

except Exception as e:
    print(f"❌ 에러 발생: {e}")