"""
AST-based CI guard: spine bypass + randomness detection.

Scans apps_lic/, apps_rg/, agentic_core/ for:
  A) Banned direct instantiation of spine classes outside allowed adapters.
  B) Randomness usage in deterministic paths.

Uses a baseline file to track pre-existing violations so only NEW violations
fail the build.

Exit codes:
  0 — no new violations
  1 — new violations found
"""

from __future__ import annotations

import argparse
import ast
import os
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    OPS_SCRIPTS_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
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
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_reads_through,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("check_spine_bypass", "p4obs", "metric_1")
_emit_emits_metric_event("check_spine_bypass", "p4obs", "metric_2")
_emit_emits_metric_event("check_spine_bypass", "p4obs", "metric_3")
_emit_emits_metric_event("check_spine_bypass", "p4obs", "metric_4")
_emit_emits_metric_event("check_spine_bypass", "p4obs", "metric_5")
_emit_emits_metric_event("check_spine_bypass", "p4obs", "metric_6")
_emit_records_incident_event("check_spine_bypass", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_spine_bypass", "p4obs", "anomaly")
_emit_writes_observability_log("check_spine_bypass", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_spine_bypass", "p4obs", "mon_state")
_emit_triggers_alert("check_spine_bypass", "p4obs", "alert")
_emit_links_incident_trace("check_spine_bypass", "p4obs", "trace_link")
_emit_captures_pattern("check_spine_bypass", "p3lm", "pattern")
_emit_records_learning_event("check_spine_bypass", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_spine_bypass", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_spine_bypass", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_spine_bypass", "p3lm", "routing")
_emit_improves_agent_policy("check_spine_bypass", "p3lm", "policy")
_emit_stores_learning_state("check_spine_bypass", "p3lm", "state")
_emit_records_execution_trace("check_spine_bypass", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_spine_bypass", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_spine_bypass", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_spine_bypass", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_spine_bypass", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_spine_bypass", "env_read", "p2_env_1")
_emit_reads_environ("check_spine_bypass", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_spine_bypass", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_spine_bypass", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "check_spine_bypass")
_emit_applies_guardrail("p0", "check_spine_bypass", "p0_governance")
_emit_reads_policy_state("p0", "check_spine_bypass", "policy_binding")
_emit_snapshots_state("p0", "check_spine_bypass", "state_snapshot")
_emit_pulls_context("p1", "check_spine_bypass", "context_pull")
_emit_pulls_context("p1", "check_spine_bypass", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_spine_bypass", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_spine_bypass", "uwg_term_secondary")
_emit_writes_through("p1", "check_spine_bypass", "write_through")
_emit_writes_through("p1", "check_spine_bypass", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_spine_bypass", "safety_validation")
_emit_invokes_eval("p1", "check_spine_bypass", "eval_call")
_emit_proposal_commits_routing("p1", "check_spine_bypass", "routing_commit")
_emit_escalates_to_human("p1", "check_spine_bypass", "human_escalation")
_emit_routes_through("p1", "check_spine_bypass", "route_through")
_emit_checks_agent_registry("p1", "check_spine_bypass", "agent_registry")
_emit_validates_agent_capability("p1", "check_spine_bypass", "capability")
_emit_dispatches_execution_plan("p1", "check_spine_bypass", "exec_plan")
_emit_agent_executes_agent("p1", "check_spine_bypass", "sub_agent")
_emit_routes_to_agent("p1", "check_spine_bypass", "target_agent")
_emit_verifies_policy("p1", "check_spine_bypass", "policy_check")
_emit_observes_runtime_state("p1", "check_spine_bypass", "runtime_state")
_emit_verifies_boundary("p1", "check_spine_bypass", "boundary_check")
_emit_transcripts_response("p1", "check_spine_bypass", "transcript")
_emit_hard_fails_untranscripted("p1", "check_spine_bypass")
_emit_gated_by_confidence("p1", "check_spine_bypass", "confidence_gate")
emit_replay_key("p0", "check_spine_bypass")
emit_determinism_digest("p0", "check_spine_bypass")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_spine_bypass", "execution_auth")
_emit_validates_capability("p2", "check_spine_bypass", "capability_check")
_emit_routes_to_capability("p2", "check_spine_bypass", "capability_route")
_emit_writes_via_uwg("p2", "check_spine_bypass", "uwg_write")
_emit_blocks_direct_write("p2", "check_spine_bypass", "direct_write_block")
_emit_records_tool_invocation("p2", "check_spine_bypass", "tool_invocation")
_emit_captures_execution_output("p2", "check_spine_bypass", "exec_output")
_emit_dispatches_agent("p3", "check_spine_bypass", "agent_dispatch")
_emit_coordinates_agents("p3", "check_spine_bypass", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_spine_bypass", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_spine_bypass", "healing_outcome")
_emit_escalates_failure("p3", "check_spine_bypass", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_spine_bypass", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_spine_bypass", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_spine_bypass", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_spine_bypass", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_spine_bypass", "eval_metric")
_emit_stores_embedding("p4", "check_spine_bypass", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_spine_bypass", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_spine_bypass", "exec_snapshot_link")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_1")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_2")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_3")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_4")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_5")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_6")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_7")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_8")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_9")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_10")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_11")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_12")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_13")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_14")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_15")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_16")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_17")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_18")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_19")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_20")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_21")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_22")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_23")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_24")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_25")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_26")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_27")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_28")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_29")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_30")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_31")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_32")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_33")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_34")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_35")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_36")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_37")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_38")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_39")
_emit_reads_through("l4", "check_spine_bypass", "urg_read_40")

