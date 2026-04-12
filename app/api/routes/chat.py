from fastapi import APIRouter, HTTPException
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_service import generate_response

router = APIRouter()

@router.post("/")
def chat_endpoint(request: ChatRequest):
    try:
        ai_response = generate_response(request.message)
        return ChatResponse(response=ai_response)
    except Exception:
        raise HTTPException(status_code=500, detail="AI service error")