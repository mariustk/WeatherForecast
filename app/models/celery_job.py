# models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from datetime import datetime
from app.models import Base

class CeleryJob(Base):
    __tablename__ = "celery_job"
    id = Column(Integer, primary_key=True)

    # Store params as JSON (string) – safer than trying to enforce a schema here.
    params = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="PENDING")
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                         onupdate=datetime.utcnow, nullable=False)

