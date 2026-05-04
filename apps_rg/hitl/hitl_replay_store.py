"""W7 P-HITL4 — Append-only JSONL replay store for apps_rg HITL decisions.

Every HumanReviewDecision is written as a single JSON line.  Each row
contains decision_hash, input_manifest_hash, replay_key, timestamp,
chosen_option_id, and decision_id — sufficient for offline verification
without re-running the pipeline.

Hash verification:
    stored_row["decision_hash"] == sha256(decision_id + chosen_option_id + input_manifest_hash)

Plan: apps-rg-canonical-wireup-c8a4f2 W7 P-HITL4.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from apps_rg.hitl.hitl_schemas import HumanReviewDecision

_LOCK = threading.Lock()
_DEFAULT_FILENAME = "hitl_replay_log.jsonl"


class HITLReplayStore:
    """Append-only JSONL store for HumanReviewDecision records."""

    def __init__(self, store_dir: Path) -> None:
        self._path = store_dir / _DEFAULT_FILENAME
        self._path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def append(self, decision: HumanReviewDecision) -> None:
        """Append one decision row.  Thread-safe via module-level lock."""
        row: dict[str, Any] = {
            "decision_id": decision.decision_id,
            "request_id": decision.request_id,
            "chosen_option_id": decision.chosen_option_id,
            "decision_timestamp": decision.decision_timestamp,
            "input_manifest_hash": decision.input_manifest_hash,
            "decision_hash": decision.decision_hash,
            "replay_key": decision.replay_key,
            "operator_id": decision.operator_id,
        }
        with _LOCK:
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row) + "\n")

    # ------------------------------------------------------------------
    # Read / verify
    # ------------------------------------------------------------------

    def load_all(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        rows: list[dict[str, Any]] = []
        with self._path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def verify_all(self) -> list[str]:
        """Return list of error strings for rows with hash mismatch.
        Empty list means all rows verified OK.
        """
        errors: list[str] = []
        for row in self.load_all():
            expected = HumanReviewDecision.compute_hash(
                row["decision_id"],
                row["chosen_option_id"],
                row["input_manifest_hash"],
            )
            if row["decision_hash"] != expected:
                errors.append(
                    f"decision_id={row['decision_id']!r} hash mismatch: "
                    f"stored={row['decision_hash']!r} expected={expected!r}"
                )
        return errors

    def find_by_replay_key(self, replay_key: str) -> dict[str, Any] | None:
        for row in self.load_all():
            if row.get("replay_key") == replay_key:
                return row
        return None
