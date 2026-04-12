from fastapi import APIRouter, HTTPException, Header
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_service import generate_response
from app.core.config import INTERNAL_API_KEY

router = APIRouter()

@router.post("/")
def chat_endpoint(request: ChatRequest, x_api_key: str = Header(None)):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        ai_response = generate_response(request.message)
        return ChatResponse(response=ai_response)
    except Exception:
        raise HTTPException(status_code=500, detail="AI service error")