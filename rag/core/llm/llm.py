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

def generate_streamed_response(message):
    """
    Function to generate a streamed response from the language model.
    
    Args:
        query (str): The input query for which the response is generated.
        
    Yields:
        str: The streamed response text.
    """
    for chunk in misa_llm.stream(message):
        yield chunk.text()