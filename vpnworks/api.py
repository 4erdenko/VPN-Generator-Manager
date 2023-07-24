import asyncio
import json
import logging
from pprint import pprint

import aiofiles
import aiohttp
from tenacity import retry, stop_after_attempt

logger = logging.getLogger(__name__)


class VpnWorksApi:
    base_url = 'https://vpn.works'

    def __init__(self):
        self._token = None
        self._base_headers = {'Accept': 'application/json, text/plain, */*'}
        self.token_headers = self._base_headers
        self.user_headers = self._base_headers
        self.config_headers = {
            **self._base_headers,
            'Accept': 'application/json',
        }

    @property
    async def token(self):
        if self._token is None:
            await self._get_token()
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    async def _get_token(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.base_url}/token') as resp:
                resp.raise_for_status()
                data = await resp.json()
                self._token = data['Token']
                self.user_headers['Authorization'] = f'Bearer {self._token}'
                self.config_headers['Authorization'] = f'Bearer {self._token}'

    @retry(stop=stop_after_attempt(3))
    async def _make_request(
        self, endpoint, req_type='get', headers=None, as_json=True
    ):
        headers = headers or self.user_headers
        async with aiohttp.ClientSession() as session:
            method = getattr(session, req_type)
            async with method(
                f'{self.base_url}/{endpoint}', headers=headers
            ) as resp:
                if resp.status == 401:
                    await self._get_token()
                    return await self._make_request(
                        endpoint,
                        req_type=req_type,
                        headers=headers,
                        as_json=as_json,
                    )
                resp.raise_for_status()
                if as_json:
                    return await resp.json()
                else:
                    return resp.status

    async def get_users(self):
        return await self._make_request('user')

    async def get_user_stats(self):
        return await self._make_request('users/stats')

    async def delete_user(self, UserID):
        return await self._make_request(
            f'user/{str(UserID)}', req_type='delete', as_json=False
        )

    async def _get_conf_file(self):
        return await self._make_request(
            endpoint='user', headers=self.config_headers, req_type='post'
        )

    async def create_conf_file(self):
        data = await self._get_conf_file()
        wireguard_config = data.get('WireguardConfig')
        filename = wireguard_config.get('FileName')
        file_content = wireguard_config.get('FileContent')

        if filename:
            async with aiofiles.open(filename, 'w') as f:
                await f.write(file_content)
                return True
        else:
            return 'No filename provided'

    @staticmethod
    async def make_users_dict(users):
        users_dict = {}
        for user in users:
            users_dict[user['UserName']] = user
        return users_dict


# async def main():
#     client = VpnWorksApi()
#
#
# if __name__ == '__main__':
#     asyncio.run(main())