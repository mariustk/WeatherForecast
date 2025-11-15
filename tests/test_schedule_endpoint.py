import os
from datetime import datetime, timedelta, timezone
import re
from fastapi import FastAPI
from fastapi.testclient import TestClient
import requests
from app.api.external_weather import router as weather_router

def test_schedule_tasks_format():

    api_address = os.getenv("API_URL")
    response = requests.get(f"{api_address}/schedule/tasks")
    required_keys = {
        "id",
        "name",
        "duration",
        "predecessor",
        "status",
        "wave_height_limit",
    }

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    for task in data:
        # Must be a dict with exactly these keys
        assert isinstance(task, dict)
        assert set(task.keys()) == required_keys

        # Types
        assert isinstance(task["id"], int)
        assert isinstance(task["name"], str)

        # duration like "4h"
        assert isinstance(task["duration"], str)

        # predecessor can be int or None
        assert task["predecessor"] is None or isinstance(task["predecessor"], int)

        # Check status codes
        assert task["status"] in {"COMPLETED", "READY", "BLOCKED"}

        # float-ish wave height
        assert isinstance(task["wave_height_limit"], (int, float))
