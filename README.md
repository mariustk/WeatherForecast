# Weather Forecast Service

This project delivers a FastAPI application for forecasting offshore weather, running schedule analyses, and delegating long-running computations to a Celery worker backed by Redis. PostgreSQL stores task metadata and job results, while a JSON payload provides a lightweight weather feed for demonstration purposes.

## Documentation

Interactive OpenAPI documentation is available once the API is running at **http://localhost:8020/docs**.

## Project structure

```
WeatherForecast/
├── app/
│   ├── main.py                  # FastAPI entrypoint and weather endpoints
│   ├── api/
│   │   ├── schedule.py          # Scheduling endpoints consuming the weather API
│   │   └── heavy_lift_job.py    # Celery-backed job submission endpoints
│   ├── celery_app.py            # Celery configuration
│   ├── celery_tasks/
│   │   └── heavy_lift.py        # Example background task
│   ├── database.py              # SQLAlchemy engine and session helpers
│   ├── init_mock_schedule_db.py # Demo database bootstrapper
│   ├── lib.py                   # Wave-height analysis helpers
│   ├── models/                  # ORM models for schedules and jobs
│   ├── mock_forecast.json       # Sample forecast consumed by the API
│   └── weather_forecast.json    # Optional alternate forecast payload
├── demo_tools/
│   ├── generate_weather_forecast_mock.py # Regenerates the demo forecast JSON
│   └── put_and_post.py                   # Example interactions with the API
├── docker-compose.yml           # Local stack: API, worker, PostgreSQL, Redis
└── requirements.txt             # Python dependencies
```

### How the pieces fit together

1. **Weather API (`app/main.py`)** filters the JSON forecast and exposes `/weather` and `/weather_next_12_hours`.
2. **Schedule router (`app/api/schedule.py`)** queries the database, fetches weather data from the local API, and evaluates workability windows through `app.lib` utilities (placeholder for external libraries).
3. **Celery workflow (`app/api/heavy_lift_job.py` + `app/celery_tasks/heavy_lift.py`)** records jobs in PostgreSQL and processes them asynchronously via Redis-backed workers.
4. **Database helpers (`app/database.py`, `app/models`)** centralize SQLAlchemy configuration and ORM definitions.
5. **Demo scripts (`demo_tools/`)** regenerate mock data and showcase basic client interactions.

## Getting started

### 1. Launch docker setup
This assumes docker is installed on host
```bash
docker compose up --build
```

### 2. Start infrastructure

Spin up PostgreSQL and Redis, either manually or with Docker Compose:

```bash
docker compose up -d db redis
```

Credentials default to `postgres/postgres` with database `appdb` (see `docker-compose.yml`).

### 3. Seed the demo schema

```bash
python -m app.init_mock_schedule_db
```

The script recreates the schedule and heavy-lift job tables and inserts sample tasks.

To refresh the mock forecast consumed by the weather endpoints, run:

```bash
python -m demo_tools.generate_weather_forecast_mock
```

### 4. Run the FastAPI app

Keep the service on port `8006` so the schedule router can reach the weather API without code changes:

```bash
uvicorn app.main:app --reload --port 8006
```

The server exposes the following endpoints:

* `GET /weather`
* `GET /weather_next_12_hours`
* `GET /schedule/window`
* `GET /schedule/tasks`
* `PUT /schedule/task/{id}/started`
* `PUT /schedule/task/{id}/complete`
* `POST /celery-worker/heavy-lift`
* `GET /celery-worker/tasks`

### 5. Run a Celery worker (optional but required for heavy-lift jobs)

```bash
celery -A app.celery_app:celery_app worker -l info
```

Ensure `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` point to your Redis instance. When using Docker Compose, these default to the bundled Redis service.

### 6. Try the demo

* Visit **http://localhost:8006/docs** for interactive API docs.
* Trigger sample requests with `python -m demo_tools.put_and_post`.

### 7. Shut everything down

```bash
docker compose down
```

## Environment variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `DATABASE_URL` | SQLAlchemy connection string | `postgresql+psycopg2://postgres:postgres@localhost:5432/appdb` |
| `CELERY_BROKER_URL` | Celery broker location | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://redis:6379/1` |

Override these as needed when deploying or running locally without Docker.

## Development tips

* Update `app/mock_forecast.json` to model different sea states without touching application code.
* Adjust `app/lib.py` to experiment with alternative go/no-go logic.
* If you change the API port, also update the hard-coded URL in `app/api/schedule.py`.

Enjoy building on the service.
