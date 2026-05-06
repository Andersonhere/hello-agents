#!/bin/bash
# 高效并行下载图片脚本

BASE_DIR="$(pwd)"
IMAGES_DIR="$BASE_DIR/images"

# 读取 URL 列表并下载
echo "开始并行下载图片..."

# 使用 curl 并行下载，同时跳过已存在的文件
cat "$BASE_DIR/image_urls.json" | python3 -c "
import json
import sys
import os
from urllib.parse import urlparse, unquote

data = json.load(sys.stdin)
for item in data:
    url = item['url']
    local_file = item['local_file'].replace('./images/', '')

    # 跳过非 GitHub raw 图片（shields.io 等动态图片可能不需要本地化）
    if 'raw.githubusercontent.com' not in url:
        print(f'SKIP_NON_GITHUB:{url}')
        continue

    print(f'{url}|{local_file}')
" | while IFS='|' read -r url local_file; do
    if [[ "$url" == SKIP_NON_GITHUB:* ]]; then
        continue
    fi

    local_path="$IMAGES_DIR/$local_file"

    # 创建必要的子目录
    dir=$(dirname "$local_path")
    mkdir -p "$dir"

    # 如果文件不存在，则下载
    if [[ ! -f "$local_path" ]]; then
        echo "下载: $local_file"
        curl -sL --max-time 60 "$url" -o "$local_path" &
    fi
done

# 等待所有后台任务完成
wait

echo "下载完成!"
