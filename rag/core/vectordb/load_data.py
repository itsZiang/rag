from langchain_core.documents import Document
import pandas as pd

df = pd.read_csv("products_details_enhanced.csv")

docs = []

for index, row in df.iterrows():
    docs.append(Document(page_content=f"Tên điện thoại: {row['title']}.\n Thông số: {row['specifications']}, Giá: {row['price_category']}, key_features: {row['key_features']}, target_users: {row['target_users']}", metadata={"title": row["title"], "url": row["url"], "price": row["price"]}))

