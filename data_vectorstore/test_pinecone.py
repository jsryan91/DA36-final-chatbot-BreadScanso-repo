import pandas as pd
import numpy as np
import pinecone
import os
from langchain_community.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import glob

# 환경 변수 로드
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

# 🔹 Pinecone 클라이언트 초기화
pc = pinecone.Pinecone(api_key=pinecone_api_key)

# Pinecone 인덱스 생성 (없으면 생성)
dimension = 1536  # text-embedding-3-small 차원
if pinecone_index_name not in [index.name for index in pc.list_indexes()]:
    pc.create_index(
        name=pinecone_index_name,
        dimension=dimension,
        metric="cosine",  # 유사도 측정 방식 (cosine, euclidean, dot_product 중 선택)
    )

index = pc.Index(pinecone_index_name)

# 'csv/' 폴더 내 모든 CSV 파일 가져오기
csv_files = glob.glob('csv/*.csv')
print(f"🔍 총 {len(csv_files)}개의 CSV 파일을 처리합니다.")

embedding_model = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-small")

batch_size = 100

for file in csv_files:
    namespace_name = os.path.basename(file).replace(".csv", "")  # 파일명 기반 네임스페이스
    print(f"📂 파일 처리 중: {file} (네임스페이스: {namespace_name})")

    df = pd.read_csv(file)

    # 🔹 데이터프레임의 모든 행을 하나의 텍스트로 변환
    text_data = df.astype(str).apply(lambda row: ", ".join(row), axis=1).tolist()

    # 🔹 텍스트 → 벡터 변환
    vectors = embedding_model.embed_documents(text_data)
    vectors = np.array(vectors).astype('float32')

    # 🔹 Pinecone에 벡터 + 원본 데이터 저장 (Batch 업로드)
    for i in range(0, len(vectors), batch_size):
        batch_vectors = vectors[i: i + batch_size]
        batch_ids = [str(idx) for idx in range(i, i + len(batch_vectors))]
        batch_metadata = [{"original_text": text_data[idx]} for idx in range(i, i + len(batch_vectors))]

        index.upsert(
            vectors=list(zip(batch_ids, batch_vectors, batch_metadata)),
            namespace=namespace_name
        )

print("✅ 모든 CSV 파일이 개별 네임스페이스로 저장 완료!")
