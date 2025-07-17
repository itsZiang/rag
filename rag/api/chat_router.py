from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from rag.main import (
    rag_answer, rag_answer_stream, save_user_input, 
    create_new_conversation, get_conversation_list, 
    delete_conversation, load_conversation, cleanup_empty_conversations
)
from pydantic import BaseModel
from typing import Dict, Any, List

chat_router = APIRouter()

class ChatRequest(BaseModel):
    user_message: str
    conversation_id: str

class UserInputRequest(BaseModel):
    user_input: str
    conversation_id: str

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: str
    message_count: int

@chat_router.post("/chat")
async def chat_complete(request: ChatRequest) -> Dict[str, Any]:
    response = rag_answer(request.user_message, request.conversation_id)
    return {"response": response}

@chat_router.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    response = rag_answer_stream(request.user_message, request.conversation_id)
    return StreamingResponse(response, media_type="text/event-stream")

@chat_router.post("/save_user_input")
async def save_user_input_endpoint(request: UserInputRequest):
    save_user_input(request.conversation_id, request.user_input)
    return {"status": "success"}

@chat_router.post("/conversations/new")
async def create_conversation():
    conversation_id = create_new_conversation()
    return {"conversation_id": conversation_id}

@chat_router.get("/conversations")
async def get_conversations() -> List[ConversationResponse]:
    conversations = get_conversation_list()
    return conversations

@chat_router.delete("/conversations/{conversation_id}")
async def delete_conversation_endpoint(conversation_id: str):
    success = delete_conversation(conversation_id)
    return {"success": success}

@chat_router.get("/conversations/{conversation_id}")
async def get_conversation_messages(conversation_id: str):
    messages = load_conversation(conversation_id)
    return {"messages": messages}

@chat_router.get("/conversations/{conversation_id}/title")
async def get_conversation_title(conversation_id: str):
    from rag.main import load_all_conversations
    conversations = load_all_conversations()
    conversation = conversations.get(conversation_id, {})
    return {"title": conversation.get("title", "Untitled")}

@chat_router.post("/conversations/cleanup")
async def cleanup_conversations():
    """Clean up empty conversations"""
    cleanup_empty_conversations()
    return {"status": "success"}