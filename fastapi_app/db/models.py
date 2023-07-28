import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, index=True)
    request_date = Column(DateTime, default=datetime.datetime.utcnow)
    request_path = Column(String)
    request_method = Column(String)
    request_args = Column(JSON)
    response_status = Column(Integer)
    response_body = Column(JSON)
