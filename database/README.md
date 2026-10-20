# TaskFlow Database

TaskFlow uses PostgreSQL 16 as its relational database.

## Architecture

- Database engine: PostgreSQL
- Database name: taskflow
- Database user: taskflow
- Compose service: db
- Persistent Docker volume: taskflow_pgdata
- Container data directory: /var/lib/postgresql/data

The database runs in a container. Its live data is stored in a Docker
named volume rather than in this source directory.

## Schema

The Flask application defines the Task model in backend/app.py.

| Column | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| title | String(200) | Required task title |
| completed | Boolean | Whether the task is complete |

## Check database health

From the project root:

    docker compose -f docker-compose.yaml exec db \
      pg_isready -U taskflow -d taskflow

## Connect to PostgreSQL

    docker compose -f docker-compose.yaml exec db \
      psql -U taskflow -d taskflow

List tables inside psql:

    \dt

Exit psql:

    \q

## Persistence

The named volume taskflow_pgdata preserves database files when
containers are stopped or recreated.

Do not run `docker compose down -v` unless you intentionally want
to remove the Compose project's named volumes.

## Backup

Create a logical database backup:

    docker compose -f docker-compose.yaml exec -T db \
      pg_dump -U taskflow -d taskflow > taskflow-backup.sql

Keep backups outside Git and store them securely.

## Restore

Restore into an existing, compatible database:

    cat taskflow-backup.sql | docker compose \
      -f docker-compose.yaml exec -T db \
      psql -U taskflow -d taskflow

Test backup and restore procedures before relying on them.

## Security

The credentials used for local development are not suitable for
production. Use environment variables or a secret manager for
deployment credentials, and never commit real secrets or backups.
