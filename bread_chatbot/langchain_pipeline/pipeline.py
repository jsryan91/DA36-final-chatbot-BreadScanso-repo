from bread_chatbot.langchain_pipeline.llm_utils import call_api, response_nlp
from bread_chatbot.langchain_pipeline.query_engine import extract_sql_from_response, generate_query, run_query

# 대화 이력을 저장할 전역 변수
chat_history = []

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
