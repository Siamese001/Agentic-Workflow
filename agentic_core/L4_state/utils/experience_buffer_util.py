from __future__ import annotations

from agentic_core.interfaces.write_gateway import get_write_gateway


def _get_write_gateway():
    """Get UWG instance - L4 may only use, not import tools."""
    return get_write_gateway()


"\nExperienceBuffer – Sovereign Agent Role Component (Phase 30 – Dec 30, 2025)\n\nPurpose:\n  Persistent, file-backed learning from execution outcomes.\n  Enables agents to predict success probability of actions based on historical data.\n  Critical for RgHealingOrchestrator and all validators to avoid repeating failed strategies.\n\nConstitutional Alignment:\n  - Turns reactive healing into predictive intelligence\n  - Enables cumulative sovereignty improvement\n  - Fully observable via JSONL logs\n\nZero-Ambiguity Standard: Renamed from ExperienceBuffer.py to experience_buffer_util.py\n"
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write


class ExperienceBuffer:
    """
    Lightweight, append-only experience replay buffer with JSONL persistence.
    Designed for sovereign agents to learn from healing/validation outcomes.
    """

    # guardian: allow-magic-config
    def __init__(self, path: Path, max_entries: int = 1000, similarity_keys: list[str] | None = None):
        """
        Initialize buffer with persistent storage.

        Args:
            path: File path for JSONL storage (e.g., logs/healer_experience.jsonl)
            max_entries: Maximum historical entries to retain
            similarity_keys: Keys used for similarity matching (default: all keys)
        """
        self.path = Path(path)
        self.max_entries = max_entries
        self.similarity_keys = similarity_keys or []
        self.Logger = logging.getLogger(f"{__name__}.{self.path.stem}")
        _get_write_gateway().ensure_dir(self.path.parent)
        if not self.path.exists():
            assert_no_persistent_write("L4", "write_text")
            _get_write_gateway().write_text(self.path, "")
            self.Logger.info(f"Created new experience buffer at {self.path}")

    def record(self, entry: dict[str, Any]) -> None:
        """
        Record a new experience outcome.
        Appends to file and enforces size limit.
        """
        entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
        entry["entry_id"] = int(time.time() * 1000000)
        _get_write_gateway().write_json(self.path, entry, indent=2)
        self._enforce_size_limit()
        outcome = "success" if entry.get("success", False) else "failure"
        self.Logger.debug(f"Recorded {outcome}: {entry.get('action')} on {entry.get('target')}")

    def _enforce_size_limit(self) -> None:
        """Trim file to max_entries by keeping newest lines."""
        if self.max_entries <= 0:
            return
        lines = []
        try:
            with self.path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
        # guardian: allow-silent-swallow
        except Exception as e:
            self.Logger.error(f"Failed to read experience buffer: {e}")
            return
        if len(lines) > self.max_entries:
            kept = lines[-self.max_entries :]
            try:
                assert_no_persistent_write("L4", "write_text")
                _get_write_gateway().write_text(self.path, "".join(kept), encoding="utf-8")
                self.Logger.info(f"Trimmed experience buffer from {len(lines)} to {len(kept)} entries")
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                self.Logger.error(f"Failed to trim buffer: {e}")

    def load_all(self) -> list[dict[str, Any]]:
        """Load all entries (newest first)."""
        entries = []
        try:
            with self.path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
            return list(reversed(entries))
        # guardian: allow-silent-swallow
        except Exception as e:
            self.Logger.error(f"Failed to load experience buffer: {e}")
            return []

    # guardian: allow-magic-config
    def find_similar(
        self,
        action: str | None = None,
        target: str | None = None,
        context_hash: str | None = None,
        limit: int = 20,
        **extra_filters,
    ) -> list[dict[str, Any]]:
        """
        Find historically similar experiences for success prediction.
        Matches on provided filters.
        """
        all_entries = self.load_all()
        matches = []
        for entry in all_entries:
            if action and entry.get("action") != action:
                continue
            if target and entry.get("target") != target:
                continue
            if context_hash and entry.get("context_hash") != context_hash:
                continue
            if all((entry.get(k) == v for k, v in extra_filters.items())):
                matches.append(entry)
            if len(matches) >= limit:
                break
        return matches

    def predict_success_probability(
        self, action: str, target: str | None = None, context_hash: str | None = None, **extra_context
    ) -> float:
        """
        Predict success probability based on historical outcomes.
        Returns 0.5 if no relevant history.
        """
        similar = self.find_similar(action=action, target=target, context_hash=context_hash, **extra_context)
        if not similar:
            return 0.5
        successes = sum(1 for e in similar if e.get("success", False))
        return successes / len(similar)

    def get_stats(self) -> dict[str, Any]:
        """Return buffer statistics for monitoring."""
        entries = self.load_all()
        if not entries:
            return {"total_entries": 0, "success_rate": None}
        successes = sum(1 for e in entries if e.get("success", False))
        return {
            "total_entries": len(entries),
            "success_rate": successes / len(entries),
            "most_common_action": max(
                (e.get("action") for e in entries if e.get("action")),
                key=lambda a: sum(1 for e in entries if e.get("action") == a),
                default=None,
            ),
        }
