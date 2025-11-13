import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError


def get_engine():
    # Use env var if set, otherwise default to your earlier connection string
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/appdb",
    )
    return create_engine(db_url)


def dump_database():
    engine = get_engine()
    inspector = inspect(engine)

    # Exclude Postgres system schemas
    exclude_schemas = {"pg_catalog", "information_schema", "pg_toast"}

    try:
        with engine.connect() as conn:
            schemas = inspector.get_schema_names()

            for schema in schemas:
                # Skip system/internal schemas
                if schema in exclude_schemas or schema.startswith("pg_"):
                    continue

                print(f"\n==================== SCHEMA: {schema} ====================")

                tables = inspector.get_table_names(schema=schema)
                if not tables:
                    print("  (no tables)")
                    continue

                for table in tables:
                    print(f"\n--- TABLE: {schema}.{table} ---")

                    # Columns
                    columns = inspector.get_columns(table_name=table, schema=schema)
                    col_names = [col["name"] for col in columns]
                    print("Columns:", ", ".join(col_names))

                    # Fetch all rows (safe if you only have small tables)
                    query = text(f'SELECT * FROM "{schema}"."{table}"')
                    result = conn.execute(query)
                    rows = result.fetchall()

                    if not rows:
                        print("  (no rows)")
                        continue

                    # Print each row as dict-like output
                    for row in rows:
                        row_dict = {col: row[i] for i, col in enumerate(col_names)}
                        print(row_dict)

    except SQLAlchemyError as e:
        print("Error while dumping database:", e)


if __name__ == "__main__":
    dump_database()