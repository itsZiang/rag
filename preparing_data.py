from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = DirectoryLoader(
    "./data",
    glob="*.txt",
)

documents = loader.load()

# Initialize a RecursiveCharacterTextSplitter for splitting text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=256, chunk_overlap=20)

# Split the documents into chunks using the text_splitter
docs = text_splitter.split_documents(documents)

for i in range(0, len(docs)):
    if i == 10:
        break
    print(f"Chunk {i+1}: {docs[i].page_content}") 
    print("" + "="*50 + "\n")