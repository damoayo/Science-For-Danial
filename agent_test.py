import os
import json
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
from googleapiclient.discovery import build

# 1. 설정 및 클라이언트 초기화
load_dotenv()
GEMINI_KEY = os.getenv("SCIENCE_KEY")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")

ai_client = genai.Client(api_key=GEMINI_KEY)
youtube_client = build('youtube', 'v3', developerKey=YOUTUBE_KEY)

input_filename = "today_study.txt"
output_filename = "index.html"
simulator_filename = "danial_lab.html"

# 2. 오늘 공부할 내용 읽기
with open(input_filename, "r", encoding="utf-8") as f:
    target_content = f.read().strip()

print(f"🚀 [진행 중] '{target_content}' 주제로 정밀 검색 및 시뮬레이터 생성 시작...")

# 3. 제미나이에게 정교한 데이터 요청 (주제 이탈 방지 프롬프트)
prompt = f"""
너는 중1 과학 전문 멘토야. 반드시 다음 주제에만 집중해: [{target_content}]

작업 1: 유튜브 검색 플랜
- 중학교 1학년 수준에 딱 맞는 한국어 교육 영상만 찾아야 해. 
- 검색어는 반드시 '중1 과학 [주제]' 형식으로 구체적으로 짜줘.
- (중요) 고등학생용, 성인용 다큐멘터리, 자극적인 쇼츠는 절대 제외해.

작업 2: HTML 시뮬레이터
- 해당 주제의 원리를 깨달을 수 있는 상호작용 코드를 짜줘.

아래 JSON 형식만 응답해:
{{
  "youtube_plan": [
    {{"keyword": "검색어1", "tip": "이유1"}},
    {{"keyword": "검색어2", "tip": "이유2"}},
    {{"keyword": "검색어3", "tip": "이유3"}}
  ],
  "simulator_html_code": "..."
}}
"""

# 4. API 호출 (모델명과 형식을 최신 규격으로 수정!)
try:
    response = ai_client.models.generate_content(
        model='gemini-1.5-flash-latest', # 'models/gemini-1.5-flash' 대신 이렇게만 써봐!
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            # 혹시 몰라서 응답 형식을 JSON으로 강제하는 옵션도 추가했어
            response_mime_type="application/json" 
        )
    )
    
    # JSON 파싱 부분 (response_mime_type을 쓰면 마크다운 태그 없이 순수 JSON만 와서 더 안전해!)
    data = json.loads(response.text)
    
    # HTML 저장
    with open(simulator_filename, "w", encoding="utf-8") as f:
        f.write(data['simulator_html_code'])

    # 1. 리포트 본문 작성 (HTML 형식으로 작성해서 웹브라우저에서 바로 보이게 함)
    # 스타일을 살짝 넣어서 아빠가 만든 티를 팍팍 내보자!
    report_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>다니엘의 과학 큐레이션</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 40px; background-color: #f4f7f6; }}
            .container {{ background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            .lab-link {{ display: inline-block; background: #e67e22; color: white; padding: 15px 25px; border-radius: 12px; text-decoration: none; font-weight: bold; margin: 20px 0; }}
            .video-card {{ border-left: 5px solid #3498db; background: #f9f9f9; padding: 15px; margin-bottom: 20px; border-radius: 0 10px 10px 0; }}
            .video-link {{ color: #2980b9; font-weight: bold; font-size: 1.1em; }}
            .tip {{ color: #27ae60; font-style: italic; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 다니엘을 위한 정밀 과학 리포트</h1>
            <p><b>주제:</b> {target_content}</p>
            
            <a href="./{simulator_filename}" class="lab-link">🔬 아빠가 만든 미니 실험실 열기</a>
            <p><i>(먼저 실험실에서 원리를 만져보고 아래 영상을 보면 이해가 쏙쏙 될 거야!)</i></p>
            <hr>
    """

    # 2. 유튜브 검색 결과 추가 (반복문 안에서 HTML 태그로 감싸기)
    for item in data['youtube_plan']:
        search_query = f"중1 과학 {item['keyword']}"
        search_res = youtube_client.search().list(
            q=search_query, part='snippet', maxResults=1, type='video', relevanceLanguage='ko'
        ).execute()

        if search_res['items']:
            v = search_res['items'][0]
            video_id = v['id']['videoId']
            actual_url = f"https://www.youtube.com/watch?v={video_id}"
            title = v['snippet']['title']
            
            report_html += f"""
            <div class="video-card">
                <a href="{actual_url}" class="video-link" target="_blank">📺 {title}</a><br>
                <small>검색어: {search_query}</small>
                <p class="tip">👨‍🏫 <b>아빠의 꿀팁:</b> {item['tip']}</p>
            </div>
            """

    # 3. HTML 마무리 태그 및 파일 저장
    report_html += """
        </div>
    </body>
    </html>
    """

    # 최종 결과물을 index.html로 저장 (GitHub Pages의 대문 파일)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(report_html)
    
    print("✅ 완료! 이제 링크랑 주제가 제대로 잡혔을 거야. 확인해 봐!")

except Exception as e:
    print(f"❌ 에러 발생: {e}")