"""Simple disk-backed cache used to avoid repeated LLM calls."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, Optional


class DiskCache:
    """Tiny JSON file cache for reproducible runs."""

    def __init__(self, path: str):
        """Initialize a disk cache backed by a JSON file."""
        self.path = path
        self._data: Dict[str, Any] = {}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    self._data = json.load(f)
            except Exception:
                # Corrupted cache files are treated as empty.
                self._data = {}

    def get(self, key: str) -> Optional[Any]:
        """Return cached value for key if present."""
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        """Insert a value and persist it to disk."""
        self._data[key] = value
        self._persist()

    def _persist(self) -> None:
        """Write the full cache to disk."""
        with open(self.path, "w") as f:
            json.dump(self._data, f, ensure_ascii=True, indent=2)


def make_cache_key(payload: Any) -> str:
    """Create a stable hash key from a JSON-serializable payload."""
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
