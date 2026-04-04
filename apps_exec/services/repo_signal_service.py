"""Repo-backed signal service for production-like executive brief context."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from apps_shared.data_adapters import RepoSignalAdapter
from apps_shared.data_adapters import RepoSignalSnapshot as SharedRepoSignalSnapshot


@dataclass
class RepoSignalSnapshot:
    """Snapshot of repository operational signals."""

    captured_at: str
    adg: dict[str, Any] = field(default_factory=dict)
    tests: dict[str, Any] = field(default_factory=dict)
    ci: dict[str, Any] = field(default_factory=dict)
    governance: dict[str, Any] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class RepoSignalService:
    """Collects production-like operational signals from repository artifacts."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]
        self._shared = RepoSignalAdapter(self.repo_root)

    def collect(self) -> RepoSignalSnapshot:
        shared_snapshot = self._shared.collect()
        snapshot = RepoSignalSnapshot(
            captured_at=shared_snapshot.captured_at,
            adg=shared_snapshot.adg,
            tests=shared_snapshot.tests,
            ci=shared_snapshot.ci,
            governance=shared_snapshot.governance,
            sources=shared_snapshot.provenance,
        )
        snapshot.governance["baseline"] = shared_snapshot.baseline
        snapshot.governance["engineering_posture"] = self._collect_engineering_posture(shared_snapshot)
        return snapshot

    def _collect_engineering_posture(self, shared_snapshot: SharedRepoSignalSnapshot) -> dict[str, Any]:
        monitoring_dir = self.repo_root / "artifacts" / "monitoring"
        freeze_reports_dir = self.repo_root / "data" / "freeze_reports"
        governance_dir = self.repo_root / "artifacts" / "governance"

        monitoring_files = sorted(monitoring_dir.glob("*.json")) if monitoring_dir.exists() else []
        freeze_reports = sorted(freeze_reports_dir.glob("*.json")) if freeze_reports_dir.exists() else []
        governance_reports = sorted(governance_dir.glob("*.json")) if governance_dir.exists() else []

        if monitoring_dir.exists():
            shared_snapshot.provenance["monitoring_dir"] = str(monitoring_dir)
        if freeze_reports_dir.exists():
            shared_snapshot.provenance["freeze_reports_dir"] = str(freeze_reports_dir)
        if governance_dir.exists():
            shared_snapshot.provenance["governance_dir"] = str(governance_dir)

        risk_score = 0
        if not monitoring_files:
            risk_score += 1
        if not freeze_reports:
            risk_score += 1
        if not governance_reports:
            risk_score += 1

        return {
            "monitoring_artifacts": len(monitoring_files),
            "freeze_reports": len(freeze_reports),
            "governance_reports": len(governance_reports),
            "risk_level": "high" if risk_score >= 2 else "medium" if risk_score == 1 else "low",
            "adg_nodes": shared_snapshot.adg.get("nodes_count"),
            "adg_edges": shared_snapshot.adg.get("edges_count"),
        }

    def _collect_adg_signals(self, snapshot: RepoSignalSnapshot) -> dict[str, Any]:
        candidates = sorted(
            (self.repo_root / "artifacts").glob("**/adg*.sqlite"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            return {"available": False}

        sqlite_path = candidates[0]
        snapshot.sources["adg_sqlite"] = str(sqlite_path)

        result: dict[str, Any] = {
            "available": True,
            "sqlite_path": str(sqlite_path),
            "sqlite_size_bytes": sqlite_path.stat().st_size,
            "sqlite_mtime": datetime.fromtimestamp(sqlite_path.stat().st_mtime).isoformat(),
        }

        try:
            with sqlite3.connect(sqlite_path) as conn:
                cursor = conn.cursor()
                for table in ("nodes", "edges"):
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        result[f"{table}_count"] = int(cursor.fetchone()[0])
                    except sqlite3.Error:
                        result[f"{table}_count"] = None
        except sqlite3.Error:
            result["nodes_count"] = None
            result["edges_count"] = None

        return result

    def _collect_test_signals(self, snapshot: RepoSignalSnapshot) -> dict[str, Any]:
        inventory_path = self.repo_root / "artifacts" / "test_inventory.json"
        surface_path = self.repo_root / "artifacts" / "test_surface_inventory.json"

        result: dict[str, Any] = {
            "inventory_available": inventory_path.exists(),
            "surface_available": surface_path.exists(),
            "inventory_entries": 0,
            "surface_entries": 0,
        }

        if inventory_path.exists():
            snapshot.sources["test_inventory"] = str(inventory_path)
            result["inventory_entries"] = self._json_entry_count(inventory_path)

        if surface_path.exists():
            snapshot.sources["test_surface_inventory"] = str(surface_path)
            result["surface_entries"] = self._json_entry_count(surface_path)

        return result

    def _collect_ci_signals(self, snapshot: RepoSignalSnapshot) -> dict[str, Any]:
        workflows_dir = self.repo_root / ".github" / "workflows"
        ci_validation_file = self.repo_root / "artifacts" / "ci_validation_after_fix.txt"

        result: dict[str, Any] = {
            "workflow_count": 0,
            "ci_validation_lines": 0,
        }

        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            result["workflow_count"] = len(workflow_files)
            snapshot.sources["workflows_dir"] = str(workflows_dir)

        if ci_validation_file.exists():
            result["ci_validation_lines"] = self._line_count(ci_validation_file)
            snapshot.sources["ci_validation_log"] = str(ci_validation_file)

        return result

    def _collect_governance_signals(self, snapshot: RepoSignalSnapshot) -> dict[str, Any]:
        baseline_path = self.repo_root / "artifacts" / "governance" / "post_denominator_baseline.json"
        result: dict[str, Any] = {
            "denominator_baseline_available": baseline_path.exists(),
            "locked_denominators": {},
        }

        if not baseline_path.exists():
            return result

        snapshot.sources["governance_baseline"] = str(baseline_path)
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
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            return sum(1 for _ in fh)
