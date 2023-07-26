import json
import os
from typing import Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse

from database.database import SessionLocal
from database.models import Log
from vpnworks.api import VpnWorksApi
from sqlalchemy.orm import Session
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()
api = VpnWorksApi()


def remove_file(filename: str):
    os.remove(filename)


def user_not_found():
    raise HTTPException(status_code=404, detail='User not found')


@app.middleware("http")
async def log_request(request: Request, call_next):
    response = await call_next(request)

    db = SessionLocal()

    response_info = {"media_type": response.headers.get('content-type')}

    if isinstance(response, StreamingResponse):
        response_info["response_type"] = "streaming"
    elif isinstance(response, FileResponse):
        response_info["response_type"] = "file"
        response_info["filename"] = response.filename
    elif isinstance(response, JSONResponse):
        response_info["response_type"] = "json"
        response_info["content"] = response.content.decode("utf-8")
    else:
        response_info["response_type"] = "regular"
        response_info["content"] = response.body.decode("utf-8")

    log = Log(
        request_path=request.url.path,
        request_method=request.method,
        request_args=dict(request.query_params),
        response_status=response.status_code,
        response_body=response_info,
    )
    db.add(log)
    db.commit()
    db.close()

    return response







@app.get('/token', description="Retrieve the API token")
async def get_token():
    token = await api.token
    return JSONResponse({'Bearer token': token})


@app.get('/users', description="Retrieve a list of all users")
async def get_users():
    users = await api.get_users()
    return JSONResponse(users)


@app.get('/user/id/{id}', description="Retrieve a user by their ID")
async def get_user_by_id(id: int):
    response = await get_users()
    users = json.loads(response.body)
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
