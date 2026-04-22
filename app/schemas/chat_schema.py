from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []
    financialContext: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    response: str