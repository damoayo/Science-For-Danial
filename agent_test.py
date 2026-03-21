import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from googleapiclient.discovery import build

# 1. 환경 변수 및 클라이언트 설정
load_dotenv()
GEMINI_KEY = os.getenv("SCIENCE_KEY")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")

# 네 계정에서 확인된 2.5 모델 사용
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)

# 2. 학습 주제 읽기
try:
    with open("today_study.txt", "r", encoding="utf-8") as f:
        target_content = f.read().strip()
except FileNotFoundError:
    target_content = "중학교 1학년 과학: I. 과학과 인류의 지속가능한 삶"

print(f"🚀 [Gemini 2.5] 다니엘을 위한 맞춤 리포트 생성 중...")

# 3. AI에게 상세 내용 및 퀴즈 10문제 요청
prompt = f"""
중학교 1학년 학생 '다니엘'의 눈높이에서 [{target_content}] 주제를 정리해줘.
1. '변인 통제'라는 어려운 말 대신 '공정한 실험을 위해 똑같이 맞출 조건'이라는 쉬운 표현을 사용해.
2. 교과서 핵심 내용을 5가지 포인트로 아주 상세하고 다정하게 설명해줘.
3. 학습 확인을 위한 퀴즈 10문제(OX 5개, 객관식 5개)를 정답 및 해설과 함께 포함해줘.
4. 아래 JSON 형식으로만 응답해 (마크다운 없이 순수 JSON만).

{{
  "summary_points": ["상세내용1", "상세내용2", "상세내용3", "상세내용4", "상세내용5"],
  "youtube_plan": [{{"keyword": "검색어", "tip": "아빠의 팁"}}],
  "quizzes": [
    {{"id": 0, "type": "OX", "q": "질문", "a": "O/X", "ex": "해설"}},
    {{"id": 5, "type": "CHOICE", "q": "질문", "options": ["1", "2", "3", "4"], "a": 3, "ex": "해설"}}
  ]
}}
"""

