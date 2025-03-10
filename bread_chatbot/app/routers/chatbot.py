from fastapi import APIRouter
from bread_chatbot.langchain_pipeline.pipeline.llm_logic import ask_chatbot
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

# 실행
# if __name__ == "__main__":
#     while True:
#         user_question = input("질문을 입력하세요: ")
#         if user_question.lower() == 'exit':
#             break
#         llm_response = ask_chatbot(user_question)
#         print("🤷🏻‍♀️: ", llm_response)