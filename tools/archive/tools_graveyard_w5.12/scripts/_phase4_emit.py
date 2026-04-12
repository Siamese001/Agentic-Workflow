import json
from pathlib import Path

clusters = [
    {
        "cluster_id": "A",
        "root_module": "agentic_core/L0_routing/scripts/execute_ssot.py",
        "root_function": "run_pipeline",
        "root_line": 7369,
        "error_category": "API_DRIFT",
        "description": "except clause at line 7369 does not include RuntimeError. Tests mock adapter subphase methods to raise RuntimeError expecting fail-closed behavior. The exception propagates instead of being caught.",
        "first_ring_relation": "TestFailClosedOnException imports run_pipeline directly from execute_ssot",
        "adg_edge": "tests/sovereign_hardening/test_ssot_pipeline_protocol.py -> IMPORT -> agentic_core/L0_routing/scripts/execute_ssot.py::run_pipeline",
        "failing_tests": [
            "tests/sovereign_hardening/test_ssot_pipeline_protocol.py::TestFailClosedOnException::test_execute_skipped_after_validate_exception",
            "tests/sovereign_hardening/test_ssot_pipeline_protocol.py::TestFailClosedOnException::test_heal_skipped_after_validate_exception",
            "tests/sovereign_hardening/test_ssot_pipeline_protocol.py::TestFailClosedOnException::test_error_field_populated",
            "tests/sovereign_hardening/test_ssot_pipeline_protocol.py::TestFailClosedOnException::test_skip_agent_called",
            "tests/sovereign_hardening/test_ssot_pipeline_protocol.py::TestFailClosedOnException::test_update_agent_not_called_for_execute_after_exception",
            "tests/sovereign_hardening/test_ssot_pipeline_protocol.py::TestFailClosedOnException::test_update_agent_not_called_for_heal_after_exception",
            "tests/sovereign_hardening/test_ssot_pipeline_protocol.py::TestFailClosedOnException::test_exception_in_pre_commit_skips_all_subsequent",
        ],
        "failure_count": 7,
        "confidence": "high",
        "repair_action": "Add RuntimeError to except clause at execute_ssot.py:7369",
    },
    {
        "cluster_id": "B",
        "root_module": "tests/invariants/test_gap_a_b_wire_in.py",
        "root_function": "TestGapARunManifest.test_write_run_manifest_creates_file / test_write_run_manifest_trace_id_in_file",
        "root_line": 23,
        "error_category": "IMPORT_PATH_ERROR",
        "description": "Test uses APPS_RG_DIR, APPS_LIC_DIR, AGENTIC_CORE_DIR as bare names without importing them. ADG chain: test -> path_constants.py defines these constants.",
        "first_ring_relation": "test_gap_a_b_wire_in.py is in execute_ssot ADG test surface via path_constants first-ring dependency",
        "adg_edge": "tests/invariants/test_gap_a_b_wire_in.py -> IMPORT_MISSING -> agentic_core/L0_routing/config/path_constants.py",
        "failing_tests": [
            "tests/invariants/test_gap_a_b_wire_in.py::TestGapARunManifest::test_write_run_manifest_creates_file",
            "tests/invariants/test_gap_a_b_wire_in.py::TestGapARunManifest::test_write_run_manifest_trace_id_in_file",
        ],
        "failure_count": 2,
        "confidence": "high",
        "repair_action": "Add missing imports of APPS_RG_DIR, APPS_LIC_DIR, AGENTIC_CORE_DIR from path_constants to test_gap_a_b_wire_in.py",
    },
    {
        "cluster_id": "C",
        "root_module": "agentic_core/L0_routing/scripts/execute_ssot.py",
        "root_function": "_fire_meta_learning_intake",
        "root_line": 267,
        "error_category": "API_DRIFT",
        "description": "_fire_meta_learning_intake signature is (state_mgr, now_utc) but line 267 references 'decision_engine' as a bare name — not in scope. Test calls with only 2 args.",
        "first_ring_relation": "Direct import: test_fire_meta_learning_timestamps imports _fire_meta_learning_intake from execute_ssot",
        "adg_edge": "tests/unit_min_deps/test_fire_meta_learning_timestamps.py -> IMPORT -> agentic_core/L0_routing/scripts/execute_ssot.py::_fire_meta_learning_intake",
        "failing_tests": [
            "tests/unit_min_deps/test_fire_meta_learning_timestamps.py::TestFireMetaLearningTimestamps::test_empty_healing_actions_no_crash",
        ],
        "failure_count": 1,
        "confidence": "high",
        "repair_action": "Add decision_engine=None optional parameter to _fire_meta_learning_intake and use getattr default at line 267",
    },
    {
        "cluster_id": "D",
        "root_module": "agentic_core/L2_execution/healers/qwen_vllm_inference.py",
        "root_function": "_arbiter WSL subprocess",
        "root_line": 1925,
        "error_category": "IMPORT_PATH_ERROR",
        "description": "vLLM subprocess launches in WSL context without agentic_core on PYTHONPATH. ModuleNotFoundError: No module named 'agentic_core' inside WSL subprocess.",
        "first_ring_relation": "execute_ssot._arbiter launches qwen_vllm_inference.py as subprocess in WSL",
        "adg_edge": "execute_ssot.py::_arbiter:1925 -> subprocess -> qwen_vllm_inference.py",
        "failing_tests": [
            "tests/e2e/agentic_core/L0_maintenance/misc/test_ssot_e2e_reporting.py::TestSSOTE2EReporting::test_e2e_05_decision_audit_trail",
            "tests/e2e/agentic_core/L0_maintenance/misc/test_ssot_e2e_reporting.py::TestSSOTE2EReporting::test_e2e_09_full_reconciliation_loop",
        ],
        "failure_count": 2,
        "confidence": "high",
        "repair_action": "Inspect _arbiter to ensure PYTHONPATH is set when launching WSL subprocess",
    },
    {
        "cluster_id": "E",
        "root_module": "agentic_core/L0_routing/scripts/execute_ssot.py",
        "root_function": "state persistence / should_proceed_with_healing",
        "root_line": None,
        "error_category": "ASSERTION_MISMATCH",
        "description": "test_e2e_03: state file not written on crash recovery. test_e2e_08: should_proceed_with_healing returns True when test expects False for human rejection scenario.",
        "first_ring_relation": "Direct e2e test of execute_ssot orchestration",
        "adg_edge": "tests/e2e/.../test_ssot_e2e_reporting.py -> IMPORT -> execute_ssot.py",
        "failing_tests": [
            "tests/e2e/agentic_core/L0_maintenance/misc/test_ssot_e2e_reporting.py::TestSSOTE2EReporting::test_e2e_03_state_persistence_crash_recovery",
            "tests/e2e/agentic_core/L0_maintenance/misc/test_ssot_e2e_reporting.py::TestSSOTE2EReporting::test_e2e_08_human_rejection_logic",
        ],
        "failure_count": 2,
        "confidence": "medium",
        "repair_action": "Inspect e2e test setup and execute_ssot state/human rejection logic",
    },
]

out = Path("artifacts/execute_ssot_root_clusters.json")
out.write_text(
    json.dumps({"clusters": clusters, "total_clusters": len(clusters), "total_failures": 15}, indent=2),
    encoding="utf-8",
)
print("PHASE 4 artifact written.")
for c in clusters:
    print(
        f"  Cluster {c['cluster_id']}: {c['root_function']} — {c['failure_count']} failures — {c['error_category']}"
    )
