"""
Evidence runner for Harden Plan phase.

Generates evidence file with:
- CODE_COMMIT and EVIDENCE_COMMIT
- Verbatim outputs + exit codes for proof commands
- git diff --name-only and git status --porcelain
"""

import subprocess
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    DEFAULT_TIMEOUT,
)


def run_command(argv: list[str], cwd: Path) -> tuple[str, int]:
    """Run command and return (output, exit_code)."""
    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
            shell=False,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=DEFAULT_TIMEOUT,
        )
        output = result.stdout + result.stderr
        return (output, result.returncode)
    except subprocess.TimeoutExpired:
        return ("ERROR: Command timed out after 60 seconds", 1)
    # guardian: allow-silent-swallow
    except Exception as e:
        return (f"ERROR: {e}", 1)


def strip_ansi(text: str) -> str:
    """Strip ANSI escape sequences."""
    import re

    ansi_escape = re.compile("\\x1B(?:[@-Z\\\\-_]|\\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def main():
    repo_root = Path(__file__).parent.parent.parent
    evidence_dir = repo_root / "docs" / REPORTS_DIR / "plans"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_file = evidence_dir / "HARDEN_PLAN_EVIDENCE.md"
    evidence_lines = []
    evidence_lines.append("# Harden Plan Evidence")
    evidence_lines.append("")
    evidence_lines.append("## Scope")
    evidence_lines.append("")
    evidence_lines.append("Hardening specifications for architectural consistency:")
    evidence_lines.append("- Phase 1 Wave 1: L6 authority contradiction resolved, SCOPE sections added")
    evidence_lines.append("- Phase 1 Wave 2: SIGALRM removed, portable timeout patterns implemented")
    evidence_lines.append("- Phase 1 Wave 3: trace_id monotonicity defined (UUIDv7)")
    evidence_lines.append("- Phase 2 Wave 1: Specs organized under docs/specs/hardening/")
    evidence_lines.append("- Phase 2 Wave 2: Consistency check script created")
    evidence_lines.append("")
    output, exit_code = run_command(["git", "rev-parse", "HEAD"], repo_root)
    code_commit = output.strip() if exit_code == 0 else "UNKNOWN"
    evidence_lines.append("## CODE_COMMIT")
    evidence_lines.append("")
    evidence_lines.append(code_commit)
    evidence_lines.append("")
    evidence_lines.append("## EVIDENCE_COMMIT")
    evidence_lines.append("")
    evidence_lines.append("PENDING")
    evidence_lines.append("")
    evidence_lines.append("## FILES_CHANGED_CODE")
    evidence_lines.append("")
    output, exit_code = run_command(
        ["git", "show", "--name-only", "--pretty=format:", code_commit], repo_root
    )
    evidence_lines.append("```")
    evidence_lines.append(strip_ansi(output.strip()))
    evidence_lines.append("```")
    evidence_lines.append("")
    evidence_lines.append("## FILES_CHANGED_EVIDENCE")
    evidence_lines.append("")
    evidence_lines.append("```")
    evidence_lines.append("PENDING")
    evidence_lines.append("```")
    evidence_lines.append("")
    evidence_lines.append("## INSPECTED_FILES")
    evidence_lines.append("")
    evidence_lines.append("```")
    evidence_lines.append("docs/specs/hardening/AUTHORITY_HIERARCHY_INVARIANTS.md")
    evidence_lines.append("docs/specs/hardening/DEGRADATION_MATRIX.md")
    evidence_lines.append("docs/specs/hardening/L0_DECOMPOSITION_SPEC.md")
    evidence_lines.append("docs/specs/hardening/REPLAY_DETERMINISM_RULES.md")
    evidence_lines.append("docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md")
    evidence_lines.append("docs/specs/hardening/L6_DRIFT_SAFEGUARDS_SPEC.md")
    evidence_lines.append("docs/specs/hardening/UWG_ISOLATION_SPEC.md")
    evidence_lines.append("docs/specs/hardening/PTC_SCOPE_LOCK_SPEC.md")
    evidence_lines.append("docs/specs/hardening/POLICY_EPOCH_SPEC.md")
    evidence_lines.append("docs/specs/hardening/LATENCY_BUDGET_SLA_SPEC.md")
    evidence_lines.append("docs/specs/hardening/README.md")
    evidence_lines.append("docs/tools/check_spec_consistency.py")
    evidence_lines.append("```")
    evidence_lines.append("")
    evidence_lines.append("## check_spec_consistency")
    evidence_lines.append("")
    evidence_lines.append("```")
    evidence_lines.append("$ python docs/tools/check_spec_consistency.py")
    output, exit_code = run_command(["python", "docs/tools/check_spec_consistency.py"], repo_root)
    evidence_lines.append(strip_ansi(output))
    if exit_code != 0:
        evidence_lines.append(f"EXIT CODE: {exit_code}")
    evidence_lines.append("```")
    evidence_lines.append("")
    evidence_lines.append("## git_diff_name_only")
    evidence_lines.append("")
    evidence_lines.append("```")
    evidence_lines.append("$ git diff --name-only")
    output, exit_code = run_command(["git", "diff", "--name-only"], repo_root)
    evidence_lines.append(strip_ansi(output))
    if exit_code != 0:
        evidence_lines.append(f"EXIT CODE: {exit_code}")
    evidence_lines.append("```")
    evidence_lines.append("")
    evidence_lines.append("## git_status_porcelain")
    evidence_lines.append("")
    evidence_lines.append("```")
    evidence_lines.append("$ git status --porcelain")
    output, exit_code = run_command(["git", "status", "--porcelain"], repo_root)
    evidence_lines.append(strip_ansi(output))
    if exit_code != 0:
        evidence_lines.append(f"EXIT CODE: {exit_code}")
    evidence_lines.append("```")
    evidence_lines.append("")
    evidence_content = "\n".join(evidence_lines)
    for i, char in enumerate(evidence_content):
        if ord(char) > 127:
            print(f"ERROR: Non-ASCII character at position {i}: {repr(char)}")
            sys.exit(1)
    evidence_file.write_text(evidence_content, encoding="utf-8")
    print(f"Evidence file written: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
