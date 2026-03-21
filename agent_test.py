import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from googleapiclient.discovery import build

# 1. 환경 변수 및 클라이언트 설정
load_dotenv()
genai.configure(api_key=os.getenv("SCIENCE_KEY"))
model = genai.GenerativeModel('models/gemini-2.5-flash')
youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_KEY"))

# 2. 주제 읽기
try:
    with open("today_study.txt", "r", encoding="utf-8") as f:
        target_content = f.read().strip()
except:
    target_content = "중1 과학: 1단원 과학과 인류의 삶"

# 3. 프롬프트 - 중학생 눈높이 용어 + 10문제 퀴즈 요청
prompt = f"""
중학교 1학년 학생 '다니엘'의 눈높이에서 [{target_content}]를 정리해줘.
1. '변인 통제' 대신 '공정한 실험을 위해 똑같이 맞출 조건'이라는 쉬운 말을 써줘.
2. 교과서 핵심 내용을 5가지 포인트로 아주 상세하게 정리해줘.
3. 마지막에 학습 확인을 위한 퀴즈 10문제(OX 5개, 객관식 5개)를 정답/해설과 함께 포함해줘.
4. 아래 JSON 형식으로만 응답해.

{{
  "summary_points": ["내용1", "내용2", ...],
  "youtube_plan": [{{"keyword": "검색어", "tip": "다정한 설명"}}],
  "quizzes": [
    {{"type": "OX", "q": "질문", "a": "O/X", "ex": "해설"}},
    {{"type": "CHOICE", "q": "질문", "options": ["1", "2", "3", "4"], "a": 3, "ex": "해설"}}
  ],
  "lab_image_prompt": "실험실 느낌의 창의적인 일러스트 묘사 (영어)"
}}
"""

try:
    response = model.generate_content(prompt)
    data = json.loads(response.text.replace('```json', '').replace('```', '').strip())

    # 4. 이미지 생성 (다니엘이 좋아할 실험실 이미지)
    # 실제로는 이미지 생성 API나 플레이스홀더를 사용하지만, 여기선 세련된 배경을 위해 스타일 수정
    lab_img = "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&q=80"

    # 5. HTML 리포트 생성 (세련된 카드 디자인)
    report_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>다니엘의 스마트 과학실</title>
        <style>
            :root {{ --primary: #3498db; --secondary: #2ecc71; --accent: #e67e22; --bg: #f8f9fa; }}
            body {{ font-family: 'Pretendard', 'Malgun Gothic', sans-serif; background: var(--bg); color: #333; margin: 0; padding: 20px; }}
            .main-container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 30px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, var(--primary), #8e44ad); color: white; padding: 60px 20px; text-align: center; }}
            .section {{ padding: 40px; border-bottom: 1px solid #eee; }}
            .card {{ background: #fff; border: 1px solid #eef2f7; border-radius: 20px; padding: 25px; margin-bottom: 20px; transition: 0.3s; }}
            .card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }}
            .summary-item {{ display: flex; align-items: flex-start; gap: 15px; margin-bottom: 15px; }}
            .summary-number {{ background: var(--primary); color: white; border-radius: 50%; width: 25px; height: 25px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 14px; }}
            .lab-banner {{ background: url('{lab_img}') center/cover; height: 250px; border-radius: 20px; margin: 20px 0; display: flex; align-items: center; justify-content: center; }}
            .lab-btn {{ background: rgba(230, 126, 34, 0.9); color: white; padding: 15px 40px; border-radius: 50px; text-decoration: none; font-weight: bold; backdrop-filter: blur(5px); }}
            .youtube-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .yt-card {{ border: 1px solid #eee; border-radius: 15px; overflow: hidden; }}
            .yt-btn {{ display: block; background: #ff0000; color: white; text-align: center; padding: 10px; text-decoration: none; font-weight: bold; }}
            .quiz-container {{ background: #fdf2e9; border-radius: 20px; padding: 30px; }}
            .ans-box {{ display: none; background: #e8f8f5; padding: 15px; border-radius: 10px; margin-top: 10px; border-left: 5px solid var(--secondary); }}
            .btn-check {{ background: #34495e; color: white; border: none; padding: 8px 15px; border-radius: 8px; cursor: pointer; }}
        </style>
        <script>
            function showAns(id) {{ 
                const el = document.getElementById(id);
                el.style.display = el.style.display === 'block' ? 'none' : 'block';
            }}
        </script>
    </head>
    <body>
        <div class="main-container">
            <div class="header">
                <h1 style="margin:0;">🧪 다니엘의 스마트 과학 리포트</h1>
                <p style="opacity:0.9;">교과서 핵심 요약부터 퀴즈까지 한 번에!</p>
            </div>

            <div class="section">
                <h2>📖 아빠가 정리한 핵심 노트</h2>
                <div class="study-card">
                    {"".join([f'<div class="summary-item"><div class="summary-number">{i+1}</div><div>{point}</div></div>' for i, point in enumerate(data['summary_points'])])}
                </div>
                <div class="lab-banner">
                    <a href="./danial_lab.html" class="lab-btn">🔬 나만의 온라인 실험실 입장하기</a>
                </div>
            </div>

            <div class="section">
                <h2>📺 아빠 추천 영상 학습</h2>
                <div class="youtube-grid">
    """

    # 유튜브 검색 및 추가
    for i, item in enumerate(data['youtube_plan'][:4]):
        res = youtube.search().list(q=f"중1 과학 {item['keyword']}", part='snippet', maxResults=1, type='video').execute()
        if res['items']:
            v = res['items'][0]
            report_html += f"""
                <div class="yt-card">
                    <div style="padding:15px; min-height:80px;"><b>{v['snippet']['title'][:40]}...</b></div>
                    <a href="https://www.youtube.com/watch?v={v['id']['videoId']}" target="_blank" class="yt-btn">▶ 영상 보기</a>
                </div>
            """

    report_html += """
                </div>
            </div>

            <div class="section">
                <h2>📝 실력 쑥쑥! 미니 테스트 (10문제)</h2>
                <div class="quiz-container">
    """

    for i, q in enumerate(data['quizzes']):
        options_html = "".join([f"<li>{opt}</li>" for opt in q.get('options', [])])
        report_html += f"""
            <div class="card">
                <p><b>Q{i+1}. {q['q']}</b></p>
                {f'<ul>{options_html}</ul>' if options_html else ''}
                <button class="btn-check" onclick="showAns('ans{i}')">정답 및 해설 확인</button>
                <div id="ans{i}" class="ans-box">
                    <b>정답: {q['a']}</b><br>
                    <small>💡 {q['ex']}</small>
                </div>
            </div>
        """

    report_html += """
                </div>
            </div>
            <div style="text-align:center; padding:40px; color:#999;">
                ❤️ 아빠가 다니엘을 위해 정성껏 만들었어. 화이팅!
            </div>
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(report_html)
    print("🎉 성공! 이제 git push 해서 다니엘에게 보여주자!")

except Exception as e:
    print(f"❌ 오류 발생: {e}")