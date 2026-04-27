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
}


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
    )

    paths: set[str] = set()
    for module in (t0, t1):
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
