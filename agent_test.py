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

    # 7. 메인 리포트(index.html) 생성 로직 (학습 정리 & 퀴즈 추가)
    report_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>다니엘의 과학 실험실</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; max-width: 850px; margin: 0 auto; padding: 40px; background-color: #f4f7f6; }}
            .container {{ background: white; padding: 35px; border-radius: 25px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; border-bottom: 4px solid #3498db; padding-bottom: 15px; text-align: center; }}
            
            /* 학습 정리 섹션 스타일 */
            .study-summary {{ background: #eef7ff; padding: 25px; border-radius: 15px; margin: 30px 0; border-left: 8px solid #3498db; }}
            .study-summary h2 {{ color: #2980b9; margin-top: 0; }}
            .study-summary ul {{ padding-left: 20px; }}
            .study-summary li {{ margin-bottom: 10px; }}

            .lab-link {{ display: block; text-align: center; background: #e67e22; color: white; padding: 20px; border-radius: 15px; text-decoration: none; font-weight: bold; font-size: 1.2em; margin: 30px 0; transition: 0.3s; }}
            .lab-link:hover {{ background: #d35400; transform: scale(1.02); }}
            
            .video-card {{ border: 1px solid #e1e8ed; background: #ffffff; padding: 20px; margin-bottom: 25px; border-radius: 15px; }}
            .video-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; gap: 15px; }}
            .video-title {{ font-size: 1.1em; font-weight: bold; color: #2c3e50; line-height: 1.4; flex: 1; }}
            .youtube-btn {{ background: #ff0000; color: white; padding: 10px 18px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 0.95em; display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; flex-shrink: 0; box-shadow: 0 4px 0 #b30000; }}
            .daddy-tip {{ color: #27ae60; background: #eafaf1; padding: 15px; border-radius: 12px; border: 1px dashed #27ae60; }}

            /* 퀴즈 섹션 스타일 */
            .quiz-section {{ background: #fff4e5; padding: 25px; border-radius: 15px; margin-top: 40px; border: 2px solid #f39c12; }}
            .quiz-card {{ background: white; padding: 15px; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
            .quiz-btn {{ background: #34495e; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; margin-top: 10px; }}
            .ans-box {{ display: none; margin-top: 10px; padding: 10px; background: #d4edda; color: #155724; border-radius: 5px; font-weight: bold; }}
        </style>
        <script>
            function toggleAns(id) {{
                var x = document.getElementById(id);
                if (x.style.display === "none") {{ x.style.display = "block"; }} 
                else {{ x.style.display = "none"; }}
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🚀 다니엘의 과학 정복 리포트</h1>
            
            <div class="study-summary">
                <h2>📖 이번 주 핵심 개념 꽉 잡기!</h2>
                <ul>
                    <li><b>과학적 탐구:</b> 자연 현상에 의문을 갖고 객관적으로 해결하는 과정이야.</li>
                    <li><b>변인 통제 (가장 중요!):</b> 실험에서 <b>다르게 할 조건(조작 변인)</b>은 딱 하나만 정하고, 나머지는 <b>모두 같게(통제 변인)</b> 유지하는 거야.</li>
                    <li><b>지속 가능한 삶:</b> 미래 세대가 쓸 자원을 남기면서 현재 우리도 행복하게 살 수 있도록 환경을 보호하는 삶을 말해.</li>
                </ul>
            </div>

            <a href="./danial_lab.html" class="lab-link">🔬 아빠가 만든 미니 실험실 열기 (클릭!)</a>
            
            <div class="video-section">
                <h3 style="color:#2c3e50;">📺 추천 영상 학습 (영상을 보고 아래 퀴즈를 풀어봐!)</h3>
    """

    for item in data['youtube_plan']:
        query = f"중1 과학 {item['keyword']}"
        res = youtube.search().list(q=query, part='snippet', maxResults=1, type='video').execute()
        if res['items']:
            v = res['items'][0]
            clean_url = f"https://www.youtube.com/watch?v={v['id']['videoId']}"
            report_html += f"""
                <div class="video-card">
                    <div class="video-header">
                        <span class="video-title">🎥 {v['snippet']['title']}</span>
                        <a href="{clean_url}" class="youtube-btn" target="_blank">▶ 영상보기</a>
                    </div>
                    <div class="daddy-tip">{item['tip']}</div>
                </div>
            """

    report_html += """
            </div>

            <div class="quiz-section">
                <h2>📝 학습 체크! 미니 퀴즈</h2>
                
                <div class="quiz-card">
                    <p><b>Q1. (OX문제) 실험에서 결과를 정확하게 확인하려면 조작 변인을 여러 개 설정해야 한다?</b></p>
                    <button class="quiz-btn" onclick="toggleAns('ans1')">정답 확인</button>
                    <div id="ans1" class="ans-box">정답: X (조작 변인은 반드시 '하나'만 설정해야 결과가 명확해져!)</div>
                </div>

                <div class="quiz-card">
                    <p><b>Q2. (객관식) 다음 중 지속 가능한 삶을 위한 과학 기술의 역할로 적절하지 않은 것은?</b></p>
                    <p>1) 태양광 에너지 개발 <br> 2) 플라스틱 분해 미생물 연구 <br> 3) 무분별한 자원 채굴 확대 <br> 4) 오염 물질 회수 로봇 제작</p>
                    <button class="quiz-btn" onclick="toggleAns('ans2')">정답 확인</button>
                    <div id="ans2" class="ans-box">정답: 3번 (자원을 아껴 쓰고 순환시키는 것이 지속 가능한 삶의 핵심이야!)</div>
                </div>
            </div>

            <p style="text-align:center; margin-top:40px; color:#bdc3c7;">❤️ 아빠가 다니엘을 위해 정성껏 만들었단다! 화이팅!</p>
        </div>
    </body>
    </html>
    """

    # 최종 index.html 저장
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(report_html)

    print("🎉 [축성공] 모든 파일 생성 완료! 이제 git push 하러 가자!")

except Exception as e:
    print(f"❌ 최후의 수단 에러: {e}")