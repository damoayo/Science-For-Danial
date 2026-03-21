import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from googleapiclient.discovery import build

# 1. 환경 변수 로드
load_dotenv()
GEMINI_KEY = os.getenv("SCIENCE_KEY")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")

# 2. 클라이언트 설정 (네 리스트에서 확인된 2.5 모델 사용!)
genai.configure(api_key=GEMINI_KEY)
# [핵심] 네 API 리스트에 있던 정확한 명칭으로 교체!
model = genai.GenerativeModel('models/gemini-2.5-flash') 
youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)

# 3. 학습 주제 읽기
try:
    with open("today_study.txt", "r", encoding="utf-8") as f:
        target_content = f.read().strip()
except FileNotFoundError:
    target_content = "중학교 1학년 과학: I. 과학과 인류의 지속가능한 삶"

print(f"🚀 [Gemini 2.5 모드] 주제 분석 시작: {target_content[:30]}...")

# 4. 프롬프트 구성
prompt = f"""
중1 과학 멘토로서 [{target_content}] 주제에 대해 아래 JSON 형식으로만 응답해. 
다른 말은 일절 하지 말고 마크다운 태그(```json) 없이 순수 JSON 텍스트만 줘.

{{
  "youtube_plan": [
    {{"keyword": "검색어", "tip": "아빠가 다니엘에게 해주는 다정한 설명"}}
  ],
  "simulator_html_code": "변인 통제 원리를 배우는 인터랙티브 HTML/JS 코드 (가독성 좋게)"
}}
"""

try:
    # 5. API 호출 및 데이터 파싱
    response = model.generate_content(prompt)
    clean_text = response.text.replace('```json', '').replace('```', '').strip()
    data = json.loads(clean_text)
    print("✅ Gemini 2.5가 데이터를 성공적으로 생성했어!")

    # 6. 시뮬레이터 파일 저장 (danial_lab.html)
    with open("danial_lab.html", "w", encoding="utf-8") as f:
        f.write(data['simulator_html_code'])

    # 7. 메인 리포트(index.html) 웹사이트 제작
    report_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>다니엘의 과학 실험실</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; max-width: 850px; margin: 0 auto; padding: 40px; background-color: #f0f4f8; }}
            .container {{ background: white; padding: 35px; border-radius: 25px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; border-bottom: 4px solid #3498db; padding-bottom: 15px; text-align: center; }}
            .lab-link {{ display: block; text-align: center; background: #e67e22; color: white; padding: 20px; border-radius: 15px; text-decoration: none; font-weight: bold; font-size: 1.2em; margin: 30px 0; transition: 0.3s; }}
            .lab-link:hover {{ background: #d35400; transform: scale(1.02); }}
            .video-section {{ margin-top: 30px; }}
            .video-card {{ border-left: 6px solid #3498db; background: #f9f9f9; padding: 20px; margin-bottom: 25px; border-radius: 0 15px 15px 0; }}
            .video-title {{ font-size: 1.1em; font-weight: bold; color: #2980b9; text-decoration: none; }}
            .daddy-tip {{ color: #27ae60; background: #eafaf1; padding: 10px; border-radius: 8px; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 다니엘을 위한 정밀 과학 리포트</h1>
            <p style="text-align:center; color:#7f8c8d;">주제: {target_content}</p>
            
            <a href="./danial_lab.html" class="lab-link">🔬 아빠가 만든 미니 실험실 열기 (클릭!)</a>
            
            <div class="video-section">
                <h3>📺 이번 주 추천 과학 영상</h3>
    """

    # 유튜브 연동 부분
    for item in data['youtube_plan']:
        query = f"중1 과학 {item['keyword']}"
        res = youtube.search().list(q=query, part='snippet', maxResults=1, type='video').execute()
        
        if res['items']:
            v = res['items'][0]
            v_url = f"[https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=){v['id']['videoId']}"
            report_html += f"""
                <div class="video-card">
                    <a href="{v_url}" class="video-title" target="_blank">🎥 {v['snippet']['title']}</a>
                    <p class="daddy-tip">👨‍🏫 <b>아빠의 꿀팁:</b> {item['tip']}</p>
                </div>
            """

    report_html += """
            </div>
            <p style="text-align:center; margin-top:40px; color:#bdc3c7;">❤️ 아빠가 다니엘을 위해 정성껏 만들었단다!</p>
        </div>
    </body>
    </html>
    """

    # 최종 index.html 저장
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(report_html)

    print("🎉 [축성공] 모든 파일 생성 완료! 이제 git push 하러 가자!")

except Exception as e:
    print(f"❌ 최후의수단 에러: {e}")