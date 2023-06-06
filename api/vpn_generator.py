import json
import re

import httpx


def get_token():
    try:
        headers_token = {
            'Accept': 'application/json, text/plain, */*',
        }
        response_token = httpx.post(
            'https://w02s50ss63ae.vpn.works/token', headers=headers_token
        )
        token = response_token.json().get('Token')
    except Exception as error:
        return f'Error while getting token: {error}'
    return token


def get_user():
    bearer_token = get_token()
    try:
        headers_user = {
            'Accept': 'application/json, text/plain, */*',
            'Authorization': f'Bearer {bearer_token}',
        }
        response_user = httpx.get(
            'https://w02s50ss63ae.vpn.works/user', headers=headers_user
        )
    except Exception as error:
        return f'Error while getting user: {error}'
    return response_user.json()


def make_user_json():
    web_file = get_user()
    with open('user.json', 'w', encoding='utf-8') as f:
        json.dump(web_file, f, indent=4, ensure_ascii=False)


def read_user_json():
    with open('user.json', 'r', encoding='utf-8') as f:
        user_json = json.load(f)
    return user_json


def make_config():
    bearer_token = get_token()
    try:
        headers_config = {
            'Accept': 'application/octet-stream',
            'Authorization': f'Bearer {bearer_token}',
        }

        response_config = httpx.post(
            'https://w02s50ss63ae.vpn.works/user', headers=headers_config
        )
        content_disposition = response_config.headers.get(
            'Content-Disposition'
        )
        filename = re.findall(
            r"filename\*=utf-8''([^;]*)", content_disposition
        )[0].strip()
    except Exception as error:
        return f'Error when trying to make config: {error}'
    if filename:
        with open(filename, 'wb') as f:
            f.write(response_config.content)
    else:
        return 'Error when trying to create config file'

    return filename


def shorten_name(full_name):
    try:
        parts = full_name.split()
        first_part = parts[0]
        second_part = parts[1][0] + '.' if len(parts) > 1 else ''
        rest = ' '.join(parts[2:])
    except Exception as error:
        return f'Error when trying to shorten name: {error}'
    return f"{first_part} {second_part} {rest}"


def delete_user(UserID):
    bearer_token = get_token()
    try:
        headers_delete = {
            'Accept': 'application/json, text/plain, */*',
            'Authorization': f'Bearer {bearer_token}',
        }
        response_delete = httpx.delete(
            f'https://w02s50ss63ae.vpn.works/user/{UserID}',
            headers=headers_delete,
        )
    except Exception as error:
        return f'Error when trying to delete user: {error}'
    if response_delete.status_code == 204:
        return True


def get_user_id_by_name(user_name):
    user_list = get_user()
    try:
        for user in user_list:
            if user['UserName'].startswith(user_name):
                return user['UserID']
    except Exception as error:
        return f'Error while trying to get user id by name: {error}'
    return None
