import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from bread_chatbot.langchain_pipeline.table_schema import TABLE_SCHEMA
from bread_chatbot.langchain_pipeline.llm_utils import call_api

# 환경 변수 로드
load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

# DB 연결 설정 (이제 query_engine.py에서도 engine을 사용할 수 있음)
DB_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
engine = create_engine(DB_URL)

# SQL 응답에서 실행 가능한 쿼리만 추출하는 함수
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
    prompt = f"""사용자가 다음과 같은 질문을 합니다: '{user_question}'
    이전 대화 기록:
    {history_text}
    아래는 MySQL 데이터베이스의 테이블 스키마입니다:
    {TABLE_SCHEMA}
    사용자의 질문에 맞는 SQL 쿼리를 생성하세요.
    - MySQL 문법을 따를 것.
    - LIMIT 10을 기본으로 포함하여 너무 많은 데이터를 가져오지 않도록 할 것.
    - 쿼리 작성 시 관계형 데이터베이스의 구조를 고려할 것.
    - 예시로, 테이블 간의 JOIN을 올바르게 사용해야 하며, 집계 함수는 필요한 경우에만 사용해야 한다는 점을 명심할 것.
    - 오직 SQL 쿼리만 반환하고 설명이나 코드 블록 표시(```) 또는 기타 텍스트는 포함하지 마세요.
    """
    response = call_api(prompt)
    return extract_sql_from_response(response)

# SQL 쿼리 실행 후 결과를 반환
def run_query(sql_query):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            return [dict(row) for row in result.mappings().all()]
    except Exception as e:
        print(f"쿼리 실행 중 오류 발생: {e}")
        return [{"error": f"쿼리 실행 중 오류가 발생했습니다: {str(e)}"}]
