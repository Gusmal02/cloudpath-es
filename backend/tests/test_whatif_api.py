from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

MOCK_RESPONSE = """{
  "costo": {"nivel": "medio", "estimacion_mensual": "$50-150/mes", "detalle": []},
  "riesgos": [{"titulo": "Sin redundancia", "descripcion": "EC2 sin ASG", "severidad": "alta"}],
  "sugerencias": [{"titulo": "Agregar Auto Scaling", "descripcion": "...", "prioridad": "alta"}]
}"""


def test_whatif_empty_nodes_returns_400():
    r = client.post("/whatif", json={"nodes": [], "edges": [], "provider": "AWS"})
    assert r.status_code == 400


def test_whatif_returns_structured_analysis():
    with patch("routers.whatif.call_ollama", new=AsyncMock(return_value=MOCK_RESPONSE)):
        r = client.post(
            "/whatif",
            json={
                "nodes": [
                    {"id": "n1", "data": {"label": "EC2", "category": "Cómputo", "description": "VMs"}}
                ],
                "edges": [],
                "provider": "AWS",
            },
        )
    assert r.status_code == 200
    body = r.json()
    assert "costo" in body
    assert "riesgos" in body
    assert "sugerencias" in body


def test_whatif_ollama_unavailable_returns_503():
    from whatif.ollama_client import OllamaUnavailableError

    with patch(
        "routers.whatif.call_ollama",
        new=AsyncMock(side_effect=OllamaUnavailableError("down")),
    ):
        r = client.post(
            "/whatif",
            json={
                "nodes": [
                    {"id": "n1", "data": {"label": "S3", "category": "Almacenamiento", "description": "Objetos"}}
                ],
                "edges": [],
                "provider": "AWS",
            },
        )
    assert r.status_code == 503


# Integration test — skipped when Ollama is not running
def _ollama_available() -> bool:
    try:
        httpx.get("http://localhost:11434/api/tags", timeout=2)
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _ollama_available(), reason="Ollama not running")
def test_whatif_live_ollama_returns_valid_structure():
    r = client.post(
        "/whatif",
        json={
            "nodes": [
                {"id": "n1", "data": {"label": "EC2", "category": "Cómputo", "description": "Instancias virtuales"}},
                {"id": "n2", "data": {"label": "RDS", "category": "Base de datos", "description": "SQL administrado"}},
            ],
            "edges": [{"source": "n1", "target": "n2"}],
            "provider": "AWS",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "costo" in body
    assert isinstance(body["riesgos"], list)
    assert isinstance(body["sugerencias"], list)
