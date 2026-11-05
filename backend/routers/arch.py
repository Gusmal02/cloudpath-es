import json
import sqlite3
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator

from config import get_settings
from database.sqlite_client import get_db

router = APIRouter(prefix="/arch", tags=["arch"])


def _get_db():
    settings = get_settings()
    db = get_db(settings.db_path)
    try:
        yield db
    finally:
        db.close()


class ArchIn(BaseModel):
    name: str
    provider: str
    nodes_json: str = "[]"
    edges_json: str = "[]"

    @field_validator("nodes_json", "edges_json")
    @classmethod
    def must_be_valid_json(cls, v: str) -> str:
        try:
            json.loads(v)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON inválido: {exc}") from exc
        return v


@router.post("")
def save_arch(body: ArchIn, db: sqlite3.Connection = Depends(_get_db)):
    arch_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO architectures (id, name, provider, nodes_json, edges_json) VALUES (?,?,?,?,?)",
        (arch_id, body.name, body.provider, body.nodes_json, body.edges_json),
    )
    db.commit()
    row = db.execute(
        "SELECT id, name, provider, created_at FROM architectures WHERE id=?",
        (arch_id,),
    ).fetchone()
    return dict(row)


@router.get("")
def list_arch(provider: str | None = None, db: sqlite3.Connection = Depends(_get_db)):
    if provider:
        rows = db.execute(
            "SELECT id, name, provider, created_at FROM architectures WHERE provider=? ORDER BY created_at DESC",
            (provider,),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT id, name, provider, created_at FROM architectures ORDER BY created_at DESC",
        ).fetchall()
    return [dict(r) for r in rows]


@router.get("/{arch_id}")
def get_arch(arch_id: str, db: sqlite3.Connection = Depends(_get_db)):
    row = db.execute(
        "SELECT * FROM architectures WHERE id=?", (arch_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Arquitectura no encontrada")
    return dict(row)


@router.delete("/{arch_id}")
def delete_arch(arch_id: str, db: sqlite3.Connection = Depends(_get_db)):
    db.execute("DELETE FROM architectures WHERE id=?", (arch_id,))
    db.commit()
    return {"deleted": True}
