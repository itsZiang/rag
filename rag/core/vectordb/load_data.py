from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import WikipediaLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

documents = WikipediaLoader(
    query="Đàn tranh", 
    load_max_docs=1,
    lang="vi",
    doc_content_chars_max=10000000
).load()

# Initialize a RecursiveCharacterTextSplitter for splitting text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=20)

# Split the documents into chunks using the text_splitter
docs = text_splitter.split_documents(documents)