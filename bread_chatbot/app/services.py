import requests
import os
from dotenv import load_dotenv

# ==================    <<  불러오기/경로지정  >> =========================

# 1. OpenAI API 키 가져오기
# 환경 변수 로드
load_dotenv()
# OpenAI API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ==================    <<  유틸 함수  >> =========================

# OpenAI API 요청 -> 챗봇 응답 가져오기
def get_openai_response(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are an AI expert in bakery sales analysis."},
                {"role": "user", "content": prompt}
            ]
        }

        # OpenAI API에 데이터 보냄
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )

        # 응답 상태 코드 확인
        if response.status_code == 200:
            # JSON 응답 파싱
            result = response.json()

            # 안전하게 응답 데이터 추출
            if "choices" in result and len(result["choices"]) > 0:
                if "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
                    return result["choices"][0]["message"]["content"]
                else:
                    return "OpenAI 응답 구조 오류: 'message' 또는 'content' 키를 찾을 수 없습니다."
            else:
                return "OpenAI 응답 구조 오류: 'choices' 키를 찾을 수 없거나 비어 있습니다."
        else:
            return f"OpenAI API 오류: 상태 코드 {response.status_code}, 응답: {response.text}"

    except Exception as e:
        return f"OpenAI API 오류: {str(e)}"