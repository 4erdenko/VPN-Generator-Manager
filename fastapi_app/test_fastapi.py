# from fastapi import FastAPI
# from fastapi.testclient import TestClient
# from fastapi_app.main import app, get_db
# from db.models import Log, Base  # Импортируем существующую базу
# from datetime import datetime
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from unittest.mock import Mock, patch
# import pytest
#
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Base.metadata.create_all(bind=engine)  # Создание всех таблиц в базе данных
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
#
# def override_get_db():
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()
#
# @pytest.fixture()
# def client():
#     with TestClient(app) as client:
#         yield client
#
# def test_get_logs(client):
#     with TestingSessionLocal() as db:
#
#         log1 = Log(
#             request_date=datetime.strptime("2023-08-11T15:25:00.396061", "%Y-%m-%dT%H:%M:%S.%f"),
#             request_path="/logs",
#             request_method="GET",
#             request_args={},
#             response_status=200,
#             response_body='''{}'''
#         )
#
#         db.add(log1)
#         db.commit()
#
#         # Temporarily replace the get_db dependency
#         original_get_db = app.dependency_overrides.get(get_db)
#         app.dependency_overrides[get_db] = override_get_db
#
#         response = client.get("/logs")
#
#         # Restore the original get_db function
#         app.dependency_overrides[get_db] = original_get_db
#         print(response.text)
#         assert response.status_code == 200
#         data = response.json()
#         print(data)
#
#         # Make sure that the response includes the log we added
#         # assert len(data) == 1
#         # assert data[0]["request_path"] == "/logs"
#         # assert data[0]["request_method"] == "GET"
