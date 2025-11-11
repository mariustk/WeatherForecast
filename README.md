# Weather Forecast Service

A FastAPI-based service for delivering weather forecasts and scheduling offshore tasks. The API exposes endpoints for retrieving weather windows and managing task statuses while sourcing data from a PostgreSQL database and a JSON-based weather feed.

## 📚 Documentation

* Interactive OpenAPI documentation is available once the app is running at **http://localhost:8006/docs**.

## 🏗️ Architecture Overview

```
WeatherForecast/
├── app/
│   ├── main.py              # FastAPI application entry point & weather endpoints
│   ├── database.py          # SQLAlchemy engine and session dependency
│   ├── lib.py               # Wave analysis helpers used by the schedule router
│   ├── models/              # SQLAlchemy ORM models (e.g., Task)
│   ├── routers/
│   │   └── schedule.py      # Task scheduling endpoints, integrates weather feed
│   ├── mock_forecast.json   # Demo weather data consumed by /weather endpoints
│   └── weather_forecast.json  # Optional alternate forecast payload
├── demo_tools/
│   ├── generate_weather_forecast_mock.py # Utility to regenerate mock forecast JSON
│   ├── init_mock_schedule_db.py          # Seeds the demo PostgreSQL database
│   └── reqs.py                           # Minimal example of hitting schedule endpoints
└── docker-compose.yml       # Postgres service used by the API
```

Key data flows:

1. **Incoming Requests → `app/main.py`** – FastAPI handles `/weather` and `/weather_next_12_hours` using the mock JSON forecast.
2. **Scheduling API → `app/routers/schedule.py`** – Combines database tasks with weather data fetched from the running FastAPI service and produces go/no-go analyses through `app/lib.py`.
3. **Database Layer → `app/database.py` & `app/models/`** – SQLAlchemy models and session factories used in request handlers.
4. **Demo Utilities → `demo_tools/`** – Scripts to populate mock weather data and seed PostgreSQL for local experimentation.

## 🚀 Getting Started

### 1. Install Dependencies

Create a virtual environment and install core dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn "sqlalchemy>=2" psycopg2-binary httpx requests
```

### 2. Launch PostgreSQL with Docker Compose

```bash
docker compose up -d db
```

The compose file provisions a PostgreSQL 16 container listening on `localhost:5432` with the credentials `postgres/postgres` and database `appdb`.

### 3. Seed Demo Data

With PostgreSQL running:

```bash
python -m demo_tools.init_mock_schedule_db
```

This script drops & recreates the schema defined in `app.models.schedule` and inserts a handful of sample tasks.

To (re)generate the JSON weather feed consumed by the `/weather` endpoints:

```bash
python -m demo_tools.generate_weather_forecast_mock
```

The command writes a fresh 24-hour forecast into `app/mock_forecast.json`.

### 4. Run the FastAPI Application

Start the API locally on port `8006` (matching the internal schedule client configuration):

```bash
uvicorn app.main:app --reload --port 8006
```

The server now exposes:

* `GET /weather` – Filtered forecast between two Unix timestamps for a `lat,lon` location.
* `GET /weather_next_12_hours` – Convenience endpoint for the upcoming 12 hours.
* `GET /schedule/window` – Combines database tasks with forecast data to compute go/no-go windows.
* `GET /schedule/all_tasks`, `PUT /schedule/task/{id}/complete`, `PUT /schedule/task/{id}/started` – Simple task management operations.

### 5. Try the Demo Endpoints

* Visit **http://localhost:8006/docs** to explore and call endpoints via Swagger UI.
* Use the helper script to trigger an example request:

  ```bash
  python -m demo_tools.reqs
  ```

  (Ensure the API server is running on port 8006 and adjust the URL inside `demo_tools/reqs.py` if necessary.)

### 6. Shut Down

When finished, stop the database container:

```bash
docker compose down
```

## 🧪 Development Tips

* Update `app/mock_forecast.json` whenever you want new weather scenarios without touching the code.
* Modify `demo_tools/init_mock_schedule_db.py` to tailor the seeded tasks for testing different scheduling outcomes.
* If you change the API port, update the base URL used in `app/routers/schedule.py` and any demo scripts referencing the service.

Happy forecasting! 🌤️
