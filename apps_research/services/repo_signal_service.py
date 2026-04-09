"""Repo-backed signal service for production-like research context."""

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
        snapshot.governance["research_context"] = self._collect_research_context(shared_snapshot)
        return snapshot

    def _collect_research_context(self, shared_snapshot: SharedRepoSignalSnapshot) -> dict[str, Any]:
        playbooks_dir = self.repo_root / "data" / "external" / "reference_playbooks"
        corpus_dir = self.repo_root / "data" / "corpus"
        evidence_dir = self.repo_root / "artifacts" / "evidence"
        forensic_files = sorted((self.repo_root / "artifacts").glob("forensic_discovery_*.json"))

        playbook_count = len(list(playbooks_dir.glob("*"))) if playbooks_dir.exists() else 0
        corpus_count = len(list(corpus_dir.glob("*.jsonl"))) if corpus_dir.exists() else 0
        evidence_count = len(list(evidence_dir.glob("*"))) if evidence_dir.exists() else 0

        if playbooks_dir.exists():
            shared_snapshot.provenance["reference_playbooks_dir"] = str(playbooks_dir)
        if corpus_dir.exists():
            shared_snapshot.provenance["research_corpus_dir"] = str(corpus_dir)
        if evidence_dir.exists():
            shared_snapshot.provenance["evidence_dir"] = str(evidence_dir)
        if forensic_files:
            shared_snapshot.provenance["forensic_discovery_latest"] = str(forensic_files[-1])

        freshness_score = 0
        freshness_score += 1 if playbook_count > 0 else 0
        freshness_score += 1 if corpus_count > 0 else 0
        freshness_score += 1 if evidence_count > 0 else 0
        freshness_score += 1 if len(forensic_files) > 0 else 0

        return {
            "reference_playbooks": playbook_count,
            "corpus_files": corpus_count,
            "evidence_artifacts": evidence_count,
            "forensic_snapshots": len(forensic_files),
            "source_reliability": round(freshness_score / 4, 3),
            "drift_delta_available": bool(shared_snapshot.baseline.get("available")),
        }
