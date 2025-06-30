"""Тесты для модуля vpnworks/api.py"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from vpnworks.api import VpnWorksApi


@pytest.fixture
def api_client():
    """Фикстура для создания экземпляра API клиента"""
    return VpnWorksApi()


class TestVpnWorksApi:
    """Тесты для класса VpnWorksApi"""

    def test_init(self, api_client):
        """Тест инициализации клиента"""
        assert api_client.base_url == 'https://vpn.works'
        assert api_client._token is None
        assert isinstance(api_client.client, httpx.AsyncClient)
        assert 'Accept' in api_client._base_headers

    @pytest.mark.asyncio
    async def test_get_token_success(self, api_client):
        """Тест успешного получения токена"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'Token': 'test_token_123'}
        mock_response.raise_for_status = MagicMock()

        with patch.object(api_client.client, 'post', return_value=mock_response) as mock_post:
            await api_client._get_token()

            mock_post.assert_called_once_with('https://vpn.works/token')
            assert api_client._token == 'test_token_123'
            assert 'Authorization' in api_client.user_headers
            assert api_client.user_headers['Authorization'] == 'Bearer test_token_123'

    @pytest.mark.asyncio
    async def test_get_token_http_error(self, api_client):
        """Тест обработки HTTP ошибки при получении токена"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPError("Network error")

        with patch.object(api_client.client, 'post', return_value=mock_response):
            with pytest.raises(httpx.HTTPError):
                await api_client._get_token()

    @pytest.mark.asyncio
    async def test_token_property(self, api_client):
        """Тест свойства token"""
        # Сначала токен должен быть None
        assert api_client._token is None

        # При первом обращении должен вызваться _get_token
        with patch.object(api_client, '_get_token') as mock_get_token:
            mock_get_token.return_value = None
            api_client._token = 'cached_token'

            token = await api_client.token
            assert token == 'cached_token'

    @pytest.mark.asyncio
    async def test_make_request_success(self, api_client):
        """Тест успешного выполнения запроса"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch.object(api_client.client, 'get', return_value=mock_response) as mock_get:
            result = await api_client._make_request('test_endpoint')

            mock_get.assert_called_once_with(
                'https://vpn.works/test_endpoint',
                headers=api_client.user_headers
            )
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_make_request_401_retry(self, api_client):
        """Тест повторного запроса при 401 ошибке"""
        # Первый ответ с 401
        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401

        # Второй успешный ответ
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.raise_for_status = MagicMock()

        with patch.object(api_client.client, 'get', side_effect=[mock_response_401, mock_response_200]) as mock_get, \
             patch.object(api_client, '_get_token') as mock_get_token:

            result = await api_client._make_request('test_endpoint')

            assert mock_get.call_count == 2
            mock_get_token.assert_called_once()
            assert result == mock_response_200

    @pytest.mark.asyncio
    async def test_get_users(self, api_client):
        """Тест получения списка пользователей"""
        mock_response = MagicMock()
        mock_response.json.return_value = [{'UserID': 1, 'UserName': 'test'}]

        with patch.object(api_client, '_make_request', return_value=mock_response) as mock_request:
            result = await api_client.get_users()

            mock_request.assert_called_once_with('user')
            assert result == [{'UserID': 1, 'UserName': 'test'}]

    @pytest.mark.asyncio
    async def test_get_users_stats(self, api_client):
        """Тест получения статистики пользователей"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'ActiveUsers': [{'Value': 5}]}

        with patch.object(api_client, '_make_request', return_value=mock_response) as mock_request:
            result = await api_client.get_users_stats()

            mock_request.assert_called_once_with('users/stats')
            assert result == {'ActiveUsers': [{'Value': 5}]}

    @pytest.mark.asyncio
    async def test_delete_user(self, api_client):
        """Тест удаления пользователя"""
        user_id = 123
        mock_response = MagicMock()

        with patch.object(api_client, '_make_request', return_value=mock_response) as mock_request:
            result = await api_client.delete_user(user_id)

            mock_request.assert_called_once_with('user/123', req_type='delete')
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_get_user_id(self, api_client):
        """Тест получения ID пользователя по имени"""
        users_data = {
            'user1': {'UserID': 1, 'UserName': 'user1'},
            'user2': {'UserID': 2, 'UserName': 'user2'}
        }

        with patch.object(api_client, 'get_users_dict', return_value=users_data) as mock_get_users:
            # Тест существующего пользователя
            result = await api_client.get_user_id('user1')
            assert result == 1

            # Тест несуществующего пользователя
            result = await api_client.get_user_id('nonexistent')
            assert result is None

            mock_get_users.assert_called()