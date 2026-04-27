"""
Phase 6 -- deterministic replay engine.

Runs each scenario twice and compares the deterministic projection of the
two traces. Fields that MUST be byte-identical across replays are listed
in DETERMINISTIC_FIELDS (the spec's 12 hash/digest/id fields minus the
clock and uuid fields). Fields that ARE expected to differ live in
NONDETERMINISTIC_FIELDS.

Output:
  artifacts/runtime/requirements_proof/replay/replay_<scenario>_run_1.json
  artifacts/runtime/requirements_proof/replay/replay_<scenario>_run_2.json
  artifacts/runtime/requirements_proof/replay/replay_comparison.json

This is the FOUNDATIONAL replay-evidence layer. PROVEN status for a record
that depends on replay evidence requires:
  (a) the runtime stage emits the relevant span (Phase 5 contract)
  (b) the deterministic projection across two runs matches (this phase)
  (c) any anti-bypass negative for that span/attribute fails its mutator
      (Phase 7)

If any of (a/b/c) fail, status remains IMPLEMENTED_NOT_PROVEN.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


# Fields that the spec says are stable across replays of the same input.
# Hashes/digests/named-ids — derived from the (scenario, request) tuple,
# not from the wall clock.
DETERMINISTIC_FIELDS: Tuple[str, ...] = (
    "name",
    "route_id",
    "step_id",
    "gate_id",
    "policy_hash",
    "blueprint_hash",
    "replay_key",
    "contract_digest",
    "status",
    "reason_codes",
    "artifact_refs",
    "tokens_in",
    "tokens_out",
    "cost_usd",
)

# Fields that DO vary across replays. uuid + clock. Listed for completeness
# so the comparison report can show what was *expected* to differ.
NONDETERMINISTIC_FIELDS: Tuple[str, ...] = (
    "trace_id",
    "span_id",
    "parent_span_id",
    "request_id",
    "run_id",
    "start_unix_ns",
    "end_unix_ns",
    "latency_ms",
)


def _build_name_path(span: Dict[str, Any], by_id: Dict[str, Dict[str, Any]]) -> Tuple[str, ...]:
    """Walk parent chain by name to produce a uuid-free identifier."""
    out: List[str] = []
    cur: Dict[str, Any] | None = span
    safety = 0
    while cur is not None and safety < 64:
        out.append(cur["name"])
        parent_id = cur.get("parent_span_id", "")
        cur = by_id.get(parent_id) if parent_id else None
        safety += 1
    return tuple(reversed(out))


def deterministic_projection(trace: Dict[str, Any]) -> Dict[str, Any]:
    """Return the uuid/clock-stripped projection of a trace.

    Spans are keyed by their name-path from root (which is stable across
    replays because span names and the parent-graph are deterministic),
    not by their uuid. Within each name-path, the deterministic field
    values are extracted in canonical order.
    """
    by_id = {s["span_id"]: s for s in trace["spans"]}
    keyed: List[Tuple[Tuple[str, ...], Dict[str, Any]]] = []
    for s in trace["spans"]:
        path = _build_name_path(s, by_id)
        proj = {f: s.get(f) for f in DETERMINISTIC_FIELDS}
        keyed.append((path, proj))
    # Stable order by name-path; within a path the dict is already ordered
    # by DETERMINISTIC_FIELDS.
    keyed.sort(key=lambda kv: kv[0])
    return {
        "scenario": trace["scenario"],
        "span_count": trace["span_count"],
        "spans": [{"path": list(p), "fields": f} for p, f in keyed],
    }


def replay_digest(trace: Dict[str, Any]) -> str:
    """SHA-256 hex digest of the deterministic projection."""
    proj = deterministic_projection(trace)
    blob = json.dumps(proj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def run_replay_pair(scenario_name: str, scenario_fn) -> Dict[str, Any]:
    """Run one scenario twice, compare deterministic digests, build report.

    The two runs SHARE the scenario inputs (policy/blueprint/replay_key
    digests are derived from a static label inside the harness). They DIFFER
    only in clock and freshly-minted uuids. If the deterministic digest
    matches across runs, replay-determinism for that scenario is proven.
    """
    trace_a = scenario_fn().to_dict()
    trace_b = scenario_fn().to_dict()
    digest_a = replay_digest(trace_a)
    digest_b = replay_digest(trace_b)
    matches = digest_a == digest_b

    # Per-span field-level comparison so the report is auditable.
    proj_a = deterministic_projection(trace_a)["spans"]
    proj_b = deterministic_projection(trace_b)["spans"]
    span_diffs: List[Dict[str, Any]] = []
    if len(proj_a) != len(proj_b):
        span_diffs.append(
            {
                "issue": "span_count_mismatch",
                "run_1_count": len(proj_a),
                "run_2_count": len(proj_b),
            }
        )
    else:
        for left, right in zip(proj_a, proj_b):
            if left != right:
                span_diffs.append(
                    {
                        "issue": "span_field_drift",
                        "path": left["path"],
                        "run_1_fields": left["fields"],
                        "run_2_fields": right["fields"],
                    }
                )

    return {
        "scenario": scenario_name,
        "run_1": trace_a,
        "run_2": trace_b,
        "deterministic_digest_run_1": digest_a,
        "deterministic_digest_run_2": digest_b,
        "deterministic_match": matches,
        "fields_compared_deterministic": list(DETERMINISTIC_FIELDS),
        "fields_compared_nondeterministic": list(NONDETERMINISTIC_FIELDS),
        "span_diffs": span_diffs,
    }


def write_replay_artifacts(replay_dir: Path, scenario_name: str, replay_result: Dict[str, Any]) -> Dict[str, str]:
    """Persist a single scenario's replay-pair output."""
    replay_dir.mkdir(parents=True, exist_ok=True)
    p1 = replay_dir / f"replay_{scenario_name}_run_1.json"
    p2 = replay_dir / f"replay_{scenario_name}_run_2.json"
    p1.write_text(json.dumps(replay_result["run_1"], indent=2, ensure_ascii=False), encoding="utf-8")
    p2.write_text(json.dumps(replay_result["run_2"], indent=2, ensure_ascii=False), encoding="utf-8")
    return {"run_1": str(p1), "run_2": str(p2)}


