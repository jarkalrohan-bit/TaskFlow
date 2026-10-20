import pytest

from app import create_app, db


@pytest.fixture()
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
    })

    with app.app_context():
        db.create_all()

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.drop_all()


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["database"] == "connected"


def test_create_and_list_task(client):
    response = client.post(
        "/api/tasks",
        json={"title": "Learn Kubernetes"},
    )
    assert response.status_code == 201
    assert response.json["title"] == "Learn Kubernetes"
    assert response.json["completed"] is False

    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert len(response.json) == 1


def test_reject_empty_title(client):
    response = client.post("/api/tasks", json={"title": "  "})
    assert response.status_code == 400


def test_update_and_delete_task(client):
    created = client.post(
        "/api/tasks",
        json={"title": "Practice CI/CD"},
    )
    task_id = created.json["id"]

    updated = client.patch(
        f"/api/tasks/{task_id}",
        json={"completed": True},
    )
    assert updated.status_code == 200
    assert updated.json["completed"] is True

    deleted = client.delete(f"/api/tasks/{task_id}")
    assert deleted.status_code == 204

    missing = client.get("/api/tasks")
    assert missing.json == []
