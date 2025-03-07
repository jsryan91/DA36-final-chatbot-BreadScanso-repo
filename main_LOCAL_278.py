from fastapi import FastAPI
from app.routers import chatbot
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정
origins = [
    "http://localhost:8000",
    "*",  # 프론트엔드 도메인으로 수정 필요
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 출처
    allow_credentials=True,
    allow_methods=["*"],  # 허용할 HTTP 메서드 (GET, POST 등)
    allow_headers=["*"],  # 허용할 HTTP 헤더
)

# 라우터 등록 (엔드포인트 등록)
app.include_router(chatbot.router)

# 직접 실행 시에도, 컨테이너에서 실행 시에도 동작하도록 수정
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
else:
    # 컨테이너에서 gunicorn 등으로 실행될 때 사용될 app 객체
    # 이 부분은 그대로 두어 app 객체를 노출시킵니다
    pass