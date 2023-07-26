# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# database.py
SQLALCHEMY_DATABASE_URL = 'postgresql://username:password@db:5432/database'





engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
