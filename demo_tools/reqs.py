import requests
r = requests.put(
    "http://127.0.0.1:8005/schedule/task/6/started")
print(r.status_code, r.json())

