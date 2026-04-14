"""Repo-backed signal service for production-like resume workflow context."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from apps_shared.data_adapters import RepoSignalAdapter
    from apps_shared.data_adapters import RepoSignalSnapshot as SharedRepoSignalSnapshot

    _HAS_SHARED_REPO_SIGNALS = True
except Exception:  # guardian: allow-broad-exception -- apps_shared is an optional monorepo dep; absent in standalone/CI environments
    RepoSignalAdapter = None  # type: ignore[assignment,misc]
    SharedRepoSignalSnapshot = Any  # type: ignore[assignment,misc]
    _HAS_SHARED_REPO_SIGNALS = False


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
    """Collect production-like operational signals from repository artifacts."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]
        self._shared = RepoSignalAdapter(self.repo_root) if _HAS_SHARED_REPO_SIGNALS else None

    def collect(self) -> RepoSignalSnapshot:
        if self._shared is None:
            return self._collect_fallback()
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
        snapshot.governance["market_fit"] = self._collect_market_fit_signals(shared_snapshot)
        return snapshot

    def _collect_fallback(self) -> RepoSignalSnapshot:
        workflows = sorted((self.repo_root / ".github" / "workflows").glob("*.yml"))
        workflows.extend(sorted((self.repo_root / ".github" / "workflows").glob("*.yaml")))
        test_files = list(self.repo_root.rglob("test_*.py"))
        snapshot = RepoSignalSnapshot(
            captured_at=datetime.utcnow().isoformat() + "Z",
            adg={"available": False, "nodes_count": 0},
            tests={
                "inventory_available": bool(test_files),
                "surface_available": bool(test_files),
                "inventory_entries": len(test_files),
            },
            ci={"workflow_count": len(workflows)},
            governance={"denominator_baseline_available": False},
            sources={"mode": "fallback"},
        )
        snapshot.governance["baseline"] = {"available": False}
        snapshot.governance["market_fit"] = {
            "best_practice_docs": 0,
            "rg_config_json_count": len(list((self.repo_root / "apps_rg" / "config").glob("*.json")))
            if (self.repo_root / "apps_rg" / "config").exists()
            else 0,
            "benchmark_history_count": len(
                list((self.repo_root / "artifacts").glob("benchmark_results*.json"))
            )
            if (self.repo_root / "artifacts").exists()
            else 0,
            "role_fit_score": 0.0,
            "delta_available": False,
        }
        return snapshot

    def _collect_market_fit_signals(self, shared_snapshot: SharedRepoSignalSnapshot) -> dict[str, Any]:
        best_practices_dir = self.repo_root / "data" / "external" / "openai_best_practices"
        rg_config_dir = self.repo_root / "apps_rg" / "config"
        benchmark_files = sorted((self.repo_root / "artifacts").glob("benchmark_results*.json"))

        best_practice_docs = len(list(best_practices_dir.glob("*"))) if best_practices_dir.exists() else 0
        rg_config_files = len(list(rg_config_dir.glob("*.json"))) if rg_config_dir.exists() else 0

        if best_practices_dir.exists():
            shared_snapshot.provenance["openai_best_practices_dir"] = str(best_practices_dir)
        if rg_config_dir.exists():
            shared_snapshot.provenance["apps_rg_config_dir"] = str(rg_config_dir)
        if benchmark_files:
            shared_snapshot.provenance["rg_benchmark_latest"] = str(benchmark_files[-1])

        fit_score = 0
        fit_score += 1 if best_practice_docs > 0 else 0
        fit_score += 1 if rg_config_files > 0 else 0
        fit_score += 1 if len(benchmark_files) > 0 else 0

        return {
            "best_practice_docs": best_practice_docs,
            "rg_config_json_count": rg_config_files,
            "benchmark_history_count": len(benchmark_files),
            "role_fit_score": round(fit_score / 3, 3),
            "delta_available": bool(shared_snapshot.baseline.get("available")),
        }
