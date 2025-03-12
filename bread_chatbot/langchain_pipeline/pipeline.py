from bread_chatbot.langchain_pipeline.llm_utils import call_api, response_nlp
from bread_chatbot.langchain_pipeline.query_engine import extract_sql_from_response, generate_query, run_query, analyze_question_type, simple_data_response, advanced_analysis_response, context_only_response
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# 대화 이력을 저장할 전역 변수
message_history = ChatMessageHistory()

# 전체 흐름을 자동으로 실행, 대화 맥락 반영 (수정된 버전)
def ask_chatbot(user_question):
    recent_messages = message_history.messages[-10:] if message_history.messages else []
    history_text = "\n".join([
        f"Question: {msg.content}" if isinstance(msg, HumanMessage) else f"Answer: {msg.content}"
        for msg in recent_messages
    ])  # 최근 5개 대화 유지

    # 질문 유형 분류
    needs_sql, analysis_type = analyze_question_type(user_question, history_text)
    print(f"SQL 쿼리 필요 여부: {needs_sql}, 분석 유형: {analysis_type}")  # 디버깅용

    if needs_sql:
        # SQL 쿼리 생성
        query = generate_query(user_question, history_text)
        print(f"생성된 SQL 쿼리: {query}")  # 디버깅용

        # 쿼리 실행
        query_result = run_query(query)
        print(f"쿼리 결과: {query_result}")  # 디버깅용

        # 분석 유형에 따른 응답 생성
        if analysis_type == "SIMPLE":
            final_response = simple_data_response(user_question, query, query_result, history_text)
        else:  # ADVANCED
            final_response = advanced_analysis_response(user_question, query, query_result, history_text)
    else:
        # 맥락 기반 응답 생성
        final_response = context_only_response(user_question, history_text)
        query = "SQL 쿼리 없이 맥락 기반 응답"  # 로그용

    # 대화 기록 업데이트
    # chat_history.append(f"Q: {user_question}\nA: {final_response}")
    message_history.add_user_message(user_question)
    message_history.add_ai_message(final_response)

    return final_response