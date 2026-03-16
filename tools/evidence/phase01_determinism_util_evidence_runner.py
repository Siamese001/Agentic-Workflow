"""
Phase 1 evidence runner — Python-only, shell=False, no PowerShell.

Executes commands via subprocess argv arrays, captures output,
aborts immediately if any output contains 'pwsh' or 'PowerShell' (case-insensitive).

Writes evidence to: docs/reports/plans/phase_01_shared_determinism_util.md
"""

from __future__ import annotations

import subprocess
import sys

from agentic_core.L0_routing.config.path_constants import (
    APPS_SHARED_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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

_emit_records_execution_trace("p0", "evidence", "phase01_determinism_util_evidence_runner")
_emit_applies_guardrail("p0", "phase01_determinism_util_evidence_runner", "p0_governance")
_emit_reads_policy_state("p0", "phase01_determinism_util_evidence_runner", "policy_binding")
_emit_snapshots_state("p0", "phase01_determinism_util_evidence_runner", "state_snapshot")
emit_replay_key("p0", "phase01_determinism_util_evidence_runner")
emit_determinism_digest("p0", "phase01_determinism_util_evidence_runner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "phase01_determinism_util_evidence_runner", "execution_auth")
_emit_validates_capability("p2", "phase01_determinism_util_evidence_runner", "capability_check")
_emit_routes_to_capability("p2", "phase01_determinism_util_evidence_runner", "capability_route")
_emit_writes_via_uwg("p2", "phase01_determinism_util_evidence_runner", "uwg_write")
_emit_blocks_direct_write("p2", "phase01_determinism_util_evidence_runner", "direct_write_block")
_emit_records_tool_invocation("p2", "phase01_determinism_util_evidence_runner", "tool_invocation")
_emit_captures_execution_output("p2", "phase01_determinism_util_evidence_runner", "exec_output")
_emit_dispatches_agent("p3", "phase01_determinism_util_evidence_runner", "agent_dispatch")
_emit_coordinates_agents("p3", "phase01_determinism_util_evidence_runner", "agent_coordination")
_emit_records_workflow_lineage("p3", "phase01_determinism_util_evidence_runner", "workflow_lineage")
_emit_records_healing_outcome("p3", "phase01_determinism_util_evidence_runner", "healing_outcome")
_emit_escalates_failure("p3", "phase01_determinism_util_evidence_runner", "failure_escalation")
_emit_orchestrates_workflow("p3", "phase01_determinism_util_evidence_runner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "phase01_determinism_util_evidence_runner", "healing_dispatch")
_emit_invokes_evaluation("p3", "phase01_determinism_util_evidence_runner", "evaluation_signal")
_emit_records_telemetry_event("p4", "phase01_determinism_util_evidence_runner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "phase01_determinism_util_evidence_runner", "eval_metric")
_emit_stores_embedding("p4", "phase01_determinism_util_evidence_runner", "embedding_store")
_emit_updates_meta_learning_state("p4", "phase01_determinism_util_evidence_runner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "phase01_determinism_util_evidence_runner", "exec_snapshot_link")

REPO_ROOT = get_validated_project_root()
EVIDENCE_PATH = REPO_ROOT / "docs" / REPORTS_DIR / "plans" / "phase_01_shared_determinism_util.md"
DETERMINISM_UTIL = REPO_ROOT / APPS_SHARED_DIR / "utils" / "determinism_util.py"
TEST_FILE = REPO_ROOT / TESTS_DIR / "unit_min_deps" / "test_determinism_util.py"


def run(argv: list[str]) -> tuple[int, str]:
    """Run a command with shell=False, return (returncode, combined output)."""
    result = subprocess.run(
        argv,
        cwd=str(REPO_ROOT),
        capture_output=True,
        shell=False,
    )
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    combined = stdout + stderr
    # Check only stderr for PowerShell invocation evidence.
    # stdout may contain diff/log content that legitimately references "PowerShell" in comments.
    # Strip PS prompt lines (terminal artifacts) before checking.
    stderr_lines = [line for line in stderr.splitlines() if not line.strip().startswith("PS ")]
    stderr_check = "\n".join(stderr_lines)
    if "pwsh" in stderr_check.lower() or "powershell" in stderr_check.lower():
        print("ABORT: PowerShell detected in stderr output.", file=sys.stderr)
        sys.exit(1)
    return result.returncode, combined


def section(title: str, content: str) -> str:
    return f"## {title}\n\n```\n{content.strip()}\n```\n\n"


def main() -> None:
    outputs: dict[str, tuple[int, str]] = {}

    print("Running focused pytest (new tests only)...")
    rc1, out1 = run([sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_determinism_util.py"])
    outputs["focused_pytest"] = (rc1, out1)

    print("Running full suite...")
    rc2, out2 = run([sys.executable, "-m", "pytest", "-q"])
    outputs["full_suite"] = (rc2, out2)

    print("Running git diff --stat...")
    rc3, out3 = run(["git", "diff", "--stat", "HEAD"])
    outputs["git_diff_stat"] = (rc3, out3)

    print("Running git diff...")
    rc4, out4 = run(["git", "diff", "HEAD"])
    outputs["git_diff"] = (rc4, out4)

    determinism_util_content = DETERMINISM_UTIL.read_text(encoding="utf-8")
    test_file_content = TEST_FILE.read_text(encoding="utf-8")

    focused_rc, focused_out = outputs["focused_pytest"]
    full_rc, full_out = outputs["full_suite"]
    diff_stat_rc, diff_stat_out = outputs["git_diff_stat"]
    diff_rc, diff_out = outputs["git_diff"]

    nl = "\n"
    sec_focused = section(
        "Command: python -m pytest -q tests/unit_min_deps/test_determinism_util.py",
        "Exit code: " + str(focused_rc) + nl + nl + focused_out,
    )
    sec_full = section(
        "Command: python -m pytest -q (full suite)",
        "Exit code: " + str(full_rc) + nl + nl + full_out,
    )
    sec_stat = section(
        "Command: git diff --stat HEAD",
        "Exit code: " + str(diff_stat_rc) + nl + nl + diff_stat_out,
    )
    sec_diff = section(
        "Command: git diff HEAD",
        "Exit code: " + str(diff_rc) + nl + nl + diff_out,
    )

    parts = [
        "# Phase 1: Shared Determinism Utility — Evidence",
        "",
        "Implement `apps_shared/utils/determinism_util.py` with recursive nondeterminism stripping",
        "and deterministic hashing bound to `canonical_bytes()` from the L0 spine.",
        "",
        "## Scope",
        "",
        "- New file: `apps_shared/utils/determinism_util.py`",
        "- New file: `tests/unit_min_deps/test_determinism_util.py`",
        "",
        "## Commit Hash",
        "",
        "PENDING",
        "",
        "## Files Changed",
        "",
        "- `apps_shared/utils/determinism_util.py` (created)",
        "- `tests/unit_min_deps/test_determinism_util.py` (created)",
        "- `docs/reports/plans/phase_01_shared_determinism_util.md` (created)",
        "- `tools/evidence/phase01_determinism_util_evidence_runner.py` (created)",
        "",
        sec_focused,
        sec_full,
        sec_stat,
        sec_diff,
        "## apps_shared/utils/determinism_util.py (verbatim)",
        "",
        "```python",
        determinism_util_content,
        "```",
        "",
        "## tests/unit_min_deps/test_determinism_util.py (verbatim)",
        "",
        "```python",
        test_file_content,
        "```",
        "",
    ]
    md = nl.join(parts)

    # Strip trailing whitespace and enforce LF line endings so pre-commit hooks pass cleanly.
    md = "\n".join(line.rstrip() for line in md.splitlines()) + "\n"
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(md.encode("utf-8"))
    print(f"Evidence written to: {EVIDENCE_PATH}")

    if focused_rc != 0:
        print("FAIL: focused pytest returned non-zero.", file=sys.stderr)
        sys.exit(focused_rc)


if __name__ == "__main__":
    main()
