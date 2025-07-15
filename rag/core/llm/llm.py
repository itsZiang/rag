from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
APP_CODE = os.getenv("APP_CODE")

# Initialize the OpenAI language model for response generation
misa_llm = ChatOpenAI(
    model="misa-qwen3-30b",
    base_url=BASE_URL,
    api_key=API_KEY,
    default_headers={
        "App-Code": APP_CODE
    },
    max_tokens=1024,
    temperature=0.7,
    extra_body={
        "service": "test-aiservice.misa.com.vn",
        "chat_template_kwargs": {            
            "enable_thinking": False
        }
    }
)

# messages = [
#     (
#         "system",
#         "You are a helpful assistant.",
#     ),
#     (
#         "human", 
#         "what is the capital of Vietnam? Answer in Vietnamese."
#     ),
# ]

# ai_msg = misa_llm.invoke(messages)
# print(ai_msg.content)
