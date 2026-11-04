import os
from dataclasses import dataclass, field
from pathlib import Path

# Data lives inside backend/data/ alongside this package
_ROOT = Path(__file__).parent / "data"


def _default(env_key: str, relative: str) -> str:
    return os.environ.get(env_key, str(_ROOT / relative))


@dataclass
class Settings:
    db_path: str = field(default_factory=lambda: _default("CLOUDPATH_DB_PATH", "cloudpath.db"))
    chroma_path: str = field(default_factory=lambda: _default("CLOUDPATH_CHROMA_PATH", "chroma"))
    questions_dir: str = field(default_factory=lambda: _default("CLOUDPATH_QUESTIONS_DIR", "questions"))
    port_file: str = field(default_factory=lambda: _default("CLOUDPATH_PORT_FILE", ".port"))
    ollama_url: str = field(default_factory=lambda: os.environ.get("OLLAMA_URL", "http://localhost:11434"))
    ollama_model: str = field(default_factory=lambda: os.environ.get("OLLAMA_MODEL", "llama3.2:3b"))


def get_settings() -> Settings:
    return Settings()
