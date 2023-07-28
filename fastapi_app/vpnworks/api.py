import aiofiles
import httpx
from tenacity import retry, stop_after_attempt


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
        async with httpx.AsyncClient() as client:
            resp = await client.post(f'{self.base_url}/token')
            resp.raise_for_status()
            data = resp.json()
            self._token = data['Token']
            self.user_headers['Authorization'] = f'Bearer {self._token}'
            self.config_headers['Authorization'] = f'Bearer {self._token}'

    @retry(stop=stop_after_attempt(3))
    async def _make_request(self, endpoint, req_type='get', headers=None):
        headers = headers or self.user_headers
        async with httpx.AsyncClient() as client:
            method = getattr(client, req_type)
            resp = await method(f'{self.base_url}/{endpoint}', headers=headers)
            if resp.status_code == 401:
                await self._get_token()
                return await self._make_request(
                    endpoint,
                    req_type=req_type,
                    headers=headers,
                )
            if req_type == 'delete':
                return resp
            resp.raise_for_status()
            return resp

    async def get_users(self):
        response = await self._make_request('user')
        return response.json()

    async def get_users_stats(self):
        response = await self._make_request('users/stats')
        return response.json()

    async def delete_user(self, UserID):
        response = await self._make_request(
            f'user/{str(UserID)}',
            req_type='delete',
        )
        return response.status_code

    async def get_conf_file(self):
        response = await self._make_request(
            endpoint='user', headers=self.config_headers, req_type='post'
        )
        return response.json()

    async def create_conf_file(self):
        data = await self.get_conf_file()
        wireguard_config = data.get('WireguardConfig')
        filename = wireguard_config.get('FileName')
        file_content = wireguard_config.get('FileContent')
        username = data.get('UserName')

        if filename:
            async with aiofiles.open(filename, 'w') as f:
                await f.write(file_content)
                return filename, username
        else:
            return 'No filename provided'

    async def get_users_dict(self):
        users = await self.get_users()
        users_dict = {user['UserName']: user for user in users}
        return users_dict

    async def get_user_id(self, name):
        users_dict = await self.get_users_dict()
        return users_dict.get(str(name), {}).get('UserID')


# async def main():
#     c = VpnWorksApi()
#     # b = await c.get_users_dict()
#     # print(b)
#     d = await c.delete_user('123')
#     print(d)
#
# asyncio.run(main())
