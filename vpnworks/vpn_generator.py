import json
import logging
import re

import httpx

logger = logging.getLogger(__name__)


def get_token():
    """
    This function is used to obtain a bearer token for making authorized
    requests to the 'https://vpn.works' API.

    Returns:
        str: The bearer token as a string if successful.
        Otherwise, it returns the error message.
    """
    try:
        headers_token = {
            'Accept': 'application/json, text/plain, */*',
        }
        response_token = httpx.post(
            'https://vpn.works/token', headers=headers_token
        )
        token = response_token.json().get('Token')
    except Exception as error:
        logger.error(f'Error while getting token: {error}')
        return f'Error while getting token: {error}'
    logger.info('Token successfully got')
    return token


def get_user():
    """
    This function retrieves the user's data from
    the 'https://vpn.works' API using the bearer token.

    Returns:
        dict: The user data as a dictionary if successful.
        Otherwise, it returns the error message.
    """
    bearer_token = get_token()
    try:
        headers_user = {
            'Accept': 'application/json, text/plain, */*',
            'Authorization': f'Bearer {bearer_token}',
        }
        response_user = httpx.get(
            'https://vpn.works/user', headers=headers_user
        )
    except Exception as error:
        logger.error(f'Error while getting user: {error}')
        return f'Error while getting user: {error}'
    logger.info('Json successfully got')
    return response_user.json()


def make_user_json():
    """
    This function writes the user's data to a local JSON file.
    """
    web_file = get_user()
    with open('user.json', 'w', encoding='utf-8') as f:
        json.dump(web_file, f, indent=4, ensure_ascii=False)
    logger.info('Json successfully created')


def read_user_json():
    """
    This function reads the user's data from a local JSON file.

    Returns:
        dict: The user data as a dictionary.
    """
    with open('user.json', 'r', encoding='utf-8') as f:
        user_json = json.load(f)
    logger.info('Json successfully read')
    return user_json


def make_config():
    """
    This function makes a configuration request to
    the 'https://vpn.works' API and saves the response as a file.

    Returns:
        str: The filename if successful.
        Otherwise, it returns the error message.
    """
    bearer_token = get_token()
    try:
        headers_config = {
            'Accept': 'application/octet-stream',
            'Authorization': f'Bearer {bearer_token}',
        }

        response_config = httpx.post(
            'https://vpn.works/user', headers=headers_config
        )
        content_disposition = response_config.headers.get(
            'Content-Disposition'
        )
        filename = re.findall(
            r"filename\*=utf-8''([^;]*)", content_disposition
        )[0].strip()
    except Exception as error:
        logger.error(f'Error when trying to make config: {error}')
        return f'Error when trying to make config: {error}'
    if filename:
        with open(filename, 'wb') as f:
            f.write(response_config.content)
    else:
        logger.error('Error when trying to make config')
        return 'Error when trying to create config file'
    logger.info('Config successfully created')
    return filename


def shorten_name(full_name):
    """
    This function shortens a full name by reducing the middle name
    to an initial.

    Args:
        full_name (str): The full name to be shortened.

    Returns:
        str: The shortened name if successful.
        Otherwise, it returns the error message.
    """
    try:
        parts = full_name.split()
        first_part = parts[0]
        second_part = parts[1][0] + '.' if len(parts) > 1 else ''
        rest = ' '.join(parts[2:])
    except Exception as error:
        logger.error(f'Error when trying to shorten name: {error}')
        return f'Error when trying to shorten name: {error}'
    return f'{first_part} {second_part} {rest}'


def delete_user(UserID):
    """
    This function sends a delete request to the 'https://vpn.works' API
    to delete a user.

    Args:
        UserID (str): The ID of the user to be deleted.

    Returns:
        bool: True if successful, otherwise it returns the error message.
    """
    bearer_token = get_token()
    try:
        headers_delete = {
            'Accept': 'application/json, text/plain, */*',
            'Authorization': f'Bearer {bearer_token}',
        }
        response_delete = httpx.delete(
            f'https://vpn.works/user/{UserID}',
            headers=headers_delete,
        )
    except Exception as error:
        logger.error(f'Error when trying to delete user: {error}')
        return f'Error when trying to delete user: {error}'
    if response_delete.status_code == 204:
        logger.info('User successfully deleted')
        return True


def get_user_id_by_name(user_name):
    """
    This function retrieves the ID of a user by searching the user list
    for a specific username.

    Args:
        user_name (str): The username to search for.

    Returns:
        str: The user ID if successful. Otherwise,
        it returns the error message.
    """
    user_list = get_user()
    try:
        for user in user_list:
            if user['UserName'].startswith(user_name):
                return user['UserID']
    except Exception as error:
        logger.error(f'Error while trying to get user id by name: {error}')
        return f'Error while trying to get user id by name: {error}'
    logger.info('User id successfully got')
    return None


def get_stats():
    """
    This function retrieves the stats of the VPN server.
    :return: The stats if successful. Otherwise,
        it returns the error message.
    """
    bearer_token = get_token()
    try:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Authorization': f'Bearer {bearer_token}',
        }
        response = httpx.get(
            'https://vpn.works/users/stats',
            headers=headers,
        )
        acitve_users_all = response.json().get('ActiveUsers')
        active_users = acitve_users_all[-1]['Value']
        total_users_all = response.json().get('TotalUsers')
        total_users = total_users_all[-1]['Value']
        total_traffic_all = response.json().get('TotalTrafficGB')
        total_traffic = total_traffic_all[-1]['Value']
        logger.info('Stats successfully got')
        return active_users, total_users, total_traffic
    except Exception as error:
        logger.error(f'Error while trying to get stats: {error}')
        return f'Error while trying to get stats: {error}'
