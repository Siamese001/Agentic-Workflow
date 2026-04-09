"""Repo-backed signal service for production-like RFP workflow context."""

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
        snapshot.governance["delivery_proof"] = self._collect_delivery_proof(shared_snapshot)
        return snapshot

    def _collect_delivery_proof(self, shared_snapshot: SharedRepoSignalSnapshot) -> dict[str, Any]:
        contracts_dir = self.repo_root / "docs" / "contracts"
        k8s_dir = self.repo_root / "k8s"
        manifests_dir = self.repo_root / "data" / "manifests"
        adg_reports_dir = self.repo_root / "reports" / "adg"
        validation_files = sorted((self.repo_root / "artifacts").glob("validation_*.json"))

        contracts = len(list(contracts_dir.glob("*"))) if contracts_dir.exists() else 0
        k8s_specs = len(list(k8s_dir.glob("*.yaml"))) if k8s_dir.exists() else 0
        manifests = len(list(manifests_dir.glob("*"))) if manifests_dir.exists() else 0
        adg_reports = len(list(adg_reports_dir.glob("*.json"))) if adg_reports_dir.exists() else 0

        if contracts_dir.exists():
            shared_snapshot.provenance["contracts_dir"] = str(contracts_dir)
        if k8s_dir.exists():
            shared_snapshot.provenance["k8s_dir"] = str(k8s_dir)
        if manifests_dir.exists():
            shared_snapshot.provenance["manifests_dir"] = str(manifests_dir)
        if adg_reports_dir.exists():
            shared_snapshot.provenance["adg_reports_dir"] = str(adg_reports_dir)

        confidence = 0
        confidence += 1 if contracts > 0 else 0
        confidence += 1 if k8s_specs > 0 else 0
        confidence += 1 if manifests > 0 else 0
        confidence += 1 if adg_reports > 0 else 0

        return {
            "contracts_count": contracts,
            "k8s_specs_count": k8s_specs,
            "manifest_count": manifests,
            "adg_report_count": adg_reports,
            "validation_artifacts": len(validation_files),
            "requirement_confidence": round(confidence / 4, 3),
        }
