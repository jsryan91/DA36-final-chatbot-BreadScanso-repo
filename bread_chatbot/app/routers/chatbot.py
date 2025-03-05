from fastapi import APIRouter
import os
from fastapi.responses import FileResponse
from app.models import ChatRequest
from app.services import generate_prompt, get_openai_response, generate_tts
from app.services import TTS_SAVE_PATH


# ==================    <<  불러오기/경로지정  >> =========================

# 1. 라우터 설정
router = APIRouter()

# ==================    <<  엔드 포인트  >> =========================

# 1. 챗봇 엔드포인트
@router.post("/chatbot_endpoint")  # django가 /chatbot_fastapi 엔드포인트로 POST 요청
async def chatbot_endpoint(request: ChatRequest):  # request가 ChatRequest 타입이므로, question, sales_data 자동 파싱
    try:
        if not request.question:
            return {"error": "질문을 입력해 주세요."}

        # 매출 데이터 검증
        if not request.sales_data:
            print("매출 데이터가 없습니다.")
            # 빈 데이터라도 에러가 나지 않게 기본값 설정
            request.sales_data = {"products": [], "summary": {}}

        # 비동기로 django_chatbot 호출 -> OpenAPI 요청 끝날 떄까지 기다려서 응답 반환
        return await django_chatbot(request)

    except Exception as e:
        print(f"서버오류: {str(e)}")
        return {"error": f"서버오류: {str(e)}"}


# 2. OpenAI API 호출 -> AI 응답 생성
@router.post("/chatbot")
async def django_chatbot(request: ChatRequest):
    try:
        # 사용자 질문 + 매출데이터를 하나의 프롬프트로 변환
        prompt = generate_prompt(request.question, request.sales_data)
        # openai API에 프롬프트 보내서 답변 받음
        openai_response = get_openai_response(prompt)
        # TTS 변환 / 변환 실패 시 None
        tts_file = generate_tts(openai_response) if openai_response else None
        # AI 응답, tts 파일 경로 반환
        return {"answer": openai_response, "tts_file": tts_file}
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        return {"error": f"OpenAI API 오류: {str(e)}"}

# 3. TTS 파일 제공 엔드포인트
# 생성된 파일 다운로드 / 브라우저에서 음성 재생
@router.get("/tts/{file_name}")
async def get_tts_file(file_name: str):
    file_path = os.path.join(TTS_SAVE_PATH, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", filename=file_name)
    return {"error": "파일을 찾을 수 없습니다."}



