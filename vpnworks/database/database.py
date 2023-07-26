# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = ('postgresql://postgres:uFB%26kDZ%2At%23L%5E3J2q4kS4rnr%2ANRfR%40q@localhost:5432/api_test')




engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
