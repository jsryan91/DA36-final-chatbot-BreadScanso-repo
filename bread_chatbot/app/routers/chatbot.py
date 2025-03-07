from fastapi import APIRouter
from bread_chatbot.langchain_pipeline.pipeline import LangChainPipeline
from pydantic import BaseModel


# ==================    <<  불러오기/경로지정  >> =========================

# 1. 라우터 설정
router = APIRouter()

# 2. 파이프라인
pipeline = LangChainPipeline()

# 3. 요청 모델 정의
class QuestionRequest(BaseModel):
    question: str

# ==================    <<  엔드 포인트  >> =========================

@router.post("/chatbot")
async def business_advisor_endpoint(request: QuestionRequest):
    try:
        business_advice = pipeline.get_business_advice(request.question)
        return {"answer": business_advice}
    except Exception as e:
        print(f"채팅 처리 중 오류 발생: {str(e)}")
        return {"error": f"처리 중 오류가 발생했습니다: {str(e)}"}
