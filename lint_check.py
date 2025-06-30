#!/usr/bin/env python3
"""
Простая утилита для проверки стиля кода без flake8.
Проверяет базовые правила форматирования.
"""

import os
import re
import sys
from pathlib import Path

def check_file_style(filepath):
    """Проверяет стиль отдельного файла."""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines, 1):
        # Проверка длины строки (рекомендация PEP 8: 79 символов)
        if len(line.rstrip()) > 88:  # Более мягкий лимит
            issues.append(f"Line {line_num}: Line too long ({len(line.rstrip())} > 88 characters)")
        
        # Проверка пробелов в конце строки
        if line.rstrip() != line.rstrip('\n'):
            issues.append(f"Line {line_num}: Trailing whitespace")
        
        # Проверка табуляций
        if '\t' in line:
            issues.append(f"Line {line_num}: Contains tabs, use spaces")
        
        # Проверка двойных пробелов перед комментариями
        if re.search(r'[^\s]  #', line):
            issues.append(f"Line {line_num}: Use single space before inline comment")
    
    return issues

def check_directory(directory_path):
    """Проверяет все Python файлы в директории."""
    python_files = list(Path(directory_path).rglob("*.py"))
    total_issues = 0
    
    print(f"Проверяю {len(python_files)} Python файлов...")
    
    for py_file in python_files:
        # Пропускаем файлы в виртуальных окружениях
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        try:
            issues = check_file_style(py_file)
            if issues:
                print(f"\n📁 {py_file}:")
                for issue in issues:
                    print(f"  ⚠️  {issue}")
                total_issues += len(issues)
            else:
                print(f"✅ {py_file}")
        except Exception as e:
            print(f"❌ Ошибка при проверке {py_file}: {e}")
    
    return total_issues

def main():
    """Основная функция."""
    print("🔍 Простая проверка стиля кода Python\n")
    
    # Проверяем основные файлы проекта
    files_to_check = [
        'main.py',
        'config.py', 
        'validate_config.py',
        'vpnworks/api.py'
    ]
    
    total_issues = 0
    
    print("Проверяю основные файлы:")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                issues = check_file_style(file_path)
                if issues:
                    print(f"\n📁 {file_path}:")
                    for issue in issues:
                        print(f"  ⚠️  {issue}")
                    total_issues += len(issues)
                else:
                    print(f"✅ {file_path}")
            except Exception as e:
                print(f"❌ Ошибка при проверке {file_path}: {e}")
        else:
            print(f"⚠️  Файл {file_path} не найден")
    
    # Проверяем тесты
    if os.path.exists('tests'):
        print(f"\nПроверяю тесты:")
        test_issues = check_directory('tests')
        total_issues += test_issues
    
    print(f"\n{'='*50}")
    if total_issues == 0:
        print("🎉 Все проверки пройдены! Код соответствует стилю.")
        return 0
    else:
        print(f"⚠️  Найдено {total_issues} проблем со стилем.")
        print("💡 Рекомендуется исправить их для лучшей читаемости кода.")
        return 1

if __name__ == '__main__':
    sys.exit(main())