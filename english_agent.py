import os
import json
import datetime
import google.generativeai as genai

# 1. 환경설정 및 게시판 데이터 가져오기
GEMINI_KEY = os.getenv("SCIENCE_KEY") # 과학 때 썼던 키 그대로 사용!
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

issue_title = os.getenv("ISSUE_TITLE", "Lesson 3") # 예: "Lesson 3"
issue_body = os.getenv("ISSUE_BODY", "No data") # 선생님 코멘트 + 대화록

today_str = datetime.date.today().strftime("%Y년 %m월 %d일")
html_filename = f"english_{datetime.date.today().strftime('%Y%m%d')}.html"

# 2. 교재 지식 창고 (Lesson 별 핵심 내용)
curriculum_db = {
    "Lesson 3": {
        "title": "Spending Time with Grandparents",
        "grammar": "빈도부사 (usually, often, rarely, never)",
        "key_patterns": ["What do you usually do after school?", "How often do you go shopping?", "I never sleep late."]
    },
    "Lesson 4": {
        "title": "How Great the Idea Is!",
        "grammar": "감탄문과 미래시제 (will)",
        "key_patterns": ["What an exciting game that was!", "I will go on a trip."]
    }
    # 앞으로 진도 나갈 때마다 여기에 추가하면 돼!
}

# 제목(예: Lesson 3)을 바탕으로 이번 주 교재 정보 가져오기
lesson_info = curriculum_db.get(issue_title, curriculum_db["Lesson 3"])

# 3. Gemini에게 지시할 프롬프트
prompt = f"""
너는 중학교 1학년 다니엘의 1:1 영어 코치야.
다음 [선생님 피드백 및 대화록]과 [이번 주 교과서 진도]를 바탕으로 다니엘을 위한 융합 학습 데이터를 만들어줘.

[이번 주 교과서 진도: {issue_title}]
- 주제: {lesson_info['title']}
- 핵심 문법: {lesson_info['grammar']}
- 주요 패턴: {lesson_info['key_patterns']}

[선생님 피드백 및 대화록]
{issue_body}

다음 3가지 내용을 포함해서 JSON 형식으로만 응답해. (마크다운 기호 금지)
{{
  "review_note": "대화록에서 틀렸던 문장 1개(Original)와 교정된 문장(Better), 그리고 아빠의 다정한 조언(한국어)",
  "preview_sentence": "이번 주 교과서 핵심 문법/패턴을 활용하여, 다니엘이 다음 화상 수업 때 원어민 선생님에게 자신 있게 써먹을 수 있는 완벽한 문장 1개와 그 한국어 뜻",
  "quiz_korean": "조립 게임에 쓸 교정된 문장의 한국어 뜻",
  "quiz_words": ["조립", "게임에", "쓸", "영어", "단어들", "리스트", "(순서 섞어서)"],
  "quiz_answer": "완벽한 영어 정답 문장"
}}
"""

try:
    # 4. Gemini 데이터 생성
    res = model.generate_content(prompt)
    data = json.loads(res.text.replace('```json', '').replace('```', '').strip())

    # 5. 영작 게임 위젯 JSON 조립
    widget_json = {
      "component": "LlmGeneratedComponent",
      "props": {
        "height": "500px",
        "prompt": f"Create an interactive English Sentence Builder widget. Initial state: Show a Korean sentence: '{data['quiz_korean']}' and draggable/clickable English word blocks scattered randomly: {data['quiz_words']}. UI: Clean, playful, modern interface. Include an empty drop zone with slots for the words. The user clicks or drags blocks into the slots. Include a 'Check Answer' button. If the exact order '{data['quiz_answer']}' is achieved, show a bright green success message ('Perfect!'). If wrong, highlight incorrect blocks in red and provide a hint. Smooth animations."
      }
    }
    widget_string = json.dumps(widget_json)

    # 6. HTML 웹사이트 디자인 생성
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>다니엘의 Daily English</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Nanum+Square+Round:wght@400;700;800&display=swap');
            body {{ font-family: 'Nanum Square Round', sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 20px; }}
            .container {{ max-width: 800px; margin: auto; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .header h1 {{ color: #2c3e50; font-size: 2.5em; }}
            .card {{ background: white; border-radius: 20px; padding: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 30px; }}
            .tag {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; font-weight: bold; margin-bottom: 15px; }}
            .tag-review {{ background: #e74c3c; }}
            .tag-preview {{ background: #3498db; }}
            .comment {{ background: #fff3cd; padding: 15px; border-left: 5px solid #f1c40f; border-radius: 0 10px 10px 0; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📚 다니엘의 10분 영어 스낵</h1>
                <p>{today_str} | {issue_title}: {lesson_info['title']}</p>
            </div>

            <div class="card">
                <span class="tag tag-review">Part 1. 오답 노트</span>
                <h2 style="margin-top:0;">어제 놓친 문장, 오늘 완벽하게!</h2>
                <p>👉 <b>{data['review_note']}</b></p>
            </div>

            <div class="card">
                <span class="tag tag-preview">Part 2. 다음 수업 치트키</span>
                <h2 style="margin-top:0;">선생님을 깜짝 놀라게 할 한마디!</h2>
                <div class="comment">
                    <p style="font-size: 1.2em; font-weight: bold; color: #2980b9;">"{data['preview_sentence']}"</p>
                </div>
            </div>

            <div class="card">
                <h2>🎮 Part 3. 오늘의 영작 짐(Gym)</h2>
                <p>배운 문장을 직접 조립해 봐!</p>
                <script type="application/json">{widget_string}</script>
            </div>
        </div>
    </body>
    </html>
    """

    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ {html_filename} 생성 완료!")

except Exception as e:
    print(f"❌ 에러 발생: {e}")