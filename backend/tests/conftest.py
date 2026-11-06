"""Shared pytest fixtures for all test modules."""
import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def empty_questions_dir(tmp_path_factory):
    """Empty questions directory — prevents loading real Chroma data during tests."""
    return str(tmp_path_factory.mktemp("questions"))


@pytest.fixture(scope="session")
def test_client(tmp_path_factory, empty_questions_dir):
    """FastAPI TestClient backed by an isolated temp SQLite + Chroma instance."""
    db_dir = tmp_path_factory.mktemp("data")
    db_path = str(db_dir / "test.db")
    chroma_path = str(db_dir / "chroma")

    os.environ["CLOUDPATH_DB_PATH"] = db_path
    os.environ["CLOUDPATH_CHROMA_PATH"] = chroma_path
    os.environ["CLOUDPATH_QUESTIONS_DIR"] = empty_questions_dir

    # Clear cached settings so env vars take effect
    from config import get_settings
    get_settings.cache_clear()

    # Clear Chroma client singleton so it uses temp path
    from questions.chroma_client import _get_client
    _get_client.cache_clear()

    from main import app
    with TestClient(app) as c:
        yield c

    get_settings.cache_clear()
    _get_client.cache_clear()
    os.environ.pop("CLOUDPATH_DB_PATH", None)
    os.environ.pop("CLOUDPATH_CHROMA_PATH", None)
    os.environ.pop("CLOUDPATH_QUESTIONS_DIR", None)
