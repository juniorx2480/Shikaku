import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from sqlmodel import create_engine, SQLModel, Session
from fastapi.testclient import TestClient


def setup_test_app(monkeypatch):
    # create in-memory SQLite and override get_session before importing app.main
    import importlib
    database = importlib.import_module("app.database")

    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    def get_session_override():
        with Session(engine) as session:
            yield session

    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "get_session", get_session_override)

    main = importlib.import_module("app.main")

    # After models are imported by app.main, create tables on test engine
    SQLModel.metadata.create_all(engine)

    return main.app


def test_register_login_and_crud(monkeypatch):
    app = setup_test_app(monkeypatch)
    client = TestClient(app)

    # register
    r = client.post("/auth/register", json={"username": "user1", "password": "pass"})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "user1"

    # login (OAuth2 form)
    r = client.post("/auth/token", data={"username": "user1", "password": "pass"})
    assert r.status_code == 200
    token = r.json().get("access_token")
    assert token
    headers = {"Authorization": f"Bearer {token}"}

    # create algorithm
    r = client.post("/algorithms", json={"title": "Alg1", "description": "desc"}, headers=headers)
    assert r.status_code == 200
    alg = r.json()
    assert alg["title"] == "Alg1"
    alg_id = alg["id"]

    # get list
    r = client.get("/algorithms")
    assert r.status_code == 200
    assert len(r.json()) == 1

    # read
    r = client.get(f"/algorithms/{alg_id}")
    assert r.status_code == 200
    assert r.json()["id"] == alg_id

    # update
    r = client.put(f"/algorithms/{alg_id}", json={"title": "Alg1 updated"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["title"] == "Alg1 updated"

    # delete
    r = client.delete(f"/algorithms/{alg_id}", headers=headers)
    assert r.status_code == 200

    # users list (requires auth)
    r = client.get("/users", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
