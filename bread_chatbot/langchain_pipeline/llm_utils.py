import os
from openai import OpenAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# 하나의 통합된 AI 요청 함수
def call_api(prompt, model="gpt-4o"):
# def call_api(prompt, model="claude-3-opus-20240229"):
    try:
        client = OpenAI(api_key=openai_api_key)
        # client = ChatAnthropic(api_key=anthorpic_aip_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an AI assistant specializing in SQL and data analysis."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")
        return f"오류가 발생했습니다. 다시 시도해주세요."

# 결과를 자연어로 변환
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
