# TaskFlow — Containerized Task Management Application

TaskFlow is a full-stack task management application built to demonstrate
containerization, service communication, database persistence, testing,
and practical DevOps deployment workflows.

## Features

- Create, list, complete, and delete tasks.
- React frontend served by Nginx.
- Flask REST API using SQLAlchemy.
- PostgreSQL relational database.
- Docker Compose orchestration.
- Container health checks and startup dependencies.
- Persistent PostgreSQL storage using a named Docker volume.
- Automated backend tests with pytest.

## Architecture

```text
Browser
   |
   | http://localhost:8081
   v
React application served by Nginx
   |
   | /api/* reverse proxy
   v
Flask API + Gunicorn
   |
   | PostgreSQL connection
   v
PostgreSQL 16
   |
   v
Docker named volume: taskflow_pgdata
```

The browser communicates with Nginx. Nginx forwards `/api/` requests to
the backend using the internal Docker Compose network. PostgreSQL is not
published on a host port by the Compose configuration.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite |
| Web server / reverse proxy | Nginx |
| Backend | Python, Flask, SQLAlchemy |
| Application server | Gunicorn |
| Database | PostgreSQL 16 |
| Containers | Docker |
| Orchestration | Docker Compose |
| Backend tests | pytest |

## Prerequisites

Install:

- Docker Engine or Docker Desktop with Linux containers enabled.
- Docker Compose v2 (`docker compose`).
- Git.

Node.js and Python are needed for local development, but not to run the
complete application through Docker Compose.

## Repository structure

```text
taskflow/
├── backend/
│   ├── app.py
│   ├── init_db.py
│   ├── test_app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   ├── Dockerfile
│   ├── nginx.conf
│   └── .dockerignore
├── database/
│   └── README.md
├── docker-compose.yaml
├── .gitignore
└── README.md
```

## Run with Docker Compose

Clone the repository and enter its directory:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd taskflow
```

Build and start all services:

```bash
docker compose -f docker-compose.yaml up --build -d
```

Check service status:

```bash
docker compose -f docker-compose.yaml ps
```

Expected services:

- `frontend`: serves the application on host port 8081.
- `backend`: provides the Flask API on the internal Compose network.
- `db`: runs PostgreSQL 16 on the internal Compose network.

Open the application:

http://localhost:8081

Port 8081 is used to avoid conflicts with services such as Jenkins that
may already occupy port 8080.

## Verify the deployment

Check backend health through the frontend reverse proxy:

```bash
curl -i http://localhost:8081/api/health
```

Expected HTTP status: `200 OK`.

Expected response:

```json
{
  "status": "ok",
  "database": "connected"
}
```

List tasks:

```bash
curl -i http://localhost:8081/api/tasks
```

Create a task:

```bash
curl -i -X POST http://localhost:8081/api/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Learn Docker Compose"}'
```

Complete a task by replacing `<TASK_ID>` with the returned ID:

```bash
curl -i -X PATCH http://localhost:8081/api/tasks/<TASK_ID> \
  -H 'Content-Type: application/json' \
  -d '{"completed":true}'
```

Delete a task:

```bash
curl -i -X DELETE http://localhost:8081/api/tasks/<TASK_ID>
```

A successful delete returns HTTP `204 No Content`.

## Database and persistence

PostgreSQL stores its live database files in the named Docker volume
`taskflow_pgdata`, mounted at `/var/lib/postgresql/data` inside the
database container.

The `database/` directory contains database documentation and scripts;
it is not the live database storage directory.

Inspect database readiness:

```bash
docker compose -f docker-compose.yaml exec db \
  pg_isready -U taskflow -d taskflow
```

List database tables:

```bash
docker compose -f docker-compose.yaml exec db \
  psql -U taskflow -d taskflow -c '\dt'
```

Inspect the task records:

```bash
docker compose -f docker-compose.yaml exec db \
  psql -U taskflow -d taskflow \
  -c 'SELECT id, title, completed FROM task ORDER BY id;'
```

### Restart services

```bash
docker compose -f docker-compose.yaml restart
```

### Stop services without deleting database data

```bash
docker compose -f docker-compose.yaml down
```

The named database volume is retained.

**Warning:** `docker compose down -v` removes Compose-managed named
volumes. Do not use it when you need to preserve your database.

### Back up the database

Create a logical backup outside the repository:

```bash
mkdir -p "$HOME/taskflow-backups"

docker compose -f docker-compose.yaml exec -T db \
  pg_dump -U taskflow -d taskflow \
  > "$HOME/taskflow-backups/taskflow-$(date +%F-%H%M%S).sql"
```

Check that the backup file is nonempty:

```bash
ls -lh "$HOME"/taskflow-backups/
```

Test backup and restore procedures before relying on backups for recovery.

## Logs and troubleshooting

View logs for all services:

```bash
docker compose -f docker-compose.yaml logs --tail=100
```

Follow backend logs:

```bash
docker compose -f docker-compose.yaml logs -f backend
```

Check the database health:

```bash
docker compose -f docker-compose.yaml exec db \
  pg_isready -U taskflow -d taskflow
```

Rebuild after changing application code or Dockerfiles:

```bash
docker compose -f docker-compose.yaml up --build -d
```

If port 8081 is already in use, change the frontend port mapping in
`docker-compose.yaml` and use the new port in your browser and curl tests.

If the API reports a database connection failure, inspect backend and
database logs before changing credentials or deleting volumes.

## Local development

### Backend

From the `backend/` directory, create and activate a Python virtual
environment using the appropriate commands for your operating system.
Install the packages from `requirements.txt` and run the Flask application.

The local backend defaults to SQLite if `DATABASE_URL` is not set.
Configure `DATABASE_URL` when you want local development to use PostgreSQL.

### Frontend

From the `frontend/` directory:

```bash
npm ci
npm run dev
```

The frontend `.env` can configure `VITE_API_URL` for local development.
For the containerized deployment, the empty Vite API URL uses relative
`/api/` requests, which Nginx forwards to the backend.

## Testing

Run backend tests locally after installing the backend requirements:

```bash
cd backend
python -m pytest -v
```

Run the application through Compose and verify health and CRUD operations
using the commands in the deployment section.

## Security notes

- The password in the Compose configuration is for local development only.
- Do not commit real credentials, private keys, local `.env` files, or
  database backups.
- Use managed secrets or environment-specific configuration for deployed
  environments.
- PostgreSQL is not published on a host port by this Compose configuration.
- Flask's debug development server is not used by the containerized
  backend; Gunicorn serves the application.

## Current scope and roadmap

Current scope:

- Full-stack task CRUD operations.
- Containerized frontend, backend, and database.
- Compose health checks and persistent storage.
- Basic backend automated tests.

Planned improvements:

- CI/CD with GitHub Actions.
- Container image scanning with Trivy.
- Image publishing to GitHub Container Registry.
- Database schema migrations with Alembic.
- Kubernetes deployment manifests.
- AWS EKS deployment, monitoring, and operational documentation.

## License

Choose and add an appropriate open-source license before publishing this
project for reuse.
