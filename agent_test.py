import os
import json
import time
import datetime
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from googleapiclient.discovery import build

# ==========================================
# 1. 환경 설정 및 API 연결
# ==========================================
load_dotenv()
GEMINI_KEY = os.getenv("SCIENCE_KEY")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)

# ==========================================
# 2. 커리큘럼 및 파일명 설정
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

iso_date = datetime.date.today().isoformat()
today_str = datetime.date.today().strftime("%Y년 %m월 %d일")

report_file = f"report_w{current_week}.html"
lab_file = f"lab_w{current_week}.html"
github_url = f"https://damoayo.github.io/Science-For-Danial/{report_file}"

# ==========================================
# 3. 노션 기록 함수
# ==========================================
def save_to_notion(week_num, title_text, date_str, report_url, study_data):
    if not NOTION_TOKEN or not NOTION_DATABASE_ID: return
    url = "https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    # 노션 페이지 내부 블록 구성
    children = [
        {"object": "block", "type": "callout", "callout": {"rich_text": [{"text": {"content": f"W{week_num} 리포트가 도착했어!"}}], "icon": {"emoji": "🧪"}}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "📖 핵심 요약"}}]}}
    ]
    for p in study_data['summary_points']:
        children.append({"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": p}}]}})

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "icon": {"emoji": "🔬"},
        "properties": {
            "주제": {"title": [{"text": {"content": title_text}}]},
            "주차": {"number": week_num},
            "날짜": {"date": {"start": date_str}},
            "링크": {"url": report_url}
        },
        "children": children
    }
    requests.post(url, headers=headers, json=data)

# ==========================================
# 4. 데이터 생성 및 HTML 제작
# ==========================================
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

try:
    res = model.generate_content(prompt)
    study_data = json.loads(res.text.replace('```json', '').replace('```', '').strip())

    # --- 여기서부터 HTML 디자인 대수술 ---
    report_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>다니엘의 과학 도서관</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Nanum+Square+Round:wght@400;700;800&display=swap');
            :root {{ --main: #3498db; --point: #e67e22; --bg: #f8fafd; --text: #2c3e50; }}
            body {{ font-family: 'Nanum Square Round', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; line-height: 1.6; }}
            .header {{ background: linear-gradient(135deg, #6dd5ed, #2193b0); color: white; padding: 60px 20px; text-align: center; clip-path: ellipse(150% 100% at 50% 0%); }}
            .container {{ max-width: 800px; margin: -50px auto 50px; padding: 0 20px; }}
            .card {{ background: white; border-radius: 25px; padding: 35px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); margin-bottom: 30px; border: 1px solid #eff3f6; }}
            .point-box {{ border-left: 6px solid var(--main); background: #f0f7ff; padding: 20px; border-radius: 0 15px 15px 0; margin-bottom: 25px; position: relative; }}
            .point-num {{ position: absolute; left: -15px; top: -15px; background: var(--main); color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 4px solid white; }}
            .img-deco {{ width: 100%; height: 200px; border-radius: 20px; object-fit: cover; margin-bottom: 20px; }}
            .quiz-zone {{ background: #fff9f2; border: 2px dashed #ffdebd; border-radius: 25px; padding: 30px; }}
            .q-card {{ background: white; padding: 20px; border-radius: 15px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }}
            .btn-ans {{ background: var(--text); color: white; border: none; padding: 8px 18px; border-radius: 10px; cursor: pointer; font-size: 0.9em; }}
            .ans-box {{ display: none; background: #e8f8f5; padding: 15px; border-radius: 10px; margin-top: 10px; border-left: 5px solid #2ecc71; }}
            .lab-btn {{ display: block; text-align: center; background: var(--point); color: white; padding: 20px; border-radius: 15px; text-decoration: none; font-weight: 800; font-size: 1.2em; transition: 0.3s; }}
            .lab-btn:hover {{ transform: scale(1.02); box-shadow: 0 10px 20px rgba(230,126,34,0.3); }}
        </style>
        <script>function toggleAns(id){{ var x=document.getElementById(id); x.style.display=(x.style.display==='none'||x.style.display==='')?'block':'none'; }}</script>
    </head>
    <body>
        <div class="header">
            <h1 style="margin:0; font-size:2.2em;">🔬 다니엘의 스마트 과학 리포트</h1>
            <p style="opacity:0.9; font-weight:700; margin-top:10px;">{target_content}</p>
        </div>
        <div class="container">
            <div class="card">
                <img src="https://images.unsplash.com/photo-1518152006812-edab29b069ac?auto=format&fit=crop&w=800&q=80" class="img-deco">
                <h2 style="color:var(--main); margin-bottom:30px;">📖 아빠의 핵심 요약 노트</h2>
    """

    for i, p in enumerate(study_data['summary_points']):
        report_content += f"""
                <div class="point-box">
                    <div class="point-num">{i+1}</div>
                    <p style="margin:0; font-weight:700; color:#34495e; line-height:1.8;">{p}</p>
                </div>
        """

    report_content += f"""
                <a href="./{lab_file}" class="lab-btn">🧪 나만의 애니메이션 실험실 가기 →</a>
            </div>

            <div class="card quiz-zone">
                <h2 style="color:var(--point); text-align:center;">📝 실력 쑥쑥! 퀴즈 타임</h2>
    """

    for i, q in enumerate(study_data['quizzes']):
        opts = "".join([f"<li>· {o}</li>" for o in q.get('options', [])])
        report_content += f"""
                <div class="q-card">
                    <p style="font-weight:800;">Q{i+1}. {q['q']}</p>
                    {f'<ul style="list-style:none; padding:0 0 10px 10px; color:#666;">{opts}</ul>' if opts else ''}
                    <button class="btn-ans" onclick="toggleAns('ans{i}')">정답 확인</button>
                    <div id="ans{i}" class="ans-box">✨ 정답: <b>{q['a']}</b><br><small>{q['ex']}</small></div>
                </div>
        """

    report_content += """
            </div>
            <p style="text-align:center; color:#bdc3c7; margin-top:30px;">아빠가 다니엘을 위해 코드로 만든 사랑의 리포트 ❤️</p>
        </div>
    </body>
    </html>
    """
    with open(report_file, "w", encoding="utf-8") as f: f.write(report_content)
    
    # [히스토리 업데이트 및 index.html 생성 코드는 그대로 유지]
    # ... (생략하지만 실제 파일에는 포함되어야 함)
    
    save_to_notion(current_week, target_content, iso_date, github_url, study_data)
    print("🎉 웹사이트 디자인 개편 완료!")

except Exception as e:
    print(f"❌ 에러: {e}")