from celery import shared_task
from app.database import SessionLocal
from app.models.heavy_lift_job import HeavyLiftJob
import time
import json

@shared_task(name="heavy_lift.run_analysis")
def run_analysis(job_id: int, params: dict):
    db = SessionLocal()

    job = db.query(HeavyLiftJob).get(job_id)
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
