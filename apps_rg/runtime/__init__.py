"""apps_rg runtime spine adapter.

Wraps the deterministic HOP pipeline in genuine governance receipts:

    U0 intake -> L1 plan -> L0 route -> L3 bypass -> L2 execute -> Exit X3 -> L6 exhaust

Every receipt is hash-bound and threaded by a single ``run_id``. Spans
are emitted to ``otel_runtime_trace.json`` in the run dir. The legitimate
execution form for apps_rg is NOT MANAGED_WORKFLOW — apps_rg is a
deterministic HOP pipeline. The static L3 DAG documents the HOP topology
for governance purposes; runtime L3 orchestration is correctly bypassed
via ``NO_MANAGED_WORKFLOW_REQUIRED`` per the user's e2e proof spec.
"""
from apps_rg.runtime.context import GovernedRun, governed_run

__all__ = ["GovernedRun", "governed_run"]
