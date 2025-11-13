# init_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.models.schedule import Task
from app.models.heavy_lift_job import HeavyLiftJob


# matches your docker-compose settings
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/appdb"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# DEMO: wipe and recreate
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# Seed data
tasks = [
    Task(id=1, name="task 1", duration="4h", predecessor=None, status="COMPLETED", wave_height_limit=2.0),
    Task(id=2, name="task 2", duration="4h", predecessor=1, status="COMPLETED", wave_height_limit=2.0),
    Task(id=3, name="task 3", duration="2h", predecessor=2, status="READY",     wave_height_limit=2.0),
    Task(id=4, name="task 4", duration="3h", predecessor=3, status="BLOCKED",   wave_height_limit=1.5),
    Task(id=5, name="task 5", duration="4h", predecessor=4, status="BLOCKED",   wave_height_limit=2.5),
]

session.add_all(tasks)
session.commit()
session.close()



