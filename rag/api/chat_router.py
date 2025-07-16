from fastapi import APIRouter
from rag.main import rag_answer
from pydantic import BaseModel
from typing import Dict, Any


chat_router = APIRouter()


class ChatRequest(BaseModel):
    user_message: str

@chat_router.post("/chat")
async def chat_complete(request: ChatRequest) -> Dict[str, Any]:
    response = rag_answer(request.user_message)
    return {"response": response}