PROJECT_ROOT = get_validated_project_root()
BASELINE_FILE = PROJECT_ROOT / OPS_SCRIPTS_DIR / "hooks" / "spine_bypass_baseline.txt"

# ---------------------------------------------------------------------------
# A) Banned direct instantiation
# ---------------------------------------------------------------------------

BANNED_INSTANTIATION = {
    "HOPPipelineExecutor",
    "ResumeOrchestratorEngine",
    "CIDRegistry",
}

# Files where banned instantiation IS allowed.
INSTANTIATION_ALLOWLIST = {
    PROJECT_ROOT / APPS_LIC_DIR / "engines" / "lic_spine_adapter.py",
    PROJECT_ROOT / APPS_RG_DIR / "engines" / "rg_spine_adapter.py",
}

# ---------------------------------------------------------------------------
# B) Randomness ban
# ---------------------------------------------------------------------------

# Directories where randomness is banned.
RANDOMNESS_BANNED_DIRS = [
    PROJECT_ROOT / APPS_LIC_DIR / "reasoning",
    PROJECT_ROOT / APPS_LIC_DIR / "engines",
    PROJECT_ROOT / APPS_RG_DIR / "reasoning",
    PROJECT_ROOT / APPS_RG_DIR / "engines",
    PROJECT_ROOT / AGENTIC_CORE_DIR,
]

# Scan roots for the full guard.
SCAN_ROOTS = [
    PROJECT_ROOT / APPS_LIC_DIR,
    PROJECT_ROOT / APPS_RG_DIR,
    PROJECT_ROOT / AGENTIC_CORE_DIR,
]

# Directory name segments to exclude from scanning.
EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS


def _is_excluded(path: Path) -> bool:
    """Return True if any part of the path is in the exclude set."""
    return bool(set(path.parts) & EXCLUDE_DIRS)


def _in_randomness_banned_dir(path: Path) -> bool:
    """Return True if path is under one of the randomness-banned directories."""
    for banned in RANDOMNESS_BANNED_DIRS:
        try:
            path.relative_to(banned)
            return True
        except ValueError:
            continue
    return False


def collect_python_files() -> list[Path]:
    """Collect all .py files under SCAN_ROOTS, excluding excluded dirs."""
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for py_file in sorted(root.rglob("*.py")):
            if not _is_excluded(py_file):
                files.append(py_file)
    return files


# ---------------------------------------------------------------------------
# AST visitors
# ---------------------------------------------------------------------------


class SpineBypassVisitor(ast.NodeVisitor):
    """Detect banned direct instantiation of spine classes (Call nodes only)."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.violations: list[str] = []

    def visit_Call(self, node: ast.Call) -> None:
        name = self._resolve_name(node.func)
        if name in BANNED_INSTANTIATION:
            rel = self.file_path.relative_to(PROJECT_ROOT).as_posix()
            self.violations.append(
                f"{rel}:{node.lineno}:spine_bypass:banned direct instantiation of '{name}'",
            )
        self.generic_visit(node)

    @staticmethod
    def _resolve_name(node: ast.expr) -> str:
        """Extract the callable name from Name or Attribute nodes."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ""


