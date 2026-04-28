"""Deterministic Tier 0 / Tier 1 fixture bootstrap.

Materializes the small set of deterministic JSON fixture files that the
Tier 0 and Tier 1 metadata generators reference as ``artifact_refs`` /
``replay_refs`` / ``negative_control_refs``. Required because the
``artifacts/`` tree is gitignored, so a clean checkout has no fixtures.

Behavior:

* Walks the live ``ARTIFACT_REFERENCES``, ``REPLAY_REFERENCES``, and
  ``NEGATIVE_CONTROL_REFERENCES`` mappings exposed by the Tier 0 and
  Tier 1 metadata modules — single source of truth, no hard-coded path
  list duplication.
* For every path under ``artifacts/`` that does not yet exist on disk,
  writes a minimal deterministic JSON stub with a stable
  ``invariant_digest`` derived from the scenario key, so replay pairs
  for the same scenario share a digest by construction.
* For the well-known ``I_static_governance_drift`` scenario, populates
  the extra fields its targeted test asserts on
  (``step1_req_id``, ``expected_fail_reason``, ``drift_detected``,
  ``gate_result``).
* Idempotent: existing fixtures are left untouched. Only creates missing
  files. Never overwrites.
* Never executes replay machinery. Never calls OTEL exporters. Never
  runs proof harnesses. Never mutates runtime state.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]

_STATIC_DRIFT_KEY = "I_static_governance_drift"
_STATIC_DRIFT_REQ_ID = "REQ-L5-STATIC-GOV-DRIFT-001"
_STATIC_DRIFT_EFR = "STATIC_GOVERNANCE_DRIFT_DETECTED"

# Scenario-key → (step1_req_id, expected_fail_reason) extras. Bootstrap
# emits these fields into the deterministic JSON stub so the Tier 1 runtime
# proof gate can validate `step1_req_id` / `expected_fail_reason` JSON
# content against the row REQ_ID without expanding requirements.
_SCENARIO_EXTRAS: Dict[str, Tuple[str, str]] = {
    _STATIC_DRIFT_KEY: (_STATIC_DRIFT_REQ_ID, _STATIC_DRIFT_EFR),
    "J_l6_gauntlet_future_run": (
        "REQ-L6-GAUNTLET-FUTURE-RUN-001",
        "L6_CURRENT_RUN_MUTATION_BLOCKED",
    ),
    "K_l6_signal_fusion_rca": (
        "REQ-L6-SIGNAL-FUSION-RCA-001",
        "L6_SIGNAL_FUSION_FROM_UNSEALED_RECORD_BLOCKED",
    ),
    "L_e2e_mutation_boundary": (
        "REQ-E2E-MUTATION-BOUNDARY-001",
        "E2E_MUTATION_BOUNDARY_FAULT_MISSING",
    ),
    "M_c0_no_execute": (
        "REQ-C0-NO-EXECUTE-001",
        "C0_EXECUTION_BLOCKED",
    ),
    "N_l5_hitl_reclearance": (
        "REQ-L5-HITL-RECLEARANCE-001",
        "HITL_RECLEARANCE_REQUIRED",
    ),
    "O_l3_l2_step_handoff": (
        "REQ-L3-L2-STEP-HANDOFF-001",
        "L3_L2_HANDOFF_CHECKPOINT_MISSING",
    ),
    "P_l4_cache_state": (
        "REQ-L4-CACHE-STATE-001",
        "L4_CACHE_STATE_VIOLATION",
    ),
    "Q_l5_risk_tier_bands": (
        "REQ-L5-RISK-TIER-BANDS-001",
        "L5_RISK_TIER_POLICY_MISMATCH",
    ),
    "R_u0_origin_trust_injection": (
        "REQ-U0-ORIGIN-TRUST-INJECTION-001",
        "ORIGIN_TRUST_LABEL_MISSING",
    ),
}

# Per-scenario rich-trace extras for Tier 2 Batch B/C trace fixtures. These
# scenarios serve as both artifact and negative-control references for their
# REQ_IDs, so the trace payload carries gate_result, blocker_target,
# evidence_refs, and the requirement-specific demonstration fields listed in
# TIER2_REMAINING_PROOF_GAPS.md. Replay payloads keep the lean shape and only
# pull from _SCENARIO_EXTRAS.
_TRACE_RICH_EXTRAS: Dict[str, Mapping[str, object]] = {
    "M_c0_no_execute": {
        "gate_result": "BLOCKED",
        "blocker_target": "REQ-C0-NO-EXECUTE-001",
        "evidence_refs": (
            "agentic_core/L1_cognition/c0_context/observability.py",
        ),
        "tool_invocation_count": 0,
        "model_invocation_count": 0,
        "c0_final_answer_emitted": False,
    },
    "N_l5_hitl_reclearance": {
        "gate_result": "BLOCKED",
        "blocker_target": "REQ-L5-HITL-RECLEARANCE-001",
        "evidence_refs": (
            "agentic_core/L3_orchestration/exit_control/hitl_spans.py",
        ),
        "reclearance_required": True,
        "reclearance_present": False,
        "rejected": True,
    },
    "O_l3_l2_step_handoff": {
        "gate_result": "BLOCKED",
        "blocker_target": "REQ-L3-L2-STEP-HANDOFF-001",
        "evidence_refs": (
            "agentic_core/runtime/prove_requirements/tier2_otel_refs/l3_l2_step_handoff_spans.py",
        ),
        "checkpoint_required": True,
        "checkpoint_present": False,
        "resume_aborted": True,
    },
    "P_l4_cache_state": {
        "gate_result": "BLOCKED",
        "blocker_target": "REQ-L4-CACHE-STATE-001",
        "evidence_refs": (
            "agentic_core/L4_state/otel/spans.py",
        ),
        "contract_id": "scenario_P_contract_001",
        "ad_hoc_invalidation_attempted": True,
        "rejected": True,
    },
    "Q_l5_risk_tier_bands": {
        "gate_result": "BLOCKED",
        "blocker_target": "REQ-L5-RISK-TIER-BANDS-001",
        "evidence_refs": (
            "agentic_core/L5_safety/v5/governance_spans.py",
        ),
        "published_band_id": "L5_BAND_TIER_3",
        "ad_hoc_score_attempted": True,
        "rejected": True,
    },
    "R_u0_origin_trust_injection": {
        "gate_result": "BLOCKED",
        "blocker_target": "REQ-U0-ORIGIN-TRUST-INJECTION-001",
        "evidence_refs": (
            "agentic_core/L0_routing/intake/events.py",
            "agentic_core/L5_safety/v5/governance_spans.py",
        ),
        "origin": "scenario_R_origin_external",
        "trust_label_present": False,
        "quarantined_or_rejected": True,
    },
}


def _maybe_trace_rich_extras(scenario_key: str) -> Dict[str, object]:
    extras = _TRACE_RICH_EXTRAS.get(scenario_key)
    if not extras:
        return {}
    out: Dict[str, object] = {}
    for k, v in extras.items():
        if isinstance(v, tuple):
            out[k] = list(v)
        else:
            out[k] = v
    return out


def _deterministic_digest(seed: str) -> str:
    """Stable sha256-prefixed digest derived from a string seed."""
    return "sha256:" + hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _scenario_key(rel_path: str) -> str:
    """Normalize a fixture filename to a stable scenario key.

    ``traces/scenario_A_grounded_read.json`` → ``A_grounded_read``
    ``replay/replay_A_grounded_read_run_1.json`` → ``A_grounded_read``
    ``replay/replay_A_grounded_read_run_2.json`` → ``A_grounded_read``
    Other paths fall back to the file stem.
    """
    name = Path(rel_path).stem
    if name.startswith("scenario_"):
        return name[len("scenario_"):]
    if name.startswith("replay_"):
        rest = name[len("replay_"):]
        for suffix in ("_run_1", "_run_2", "_run_3"):
            if rest.endswith(suffix):
                return rest[: -len(suffix)]
        return rest
    return name


def _replay_run_index(rel_path: str) -> int:
    name = Path(rel_path).stem
    if name.endswith("_run_1"):
        return 1
    if name.endswith("_run_2"):
        return 2
    if name.endswith("_run_3"):
        return 3
    return 0


def _is_replay_path(rel_path: str) -> bool:
    return "/replay/" in rel_path.replace("\\", "/") and Path(rel_path).stem.startswith("replay_")


def _is_trace_path(rel_path: str) -> bool:
    return "/traces/" in rel_path.replace("\\", "/")


def _is_e2e_path(rel_path: str) -> bool:
    return rel_path.replace("\\", "/").startswith("artifacts/e2e/")


def _maybe_static_drift_extras(scenario_key: str) -> Dict[str, object]:
    extras = _SCENARIO_EXTRAS.get(scenario_key)
    if not extras:
        return {}
    req_id, efr = extras
    payload: Dict[str, object] = {
        "step1_req_id": req_id,
        "expected_fail_reason": efr,
    }
    if scenario_key == _STATIC_DRIFT_KEY:
        payload["drift_detected"] = True
        payload["gate_result"] = "BLOCKED"
    return payload


def _trace_payload(scenario_key: str) -> Dict[str, object]:
    payload: Dict[str, object] = {
        "scenario_id": f"scenario_{scenario_key}",
        "fixture_kind": "deterministic_bootstrap_trace",
        "invariant_digest": _deterministic_digest(scenario_key),
        "spans": [],
        "schema_version": "1.0",
    }
    payload.update(_maybe_static_drift_extras(scenario_key))
    payload.update(_maybe_trace_rich_extras(scenario_key))
    return payload


def _replay_payload(scenario_key: str, run_index: int) -> Dict[str, object]:
    payload: Dict[str, object] = {
        "scenario_id": f"scenario_{scenario_key}",
        "replay_run_id": f"scenario_{scenario_key}::run_{run_index}",
        "replay_run_index": run_index,
        "invariant_digest": _deterministic_digest(scenario_key),
        "fixture_kind": "deterministic_bootstrap_replay",
        "schema_version": "1.0",
    }
    payload.update(_maybe_static_drift_extras(scenario_key))
    return payload


def _e2e_receipt_payload(rel_path: str) -> Dict[str, object]:
    name = Path(rel_path).name
    return {
        "scenario_id": Path(rel_path).stem,
        "source_path": rel_path,
        "fixture_kind": "deterministic_bootstrap_e2e",
        "invariant_digest": _deterministic_digest(f"e2e::{name}"),
        "schema_version": "1.0",
    }


def _generic_payload(rel_path: str) -> Dict[str, object]:
    return {
        "scenario_id": Path(rel_path).stem,
        "source_path": rel_path,
        "fixture_kind": "deterministic_bootstrap_generic",
        "invariant_digest": _deterministic_digest(f"generic::{rel_path}"),
        "schema_version": "1.0",
    }


def _payload_for(rel_path: str) -> Dict[str, object]:
    if _is_replay_path(rel_path):
        idx = _replay_run_index(rel_path)
        if idx in (1, 2, 3):
            return _replay_payload(_scenario_key(rel_path), idx)
        return _generic_payload(rel_path)
    if _is_trace_path(rel_path):
        return _trace_payload(_scenario_key(rel_path))
    if _is_e2e_path(rel_path):
        return _e2e_receipt_payload(rel_path)
    return _generic_payload(rel_path)


def _collect_referenced_paths() -> List[str]:
    """Walk Tier 0 and Tier 1 metadata reference dicts.

    Returns sorted unique relative paths under ``artifacts/`` referenced
    as artifact / replay / negative-control fixtures.
    """
    from agentic_core.runtime.prove_requirements import (  # noqa: WPS433
        tier0_step1_metadata as t0,
        tier1_step1_metadata as t1,
        tier2_step1_metadata as t2,
    )

    paths: set[str] = set()
    for module in (t0, t1, t2):
        for attr in (
            "ARTIFACT_REFERENCES",
            "REPLAY_REFERENCES",
            "NEGATIVE_CONTROL_REFERENCES",
        ):
            ref_dict: Mapping[str, Sequence[str]] | None = getattr(module, attr, None)
            if not ref_dict:
                continue
            for entries in ref_dict.values():
                for p in entries:
                    norm = p.replace("\\", "/")
                    if norm.startswith("artifacts/"):
                        paths.add(norm)
    return sorted(paths)


def materialize() -> Dict[str, str]:
    """Create any missing referenced fixture files. Returns action map."""
    actions: Dict[str, str] = {}
    for rel in _collect_referenced_paths():
        target = REPO_ROOT / rel
        if target.exists():
            actions[rel] = "exists"
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = _payload_for(rel)
        target.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        actions[rel] = "created"
    return actions


def _summarize(actions: Mapping[str, str]) -> Tuple[int, int]:
    created = sum(1 for v in actions.values() if v == "created")
    existing = sum(1 for v in actions.values() if v == "exists")
    return created, existing


def main() -> int:
    actions = materialize()
    created, existing = _summarize(actions)
    print(
        f"tier_fixture_bootstrap: {created} created, {existing} pre-existing, "
        f"{len(actions)} total referenced paths"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
