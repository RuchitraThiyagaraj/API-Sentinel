"""
database.py
-----------
Sets up the SQLAlchemy engine, session factory, and declarative Base.

Flow:
FastAPI  ->  SQLAlchemy Session  ->  MySQL
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:root15@localhost:3306/api_sentinel",
)

# pool_pre_ping avoids "MySQL server has gone away" errors on idle connections
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a DB session per request
    and always closes it afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
