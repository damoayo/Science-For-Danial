import os
import json
import datetime
import sys
import google.generativeai as genai
from googleapiclient.discovery import build

# 1. 환경설정 및 AI/유튜브 연결
GEMINI_KEY = os.getenv("SCIENCE_KEY")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})

today = datetime.date.today()
today_str = today.strftime("%Y년 %m월 %d일")
html_filename = f"science_{today.strftime('%Y%m%d')}.html"

# 📅 진도 자동 계산
start_date = datetime.date(2026, 3, 23)
start_unit = 1
weeks_passed = (today - start_date).days // 7
current_unit_index = ((start_unit - 1 + weeks_passed) % 8) + 1

# 2. 📚 과학 DB
study_db = {
    1: {"topic": "지권의 변화", "concepts": ["지구계", "지각", "맨틀", "외핵", "내핵"], "focus": "지구 내부 구조의 특징"},
    2: {"topic": "여러 가지 힘", "concepts": ["중력", "탄성력", "마찰력", "부력"], "focus": "힘의 크기와 방향"},
    3: {"topic": "생물의 다양성", "concepts": ["종 다양성", "생태계", "변이", "분류"], "focus": "생물을 분류하는 이유와 방법"},
    4: {"topic": "기체의 성질", "concepts": ["입자 운동", "압력", "보일 법칙", "샤를 법칙"], "focus": "온도와 압력에 따른 기체의 부피 변화"},
    5: {"topic": "물질의 상태 변화", "concepts": ["융해", "응고", "기화", "액화", "승화"], "focus": "상태 변화 시 열에너지의 흡수와 방출"},
    6: {"topic": "빛과 파동", "concepts": ["반사", "굴절", "진폭", "파장", "진동수"], "focus": "빛의 직진, 반사, 굴절 법칙"},
    7: {"topic": "과학과 나의 미래", "concepts": ["첨단 과학", "환경 오염", "지속 가능한 발전"], "focus": "과학 기술의 발달과 우리 생활"},
    8: {"topic": "종합 복습", "concepts": ["핵심 개념 총정리", "실생활 적용"], "focus": "1~7단원 융합 문제"}
}
current_study = study_db.get(current_unit_index, study_db[1])

# 3. 🤖 AI 프롬프트 (유튜브 추천 지시 추가)
prompt = f"""
너는 중학교 1학년 다니엘의 과학 코치야. 
[단원 {current_unit_index}] 주제: {current_study['topic']} / 포커스: {current_study['focus']}

아래 JSON 형식으로 응답해.
{{
  "intro_message": "다니엘, 오늘은 {current_unit_index}단원 '{current_study['topic']}'에 대해 알아볼 거야!",
  "science_summary": "오늘의 학습 포커스를 <ul><li> 태그로 재미있게 요약해.",
  "youtube_keyword": "{current_study['topic']} EBS 중학과학",
  "youtube_tip": "이 영상을 보면 오늘 배운 내용이 머릿속에 쏙쏙 들어올 거야!",
  "concept_cards": [
    {{"keyword": "주요 개념", "definition": "과학적 정의", "example": "실생활 예시"}}
  ],
  "quizzes": [
    {{"q": "개념 퀴즈 (총 5문제)", "hint": "힌트", "a": "정답"}}
  ],
  "thought_experiment": "오늘 배운 내용을 바탕으로 한 사고 실험 질문 1개"
}}
"""

