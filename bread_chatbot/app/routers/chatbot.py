from fastapi import APIRouter
from app.models import ChatRequest
from app.services import get_openai_response

# ==================    <<  불러오기/경로지정  >> =========================

# 1. 라우터 설정
router = APIRouter()

# ==================    <<  엔드 포인트  >> =========================

# 1. 챗봇 엔드포인트
@router.post("/chatbot_endpoint")  # django가 /chatbot_endpoint로 POST 요청
async def chatbot_endpoint(request: ChatRequest):
    print(request)
    try:
        if not request.question:
            return {"error": "질문을 입력해 주세요."}

        # 비동기로 django_chatbot 호출 -> OpenAPI 요청 끝날 떄까지 기다려서 응답 반환
        return await django_chatbot(request)

    except Exception as e:
        print(f"서버오류: {str(e)}")
        return {"error": f"서버오류: {str(e)}"}


# 2. OpenAI API 호출 -> AI 응답 생성
@router.post("/chatbot")
async def django_chatbot(request: ChatRequest):
    try:
        # openai API에 프롬프트 보내서 답변 받음
        openai_response = get_openai_response(request.question)
        # 응답 반환
        return {"answer": openai_response}
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        return {"error": f"OpenAI API 오류: {str(e)}"}