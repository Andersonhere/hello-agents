#!/usr/bin/env python3
"""
修复子目录中 md 文件的图片路径（添加 ../）
"""

import os
from pathlib import Path

BASE_DIR = Path.cwd()

def main():
    md_files = list(BASE_DIR.glob("**/*.md"))

    print(f"处理 {len(md_files)} 个 md 文件...")

    modified_count = 0
    for md_file in md_files:
        # 检查文件是否在子目录中
        if md_file.parent == BASE_DIR:
            continue  # 根目录的文件不需要修改

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 将 ./images/ 改为 ../images/
            old_str = 'src="./images/'
            new_str = 'src="../images/'

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
