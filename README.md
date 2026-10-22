# TaskFlow — Containerized Task Management Application

TaskFlow is a full-stack task management application built to demonstrate containerization, REST API development, database persistence, automated testing, and Kubernetes deployment workflows.

The application supports task creation, listing, completion, and deletion. It runs locally using Docker Compose and can also be deployed to a local Kubernetes cluster using kind.

## 📋 Table of Contents
1. [Features](#-features)
2. [Architecture](#-architecture)
3. [Technology Stack](#-technology-stack)
4. [Repository Structure](#-repository-structure)
5. [Prerequisites](#-prerequisites)
6. [Run with Docker Compose](#-run-with-docker-compose)
7. [Deploy to Kubernetes with kind](#-deploy-to-kubernetes-with-kind)
8. [Verify the Application](#-verify-the-application)
9. [Database Persistence and Backups](#-database-persistence-and-backups)
10. [Testing](#-testing)
11. [Troubleshooting](#-troubleshooting)
12. [Security](#-security)
13. [Roadmap](#-roadmap)
14. [License](#-license)

---

## ✨ Features

* **Task Operations:** Create, list, complete, and delete tasks seamlessly.
* **Modern Frontend:** React frontend built with Vite and served by Nginx.
* **Robust Backend:** Flask REST API using SQLAlchemy ORM and running on Gunicorn.
* **Relational Database:** PostgreSQL 16 relational database engine.
* **Orchestration:** Local setup via Docker Compose and native Kubernetes deployment via `kind`.
* **Resiliency:** Persistent PostgreSQL storage, health checks, and explicit resource configurations.
* **Reverse Proxy:** Nginx reverse proxy configurations handling all API incoming requests.
* **Automated Quality:** Backend automated test coverage built with `pytest`.
* **Declarative Deployments:** Structured Kubernetes manifests customized via Kustomize.

---

## 🏗️ Architecture

### Docker Compose Diagram
```text
Browser
   │
   │ http://localhost:8081
   ▼
React Frontend served by Nginx
   │
   │ /api/* reverse proxy
   ▼
Flask REST API + Gunicorn
   │
   │ SQLAlchemy / PostgreSQL driver
   ▼
PostgreSQL 16
   │
   ▼
Docker named volume: taskflow_pgdata
```
The browser accesses the frontend through Nginx. Nginx forwards `/api/` requests to the backend over the internal Docker Compose network. PostgreSQL is isolated and not published on a host port by default.

### Kubernetes with kind Diagram
```text
Browser
   │
   │ http://localhost:8082 (via kubectl port-forward)
   ▼
Frontend Service
   │
   ▼
Frontend Pod: React + Nginx
   │
   │ /api/* reverse proxy
   ▼
Backend Service
   │
   ▼
Backend Pod: Flask + Gunicorn
   │
   ▼
PostgreSQL Service
   │
   ▼
PostgreSQL StatefulSet
   │
   ▼
PersistentVolumeClaim
```
The Kubernetes resources are deployed in the isolated `taskflow` namespace. The frontend and backend communicate through Kubernetes Services. PostgreSQL runs as a StatefulSet with persistent storage. 

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React, Vite |
| **Web server and reverse proxy** | Nginx |
| **Backend** | Python, Flask |
| **Application server** | Gunicorn |
| **ORM** | SQLAlchemy |
| **Database** | PostgreSQL 16 |
| **Backend testing** | pytest |
| **Containers** | Docker |
| **Local orchestration** | Docker Compose |
| **Kubernetes** | Kubernetes with kind |
| **Kubernetes configuration** | YAML manifests and Kustomize |
| **CI/CD (Planned)** | GitHub Actions |
| **Container registry (Planned)** | GitHub Container Registry |
| **GitOps (Planned)** | Argo CD |

---

## 📁 Repository Structure

```text
taskflow/
├── backend/
│   ├── app.py
│   ├── init_db.py
│   ├── test_app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── wait_for_db.py
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   ├── Dockerfile
│   └── nginx.conf
├── database/
│   └── README.md
├── k8s/
│   ├── backend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── database/
│   │   ├── secret.yaml
│   │   ├── service.yaml
│   │   └── statefulset.yaml
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── kind-config.yaml
│   ├── kustomization.yaml
│   └── namespace.yaml
├── docker-compose.yml
├── .gitignore
└── README.md
```

> ⚠️ **Important:** `Notes.md` is intentionally omitted because it contains personal notes. Keep it out of the public repository to avoid leakages.
> 
> 🔒 **Notice:** The `k8s/database/secret.yaml` entry represents a local development configuration file. Do not commit it if it contains valid plain text or base64 credentials.

---

## 🛑 Prerequisites

### For Docker Compose
* Docker Engine or Docker Desktop with Linux containers enabled.
* Docker Compose v2.
* Git.

### For Kubernetes with kind
* Docker Engine or Docker Desktop.
* kind CLI installed.
* kubectl CLI installed.
* Cloned TaskFlow source code.

> **Note:** Node.js and Python are required for local bare-metal development and testing, but they are **not** required on the host computer to run the application using its container images.

---

## 🐳 Run with Docker Compose

Run the following commands from the project root directory.

### 1. Build and start the application
```bash
docker compose -f docker-compose.yml up --build -d
```
*(If your file is named `docker-compose.yaml`, substitute that filename instead).*

### 2. Check service status
```bash
docker compose -f docker-compose.yml ps
```
**Expected services:**
* `frontend`: Serves the web application on host port `8081`. (Port `8081` avoids conflicts with services using `8080`).
* `backend`: Provides the Flask REST API on the internal Compose network.
* `db`: Runs the PostgreSQL 16 container.

### 3. Open the application
Visit your browser at: [http://localhost:8081](http://localhost:8081)

### 4. Stop the application
```bash
docker compose -f docker-compose.yml down
```
> ❗ **Warning:** Avoid appending `-v` (`docker compose down -v`) when you need to preserve your database data. The `-v` option permanently deletes Compose-managed named volumes.

---

## ☸️ Deploy to Kubernetes with kind

Run these commands from the project root directory.

### 1. Create the kind cluster
If the cluster does not already exist:
```bash
kind create cluster --name taskflow --config k8s/kind-config.yaml
```
Verify cluster context:
```bash
kubectl cluster-info --context kind-taskflow
kubectl get nodes
```

### 2. Build the application images
Ensure the tag names match your Kubernetes Deployment manifests:
```bash
docker build -t taskflow-backend:dev ./backend
docker build -t taskflow-frontend:dev ./frontend
```

### 3. Load images into kind
Locally built images must be loaded into the `kind` cluster environment to pull successfully without a remote registry:
```bash
kind load docker-image taskflow-backend:dev --name taskflow
kind load docker-image taskflow-frontend:dev --name taskflow
```

### 4. Configure database credentials
The database credentials must match the configuration expected by the PostgreSQL StatefulSet and backend Deployment. Create or update `k8s/database/secret.yaml` locally before running deployment pipelines.

Verify file existence:
```bash
ls -l k8s/database/secret.yaml
```
*Note: Excluding the local file from Git does not automatically create the Secret in the cluster. It must exist inside Kubernetes before dependent workloads start.*

### 5. Validate and deploy the manifests
Render configuration changes:
```bash
kubectl kustomize k8s
```
Dry-run manifest validation against the live cluster API:
```bash
kubectl apply --dry-run=server -k k8s
```
Deploy the configurations:
```bash
kubectl apply -k k8s
```

### 6. Check deployment status
```bash
kubectl get pods -n taskflow
kubectl get services -n taskflow
kubectl get pvc -n taskflow
```
Monitor rollout health:
```bash
kubectl rollout status deployment -n taskflow
```

---

## 🔍 Verify the Application

### Accessing the Frontend
Forward the host machine interface port to the internal Kubernetes frontend service:
```bash
kubectl port-forward -n taskflow service/taskflow-frontend 8082:80
```
* Keep this terminal open while using the application.
* Visit the UI at: [http://localhost:8082](http://localhost:8082)

*(If your service name differs, identify it using `kubectl get services -n taskflow`)*

### Verifying the Backend API Directly
In a secondary terminal workspace, forward port `5000`:
```bash
kubectl port-forward -n taskflow service/taskflow-backend 5000:5000
```
Test backend routing availability using `curl`:
```bash
curl -i http://localhost:5000/api/health
curl -i http://localhost:5000/api/tasks
```

---

## 💾 Database Persistence and Backups
### Docker Compose

PostgreSQL stores its data in the named Docker volume taskflow_pgdata, mounted inside the database container.

Check database readiness:
```bash
docker compose -f docker-compose.yml exec db \
  pg_isready -U taskflow -d taskflow
```

List database tables:
```bash
docker compose -f docker-compose.yml exec db \
  psql -U taskflow -d taskflow -c '\dt'
```

Inspect task records:
```bash
docker compose -f docker-compose.yml exec db \
  psql -U taskflow -d taskflow \
  -c 'SELECT id, title, completed FROM task ORDER BY id;'
```

These commands assume the database service, database, and role are named db, taskflow, and taskflow, respectively. Adjust them if your configuration differs.

## Kubernetes

Inspect PostgreSQL and its storage:
```bash
kubectl get statefulset,pods,pvc -n taskflow
kubectl logs -n taskflow statefulset/taskflow-db
```

The StatefulSet and PersistentVolumeClaim configuration determine how database storage is attached and retained. Deleting a Pod is not the same as deleting its persistent storage.

## Back up the Docker Compose database

Create a backup directory outside the repository:
```bash
mkdir -p "$HOME/taskflow-backups"
```

Create a logical backup:
```bash
docker compose -f docker-compose.yml exec -T db \
  pg_dump -U taskflow -d taskflow \
  > "$HOME/taskflow-backups/taskflow-$(date +%F-%H%M%S).sql"
```

Check the resulting file:
```bash
ls -lh "$HOME"/taskflow-backups/
```

Test backup and restore procedures before relying on them for recovery. Protect backup files because they may contain application data.

## 🧪 Testing
Backend tests

From the project root:
```bash
cd backend
python -m pytest -v
```

Install the backend dependencies from requirements.txt in an appropriate Python virtual environment before running the tests.

Container and Kubernetes verification

For Docker Compose:
```bash
docker compose -f docker-compose.yml ps
docker compose -f docker-compose.yml logs --tail=100
```

For Kubernetes:
```bash
kubectl get pods -n taskflow
kubectl get services -n taskflow
kubectl get pvc -n taskflow
kubectl kustomize k8s
kubectl apply --dry-run=server -k k8s
```

A successful dry run validates the manifests against the current cluster API, but does not prove that every application component will start successfully.

## 🔧 Troubleshooting
Inspect Kubernetes Pods
```bash
kubectl get pods -n taskflow
kubectl describe pod -n taskflow <POD_NAME>
```

Replace <POD_NAME> with the actual Pod name.

Inspect backend logs
```bash
kubectl logs -n taskflow deployment/taskflow-backend
```
Inspect PostgreSQL logs
```bash
kubectl logs -n taskflow statefulset/taskflow-db
```

Adjust resource names if your manifests use different names.

Check Services and endpoints
```bash
kubectl get services -n taskflow
kubectl get endpoints -n taskflow
```

If the API is unreachable, verify Service ports, target ports, Pod labels, readiness, and Nginx proxy configuration.

Rebuild and reload changed images

After changing application code or Dockerfiles:

```bash
docker build -t taskflow-backend:dev ./backend
docker build -t taskflow-frontend:dev ./frontend

kind load docker-image taskflow-backend:dev --name taskflow
kind load docker-image taskflow-frontend:dev --name taskflow
```

Ensure Deployment image tags and image pull policies match your local kind workflow. If a running Pod does not pick up a changed image with the same tag, trigger an appropriate rollout or use a distinct image tag.

## Port-forwarding issues

If a local port is already occupied, use another local port:

```bash
kubectl port-forward -n taskflow service/taskflow-frontend 8083:80
```

Then open http://localhost:8083

## 🔐 Security
- Never commit passwords, tokens, private keys, production credentials, or sensitive .env files.
- Keep local Kubernetes Secret files out of Git.
- Kubernetes Secret base64 encoding is not encryption.
- Review Git history for credentials before publishing the repository.
- Rotate any credential that has been exposed or committed.
- Use a suitable secret-management system and least-privilege access controls for production.
- Avoid unnecessarily exposing PostgreSQL outside the cluster or Compose network.
- Never use development credentials in production.
- Keep container base images and application dependencies updated.
- Consider container image scanning, vulnerability management, and automated testing in CI.
- kind is a local development and learning environment, not a production hosting platform.
## 📍 Roadmap
## Completed baseline
- Build and run the frontend, backend, and PostgreSQL containers.
- Orchestrate the application using Docker Compose.
- Implement task CRUD endpoints and backend tests.
- Deploy frontend and backend workloads to kind.
- Configure PostgreSQL using a StatefulSet and persistent storage.
- Configure Kubernetes Services and application health checks.
- Verify backend health and task retrieval.
- Validate Kubernetes manifests using Kustomize and server-side dry run.
## Planned improvements
- Finalize repository documentation and secret exclusions.
- Review Git history and safely publish the Kubernetes baseline.
- Add GitHub Actions for automated tests and frontend/backend image builds.
- Publish versioned images to GitHub Container Registry (GHCR).
- Automate deployment updates using a controlled image-tagging strategy.
- Introduce Argo CD for GitOps-based deployment.
- Add database migrations with Alembic.
- Improve observability, container scanning, and deployment security.
- Explore deployment to AWS EKS.


## 📝 License

No license has been specified yet. Add an appropriate open-source license before granting others permission to reuse, modify, or distribute the project.