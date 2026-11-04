import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path):
    os.environ["CLOUDPATH_DB_PATH"] = str(tmp_path / "test.db")
    os.environ["CLOUDPATH_CHROMA_PATH"] = str(tmp_path / "chroma")
    os.environ["CLOUDPATH_PORT_FILE"] = str(tmp_path / ".port")

    from main import app
    with TestClient(app) as c:
        yield c


def test_save_and_load_architecture(client):
    r = client.post("/arch", json={
        "name": "Mi primera arquitectura",
        "provider": "AWS",
        "nodes_json": '[{"id":"1","type":"service","position":{"x":100.5,"y":200.5}}]',
        "edges_json": "[]",
    })
    assert r.status_code == 200
    arch_id = r.json()["id"]
    assert r.json()["name"] == "Mi primera arquitectura"

    r2 = client.get(f"/arch/{arch_id}")
    assert r2.status_code == 200
    assert r2.json()["name"] == "Mi primera arquitectura"
    assert '"x":100.5' in r2.json()["nodes_json"]


def test_list_architectures_filtered_by_provider(client):
    client.post("/arch", json={"name": "AWS arch", "provider": "AWS", "nodes_json": "[]", "edges_json": "[]"})
    client.post("/arch", json={"name": "GCP arch", "provider": "GCP", "nodes_json": "[]", "edges_json": "[]"})

    r = client.get("/arch?provider=AWS")
    assert r.status_code == 200
    names = [a["name"] for a in r.json()]
    assert "AWS arch" in names
    assert "GCP arch" not in names


def test_delete_architecture(client):
    r = client.post("/arch", json={"name": "borrar", "provider": "AWS", "nodes_json": "[]", "edges_json": "[]"})
    arch_id = r.json()["id"]

    del_r = client.delete(f"/arch/{arch_id}")
    assert del_r.status_code == 200
    assert del_r.json()["deleted"] is True

    r2 = client.get(f"/arch/{arch_id}")
    assert r2.status_code == 404


def test_get_nonexistent_architecture_returns_404(client):
    r = client.get("/arch/no-existe-este-id")
    assert r.status_code == 404
