"""Тесты для модуля config.py"""

import os
import pytest
from unittest.mock import patch, mock_open
import tempfile


def test_check_credentials_success():
    """Тест успешной проверки учетных данных"""
    with patch.dict(os.environ, {'BOT_API': 'test_token', 'CHAT_ID': '123456'}):
        with patch('config.BOT_API', 'test_token'), \
             patch('config.CHAT_ID', 123456):
            # Импортируем функцию после патча
            from config import check_credentials
            # Не должно выбросить исключение
            check_credentials()


def test_check_credentials_missing_bot_api():
    """Тест проверки с отсутствующим BOT_API"""
    with patch('config.BOT_API', None), \
         patch('config.CHAT_ID', 123456):
        from config import check_credentials
        with pytest.raises(ValueError, match="Missing environment variables: BOT_API"):
            check_credentials()


def test_check_credentials_missing_chat_id():
    """Тест проверки с отсутствующим CHAT_ID"""
    with patch('config.BOT_API', 'test_token'), \
         patch('config.CHAT_ID', None):
        from config import check_credentials
        with pytest.raises(ValueError, match="Missing environment variables: CHAT_ID"):
            check_credentials()


def test_check_credentials_missing_both():
    """Тест проверки с отсутствующими обеими переменными"""
    with patch('config.BOT_API', None), \
         patch('config.CHAT_ID', None):
        from config import check_credentials
        with pytest.raises(ValueError, match="Missing environment variables: BOT_API, CHAT_ID"):
            check_credentials()


def test_start_msg_default():
    """Тест значения по умолчанию для START_MSG"""
    with patch.dict(os.environ, {}, clear=True):
        with patch('builtins.open', mock_open(read_data="")):
            with patch('os.path.join', return_value='.env'):
                # Перезагружаем модуль для применения изменений
                import importlib
                import config
                importlib.reload(config)
                assert config.START_MSG == 'Hello World!'


def test_env_file_loading():
    """Тест загрузки переменных из .env файла"""
    env_content = "BOT_API=test_token\nCHAT_ID=123456\nSTART_MSG=Test Message"

    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write(env_content)
        temp_path = f.name

    try:
        with patch('os.path.join', return_value=temp_path):
            # Очищаем переменные окружения
            with patch.dict(os.environ, {}, clear=True):
                import importlib
                import config
                importlib.reload(config)

                # Проверяем, что переменные загрузились
                assert config.BOT_API is not None
                assert config.CHAT_ID is not None
                assert config.START_MSG is not None
    finally:
        os.unlink(temp_path)