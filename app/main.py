from fastapi import FastAPI, Query, HTTPException
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import json
from pathlib import Path
from app.api import schedule
from app.api import celeri_worker
from app.api import external_weather
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models.schedule import Task, Base
from app.init_mock_schedule_db import init_db_demo

app = FastAPI()
app.include_router(schedule.router)
app.include_router(celeri_worker.router)
app.include_router(external_weather.router)



init_db_demo()

@app.get("/")
def root():
    return {"message": "Hello World"}

