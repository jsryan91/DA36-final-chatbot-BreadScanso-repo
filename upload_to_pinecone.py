import pandas as pd
import numpy as np
import pinecone
import os
from sqlalchemy import create_engine
from langchain_community.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

pc = pinecone.Pinecone(api_key=pinecone_api_key)

# Pinecone 인덱스 가져오기
dimension = 1536
if pinecone_index_name not in pc.list_indexes().names():
    pc.create_index(name=pinecone_index_name, dimension=dimension, metric="cosine")

index = pc.Index(pinecone_index_name)
embedding_model = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-small")
engine = create_engine('mysql+pymysql://teamuser:StM!chel1905@3.34.46.30/dev_db')


def upload_to_pinecone(df, namespace, batch_size=100):
    """데이터프레임을 Pinecone에 업로드하는 함수"""
    if df.empty:
        print(f"⚠️ {namespace} 데이터가 비어있습니다. 업로드를 건너뜁니다.")
        return

    print(f"🚀 {namespace} 데이터 벡터화 및 Pinecone 업로드 시작...")

    text_data = df.astype(str).apply(lambda row: ", ".join(row), axis=1).tolist()
    vectors = embedding_model.embed_documents(text_data)
    vectors = np.array(vectors).astype('float32')

    for i in range(0, len(vectors), batch_size):
        batch_vectors = vectors[i: i + batch_size]
        batch_ids = [f"{namespace}_{idx}" for idx in range(i, i + len(batch_vectors))]
        batch_metadata = [{"original_text": text_data[idx]} for idx in range(i, i + len(batch_vectors))]

        index.upsert(
            vectors=list(zip(batch_ids, batch_vectors, batch_metadata)),
            namespace=namespace
        )

    print(f"✅ {namespace} 데이터 {len(df)}개 업로드 완료!")

# 데이터 가져오기
queries = {
    "sales": """
        SELECT 
            o.store, i.item_id, i.item_name, DATE(o.order_at) AS order_date, 
            SUM(oi.item_count) AS total_sold, 
            SUM(oi.item_count * i.sale_price) AS total_amount
        FROM kiosk_orderitem oi
        JOIN kiosk_orderinfo o ON oi.order_id = o.order_id
        JOIN menu_item i ON oi.item_id = i.item_id
        GROUP BY o.store, i.item_id, i.item_name, order_date
        ORDER BY o.store, order_date DESC, total_sold DESC;
    """,
    "members": """
        WITH FavoriteProducts AS (
            SELECT 
                m.member_id, m.name AS member_name, i.item_name, COUNT(*) AS product_count,
                RANK() OVER (PARTITION BY m.member_id ORDER BY COUNT(*) DESC) AS product_rank
            FROM kiosk_orderinfo o
            JOIN kiosk_paymentinfo p ON o.order_id = p.order_id
            JOIN member_member m ON p.member_id = m.member_id
            JOIN kiosk_orderitem oi ON o.order_id = oi.order_id
            JOIN menu_item i ON oi.item_id = i.item_id
            GROUP BY m.member_id, i.item_name
        )
        SELECT 
            m.member_id, m.name AS member_name, COUNT(DISTINCT o.order_id) AS total_orders,
            SUM(o.final_amount) AS total_spent,
            GROUP_CONCAT(DISTINCT fp.item_name ORDER BY fp.product_rank SEPARATOR ', ') AS favorite_products
        FROM member_member m
        LEFT JOIN kiosk_paymentinfo p ON m.member_id = p.member_id
        LEFT JOIN kiosk_orderinfo o ON p.order_id = o.order_id
        LEFT JOIN FavoriteProducts fp ON m.member_id = fp.member_id AND fp.product_rank <= 3
        GROUP BY m.member_id, m.name
        ORDER BY total_spent DESC;
    """,
    "orders": """
        SELECT 
            o.order_id, o.store, o.order_at, m.member_id, m.name AS member_name, 
            o.final_amount, p.payment_method AS payment_type, 
            i.item_id, i.item_name, oi.item_count
        FROM kiosk_orderinfo o
        LEFT JOIN kiosk_paymentinfo p ON o.order_id = p.order_id
        LEFT JOIN member_member m ON p.member_id = m.member_id
        LEFT JOIN kiosk_orderitem oi ON o.order_id = oi.order_id
        LEFT JOIN menu_item i ON oi.item_id = i.item_id
        ORDER BY o.order_at DESC;
    """,
    "qna": """
        SELECT 
            q.qna_id, q.title AS question_title, q.content AS question_content, 
            r.content AS answer, q.created_at AS question_date, r.created_at AS answer_date
        FROM member_qna q
        LEFT JOIN member_qnareply r ON q.qna_id = r.qna_id
        ORDER BY q.created_at DESC
        LIMIT 10;
    """
}

# 각 데이터셋 처리
for namespace, query in queries.items():
    df = pd.read_sql(query, engine)
    upload_to_pinecone(df, namespace)

engine.dispose()
print("🚀 모든 데이터가 Pinecone에 업데이트되었습니다!")
