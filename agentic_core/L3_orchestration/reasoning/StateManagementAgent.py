"""Minimal StateManagementAgent source file for AST-driven tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class StateEntry:
    key: str
    file_path: str
    value: Any = None

    def as_dict(self) -> dict[str, Any]:
        return {"key": self.key, "file_path": self.file_path, "value": self.value}


class StateManagementAgent:
    def __init__(self) -> None:
        self._state: dict[str, StateEntry] = {}

    @staticmethod
    def _normalize_key(key: str | None) -> str:
        normalized = str(key or "default").strip()
        return normalized or "default"

    @staticmethod
    def _normalize_file_path(file_path: str | Path) -> str:
        if not file_path:
            return ""
        return str(Path(file_path).as_posix())

    def run(self, key: str, file_path: str, value: Any = None) -> StateEntry:
        normalized_key = self._normalize_key(key)
        normalized_path = self._normalize_file_path(file_path)
        entry = StateEntry(key=normalized_key, file_path=normalized_path, value=value)
        self._state[normalized_key] = entry
        return entry

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(payload or {})
        entry = self.run(
            normalized.get("key", "default"),
            normalized.get("file_path", ""),
            normalized.get("value"),
        )
        return entry.as_dict()

    def get(self, key: str) -> StateEntry | None:
        return self._state.get(self._normalize_key(key))

    def delete(self, key: str) -> StateEntry | None:
        return self._state.pop(self._normalize_key(key), None)

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return {key: entry.as_dict() for key, entry in self._state.items()}
