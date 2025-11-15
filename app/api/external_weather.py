"""Weather service endpoints backed by the static JSON forecast file."""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Load JSON mock at startup
DATA_PATH = Path(__file__).parent.parent / "mock_forecast.json"
with open(DATA_PATH, "r") as f:
    weather_data = json.load(f)

router = APIRouter(prefix="/weather-service", tags=["weather service"])

@router.get("/weather")
def get_weather(
    location: str = Query("61.5,4.8", description="Format: lat,lon"),
    time_from: int = Query(..., alias="from", description="Start timestamp (unix seconds, UTC)"),
    time_to: int = Query(...,le=10000000000, description="End timestamp (unix seconds, UTC)")
) -> Dict[str, Any]:
    """Return forecast data filtered by the requested location and time range."""
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

    # Echo requested location
    return {
        "location": {"lat": lat, "lon": lon},
        "forecast": filtered_forecast,
    }

@router.get("/weather_next_12_hours")
def get_weather_next_12_hours(location: str = Query(..., description="Format: lat,lon")) -> Dict[str, Any]:
    """Return the next twelve hours of forecast data for the requested location."""

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