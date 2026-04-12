from fastapi import FastAPI
from app.api.routes import chat

app = FastAPI()

app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.get("/")
def root():
    return {"message": "AI Service Running"}