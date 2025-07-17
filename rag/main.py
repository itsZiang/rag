from rag.core.llm.llm import misa_llm, llm, chat_complete
from rag.core.vectordb.milvus import vector_store
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import logging
from setup import setup_logging
import json
import os
import uuid
from datetime import datetime
setup_logging()
logger = logging.getLogger(__name__)

llm = misa_llm

# Define the prompt template for generating AI responses
PROMPT_TEMPLATE = """
Human: You are an AI assistant, and provides answers to questions.
Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

<chat_history>
{chat_history}
</chat_history>

<context>
{context}
</context>

<question>
{question}
</question>

A:"""

# Create a PromptTemplate instance with the defined template and input variables
prompt = PromptTemplate(
    template=PROMPT_TEMPLATE, input_variables=["context", "question", "chat_history"]
)
# Convert the vector store to a retriever
retriever = vector_store.as_retriever()

# Define a function to format the retrieved documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def load_all_conversations():
    """Load tất cả conversations"""
    try:
        if not os.path.exists("chat_history.json"):
            save_all_conversations({})
            return {}
            
        with open("chat_history.json", "r", encoding="utf-8") as f:
            content = f.read().strip()
            
            if not content:
                save_all_conversations({})
                return {}
                
            data = json.loads(content)
            
            # Migrate old format to new format
            if isinstance(data, list):
                # Old format: convert to new format
                if data:  # Nếu có data cũ
                    conversation_id = str(uuid.uuid4())
                    new_data = {
                        conversation_id: {
                            "id": conversation_id,
                            "title": data[0]["question"][:50] + "..." if len(data[0]["question"]) > 50 else data[0]["question"],
                            "created_at": datetime.now().isoformat(),
                            "messages": data
                        }
                    }
                    save_all_conversations(new_data)
                    return new_data
                else:
                    return {}
            
            return data
            
    except json.JSONDecodeError:
        logger.warning("chat_history.json is corrupted, creating new file")
        save_all_conversations({})
        return {}
    except Exception as e:
        logger.error(f"Error loading conversations: {e}")
        save_all_conversations({})
        return {}

