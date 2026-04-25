from fastapi import FastAPI

from app.api.routes import chat
from app.api.routes.generate_quiz import router as quiz_router  # ✅ FIXED
from app.api.routes.explain_answers import router as explain_router

app = FastAPI()

app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

# ✅ REGISTER QUIZ ROUTE
app.include_router(quiz_router, tags=["Quiz"])
app.include_router(explain_router)

@app.get("/")
def root():
    return {"message": "AI Service Running"}