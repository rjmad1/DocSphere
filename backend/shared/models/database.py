"""
EKOS Database Infrastructure & Connection Pooling
Configures SQLAlchemy engine, session management, and database configuration.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_URI = os.getenv("POSTGRES_URI", "sqlite:///./ekos_production.db")

engine = create_engine(
    POSTGRES_URI,
    connect_args={"check_same_thread": False} if POSTGRES_URI.startswith("sqlite") else {},
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
