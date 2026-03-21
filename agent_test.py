import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv
from googleapiclient.discovery import build

# 1. 설정 로드
load_dotenv()
GEMINI_KEY = os.getenv("SCIENCE_KEY")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")

genai.configure(api_key=GEMINI_KEY)
# 서버가 불안정할 땐 2.5-flash 대신 1.5-flash나 1.5-pro로 자동 전환되게 모델명을 리스트에 두자
# 하지만 네 계정은 2.5가 메인이니 일단 2.5로 시도!
model = genai.GenerativeModel('models/gemini-2.5-flash')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)

# 2. 주제 읽기
try:
    with open("today_study.txt", "r", encoding="utf-8") as f:
        target_content = f.read().strip()
except:
    target_content = "중학교 1학년 과학: I. 과학과 인류의 지속가능한 삶"

print(f"🚀 [Gemini 2.5] 다니엘 맞춤형 리포트 생성 시작...")

# 3. 프롬프트 (중학생 눈높이 용어 + 10문제 퀴즈)
prompt = f"""
중학교 1학년 학생 '다니엘'의 눈높이에서 [{target_content}] 주제를 정리해줘.
1. '변인 통제' 대신 '공정한 실험을 위해 똑같이 맞출 조건'이라는 쉬운 표현을 사용해.
2. 교과서 핵심 내용을 5가지 포인트로 아주 상세하고 다정하게 설명해줘.
3. 학습 확인을 위한 퀴즈 10문제(OX 5개, 객관식 5개)를 정답 및 해설과 함께 포함해줘.
4. 아래 JSON 형식으로만 응답해.

{{
  "summary_points": ["내용1", "내용2", "내용3", "내용4", "내용5"],
  "youtube_plan": [{{"keyword": "검색어", "tip": "설명"}}],
  "quizzes": [
    {{"type": "OX", "q": "질문", "a": "O/X", "ex": "해설"}},
    {{"type": "CHOICE", "q": "질문", "options": ["1", "2", "3", "4"], "a": 3, "ex": "해설"}}
  ]
}}
"""

def generate_with_retry(max_retries=3):
    for i in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return json.loads(response.text.replace('```json', '').replace('```', '').strip())
        except Exception as e:
            if i < max_retries - 1:
                print(f"⚠️ 서버가 바쁜가봐요. {i+1}번 재시도 중...")
                time.sleep(2)
            else:
                raise e

try:
    data = generate_with_retry()
    print("✅ 데이터 생성 완료!")

    # 4. index.html 생성 (세련된 디자인)
    report_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>다니엘의 스마트 과학실</title>
        <style>
            :root {{ --primary: #3498db; --secondary: #2ecc71; --accent: #e67e22; --bg: #f4f7f6; }}
            body {{ font-family: 'Malgun Gothic', sans-serif; background: var(--bg); color: #333; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 30px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, var(--primary), #8e44ad); color: white; padding: 50px 20px; text-align: center; }}
            .section {{ padding: 40px; border-bottom: 1px solid #eee; }}
            .study-card {{ background: #f9fbfd; border-radius: 20px; padding: 25px; border-left: 8px solid var(--primary); }}
            .lab-banner {{ background: url('https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1200&q=80') center/cover; height: 250px; border-radius: 20px; margin: 20px 0; display: flex; align-items: center; justify-content: center; }}
            .lab-btn {{ background: rgba(230, 126, 34, 0.95); color: white; padding: 18px 45px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.2em; backdrop-filter: blur(5px); }}
            .yt-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
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
                <p>아빠가 직접 코딩해서 만든 다니엘 전용 학습지!</p>
            </div>
            <div class="section">
                <h2>📖 핵심 요약 노트</h2>
                <div class="study-card">
                    {"".join([f'<p><b>{i+1}. </b> {point}</p>' for i, point in enumerate(data['summary_points'])])}
                </div>
                <div class="lab-banner">
                    <a href="./danial_lab.html" class="lab-btn">🔬 나만의 애니메이션 실험실 가기</a>
                </div>
            </div>
            <div class="section">
                <h2>📺 추천 영상</h2>
                <div class="yt-grid">
    """

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
                <h2>📝 학습 체크 퀴즈 (10문제)</h2>
                <div class="quiz-container">
    """

    for i, q in enumerate(data['quizzes']):
        opts = "".join([f"<li>{o}</li>" for o in q.get('options', [])])
        report_html += f"""
            <div class="q-card">
                <p><b>Q{i+1}. {q['q']}</b></p>
                {f'<ul style="list-style:none; padding:0;">{opts}</ul>' if opts else ''}
                <button class="check-btn" onclick="toggleAns('ans{i}')">정답 확인</button>
                <div id="ans{i}" class="ans-box">정답: {q['a']} <br><small>💡 {q['ex']}</small></div>
            </div>
        """

    report_html += """
                </div>
            </div>
            <div style="text-align:center; padding:40px; color:#bdc3c7;">❤️ 아빠가 다니엘을 위해 정성껏 만들었어!</div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(report_html)

    # 5. danial_lab.html 생성 (애니메이션 버전)
    lab_html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>다니엘의 얼음 실험실</title>
        <style>
            body { font-family: 'Malgun Gothic', sans-serif; background: #eef2f3; text-align: center; padding: 20px; }
            .lab-box { background: white; max-width: 500px; margin: 0 auto; padding: 30px; border-radius: 25px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
            .ice-container { height: 180px; display: flex; align-items: center; justify-content: center; margin: 20px 0; background: #f9fbfd; border-radius: 15px; position: relative; }
            .ice { width: 100px; height: 100px; background: linear-gradient(135deg, #fff, #abdfff); border-radius: 15px; transition: transform 0.1s; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #3498db; }
            .btn { background: #e67e22; color: white; border: none; padding: 15px; border-radius: 10px; cursor: pointer; width: 100%; font-weight: bold; }
            #timer { font-size: 2.5em; color: #e74c3c; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="lab-box">
            <h2>🔬 얼음 녹이기 실험</h2>
            <p>공정한 실험을 위해 <b>똑같은 조건</b>을 맞춰보자!</p>
            <div id="timer">00:00</div>
            <div class="ice-container"><div id="iceBlock" class="ice">ICE</div></div>
            <select id="drink" style="width:100%; padding:10px; border-radius:10px; margin-bottom:10px;">
                <option value="15">물 (빨름)</option><option value="35">주스 (중간)</option><option value="55">설탕물 (느림)</option>
            </select>
            <button class="btn" onclick="start()">실험 시작!</button>
            <p id="msg" style="margin-top:20px; font-weight:bold;"></p>
            <a href="./index.html" style="color:#3498db; text-decoration:none;">← 돌아가기</a>
        </div>
        <script>
            let t=0, timer=null;
            function start(){
                const ice=document.getElementById('iceBlock'), target=parseInt(document.getElementById('drink').value);
                t=0; if(timer) clearInterval(timer);
                timer=setInterval(()=>{
                    t++; document.getElementById('timer').innerText=`00:${String(t).padStart(2,'0')}`;
                    let s=1-(t/target); ice.style.transform=`scale(${s})`; ice.style.opacity=s;
                    if(t>=target){ clearInterval(timer); document.getElementById('msg').innerText="✅ 다 녹았다! 조건에 따라 속도가 다르지?"; ice.style.transform="scale(0)"; }
                },100);
            }
        </script>
    </body>
    </html>
    """
    with open("danial_lab.html", "w", encoding="utf-8") as f: f.write(lab_html)
    print("🎉 성공! 이제 깃허브로 전송하자!")

except Exception as e:
    print(f"❌ 최종 에러: {e}")