from typing import Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from vpnworks.api import VpnWorksApi

app = FastAPI()
api = VpnWorksApi()


def remove_file(filename: str):
    os.remove(filename)


def user_not_found():
    raise HTTPException(status_code=404, detail='User not found')


@app.get('/token', description="Retrieve the API token")
async def get_token():
    token = await api.token
    return {'Bearer token': token}


@app.get('/users', description="Retrieve a list of all users")
async def get_users():
    return await api.get_users()


@app.get('/user/id/{id}', description="Retrieve a user by their ID")
async def get_user_by_id(id: int):
    users = await get_users()
    try:
        return users[id]
    except IndexError:
        return user_not_found()


@app.get('/user/name/{name}', description="Retrieve a user by their name")
async def get_user_by_name(name: str):
    users_dict = await api.get_users_dict()
    user = users_dict.get(name)
    if not user:
        return user_not_found()
    return user


@app.delete('/user/delete/{user_id}', description="Delete a user by their ID")
async def delete_user(user_id: str):
    result_code = await api.delete_user(user_id)
    if result_code == 403:
        return user_not_found()
    return result_code


@app.get('/user/{name}/stats',
description='Get personal stats for user via username')
async def get_personal_stats(name: str):
    users = await api.get_users_dict()
    user = users.get(str(name))
    if user:
        created_date = user.get('CreatedAt')
        last_visited = user.get('LastVisitHour')
        gb_quota = user.get('MonthlyQuotaRemainingGB')
        status = user.get('Status')
        return {
            name: {
                'CreatedAt': created_date,
                'LastVisitHour': last_visited,
                'MonthlyQuotaRemainingGB': gb_quota,
                'Status': status
            }
        }
    else:
        return user_not_found()


@app.get('/config',
description='Create and download user conf file')
async def get_config_file(background_tasks: BackgroundTasks):
    filename, _ = await api.create_conf_file()
    background_tasks.add_task(remove_file, filename)
    return FileResponse(filename, filename=filename)