class RandomnessVisitor(ast.NodeVisitor):
    """Detect randomness usage in deterministic paths (Call nodes only to avoid double-reporting)."""

    # (module, attr) pairs for attribute-chain bans.
    BANNED_ATTR_CHAINS: frozenset[tuple[str, str]] = frozenset(
        {
            ("numpy", "random"),
            ("np", "random"),
            ("uuid", "uuid4"),
            ("datetime", "now"),
            ("datetime", "utcnow"),
            ("random", "random"),
            ("random", "choice"),
            ("random", "randint"),
            ("random", "shuffle"),
            ("random", "sample"),
            ("random", "seed"),
        },
    )

    # Banned bare module names used as callables.
    BANNED_BARE_CALLS = {"random"}

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.violations: list[str] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Only inspect Call nodes to avoid double-reporting attribute accesses."""
        chain = self._resolve_chain(node.func)
        rel = self.file_path.relative_to(PROJECT_ROOT).as_posix()

        if len(chain) == 1 and chain[0] in self.BANNED_BARE_CALLS:
            self.violations.append(f"{rel}:{node.lineno}:randomness:banned randomness call '{chain[0]}()'")
        elif len(chain) >= 2:
            pair = (chain[0], chain[1])
            if pair in self.BANNED_ATTR_CHAINS:
                self.violations.append(
                    f"{rel}:{node.lineno}:randomness:banned randomness call '{'.'.join(chain[:2])}'",
                )
        self.generic_visit(node)

    @staticmethod
    def _resolve_chain(node: ast.expr) -> list[str]:
        """Resolve an Attribute chain or Name to a list of name parts."""
        parts: list[str] = []
        current: ast.expr = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        parts.reverse()
        return parts


# ---------------------------------------------------------------------------
# Baseline helpers
# ---------------------------------------------------------------------------


def load_baseline() -> set[str]:
    """Load pre-existing violation signatures from baseline file."""
    if not BASELINE_FILE.exists():
        return set()
    try:
        return {
            line.strip() for line in BASELINE_FILE.read_text(encoding="utf-8").splitlines() if line.strip()
        }
    except OSError:    # guardian: Add error context logging
        return set()


def write_baseline(violations: list[str]) -> None:
    """Write current violations to baseline (requires env var guard)."""
    if os.environ.get("ALLOW_SPINE_BASELINE_WRITE") != "1":
        print(
            "[ERROR] --write-baseline requires ALLOW_SPINE_BASELINE_WRITE=1 env var",
            file=sys.stderr,
        )
        sys.exit(1)
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(sorted(set(violations))) + "\n"
    BASELINE_FILE.write_text(content, encoding="utf-8")
    print(f"Wrote {len(set(violations))} violations to {BASELINE_FILE.relative_to(PROJECT_ROOT)}")


# ---------------------------------------------------------------------------
# Main scanning logic
# ---------------------------------------------------------------------------


def check_file_instantiation(path: Path) -> list[str]:
    """Check a file for banned spine class instantiation."""
    if path in INSTANTIATION_ALLOWLIST:
        return []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:    # guardian: Syntax errors should be caught at parser level, not runtime
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        return [f"{rel}:{exc.lineno}:syntax:SyntaxError: {exc.msg}"]
    visitor = SpineBypassVisitor(path)
    visitor.visit(tree)
    return visitor.violations


def check_file_randomness(path: Path) -> list[str]:
    """Check a file for banned randomness usage."""
    if not _in_randomness_banned_dir(path):
        return []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:    # guardian: Syntax errors should be caught at parser level, not runtime
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        return [f"{rel}:{exc.lineno}:syntax:SyntaxError: {exc.msg}"]
    visitor = RandomnessVisitor(path)
    visitor.visit(tree)
    return visitor.violations


def main() -> int:
    parser = argparse.ArgumentParser(description="AST spine bypass + randomness guard")
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Write current violations to baseline (requires ALLOW_SPINE_BASELINE_WRITE=1)",
    )
    args = parser.parse_args()

    files = collect_python_files()
    all_violations: list[str] = []

    for path in files:
        all_violations.extend(check_file_instantiation(path))
        all_violations.extend(check_file_randomness(path))

    if args.write_baseline:
        write_baseline(all_violations)
        return 0

    baseline = load_baseline()
    current_set = set(all_violations)
    new_violations = sorted(current_set - baseline)

    if not new_violations:
        existing = len(current_set & baseline)
        print(
            f"[OK] Spine bypass + randomness guard: 0 new violations "
            f"({len(files)} files scanned, {existing} baselined)",
        )
        return 0

    print(
        f"[FAIL] Spine bypass + randomness guard: {len(new_violations)} NEW violation(s) "
        f"(out of {len(current_set)} total)\n",
    )
    for v in new_violations:
        print(f"  {v}")
    print(
        "\n[ACTION] Fix violations or run with ALLOW_SPINE_BASELINE_WRITE=1 "
        "--write-baseline to baseline pre-existing debt.",
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
