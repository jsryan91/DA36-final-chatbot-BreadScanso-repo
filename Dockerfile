# Python 3.12를 베이스 이미지로 사용
FROM python:3.12

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 Python 패키지 설치를 위한 requirements.txt 파일 생성
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정 (필요시 .env 파일을 통해 오버라이드 가능)
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8003

# 애플리케이션 실행 (Uvicorn을 사용하여 직접 실행)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]