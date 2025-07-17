from langchain_core.documents import Document
import pandas as pd

df = pd.read_csv("products_details.csv")

docs = []

for index, row in df.iterrows():
    docs.append(Document(page_content=f"Tên điện thoại: {row['title']}.\n Thông số: {row['specifications']}", metadata={"title": row["title"], "url": row["url"]}))

