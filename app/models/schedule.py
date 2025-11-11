# models.py
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    duration = Column(String)
    predecessor = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    status = Column(String)
    wave_height_limit = Column(Float)