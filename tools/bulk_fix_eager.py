"""
Mechanical eager import fixer - converts module-level agentic_core imports
to lazy fixtures using a simple find-and-replace pattern.
"""

import re
from pathlib import Path

REPO_ROOT = Path("c:/Git/Agentic-Workflow")

# Files to process (from the violation scan)
FILES = [
    "tests/architecture/test_wave2_phase2_3_prompt_taxonomy.py",
    "tests/e2e/test_ptc_full_lifecycle_e2e.py",
    "tests/e2e/test_ptc_aggressive_hardening.py",
    "tests/e2e/test_hitl_lifecycle_e2e.py",
    "tests/e2e/test_graphrag_hardened.py",
    "tests/e2e/test_graphrag_e2e.py",
    "tests/e2e/test_prompt_lifecycle_edge_cases_e2e.py",
    "tests/e2e/test_mcp_drift_e2e.py",
    "tests/e2e/test_code_validation_gates_e2e.py",
    "tests/e2e/test_cross_layer_integration_e2e.py",
    "tests/e2e/test_opentelemetry_integration_e2e.py",
    "tests/e2e/test_runtime_adg_l6_observability_e2e.py",
    "tests/integration/test_ptc_full_integration.py",
    "tests/integration/test_depth_violation_no_archive_invariant.py",
    "tests/integration/test_ci_adg_migration.py",
    "tests/integration/test_prompt_lifecycle_pipeline.py",
    "tests/integration/agentic_core/test_redis_l1_retrieval_gate_e2e.py",
    "tests/integration/test_wave4_simple_integration.py",
]






if __name__ == "__main__":
    main()
