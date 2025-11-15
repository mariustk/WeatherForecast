from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.external_weather import router as weather_router


def test_weather_endpoint_filters_forecast_range():
    app = FastAPI()
    app.include_router(weather_router)
    client = TestClient(app)

    target_time = datetime.fromisoformat("2025-11-11T21:55:23+00:00")
    params = {
        "location": "61.5,4.8",
        "from": int((target_time - timedelta(minutes=5)).replace(tzinfo=timezone.utc).timestamp()),
        "time_to": int((target_time + timedelta(minutes=5)).replace(tzinfo=timezone.utc).timestamp()),
    }

    response = client.get("/weather-service/weather", params=params)

    assert response.status_code == 200
    payload = response.json()

    assert payload["location"] == {"lat": 61.5, "lon": 4.8}
    assert len(payload["forecast"]) == 1

    forecast_entry = payload["forecast"][0]
    assert forecast_entry["timestamp"] == "2025-11-11T21:55:23Z"
    assert forecast_entry["wave_height"] == 2.7
