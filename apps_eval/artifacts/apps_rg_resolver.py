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
_EVAL_OUTPUT_ROLES = frozenset(
    {
        "eval_record",
        "scorecard_rows",
        "component_scorecards",
        "coverage_matrix",
        "regression_summary",
    }
)


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
    byte_length: int = 0
    failure_reason: str = ""

    @property
    def found(self) -> bool:
        return bool(self.artifact_ref)


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


def _normal_digest(value: Any) -> str:
    return str(value or "").strip().removeprefix("sha256:")


def _contained_path(ref: str | Path, root: Path) -> Path | None:
    resolved_root = root.resolve()
    raw = Path(ref)
    candidate = raw.resolve() if raw.is_absolute() else (resolved_root / raw).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError:
        return None
    return candidate


def _manifest_digest(snapshot: AppOutputSnapshot, rel: str) -> str:
    for row in snapshot.source_artifact_manifest or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("artifact_ref") or "").replace("\\", "/") == rel:
            return _normal_digest(row.get("sha256"))
    return ""


def _payload_for_verified_path(path: Path) -> tuple[Any, str]:
    if path.suffix.lower() != ".json":
        return None, ""
    payload = json_payload(path)
    if payload is None:
        return None, "unreadable_json_artifact"
    return payload, ""


def _missing(
    *,
    role: str,
    source_schema: str,
    expected_refs: tuple[str, ...],
    reason: str = "",
) -> ResolvedAppsRgArtifact:
    return ResolvedAppsRgArtifact(
        artifact_role=role,
        resolution_source="missing",
        source_artifact_schema=source_schema,
        expected_refs=expected_refs,
        failure_reason=reason,
    )


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
    eval_root_text = str(planned.get("__eval_artifact_root__") or "").strip()
    emission_complete = planned.get("__emission_complete__") is True
    if planned_value not in (None, "", [], {}) and eval_root_text and emission_complete:
        eval_root = Path(eval_root_text).resolve()
        invalid_reason = "planned_eval_artifact_not_emitted"
        for value in as_list(planned_value):
            candidate = _contained_path(str(value), eval_root)
            if candidate is None:
                invalid_reason = "planned_eval_artifact_outside_eval_root"
                continue
            if not candidate.is_file():
                continue
            payload, payload_error = _payload_for_verified_path(candidate)
            if payload_error:
                invalid_reason = payload_error
                continue
            digest = path_digest(candidate)
            if not digest:
                invalid_reason = "planned_eval_artifact_digest_unavailable"
                continue
            return ResolvedAppsRgArtifact(
                artifact_role=role,
                artifact_ref=candidate.as_posix(),
                evidence_ref=candidate.relative_to(eval_root).as_posix(),
                evidence_digest=digest,
                payload=payload,
                resolution_source="emitted_eval_artifact",
                source_artifact_schema=source_schema,
                expected_refs=expected_refs,
                byte_length=candidate.stat().st_size,
            )
        if role in _EVAL_OUTPUT_ROLES:
            return _missing(
                role=role,
                source_schema=source_schema,
                expected_refs=expected_refs,
                reason=invalid_reason,
            )
    elif role in _EVAL_OUTPUT_ROLES:
        return _missing(
            role=role,
            source_schema=source_schema,
            expected_refs=expected_refs,
            reason=(
                "eval_emission_not_complete"
                if not emission_complete
                else "eval_artifact_root_or_emitted_artifact_missing"
            ),
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
            return _missing(
                role=role,
                source_schema=source_schema,
                expected_refs=expected_refs,
                reason="snapshot_artifact_index_missing_ref",
            )
        if not snapshot.run_root:
            return _missing(
                role=role,
                source_schema=source_schema,
                expected_refs=expected_refs,
                reason="snapshot_artifact_index_missing_source_root",
            )
        root = Path(snapshot.run_root).resolve()
        candidate = _contained_path(artifact_ref, root)
        if candidate is None:
            return _missing(
                role=role,
                source_schema=source_schema,
                expected_refs=expected_refs,
                reason="snapshot_artifact_index_outside_source_root",
            )
        if not candidate.is_file():
            return _missing(
                role=role,
                source_schema=source_schema,
                expected_refs=expected_refs,
                reason="snapshot_artifact_index_file_missing",
            )
        rel = candidate.relative_to(root).as_posix()
        expected_digest = ""
        if isinstance(first, dict):
            expected_digest = _normal_digest(first.get("evidence_digest") or first.get("sha256"))
        expected_digest = expected_digest or _manifest_digest(snapshot, rel)
        observed_digest = path_digest(candidate)
        if not expected_digest or not observed_digest or observed_digest != expected_digest:
            return _missing(
                role=role,
                source_schema=source_schema,
                expected_refs=expected_refs,
                reason="snapshot_artifact_index_digest_mismatch_or_missing",
            )
        payload, payload_error = _payload_for_verified_path(candidate)
        if payload_error:
            return _missing(
                role=role,
                source_schema=source_schema,
                expected_refs=expected_refs,
                reason=payload_error,
            )
        return ResolvedAppsRgArtifact(
            artifact_role=role,
            artifact_ref=candidate.as_posix(),
            evidence_ref=rel,
            evidence_digest=observed_digest,
            payload=payload,
            resolution_source="snapshot_artifact_index",
            source_artifact_schema=source_schema,
            expected_refs=expected_refs,
            byte_length=candidate.stat().st_size,
        )

    root = Path(snapshot.run_root).resolve() if snapshot.run_root else None
    if root is not None:
        for rel in expected_refs:
            candidate = _contained_path(rel, root)
            if candidate is None:
                continue
            if candidate.is_file():
                observed_digest = path_digest(candidate)
                expected_digest = _manifest_digest(snapshot, rel)
                if snapshot.source_artifact_manifest and (
                    not expected_digest or observed_digest != expected_digest
                ):
                    return _missing(
                        role=role,
                        source_schema=source_schema,
                        expected_refs=expected_refs,
                        reason="source_manifest_digest_mismatch_or_missing",
                    )
                payload, payload_error = _payload_for_verified_path(candidate)
                if payload_error:
                    return _missing(
                        role=role,
                        source_schema=source_schema,
                        expected_refs=expected_refs,
                        reason=payload_error,
                    )
                return ResolvedAppsRgArtifact(
                    artifact_role=role,
                    artifact_ref=candidate.as_posix(),
                    evidence_ref=rel,
                    evidence_digest=observed_digest,
                    payload=payload,
                    resolution_source="run_root_file",
                    source_artifact_schema=source_schema,
                    expected_refs=expected_refs,
                    byte_length=candidate.stat().st_size,
                )

    return _missing(
        role=role,
        source_schema=source_schema,
        expected_refs=expected_refs,
    )
