import os
import json
import time
import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from googleapiclient.discovery import build

# ==========================================
# 1. 환경 설정 및 API 연결
# ==========================================
load_dotenv()
GEMINI_KEY = os.getenv("SCIENCE_KEY")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)

# ==========================================
# 2. 커리큘럼 및 히스토리(목차) 관리
# ==========================================
curriculum = [
    "중학교 1학년 과학: 1. 과학과 인류의 지속가능한 삶",
    "중학교 1학년 과학: 2. 지각의 물질 (광물과 암석)",
    "중학교 1학년 과학: 3. 지각의 변화 (지진과 화산)",
    "중학교 1학년 과학: 4. 여러 가지 힘 (중력과 탄성력)",
    "중학교 1학년 과학: 5. 여러 가지 힘 (마찰력과 부력)",
    "중학교 1학년 과학: 6. 물질의 상태 변화 (고체, 액체, 기체)",
    "중학교 1학년 과학: 7. 물질의 상태 변화와 열 에너지",
    "중학교 1학년 과학: 8. 기체의 성질 (보일 법칙과 샤를 법칙)",
    "중학교 1학년 과학: 9. 빛과 파동 (빛의 반사와 굴절)",
    "중학교 1학년 과학: 10. 빛과 파동 (파동과 소리)",
    "중학교 1학년 과학: 11. 생물의 다양성과 분류",
    "중학교 1학년 과학: 12. 생물 다양성의 보전"
]

current_week = datetime.date.today().isocalendar()[1]
topic_index = current_week % len(curriculum)
target_content = curriculum[topic_index]
today_str = datetime.date.today().strftime("%Y년 %m월 %d일")

# 매주 생성될 파일 이름 설정
report_file = f"report_w{current_week}.html"
lab_file = f"lab_w{current_week}.html"

# 히스토리 파일 읽기 (없으면 새로 생성)
HISTORY_FILE = "history.json"
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = {}

print(f"📅 [자동 진도 시스템] 이번 주 주제: {target_content} (W{current_week})")

