"""Pytest collection rules for active ``tests/unit/apps_eval`` coverage.

The ignored files below target the pre-reset apps_eval agent/orchestrator
surface.  The hard-reset plan retired those runtime authorities; active
apps_eval unit coverage now exercises contracts, deterministic graders,
registry loading, runner scoring, and the telemetry shim.
"""

collect_ignore = [
    "reasoning/test_eval_hop_orchestrator.py",
    "test_governed_run_integration.py",
    "test_regression_taxonomy.py",
]
