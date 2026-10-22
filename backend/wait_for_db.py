import os
import time

import psycopg

database_url = os.environ["DATABASE_URL"]

# Convert SQLAlchemy's URL into a psycopg-compatible URI.
if database_url.startswith("postgresql+psycopg://"):
    database_url = database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )

for attempt in range(30):
    try:
        with psycopg.connect(database_url, connect_timeout=3):
            print("PostgreSQL is ready!")
            break
    except psycopg.OperationalError as exc:
        if attempt == 29:
            raise RuntimeError(
                "PostgreSQL did not become ready after 30 attempts"
            ) from exc

        print(f"Waiting for PostgreSQL ({attempt + 1}/30)...")
        time.sleep(2)