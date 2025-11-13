from celery import shared_task
from app.database import SessionLocal
from app.models.celery_job import CeleryJob
import time
import json

@shared_task(name="complicated_analysis.run_analysis")
def run_analysis(job_id: int, params: dict):
    db = SessionLocal()

    job = db.query(CeleryJob).get(job_id)
    if not job:
        return

    job.status = "RUNNING"
    db.commit()

    try:
        # Heavy analysis placeholder
        time.sleep(10)

        result = {"ok": True, "details": params}

        job.status = "SUCCEEDED"
        job.result = json.dumps(result)

    except Exception as e:
        job.status = "FAILED"
        job.error = str(e)

    finally:
        db.commit()
        db.close()

    return True
