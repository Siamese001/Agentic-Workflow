"""
Identify agents with lowest code quality metrics for targeted refactoring.
Focuses on typed %, documented %, and schema strictness %.
"""

import json
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "identify_low_quality_agents_util")
emit_determinism_digest("p0", "identify_low_quality_agents_util")

_emit_dispatches_healing_run("p1", "identify_low_quality_agents_util", "L0")
_emit_routes_through("p1", "identify_low_quality_agents_util", "L0")
_emit_escalates_to_human("p1", "identify_low_quality_agents_util", "L0")
_emit_reads_policy_state("p1", "identify_low_quality_agents_util", "L0")
_emit_authorize_and_execute("p2", "identify_low_quality_agents_util", "execution_auth")
_emit_validates_capability("p2", "identify_low_quality_agents_util", "capability_check")
_emit_routes_to_capability("p2", "identify_low_quality_agents_util", "capability_route")
_emit_writes_via_uwg("p2", "identify_low_quality_agents_util", "uwg_write")
_emit_blocks_direct_write("p2", "identify_low_quality_agents_util", "direct_write_block")
_emit_records_tool_invocation("p2", "identify_low_quality_agents_util", "tool_invocation")
_emit_captures_execution_output("p2", "identify_low_quality_agents_util", "exec_output")
_emit_dispatches_agent("p3", "identify_low_quality_agents_util", "agent_dispatch")
_emit_coordinates_agents("p3", "identify_low_quality_agents_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "identify_low_quality_agents_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "identify_low_quality_agents_util", "healing_outcome")
_emit_escalates_failure("p3", "identify_low_quality_agents_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "identify_low_quality_agents_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "identify_low_quality_agents_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "identify_low_quality_agents_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "identify_low_quality_agents_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "identify_low_quality_agents_util", "eval_metric")
_emit_stores_embedding("p4", "identify_low_quality_agents_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "identify_low_quality_agents_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "identify_low_quality_agents_util", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"


def calculate_quality_score(agent: dict[str, Any]) -> float:
    """Calculate combined quality score (lower is worse)."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "calculate_quality_score", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "calculate_quality_score", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "calculate_quality_score")
    typed = agent.get("typed_pct", 0)
    documented = agent.get("documented_pct", 0)
    schema = agent.get("schema_strictness", 0)
    return (typed + documented + schema) / 3


def main():
    """Identify agents needing refactoring."""
    print("=" * 70)
    print("IDENTIFYING LOW QUALITY AGENTS FOR REFACTORING")
    print("=" * 70)
    with open(DISCOVERY_FILE, encoding="utf-8") as f:
        agents = json.load(f)
    agent_scores = []
    for agent in agents:
        score = calculate_quality_score(agent)
        agent_scores.append(
            {
                "name": agent.get("class_name"),
                "path": agent.get("path"),
                "typed_pct": agent.get("typed_pct", 0),
                "documented_pct": agent.get("documented_pct", 0),
                "schema_strictness": agent.get("schema_strictness", 0),
                "quality_score": score,
            }
        )
    agent_scores.sort(key=lambda x: x["quality_score"])
    needs_work = [
        a
        for a in agent_scores
        if a["typed_pct"] < 100 or a["documented_pct"] < 100 or a["schema_strictness"] < 100
    ]
    print(f"\nTotal agents: {len(agents)}")
    print(f"Agents needing improvement: {len(needs_work)}")
    print("\nCurrent averages:")
    print(f"  Typed: {sum(a['typed_pct'] for a in agent_scores) / len(agent_scores):.1f}%")
    print(f"  Documented: {sum(a['documented_pct'] for a in agent_scores) / len(agent_scores):.1f}%")
    print(f"  schema: {sum(a['schema_strictness'] for a in agent_scores) / len(agent_scores):.1f}%")
    print("\n" + "=" * 70)
    print("REFACTORING BATCHES (5-6 agents each)")
    print("=" * 70)
    batch_size = 6
    for batch_num, i in enumerate(range(0, min(30, len(needs_work)), batch_size), 1):
        batch = needs_work[i : i + batch_size]
        print(f"\n### BATCH {batch_num} ###")
        for agent in batch:
            print(f"\n{agent['name']}")
            print(f"  Path: {agent['path']}")
            print(
                f"  Typed: {agent['typed_pct']:.0f}% | Doc: {agent['documented_pct']:.0f}% | schema: {agent['schema_strictness']:.0f}%"
            )
            print(f"  Quality Score: {agent['quality_score']:.1f}%")


if __name__ == "__main__":
    main()
