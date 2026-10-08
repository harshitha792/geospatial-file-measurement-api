from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_root():
    r=client.get("/")
    assert r.status_code==200
    assert r.json()["status"]=="running"

def test_missing_file():
    assert client.get("/api/files/not-found/").status_code==404
