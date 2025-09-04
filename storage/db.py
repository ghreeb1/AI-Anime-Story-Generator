"""Simple local JSON storage for prototypes.

Provides basic save/load for records keyed by id. In production, replace
with MongoDB integration.
"""
import json
import os
from typing import Any, Dict


class LocalDB:
    def __init__(self, path: str = "storage/db.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _read_all(self) -> Dict[str, Any]:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, key: str, record: Dict[str, Any]) -> None:
        data = self._read_all()
        data[key] = record
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, key: str) -> Dict[str, Any]:
        data = self._read_all()
        return data.get(key)


