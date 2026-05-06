#!/usr/bin/env python3
"""
下载 md 文档中的远程图片到本地，保持原有目录结构
"""

import os
import re
import json
import urllib.request
from pathlib import Path
from urllib.parse import urlparse, unquote
import ssl
import subprocess

# 忽略 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

BASE_DIR = Path.cwd()
IMAGES_DIR = BASE_DIR / "images"

# 确保图片目录存在
IMAGES_DIR.mkdir(exist_ok=True)

def get_github_raw_path(url):
    """从 GitHub raw URL 提取相对路径"""
    if 'raw.githubusercontent.com' in url:
        # 提取 /datawhalechina/Hello-Agents/main/ 之后的路径
        parts = url.split('/main/')
        if len(parts) > 1:
            return parts[1]  # 返回 docs/images/... 路径
    return None

def download_with_curl(url, local_path):
    """使用 curl 下载图片"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        if os.path.exists(local_path):
            return True

        result = subprocess.run(
            ['curl', '-sL', '--max-time', '60', '-o', local_path, url],
            capture_output=True,
            text=True,
            timeout=70
        )
        return result.returncode == 0
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return False

def main():
    # 读取 URL 列表
    with open(BASE_DIR / 'image_urls.json', 'r', encoding='utf-8') as f:
        url_list = json.load(f)

    print(f"总共 {len(url_list)} 个图片 URL")

    # 下载 GitHub raw 图片
    github_count = 0
    download_count = 0
    skip_count = 0

    for item in url_list:
        url = item['url']

        # 只处理 GitHub raw 图片
        rel_path = get_github_raw_path(url)
        if not rel_path:
            skip_count += 1
            continue

        github_count += 1
        local_path = IMAGES_DIR / rel_path

        if local_path.exists():
            skip_count += 1
            continue

        print(f"下载: {rel_path}")
        if download_with_curl(url, str(local_path)):
            download_count += 1
        else:
            print(f"  -> 失败!")

    print(f"\n完成: GitHub 图片 {github_count} 个, 本次下载 {download_count} 个, 跳过 {skip_count} 个")

if __name__ == '__main__':
    main()