try:
    # 4. API 호출 및 데이터 파싱
    response = model.generate_content(prompt)
    clean_text = response.text.replace('```json', '').replace('```', '').strip()
    data = json.loads(clean_text)

    # 5. 메인 리포트(index.html) 디자인 및 생성
    report_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>다니엘의 스마트 과학실</title>
        <style>
            :root {{ --primary: #3498db; --secondary: #2ecc71; --accent: #e67e22; --bg: #f4f7f6; }}
            body {{ font-family: 'Malgun Gothic', sans-serif; background: var(--bg); color: #333; line-height: 1.6; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 30px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, var(--primary), #8e44ad); color: white; padding: 50px 20px; text-align: center; }}
            .section {{ padding: 40px; border-bottom: 1px solid #eee; }}
            .study-card {{ background: #f9fbfd; border-radius: 20px; padding: 25px; border-left: 8px solid var(--primary); }}
            .summary-item {{ margin-bottom: 20px; }}
            .lab-banner {{ background: url('https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1200&q=80') center/cover; height: 250px; border-radius: 20px; margin: 20px 0; display: flex; align-items: center; justify-content: center; }}
            .lab-btn {{ background: rgba(230, 126, 34, 0.95); color: white; padding: 18px 45px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.2em; backdrop-filter: blur(5px); transition: 0.3s; }}
            .lab-btn:hover {{ transform: scale(1.05); background: var(--accent); }}
            .yt-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
            .yt-card {{ border: 1px solid #eee; border-radius: 15px; overflow: hidden; background: #fff; }}
            .yt-btn {{ display: block; background: #ff0000; color: white; text-align: center; padding: 12px; text-decoration: none; font-weight: bold; }}
            .quiz-container {{ background: #fff4e5; border-radius: 20px; padding: 30px; }}
            .q-card {{ background: white; padding: 20px; border-radius: 15px; margin-bottom: 15px; }}
            .ans-box {{ display: none; background: #e8f8f5; padding: 15px; border-radius: 10px; margin-top: 10px; border-left: 5px solid var(--secondary); font-weight: bold; }}
            .check-btn {{ background: #34495e; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }}
        </style>
        <script>
            function toggleAns(id) {{
                var x = document.getElementById(id);
                x.style.display = (x.style.display === "none" || x.style.display === "") ? "block" : "none";
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧪 다니엘의 스마트 과학 정복 리포트</h1>
                <p>아빠와 함께하는 즐거운 과학 시간!</p>
            </div>

            <div class="section">
                <h2>📖 이번 주 핵심 요약 (아빠의 비밀 노트)</h2>
                <div class="study-card">
                    {"".join([f'<div class="summary-item"><b>{i+1}. </b> {point}</div>' for i, point in enumerate(data['summary_points'])])}
                </div>
                <div class="lab-banner">
                    <a href="./danial_lab.html" class="lab-btn">🔬 나만의 온라인 실험실 입장하기 (클릭!)</a>
                </div>
            </div>

            <div class="section">
                <h2>📺 추천 영상 학습</h2>
                <div class="yt-grid">
    """

    # 유튜브 검색 및 추가
    for item in data['youtube_plan'][:4]:
        res = youtube.search().list(q=f"중1 과학 {item['keyword']}", part='snippet', maxResults=1, type='video').execute()
        if res['items']:
            v = res['items'][0]
            v_url = f"https://www.youtube.com/watch?v={v['id']['videoId']}"
            report_html += f"""
                <div class="yt-card">
                    <div style="padding:15px; font-weight:bold; height:50px; overflow:hidden;">{v['snippet']['title']}</div>
                    <a href="{v_url}" target="_blank" class="yt-btn">▶ 영상 보기</a>
                </div>
            """

    report_html += """
                </div>
            </div>

            <div class="section">
                <h2>📝 실력 확인! 미니 테스트 (10문제)</h2>
                <div class="quiz-container">
    """

    for i, q in enumerate(data['quizzes']):
        options_html = "".join([f"<li>{opt}</li>" for opt in q.get('options', [])])
        report_html += f"""
            <div class="q-card">
                <p><b>Q{i+1}. {q['q']}</b></p>
                {f'<ul style="list-style:none; padding:0;">{options_html}</ul>' if options_html else ''}
                <button class="check-btn" onclick="toggleAns('ans{i}')">정답 확인</button>
                <div id="ans{i}" class="ans-box">정답: {q['a']} <br><small>💡 {q['ex']}</small></div>
            </div>
        """

    report_html += """
                </div>
            </div>
            <div style="text-align:center; padding:40px; color:#bdc3c7;">❤️ 아빠가 다니엘을 위해 정성껏 만들었어. 화이팅!</div>
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(report_html)

    # 6. 애니메이션 실험실(danial_lab.html) 별도 생성
    lab_code = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>다니엘의 얼음 실험실</title>
        <style>
            body { font-family: 'Malgun Gothic', sans-serif; background: #eef2f3; text-align: center; padding: 20px; }
            .lab-box { background: white; max-width: 500px; margin: 0 auto; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            .ice { width: 120px; height: 120px; background: linear-gradient(135deg, #fff, #00d2ff); margin: 30px auto; border-radius: 15px; transition: 0.5s; display: flex; align-items: center; justify-content: center; font-weight: bold; }
            .btn { background: #e67e22; color: white; border: none; padding: 15px 30px; border-radius: 10px; cursor: pointer; font-weight: bold; margin-top: 20px; width: 100%; }
            #timer { font-size: 2.5em; color: #e74c3c; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="lab-box">
            <h2>🔬 얼음 녹이기 실험</h2>
            <p>공정한 실험을 위해 <b>조건을 똑같이</b> 맞춰보자!</p>
            <div id="iceBlock" class="ice">얼음</div>
            <div id="timer">00:00</div>
            <select id="drink" style="width:100%; padding:10px; border-radius:10px; margin-bottom:10px;">
                <option value="15">그냥 물 (제일 빨리 녹음)</option>
                <option value="30">오렌지 주스 (조금 느림)</option>
                <option value="50">설탕물 (가장 느림)</option>
            </select>
            <button class="btn" onclick="start()">실험 시작!</button>
            <p id="msg" style="margin-top:20px; color:#34495e;">음료수를 선택하고 버튼을 눌러!</p>
            <a href="./index.html" style="display:block; margin-top:20px; color:#3498db;">← 리포트로 돌아가기</a>
        </div>
        <script>
            let t = 0, timer = null;
            function start() {
                const ice = document.getElementById('iceBlock');
                const target = parseInt(document.getElementById('drink').value);
                t = 0; if(timer) clearInterval(timer);
                ice.style.transform = "scale(1)"; ice.style.opacity = "1";
                timer = setInterval(() => {
                    t++;
                    document.getElementById('timer').innerText = `00:${String(t).padStart(2, '0')}`;
                    let s = 1 - (t / target); ice.style.transform = `scale(${s})`; ice.style.opacity = s;
                    if(t >= target) {
                        clearInterval(timer);
                        document.getElementById('msg').innerHTML = `✅ <b>${target}초</b> 만에 녹았어! 조건을 잘 맞췄나봐!`;
                        ice.style.transform = "scale(0)";
                    }
                }, 100);
            }
        </script>
    </body>
    </html>
    """
    with open("danial_lab.html", "w", encoding="utf-8") as f:
        f.write(lab_code)

    print("🎉 모든 파일 생성 완료! 이제 git push 하러 가자!")

except Exception as e:
    print(f"❌ 에러 발생: {e}")