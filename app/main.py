from fastapi import FastAPI
from app.api import schedule
from app.api import celeri_worker
from app.api import external_weather
from app.init_mock_schedule_db import init_db_demo

app = FastAPI()
app.include_router(schedule.router)
app.include_router(celeri_worker.router)
app.include_router(external_weather.router)

init_db_demo()

@app.get("/")
def root():
    return {"message": "Hello World"}

