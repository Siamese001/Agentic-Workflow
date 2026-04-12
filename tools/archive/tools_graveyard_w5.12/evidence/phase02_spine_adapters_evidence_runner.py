"""Phase 2 Spine Adapters Evidence Runner - Deterministic Generator.

Generates verbatim evidence for Phase 2 completion.
All commands executed via subprocess with argv arrays (shell=False).
PowerShell detection via argv-level checks only (no output scanning).
"""

import subprocess
import sys
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import REPORTS_DIR


def run_cmd(args, cwd=None):
    """Execute command and return (rc, stdout, stderr)."""
    argv0_lower = str(args[0]).lower()
    if "pwsh" in argv0_lower or "powershell" in argv0_lower:
        print(f"ERROR: PowerShell usage detected in command: {' '.join(args)}")
        sys.exit(1)
    r = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, shell=False, encoding="utf-8", errors="replace"
    )
    return (r.returncode, r.stdout, r.stderr)


def read_file_content(filepath):
    """Read file content as text."""
    try:
        return Path(filepath).read_text(encoding="utf-8")
    except FileNotFoundError:  # guardian: File operations should check existence before access
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    except UnicodeDecodeError as e:  # guardian: Encoding errors should specify fallback encoding strategy
        print(f"ERROR: Unicode decode error in {filepath}: {e}")
        sys.exit(1)
    except OSError as e:  # guardian: Add error context logging
        print(f"ERROR: OS error reading {filepath}: {e}")
        sys.exit(1)


def main():
    """Generate Phase 2 evidence deterministically."""
    if len(sys.argv) < 2:
        print("Usage: python phase02_spine_adapters_evidence_runner.py <CODE_COMMIT>")
        sys.exit(1)
    code_commit = sys.argv[1]
    if len(code_commit) != 40:
        print(f"ERROR: CODE_COMMIT must be 40-hex, got: {code_commit}")
        sys.exit(1)
    repo_root = Path(__file__).parent.parent.parent
    evidence_file = repo_root / "docs" / REPORTS_DIR / "plans" / "phase_02_spine_adapters.md"
    print(f"Generating Phase 2 evidence: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")
    evidence_lines = []
    evidence_lines.append("# Phase 2: LIC + RG Spine Adapters (Deterministic CID)")
    evidence_lines.append("")
    evidence_lines.append("## Scope")
    evidence_lines.append(
        "Implement LIC and RG spine adapters with deterministic CID derivation and unit tests."
    )
    evidence_lines.append("")
    evidence_lines.append("## CODE_COMMIT")
    evidence_lines.append(code_commit)
    evidence_lines.append("")
    evidence_lines.append("## EVIDENCE_COMMIT")
    evidence_lines.append("PENDING")
    evidence_lines.append("")
    rc, out, err = run_cmd(["git", "show", "--name-only", "--pretty=format:", "HEAD"], cwd=repo_root)
    if rc != 0:
        print(f"ERROR: git show failed: {err}")
        sys.exit(1)
    evidence_lines.append("## Files Changed")
    evidence_lines.append("```")
    for line in out.strip().split("\n"):
        if line.strip():
            evidence_lines.append(line.strip())
    evidence_lines.append("```")
    evidence_lines.append("")
    commands = [
        (
            [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_apps_lic_spine_adapter.py"],
            "LIC Unit Tests",
        ),
        (
            [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_apps_rg_spine_adapter.py"],
            "RG Unit Tests",
        ),
        ([sys.executable, "-m", "pytest", "-q"], "Full Test Suite"),
        ([sys.executable, "ops_scripts/ci/check_spine_bypass.py"], "Spine Bypass Check"),
        (["git", "diff", "--stat"], "Git Diff Stat"),
        (["git", "diff"], "Git Full Diff"),
    ]
    for cmd, title in commands:
        evidence_lines.append(f"## {title}")
        evidence_lines.append("```")
        rc, out, err = run_cmd(cmd, cwd=repo_root)
        if rc != 0:
            print(f"ERROR: Command failed: {' '.join(cmd)}")
            print(f"Error: {err}")
            sys.exit(1)
        evidence_lines.append(f"$ {' '.join(cmd)}")
        evidence_lines.append(out.strip())
        if err:
            evidence_lines.append(f"STDERR: {err.strip()}")
        evidence_lines.append("```")
        evidence_lines.append("")
    files_to_include = [
        "apps_lic/engines/lic_spine_adapter.py",
        "apps_rg/engines/rg_spine_adapter.py",
        "tests/unit_min_deps/test_apps_lic_spine_adapter.py",
        "tests/unit_min_deps/test_apps_rg_spine_adapter.py",
        "tools/evidence/phase02_spine_adapters_evidence_runner.py",
    ]
    for filepath in files_to_include:
        evidence_lines.append(f"## {filepath}")
        evidence_lines.append("```python")
        content = read_file_content(repo_root / filepath)
        evidence_lines.append(content)
        evidence_lines.append("```")
        evidence_lines.append("")
    evidence_content = "\n".join(line.rstrip() for line in evidence_lines)
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(evidence_content, encoding="utf-8", newline="\n")
    print(f"Evidence generated successfully at: {evidence_file}")


if __name__ == "__main__":
    main()
