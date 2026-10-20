import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

load_dotenv()

db = SQLAlchemy()


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
        }


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "sqlite:///taskflow.db",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    @app.get("/api/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="ok", database="connected"), 200
        except Exception:
            db.session.rollback()
            return jsonify(status="error", database="unavailable"), 503

    @app.get("/api/tasks")
    def list_tasks():
        tasks = db.session.execute(
            db.select(Task).order_by(Task.id)
        ).scalars().all()
        return jsonify([task.to_dict() for task in tasks])

    @app.post("/api/tasks")
    def create_task():
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify(error="A JSON object is required"), 400

        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            return jsonify(error="Title is required"), 400

        title = title.strip()
        if len(title) > 200:
            return jsonify(error="Title must be 200 characters or fewer"), 400

        task = Task(title=title)
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201

    @app.patch("/api/tasks/<int:task_id>")
    def update_task(task_id):
        task = db.session.get(Task, task_id)
        if task is None:
            return jsonify(error="Task not found"), 404

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="A JSON object is required"), 400

        if "completed" in data:
            if not isinstance(data["completed"], bool):
                return jsonify(error="completed must be a boolean"), 400
            task.completed = data["completed"]

        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip():
                return jsonify(error="Title cannot be empty"), 400
            if len(title.strip()) > 200:
                return jsonify(error="Title must be 200 characters or fewer"), 400
            task.title = title.strip()

        db.session.commit()
        return jsonify(task.to_dict())

    @app.delete("/api/tasks/<int:task_id>")
    def delete_task(task_id):
        task = db.session.get(Task, task_id)
        if task is None:
            return jsonify(error="Task not found"), 404

        db.session.delete(task)
        db.session.commit()
        return "", 204

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="127.0.0.1", port=5000, debug=True)
