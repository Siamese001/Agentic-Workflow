#!/usr/bin/env python3
"""Phases 3-4 Consolidated Evidence Runner.

Single evidence file for entire Phases 3-4 run.
Python-only execution, argv-level PowerShell detection, LF endings.
"""

import subprocess
import sys
from pathlib import Path


def run_cmd(args, cwd=None):
    """Execute command and return (rc, stdout, stderr)."""
    # PowerShell detection at argv level only
    argv0_lower = str(args[0]).lower()
    if "pwsh" in argv0_lower or "powershell" in argv0_lower:
        print(f"ERROR: PowerShell usage detected in command: {' '.join(args)}")
        sys.exit(1)

    r = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, shell=False, encoding="utf-8", errors="replace"
    )
    return r.returncode, r.stdout, r.stderr


def read_file_content(filepath):
    """Read file content as text."""
    try:
        return Path(filepath).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"ERROR: Unicode decode error in {filepath}: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: OS error reading {filepath}: {e}")
        sys.exit(1)


def main():
    """Generate Phases 3-4 consolidated evidence."""
    repo_root = Path(__file__).parent.parent.parent
    evidence_file = repo_root / "docs" / "reports" / "plans" / "phase_03_04_consolidated.md"

    print(f"Generating Phases 3-4 consolidated evidence: {evidence_file}")

    # Start building evidence content
    evidence_lines = []

    # Header with scope
    evidence_lines.append("# Phases 3-4: Spine Adapter Production Closure (Consolidated)")
    evidence_lines.append("")
    evidence_lines.append("## Scope")
    evidence_lines.append("Phase 3: Single-evidence-per-response contract implementation")
    evidence_lines.append(
        "Phase 4: Production-grade spine adapter hardening (CID invariants, import stability, governance)"
    )
    evidence_lines.append("")

    # FINAL_HEAD
    rc, out, err = run_cmd(["git", "rev-parse", "HEAD"], cwd=repo_root)
    if rc != 0:
        print(f"ERROR: git rev-parse failed: {err}")
        sys.exit(1)
    final_head = out.strip()
    evidence_lines.append("## FINAL_HEAD")
    evidence_lines.append(final_head)
    evidence_lines.append("")

    # CODE_SCOPE
    evidence_lines.append("## CODE_SCOPE")
    evidence_lines.append("```")
    evidence_lines.append("Phase 3:")
    evidence_lines.append("  tools/evidence/phase03_04_consolidated_evidence_runner.py")
    evidence_lines.append("Phase 4:")
    evidence_lines.append("  apps_lic/engines/__init__.py")
    evidence_lines.append("  apps_rg/engines/__init__.py")
    evidence_lines.append("  tests/unit_min_deps/test_apps_lic_spine_adapter.py")
    evidence_lines.append("  tests/unit_min_deps/test_apps_rg_spine_adapter.py")
    evidence_lines.append("```")
    evidence_lines.append("")

    # Command outputs
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
        (["git", "show", "--name-only", "--pretty=format:", "HEAD"], "Files Changed in HEAD"),
        (["git", "diff", "--stat"], "Git Diff Stat"),
        (["git", "diff"], "Git Full Diff"),
    ]

    for cmd, title in commands:
        evidence_lines.append(f"## {title}")
        evidence_lines.append("```")
        evidence_lines.append(f"$ {' '.join(cmd)}")
        rc, out, err = run_cmd(cmd, cwd=repo_root)
        if rc != 0:
            print(f"WARNING: Command failed: {' '.join(cmd)}")
            print(f"Exit code: {rc}")
            print(f"Stderr: {err}")
            # Don't exit on test failures, capture them in evidence

        evidence_lines.append(out.strip() if out else "(no output)")
        if err:
            evidence_lines.append(f"STDERR: {err.strip()}")
        evidence_lines.append("```")
        evidence_lines.append("")

    # File contents - dynamically determine which files were changed
    files_to_include = [
        "tools/evidence/phase03_04_consolidated_evidence_runner.py",
        "apps_lic/engines/__init__.py",
        "apps_rg/engines/__init__.py",
        "tests/unit_min_deps/test_apps_lic_spine_adapter.py",
        "tests/unit_min_deps/test_apps_rg_spine_adapter.py",
    ]

    for filepath in files_to_include:
        full_path = repo_root / filepath
        if full_path.exists():
            evidence_lines.append(f"## {filepath}")
            evidence_lines.append("```python")
            content = read_file_content(full_path)
            evidence_lines.append(content)
            evidence_lines.append("```")
            evidence_lines.append("")

    # Write evidence file with LF line endings and no trailing whitespace
    evidence_content = "\n".join(line.rstrip() for line in evidence_lines)
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(evidence_content, encoding="utf-8", newline="\n")

    print(f"Evidence generated successfully: {evidence_file}")
    print(f"FINAL_HEAD: {final_head}")


if __name__ == "__main__":
    main()
