import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")


# API 호출 함수 (LangChain 방식으로 간소화)
def call_api(prompt, model="gpt-4o"):
    """LangChain을 이용해 LLM API를 호출합니다."""
    try:
        chain = create_chain("You are an AI assistant specializing in SQL and data analysis.", model)
        return chain.invoke({"input": prompt})
    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")
        return f"오류가 발생했습니다. 다시 시도해주세요."


# 결과를 자연어로 변환 (함수 자체는 유지, 내부적으로 LangChain 활용)
def response_nlp(user_question, query, query_result, history_text=""):
    prompt = f"""당신은 베이커리의 친절한 매출 분석가입니다.
    이전 대화 기록:
    {history_text}
    사용자의 질문:
    {user_question}

    실행된 SQL 쿼리:
    {query}

    다음 SQL 실행 결과를 사용자에게 전달할 문장으로 변환하세요:
    {query_result}
    """
    return call_api(prompt)

# 🦜랭체인
def get_llm(model="gpt-4o"):
    """모델 이름에 따라 적절한 LLM 인스턴스를 반환합니다."""
    if model.startswith("gpt"):
        return ChatOpenAI(
            model=model,
            openai_api_key=openai_api_key,
            temperature=0.1
        )
    elif model.startswith("claude"):
        return ChatAnthropic(
            model=model,
            anthropic_api_key=anthropic_api_key,
            temperature=0.1
        )
    else:
        # 기본값은 gpt-4o
        return ChatOpenAI(
            model="gpt-4o",
            openai_api_key=openai_api_key,
            temperature=0.1
        )


# 간단한 프롬프트 체인 생성
def create_chain(system_prompt, model="gpt-4o"):
    """시스템 프롬프트와 모델을 입력받아 LangChain 체인을 생성합니다."""
    llm = get_llm(model)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])

    chain = prompt | llm | StrOutputParser()
    return chain