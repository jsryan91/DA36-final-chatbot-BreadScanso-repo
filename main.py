from fastapi import FastAPI
from bread_chatbot.app.routers import chatbot
import uvicorn

# FastAPI 앱 생성
app = FastAPI()

# 라우터 등록 (엔드포인트 등록)
app.include_router(chatbot.router)

# Uvicorn 실행
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)