"""apps_eval/L6 microstep-grain parity checks.

This module compares required apps_eval ScorecardRows with L6 shadow
observations at the shared microstep join grain. It is read-only and produces
future-run-only observability evidence.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from agentic_core.L6_observability.shadow_eval.microsteps import (
    evidence_class_for_alignment_source,
)

L6_APPS_EVAL_GRAIN_PARITY_SCHEMA_VERSION = "agentic_core.l6_apps_eval_grain_parity.v1"
L6_APPS_EVAL_COVERAGE_JOIN_KEY = [
    "microstep_id",
    "stage_id",
    "lane_id",
    "gate_id",
    "artifact_role",
    "component_id",
    "subcomponent_id",
]
_WARN_ALIGNMENT_SOURCES = {"contract_only_pseudo_rows", "failure_terminal_no_apps_eval_rows"}


def _row_key(row: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(str(row.get(field) or "") for field in L6_APPS_EVAL_COVERAGE_JOIN_KEY)


def _key_payload(key: tuple[str, ...]) -> dict[str, str]:
    return dict(zip(L6_APPS_EVAL_COVERAGE_JOIN_KEY, key, strict=True))


def _key_label(key: tuple[str, ...]) -> str:
    return "|".join(key)


def _malformed_keys(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, str]]:
    malformed: list[dict[str, str]] = []
    for row in rows:
        key = _row_key(row)
        # lane_id can be empty for global/package rows; all other fields define
        # the scorecard/observation grain and must be present.
        missing = [
            field
            for field, value in zip(L6_APPS_EVAL_COVERAGE_JOIN_KEY, key, strict=True)
            if field != "lane_id" and not value
        ]
        if missing:
            payload = _key_payload(key)
            payload["missing_fields"] = ",".join(missing)
            malformed.append(payload)
    return malformed


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


def build_l6_apps_eval_grain_parity(
    *,
    run_id: str,
    runtime_exhaust_bundle_id: str,
    microstep_contract_digest: str,
    apps_eval_scorecard_ref: str,
    l6_observation_ref: str,
    apps_eval_rows: Iterable[Mapping[str, Any]],
    l6_observations: Iterable[Mapping[str, Any]],
    alignment_source: str,
) -> dict[str, Any]:
    """Compare required apps_eval rows and L6 observations at shared grain."""
    eval_rows = [dict(row) for row in apps_eval_rows if row.get("required", True)]
    obs_rows = [dict(row) for row in l6_observations if not row.get("orphan_observation")]
    eval_by_key = {_row_key(row): row for row in eval_rows}
    obs_by_key = {_row_key(row): row for row in obs_rows}
    malformed = _malformed_keys(eval_rows) + _malformed_keys(obs_rows)
    missing_in_l6 = [_key_payload(key) for key in sorted(set(eval_by_key) - set(obs_by_key), key=_key_label)]
    missing_in_apps_eval = [_key_payload(key) for key in sorted(set(obs_by_key) - set(eval_by_key), key=_key_label)]
    verdict_mismatches = []
    for key in sorted(set(eval_by_key) & set(obs_by_key), key=_key_label):
        eval_verdict = str(eval_by_key[key].get("verdict") or "UNKNOWN")
        seen_verdict = str(obs_by_key[key].get("eval_verdict_seen") or "UNKNOWN")
        if seen_verdict != eval_verdict:
            verdict_mismatches.append(
                {
                    **_key_payload(key),
                    "apps_eval_verdict": eval_verdict,
                    "l6_eval_verdict_seen": seen_verdict,
                }
            )

    apps_eval_rows_bound = alignment_source == "apps_eval_scorecard_rows"
    authority_mismatch = _authority_mismatch(obs_rows)
    unbound_extra_observations = missing_in_apps_eval and apps_eval_rows_bound
    if malformed or missing_in_l6 or unbound_extra_observations or verdict_mismatches or authority_mismatch:
        status = "FAIL"
    elif apps_eval_rows_bound:
        status = "PASS"
    elif alignment_source in _WARN_ALIGNMENT_SOURCES:
        status = "WARN"
    else:
        status = "FAIL"

    return {
        "schema_version": L6_APPS_EVAL_GRAIN_PARITY_SCHEMA_VERSION,
        "run_id": run_id,
        "runtime_exhaust_bundle_id": runtime_exhaust_bundle_id,
        "microstep_contract_digest": microstep_contract_digest,
        "apps_eval_scorecard_ref": apps_eval_scorecard_ref,
        "l6_observation_ref": l6_observation_ref,
        "alignment_source": alignment_source,
        "apps_eval_rows_bound": apps_eval_rows_bound,
        "evidence_class": evidence_class_for_alignment_source(alignment_source),
        "coverage_join_key": list(L6_APPS_EVAL_COVERAGE_JOIN_KEY),
        "rows_expected": len(eval_rows),
        "apps_eval_rows_seen": len(eval_rows),
        "l6_observation_rows_seen": len(obs_rows),
        "missing_in_l6": missing_in_l6,
        "missing_in_apps_eval": missing_in_apps_eval,
        "verdict_mismatches": verdict_mismatches,
        "malformed_join_keys": malformed,
        "authority_mismatch": authority_mismatch,
        "grain_parity_status": status,
        "current_run_mutation_assertion": False,
        "l4_write_assertion": False,
        "future_run_only": True,
    }


__all__ = [
    "L6_APPS_EVAL_COVERAGE_JOIN_KEY",
    "L6_APPS_EVAL_GRAIN_PARITY_SCHEMA_VERSION",
    "build_l6_apps_eval_grain_parity",
]