def write_replay_comparison(replay_dir: Path, results: List[Dict[str, Any]]) -> Path:
    """Aggregate report covering all scenarios."""
    replay_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "all_scenarios_match": all(r["deterministic_match"] for r in results),
        "fields_compared_deterministic": list(DETERMINISTIC_FIELDS),
        "fields_compared_nondeterministic": list(NONDETERMINISTIC_FIELDS),
        "scenarios": [
            {
                "scenario": r["scenario"],
                "deterministic_match": r["deterministic_match"],
                "deterministic_digest_run_1": r["deterministic_digest_run_1"],
                "deterministic_digest_run_2": r["deterministic_digest_run_2"],
                "span_diffs": r["span_diffs"],
            }
            for r in results
        ],
    }
    out = replay_dir / "replay_comparison.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def run_full_replay_suite(scenario_fns, replay_dir: Path) -> Dict[str, Any]:
    """Top-level driver. Runs all scenarios pair-wise, writes every artifact,
    returns the aggregate summary."""
    results: List[Dict[str, Any]] = []
    paths: Dict[str, Dict[str, str]] = {}
    for name, fn in scenario_fns:
        result = run_replay_pair(name, fn)
        results.append(result)
        paths[name] = write_replay_artifacts(replay_dir, name, result)
    comparison_path = write_replay_comparison(replay_dir, results)
    return {
        "scenario_paths": paths,
        "comparison_path": str(comparison_path),
        "all_scenarios_match": all(r["deterministic_match"] for r in results),
        "per_scenario_match": {r["scenario"]: r["deterministic_match"] for r in results},
        "per_scenario_digests": {
            r["scenario"]: r["deterministic_digest_run_1"] for r in results
        },
    }
