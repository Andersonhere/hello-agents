#!/usr/bin/env python3
"""
修复 md 文件中的图片路径（去掉多余的 docs/ 部分）
"""

import os
import re
from pathlib import Path

BASE_DIR = Path.cwd()

def main():
    # 查找所有 md 文件
    md_files = list(BASE_DIR.glob("**/*.md"))

    print(f"处理 {len(md_files)} 个 md 文件...")

    modified_count = 0
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 修复路径：将 ./images/docs/images/ 改为 ./images/
            old_str = './images/docs/images/'
            new_str = './images/'

            if old_str in content:
                content = content.replace(old_str, new_str)
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                modified_count += 1
                print(f"已修复: {md_file}")
        except Exception as e:
            print(f"处理文件 {md_file} 出错: {e}")

    print(f"\n完成! 共修复了 {modified_count} 个文件")

if __name__ == '__main__':
    main()
