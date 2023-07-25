from typing import Optional

from fastapi import FastAPI
from vpnworks.api import VpnWorksApi  # Убедитесь, что путь импорта корректен

app = FastAPI()
api = VpnWorksApi()


@app.get('/token')
async def get_token():
    token = await api.token
    return {'Bearer token': token}


@app.get('/users')
async def get_users():
    return await api.get_users()

@app.get('/user')
async def get_user(name: Optional[str] = None, id: Optional[int] = None):
    if name is not None:
        users_dict = await api.get_users_dict()
        return users_dict.get(name)
    elif id is not None:
        users = (await get_users())
        try:
            return users[id]
        except IndexError:
            return {'status':'User not found'}
    else:
        return {'status':'No name or id provided'}


@app.get('/user/delete/{user_id}')
async def delete_user(user_id: str):
    result = await api.delete_user(user_id)
    return {'status': result}


@app.get('/user/{name}/stats')
async def get_personal_stats(name: str):
    users = await api.get_users_dict()
    user = users.get(str(name))
    created_date = user.get('CreatedAt')
    last_visited = user.get('LastVisitHour')
    gb_quota = user.get('MonthlyQuotaRemainingGB')
    return {
        name: {
            'CreatedAt': created_date,
            'LastVisitHour': last_visited,
            'MonthlyQuotaRemainingGB': gb_quota,
        }
    }




@app.get('/config')
async def get_config_file():
    return await api.get_conf_file()
