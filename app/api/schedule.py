"""Scheduling endpoints that orchestrate tasks using weather forecasts."""

# api/schedule.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models.schedule import Task
from app.database import get_db  # you'd define get_db() returning a session
from app.lib import wow_analysis
from datetime import datetime, timezone, timedelta
import httpx

router = APIRouter(prefix="/schedule", tags=["schedule"])

def parse_hours(duration_str: str) -> int:
    """Convert a duration string such as ``"4h"`` into an integer hour value."""
    # expects like "4h"
    if not duration_str.endswith("h"):
        raise ValueError("duration must be like '4h'")
    return int(duration_str[:-1])

def unix_seconds(dt: datetime) -> int:
    """Convert a timezone-aware datetime into Unix seconds."""
    return int(dt.timestamp())

def iso_utc(dt: datetime) -> str:
    """Serialise a datetime to an ISO 8601 UTC string without fractional seconds."""
    return dt.replace(microsecond=0).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

@router.get("/window") # Async due to "Call to external API (weather forecast)
async def schedule_window(
    schedule_id: int = Query(..., description="ID of the task/schedule"),
    lat: float = Query(61.5),
    lon: float = Query(4.8),
    lookahead_hours: int = Query(12, ge=1, le=168, description="Forecast horizon in hours (default 12)"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Calculate start windows for the schedule based on forecasted wave conditions."""

    # Fetch task
    task = db.get(Task, schedule_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {schedule_id} not found")

    try:
        task_hours = parse_hours(task.duration)          # e.g. "4h" -> 4
        wave_height_limit = float(task.wave_height_limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid task fields: {e}")

    now_utc = datetime.now(tz=timezone.utc)
    end_utc = now_utc + timedelta(hours=lookahead_hours)

    params = {
        "location": f"{lat},{lon}",
        "from": unix_seconds(now_utc),
        "time_to": unix_seconds(end_utc),
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get("http://localhost:8020/weather-service/weather", params=params) # Pretending that this is external
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"Weather API error: {resp.text}")

    data = resp.json()
    raw = data.get("forecast", [])
    if not raw:
        return {
            "schedule_id": schedule_id,
            "task": {"duration": task.duration, "wave_height_limit": wave_height_limit},
            "location": {"lat": lat, "lon": lon},
            "hourly_forecast": [],
            "analysis": {"go_no_go": [], "start_windows": []},
            "note": "No forecast points returned in the requested window.",
        }

    #Resample to 1h spacing by averaging all points within each hour bucket
    buckets = {}
    for p in raw:
        t = datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00"))
        hour_bucket = t.replace(minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

        if hour_bucket not in buckets:
            buckets[hour_bucket] = {"wind_speed": 0.0, "wave_height": 0.0, "wave_period": 0.0, "n": 0}

        b = buckets[hour_bucket]
        b["wind_speed"] += float(p["wind_speed"])
        b["wave_height"] += float(p["wave_height"])
        b["wave_period"] += float(p["wave_period"])
        b["n"] += 1

    # Ensure continuous hourly timeline from the first to last available bucket within [now, end]
    timeline = []
    cur_time = now_utc.replace(minute=0, second=0, microsecond=0)
    end_aligned = end_utc.replace(minute=0, second=0, microsecond=0)
    while cur_time <= end_aligned:
        if cur_time in buckets and buckets[cur_time]["n"] > 0:
            n = buckets[cur_time]["n"]
            timeline.append({
                "timestamp": iso_utc(cur_time),
                "wind_speed": buckets[cur_time]["wind_speed"] / n,
                "wave_height": buckets[cur_time]["wave_height"] / n,
                "wave_period": buckets[cur_time]["wave_period"] / n
            })
        # if an hour has no points, we skip it (keeps result truly based on available data)
        cur_time += timedelta(hours=1)

    if not timeline:
        return {
            "schedule_id": schedule_id,
            "task": {"duration": task.duration, "wave_height_limit": wave_height_limit},
            "location": {"lat": lat, "lon": lon},
            "hourly_forecast": [],
            "analysis": {"go_no_go": [], "start_windows": []},
            "note": "No hourly buckets with data.",
        }

    # WOW analysis over hourly wave height series
    wave_series = [p["wave_height"] for p in timeline]
    go_no_go, start_indices = wow_analysis(wave_series, task_hours, wave_height_limit)

    # Prepare start windows with start + duration
    start_windows = []
    for idx in start_indices:
        start_ts = datetime.fromisoformat(timeline[idx]["timestamp"].replace("Z", "+00:00"))
        end_ts = start_ts + timedelta(hours=task_hours)
        start_windows.append({
            "start": iso_utc(start_ts),
            "end": iso_utc(end_ts),
            "duration_hours": task_hours,
        })

    return {
        "schedule_id": schedule_id,
        "task": {
            "name": getattr(task, "name", None),
            "duration": task.duration,
            "wave_height_limit": wave_height_limit,
        },
        "location": {"lat": lat, "lon": lon},
        "hourly_forecast": timeline,
        "analysis": {
            "go_no_go": go_no_go,   # aligned with hourly_forecast
            "start_windows": start_windows,
        },
    }



@router.get("/tasks")
def get_all_tasks(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Return all tasks stored in the scheduling table."""
    tasks = db.execute(select(Task)).scalars().all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "duration": t.duration,
            "predecessor": t.predecessor,
            "status": t.status,
            "wave_height_limit": t.wave_height_limit,
        }
        for t in tasks
    ]

@router.put("/task/{task_id}/complete") # PUT since we are modifying underlying database
def mark_task_complete(task_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Mark a specific task as completed and return the updated record."""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Update the status
    task.status = "COMPLETED"
    db.commit()
    db.refresh(task)

    return {
        "message": f"Task {task_id} marked as completed",
        "task": {
            "id": task.id,
            "name": task.name,
            "status": task.status,
            "duration": task.duration,
            "predecessor": task.predecessor,
            "wave_height_limit": task.wave_height_limit,
        },
    }


@router.put("/task/{task_id}/started") # PUT since we are modifying underlying database
def mark_task_started(task_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Mark a specific task as started and return the updated record."""
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Update the status
    task.status = "STARTED"
    db.commit()
    db.refresh(task)

    return {
        "message": f"Task {task_id} marked as completed",
        "task": {
            "id": task.id,
            "name": task.name,
            "status": task.status,
            "duration": task.duration,
            "predecessor": task.predecessor,
            "wave_height_limit": task.wave_height_limit,
        },
    }