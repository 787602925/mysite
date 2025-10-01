from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Any

try:
    from tinydb import TinyDB
except Exception:  # pragma: no cover
    TinyDB = None  # type: ignore


DB_PATH = Path(__file__).resolve().parent / 'data.json'


def get_db() -> TinyDB:
    if TinyDB is None:
        raise RuntimeError('TinyDB is not installed. Run: pip install tinydb')
    return TinyDB(DB_PATH)


def list_items() -> List[Dict[str, Any]]:
    with get_db() as db:
        return list(db)


def insert_item(item: Dict[str, Any]) -> int:
    with get_db() as db:
        return int(db.insert(item))


def remove_item(doc_id: int) -> None:
    with get_db() as db:
        db.remove(doc_ids=[doc_id])


def update_status(doc_id: int, new_status: str) -> None:
    with get_db() as db:
        db.update({'status': new_status}, doc_ids=[doc_id])


def update_item(doc_id: int, fields: Dict[str, Any]) -> None:
    allowed = {k: v for k, v in fields.items() if k in {'company', 'position', 'url', 'status', 'note'}}
    if not allowed:
        return
    with get_db() as db:
        db.update(allowed, doc_ids=[doc_id])


