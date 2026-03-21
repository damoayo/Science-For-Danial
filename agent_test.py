import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. 환경 변수 및 API 세팅
load_dotenv()
API_KEY = os.getenv("SCIENCE_KEY")

if not API_KEY:
    raise ValueError("앗! .env 파일에서 SCIENCE_KEY를 못 찾았어.")

client = genai.Client(api_key=API_KEY)

# 2. 에이전트가 입출력할 파일 이름 설정
input_filename = "today_study.txt"
output_filename = "youtube_guide.txt"

# [핵심] 읽을 파일이 있는지 먼저 체크하고, 없으면 알아서 만들어주는 센스!
if not os.path.exists(input_filename):
    with open(input_filename, "w", encoding="utf-8") as f:
        f.write("I. 지권의 변화 - 2. 암석") # 기본 샘플을 넣어둠
    print(f"[{input_filename}] 파일이 없어서 새로 만들었어! 나중에 여기에 다른 단원명도 적어봐.")

# 3. 텍스트 파일에서 단원명 쓱 읽어오기
with open(input_filename, "r", encoding="utf-8") as f:
    target_chapter = f.read().strip()

if not target_chapter:
    raise ValueError(f"[{input_filename}] 파일이 텅 비어있네. 공부할 단원을 적고 다시 돌려줘!")

print(f"📚 에이전트가 인식한 오늘 공부할 단원: {target_chapter}")
print("다니엘 전용 과학 멘토가 리포트를 작성하고 파일로 저장하는 중...\n")

# 4. 에이전트 자아 및 프롬프트 세팅
mentor_persona = """
너는 중학교 1학년 다니엘을 위한 세상에서 가장 친절하고 유쾌한 과학 학습 멘토야.
아빠가 '과학 교재 단원명'을 주면, 다니엘이 재밌게 볼 수 있는 유튜브 검색 키워드 3개와 추천 이유를 써줘.
말투는 친근하게 하고, '아빠의 꿀팁'이라는 항목을 꼭 넣어줘.
"""

# 마크다운 형식으로 깔끔하게 뽑아달라고 명시함
prompt = f"오늘 다니엘이 공부할 단원은 [{target_chapter}]야. 유튜브 큐레이션 리포트를 마크다운 형식으로 가독성 좋게 작성해 줘."

# 5. API 호출 및 파일 쓰기(저장)
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=mentor_persona,
            temperature=0.7
        )
    )
    
    # AI가 준 답변을 텍스트 파일로 촥! 저장하기
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print(f"🎉 큐레이션 완료! 폴더를 확인해 봐. [{output_filename}] 파일이 예쁘게 만들어졌을 거야.")
    
except Exception as e:
    print(f"API 호출 중 에러 발생: {e}")