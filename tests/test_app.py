import io
import os
from fastapi.testclient import TestClient
from main import app, STORAGE_DIR

client = TestClient(app)


def setup_module(module):
    STORAGE_DIR.mkdir(exist_ok=True)


def teardown_module(module):
    for f in STORAGE_DIR.iterdir():
        if f.is_file():
            f.unlink()


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "File Storage API" in data["message"]
    assert any("/files" in e for e in data["endpoints"])


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "File Storage API"


def test_upload_file():
    test_filename = "testfile.txt"
    file_content = b"Hello, FastAPI!"
    files = {"file": (test_filename, io.BytesIO(file_content), "text/plain")}

    response = client.post("/files", files=files)
    assert response.status_code == 200

    data = response.json()
    assert data["filename"] == test_filename
    assert data["size"] == len(file_content)
    assert data["content_type"] == "text/plain"
    assert (STORAGE_DIR / test_filename).exists()


def test_list_files():
    response = client.get("/files")
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert "count" in data
    assert isinstance(data["files"], list)
    assert data["count"] == len(data["files"])


def test_get_existing_file():
    test_filename = "testfile.txt"
    response = client.get(f"/files/{test_filename}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"


def test_get_nonexistent_file():
    response = client.get("/files/does_not_exist.txt")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "files_stored_total" in data
    assert "total_storage_mb" in data
    assert "timestamp" in data
