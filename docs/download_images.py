#!/usr/bin/env python3
"""
下载 md 文档中的远程图片到本地，并修改引用路径
"""

import os
import re
import json
import hashlib
import urllib.request
from pathlib import Path
from urllib.parse import urlparse, unquote
import ssl

# 忽略 SSL 验证（某些图片服务器可能需要）
ssl._create_default_https_context = ssl._create_unverified_context

# 获取当前工作目录
BASE_DIR = Path.cwd()
IMAGES_DIR = BASE_DIR / "images"

# 确保图片目录存在
IMAGES_DIR.mkdir(exist_ok=True)

def extract_image_urls(md_files):
    """从 md 文件中提取所有图片 URL"""
    urls = {}
    img_pattern = re.compile(r'<img\s+src="(https://[^"]+)"')

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = img_pattern.findall(content)
                for url in matches:
                    # 使用 URL 哈希作为键，避免重复
                    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                    if url not in urls:
                        urls[url] = {
                            'hash': url_hash,
                            'files': []
                        }
                    urls[url]['files'].append(str(md_file))
        except Exception as e:
            print(f"读取文件 {md_file} 出错: {e}")

    return urls

def get_local_filename(url):
    """根据 URL 生成本地文件名"""
    parsed = urlparse(url)
    path = unquote(parsed.path)
    filename = os.path.basename(path)

    # 如果没有文件名，生成一个
    if not filename or '.' not in filename:
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        # 尝试从 URL 推断扩展名
        if 'png' in url.lower():
            ext = '.png'
        elif 'jpg' in url.lower() or 'jpeg' in url.lower():
            ext = '.jpg'
        elif 'gif' in url.lower():
            ext = '.gif'
        elif 'svg' in url.lower():
            ext = '.svg'
        elif 'webp' in url.lower():
            ext = '.webp'
        else:
            ext = '.png'
        filename = f"image_{url_hash}{ext}"

    return filename

def download_image(url, local_path):
    """下载图片到本地"""
    try:
        print(f"下载: {url}")
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(local_path, 'wb') as f:
                f.write(response.read())
        print(f"  -> 已保存到: {local_path}")
        return True
    except Exception as e:
        print(f"  -> 下载失败: {e}")
        return False

def update_md_files(urls):
    """更新 md 文件中的图片引用路径"""
    for url, info in urls.items():
        local_filename = get_local_filename(url)
        local_path = f"./images/{local_filename}"

        # 替换文件中的 URL 为本地路径
        for md_file in info['files']:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 替换特定的 URL
                old_str = f'<img src="{url}"'
                new_str = f'<img src="{local_path}"'

                if old_str in content:
                    content = content.replace(old_str, new_str)
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"已更新: {md_file}")
            except Exception as e:
                print(f"更新文件 {md_file} 出错: {e}")

def main():
    print(f"工作目录: {BASE_DIR}")
    print(f"图片目录: {IMAGES_DIR}")

    # 查找所有 md 文件
    md_files = list(BASE_DIR.glob("**/*.md"))
    print(f"找到 {len(md_files)} 个 md 文件")

    # 提取图片 URL
    print("\n正在提取图片 URL...")
    urls = extract_image_urls(md_files)
    print(f"找到 {len(urls)} 个唯一的图片 URL")

    # 保存 URL 列表供检查
    url_list = []
    for url, info in urls.items():
        local_filename = get_local_filename(url)
        url_list.append({
            'url': url,
            'local_file': f"./images/{local_filename}",
            'used_in': info['files']
        })

    # 保存到 JSON 文件
    with open(BASE_DIR / 'image_urls.json', 'w', encoding='utf-8') as f:
        json.dump(url_list, f, ensure_ascii=False, indent=2)

    print("\nURL 列表已保存到 image_urls.json")

    # 下载图片
    print("\n开始下载图片...")
    success_count = 0
    fail_count = 0

    for url in urls.keys():
        local_filename = get_local_filename(url)
        local_path = IMAGES_DIR / local_filename

        # 检查是否已存在
        if local_path.exists():
            print(f"已存在，跳过: {local_filename}")
            success_count += 1
            continue

        if download_image(url, local_path):
            success_count += 1
        else:
            fail_count += 1

    print(f"\n下载完成: 成功 {success_count}, 失败 {fail_count}")

    # 更新 md 文件
    print("\n正在更新 md 文件中的图片引用...")
    update_md_files(urls)

    print("\n完成!")

if __name__ == '__main__':
    main()
