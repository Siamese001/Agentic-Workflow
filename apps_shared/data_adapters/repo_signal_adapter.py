"""Shared adapter for production-like repository signals."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L4_state.adapters import sqlite3_adapter as sqlite3


@dataclass
class RepoSignalSnapshot:
    """Normalized operational signal snapshot for apps_* workflows."""

    captured_at: str
    adg: dict[str, Any] = field(default_factory=dict)
    tests: dict[str, Any] = field(default_factory=dict)
    ci: dict[str, Any] = field(default_factory=dict)
    governance: dict[str, Any] = field(default_factory=dict)
    baseline: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class RepoSignalAdapter:
    """Collects shared repository signals and computes baseline deltas."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]

    def collect(self) -> RepoSignalSnapshot:
        snapshot = RepoSignalSnapshot(captured_at=datetime.now().isoformat())
        snapshot.adg = self._collect_adg(snapshot)
        snapshot.tests = self._collect_tests(snapshot)
        snapshot.ci = self._collect_ci(snapshot)
        snapshot.governance = self._collect_governance(snapshot)
        snapshot.baseline = self._collect_baseline_deltas(snapshot)
        return snapshot

    def _collect_adg(self, snapshot: RepoSignalSnapshot) -> dict[str, Any]:
        candidates = sorted(
            (self.repo_root / "artifacts").glob("**/adg*.sqlite"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            return {"available": False}

        sqlite_path = candidates[0]
        snapshot.provenance["adg_sqlite"] = str(sqlite_path)

        result: dict[str, Any] = {
            "available": True,
            "sqlite_path": str(sqlite_path),
            "sqlite_size_bytes": sqlite_path.stat().st_size,
            "sqlite_mtime": datetime.fromtimestamp(sqlite_path.stat().st_mtime).isoformat(),
            "nodes_count": None,
            "edges_count": None,
        }

        try:
            with sqlite3.connect(sqlite_path) as conn:
                cursor = conn.cursor()
                for table in ("nodes", "edges"):
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    result[f"{table}_count"] = int(cursor.fetchone()[0])
        except sqlite3.Error:
            pass

        return result

    def _collect_tests(self, snapshot: RepoSignalSnapshot) -> dict[str, Any]:
        inventory_path = self.repo_root / "artifacts" / "test_inventory.json"
        surface_path = self.repo_root / "artifacts" / "test_surface_inventory.json"

        result: dict[str, Any] = {
            "inventory_available": inventory_path.exists(),
            "surface_available": surface_path.exists(),
            "inventory_entries": 0,
            "surface_entries": 0,
        }

        if inventory_path.exists():
            snapshot.provenance["test_inventory"] = str(inventory_path)
            result["inventory_entries"] = self._json_entry_count(inventory_path)

        if surface_path.exists():
            snapshot.provenance["test_surface_inventory"] = str(surface_path)
            result["surface_entries"] = self._json_entry_count(surface_path)

        return result

    def _collect_ci(self, snapshot: RepoSignalSnapshot) -> dict[str, Any]:
        workflows_dir = self.repo_root / ".github" / "workflows"
        ci_validation_file = self.repo_root / "artifacts" / "ci_validation_after_fix.txt"

        result: dict[str, Any] = {
            "workflow_count": 0,
            "ci_validation_lines": 0,
        }

        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            result["workflow_count"] = len(workflow_files)
            snapshot.provenance["workflows_dir"] = str(workflows_dir)

        if ci_validation_file.exists():
            result["ci_validation_lines"] = self._line_count(ci_validation_file)
            snapshot.provenance["ci_validation_log"] = str(ci_validation_file)

        return result

    def _collect_governance(self, snapshot: RepoSignalSnapshot) -> dict[str, Any]:
        baseline_path = self.repo_root / "artifacts" / "governance" / "post_denominator_baseline.json"

        result: dict[str, Any] = {
            "denominator_baseline_available": baseline_path.exists(),
            "locked_denominators": {},
        }

        if not baseline_path.exists():
            return result

        snapshot.provenance["governance_baseline"] = str(baseline_path)
        try:
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return result

        if isinstance(baseline, dict):
            for key in ("calls", "records_execution_trace", "writes_to", "reads_from"):
                value = baseline.get(key)
                if isinstance(value, (int, float)):
                    result["locked_denominators"][key] = value

        return result

    def _collect_baseline_deltas(self, snapshot: RepoSignalSnapshot) -> dict[str, Any]:
        baseline_file = self.repo_root / "artifacts" / "monitoring" / "production_signal_baseline.json"

        current = {
            "nodes_count": snapshot.adg.get("nodes_count"),
            "edges_count": snapshot.adg.get("edges_count"),
            "workflow_count": snapshot.ci.get("workflow_count"),
            "inventory_entries": snapshot.tests.get("inventory_entries"),
        }

        if not baseline_file.exists():
            return {"available": False, "current": current, "delta": {}}

        snapshot.provenance["production_signal_baseline"] = str(baseline_file)
        try:
            baseline_payload = json.loads(baseline_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"available": False, "current": current, "delta": {}}

        delta: dict[str, Any] = {}
        for key, value in current.items():
            baseline_value = baseline_payload.get(key)
            if isinstance(value, (int, float)) and isinstance(baseline_value, (int, float)):
                delta[key] = value - baseline_value

        return {
            "available": True,
            "current": current,
            "baseline": baseline_payload,
            "delta": delta,
        }

    @staticmethod
    def _json_entry_count(path: Path) -> int:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return 0

        if isinstance(payload, list):
            return len(payload)
        if isinstance(payload, dict):
            return len(payload)
        return 0

    @staticmethod
    def _line_count(path: Path) -> int:
        with path.open("r", encoding="utf-8", errors="ignore") as file_handle:
            return sum(1 for _ in file_handle)
