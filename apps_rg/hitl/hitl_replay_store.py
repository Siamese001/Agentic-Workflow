"""JSONL replay store for apps_rg HITL decisions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .hitl_schemas import HumanReviewDecision


class HITLReplayStore:
    """Append-only local replay store for HITL decision records."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = root / "hitl_replay.jsonl"

    def append(self, decision: HumanReviewDecision) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(decision.to_dict(), sort_keys=True) + "\n")

    def load_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()
                if stripped:
                    rows.append(json.loads(stripped))
        return rows

    def verify_all(self) -> list[str]:
        errors: list[str] = []
        for index, row in enumerate(self.load_all(), start=1):
            try:
                decision = HumanReviewDecision(**row)
            except TypeError as exc:
                errors.append(f"row {index}: malformed decision: {exc}")
                continue
            if not decision.verify_hash():
                errors.append(f"row {index}: decision_hash mismatch")
        return errors

    def find_by_replay_key(self, replay_key: str) -> dict[str, Any] | None:
        for row in self.load_all():
            if row.get("replay_key") == replay_key:
                return row
        return None


__all__ = ["HITLReplayStore"]
