"""
ADG-Driven Test Failure Wave Prioritization Plan
Generated: 2026-04-01

Based on ADG collection analysis:
- Total files scanned: 3,952
- Collection-safe: 1,972 (49.9%)
- Collection-fatal: 1,980 (50.1%) - missing imports
- By layer: L0(429), L2(310), L5(279), L3(91), L4(75), L6(36)

Current pytest status: 4193 passed, 3331 failed, 34 skipped, 112 errors
"""

WAVE_PLAN = {
    "meta": {
        "strategy": "Largest patterns first to maximize burndown rate",
        "total_waves": 6,
        "estimated_errors_addressed": 112,
        "target": "Zero collection errors, <50 failures",
    },
    "waves": [
        {
            "wave": 1,
            "phase_id": "W1-L0-INFRA",
            "focus": "L0 Routing Infrastructure (429 files)",
            "rationale": "L0 is the foundation - routing failures cascade to all layers. 429 files affected = largest blast radius.",
            "patterns_targeted": [
                "path_constants import failures",
                "L0_routing.config imports",
                "Dispatcher/Registry initialization",
            ],
            "estimated_burndown": "40-50 errors",
            "files": [
                "agentic_core/L0_routing/config/path_constants.py",
                "agentic_core/L0_routing/config/ssot_tier_constants.py",
                "tests/unit/agentic_core/L0_routing/scripts/test_path_setup.py",
            ],
            "success_criteria": "L0 tests collect successfully, routing fixtures available",
        },
        {
            "wave": 2,
            "phase_id": "W2-L2-EXEC",
            "focus": "L2 Execution Layer (310 files)",
            "rationale": "L2 is where apps_qwen and execution agents live. Second largest layer with execution-critical code.",
            "patterns_targeted": [
                "apps_qwen module imports",
                "L2_execution agent imports",
                "Execution fixture dependencies",
            ],
            "estimated_burndown": "25-30 errors",
            "files": [
                "tests/unit/agentic_core/L2_execution/apps_qwen/test_apps_qwen_*.py",
                "agentic_core/L2_execution/apps_qwen/*.py",
            ],
            "success_criteria": "L2 execution tests collect, apps_qwen fixtures functional",
        },
        {
            "wave": 3,
            "phase_id": "W3-L5-SAFETY",
            "focus": "L5 Safety/Guardian Layer (279 files)",
            "rationale": "L5 is cross-cutting - safety failures affect all other layers. High criticality despite smaller file count.",
            "patterns_targeted": [
                "Guardian/Healer agent imports",
                "L5_safety validators",
                "Safety fixture setup",
            ],
            "estimated_burndown": "20-25 errors",
            "files": [
                "tests/unit/agentic_core/L5_safety/test_hollow_file_detector.py",
                "tests/unit/agentic_core/L5_safety/validators/test_anti_pattern_scanner_validator_*.py",
                "tests/integration/test_depth_violation_no_archive_invariant.py",
            ],
            "success_criteria": "L5 safety tests collect, guardian agents available",
        },
        {
            "wave": 4,
            "phase_id": "W4-L4-STATE",
            "focus": "L4 State/Memory Layer (75 files)",
            "rationale": "L4 state management - required for test isolation and memory bridges. Smaller but critical.",
            "patterns_targeted": [
                "GraphMemoryBridge imports",
                "FAISS store initialization",
                "L1 exact cache imports",
            ],
            "estimated_burndown": "10-15 errors",
            "files": [
                "tests/unit/agentic_core/L4_state/enforcement/test_graph_memory_bridge_*.py",
                "tests/unit/agentic_core/L4_state/memory/test_faiss_store.py",
                "tests/unit/agentic_core/L4_state/memory/test_l1_exact_cache.py",
            ],
            "success_criteria": "L4 state tests collect, memory bridges functional",
        },
        {
            "wave": 5,
            "phase_id": "W5-L3-ORCH",
            "focus": "L3 Orchestrator (91 files) + L1 Reasoning (66 files)",
            "rationale": "L3 orchestration and L1 reasoning - middle layers that coordinate L0/L2.",
            "patterns_targeted": [
                "Orchestrator imports",
                "Reasoning loop setup",
                "Librarian/context engine imports",
            ],
            "estimated_burndown": "10-15 errors",
            "files": [
                "tests/e2e/test_ptc_full_lifecycle_e2e.py",
                "tests/e2e/test_ptc_aggressive_hardening.py",
                "tests/integration/test_ptc_full_integration.py",
            ],
            "success_criteria": "PTC/orchestration tests collect",
        },
        {
            "wave": 6,
            "phase_id": "W6-L6-E2E",
            "focus": "L6 Observability (36 files) + E2E Integration",
            "rationale": "Final layer - observability and end-to-end tests. Last to fix as it depends on all other layers.",
            "patterns_targeted": [
                "Runtime ADG imports",
                "Telemetry/observability fixtures",
                "E2E test harness",
            ],
            "estimated_burndown": "5-10 errors",
            "files": [
                "tests/e2e/test_runtime_adg_l6_observability_e2e.py",
                "tests/e2e/test_hitl_lifecycle_e2e.py",
                "tests/e2e/test_code_validation_gates_e2e.py",
            ],
            "success_criteria": "All E2E tests collect, <50 total failures",
        },
    ],
    "metrics": {
        "current_state": {"passed": 4193, "failed": 3331, "skipped": 34, "errors": 112},
        "target_state": {"errors": 0, "failed": "<500", "pass_rate": ">85%"},
    },
    "pattern_analysis": {
        "largest_blast_radius": [
            {"pattern": "L0_routing imports", "affected_files": 429, "layer": "L0"},
            {"pattern": "L2_execution imports", "affected_files": 310, "layer": "L2"},
            {"pattern": "L5_safety imports", "affected_files": 279, "layer": "L5"},
        ],
        "recommended_sequence": "L0 → L2 → L5 → L4 → L3/L1 → L6/E2E",
    },
}

if __name__ == "__main__":
    import json

    print(json.dumps(WAVE_PLAN, indent=2))
