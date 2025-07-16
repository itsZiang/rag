from rag.core.llm.llm import misa_llm, llm
from rag.core.vectordb.milvus import vector_store
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import logging
from setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def rag_answer(query):
    """
    Function to answer a query using RAG (Retrieval-Augmented Generation) approach.
    
    Args:
        query (str): The question to be answered.
        
    Returns:
        str: The AI-generated answer based on the retrieved context.
    """
    
    # Retrieve relevant documents from the vector store based on the query

    # llm = misa_llm

    # Define the prompt template for generating AI responses
    PROMPT_TEMPLATE = """
    Human: You are an AI assistant, and provides answers to questions.
    Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    <context>
    {context}
    </context>

    <question>
    {question}
    </question>

    Assistant:"""

    # Create a PromptTemplate instance with the defined template and input variables
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE, input_variables=["context", "question"]
    )
    # Convert the vector store to a retriever
    retriever = vector_store.as_retriever()


    # Define a function to format the retrieved documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Define the RAG (Retrieval-Augmented Generation) chain for AI response generation
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # Invoke the RAG chain with a specific question and retrieve the response
    res = rag_chain.invoke(query)
    logger.info(f"RAG answer for query '{query}': {res}")
    return res

if __name__ == "__main__":
    # Example usage of the rag_answer function
    question = "Các phong cách chơi đàn tranh tại Trung Quốc có sự phân chia như thế nào?"
    answer = rag_answer(question)
    print(f"Question: {question}\nAnswer: {answer}")