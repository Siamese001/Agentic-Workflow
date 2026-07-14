"""Independent apps_eval/L6 binding over persisted completed-run evidence.

This module intentionally does not manufacture L6 observations from apps_eval
rows.  It binds an immutable L6 observation set to independently emitted
apps_eval ScorecardRows at the shared compound grain.  The result is post-run,
read-only, and future-run-only.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from agentic_core.L6_observability.shadow_eval.grain_parity import (
    L6_APPS_EVAL_COVERAGE_JOIN_KEY,
)
from agentic_core.L6_observability.shadow_eval.microsteps import (
    EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF,
    EVIDENCE_CLASS_CONTRACT_ONLY_ADVISORY,
)

INDEPENDENT_PARITY_SCHEMA_VERSION = "agentic_core.l6_independent_apps_eval_parity.v2"
SEALED_APPS_RG_OBSERVATION_ORIGIN = "sealed_apps_rg_artifacts"


def _canonical_digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _row_key(row: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(str(row.get(field) or "") for field in L6_APPS_EVAL_COVERAGE_JOIN_KEY)


def _key_payload(key: tuple[str, ...]) -> dict[str, str]:
    return dict(zip(L6_APPS_EVAL_COVERAGE_JOIN_KEY, key, strict=True))


def _key_label(key: tuple[str, ...]) -> str:
    return "|".join(key)


def _malformed(rows: Iterable[Mapping[str, Any]], *, side: str) -> list[dict[str, str]]:
    malformed: list[dict[str, str]] = []
    for row in rows:
        key = _row_key(row)
        missing = [
            field
            for field, value in zip(L6_APPS_EVAL_COVERAGE_JOIN_KEY, key, strict=True)
            if field != "lane_id" and not value
        ]
        if missing:
            malformed.append(
                {
                    **_key_payload(key),
                    "side": side,
                    "missing_fields": ",".join(missing),
                }
            )
    return malformed


def _duplicates(rows: Iterable[Mapping[str, Any]], *, side: str) -> list[dict[str, Any]]:
    keys = [_row_key(row) for row in rows]
    counts = Counter(keys)
    return [
        {**_key_payload(key), "side": side, "count": count}
        for key, count in sorted(counts.items(), key=lambda item: _key_label(item[0]))
        if count > 1
    ]


def _first_by_key(rows: Iterable[Mapping[str, Any]]) -> dict[tuple[str, ...], dict[str, Any]]:
    result: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in rows:
        result.setdefault(_row_key(row), dict(row))
    return result


def _normal_ref(
    value: Any,
    *,
    source_run_root: str = "",
    repository_root: str = "",
) -> str:
    """Return one source-run-relative reference or an empty invalid marker.

    Apps Eval persists both an absolute ``artifact_ref`` and a source-run
    relative ``evidence_ref``.  L6 persists repository-relative refs.  A bound
    proof must compare one namespace, so both forms are resolved against the
    sealed source-run root before comparison.  When no root is supplied, only
    already-relative, traversal-free refs are accepted.
    """

    text = str(value or "").strip().replace("\\", "/")
    if not text or "://" in text:
        return ""

    raw = Path(text)
    root_text = str(source_run_root or "").strip()
    if not root_text:
        if raw.is_absolute() or ".." in PurePosixPath(text).parts:
            return ""
        return PurePosixPath(text).as_posix().removeprefix("./")

    source_root = Path(root_text).resolve()
    candidates: list[Path]
    if raw.is_absolute():
        candidates = [raw.resolve()]
    else:
        candidates = []
        repo_text = str(repository_root or "").strip()
        if repo_text:
            candidates.append((Path(repo_text).resolve() / raw).resolve())
        candidates.append((source_root / raw).resolve())

    for candidate in candidates:
        try:
            return candidate.relative_to(source_root).as_posix()
        except ValueError:
            continue
    return ""


def _normal_sha256(value: Any) -> str:
    """Normalize legacy bare SHA-256 values to the canonical prefixed form."""

    text = str(value or "").strip().lower()
    raw = text.removeprefix("sha256:")
    if len(raw) != 64:
        return ""
    try:
        int(raw, 16)
    except ValueError:
        return ""
    return f"sha256:{raw}"


_DIGEST_IDENTITY_FIELDS = frozenset(
    {"microstep_contract_digest", "registry_digest", "snapshot_digest"}
)


def _normal_identity_value(field: str, value: Any) -> str:
    if field in _DIGEST_IDENTITY_FIELDS:
        return _normal_sha256(value)
    return str(value or "").strip()


def _observed_eval_verdict(row: Mapping[str, Any]) -> str | None:
    verdict = str(row.get("eval_verdict_seen") or "").upper()
    if verdict in {"", "UNKNOWN", "NOT_RUN"}:
        return None
    return verdict


def _authority_mismatch(rows: Iterable[Mapping[str, Any]]) -> bool:
    for row in rows:
        if row.get("current_run_mutation_assertion") is not False:
            return True
        if row.get("current_run_mutated") is True:
            return True
        if row.get("l4_write_assertion") is not False:
            return True
        if row.get("direct_l4_write_assertion") is True or row.get("direct_l4_write_attempted") is True:
            return True
        if row.get("durable_write_assertion") is True or row.get("durable_write_attempted") is True:
            return True
        if row.get("future_run_only") is False or row.get("future_run_only_assertion") is False:
            return True
    return False


def build_independent_apps_eval_parity(
    *,
    run_id: str,
    runtime_exhaust_bundle_id: str,
    microstep_contract_digest: str,
    apps_eval_scorecard_ref: str,
    l6_observation_ref: str,
    apps_eval_rows: Iterable[Mapping[str, Any]],
    l6_observations: Iterable[Mapping[str, Any]],
    observation_origin: str,
    expected_observation_bundle_id: str = "",
    parent_run_id: str = "",
    child_run_id: str = "",
    section_attempt_id: str = "",
    eval_record_id: str = "",
    snapshot_digest: str = "",
    registry_digest: str = "",
    source_run_root: str = "",
    repository_root: str = "",
    compare_artifact_digests: bool = True,
) -> dict[str, Any]:
    """Bind independent persisted observations to required apps_eval rows.

    Persisted contract observations may have ``eval_verdict_seen=NOT_RUN``.  In
    that case this receipt proves immutable grain/source binding and records an
    external verdict binding instead of pretending L6 independently graded the
    row.  When L6 did record a concrete verdict, mismatches fail closed.
    """

    eval_rows = [dict(row) for row in apps_eval_rows if row.get("required", True)]
    obs_rows = [
        dict(row)
        for row in l6_observations
        if row.get("required", True) and not row.get("orphan_observation")
    ]

    malformed = _malformed(eval_rows, side="apps_eval") + _malformed(obs_rows, side="l6")
    duplicates = _duplicates(eval_rows, side="apps_eval") + _duplicates(obs_rows, side="l6")
    eval_by_key = _first_by_key(eval_rows)
    obs_by_key = _first_by_key(obs_rows)

    eval_keys = set(eval_by_key)
    obs_keys = set(obs_by_key)
    missing_in_l6 = [_key_payload(key) for key in sorted(eval_keys - obs_keys, key=_key_label)]
    unbound_l6 = [_key_payload(key) for key in sorted(obs_keys - eval_keys, key=_key_label)]

    verdict_mismatches: list[dict[str, Any]] = []
    verdict_bindings: list[dict[str, Any]] = []
    source_ref_mismatches: list[dict[str, Any]] = []
    digest_mismatches: list[dict[str, Any]] = []

    for key in sorted(eval_keys & obs_keys, key=_key_label):
        eval_row = eval_by_key[key]
        obs_row = obs_by_key[key]
        eval_verdict = str(eval_row.get("verdict") or "UNKNOWN").upper()
        observed_verdict = _observed_eval_verdict(obs_row)
        if observed_verdict is None:
            verdict_bindings.append(
                {
                    **_key_payload(key),
                    "apps_eval_verdict": eval_verdict,
                    "binding_mode": "external_eval_bound_to_immutable_observation",
                }
            )
        elif observed_verdict != eval_verdict:
            verdict_mismatches.append(
                {
                    **_key_payload(key),
                    "apps_eval_verdict": eval_verdict,
                    "l6_eval_verdict_seen": observed_verdict,
                }
            )

        eval_evidence_ref = eval_row.get("evidence_ref")
        eval_artifact_ref = eval_row.get("artifact_ref")
        obs_ref = obs_row.get("source_ref")
        normal_eval_evidence_ref = _normal_ref(
            eval_evidence_ref,
            source_run_root=source_run_root,
            repository_root=repository_root,
        )
        normal_eval_artifact_ref = _normal_ref(
            eval_artifact_ref,
            source_run_root=source_run_root,
            repository_root=repository_root,
        )
        normal_eval_ref = normal_eval_evidence_ref or normal_eval_artifact_ref
        normal_obs_ref = _normal_ref(
            obs_ref,
            source_run_root=source_run_root,
            repository_root=repository_root,
        )
        if eval_evidence_ref and eval_artifact_ref and (
            not normal_eval_evidence_ref
            or not normal_eval_artifact_ref
            or normal_eval_evidence_ref != normal_eval_artifact_ref
        ):
            source_ref_mismatches.append(
                {
                    **_key_payload(key),
                    "apps_eval_ref": normal_eval_evidence_ref,
                    "apps_eval_artifact_ref": normal_eval_artifact_ref,
                    "l6_source_ref": normal_obs_ref,
                    "reason": "apps_eval_ref_alias_mismatch",
                }
            )
        if not normal_eval_ref or not normal_obs_ref or normal_eval_ref != normal_obs_ref:
            source_ref_mismatches.append(
                {
                    **_key_payload(key),
                    "apps_eval_ref": normal_eval_ref,
                    "l6_source_ref": normal_obs_ref,
                    "reason": (
                        "missing_or_invalid_relative_ref"
                        if not normal_eval_ref or not normal_obs_ref
                        else "relative_ref_mismatch"
                    ),
                }
            )

        # Byte-digest parity is mandatory for independent proof.  The legacy
        # flag is retained only for call-site compatibility and can no longer
        # weaken this security boundary.
        eval_digest = _normal_sha256(eval_row.get("evidence_digest"))
        obs_digest = _normal_sha256(obs_row.get("artifact_digest"))
        if not eval_digest or not obs_digest or eval_digest != obs_digest:
            digest_mismatches.append(
                {
                    **_key_payload(key),
                    "apps_eval_digest": eval_digest,
                    "l6_artifact_digest": obs_digest,
                    "reason": (
                        "missing_or_invalid_sha256"
                        if not eval_digest or not obs_digest
                        else "sha256_mismatch"
                    ),
                }
            )

    bundle_mismatches: list[dict[str, str]] = []
    expected_bundle = expected_observation_bundle_id or runtime_exhaust_bundle_id
    for row in obs_rows:
        observed_bundle = str(row.get("runtime_exhaust_bundle_id") or "")
        if not expected_bundle or not observed_bundle or observed_bundle != expected_bundle:
            bundle_mismatches.append(
                {
                    "microstep_id": str(row.get("microstep_id") or ""),
                    "expected_runtime_exhaust_bundle_id": expected_bundle,
                    "observed_runtime_exhaust_bundle_id": observed_bundle,
                    "reason": (
                        "missing_bundle_identity"
                        if not expected_bundle or not observed_bundle
                        else "bundle_identity_mismatch"
                    ),
                }
            )

    row_identity_mismatches: list[dict[str, Any]] = []
    expected_common_identity = {
        "parent_run_id": parent_run_id,
        "child_run_id": child_run_id,
        "section_attempt_id": section_attempt_id,
        "runtime_exhaust_bundle_id": runtime_exhaust_bundle_id,
        "microstep_contract_digest": microstep_contract_digest,
        "registry_digest": registry_digest,
    }
    expected_eval_identity = {
        **expected_common_identity,
        "run_id": run_id,
        "eval_record_id": eval_record_id,
        "snapshot_digest": snapshot_digest,
    }
    for side, rows, expected in (
        ("apps_eval", eval_rows, expected_eval_identity),
        ("l6", obs_rows, expected_common_identity),
    ):
        for row in rows:
            for field, wanted in expected.items():
                normalized_wanted = _normal_identity_value(field, wanted)
                observed = _normal_identity_value(field, row.get(field))
                if not normalized_wanted or not observed or observed != normalized_wanted:
                    row_identity_mismatches.append(
                        {
                            "side": side,
                            "microstep_id": str(row.get("microstep_id") or ""),
                            "field": field,
                            "expected": normalized_wanted,
                            "observed": observed,
                            "reason": (
                                "missing_identity"
                                if not normalized_wanted or not observed
                                else "identity_mismatch"
                            ),
                        }
                    )

    normalized_microstep_digest = _normal_sha256(microstep_contract_digest)
    normalized_registry_digest = _normal_sha256(registry_digest)
    normalized_snapshot_digest = _normal_sha256(snapshot_digest)
    top_level_identity_mismatches: list[dict[str, str]] = []
    if run_id and eval_record_id and run_id != eval_record_id:
        top_level_identity_mismatches.append(
            {
                "field": "run_id/eval_record_id",
                "expected": eval_record_id,
                "observed": run_id,
            }
        )
    if expected_observation_bundle_id and (
        expected_observation_bundle_id != runtime_exhaust_bundle_id
    ):
        top_level_identity_mismatches.append(
            {
                "field": "runtime_exhaust_bundle_id",
                "expected": expected_observation_bundle_id,
                "observed": runtime_exhaust_bundle_id,
            }
        )
    if (
        normalized_microstep_digest
        and normalized_registry_digest
        and normalized_microstep_digest != normalized_registry_digest
    ):
        top_level_identity_mismatches.append(
            {
                "field": "microstep_contract_digest/registry_digest",
                "expected": normalized_registry_digest,
                "observed": normalized_microstep_digest,
            }
        )

    identity_gaps = sorted(
        name
        for name, value in {
            "run_id": run_id,
            "runtime_exhaust_bundle_id": runtime_exhaust_bundle_id,
            "microstep_contract_digest": normalized_microstep_digest,
            "registry_digest": normalized_registry_digest,
            "apps_eval_scorecard_ref": str(apps_eval_scorecard_ref or "").strip(),
            "l6_observation_ref": str(l6_observation_ref or "").strip(),
            "parent_run_id": parent_run_id,
            "child_run_id": child_run_id,
            "section_attempt_id": section_attempt_id,
            "eval_record_id": eval_record_id,
            "snapshot_digest": normalized_snapshot_digest,
        }.items()
        if not str(value or "").strip()
    )

    authority_mismatch = _authority_mismatch(obs_rows)
    independent_origin = observation_origin == SEALED_APPS_RG_OBSERVATION_ORIGIN
    blocking = any(
        (
            malformed,
            duplicates,
            missing_in_l6,
            unbound_l6,
            verdict_mismatches,
            source_ref_mismatches,
            digest_mismatches,
            bundle_mismatches,
            row_identity_mismatches,
            top_level_identity_mismatches,
        )
    ) or bool(identity_gaps) or authority_mismatch or not independent_origin or not eval_rows or not obs_rows
    status = "FAIL" if blocking else "PASS"

    return {
        "schema_version": INDEPENDENT_PARITY_SCHEMA_VERSION,
        "run_id": run_id,
        "runtime_exhaust_bundle_id": runtime_exhaust_bundle_id,
        "microstep_contract_digest": normalized_microstep_digest,
        "registry_digest": normalized_registry_digest,
        "parent_run_id": parent_run_id,
        "child_run_id": child_run_id,
        "section_attempt_id": section_attempt_id,
        "eval_record_id": eval_record_id,
        "snapshot_digest": normalized_snapshot_digest,
        "source_run_root": str(source_run_root or "").strip(),
        "apps_eval_scorecard_ref": apps_eval_scorecard_ref,
        "l6_observation_ref": l6_observation_ref,
        "observation_origin": observation_origin,
        "independent_observations": independent_origin,
        "alignment_source": "independent_persisted_observations",
        "apps_eval_rows_bound": status == "PASS",
        "evidence_class": (
            EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF
            if status == "PASS"
            else EVIDENCE_CLASS_CONTRACT_ONLY_ADVISORY
        ),
        "coverage_join_key": list(L6_APPS_EVAL_COVERAGE_JOIN_KEY),
        "apps_eval_rows_seen": len(eval_rows),
        "l6_observation_rows_seen": len(obs_rows),
        "missing_in_l6": missing_in_l6,
        "unbound_l6_observations": unbound_l6,
        "duplicate_join_keys": duplicates,
        "malformed_join_keys": malformed,
        "verdict_mismatches": verdict_mismatches,
        "verdict_bindings": verdict_bindings,
        "source_ref_mismatches": source_ref_mismatches,
        "artifact_digest_mismatches": digest_mismatches,
        "runtime_exhaust_bundle_mismatches": bundle_mismatches,
        "row_identity_mismatches": row_identity_mismatches,
        "top_level_identity_mismatches": top_level_identity_mismatches,
        "identity_gaps": identity_gaps,
        "artifact_digest_comparison_required": True,
        "authority_mismatch": authority_mismatch,
        "grain_parity_status": status,
        "apps_eval_rows_digest": _canonical_digest(eval_rows),
        "l6_observations_digest": _canonical_digest(obs_rows),
        "projection_consistency_only": False,
        "current_run_mutation_assertion": False,
        "l4_write_assertion": False,
        "future_run_only": True,
    }


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"expected JSON object at {path}:{line_no}")
        rows.append(payload)
    return rows


def write_independent_parity(path: Path, payload: Mapping[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(payload), indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


__all__ = [
    "INDEPENDENT_PARITY_SCHEMA_VERSION",
    "SEALED_APPS_RG_OBSERVATION_ORIGIN",
    "build_independent_apps_eval_parity",
    "read_jsonl",
    "write_independent_parity",
]
