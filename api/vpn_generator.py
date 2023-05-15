from pprint import pprint
import json
import re

import httpx


def get_token():
    headers_token = {
        'Accept': 'application/json, text/plain, */*',
    }
    response_token = httpx.post('https://w02s50ss63ae.vpn.works/token',
                                headers=headers_token)
    token = response_token.json().get('Token')
    return token


bearer_token = get_token()


def get_user():
    headers_user = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'Bearer {bearer_token}',
    }
    response_user = httpx.get('https://w02s50ss63ae.vpn.works/user', headers=headers_user)
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
    headers_config = {
        'Accept': 'application/octet-stream',
        'Authorization': f'Bearer {bearer_token}',
    }

    response_config = httpx.post(
        'https://w02s50ss63ae.vpn.works/user', headers=headers_config
    )
    content_disposition = response_config.headers.get('Content-Disposition')
    filename = re.findall("filename\*=utf-8''([^;]*)",
                          content_disposition)[0].strip()
    with open(filename, 'wb') as f:
        f.write(response_config.content)

    return filename


def shorten_name(full_name):
    parts = full_name.split()
    first_part = parts[0]
    second_part = parts[1][0] + '.' if len(parts) > 1 else ''
    rest = ' '.join(parts[2:])
    return f"{first_part} {second_part} {rest}"
