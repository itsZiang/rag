#!/bin/bash

# Tạo thư mục data nếu chưa tồn tại
mkdir -p "data/"

# Tải xuống Paul Graham essay
wget "https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt" -O "data/paul_graham_essay.txt"

# Tải xuống Uber 2021 PDF
wget "https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf" -O "data/uber_2021.pdf"

echo "Download completed, saved in data/ directory."