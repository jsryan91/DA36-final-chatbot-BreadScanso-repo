import pandas as pd
import numpy as np
import pinecone
import os
import time
from sqlalchemy import create_engine
from langchain_community.embeddings import OpenAIEmbeddings

# 환경 변수 로드
openai_api_key = os.environ.get("OPENAI_API_KEY")
pinecone_api_key = os.environ.get("PINECONE_API_KEY")
pinecone_index_name = os.environ.get("PINECONE_INDEX_NAME")

# Pinecone 초기화
pinecone.init(api_key=pinecone_api_key, environment="gcp-starter")

# Pinecone 인덱스 확인 및 생성
dimension = 1536
if pinecone_index_name not in pinecone.list_indexes():
    print(f"🔹 {pinecone_index_name} 인덱스가 존재하지 않아 새로 생성합니다.")
    pinecone.create_index(name=pinecone_index_name, dimension=dimension, metric="cosine")

# 인덱스 생성될 때까지 대기
while pinecone_index_name not in pinecone.list_indexes():
    print("⏳ 인덱스 생성 중... 잠시 대기합니다.")
    time.sleep(5)

index = pinecone.Index(pinecone_index_name)  # 안전한 초기화
embedding_model = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-small")

# MySQL 연결
engine = create_engine('mysql+pymysql://teamuser:StM!chel1905@3.34.46.30/dev_db')


def fetch_data_with_retry(query, engine, retries=3, delay=5):
    """SQL 실행 오류 발생 시 재시도"""
    for attempt in range(retries):
        try:
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            print(f"⚠️ SQL 실행 실패 (시도 {attempt+1}/{retries}): {e}")
            time.sleep(delay)
    print("❌ 모든 시도 실패: SQL 데이터를 가져오지 못했습니다.")
    return pd.DataFrame()


def upload_to_pinecone(df, namespace, batch_size=100):
    """데이터프레임을 Pinecone에 업로"""
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


if __name__ == "__main__":
    queries = { ... }  # 기존 SQL 쿼리 유지

    for namespace, query in queries.items():
        df = fetch_data_with_retry(query, engine)
        if not df.empty:
            upload_to_pinecone(df, namespace)

    engine.dispose()
    print("🚀 모든 데이터가 Pinecone에 업데이트되었습니다!")
