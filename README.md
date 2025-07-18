# Ứng dụng RAG trong tư vấn bán lẻ điện thoại


## Usage

1. Cài đặt dependencies
```
pip install -r requirements.txt
```

2. Crawl dữ liệu ở file `products_details_enhanced.csv`

3. Index dữ liệu vào vectordb
```
bash indexing.sh
```

4. Chạy app

- FastAPI:
```
bash run.sh
```

- Streamlit
```
bash ui.sh
```

## Dữ liệu

Dữ liệu sản phẩm được lấy từ web thế giới di động. Ví dụ một dòng dữ liệu mẫu trong dataframe:

| title                        | specifications                | price_category | key_features                        | target_users         | url                        | price    |
|------------------------------|-------------------------------|----------------|--------------------------------------|----------------------|----------------------------|----------|
| iPhone 14 Pro Max 128GB      | 6.7" OLED, A16 Bionic, 128GB  | Cao cấp        | Camera chất lượng cao, pin khủng, ram lớn,...            | chụp ảnh| https://example.com/iphone | 29990000 |

- specifications:
    - màn hình
    - pin
    - chip 
    - ram
    - camera
    - ...

## Kiến trúc

Kiến trúc RAG cơ bản, gồm 2 phần:
- Retrieval
    - Embedding: intfloat/multilingual-e5-small -> **384 chiều, 512 max_seq_length**
        - Embed: `title + specs + price_category + key_features + target_user`
        - Truy xuất top-k = 8
    - VectorDB: Milvus Lite

- Generation
    - LLM: misa-qwen3-235b


## Tính năng

- Chat history: quản lý bằng file json
- Quản lý conversation: 
    - Tạo hội thoại mới, xóa hội thoại
    - Tạo title cho hội thoại


