"""Repo-backed signal service for production-like evaluation context."""

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
        snapshot.governance["release_readiness"] = self._compute_release_readiness(shared_snapshot)
        return snapshot

    def _compute_release_readiness(self, shared_snapshot: SharedRepoSignalSnapshot) -> dict[str, Any]:
        checks = {
            "adg_available": bool(shared_snapshot.adg.get("available")),
            "workflow_available": shared_snapshot.ci.get("workflow_count", 0) > 0,
            "test_signals_available": bool(
                shared_snapshot.tests.get("inventory_available")
                or shared_snapshot.tests.get("surface_available"),
            ),
            "governance_baseline_available": bool(
                shared_snapshot.governance.get("denominator_baseline_available"),
            ),
            "baseline_delta_available": bool(shared_snapshot.baseline.get("available")),
        }
        score = sum(1 for status in checks.values() if status) / len(checks)
        verdict = "ready" if score >= 0.8 else "needs_review" if score >= 0.6 else "hold"
        return {
            "score": round(score, 3),
            "verdict": verdict,
            "checks": checks,
        }
