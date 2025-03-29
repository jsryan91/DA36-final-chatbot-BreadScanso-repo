# import pandas as pd
# import numpy as np
# import pinecone
# import os
# import time
# from sqlalchemy import create_engine
# from langchain_community.embeddings import OpenAIEmbeddings
# from dotenv import load_dotenv

# load_dotenv()

# openai_api_key = os.getenv("OPENAI_API_KEY")
# pinecone_api_key = os.getenv("PINECONE_API_KEY")
# pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

# pc = pinecone.Pinecone(api_key=pinecone_api_key)

# dimension = 1536
# try:
#     indexes = pc.list_indexes().names()
#     if pinecone_index_name not in indexes:
#         print(f"🔹 {pinecone_index_name} 인덱스가 존재하지 않아 새로 생성합니다.")
#         pc.create_index(name=pinecone_index_name, dimension=dimension, metric="cosine")

#         # 인덱스 생성될 때까지 대기
#         print("⏳ 인덱스 생성 중... 잠시 대기합니다.")
#         time.sleep(10)  # 초기 대기
#         while pinecone_index_name not in pc.list_indexes().names():
#             print("⏳ 인덱스 생성 중... 계속 대기합니다.")
#             time.sleep(5)
# except Exception as e:
#     print(f"❌ Pinecone 인덱스 초기화 오류: {e}")
#     raise

# try:
#     index = pc.Index(pinecone_index_name)
#     embedding_model = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-small")
# except Exception as e:
#     print(f"❌ Pinecone 인덱스 연결 또는 임베딩 모델 초기화 오류: {e}")
#     raise

# engine = create_engine('mysql+pymysql://teamuser:StM!chel1905@3.34.46.30/dev_db')


# def fetch_data_with_retry(query, engine, retries=2, delay=5)
#     for attempt in range(retries):
#         try:
#             df = pd.read_sql(query, engine)
#             return df
#         except Exception as e:
#             print(f"⚠️ SQL 실행 실패 (시도 {attempt + 1}/{retries}): {e}")
#             time.sleep(delay)
#     print("❌ 모든 시도 실패: SQL 데이터를 가져오지 못했습니다.")
#     return pd.DataFrame()


# def upload_to_pinecone(df, namespace, batch_size=100):
#     """데이터프레임을 Pinecone에 업로드하는 함수"""
#     if df.empty:
#         print(f"⚠️ {namespace} 데이터가 비어있습니다. 업로드를 건너뜁니다.")
#         return

#     total_rows = len(df)
#     print(f"🚀 {namespace} 데이터 ({total_rows}행) 벡터화 및 Pinecone 업로드 시작...")

#     # 메타데이터 크기 제한을 위한 최대 텍스트 길이 설정
#     MAX_METADATA_LENGTH = 30000  # Pinecone 메타데이터 크기 제한에 맞게 조정

#     uploaded_count = 0
#     error_count = 0

#     try:
#         # 데이터를 문자열로 변환하고 행별로 결합
#         text_data = df.astype(str).apply(lambda row: "| ".join(row), axis=1).tolist()

#         # 배치 크기로 나누어 처리
#         for i in range(0, len(text_data), batch_size):
#             batch_texts = text_data[i:i + batch_size]

#             try:
#                 # 임베딩 생성
#                 vectors = embedding_model.embed_documents(batch_texts)
#                 vectors = np.array(vectors).astype('float32')

#                 # ID와 메타데이터 생성
#                 batch_ids = [f"{namespace}_{idx}" for idx in range(i, i + len(batch_texts))]
#                 batch_metadata = []

#                 # 메타데이터 크기 제한 적용
#                 for text in batch_texts:
#                     # 메타데이터 크기 제한을 위해 텍스트 잘라내기
#                     if len(text) > MAX_METADATA_LENGTH:
#                         text = text[:MAX_METADATA_LENGTH] + "... (잘림)"
#                     batch_metadata.append({"original_text": text})

#                 # Pinecone에 업로드
#                 index.upsert(
#                     vectors=list(zip(batch_ids, vectors, batch_metadata)),
#                     namespace=namespace
#                 )

#                 uploaded_count += len(batch_texts)
#                 print(f"📊 진행 상황: {uploaded_count}/{total_rows} 행 업로드 완료")

