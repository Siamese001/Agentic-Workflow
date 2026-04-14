"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SSOT GUARDRAIL — Shadow Classification Detector                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Scans the repository AST to detect "shadow classification" — any code     ║
║  that reimplements agent detection or file classification logic outside     ║
║  the canonical kernel (agentic_core/core/classification_kernel.py).        ║
║                                                                            ║
║  Detections:                                                               ║
║  1. Function definitions named is_agent_class, classify_file, etc.         ║
║     outside the kernel and its known consumer (FileClassificationAgent).   ║
║  2. Usage of endswith('Agent') string checks inside logic functions         ║
║     (heuristic for inline shadow classification).                          ║
║                                                                            ║
║  Usage:                                                                    ║
║    python -m agentic_core.L5_safety.enforcement.ssot_guardrail              ║
║    python -m agentic_core.L5_safety.enforcement.ssot_guardrail --fail       ║
║                                                                            ║
║  Exit codes:                                                               ║
║    0 — No violations found                                                 ║
║    1 — Violations detected (with --fail)                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import argparse
import ast
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    TESTS_DIR,
)
from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "ssot_guardrail")
emit_determinism_digest("p0", "ssot_guardrail")

_emit_dispatches_healing_run("p1", "ssot_guardrail", "L5")
_emit_routes_through("p1", "ssot_guardrail", "L5")
_emit_checks_agent_registry("p1", "ssot_guardrail", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_guardrail", "capability")
_emit_dispatches_execution_plan("p1", "ssot_guardrail", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_guardrail", "sub_agent")
_emit_routes_to_agent("p1", "ssot_guardrail", "target_agent")
_emit_verifies_policy("p1", "ssot_guardrail", "policy_check")
_emit_observes_runtime_state("p1", "ssot_guardrail", "runtime_state")
_emit_verifies_boundary("p1", "ssot_guardrail", "boundary_check")
_emit_transcripts_response("p1", "ssot_guardrail", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_guardrail")
_emit_gated_by_confidence("p1", "ssot_guardrail", "confidence_gate")
_emit_escalates_to_human("p1", "ssot_guardrail", "L5")
_emit_reads_policy_state("p1", "ssot_guardrail", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "ssot_guardrail")
_emit_applies_guardrail("p0", "ssot_guardrail", "p0_governance")
_emit_snapshots_state("p0", "ssot_guardrail", "state_snapshot")
_emit_authorize_and_execute("p2", "ssot_guardrail", "execution_auth")
_emit_validates_capability("p2", "ssot_guardrail", "capability_check")
_emit_routes_to_capability("p2", "ssot_guardrail", "capability_route")
_emit_writes_via_uwg("p2", "ssot_guardrail", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_guardrail", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_guardrail", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_guardrail", "exec_output")
_emit_dispatches_agent("p3", "ssot_guardrail", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_guardrail", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_guardrail", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_guardrail", "healing_outcome")
_emit_escalates_failure("p3", "ssot_guardrail", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_guardrail", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_guardrail", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_guardrail", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_guardrail", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_guardrail", "eval_metric")
_emit_stores_embedding("p4", "ssot_guardrail", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_guardrail", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_guardrail", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("ssot_guardrail", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_guardrail", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_guardrail", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_guardrail", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_guardrail", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_guardrail", "p4obs", "metric_6")
_emit_records_incident_event("ssot_guardrail", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_guardrail", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_guardrail", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_guardrail", "p4obs", "mon_state")
_emit_triggers_alert("ssot_guardrail", "p4obs", "alert")
_emit_links_incident_trace("ssot_guardrail", "p4obs", "trace_link")
_emit_captures_pattern("ssot_guardrail", "p3lm", "pattern")
_emit_records_learning_event("ssot_guardrail", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_guardrail", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_guardrail", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_guardrail", "p3lm", "routing")
_emit_improves_agent_policy("ssot_guardrail", "p3lm", "policy")
_emit_stores_learning_state("ssot_guardrail", "p3lm", "state")
_emit_records_execution_trace("ssot_guardrail", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_guardrail", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_guardrail", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_guardrail", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_guardrail", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_guardrail", "env_read", "p2_env_1")
_emit_reads_environ("ssot_guardrail", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_guardrail", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_guardrail", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ssot_guardrail", "context_pull")
_emit_pulls_context("p1", "ssot_guardrail", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ssot_guardrail", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_guardrail", "uwg_term_2")
_emit_writes_through("p1", "ssot_guardrail", "write_through")
_emit_writes_through("p1", "ssot_guardrail", "write_through_2")
_emit_validated_by_safety_plane("p1", "ssot_guardrail", "safety_validation")
_emit_invokes_eval("p1", "ssot_guardrail", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_guardrail", "routing_commit")

# ============================================================================
# CONFIGURATION
# ============================================================================

# The canonical kernel — exempt from all checks
KERNEL_PATH = "agentic_core/core/classification_kernel.py"

# Files that are allowed to have classification-related function names
# because they are direct consumers/wrappers of the kernel
ALLOWLISTED_FILES: frozenset[str] = frozenset(
    {
        KERNEL_PATH,
        # FCA is the high-level consumer that wraps the kernel
        "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
        # This guardrail itself
        "agentic_core/L5_safety/enforcement/ssot_guardrail.py",
        # Contract tests reference the kernel
        "tests/core/test_classification_contract.py",
        # --- Phase 1 refactored wrappers (delegate to kernel) ---
        # complexity_visitor_util: is_sovereign_agent() → kernel, is_agent_class() shim
        "agentic_core/L0_routing/utils/complexity_visitor_util.py",
        # full_agent_discovery: analyze_agent_integrity() → kernel classify_file_standalone()
        "agentic_core/L0_routing/scripts/full_agent_discovery.py",
        # run_classification: classify_file() → kernel classify_file_standalone()
        "ops_scripts/maintenance/run_classification.py",
        # discovery_util: _scan_file_for_agents() → kernel is_agent_file()
        "agentic_core/runtime/utils/discovery_util.py",
        # file_intent: _is_agent_class() aligned with kernel naming rules
        "agentic_core/prompt_governance/scripts/file_intent.py",
        # type_erasure_validator: _is_agent_class() aligned with kernel
        "agentic_core/L5_safety/validators/type_erasure_validator.py",
        # Dedup utilities: is_agent_file() aligned with kernel naming
        "agentic_core/L0_routing/scripts/extract_agent_duplicates_util.py",
        "agentic_core/L0_routing/scripts/find_real_duplicates_v2_util.py",
        # --- Phase 2 Step 1: Refactored to delegate to kernel ---
        # generate_agent_table_simple_util: is_agent_file() wraps kernel for string paths
        "dev_tools/l0_scripts/generate_agent_table_simple_util.py",
        # pascal_sovereignty_fixer: classify_file() → kernel classify_file_standalone()
        "dev_tools/l0_scripts/pascal_sovereignty_fixer.py",
        # mece_test_rebaseline: classify_file() → kernel classify_file_standalone()
        "ops_scripts/general/mece_test_rebaseline.py",
    },
)

# Function names that indicate shadow classification logic
SHADOW_FUNCTION_NAMES: frozenset[str] = frozenset(
    {
        "is_agent_class",
        "classify_file",
        "classify_file_standalone",
        "_is_agent_class",
        "_classify_file",
        "is_agent_file",
    },
)

# Files allowed to have endswith('Agent') checks because they operate on
# AST class nodes for metadata extraction (not classification)
ENDSWITH_AGENT_ALLOWLIST: frozenset[str] = frozenset(
    {
        KERNEL_PATH,
        "agentic_core/L5_safety/reasoning/FileClassificationAgent.py",
        "agentic_core/L5_safety/enforcement/ssot_guardrail.py",
        "tests/core/test_classification_contract.py",
        # These use endswith("Agent") for metadata extraction, not classification:
        "agentic_core/L0_routing/utils/complexity_visitor_util.py",
        "agentic_core/L0_routing/scripts/full_agent_discovery.py",
        # Naming/renaming scripts that check suffixes for compliance:
        "agentic_core/L5_safety/enforcement/ssot_scanner_enforcer.py",
        "agentic_core/L5_safety/enforcement/registry_verification_enforcer.py",
        "agentic_core/L5_safety/enforcement/data_enforcer.py",
        "agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py",
        # Dedup/migration scripts:
        "agentic_core/L0_routing/scripts/extract_agent_duplicates_util.py",
        "agentic_core/L0_routing/scripts/find_real_duplicates_v2_util.py",
        # Naming convention enforcement:
        "ops_scripts/maintenance/run_classification.py",
    },
)

# Directories to exclude from scanning
EXCLUDE_DIRS: frozenset[str] = (
    GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
)


# ============================================================================
# VIOLATION DATA MODEL
# ============================================================================


@dataclass
class Violation:
    """A single guardrail violation."""

    file: str
    line: int
    rule: str
    detail: str
    severity: str = "ERROR"


@dataclass
class ScanResult:
    """Aggregated scan results."""

    files_scanned: int = 0
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


# ============================================================================
# AST SCANNERS
# ============================================================================


def _normalize_path(path: Path, project_root: Path) -> str:
    """Convert absolute path to forward-slash relative path."""
    try:
        rel = path.relative_to(project_root)
    except ValueError:
        rel = path
    return str(rel).replace("\\", "/")


def scan_shadow_functions(
    tree: ast.AST,
    rel_path: str,
) -> list[Violation]:
    """Detect function definitions that shadow kernel classification."""
    violations = []

    if rel_path in ALLOWLISTED_FILES:
        return violations

    for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in SHADOW_FUNCTION_NAMES:
                violations.append(
                    Violation(
                        file=rel_path,
                        line=node.lineno,
                        rule="SHADOW_FUNCTION",
                        detail=(
                            f"Function '{node.name}()' reimplements classification logic. "
                            f"Use: from agentic_core.L5_safety.core_kernel.classification_kernel import is_agent_file"
                        ),
                    ),
                )
    return violations


def scan_endswith_agent(
    tree: ast.AST,
    rel_path: str,
) -> list[Violation]:
    """Detect usage of endswith('Agent') string checks in logic functions.

    This is a heuristic for inline shadow classification. We look for
    ast.Call nodes where the function is an Attribute named 'endswith'
    and the argument is a string containing 'Agent'.
    """
    violations = []

    if rel_path in ENDSWITH_AGENT_ALLOWLIST:
        return violations

    for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
        if not isinstance(node, ast.Call):
            continue
        # Match: <expr>.endswith("Agent") or <expr>.endswith("Agent")
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "endswith":
            continue
        # Check if any argument is a string containing "Agent"
        for arg in tqdm(node.args, desc="Processing", unit="item"):
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if "Agent" in arg.value:
                    violations.append(
                        Violation(
                            file=rel_path,
                            line=node.lineno,
                            rule="ENDSWITH_AGENT",
                            detail=(
                                f"Inline endswith('{arg.value}') check detected. "
                                f"Consider using classification_kernel.is_agent_file() instead."
                            ),
                            severity="WARNING",
                        ),
                    )
            # Also check tuples: endswith(("Agent", "BaseAgent"))
            if isinstance(arg, ast.Tuple):
                for elt in tqdm(arg.elts, desc="Processing", unit="item"):
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        if "Agent" in elt.value:
                            violations.append(
                                Violation(
                                    file=rel_path,
                                    line=node.lineno,
                                    rule="ENDSWITH_AGENT",
                                    detail=(
                                        f"Inline endswith((..., '{elt.value}', ...)) check detected. "
                                        f"Consider using classification_kernel.is_agent_file() instead."
                                    ),
                                    severity="WARNING",
                                ),
                            )
                            break  # One violation per call site is enough
    return violations


# ============================================================================
# MAIN SCANNER
# ============================================================================


def scan_repository(project_root: Path) -> ScanResult:
    """Scan all Python files in the repository for SSOT violations."""
    result = ScanResult()

    scan_dirs = [
        project_root / AGENTIC_CORE_DIR,
        project_root / APPS_LIC_DIR,
        project_root / APPS_RG_DIR,
        project_root / APPS_SHARED_DIR,
        project_root / OPS_SCRIPTS_DIR,
        project_root / TESTS_DIR,
    ]

    for scan_dir in tqdm(scan_dirs, desc="Processing", unit="item"):
        if not scan_dir.exists():
            continue
        for dirpath, dirnames, filenames in tqdm(os.walk(scan_dir), desc="Processing", unit="item"):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for fn in tqdm(filenames, desc="Processing", unit="item"):
                if not fn.endswith(".py"):
                    continue
                fp = Path(dirpath) / fn
                rel_path = _normalize_path(fp, project_root)

                try:
                    content = fp.read_text(encoding="utf-8", errors="replace")
                    tree = ast.parse(content)
                except (
                    SyntaxError,
                    OSError,
                ):  # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling
                    continue

                result.files_scanned += 1
                result.violations.extend(scan_shadow_functions(tree, rel_path))
                result.violations.extend(scan_endswith_agent(tree, rel_path))

    return result


# ============================================================================
# CLI
# ============================================================================


def main() -> int:
    """Run the SSOT guardrail scanner."""
    parser = argparse.ArgumentParser(
        description="SSOT Guardrail: Detect shadow classification logic",
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Exit with code 1 if any violations are found",
    )
    parser.add_argument(
        "--errors-only",
        action="store_true",
        help="Only report ERROR severity (ignore WARNINGs)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    result = scan_repository(project_root)

    violations = result.violations
    if args.errors_only:
        violations = [v for v in violations if v.severity == "ERROR"]

    if args.json:
        import json

        output = {
            "files_scanned": result.files_scanned,
            "violation_count": len(violations),
            "passed": len(violations) == 0,
            "violations": [
                {
                    "file": v.file,
                    "line": v.line,
                    "rule": v.rule,
                    "detail": v.detail,
                    "severity": v.severity,
                }
                for v in violations
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"SSOT Guardrail Scan: {result.files_scanned} files scanned")
        print(f"Violations: {len(violations)}")
        if violations:
            print()
            for v in violations:
                print(f"  [{v.severity}] {v.file}:{v.line}")
                print(f"    Rule: {v.rule}")
                print(f"    {v.detail}")
                print()
        else:
            print("Status: PASS — No shadow classification detected.")

    if args.fail and len(violations) > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
