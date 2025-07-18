from langchain_milvus import Milvus, BM25BuiltInFunction
from rag.core.embedding.embedding import embedding
from rag.core.vectordb.load_data import docs

URI = "./milvus_example.db"
COLLECTION_NAME = "tgdd_1"

from pymilvus import connections, utility

connections.connect(uri="./milvus_demo.db")

if not utility.has_collection(COLLECTION_NAME):
    vector_store = Milvus.from_documents(
        documents=docs,
        embedding=embedding,
        connection_args={
            "uri": "./milvus_demo.db",
        },
        collection_name=COLLECTION_NAME,
        drop_old=True,
    )
else:
    # Only connect, do not re-insert documents
    vector_store = Milvus(
        embedding_function=embedding,
        connection_args={
            "uri": "./milvus_demo.db",
        },
        collection_name=COLLECTION_NAME,
    )
