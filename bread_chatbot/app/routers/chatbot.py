from fastapi import APIRouter
<<<<<<< HEAD
from app.models import ChatRequest
from app.services import get_openai_response
=======
from bread_chatbot.langchain_pipeline.pipeline import LangChainPipeline
from pydantic import BaseModel

>>>>>>> 38189585a3a38424c578bc22d7d4562a15bcb184

# ==================    <<  불러오기/경로지정  >> =========================

# 1. 라우터 설정
router = APIRouter()

# 2. 파이프라인
pipeline = LangChainPipeline()

# 3. 요청 모델 정의
class QuestionRequest(BaseModel):
    question: str

# ==================    <<  엔드 포인트  >> =========================

<<<<<<< HEAD
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
=======
>>>>>>> 38189585a3a38424c578bc22d7d4562a15bcb184
@router.post("/chatbot")
async def business_advisor_endpoint(request: QuestionRequest):
    try:
<<<<<<< HEAD
        # openai API에 프롬프트 보내서 답변 받음
        openai_response = get_openai_response(request.question)
        # 응답 반환
        return {"answer": openai_response}
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        return {"error": f"OpenAI API 오류: {str(e)}"}
=======
        business_advice = pipeline.get_business_advice(request.question)
        return {"answer": business_advice}
    except Exception as e:
        print(f"채팅 처리 중 오류 발생: {str(e)}")
        return {"error": f"처리 중 오류가 발생했습니다: {str(e)}"}
>>>>>>> 38189585a3a38424c578bc22d7d4562a15bcb184
