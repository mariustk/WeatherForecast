from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.models import Base

class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    duration = Column(String)
    predecessor = Column(Integer, ForeignKey("task.id"), nullable=True)
    status = Column(String)
    wave_height_limit = Column(Float)