def save_all_conversations(conversations):
    """Save tất cả conversations"""
    try:
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(conversations, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving conversations: {e}")

def load_conversation(conversation_id):
    """Load một conversation cụ thể"""
    conversations = load_all_conversations()
    return conversations.get(conversation_id, {}).get("messages", [])

def save_conversation(conversation_id, messages, title=None):
    """Save một conversation"""
    conversations = load_all_conversations()
    
    if conversation_id not in conversations:
        # Generate title from first message if available
        if messages and not title:
            title = generate_conversation_title(messages[0]["question"])
        elif not title:
            title = "New Conversation"
            
        conversations[conversation_id] = {
            "id": conversation_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
    
    conversations[conversation_id]["messages"] = messages
    conversations[conversation_id]["updated_at"] = datetime.now().isoformat()
    
    # Update title if this is the first message and we don't have a proper title yet
    if messages and (conversations[conversation_id]["title"] == "New Conversation" or conversations[conversation_id]["title"] == "Untitled"):
        conversations[conversation_id]["title"] = generate_conversation_title(messages[0]["question"])
    
    save_all_conversations(conversations)

def create_new_conversation():
    """Tạo conversation mới"""
    # Clean up empty conversations before creating new one
    cleanup_empty_conversations()
    
    conversation_id = str(uuid.uuid4())
    conversations = load_all_conversations()
    conversations[conversation_id] = {
        "id": conversation_id,
        "title": "New Conversation",
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    save_all_conversations(conversations)
    return conversation_id

def get_conversation_list():
    """Lấy danh sách tất cả conversations"""
    conversations = load_all_conversations()
    conversation_list = []
    for conv_id, conv_data in conversations.items():
        messages = conv_data.get("messages", [])
        # Chỉ hiển thị conversations có ít nhất 1 message
        if messages:
            conversation_list.append({
                "id": conv_id,
                "title": conv_data.get("title", "Untitled"),
                "created_at": conv_data.get("created_at", ""),
                "message_count": len(messages)
            })
    
    # Sort by created_at descending
    conversation_list.sort(key=lambda x: x["created_at"], reverse=True)
    return conversation_list

def delete_conversation(conversation_id):
    """Xóa một conversation"""
    conversations = load_all_conversations()
    if conversation_id in conversations:
        del conversations[conversation_id]
        save_all_conversations(conversations)
        return True
    return False

def cleanup_empty_conversations():
    """Xóa các conversation rỗng (không có message)"""
    conversations = load_all_conversations()
    empty_conversations = []
    
    for conv_id, conv_data in conversations.items():
        if not conv_data.get("messages", []):
            empty_conversations.append(conv_id)
    
    for conv_id in empty_conversations:
        del conversations[conv_id]
    
    if empty_conversations:
        save_all_conversations(conversations)
        logger.info(f"Cleaned up {len(empty_conversations)} empty conversations")

def save_user_input(conversation_id, user_input):
    """Lưu input của user vào conversation"""
    try:
        messages = load_conversation(conversation_id)
        
        # Kiểm tra xem có phải là tin nhắn mới không (tránh duplicate)
        if not messages or messages[-1].get("question") != user_input:
            messages.append({
                "question": user_input,
                "answer": ""  # Sẽ được cập nhật sau khi có response
            })
            save_conversation(conversation_id, messages)
            logger.info(f"User input saved to conversation {conversation_id}: {user_input}")
    except Exception as e:
        logger.error(f"Error saving user input: {e}")

def format_chat_history(history):
    formatted = []
    for item in history:
        formatted.append(f"Human: {item['question']}")
        if item['answer']:  # Chỉ thêm answer nếu có
            formatted.append(f"Assistant: {item['answer']}")
    return "\n".join(formatted)

def rag_answer(query, conversation_id):
    try:
        messages = load_conversation(conversation_id)
        formatted_history = format_chat_history(messages)
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough(), "chat_history": lambda x: formatted_history}
            | prompt
            | misa_llm
            | StrOutputParser()
        )
        # Invoke the RAG chain with a specific question and retrieve the response
        res = rag_chain.invoke(query)
        logger.info(f"RAG answer for query '{query}': {res}")
        
        # Cập nhật answer vào conversation
        messages = load_conversation(conversation_id)
        for item in reversed(messages):
            if item["question"] == query and not item["answer"]:
                item["answer"] = res
                break
        
        # Giữ chỉ 20 tin nhắn gần nhất
        if len(messages) > 20:
            messages = messages[-20:]
        
        save_conversation(conversation_id, messages)
        
        return res
        
    except Exception as e:
        logger.error(f"Error in rag_answer: {e}")
        return f"Error: {str(e)}"

def rag_answer_stream(query, conversation_id):
    try:
        messages = load_conversation(conversation_id)
        formatted_history = format_chat_history(messages)
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough(), "chat_history": lambda x: formatted_history}
            | prompt
            | misa_llm
            | StrOutputParser()
        )
        
        full_response = ""
        chunks = rag_chain.stream(query)
        for chunk in chunks:
            full_response += chunk
            yield chunk
        
        # Cập nhật answer vào conversation sau khi stream xong
        messages = load_conversation(conversation_id)
        for item in reversed(messages):
            if item["question"] == query and not item["answer"]:
                item["answer"] = full_response
                break
        
        if len(messages) > 20:
            messages = messages[-20:]
        
        save_conversation(conversation_id, messages)
        
    except Exception as e:
        logger.error(f"Error in rag_answer_stream: {e}")
        yield f"Error: {str(e)}"

def generate_conversation_title(first_message):
    """Generate title for conversation based on first user message"""
    try:
        prompt = f"""Generate a short, descriptive title (maximum 50 characters) for a conversation that starts with this message: "{first_message}"

The title should be:
- Concise and descriptive
- Maximum 50 characters
- In the same language as the message
- Capture the main topic or intent

Title:"""
        
        title_response = chat_complete(prompt)
        if isinstance(title_response, str):
            title = title_response.strip()
        else:
            title = str(title_response).strip()
            
        # Remove quotes if present
        title = title.strip('"').strip("'")
        # Limit to 50 characters
        if len(title) > 50:
            title = title[:47] + "..."
        return title
    except Exception as e:
        logger.error(f"Error generating title: {e}")
        # Fallback to simple truncation
        return first_message[:50] + "..." if len(first_message) > 50 else first_message

# Khởi tạo conversations file khi import module
if not os.path.exists("chat_history.json"):
    save_all_conversations({})

if __name__ == "__main__":
    # Example usage of the rag_answer function
    conversation_id = create_new_conversation()
    question = "Các phong cách chơi đàn tranh tại Trung Quốc có sự phân chia như thế nào?"
    save_user_input(conversation_id, question)
    answer = rag_answer(question, conversation_id)
    print(f"Question: {question}\nAnswer: {answer}")