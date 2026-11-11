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
    # First create a task
    res = client.post("/api/tasks", json={"title": "Task 1"})
    task_id = res.get_json()["id"]
    
    # Test invalid boolean
    response = client.patch(f"/api/tasks/{task_id}", json={"completed": "yes"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "completed must be a boolean"