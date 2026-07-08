"""Shared apps_rg artifact resolution for scorecards and diagnostics."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_eval.contracts import AppOutputSnapshot


_EXTRA_ROLE_PATHS = {
    "graph_selection_rationale": [
        "native_c03_final_evidence.json",
        "graph_selection_rationale.json",
        "c03_promotion_candidates.json",
        "selected_graph_evidence_plan.json",
    ],
}


@dataclass(frozen=True)
class ResolvedAppsRgArtifact:
    artifact_role: str
    artifact_ref: str = ""
    evidence_ref: str = ""
    evidence_digest: str = ""
    payload: Any = None
    resolution_source: str = "missing"
    source_artifact_schema: str = ""
    expected_refs: tuple[str, ...] = ()

    @property
    def found(self) -> bool:
        return bool(self.artifact_ref)


def canonical_digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def path_digest(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def json_payload(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _index_artifact_ref(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("artifact_ref") or value.get("path") or value.get("ref") or "").strip()
    return str(value or "").strip()


def _index_evidence_ref(value: Any, fallback: str) -> str:
    if isinstance(value, dict):
        return str(value.get("evidence_ref") or value.get("artifact_ref") or value.get("path") or fallback).strip()
    return fallback


def _index_payload(value: Any) -> Any:
    return value.get("payload") if isinstance(value, dict) and "payload" in value else value


def expected_relative_paths(
    *,
    role: str,
    lane_id: str,
    artifact_contract: dict[str, Any],
) -> tuple[str, ...]:
    role_contract = artifact_contract.get("artifact_roles", {}).get(role, {})
    templates = list(role_contract.get("relative_paths", []))
    templates.extend(_EXTRA_ROLE_PATHS.get(role, []))
    return tuple(str(template).format(lane=lane_id) for template in templates)


def resolve_apps_rg_artifact(
    *,
    snapshot: AppOutputSnapshot,
    role: str,
    lane_id: str = "",
    artifact_contract: dict[str, Any],
    planned_eval_artifacts: dict[str, Any] | None = None,
) -> ResolvedAppsRgArtifact:
    planned = planned_eval_artifacts or {}
    role_contract = artifact_contract.get("artifact_roles", {}).get(role, {})
    source_schema = str(role_contract.get("source_artifact_schema", ""))
    expected_refs = expected_relative_paths(
        role=role,
        lane_id=lane_id,
        artifact_contract=artifact_contract,
    )

    planned_value = planned.get(role)
    if planned_value not in (None, "", [], {}):
        first = as_list(planned_value)[0]
        return ResolvedAppsRgArtifact(
            artifact_role=role,
            artifact_ref=str(first),
            evidence_ref="planned_apps_eval_emit",
            evidence_digest=canonical_digest(planned_value),
            payload=planned_value,
            resolution_source="planned_eval_artifacts",
            source_artifact_schema=source_schema,
            expected_refs=expected_refs,
        )

    index = snapshot.artifact_index or {}
    for key in (f"{lane_id}:{role}" if lane_id else "", role):
        if not key:
            continue
        index_value = index.get(key)
        if index_value in (None, "", [], {}):
            continue
        first = as_list(index_value)[0]
        artifact_ref = _index_artifact_ref(first)
        if not artifact_ref:
            continue
        return ResolvedAppsRgArtifact(
            artifact_role=role,
            artifact_ref=artifact_ref,
            evidence_ref=_index_evidence_ref(first, artifact_ref),
            evidence_digest=canonical_digest(index_value),
            payload=_index_payload(first),
            resolution_source="snapshot_artifact_index",
            source_artifact_schema=source_schema,
            expected_refs=expected_refs,
        )

    root = Path(snapshot.run_root).resolve() if snapshot.run_root else None
    if root is not None:
        for rel in expected_refs:
            candidate = (root / rel).resolve()
            if candidate.is_file():
                return ResolvedAppsRgArtifact(
                    artifact_role=role,
                    artifact_ref=candidate.as_posix(),
                    evidence_ref=rel,
                    evidence_digest=path_digest(candidate),
                    payload=json_payload(candidate) if candidate.suffix.lower() == ".json" else None,
                    resolution_source="run_root_file",
                    source_artifact_schema=source_schema,
                    expected_refs=expected_refs,
                )

    return ResolvedAppsRgArtifact(
        artifact_role=role,
        resolution_source="missing",
        source_artifact_schema=source_schema,
        expected_refs=expected_refs,
    )

