import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from bread_chatbot.langchain_pipeline.table_schema import TABLE_SCHEMA
from bread_chatbot.langchain_pipeline.llm_utils import create_chain
from langchain_community.utilities import SQLDatabase

# 환경 변수 로드
load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

# DB 연결 설정 (이제 query_engine.py에서도 engine을 사용할 수 있음)
DB_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
engine = create_engine(DB_URL)
db = SQLDatabase.from_uri(DB_URL)

# SQL 응답에서 실행 가능한 쿼리만 추출하는 함수 (자꾸 쿼리 외의 텍스트까지 인식해서 오류 발생 -> 텍스트 제외)
def extract_sql_from_response(response):
    # SQL 코드 블록이 있는지 확인
    if "```sql" in response and "```" in response.split("```sql")[1]:
        # 코드 블록 사이의 SQL 추출
        sql = response.split("```sql")[1].split("```")[0].strip()
        return sql
    # 코드 블록 없이 ```만 있는 경우 확인
    elif "```" in response:
        code_blocks = response.split("```")
        if len(code_blocks) >= 3:  # 최소한 앞뒤 텍스트와 코드 블록이 있어야 함
            return code_blocks[1].strip()
    # 코드 블록은 없지만 SQL 쿼리로 보이는 경우
    if "SELECT" in response.upper() and "FROM" in response.upper():
        return response.strip()
    # SQL을 찾지 못한 경우 원본 응답 반환
    return response

# 사용자 입력을 기반으로 SQL 쿼리를 생성
def generate_query(user_question, history_text=""):
    system_prompt = f"""사용자가 다음과 같은 질문을 합니다: '{user_question}'
    이전 대화 기록:
    {history_text}
    아래는 MySQL 데이터베이스의 테이블 스키마입니다:
    {TABLE_SCHEMA}
    사용자의 질문에 맞는 SQL 쿼리를 생성하세요.
    - MySQL 문법을 따를 것.
    - 제공된 TABLE_SCHEMA의 column만을 이용할 것. kiosk_paymentinfo, kiosk_orderitem 테이블에는 store가 없음.
    - LIMIT 10을 기본으로 포함하여 너무 많은 데이터를 가져오지 않도록 할 것.
    - 쿼리 작성 시 관계형 데이터베이스의 구조를 고려할 것.
    - 예시로, 테이블 간의 JOIN을 올바르게 사용해야 하며, 집계 함수는 필요한 경우에만 사용해야 한다는 점을 명심할 것.
    - 오직 SQL 쿼리만 반환하고 설명이나 코드 블록 표시(```) 또는 기타 텍스트는 포함하지 말 것.
    """
    sql_chain = create_chain(system_prompt)
    response = sql_chain.invoke({"input": user_question})
    return extract_sql_from_response(response)

# 질문 분석 및 응답 유형 분류 함수
def analyze_question_type(user_question, history_text=""):
    system_prompt = f"""당신은 베이커리 매출 분석 전문가입니다. 
    아래 테이블 스키마를 가진 데이터베이스를 활용해야 합니다:
    {TABLE_SCHEMA}

    위 질문에 대해 판단해주세요:
    1. 이 질문은 데이터베이스 조회가 필요한 질문인가요? (YES/NO)
    2. 만약 데이터베이스 조회가 필요하다면, 이 질문은:
       A. 단순 데이터 조회 및 집계가 필요한가요? (직접적인 데이터 요청)
       B. 결과에 대한 통계 분석이나 심층적 고찰이 필요한가요? (추세 분석, 의미 해석, 제안 등)

    다음 형식으로만 답변해주세요:
    - NEEDS_SQL: YES 또는 NO
    - ANALYSIS_TYPE: SIMPLE 또는 ADVANCED (NEEDS_SQL이 YES인 경우만)
    """
    analyzer_chain = create_chain(system_prompt)

    input_with_history = f"""이전 대화 기록:
    {history_text}
    사용자 질문 : '{user_question}'"""

    response = analyzer_chain.invoke({"input": input_with_history})

    # 응답에서 필요한 정보 추출
    needs_sql = "NEEDS_SQL: YES" in response.upper()

    analysis_type = "SIMPLE"  # 기본값
    if needs_sql and "ANALYSIS_TYPE: ADVANCED" in response.upper():
        analysis_type = "ADVANCED"

    return needs_sql, analysis_type

# SQL 결과에 대한 단순 응답 생성 -> True/SIMPLE
def simple_data_response(user_question, query, query_result, history_text=""):
    system_prompt = f"""당신은 Breadscanso 베이커리의 친절한 매출 분석가입니다.
    이전 대화 기록:
    {history_text}
    사용자의 질문:
    {user_question}
    실행된 SQL 쿼리:
    {query}
    다음 SQL 실행 결과를 사용자에게 전달할 문장으로 변환하세요:
    {query_result}
    - 매장 A는 서초점, 매장 B는 강남점으로 표현할 것.
    - 사용자 친화적으로 대답할 것.
    """
    simple_chain = create_chain(system_prompt)
    return simple_chain.invoke({"input": ""})

# SQL 결과에 대한 심층 분석 응답 생성 -> True/ADVANCED
def advanced_analysis_response(user_question, query, query_result, history_text=""):
    system_prompt = f"""당신은 Breadscanso 베이커리의 전문 매출 분석가입니다.
    이전 대화 기록:
    {history_text}
    사용자의 질문:
    {user_question}
    실행된 SQL 쿼리:
    {query}
    다음 SQL 실행 결과에 대한 심층 분석을 제공하세요:
    {query_result}

    다음을 포함하여 응답을 작성하세요:
    - 매장 A는 서초점, 매장 B는 강남점으로 표현할 것.
    - 데이터의 주요 패턴이나 추세를 파악할 것.
    - 데이터를 기반으로 필요시, 개선 방안이나 권장 사항을 베이커리 운영 전문가로서 제안할 것.
    - 전문적이고 통찰력 있는 응답을 제공할 것.
    - 핵심만 포함해서 400자 이내로 작성할 것.
    """
    advanced_chain = create_chain(system_prompt)
    return advanced_chain.invoke({"input": ""})


# SQL 쿼리 실행 후 결과를 반환
def run_query(sql_query):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            return [dict(row) for row in result.mappings().all()]
    except Exception as e:
        print(f"쿼리 실행 중 오류 발생: {e}")
        return [{"error": f"쿼리 실행 중 오류가 발생했습니다: {str(e)}"}]

# 맥락 기반 대화 응답 생성 (SQL 없이) -> False/Simple
def context_only_response(user_question, history_text=""):
    system_prompt = f"""당신은 Breadscanso 베이커리의 친절한 매출 분석가입니다. 데이터 분석 전문가로서, 베이커리 운영에 관한 일반적인 지식과 통찰력을 갖고 있습니다.
    이전 대화 기록:
    {history_text}
    사용자의 질문:
    {user_question}

    이것은 구체적인 데이터 조회가 필요 없는 질문입니다. 베이커리 전문가로서의 지식과 경험, 그리고 이전 대화 맥락에 기반하여 친절하고 도움이 되는 응답을 제공해주세요.
    응답은 데이터베이스 조회 없이도 충분히 답변 가능한 내용이어야 합니다.
    인사 혹은 감사 인사에는 일상 대화처럼 응답해야 합니다.
    """
    context_chain = create_chain(system_prompt)
    return context_chain.invoke({"input": user_question})

