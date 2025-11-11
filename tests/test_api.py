from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, Dict

from app.main import weather_data
from app.models.schedule import Task


class DummyResponse:
    def __init__(self, status_code: int, data: Dict[str, Any]):
        self.status_code = status_code
        self._data = data
        self.text = ""

    def json(self) -> Dict[str, Any]:
        return self._data


class DummyAsyncClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def __aenter__(self) -> "DummyAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        return None

    async def get(self, url: str, params: Dict[str, Any]):  # type: ignore[override]
        start = datetime.fromtimestamp(params["from"], tz=timezone.utc)
        points = []
        for hour in range(4):
            timestamp = (start + timedelta(hours=hour)).replace(microsecond=0)
            points.append(
                {
                    "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
                    "wind_speed": 5 + hour,
                    "wave_height": 0.5,
                    "wave_period": 10,
                }
            )
        return DummyResponse(200, {"forecast": points})


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_weather_endpoint_filters_by_time(client):
    first_point = weather_data["forecast"][0]
    start = datetime.fromisoformat(first_point["timestamp"].replace("Z", "+00:00"))
    from_ts = int(start.timestamp())
    to_ts = int((start + timedelta(hours=1)).timestamp())

    response = client.get(
        "/weather",
        params={"location": "60.0,5.0", "from": from_ts, "time_to": to_ts},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["location"] == {"lat": 60.0, "lon": 5.0}
    assert all(
        from_ts <= datetime.fromisoformat(point["timestamp"].replace("Z", "+00:00")).timestamp() <= to_ts
        for point in body["forecast"]
    )


def test_weather_endpoint_invalid_location(client):
    response = client.get(
        "/weather",
        params={"location": "invalid", "from": 0, "time_to": 1},
    )
    assert response.status_code == 400


def test_schedule_window_returns_analysis(monkeypatch, client, db_session, sample_task):
    from app.routers import schedule

    monkeypatch.setattr(schedule, "httpx", SimpleNamespace(AsyncClient=DummyAsyncClient))

    response = client.get(
        "/schedule/window",
        params={
            "schedule_id": sample_task.id,
            "lat": 60.0,
            "lon": 5.0,
            "lookahead_hours": 4,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["schedule_id"] == sample_task.id
    assert body["task"]["duration"] == sample_task.duration
    assert len(body["hourly_forecast"]) >= 1
    assert body["analysis"]["go_no_go"]
    assert body["analysis"]["start_windows"]


def test_mark_task_complete_updates_status(client, db_session):
    task = Task(
        name="Calibrate equipment",
        duration="3h",
        predecessor=None,
        status="PLANNED",
        wave_height_limit=1.5,
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.put(f"/schedule/task/{task.id}/complete")

    assert response.status_code == 200
    payload = response.json()
    assert payload["task"]["status"] == "COMPLETED"

    db_session.refresh(task)
    assert task.status == "COMPLETED"
