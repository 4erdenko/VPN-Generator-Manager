"""Тесты для модуля validate_config.py"""

import pytest
import sys
import tempfile
import os
from unittest.mock import patch, MagicMock
from pathlib import Path
import validate_config


class TestValidateConfig:
    """Тесты для функций валидации конфигурации"""

    def test_check_python_version_compatible(self):
        """Тест проверки совместимой версии Python"""
        with patch.object(sys, 'version_info', (3, 10, 0)):
            result = validate_config.check_python_version()
            assert result is True

    def test_check_python_version_too_old(self):
        """Тест проверки старой версии Python"""
        with patch.object(sys, 'version_info', (3, 8, 0)):
            with patch('builtins.print') as mock_print:
                result = validate_config.check_python_version()
                assert result is False
                mock_print.assert_any_call("❌ Python 3.8 is too old")

    def test_check_dependencies_success(self):
        """Тест успешной проверки зависимостей"""
        # Мокаем все необходимые импорты
        modules = ['aiogram', 'httpx', 'aiofiles', 'coloredlogs']
        with patch.dict('sys.modules', {module: MagicMock() for module in modules}):
            with patch('builtins.print') as mock_print:
                result = validate_config.check_dependencies()
                assert result is True
                mock_print.assert_called_with("✅ All required dependencies are installed")

    def test_check_dependencies_missing(self):
        """Тест проверки с отсутствующими зависимостями"""
        # Мокаем ImportError для aiogram
        with patch('builtins.__import__', side_effect=ImportError("No module named 'aiogram'")):
            with patch('builtins.print') as mock_print:
                result = validate_config.check_dependencies()
                assert result is False
                # Проверяем, что было выведено сообщение об ошибке
                mock_print.assert_any_call("   Run: pip install -r requirements.txt")

    def test_check_env_file_not_exists(self):
        """Тест проверки несуществующего .env файла"""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('builtins.print') as mock_print:
                result = validate_config.check_env_file()
                assert result is False
                mock_print.assert_any_call("❌ .env file not found")

    def test_check_env_file_exists_valid(self):
        """Тест проверки существующего валидного .env файла"""
        env_content = "BOT_API=real_token_123\nCHAT_ID=123456789\nSTART_MSG=Hello"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            temp_path = f.name

        try:
            with patch('pathlib.Path.exists', return_value=True), \
                 patch('builtins.open', return_value=open(temp_path, 'r')):
                with patch('builtins.print') as mock_print:
                    result = validate_config.check_env_file()
                    assert result is True
                    mock_print.assert_any_call("✅ .env file found")
                    mock_print.assert_any_call("✅ Required environment variables are set")
        finally:
            os.unlink(temp_path)

    def test_check_env_file_placeholder_values(self):
        """Тест проверки .env файла с placeholder значениями"""
        env_content = "BOT_API=your_actual_bot_token\nCHAT_ID=your_actual_chat_id"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            temp_path = f.name

        try:
            with patch('pathlib.Path.exists', return_value=True), \
                 patch('builtins.open', return_value=open(temp_path, 'r')):
                with patch('builtins.print') as mock_print:
                    result = validate_config.check_env_file()
                    assert result is False
                    mock_print.assert_any_call("❌ Missing or placeholder values for: BOT_API, CHAT_ID")
        finally:
            os.unlink(temp_path)

    def test_check_env_file_missing_variables(self):
        """Тест проверки .env файла с отсутствующими переменными"""
        env_content = "START_MSG=Hello World"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            temp_path = f.name

        try:
            with patch('pathlib.Path.exists', return_value=True), \
                 patch('builtins.open', return_value=open(temp_path, 'r')):
                with patch('builtins.print') as mock_print:
                    result = validate_config.check_env_file()
                    assert result is False
                    mock_print.assert_any_call("❌ Missing or placeholder values for: BOT_API, CHAT_ID")
        finally:
            os.unlink(temp_path)

    def test_main_all_checks_pass(self):
        """Тест main функции при успешных проверках"""
        with patch('validate_config.check_python_version', return_value=True), \
             patch('validate_config.check_dependencies', return_value=True), \
             patch('validate_config.check_env_file', return_value=True):
            with patch('builtins.print') as mock_print:
                result = validate_config.main()
                assert result == 0
                mock_print.assert_any_call("🎉 Configuration is valid! You can start the bot.")

    def test_main_some_checks_fail(self):
        """Тест main функции при неудачных проверках"""
        with patch('validate_config.check_python_version', return_value=False), \
             patch('validate_config.check_dependencies', return_value=True), \
             patch('validate_config.check_env_file', return_value=True):
            with patch('builtins.print') as mock_print:
                result = validate_config.main()
                assert result == 1
                mock_print.assert_any_call("❌ Configuration has issues. Please fix them before starting the bot.")