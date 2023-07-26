from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    request_date = Column(DateTime, default=datetime.datetime.utcnow)
    request_path = Column(String)
    request_method = Column(String)
    request_args = Column(JSON)
    response_status = Column(Integer)
    response_body = Column(JSON)
