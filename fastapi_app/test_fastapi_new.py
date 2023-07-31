from datetime import datetime

import pytest
from db.models import Log
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db

# Подготовка тестовой базы данных SQLite в памяти
SQLALCHEMY_DATABASE_URL = 'sqlite:///:memory:'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Подготовка клиента для тестирования
client = TestClient(app)


@pytest.fixture(scope='module')
def test_database():
    # Создаем таблицы
    from db.models import Base

    Base.metadata.create_all(bind=engine)

    # Добавляем тестовые логи
    session = TestingSessionLocal()
    logs = [
        Log(
            request_date=datetime(2023, 7, 28, 10, 30),
            request_path='/test1',
            request_method='GET',
            request_args={'param1': 'value1'},
            response_status=200,
            response_body={'key': 'value'},
        ),
        Log(
            request_date=datetime(2023, 7, 29, 14, 15),
            request_path='/test2',
            request_method='POST',
            request_args={'param2': 'value2'},
            response_status=404,
            response_body={'error': 'Not Found'},
        ),
    ]
    for log in logs:
        session.add(log)

    session.commit()
    session.close()
    yield

    # Удаляем тестовую базу данных после завершения всех тестов
    Base.metadata.drop_all(bind=engine)


from unittest.mock import patch

from main import app, get_logs


# Замокаем функцию get_logs, чтобы она возвращала фейковый результат
@patch('main.get_logs')
def test_get_logs_success(mock_get_logs):
    # Указываем, что функция get_logs должна вернуть фейковые данные
    mock_get_logs.return_value = [
        {
            'request_date': '2023-07-28T10:30:00',
            'request_path': '/test1',
            'request_method': 'GET',
            'request_args': {'param1': 'value1'},
            'response_status': 200,
            'response_body': {'key': 'value'},
        },
        {
            'request_date': '2023-07-29T14:15:00',
            'request_path': '/test2',
            'request_method': 'POST',
            'request_args': {'param2': 'value2'},
            'response_status': 404,
            'response_body': {'error': 'Not Found'},
        },
    ]

    with TestClient(app) as client:
        response = client.get('/logs')

    assert response.status_code == 200
    assert response.json() == [
        {
            'request_date': '2023-07-28T10:30:00',
            'request_path': '/test1',
            'request_method': 'GET',
            'request_args': {'param1': 'value1'},
            'response_status': 200,
            'response_body': {'key': 'value'},
        },
        {
            'request_date': '2023-07-29T14:15:00',
            'request_path': '/test2',
            'request_method': 'POST',
            'request_args': {'param2': 'value2'},
            'response_status': 404,
            'response_body': {'error': 'Not Found'},
        },
    ]


def test_get_logs_invalid_order(test_database):
    response = client.get('/logs?order=invalid')
    assert response.status_code == 400
    assert response.json() == {
        'detail': "Order must be either 'asc' or 'desc'"
    }


def test_get_logs_invalid_dates(test_database):
    response = client.get('/logs?start_date=2023-07-30&end_date=2023-07-28')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Start date must be before end date'}


def test_get_logs_no_logs(test_database):
    response = client.get('/logs?limit=0')
    assert response.status_code == 200
    assert response.json() == []
