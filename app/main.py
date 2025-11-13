from fastapi import FastAPI, Query, HTTPException
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import json
from pathlib import Path
from app.api import schedule
from app.api import heavy_lift_job
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models.schedule import Task, Base


app = FastAPI()
app.include_router(schedule.router)
app.include_router(heavy_lift_job.router)


# Load JSON mock at startup
DATA_PATH = Path(__file__).parent / "mock_forecast.json"
with open(DATA_PATH, "r") as f:
    weather_data = json.load(f)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/weather")
def get_weather(
    location: str = Query(..., description="Format: lat,lon"),
    time_from: int = Query(..., alias="from", description="Start timestamp (unix seconds, UTC)"),
    time_to: int = Query(..., description="End timestamp (unix seconds, UTC)")
) -> Dict[str, Any]:
    # Parse and validate location
    try:
        lat_str, lon_str = location.split(",")
        lat, lon = float(lat_str), float(lon_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid location format. Expected 'lat,lon'.")

    # Time bounds (UTC-aware)
    from_time = datetime.fromtimestamp(time_from, tz=timezone.utc)
    to_time = datetime.fromtimestamp(time_to, tz=timezone.utc)

    # Filter forecast entries by time range (timestamps in JSON are Z/UTC)
    filtered_forecast = []
    for entry in weather_data["forecast"]:
        entry_time = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
        if from_time <= entry_time <= to_time:
            filtered_forecast.append(entry)

    # Echo requested location; or validate against file if you prefer
    return {
        "location": {"lat": lat, "lon": lon},
        "forecast": filtered_forecast,
    }


@app.get("/weather_next_12_hours")
def get_weather_next_12_hours(location: str = Query(..., description="Format: lat,lon")) -> Dict[str, Any]:

    # Parse and validate location
    try:
        lat_str, lon_str = location.split(",")
        lat, lon = float(lat_str), float(lon_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid location format. Expected 'lat,lon'.")

    # Time bounds (UTC-aware)
    from_time = datetime.now(tz=timezone.utc)
    to_time = from_time + timedelta(hours=12)

    # Filter forecast entries by time range (timestamps in JSON are Z/UTC)
    filtered_forecast = []
    for entry in weather_data["forecast"]:
        entry_time = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
        if from_time <= entry_time <= to_time:
            filtered_forecast.append(entry)


    # Echo requested location; or validate against file if you prefer
    return {
        "location": {"lat": lat, "lon": lon},
        "forecast": filtered_forecast,
    }