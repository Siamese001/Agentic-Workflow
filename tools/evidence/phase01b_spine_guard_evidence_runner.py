"""
Phase 1B evidence runner — Python-only, shell=False, no PowerShell.

Executes commands via subprocess argv arrays, captures output,
writes evidence to: docs/reports/plans/phase_01b_ci_spine_guard.md
"""

from __future__ import annotations

import subprocess
import sys

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
    get_validated_project_root,
)

PROJECT_ROOT = get_validated_project_root()
EVIDENCE_PATH = PROJECT_ROOT / "docs" / REPORTS_DIR / "plans" / "phase_01b_ci_spine_guard.md"
GUARD_SCRIPT = PROJECT_ROOT / OPS_SCRIPTS_DIR / "ci" / "check_spine_bypass.py"
WORKFLOW_FILE = PROJECT_ROOT / ".github" / "workflows" / "spine-determinism-guard.yml"
BASELINE_FILE = PROJECT_ROOT / OPS_SCRIPTS_DIR / "hooks" / "spine_bypass_baseline.txt"


def run(argv: list[str]) -> tuple[int, str]:
    """Run a command with shell=False, return (returncode, combined output)."""
    result = subprocess.run(
        argv,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        shell=False,
    )
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    combined = stdout + stderr
    # Check only stderr for PowerShell invocation evidence.
    # stdout may contain diff content that legitimately references shell names.
    stderr_lines = [line for line in stderr.splitlines() if not line.strip().startswith("PS ")]
    stderr_check = "\n".join(stderr_lines)
    if "pwsh" in stderr_check.lower() or "powershell" in stderr_check.lower():
        print("ABORT: PowerShell detected in stderr output.", file=sys.stderr)
        sys.exit(1)
    return result.returncode, combined


def section(title: str, content: str) -> str:
    return "## " + title + "\n\n```\n" + content.strip() + "\n```\n\n"


def main() -> None:
    nl = "\n"

    print("Running check_spine_bypass.py...")
    guard_rc, guard_out = run([sys.executable, "ops_scripts/ci/check_spine_bypass.py"])

    print("Running git diff --stat...")
    stat_rc, stat_out = run(["git", "diff", "--stat"])

    print("Running git diff...")
    diff_rc, diff_out = run(["git", "diff"])

    guard_content = GUARD_SCRIPT.read_text(encoding="utf-8")
    workflow_content = WORKFLOW_FILE.read_text(encoding="utf-8")
    baseline_lines = (
        len(BASELINE_FILE.read_text(encoding="utf-8").splitlines()) if BASELINE_FILE.exists() else 0
    )

    sec_guard = section(
        "Command: python ops_scripts/ci/check_spine_bypass.py",
        "Exit code: " + str(guard_rc) + nl + nl + guard_out,
    )
    sec_stat = section(
        "Command: git diff --stat",
        "Exit code: " + str(stat_rc) + nl + nl + stat_out,
    )
    sec_diff = section(
        "Command: git diff",
        "Exit code: " + str(diff_rc) + nl + nl + diff_out,
    )

    parts = [
        "# Phase 1B: AST Spine Bypass + Randomness CI Guard — Evidence",
        "",
        "AST-based CI guard preventing spine bypass and randomness usage in deterministic paths.",
        "Baseline captures "
        + str(baseline_lines)
        + " pre-existing violations; only NEW violations fail the build.",
        "",
        "## Commit Hash",
        "",
        "PENDING",
        "",
        "## Files Changed",
        "",
        "- `ops_scripts/ci/check_spine_bypass.py` (created)",
        "- `ops_scripts/hooks/spine_bypass_baseline.txt` (created)",
        "- `.github/workflows/spine-determinism-guard.yml` (created)",
        "- `tools/evidence/phase01b_spine_guard_evidence_runner.py` (created)",
        "- `docs/reports/plans/phase_01b_ci_spine_guard.md` (created)",
        "",
        sec_guard,
        sec_stat,
        sec_diff,
        "## ops_scripts/ci/check_spine_bypass.py (verbatim)",
        "",
        "```python",
        guard_content,
        "```",
        "",
        "## .github/workflows/spine-determinism-guard.yml (verbatim)",
        "",
        "```yaml",
        workflow_content,
        "```",
        "",
    ]
    md = nl.join(parts)

    # Strip trailing whitespace and enforce LF line endings.
    md = "\n".join(line.rstrip() for line in md.splitlines()) + "\n"
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(md.encode("utf-8"))
    print("Evidence written to: " + str(EVIDENCE_PATH))

    if guard_rc != 0:
        print("FAIL: check_spine_bypass.py returned non-zero.", file=sys.stderr)
        sys.exit(guard_rc)


if __name__ == "__main__":
    main()
