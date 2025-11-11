import json
import random
from datetime import datetime, timedelta, timezone

# --- Settings ---
lat, lon = 61.5, 4.8
start_time = datetime.now(tz=timezone.utc)
end_time = start_time + timedelta(hours=24)
step = timedelta(minutes=30)

# --- Generate forecast data ---
forecast = []
t = start_time
while t <= end_time:
    wind_speed = round(random.uniform(8.0, 22.0), 1)
    wave_height = round(random.uniform(0.5, 3.0), 1)
    wave_period = round(random.uniform(6.5, 9.5), 1)

    forecast.append({
        "timestamp": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "wind_speed": wind_speed,
        "wave_height": wave_height,
        "wave_period": wave_period
    })
    t += step

# --- Combine into final structure ---
mock_data = {
    "location": {"lat": lat, "lon": lon},
    "forecast": forecast
}

# --- Print or save ---
print(json.dumps(mock_data, indent=2))
# or write to file:
with open("mock_forecast.json", "w") as f:
    json.dump(mock_data, f, indent=2)