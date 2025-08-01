from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
APP_CODE = os.getenv("APP_CODE")

# Initialize the OpenAI language model for response generation
misa_llm = ChatOpenAI(
    # model="misa-qwen3-30b",
    model="misa-qwen3-235b",
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

openai_model = ChatOpenAI(
    model="gpt-4o-mini",
)

groq_model = ChatGroq(api_key=os.getenv("GROQ_API_KEY"),
                    model="moonshotai/kimi-k2-instruct",
                    temperature=0.7
                    )


def chat_complete(message):
    return groq_model.invoke(message).content
