from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.heavy_lift_job import HeavyLiftJob
from app.celery_app import celery_app
import json

router = APIRouter(prefix="/celery-worker", tags=["celery_worker"])

@router.post("/heavy-lift", status_code=202) # Staus code 202 Accepted
def submit_heavy_lift_job(params: dict, db: Session = Depends(get_db)):
    job = HeavyLiftJob(params=json.dumps(params), status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)
    celery_app.send_task(
        "heavy_lift.run_analysis",
        kwargs={"job_id": job.id, "params": params},
    )

    return {"job_id": job.id, "status": job.status}