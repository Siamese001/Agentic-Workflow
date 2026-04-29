"""Validate that an apps_rg run exercises the full v33 architecture spine.

Captures every `adg.*` DEBUG emission from `lifecycle_trace_contract._emit_*`
during a generate_resume run, aggregates them by layer + edge kind, and
produces a coverage matrix mapping the user's requested spine stages
(U0 -> L1 -> L0 -> C0/PA -> L3 -> L2 + healing -> metrics + exit ->
meta-learning bus -> L4 -> L5 -> runtime gates) to actual runtime evidence.

Usage:
    python apps_rg/scripts/validate_spine_coverage.py
"""
from __future__ import annotations

import asyncio
import logging
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import json

# ─── Capture handler ─────────────────────────────────────────────────────────


class AdgEmissionCapture(logging.Handler):
    """Capture every record emitted on any logger whose name starts with adg."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.records: list[dict] = []
        # Match LayerSegment emitted in the formatted message body, e.g.:
        # "records_execution_trace root_trace_id=... layer=L3_ORCHESTRATION op=..."
        self._layer_re = re.compile(r"layer=(L[0-6]_[A-Z]+|U0_[A-Z]+|C0_[A-Z]+|PA_[A-Z]+)")
        # ALSO catch LayerSegment passed as segment positional arg (rare)
        self._segment_re = re.compile(r"\b(L[0-6]_[A-Z]+|L[0-6]_REASONING|L[0-6]_ROUTING|L[0-6]_EXECUTION|L[0-6]_ORCHESTRATION|L[0-6]_STATE|L[0-6]_POLICY|L[0-6]_OBSERVABILITY)\b")

    def emit(self, record: logging.LogRecord) -> None:
        if not record.name.startswith("adg."):
            return
        msg = record.getMessage()
        edge_kind = record.name[len("adg."):]  # e.g. "records_execution_trace"
        # Extract layer hint from message body
        layer = None
        m = self._layer_re.search(msg)
        if m:
            layer = m.group(1)
        else:
            m2 = self._segment_re.search(msg)
            if m2:
                layer = m2.group(1)
        self.records.append({
            "logger": record.name,
            "edge_kind": edge_kind,
            "layer_hint": layer,
            "message": msg,
            "module": record.module,
        })


# ─── Spine stage taxonomy ────────────────────────────────────────────────────
# Maps each stage in the user's request to the edge-kinds that PROVE it ran.
# Source of truth: lifecycle_trace_contract.py emitter functions.

SPINE_STAGES: dict[str, dict] = {
    "U0_input_intake": {
        "description": "User input received, validated, normalized",
        "edge_kinds": [
            "validates_request",
            "captures_user_intent",
            "transcripts_response",
            "captures_execution_output",
        ],
    },
    "L1_reasoning_planning": {
        "description": "Cognition layer: intent → plan",
        "edge_kinds": [
            "records_execution_trace",
            "reads_policy_state",
            "applies_guardrail",
            "snapshots_state",
        ],
        "layer_match": "L1_REASONING",
    },
    "L0_routing": {
        "description": "Provider/agent/tool selection",
        "edge_kinds": [
            "routes_through",
            "routes_to_agent",
            "routes_to_capability",
            "validates_capability",
            "checks_agent_registry",
            "validates_agent_capability",
        ],
        "layer_match": "L0_ROUTING",
    },
    "C0_PA_context_plan_action": {
        "description": "Context engineering / plan-action binding",
        "edge_kinds": [
            "reads_l4_surface",
            "receives_policy_hash",
            "dispatches_execution_plan",
            "authorize_and_execute",
            "gated_by_confidence",
        ],
    },
    "L3_orchestration": {
        "description": "Multi-agent / workflow orchestration (if needed)",
        "edge_kinds": [
            "orchestrates_workflow",
            "dispatches_agent",
            "coordinates_agents",
            "agent_executes_agent",
            "l3_reads_l4_surface",
            "records_workflow_lineage",
        ],
        "layer_match": "L3_ORCHESTRATION",
        "optional": True,
    },
    "L2_execution_with_healing": {
        "description": "Tool/agent execution + healing if failures",
        "edge_kinds": [
            "records_tool_invocation",
            "captures_execution_output",
            "dispatches_healing_run",
            "records_healing_outcome",
            "escalates_failure",
        ],
        "layer_match": "L2_EXECUTION",
    },
    "metrics_and_exit_criteria": {
        "description": "Evaluation metrics + exit gate decisions",
        "edge_kinds": [
            "captures_evaluation_metric",
            "invokes_evaluation",
            "emits_metric_event",
            "captures_pattern",
            "records_validation_outcome",
        ],
    },
    "meta_learning_bus_feedback": {
        "description": "Meta-learning feedback bus updates",
        "edge_kinds": [
            "feeds_meta_learning",
            "updates_meta_learning_state",
            "improves_agent_policy",
            "stores_embedding",
            "links_execution_to_snapshot",
        ],
    },
    "L4_state_updates": {
        "description": "UWG / canonical state writes",
        "edge_kinds": [
            "writes_via_uwg",
            "blocks_direct_write",
            "claims_write_lock",
            "syncs_l4_telemetry",
            "materializes_read_view",
            "refreshes_retrieval_surface",
            "swaps_version_alias",
            "execution_terminates_at_uwg",
        ],
        "layer_match": "L4_STATE",
    },
    "L5_safety_policy": {
        "description": "Safety / policy / HITL gates",
        "edge_kinds": [
            "applies_guardrail",
            "verifies_policy",
            "verifies_boundary",
            "escalates_to_human",
            "hard_fails_untranscripted",
            "l5_reads_l4_surface",
        ],
        "layer_match": "L5_POLICY",
    },
    "runtime_gates_observability": {
        "description": "Runtime gates + L6 observability",
        "edge_kinds": [
            "records_telemetry_event",
            "captures_runtime_anomaly",
            "l6_ingests_l4_trace",
            "signs_execution_trace",
            "emits_replay_key",
            "emits_determinism_digest",
        ],
        "layer_match": "L6_OBSERVABILITY",
    },
}


def install_capture() -> AdgEmissionCapture:
    """Attach capture handler to root and elevate adg.* loggers to DEBUG."""
    handler = AdgEmissionCapture()
    root = logging.getLogger()
    root.addHandler(handler)
    # Set DEBUG level on every adg.* logger that already exists, plus the
    # parent "adg" logger so newly created sub-loggers inherit it.
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name.startswith("adg"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    logging.getLogger("adg").setLevel(logging.DEBUG)
    return handler


def aggregate(records: list[dict]) -> dict:
    """Aggregate captured records: counts by edge_kind, by layer."""
    by_edge: Counter = Counter(r["edge_kind"] for r in records)
    by_layer: Counter = Counter(r["layer_hint"] for r in records if r["layer_hint"])
    by_module: Counter = Counter(r["module"] for r in records)
    return {
        "total_emissions": len(records),
        "unique_edge_kinds": len(by_edge),
        "unique_layers": len(by_layer),
        "by_edge_kind": dict(by_edge.most_common()),
        "by_layer": dict(by_layer.most_common()),
        "by_module_top20": dict(by_module.most_common(20)),
    }


def stage_coverage(records: list[dict]) -> dict[str, dict]:
    """Map each spine stage to actual runtime evidence."""
    edge_counts: Counter = Counter(r["edge_kind"] for r in records)
    layer_counts: Counter = Counter(r["layer_hint"] for r in records if r["layer_hint"])
    out: dict[str, dict] = {}
    for stage_id, spec in SPINE_STAGES.items():
        edge_hits = {ek: edge_counts.get(ek, 0) for ek in spec["edge_kinds"]}
        edge_hits_nonzero = {k: v for k, v in edge_hits.items() if v > 0}
        layer_hits = (
            layer_counts.get(spec["layer_match"], 0)
            if spec.get("layer_match")
            else None
        )
        # A stage is "covered" if at least one edge-kind fired OR (when a
        # layer_match is defined) the layer was tagged on >= 1 emission.
        covered = bool(edge_hits_nonzero) or (layer_hits is not None and layer_hits > 0)
        out[stage_id] = {
            "description": spec["description"],
            "covered": covered,
            "optional": spec.get("optional", False),
            "edge_kinds_observed": edge_hits_nonzero,
            "edge_kinds_missing": [ek for ek in spec["edge_kinds"] if ek not in edge_hits_nonzero],
            "layer_match_count": layer_hits,
        }
    return out


async def run_apps_rg_main():
    """Invoke generate_resume.main() inline so emissions are captured."""
    from apps_rg.scripts.generate_resume import main  # noqa: PLC0415

    await main()


def main() -> int:
    capture = install_capture()
    print("Spine Validator — capture installed, running apps_rg.scripts.generate_resume...")
    try:
        asyncio.run(run_apps_rg_main())
    except SystemExit:
        pass
    print(f"Captured {len(capture.records)} adg.* DEBUG emissions")

    summary = aggregate(capture.records)
    coverage = stage_coverage(capture.records)

    # Console report
    print("\n" + "=" * 72)
    print("V33 SPINE COVERAGE REPORT — apps_rg run")
    print("=" * 72)
    print(f"Total adg.* emissions   : {summary['total_emissions']}")
    print(f"Unique edge kinds fired : {summary['unique_edge_kinds']}")
    print(f"Unique layers tagged    : {summary['unique_layers']}")
    print(f"By layer                : {summary['by_layer']}")
    print()
    print(f"{'Stage':<40} {'Cov':<6} {'Hits':<6} {'Layer Match':<12}")
    print("-" * 72)
    for stage_id, info in coverage.items():
        cov = "OK" if info["covered"] else ("opt" if info["optional"] else "MISS")
        hits = sum(info["edge_kinds_observed"].values())
        lm = info["layer_match_count"]
        lm_str = str(lm) if lm is not None else "-"
        print(f"{stage_id:<40} {cov:<6} {hits:<6} {lm_str:<12}")
    print()

    # Top 15 edge kinds for context
    print("Top 15 edge kinds by emission count:")
    for ek, c in list(summary["by_edge_kind"].items())[:15]:
        print(f"  {ek:<45} {c}")
    print()

    # Failures
    missing_required = [
        sid for sid, info in coverage.items()
        if not info["covered"] and not info["optional"]
    ]
    print(f"Missing required stages : {missing_required if missing_required else 'NONE'}")
    print()

    # Persist JSON report
    report = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "summary": summary,
        "coverage": coverage,
        "missing_required_stages": missing_required,
    }
    out_path = Path(__file__).parent / "spine_coverage_report.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"Report written: {out_path}")
    return 0 if not missing_required else 1


if __name__ == "__main__":
    raise SystemExit(main())
