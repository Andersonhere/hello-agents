#!/usr/bin/env python3
"""
修改 md 文件中的图片引用路径为本地路径
"""

import os
import re
import json
from pathlib import Path

BASE_DIR = Path.cwd()
IMAGES_DIR = BASE_DIR / "images"

def get_local_path(url):
    """从 GitHub raw URL 获取本地相对路径"""
    if 'raw.githubusercontent.com' in url:
        parts = url.split('/main/')
        if len(parts) > 1:
            return f"./images/{parts[1]}"
    return None

def main():
    # 读取 URL 列表
    with open(BASE_DIR / 'image_urls.json', 'r', encoding='utf-8') as f:
        url_list = json.load(f)

    print(f"开始修改 md 文件...")

    # 记录修改的文件
    modified_files = set()

    for item in url_list:
        url = item['url']
        local_path = get_local_path(url)

        if not local_path:
            continue

        # 遍历所有引用的文件
        for md_file in item['used_in']:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 替换 URL
                old_str = f'<img src="{url}"'
                new_str = f'<img src="{local_path}"'

                if old_str in content:
                    content = content.replace(old_str, new_str)
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    modified_files.add(md_file)
            except Exception as e:
                print(f"处理文件 {md_file} 出错: {e}")

    print(f"完成! 共修改了 {len(modified_files)} 个文件:")
    for f in sorted(modified_files):
        print(f"  - {f}")

if __name__ == '__main__':
    main()