# ==========================================
# 3. AI 리포트 생성 요청
# ==========================================
prompt = f"""
중학교 1학년 학생 '다니엘'의 눈높이에서 [{target_content}] 주제를 정리해줘.
1. 어려운 한자어 대신 '공정한 실험을 위해 똑같이 맞출 조건'과 같이 쉬운 표현을 사용해.
2. 교과서 핵심 내용을 5가지 포인트로 아주 상세하고 다정하게 설명해줘.
3. 학습 확인을 위한 퀴즈 10문제(OX 5개, 객관식 5개)를 정답 및 해설과 함께 포함해줘.
4. 아래 JSON 형식으로만 응답해 (절대 마크다운 기호 없이 순수 JSON 텍스트만 출력).

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
            res = model.generate_content(prompt)
            return json.loads(res.text.replace('```json', '').replace('```', '').strip())
        except Exception as e:
            if i < max_retries - 1:
                print(f"⚠️ 서버 응답 지연. {i+1}번 재시도 중...")
                time.sleep(2)
            else:
                raise e

try:
    data = generate_with_retry()
    print("✅ 데이터 생성 완료! HTML 제작 시작...")

    # ==========================================
    # 4. 개별 주차 리포트 (report_wOO.html) 생성
    # ==========================================
    report_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>{target_content}</title>
        <style>
            :root {{ --primary: #3498db; --secondary: #2ecc71; --accent: #e67e22; --bg: #f4f7f6; }}
            body {{ font-family: 'Malgun Gothic', sans-serif; background: var(--bg); color: #333; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 30px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, var(--primary), #8e44ad); color: white; padding: 40px 20px; text-align: center; position: relative; }}
            .back-link {{ position: absolute; top: 20px; left: 20px; color: white; text-decoration: none; font-weight: bold; background: rgba(0,0,0,0.2); padding: 8px 15px; border-radius: 10px; }}
            .section {{ padding: 40px; border-bottom: 1px solid #eee; }}
            .study-card {{ background: #f9fbfd; border-radius: 20px; padding: 25px; border-left: 8px solid var(--primary); }}
            .lab-banner {{ background: url('https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1200&q=80') center/cover; height: 200px; border-radius: 20px; margin: 20px 0; display: flex; align-items: center; justify-content: center; }}
            .lab-btn {{ background: rgba(230, 126, 34, 0.95); color: white; padding: 15px 40px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.2em; }}
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
                <a href="index.html" class="back-link">← 전체 목차로 가기</a>
                <h1 style="margin:0; padding-top:20px;">{target_content}</h1>
                <p style="margin-top:10px; opacity:0.9;">아빠가 직접 코딩해서 만든 이번 주 학습지!</p>
            </div>
            <div class="section">
                <h2>📖 핵심 요약 노트</h2>
                <div class="study-card">
                    {"".join([f'<p style="margin-bottom:15px; line-height:1.7;"><b>{i+1}. </b> {point}</p>' for i, point in enumerate(data['summary_points'])])}
                </div>
                <div class="lab-banner">
                    <a href="./{lab_file}" class="lab-btn">🔬 나만의 애니메이션 실험실 가기</a>
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
            report_html += f"""<div class="yt-card"><div style="padding:15px; font-weight:bold; height:50px; overflow:hidden;">{v['snippet']['title']}</div><a href="https://www.youtube.com/watch?v={v['id']['videoId']}" target="_blank" class="yt-btn">▶ 영상 보기</a></div>"""

    report_html += """</div></div><div class="section"><h2>📝 학습 체크 퀴즈 (10문제)</h2><div class="quiz-container">"""
    for i, q in enumerate(data['quizzes']):
        opts = "".join([f"<li style='margin-bottom:5px;'>{o}</li>" for o in q.get('options', [])])
        report_html += f"""<div class="q-card"><p><b>Q{i+1}. {q['q']}</b></p>{f'<ul style="list-style:none; padding-left:10px;">{opts}</ul>' if opts else ''}<button class="check-btn" onclick="toggleAns('ans{i}')">정답 확인</button><div id="ans{i}" class="ans-box">정답: {q['a']} <br><small>💡 {q['ex']}</small></div></div>"""
    report_html += """</div></div><div style="text-align:center; padding:40px; color:#bdc3c7;">❤️ 아빠가 다니엘을 위해 정성껏 만들었어!</div></div></body></html>"""
    
    with open(report_file, "w", encoding="utf-8") as f: 
        f.write(report_html)

    # ==========================================
    # 5. 개별 주차 애니메이션 실험실 (lab_wOO.html) 생성
    # ==========================================
    lab_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>얼음 실험실</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; background: #eef2f3; text-align: center; padding: 20px; }}
            .lab-box {{ background: white; max-width: 500px; margin: 0 auto; padding: 30px; border-radius: 25px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }}
            .ice-container {{ height: 180px; display: flex; align-items: center; justify-content: center; margin: 20px 0; background: #f9fbfd; border-radius: 15px; position: relative; }}
            .ice {{ width: 100px; height: 100px; background: linear-gradient(135deg, #fff, #abdfff); border-radius: 15px; transition: transform 0.1s; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #3498db; }}
            .btn {{ background: #e67e22; color: white; border: none; padding: 15px; border-radius: 10px; cursor: pointer; width: 100%; font-weight: bold; font-size: 1.1em;}}
            #timer {{ font-size: 2.5em; color: #e74c3c; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="lab-box">
            <h2>🔬 얼음 녹이기 실험</h2>
            <div id="timer">00:00</div>
            <div class="ice-container"><div id="iceBlock" class="ice">ICE</div></div>
            <select id="drink" style="width:100%; padding:10px; border-radius:10px; margin-bottom:10px; font-size: 1em;">
                <option value="15">물 (빨름)</option><option value="35">주스 (중간)</option><option value="55">설탕물 (느림)</option>
            </select>
            <button class="btn" onclick="start()">실험 시작!</button>
            <p id="msg" style="margin-top:20px; font-weight:bold;"></p>
            <a href="./{report_file}" style="color:#3498db; text-decoration:none; display:inline-block; margin-top:15px; font-weight:bold;">← 이번 주 리포트로 돌아가기</a>
        </div>
        <script>
            let t=0, timer=null;
            function start(){{
                const ice=document.getElementById('iceBlock'), target=parseInt(document.getElementById('drink').value);
                t=0; if(timer) clearInterval(timer);
                ice.style.transform="scale(1)"; ice.style.opacity="1"; document.getElementById('msg').innerText="";
                timer=setInterval(()=>{{
                    t++; document.getElementById('timer').innerText=`00:${{String(t).padStart(2,'0')}}`;
                    let s=1-(t/target); ice.style.transform=`scale(${{s}})`; ice.style.opacity=s;
                    if(t>=target){{ clearInterval(timer); document.getElementById('msg').innerHTML="✅ 다 녹았다!<br>조건에 따라 속도가 다르지?"; ice.style.transform="scale(0)"; }}
                }},100);
            }}
        </script>
    </body>
    </html>
    """
    with open(lab_file, "w", encoding="utf-8") as f: 
        f.write(lab_html)

    # ==========================================
    # 6. 히스토리 기록 업데이트
    # ==========================================
    history[str(current_week)] = {
        "title": target_content,
        "date": today_str,
        "report_file": report_file
    }
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

    # ==========================================
    # 7. 메인 대시보드 (index.html) 생성
    # ==========================================
    # 히스토리를 최신순으로 정렬해서 보여주기
    sorted_history = sorted(history.items(), key=lambda x: int(x[0]), reverse=True)
    
    index_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>다니엘의 과학 포털</title>
        <style>
            :root {{ --primary: #2c3e50; --accent: #3498db; --bg: #ecf0f1; }}
            body {{ font-family: 'Malgun Gothic', sans-serif; background: var(--bg); padding: 40px 20px; }}
            .dashboard {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 20px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            h1 {{ text-align: center; color: var(--primary); margin-bottom: 40px; border-bottom: 3px solid var(--accent); padding-bottom: 20px; }}
            .history-list {{ display: flex; flex-direction: column; gap: 15px; }}
            .history-card {{ display: flex; align-items: center; justify-content: space-between; padding: 20px; background: #f8f9fa; border-radius: 12px; border-left: 6px solid var(--accent); text-decoration: none; color: #333; transition: 0.2s; }}
            .history-card:hover {{ transform: translateX(5px); background: #eef2f5; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
            .week-badge {{ background: var(--accent); color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.9em; font-weight: bold; }}
            .card-title {{ font-size: 1.1em; font-weight: bold; margin: 5px 0; }}
            .card-date {{ font-size: 0.85em; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <h1>📚 다니엘의 과학 지식 도서관</h1>
            <p style="text-align:center; color:#7f8c8d; margin-bottom:30px;">아빠가 매주 만들어주는 과학 리포트 모음이야. 복습하고 싶을 때 언제든 눌러봐!</p>
            <div class="history-list">
    """
    
    for week_num, info in sorted_history:
        index_html += f"""
            <a href="{info['report_file']}" class="history-card">
                <div>
                    <div class="week-badge">Week {week_num}</div>
                    <div class="card-title">{info['title']}</div>
                    <div class="card-date">{info['date']} 생성됨</div>
                </div>
                <div style="font-size: 1.5em; color: #3498db;">▶</div>
            </a>
        """

    index_html += """
            </div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print("🎉 자동 목차 시스템 및 전체 파일 생성 완료!")

except Exception as e:
    print(f"❌ 최종 에러: {e}")