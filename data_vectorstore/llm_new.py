from sqlalchemy import create_engine, text
from openai import OpenAI
from dotenv import load_dotenv
import pymysql
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

DB_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
engine = create_engine(DB_URL)

TABLE_SCHEMA = """
kiosk_orderinfo: order_id (PK), order_at(주문 일시: 날짜+시간), total_amount(주문 총액), store(A: 서초점 B: 강남점), earned_points(적립 포인트), final_amount(최종 결제 금액), total_count(합계 수량)
kiosk_orderitem: order_item_id (PK), order_id (FK to OrderInfo), item_id (FK to Item), item_count(주문 항목별 수량), item_total(주문 항목별 총액)
kiosk_paymentinfo: payment_id (PK), order_id (FK to OrderInfo), member_id (FK to Member, null: 비회원), payment_method(결제 수단, credit: 카드, epay: 간편결제), payment_status(결제 상태, 1: 결제 완료, 0: 결체 취소), pay_at(결제 일시: 날짜+시간), used_points(사용된 포인트)
menu_item: item_id (PK), item_name(제품명), store(A: 서초점 B: 강남점), sale_price(판매가), cost_price(원가), category(dessert: 디저트류, bread: 빵류), stock(재고), created_at(제품 등록 일시: 날짜+시간), best(인기상품 여부, boolean type), new(신상품 여부, boolean type), show(홈페이지 노출 여부, boolean type)
member_member: member_id (PK), name, sex(M: 남성, F: 여성), age_group(연령대: 20, 30, 40, 50, 60), total_spent(총 소비 금액), points(보유 포인트), last_visited(마지막 방문일: 날짜+시간), visit_count(방문 횟수), member_type(회원 유형), store(A: 서초점 B: 강남점, membertype==manager인 경우만 존재), earning_rate(적립 비율, membertype==manager인 경우만 존재)
"""

# 대화 이력을 저장할 전역 변수
chat_history = []


# 하나의 통합된 AI 요청 함수
def call_api(prompt, model="gpt-4o"):
    try:
        client = OpenAI(api_key=openai_api_key)
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


# 전체 흐름을 자동으로 실행, 대화 맥락 반영
def ask_chatbot(user_question):
    global chat_history
    history_text = "\n".join(chat_history[-5:])  # 최근 5개 대화 유지

    # SQL 쿼리 생성 (이미 extract_sql_from_response 내장)
    query = generate_query(user_question, history_text)
    print(f"생성된 SQL 쿼리: {query}")  # 디버깅용

    # 쿼리 실행
    query_result = run_query(query)
    print(f"쿼리 결과: {query_result}")  # 디버깅용

    # 결과를 자연어로 변환
    final_response = response_nlp(user_question, query, query_result, history_text)

    # 대화 기록 업데이트
    chat_history.append(f"Q: {user_question}\nA: {final_response}")

    return final_response


# 실행
if __name__ == "__main__":
    while True:
        user_question = input("질문을 입력하세요: ")
        if user_question.lower() == 'exit':
            break
        llm_response = ask_chatbot(user_question)
        print("🤷🏻‍♀️: ", llm_response)