try:
    res = model.generate_content(prompt)
    data = json.loads(res.text.strip())
    js_quizzes = json.dumps(data.get('quizzes', []))

    # 📺 유튜브 영상 불러오기 (진짜 영상 화면을 가져옵니다!)
    youtube_html = ""
    if YOUTUBE_KEY and data.get("youtube_keyword"):
        try:
            youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
            req = youtube.search().list(q=data["youtube_keyword"], part="snippet", maxResults=1, type="video")
            yt_res = req.execute()
            if yt_res['items']:
                vid_id = yt_res['items'][0]['id']['videoId']
                youtube_html = f"""
                <div class="card" style="background: #fff0f5; border: 1px solid #ffb6c1;">
                    <span class="tag" style="background: #ff69b4;">Part 2. 아빠의 추천 영상 🎬</span>
                    <h3 style="color: #c0392b;">{data.get("youtube_tip", "이 영상을 먼저 보면 이해가 훨씬 빠를 거야!")}</h3>
                    <iframe width="100%" height="400" src="https://www.youtube.com/embed/{vid_id}" frameborder="0" allowfullscreen style="border-radius:15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"></iframe>
                </div>
                """
        except Exception as yt_e:
            print(f"유튜브 불러오기 실패: {yt_e}")

    # 🔤 개념 카드 조립
    card_html = ""
    for c in data.get('concept_cards', []):
        card_html += f"""
        <div class="voca-card" onclick="toggleCard(this)">
            <div class="voca-en">
                <div class="word-title">🔬 {c.get('keyword', '')}</div>
                <div class="click-hint">클릭해서 뜻과 예시 보기 👆</div>
            </div>
            <div class="voca-ko" style="display: none;">
                <div class="word-title" style="color:#e67e22;">{c.get('keyword', '')}</div>
                <div class="meaning-ko">💡 정의: {c.get('definition', '')}</div>
                <div class="example-ko">🌍 예시: {c.get('example', '')}</div>
            </div>
        </div>
        """

    # HTML 조립 (유튜브 영역 추가)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>다니엘의 스파크 과학 스낵</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Nanum+Square+Round:wght@400;700;800&display=swap');
            body {{ font-family: 'Nanum Square Round', sans-serif; background: #f0f4f8; color: #333; margin: 0; padding: 20px; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: auto; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .card {{ background: white; border-radius: 20px; padding: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 30px; }}
            .tag {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; margin-bottom: 15px; font-size: 0.9em; }}
            .voca-card {{ background: #fff; padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 5px solid #2ecc71; box-shadow: 0 4px 6px rgba(0,0,0,0.05); cursor: pointer; transition: 0.3s; }}
            .voca-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.1); }}
            .word-title {{ font-size: 1.4em; font-weight: 800; color: #27ae60; margin-bottom: 8px; }}
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
                <h1 style="color: #2c3e50;">🔭 다니엘의 스파크 과학 스낵</h1>
                <p style="color: #7f8c8d; font-weight: bold;">{today_str} | 과학 {current_unit_index}단원: {current_study['topic']}</p>
            </div>

            <div class="card" style="border: 1px solid #e1e8ed;">
                <span class="tag" style="background: #e74c3c;">Part 1. 오늘의 미션</span>
                <h3 style="color: #c0392b;">👨‍🔬 {data.get('intro_message', '')}</h3>
                <hr style="border: 0; height: 1px; background: #dcdde1; margin: 20px 0;">
                <h3 style="color: #2980b9;">핵심 원리 이해하기</h3>
                <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db;">
                    {data.get('science_summary', '')}
                </div>
            </div>

            {youtube_html}

            <div class="card">
                <span class="tag" style="background: #2ecc71;">Part 3. 개념 뒤집기 카드</span>
                <p style="color: #27ae60; font-weight:bold;">키워드를 보고 어떤 뜻인지 먼저 상상해 본 다음 클릭해 봐!</p>
                {card_html}
            </div>

            <div class="card">
                <span class="tag" style="background: #f39c12;">Part 4. 실전 과학 퀴즈</span>
                <div id="quiz-container"></div>
            </div>
            
            <div class="card" style="background: #fdf5e6;">
                <span class="tag" style="background: #8e44ad;">Part 5. 아인슈타인 사고 실험</span>
                <h3 style="color: #8e44ad;">🧠 {data.get('thought_experiment', '')}</h3>
            </div>
        </div>

        <script>
            function toggleCard(card) {{
                const enDiv = card.querySelector('.voca-en');
                const koDiv = card.querySelector('.voca-ko');
                if (enDiv.style.display === 'none') {{
                    enDiv.style.display = 'block'; koDiv.style.display = 'none'; card.style.borderLeftColor = '#2ecc71';
                }} else {{
                    enDiv.style.display = 'none'; koDiv.style.display = 'block'; card.style.borderLeftColor = '#e67e22';
                }}
            }}

            function renderQuizzes(quizzes, containerId) {{
                const container = document.getElementById(containerId);
                quizzes.forEach((quiz, index) => {{
                    const html = `
                        <div class="quiz-box">
                            <div class="quiz-q">Q${{index+1}}. ${{quiz.q}}</div>
                            <input type="text" id="input_q_${{index}}" class="quiz-input" placeholder="정답 입력">
                            <button class="btn-action" onclick="document.getElementById('hint_q_${{index}}').style.display='block'">힌트</button>
                            <button class="btn-action" style="background: #3498db; color: white;" onclick="checkQuiz('q_${{index}}', '${{quiz.a.replace(/'/g, "\\'")}}')">확인</button>
                            <div id="hint_q_${{index}}" style="display:none; color:#e67e22; margin-top:10px;">💡 ${{quiz.hint}}</div>
                            <div id="result_q_${{index}}" style="display:none; margin-top:15px; font-weight:bold;"></div>
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
                    resultDiv.style.color = '#2ecc71'; resultDiv.innerHTML = "🎉 정답입니다! 훌륭해요!";
                }} else {{
                    resultDiv.style.color = '#e74c3c'; resultDiv.innerHTML = `🤔 정답: <b>${{correctAnswer}}</b>`;
                }}
            }}

            renderQuizzes({js_quizzes}, 'quiz-container');
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
        discord_msg = {"content": f"📣 **[다니엘의 스파크 과학 스낵 도착!]**\n🔭 **오늘의 주제:** {current_study['topic']}\n👉 **공부하러 가기:** {report_link}"}
        requests.post(discord_url, json=discord_msg)

except Exception as e:
    print(f"❌ 에러 발생: {e}")
    sys.exit(1)