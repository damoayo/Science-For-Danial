import os
import json
import time
import datetime
import requests # 노션 통신을 위한 라이브러리 추가
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

# 노션에 보낼 날짜 형식 (YYYY-MM-DD)
iso_date = datetime.date.today().isoformat()
today_str = datetime.date.today().strftime("%Y년 %m월 %d일")

report_file = f"report_w{current_week}.html"
lab_file = f"lab_w{current_week}.html"
# 네 깃허브 페이지 주소에 맞게 수정 (예: damoayo.github.io)
github_url = f"https://damoayo.github.io/Science-For-Danial/{report_file}"

# ... (중간의 프롬프트 작성 및 HTML(report_wOO.html, lab_wOO.html, index.html) 생성 코드는 이전과 100% 동일하게 유지. 너무 길어서 이 부분은 아까 완성한 코드 그대로 쓰면 돼!) ...
# *주의: 프롬프트 요청부터 index.html 파일 저장하는 부분까지는 이전에 성공한 코드 그대로 두면 됨!*

# ==========================================
# (이 아래 부분을 index.html 저장 코드가 끝난 맨 마지막에 추가해!)
# 3. 노션 데이터베이스에 자동 기록하기
# ==========================================
def save_to_notion(week_num, title_text, date_str, report_url):
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("⚠️ 노션 토큰이나 ID가 없어서 노션 기록은 건너뜁니다.")
        return

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 노션 표(Database) 속성에 맞춰서 데이터 조립
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "주제": {"title": [{"text": {"content": title_text}}]},
            "주차": {"number": week_num},
            "날짜": {"date": {"start": date_str}},
            "링크": {"url": report_url}
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("✅ 노션 데이터베이스에 성공적으로 기록됐어!")
        else:
            print(f"❌ 노션 기록 실패: {response.text}")
    except Exception as e:
        print(f"❌ 노션 통신 에러: {e}")

# 노션 기록 함수 실행!
save_to_notion(current_week, target_content, iso_date, github_url)
print("🎉 모든 작업(HTML 생성 + 깃허브 저장 + 노션 기록) 완료!")