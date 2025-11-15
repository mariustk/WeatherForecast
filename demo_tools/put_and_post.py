import requests
import json
r = requests.put(
    "http://127.0.0.1:8020/schedule/task/5/started")
print(r.status_code, r.json())

payload = {'HS':2,'TP':9,"SimLength":200}
r = requests.post(
    "http://127.0.0.1:8020/celery-worker/submit_complicated_job",
    json=payload)
print(r.status_code, r)