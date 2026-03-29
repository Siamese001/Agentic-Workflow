"""Repo-backed signal service for production-like LIC campaign context."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_shared.data_adapters import RepoSignalAdapter, RepoSignalSnapshot


class RepoSignalService:
    """Collects shared and LIC-specific operational signals from repository artifacts."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]
        self._shared = RepoSignalAdapter(self.repo_root)

    def collect(self) -> RepoSignalSnapshot:
        snapshot = self._shared.collect()
        lic_domain = self._collect_lic_domain_signals(snapshot)
        observability = self._collect_observability_signals(snapshot)

        snapshot.governance["lic_domain"] = lic_domain
        snapshot.governance["observability"] = observability
        return snapshot

    def _collect_lic_domain_signals(self, snapshot: RepoSignalSnapshot) -> dict[str, Any]:
        agent_specs_path = self.repo_root / "apps_lic" / "config" / "agent_specs.json"
        sender_kb_path = self.repo_root / "apps_shared" / "data" / "sender_knowledge_base.json"

        result: dict[str, Any] = {
            "agent_specs_available": agent_specs_path.exists(),
            "sender_knowledge_base_available": sender_kb_path.exists(),
            "agent_spec_count": 0,
            "sender_profile_count": 0,
        }

        if agent_specs_path.exists():
            snapshot.provenance["apps_lic_agent_specs"] = str(agent_specs_path)
            result["agent_spec_count"] = self._json_entry_count(agent_specs_path)

        if sender_kb_path.exists():
            snapshot.provenance["apps_shared_sender_kb"] = str(sender_kb_path)
            result["sender_profile_count"] = self._json_entry_count(sender_kb_path)

        return result

    def _collect_observability_signals(self, snapshot: RepoSignalSnapshot) -> dict[str, Any]:
        observability_dir = self.repo_root / "artifacts" / "observability"
        governance_dir = self.repo_root / "artifacts" / "governance"

        result: dict[str, Any] = {
            "observability_artifact_count": 0,
            "governance_artifact_count": 0,
        }

        if observability_dir.exists():
            result["observability_artifact_count"] = len(list(observability_dir.glob("*.json")))
            snapshot.provenance["observability_dir"] = str(observability_dir)

        if governance_dir.exists():
            result["governance_artifact_count"] = len(list(governance_dir.glob("*.json")))
            snapshot.provenance["governance_dir"] = str(governance_dir)

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
