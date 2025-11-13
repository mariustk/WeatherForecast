from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv("DATABASE_URL","postgresql+psycopg2://postgres:postgres@localhost:5432/appdb")

# Create the engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True) #Pre ping just checks the db is allive in the begining

# Create a session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    """
    FastAPI dependency that yields a SQLAlchemy session.
    Closes it automatically after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
