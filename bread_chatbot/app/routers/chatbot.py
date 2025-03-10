from fastapi import APIRouter
from bread_chatbot.langchain_pipeline.pipeline import ask_chatbot
from pydantic import BaseModel


# ==================    <<  불러오기/경로지정  >> =========================

# 1. 라우터 설정
router = APIRouter()

# 2. 요청 모델 정의
class QuestionRequest(BaseModel):
    question: str

# ==================    <<  엔드 포인트  >> =========================

@router.post("/query_chatbot")
async def query_chatbot_endpoint(request: QuestionRequest):
    try:
        response = ask_chatbot(request.question)
        return {"answer": response}
    except Exception as e:
        print(f"채팅 처리 중 오류 발생: {str(e)}")
        return {"error": f"처리 중 오류가 발생했습니다: {str(e)}"}
