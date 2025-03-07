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

# openai 단일 모델 엔드포인트
# @router.post("/chatbot")
# async def chatbot_endpoint(request: QuestionRequest):
#     response = pipeline.get_openai_response(request.question)
#     return {"answer": response}

# 질문 유형에 따른 통합 엔드포인트
@router.post("/chatbot")
async def chatbot_endpoint(request: QuestionRequest):
    """모든 유형의 질문을 처리하는 통합 엔드포인트"""
    try:
        # 질문 유형 감지 (간단한 키워드 기반 분류)
        question = request.question.lower()

        # 비즈니스 조언 관련 키워드 확인
        business_keywords = ["추천", "조언", "전략", "집중", "늘리기", "향상", "개선", "분석"]
        is_business_question = any(keyword in question for keyword in business_keywords)

        # 모델 비교 요청 확인
        compare_keywords = ["비교", "두 모델", "다른 모델"]
        is_compare_request = any(keyword in question for keyword in compare_keywords)

        if is_compare_request:
            # 모델 비교 요청인 경우
            return pipeline.compare_models(request.question)
        elif is_business_question:
            # 비즈니스 조언 질문인 경우
            advisor_pipeline = pipeline.create_business_advisor_pipeline()
            response = advisor_pipeline.invoke(request.question)
            return {"answer": response}
        else:
            # 일반 질문인 경우
            response = pipeline.get_openai_response(request.question)
            return {"answer": response}

    except Exception as e:
        print(f"채팅 처리 중 오류 발생: {str(e)}")
        return {"error": f"처리 중 오류가 발생했습니다: {str(e)}"}

# openai, claude 모델 비교 엔드포인트
@router.post("/compare")
async def compare_models(request: QuestionRequest):
    return {"comparison": pipeline.compare_models(request.question)}

# 비즈니스 모델 엔드포인트
@router.post("/business-advisor")
async def business_advisor_endpoint(request: QuestionRequest):

    # 🐕 만들면 삭제할 코드
    business_advice = pipeline.get_business_advice(request.question)
    return {"answer": business_advice}

    # 🐕 만들면 살릴 코드
    # # 비즈니스 어드바이저 파이프라인 가져오기
    # advisor_pipeline = pipeline.create_business_advisor_pipeline()
    #
    # # 질문에 대한 분석 및 조언 생성
    # response = advisor_pipeline.invoke(request.question)
    # return {"answer": response}