#             except Exception as e:
#                 error_count += len(batch_texts)
#                 print(f"⚠️ 배치 업로드 실패 (행 {i}~{i + len(batch_texts) - 1}): {e}")
#                 # 10초 대기 후 계속 진행
#                 time.sleep(10)
#                 continue

#     except Exception as e:
#         print(f"❌ 벡터화 또는 업로드 중 오류 발생: {e}")
#         return

#     print(f"✅ {namespace} 데이터 {uploaded_count}개 업로드 완료! (오류: {error_count}개)")


# if __name__ == "__main__":
#     queries = {
#         "members": """
#                 WITH FavoriteProducts AS (
#                     SELECT
#                         m.member_id,
#                         m.name AS member_name,
#                         i.item_name,
#                         COUNT(*) AS product_count,
#                         RANK() OVER (PARTITION BY m.member_id ORDER BY COUNT(*) DESC) AS product_rank
#                     FROM kiosk_orderinfo o
#                     JOIN kiosk_paymentinfo p ON o.order_id = p.order_id
#                     JOIN member_member m ON p.member_id = m.member_id
#                     JOIN kiosk_orderitem oi ON o.order_id = oi.order_id
#                     JOIN menu_item i ON oi.item_id = i.item_id
#                     GROUP BY m.member_id, m.name, i.item_name
#                 )
#                 SELECT
#                     m.member_id,
#                     m.name AS member_name,
#                     m.visit_count,
#                     m.total_spent,
#                     GROUP_CONCAT(fp.item_name ORDER BY fp.product_rank SEPARATOR ', ') AS favorite_products
#                 FROM member_member m
#                 LEFT JOIN FavoriteProducts fp ON m.member_id = fp.member_id AND fp.product_rank <= 3
#                 GROUP BY m.member_id, m.name, m.visit_count, m.total_spent
#                 ORDER BY m.total_spent DESC;

#             """,
#         "orders": """
#                 SELECT 
#                     o.order_id,  -- 주문번호
#                     o.order_at,  -- 주문 일시
#                     m.member_id,  -- 회원 ID
#                     m.name AS member_name,  -- 회원 이름
#                     o.store,  -- 매장
#                     i.item_name,  -- 제품명
#                     oi.item_count,  -- 제품 당 개수
#                     i.sale_price,  -- 판매가
#                     i.cost_price,  -- 원가
#                     p.payment_method,  -- 결제 방법
#                     p.used_points,  -- 사용 포인트
#                     o.earned_points,  -- 적립 포인트
#                     # o.total_amount,  -- 주문 총액
#                     oi.item_total,  -- 주문 총액
#                     i.new AS is_new,  -- 신상품 여부
#                     i.best AS is_best  -- 인기상품 여부

#                 FROM kiosk_orderinfo o
#                 JOIN kiosk_orderitem oi ON o.order_id = oi.order_id
#                 JOIN menu_item i ON oi.item_id = i.item_id
#                 JOIN kiosk_paymentinfo p ON o.order_id = p.order_id
#                 LEFT JOIN member_member m ON p.member_id = m.member_id
#                 ORDER BY o.order_at DESC;
#             """
#         # "qna": """
#         #         SELECT
#         #             q.qna_id, q.title AS question_title, q.content AS question_content,
#         #             r.content AS answer, q.created_at AS question_date, r.created_at AS answer_date
#         #         FROM member_qna q
#         #         LEFT JOIN member_qnareply r ON q.qna_id = r.qna_id
#         #         ORDER BY q.created_at DESC
#         #         LIMIT 10;
#         #     """
#     }

#     try:
#         for namespace, query in queries.items():
#             print(f"\n🔍 {namespace} 데이터 가져오기 시작...")
#             df = fetch_data_with_retry(query, engine)
#             if not df.empty:
#                 upload_to_pinecone(df, namespace)

#                 # CSV 파일로 저장
#                 df.to_csv(f"{namespace}.csv", index=False, encoding="utf-8-sig")
#                 print(f"📁 {namespace}.csv 파일 저장 완료!")
#             else:
#                 print(f"⚠️ {namespace} 데이터를 가져오지 못했습니다.")
#     except Exception as e:
#         print(f"❌ 처리 중 오류 발생: {e}")
#     finally:
#         # 종료 시 연결 해제
#         engine.dispose()
#         print("\n🚀 모든 데이터 처리 완료!")
