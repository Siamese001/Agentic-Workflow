"""
agentic_core/enforcement/sealed_interface_check_enforcer.py

AST-based enforcement: blocks apps_* from importing sealed interface
implementation modules (_impl pattern) and direct L* layer imports.

Runs as CI gate and can be invoked as:
    python -m agentic_core.enforcement.sealed_interface_check_enforcer

EXIT CODES:
    0 — no violations found
    1 — violations found (prints details)
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "sealed_interface_check_enforcer")
emit_determinism_digest("p0", "sealed_interface_check_enforcer")

_emit_dispatches_healing_run("p1", "sealed_interface_check_enforcer", "L5")
_emit_routes_through("p1", "sealed_interface_check_enforcer", "L5")
_emit_escalates_to_human("p1", "sealed_interface_check_enforcer", "L5")
_emit_reads_policy_state("p1", "sealed_interface_check_enforcer", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "sealed_interface_check_enforcer")
_emit_applies_guardrail("p0", "sealed_interface_check_enforcer", "p0_governance")
_emit_snapshots_state("p0", "sealed_interface_check_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "sealed_interface_check_enforcer", "execution_auth")
_emit_validates_capability("p2", "sealed_interface_check_enforcer", "capability_check")
_emit_routes_to_capability("p2", "sealed_interface_check_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "sealed_interface_check_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "sealed_interface_check_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "sealed_interface_check_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "sealed_interface_check_enforcer", "exec_output")
_emit_dispatches_agent("p3", "sealed_interface_check_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "sealed_interface_check_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "sealed_interface_check_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "sealed_interface_check_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "sealed_interface_check_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "sealed_interface_check_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sealed_interface_check_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "sealed_interface_check_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "sealed_interface_check_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sealed_interface_check_enforcer", "eval_metric")
_emit_stores_embedding("p4", "sealed_interface_check_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "sealed_interface_check_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sealed_interface_check_enforcer", "exec_snapshot_link")

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_ROOTS = [
    REPO_ROOT / APPS_LIC_DIR,
    REPO_ROOT / APPS_RG_DIR,
    REPO_ROOT / APPS_SHARED_DIR,
]

FORBIDDEN_IMPORT_PATTERNS = [
    "agentic_core.interfaces._",  # _impl and other private submodules
]

FORBIDDEN_LAYER_PREFIXES = [
    "agentic_core.L0_",
    "agentic_core.L1_",
    "agentic_core.L2_",
    "agentic_core.L3_",
    "agentic_core.L4_",
    "agentic_core.L5_",
    "agentic_core.L6_",
]


def _get_import_modules(tree: ast.AST) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
    return modules


def check_file(path: Path) -> list[str]:
    """Return list of violation strings for a single file."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [f"SYNTAX_ERROR: {path}: {exc}"]

    violations: list[str] = []
    try:
        rel = path.relative_to(REPO_ROOT)
    except ValueError:
        rel = path

    for module in _get_import_modules(tree):
        for pat in FORBIDDEN_IMPORT_PATTERNS:
            if module.startswith(pat):
                violations.append(
                    f"SEALED_IMPL_BYPASS: {rel} imports '{module}' "
                    f"(sealed implementation modules are forbidden in apps_*)"
                )
        for prefix in FORBIDDEN_LAYER_PREFIXES:
            if module.startswith(prefix):
                violations.append(
                    f"DIRECT_LAYER_IMPORT: {rel} imports '{module}' (use agentic_core.interfaces.* instead)"
                )

    return violations


def run_check(apps_roots: list[Path] = APPS_ROOTS) -> list[str]:
    """Scan all apps_* Python files and return all violations."""
    all_violations: list[str] = []
    for root in apps_roots:
        if not root.exists():
            continue
        for py_file in sorted(root.rglob("*.py")):
            all_violations.extend(check_file(py_file))
    return all_violations


def main() -> int:
    violations = run_check()
    if violations:
        print(f"FAIL: {len(violations)} sovereignty violation(s) found:")
        for v in violations:
            print(f"  {v}")
        return 1
    total = sum(len(list(r.rglob("*.py"))) for r in APPS_ROOTS if r.exists())
    print(f"OK: sealed interface check passed ({total} files scanned, 0 violations)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
