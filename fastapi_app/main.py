import json
import os
from datetime import date, datetime
from typing import Any, Dict, Generator, List, Optional, Union

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import Log
from vpnworks.api import VpnWorksApi


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
api = VpnWorksApi()


def remove_file(filename: str) -> None:
    os.remove(filename)


def user_not_found():
    raise HTTPException(status_code=404, detail='User not found')



@app.middleware('http')
async def log_request(request: Request, call_next) -> Union[StreamingResponse, FileResponse, JSONResponse]:
    response = await call_next(request)

    db = SessionLocal()

    response_info = {'media_type': response.headers.get('content-type')}

    if isinstance(response, StreamingResponse):
        response_info['response_type'] = 'streaming'
    elif isinstance(response, FileResponse):
        response_info['response_type'] = 'file'
        response_info['filename'] = response.filename
    elif isinstance(response, JSONResponse):
        response_info['response_type'] = 'json'
        response_info['content'] = response.body.decode('utf-8')
    else:
        response_info['response_type'] = 'regular'
        response_info['content'] = response.body.decode('utf-8')

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


@app.get('/token', description='Retrieve the API token')
async def get_token() -> JSONResponse:
    token = await api.token
    return JSONResponse({'Bearer token': token})


@app.get('/users', description='Retrieve a list of all users')
async def get_users() -> JSONResponse:
    users = await api.get_users()
    return JSONResponse(users)


@app.get('/user/id/{id}', description='Retrieve a user by their ID')
async def get_user_by_id(id: int) -> Dict[str, Any]:
    response = await get_users()
    users = json.loads(response.body)
    try:
        return users[id]
    except IndexError:
        user_not_found()  # Just call the function to raise the exception



@app.get('/user/name/{name}', description='Retrieve a user by their name')
async def get_user_by_name(name: str) -> Union[Dict[str, Any]]:
    users_dict = await api.get_users_dict()
    user = users_dict.get(name)
    if not user:
        return user_not_found()
    return user


@app.delete('/user/delete/{user_id}', description='Delete a user by their ID')
async def delete_user(user_id: str) -> Union[int]:
    result_code = await api.delete_user(user_id)
    if result_code == 403:
        return user_not_found()
    return result_code


@app.get('/user/{name}/stats', description='Get personal stats for user via username')
async def get_personal_stats(name: str) -> Union[Dict[str, Dict[str, Union[str, int, None]]]]:
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
                'Status': status,
            }
        }
    else:
        return user_not_found()


@app.get('/config', description='Create and download user conf file')
async def get_config_file(background_tasks: BackgroundTasks) -> FileResponse:
    filename, _ = await api.create_conf_file()
    background_tasks.add_task(remove_file, filename)
    return FileResponse(filename, filename=filename)


class LogOut(BaseModel):
    request_date: datetime
    request_path: Optional[str]
    request_method: Optional[str]
    request_args: Optional[dict]
    response_status: Optional[int]
    response_body: Optional[Dict[Optional[str], Any]]

    class Config:
        from_attributes = True


@app.get('/logs', response_model=List[LogOut])
async def get_logs(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    offset: int = 0,
    order: Optional[str] = 'desc',
    db: Session = Depends(get_db),
) -> List[LogOut]:
    if order not in ['asc', 'desc']:
        raise HTTPException(
            status_code=400, detail="Order must be either 'asc' or 'desc'"
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(400, 'Start date must be before end date')

    logs_query = db.query(Log)

    if start_date:
        start_date = datetime.combine(start_date, datetime.min.time())
        logs_query = logs_query.filter(Log.request_date >= start_date)

    if end_date:
        end_date = datetime.combine(end_date, datetime.max.time())
        logs_query = logs_query.filter(Log.request_date <= end_date)

    if order == 'desc':
        logs_query = logs_query.order_by(Log.request_date.desc())
    else:
        logs_query = logs_query.order_by(Log.request_date)

    logs = logs_query.limit(limit).offset(offset).all()

    log_outs = [LogOut(**log.__dict__) for log in logs]

    return log_outs
