"""Repo-backed signal service for production-like executive brief context."""

from __future__ import annotations

import json
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
