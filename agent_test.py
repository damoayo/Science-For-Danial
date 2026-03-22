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
# 본인의 깃허브 아이디에 맞게 이 주소를 꼭 확인해줘!
github_url = f"https://damoayo.github.io/Science-For-Danial/{report_file}"

# ==========================================
# 3. 노션 상세 페이지 기록 함수 (업그레이드 버전)
# ==========================================
def save_to_notion(week_num, title_text, date_str, report_url, study_data):
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("⚠️ 노션 토큰이나 ID가 없어서 노션 기록은 건너뜁니다.")
        return

    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 노션 페이지 내부 블록 구성
    children_blocks = [
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"text": {"content": f"이번 주 주제는 [{title_text}] 입니다. 아빠가 정리한 내용을 확인해봐!"}}],
                "icon": {"emoji": "💡"},
                "color": "blue_background"
            }
        },
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "📖 핵심 요약 노트"}}]}}
    ]

    for i, point in enumerate(study_data['summary_points']):
        children_blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"text": {"content": point}}],
                "icon": {"emoji": f"{i+1}️⃣"},
                "color": "gray_background"
            }
        })

    children_blocks.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "📝 학습 체크 퀴즈"}}]}})
    for i, q in enumerate(study_data['quizzes']):
        children_blocks.append({
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [{"text": {"content": f"Q{i+1}. {q['q']}"}}],
                "children": [{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"text": {"content": f"✅ 정답: {q['a']}\n💡 해설: {q['ex']}"}, "annotations": {"bold": True}}]}
                }]
            }
        })

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "icon": {"emoji": "🧪"},
        "properties": {
            "주제": {"title": [{"text": {"content": title_text}}]},
            "주차": {"number": week_num},
            "날짜": {"date": {"start": date_str}},
            "링크": {"url": report_url}
        },
        "children": children_blocks
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("✅ 노션 상세 페이지 기록 완료!")
    else:
        print(f"❌ 노션 실패: {response.text}")

# ==========================================
# 4. 데이터 생성 및 실행 로직
# ==========================================
prompt = f"""
중학교 1학년 학생 '다니엘'의 눈높이에서 [{target_content}] 주제를 정리해줘.
1. '변인 통제' 대신 '공정한 실험을 위해 똑같이 맞출 조건'이라는 쉬운 표현을 사용해.
2. 교과서 핵심 내용을 5가지 포인트로 아주 상세하고 다정하게 설명해줘.
3. 학습 확인을 위한 퀴즈 10문제(OX 5개, 객관식 5개)를 정답 및 해설과 함께 포함해줘.
4. 아래 JSON 형식으로만 응답해. 마크다운 기호 없이 순수 JSON만 출력해.
{{
  "summary_points": ["내용1", "내용2", "내용3", "내용4", "내용5"],
  "youtube_plan": [{{"keyword": "검색어", "tip": "설명"}}],
  "quizzes": [
    {{"type": "OX", "q": "질문", "a": "O/X", "ex": "해설"}},
    {{"type": "CHOICE", "q": "질문", "options": ["1", "2", "3", "4"], "a": 3, "ex": "해설"}}
  ]
}}
"""

def generate_with_retry():
    for i in range(3):
        try:
            res = model.generate_content(prompt)
            clean_json = res.text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_json)
        except Exception as e:
            time.sleep(2)
    return None

try:
    study_data = generate_with_retry()
    if not study_data: raise Exception("데이터 생성 실패")

    # [HTML 생성 부분] - 이 부분은 이전과 동일하게 유지!
    report_html = f""
    # (실제 코드에서는 여기에 아까 완성한 HTML 생성 코드가 들어갑니다.)

    # 5. 노션에 최종 기록
    save_to_notion(current_week, target_content, iso_date, github_url, study_data)
    print("🎉 모든 작업 완료!")

except Exception as e:
    print(f"❌ 에러: {e}")