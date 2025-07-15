from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from rag.main import rag_answer

chat_router = APIRouter()


@chat_router.post("/chat")
async def chat_router_(message: str):
    response = rag_answer(message)
    return {"response": response}
