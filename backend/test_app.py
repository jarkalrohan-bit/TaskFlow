import sys
import os

# Ensure app.py can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
from app import create_app, db
from app import create_app


# ==========================================
# Helper Function (This was missing!)
# ==========================================
def get_test_app():
    app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })
    
    # Create the tables inside the app context
    with app.app_context():
        db.create_all()
        
    return app


# ==========================================
# Original Tests
# ==========================================
def test_app_creates():
    app = get_test_app()
    assert app is not None


def test_health_endpoint():
    app = get_test_app()
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200


def test_list_tasks_empty():
    app = get_test_app()
    client = app.test_client()
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_task():
    app = get_test_app()
    client = app.test_client()
    response = client.post("/api/tasks", json={"title": "Test task"})
    assert response.status_code == 201
    assert response.get_json()["title"] == "Test task"


def test_create_task_missing_title():
    app = get_test_app()
    client = app.test_client()
    response = client.post("/api/tasks", json={})
    assert response.status_code == 400


# ==========================================
# NEW Tests (To fix your Coverage Gate)
# ==========================================
def test_create_task_invalid_json():
    app = get_test_app()
    client = app.test_client()
    response = client.post("/api/tasks", data="not a json", content_type="text/plain")
    assert response.status_code == 400
    assert response.get_json()["error"] == "A JSON object is required"


def test_create_task_title_too_long():
    app = get_test_app()
    client = app.test_client()
    response = client.post("/api/tasks", json={"title": "A" * 201})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Title must be 200 characters or fewer"


def test_update_task_invalid_completed():
    app = get_test_app()
    client = app.test_client()
    
    # First create a task so we have an ID to update
    res = client.post("/api/tasks", json={"title": "Task 1"})
    task_id = res.get_json()["id"]
    
    # Test invalid boolean payload
    response = client.patch(f"/api/tasks/{task_id}", json={"completed": "yes"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "completed must be a boolean"