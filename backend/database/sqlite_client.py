import sqlite3
from pathlib import Path


def get_db(path: str = "data/cloudpath.db") -> sqlite3.Connection:
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    schema_path = Path(__file__).parent / "schema.sql"
    conn.executescript(schema_path.read_text())
    conn.commit()
    return conn
