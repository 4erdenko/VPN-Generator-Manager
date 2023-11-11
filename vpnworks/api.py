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
        self.client = httpx.AsyncClient(verify=False)

    @property
    async def token(self):
        if self._token is None:
            await self._get_token()
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    async def _get_token(self):
        resp = await self.client.post(f'{self.base_url}/token')
        resp.raise_for_status()
        data = resp.json()
        self._token = data['Token']
        self.user_headers['Authorization'] = f'Bearer {self._token}'
        self.config_headers['Authorization'] = f'Bearer {self._token}'

    @retry(stop=stop_after_attempt(3))
    async def _make_request(self, endpoint, req_type='get', headers=None):
        headers = headers or self.user_headers
        method = getattr(self.client, req_type)
        resp = await method(f'{self.base_url}/{endpoint}', headers=headers)
        if resp.status_code == 401:
            await self._get_token()
            headers['Authorization'] = f'Bearer {self._token}'
            return await self._make_request(
                endpoint,
                req_type=req_type,
                headers=headers,
            )
        resp.raise_for_status()
        return resp

    async def get_users(self):
        response = await self._make_request('user')
        return response.json()

    async def get_users_stats(self):
        response = await self._make_request('users/stats')
        return response.json()

    async def delete_user(self, UserID):
        return await self._make_request(
            f'user/{str(UserID)}',
            req_type='delete',
        )

    async def _get_conf_file(self):
        response = await self._make_request(
            endpoint='user', headers=self.config_headers, req_type='post'
        )
        return response.json()

    async def create_conf_file(self):
        data = await self._get_conf_file()
        username = data.get('UserName')
        results: dict[str, str] = {
            'username': username,
            'amnezia': '',
            'wireguard': '',
            'outline': '',
        }

        amnezia_config = data.get('AmnzOvcConfig')
        if amnezia_config:
            amnezia_filename = amnezia_config.get('FileName')
            amnezia_file_content = amnezia_config.get('FileContent')
            if amnezia_filename and amnezia_file_content:
                async with aiofiles.open(amnezia_filename, 'w') as file:
                    await file.write(amnezia_file_content)
                results.update({'amnezia': amnezia_filename})

        wireguard_config = data.get('WireguardConfig')
        if wireguard_config:
            wireguard_filename = wireguard_config.get('FileName')
            wireguard_file_content = wireguard_config.get('FileContent')
            if wireguard_filename and wireguard_file_content:
                async with aiofiles.open(wireguard_filename, 'w') as f:
                    await f.write(wireguard_file_content)
                results.update({'wireguard': wireguard_filename})

        outline_config = data.get('OutlineConfig')
        if outline_config:
            outline_key = outline_config.get('AccessKey')
            if outline_key:
                results.update({'outline': outline_key})

        if not results:
            return 'No configurations provided'
        return results

    async def get_users_dict(self):
        users = await self.get_users()
        users_dict = {user['UserName']: user for user in users}
        return users_dict

    async def get_user_id(self, name):
        users_dict = await self.get_users_dict()
        return users_dict.get(str(name), {}).get('UserID')
