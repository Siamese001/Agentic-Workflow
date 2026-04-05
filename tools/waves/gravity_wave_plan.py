#!/usr/bin/env python3
"""
Layer Gravity Violations - Wave Plan
Recategorized to HIGH Severity - 19 violations total
"""

VIOLATIONS = {
    # L0 (Routing) violations - CRITICAL - 11 total
    "L0->L2": [
        "agentic_core/L0_routing/enforcement/execution_gateway.py:134",
        "agentic_core/L0_routing/enforcement/mutation_prohibition.py:45",
        "agentic_core/L0_routing/engines/shadow_router_classifier.py:28",
        "agentic_core/L0_routing/scripts/execute_ssot.py:87",
    ],
    "L0->L3": [
        "agentic_core/L0_routing/engines/escalation_router.py:156",
        "agentic_core/L0_routing/engines/timeshift_router.py:203",
    ],
    "L0->L_PG": [
        "agentic_core/L0_routing/artifacts/deterministic_routing_gateway.py:18",
        # Plus one more not in catalog
    ],
    "L0->L_RUNTIME": [
        "agentic_core/L0_routing/artifacts/execution_trace_artifact.py:89",
    ],
    "L0->L_SL": [
        "agentic_core/L0_routing/artifacts/agent_trace_artifact.py:156",
    ],
    "L0->L_TOOLS": [
        "agentic_core/L0_routing/artifacts/execution_trace_artifact.py:234",
    ],

    # L1 (Cognition) violations - 2 total
    "L1->L2": [
        "agentic_core/L1_cognition/engines/cognitive_engine.py:93",
    ],
    "L1->L6": [
        "agentic_core/L1_cognition/enforcement/reasoning_chokepoint.py:62",
    ],

    # L5 (Safety) violations - 1 total
    "L5->L_TOOLS": [
        "agentic_core/L5_safety/hitl/review_queue_api.py:32",
    ],

    # L6 (Observability) violations - 2 total
    "L6->L_SL": [
        "agentic_core/L6_observability/engines/desk_d_governed_board.py:74",
    ],
    "L6->L_TOOLS": [
        "agentic_core/L6_observability/mcp_drift_store.py:32",
    ],

    # L_SHARED violations - 3 total
    "L_SHARED->L3": [
        "agentic_core/mixins/adaptive_execution_mixin.py:81",
    ],
    "L_SHARED->L_PG": [
        "agentic_core/mixins/prompt_rendering_mixin.py:19",
    ],
    "L_SHARED->L_SL": [
        "agentic_core/mixins/integrated_tracing_mixin.py:37",
    ],

    # L_SL (System Learning) violations - 4 total
    "L_SL->L3": [
        "system_learning/adapters/workflow_outcome_sl_adapter.py:10",
    ],
    "L_SL->L4": [
        "system_learning/engines/system_learning_admission_gate.py:18",
    ],
    "L_SL->L_APP": [
        "system_learning/runtime_adg/auto_persistence.py:18",
    ],
    "L_SL->L_RUNTIME": [
        "system_learning/engines/enhanced_rag_retrieval_cache.py:55",
    ],

    # L_TOOLS violations - 1 total
    "L_TOOLS->L_RUNTIME": [
        "agentic_core/adg/schema_util.py:24",
    ],
}

WAVE_PLAN = {
    "Wave 1 - L0->L2 (Critical)": VIOLATIONS["L0->L2"],
    "Wave 2 - L0->L3/L_PG (Critical)": VIOLATIONS["L0->L3"] + VIOLATIONS["L0->L_PG"],
    "Wave 3 - L0->L_RUNTIME/L_SL/L_TOOLS": VIOLATIONS["L0->L_RUNTIME"] + VIOLATIONS["L0->L_SL"] + VIOLATIONS["L0->L_TOOLS"],
    "Wave 4 - L1 Violations": VIOLATIONS["L1->L2"] + VIOLATIONS["L1->L6"],
    "Wave 5 - L5/L6 Violations": VIOLATIONS["L5->L_TOOLS"] + VIOLATIONS["L6->L_SL"] + VIOLATIONS["L6->L_TOOLS"],
    "Wave 6 - L_SHARED Violations": VIOLATIONS["L_SHARED->L3"] + VIOLATIONS["L_SHARED->L_PG"] + VIOLATIONS["L_SHARED->L_SL"],
    "Wave 7 - L_SL Violations": VIOLATIONS["L_SL->L3"] + VIOLATIONS["L_SL->L4"] + VIOLATIONS["L_SL->L_APP"] + VIOLATIONS["L_SL->L_RUNTIME"],
    "Wave 8 - L_TOOLS Violations": VIOLATIONS["L_TOOLS->L_RUNTIME"],
}

if __name__ == "__main__":
    total = sum(len(v) for v in VIOLATIONS.values())
    print("Layer Gravity Violations Wave Plan")
    print(f"Total: {total} HIGH severity violations")
    print()
    for wave, files in WAVE_PLAN.items():
        print(f"{wave}: {len(files)} files")
        for f in files:
            print(f"  - {f}")
        print()
