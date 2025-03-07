from pydantic import BaseModel

# ChatRequest : FastAPI가 데이터가 올바른지 자동으로 확인하게 하는 모델 (요청 데이터 모델 정의)
class ChatRequest(BaseModel):
    question: str  # user의 질문은 str 타입