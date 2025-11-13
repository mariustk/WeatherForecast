from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List, Dict, Any
from app.models.celery_job import CeleryJob
from app.celery_app import celery_app
from sqlalchemy import select
import json

router = APIRouter(prefix="/celery-worker", tags=["celery worker"])

@router.post("/submit_complicated_job", status_code=202) # Staus code 202 Accepted
def submit_complicated_job(params: dict, db: Session = Depends(get_db)):
    job = CeleryJob(params=json.dumps(params), status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)
    celery_app.send_task(
        "complicated_analysis.run_analysis",
        kwargs={"job_id": job.id, "params": params},
    )

    return {"job_id": job.id, "status": job.status}

@router.get("/tasks")
def get_celery_tasks(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Return all task."""
    tasks = db.execute(select(CeleryJob)).scalars().all()
    return [
        {
            "id": t.id,
            "status": t.status,
            "params": t.params,
            "created_at": t.created_at,
            "updated_at": t.updated_at
        }
        for t in tasks
    ]
