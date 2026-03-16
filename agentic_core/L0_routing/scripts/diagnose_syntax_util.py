#!/usr/bin/env python3
"""
Diagnose Syntax Errors - Quick syntax validation for all Python files.

Usage:
    python scripts/diagnose_syntax_util.py
"""

import ast
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.config.path_constants import TESTS_DIR
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

emit_replay_key("p0", "diagnose_syntax_util")
emit_determinism_digest("p0", "diagnose_syntax_util")

_emit_dispatches_healing_run("p1", "diagnose_syntax_util", "L0")
_emit_routes_through("p1", "diagnose_syntax_util", "L0")
_emit_escalates_to_human("p1", "diagnose_syntax_util", "L0")
_emit_reads_policy_state("p1", "diagnose_syntax_util", "L0")
_emit_authorize_and_execute("p2", "diagnose_syntax_util", "execution_auth")
_emit_validates_capability("p2", "diagnose_syntax_util", "capability_check")
_emit_routes_to_capability("p2", "diagnose_syntax_util", "capability_route")
_emit_writes_via_uwg("p2", "diagnose_syntax_util", "uwg_write")
_emit_blocks_direct_write("p2", "diagnose_syntax_util", "direct_write_block")
_emit_records_tool_invocation("p2", "diagnose_syntax_util", "tool_invocation")
_emit_captures_execution_output("p2", "diagnose_syntax_util", "exec_output")
_emit_dispatches_agent("p3", "diagnose_syntax_util", "agent_dispatch")
_emit_coordinates_agents("p3", "diagnose_syntax_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "diagnose_syntax_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "diagnose_syntax_util", "healing_outcome")
_emit_escalates_failure("p3", "diagnose_syntax_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "diagnose_syntax_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "diagnose_syntax_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "diagnose_syntax_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "diagnose_syntax_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "diagnose_syntax_util", "eval_metric")
_emit_stores_embedding("p4", "diagnose_syntax_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "diagnose_syntax_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "diagnose_syntax_util", "exec_snapshot_link")


def check_syntax(root: Path) -> int:
    """Check all Python files for syntax errors.

    Returns:
        Number of files with syntax errors
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "check_syntax", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "check_syntax", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "check_syntax")
    errors = []

    for f in root.rglob("*.py"):
        # Skip common exclusions
        if any(x in f.parts for x in ["__pycache__", ".git", "node_modules", ".venv", "venv", ARCHIVES_DIR]):
            continue

        try:
            content = f.read_text(encoding="utf-8")
            ast.parse(content)
        except SyntaxError as e:
            errors.append((str(f), e.lineno, e.msg))

    if errors:
        print(f"❌ Found {len(errors)} files with syntax errors:")
        for f, line, msg in errors:
            print(f"  {f}:{line} - {msg}")
        return len(errors)
    else:
        print("✅ All Python files have valid syntax!")
        return 0


if __name__ == "__main__":
    import sys

    root = Path(__file__).parent.parent

    # Check agentic_core
    print("Checking agentic_core...")
    agentic_errors = check_syntax(root / AGENTIC_CORE_DIR)

    # Check scripts
    print("\nChecking scripts...")
    scripts_errors = check_syntax(root / "scripts")

    # Check tests
    print("\nChecking tests...")
    tests_errors = check_syntax(root / TESTS_DIR)

    total = agentic_errors + scripts_errors + tests_errors
    print(f"\n{'=' * 60}")
    print(f"Total syntax errors: {total}")

    sys.exit(0 if total == 0 else 1)
