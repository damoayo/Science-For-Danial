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
output_filename = "youtube_guide.txt"
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

    # 리포트 작성 시작
    report = f"# 🚀 다니엘을 위한 정밀 과학 리포트\n\n**주제:** {target_content}\n\n"
    report += f"### 🔬 [아빠가 만든 실험실 열기](./{simulator_filename})\n\n---\n"

    # 유튜브 검색 실행
    for item in data['youtube_plan']:
        # 검색어 보정: '중1 과학'을 접두어로 붙여서 엉뚱한 결과 방지
        search_query = f"중1 과학 {item['keyword']}"
        
        search_res = youtube_client.search().list(
            q=search_query,
            part='snippet',
            maxResults=1,
            type='video',
            relevanceLanguage='ko'
        ).execute()

        if search_res['items']:
            v = search_res['items'][0]
            title = v['snippet']['title']
            # URL 생성 시 중복 방지 (videoId만 가져와서 깔끔하게 조합)
            video_id = v['id']['videoId']
            actual_url = f"https://www.youtube.com/watch?v={video_id}"
            
            report += f"### 📺 [{title}]({actual_url})\n"
            report += f"- **검색어:** `{search_query}`\n"
            report += f"- **꿀팁:** {item['tip']}\n\n---\n"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✅ 완료! 이제 링크랑 주제가 제대로 잡혔을 거야. 확인해 봐!")

except Exception as e:
    print(f"❌ 에러 발생: {e}")