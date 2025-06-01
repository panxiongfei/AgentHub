#!/usr/bin/env python3
"""
安全检查脚本
扫描项目中的敏感信息
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# 敏感信息模式
SENSITIVE_PATTERNS = [
    (r'password\s*=\s*["\'].*["\']', 'Password'),
    (r'api_key\s*=\s*["\'].*["\']', 'API Key'),
    (r'secret\s*=\s*["\'].*["\']', 'Secret'),
    (r'token\s*=\s*["\'].*["\']', 'Token'),
    (r'key\s*=\s*["\'].*["\']', 'Key'),
    (r'[A-Za-z0-9+/]{40,}', 'Base64 String'),
    (r'sk-[A-Za-z0-9]{48}', 'OpenAI API Key'),
    (r'ghp_[A-Za-z0-9]{36}', 'GitHub Token'),
]

# 忽略的文件和目录
IGNORE_PATTERNS = [
    '.*/.git/.*',
    '.*/node_modules/.*',
    '.*/venv/.*',
    '.*/\.venv/.*',
    '.*/__pycache__/.*',
    '.*/\.DS_Store',
    '.*/logs/.*',
    '.*/data/.*',
    '.*/results/.*',
    '.*/downloads/.*',
    '.*/security_check.py',  # 忽略自身
]


def should_ignore(file_path: str) -> bool:
    """检查是否应该忽略文件"""
    for pattern in IGNORE_PATTERNS:
        if re.match(pattern, file_path):
            return True
    return False


def scan_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """扫描单个文件"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for pattern, description in SENSITIVE_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append((line_num, description, line.strip()))
    except Exception:
        # 忽略无法读取的文件
        pass
    
    return issues


def scan_project(project_root: Path) -> List[Tuple[Path, List[Tuple[int, str, str]]]]:
    """扫描整个项目"""
    all_issues = []
    
    for root, dirs, files in os.walk(project_root):
        # 过滤目录
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]
        
        for file in files:
            file_path = Path(root) / file
            
            if should_ignore(str(file_path)):
                continue
            
            issues = scan_file(file_path)
            if issues:
                all_issues.append((file_path, issues))
    
    return all_issues


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    print(f"🔍 扫描项目: {project_root}")
    
    issues = scan_project(project_root)
    
    if not issues:
        print("✅ 未发现敏感信息")
        return
    
    print(f"⚠️  发现 {len(issues)} 个文件包含潜在敏感信息:")
    
    for file_path, file_issues in issues:
        print(f"\n📁 {file_path.relative_to(project_root)}")
        for line_num, description, line in file_issues:
            print(f"   行 {line_num}: {description}")
            print(f"   内容: {line[:100]}...")
    
    print(f"\n⚠️  请检查上述文件并移除或加密敏感信息")


if __name__ == "__main__":
    main() 