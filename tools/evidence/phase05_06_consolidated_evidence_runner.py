#!/usr/bin/env python3
"""
Phase 5-6 Consolidated Evidence Runner

Generates consolidated evidence for:
- Phase 5: Cross-App Spine Normalization & Contract Lock
- Phase 6: Spine Integrity Guardrail (Structural Enforcement)

Runner requirements:
- Must require: --code-commit <40-hex>
- Must fail if code-commit format invalid or doesn't exist
- Must fail if code-commit == current HEAD (hash-loop prevention)
- Must execute commands via subprocess.run(argv, shell=False, text=True, capture_output=True)
- Must fail if argv[0] contains "pwsh" or "powershell" (argv-level only)
- Must write EXACTLY ONE evidence file: docs/reports/plans/phase_05_06_consolidated.md
"""

import argparse
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


def read_file_content(filepath: Path) -> str:
    """Read file content with error handling."""
    try:
        return filepath.read_text(encoding="utf-8")
    except Exception as e:
        return f"ERROR: Could not read {filepath}: {e}"


def main():
    """Generate Phases 5-6 consolidated evidence."""
    parser = argparse.ArgumentParser(description="Generate Phases 5-6 consolidated evidence")
    parser.add_argument("--code-commit", required=True, help="40-hex commit hash for CODE_COMMIT")
    args = parser.parse_args()

    code_commit = args.code_commit
    if len(code_commit) != 40 or not all(c in "0123456789abcdefABCDEF" for c in code_commit):
        print(f"ERROR: Invalid CODE_COMMIT format: {code_commit}")
        sys.exit(1)

    repo_root = Path(__file__).parent.parent.parent
    evidence_file = repo_root / "docs" / "reports" / "plans" / "phase_05_06_consolidated.md"

    print(f"Generating Phases 5-6 consolidated evidence: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")

    # Verify CODE_COMMIT exists
    rc, out, err = run_cmd(["git", "cat-file", "-e", code_commit], cwd=repo_root)
    if rc != 0:
        print(f"ERROR: CODE_COMMIT does not exist: {code_commit}")
        sys.exit(1)

    # Get current HEAD for hash loop prevention
    rc, out, err = run_cmd(["git", "rev-parse", "HEAD"], cwd=repo_root)
    if rc != 0:
        print(f"ERROR: git rev-parse failed: {err}")
        sys.exit(1)
    current_head = out.strip()

    # Validate CODE_COMMIT != current HEAD (prevent hash loops)
    if code_commit == current_head:
        print(f"ERROR: CODE_COMMIT ({code_commit}) == current HEAD ({current_head})")
        print("This would create a hash loop. Use a commit from before the evidence changes.")
        sys.exit(1)

    # Start building evidence content
    evidence_lines = []
    evidence_lines.append("# Phases 5-6: Spine Adapter Normalization & Structural Enforcement (Consolidated)")
    evidence_lines.append("")
    evidence_lines.append("## Scope")
    evidence_lines.append("Phase 5: Cross-App Spine Normalization & Contract Lock")
    evidence_lines.append("Phase 6: Spine Integrity Guardrail (Structural Enforcement)")
    evidence_lines.append("")

    # CODE_COMMIT
    evidence_lines.append("## CODE_COMMIT")
    evidence_lines.append(code_commit)
    evidence_lines.append("")

    # EVIDENCE_COMMIT (placeholder, will be filled after commit)
    evidence_lines.append("## EVIDENCE_COMMIT")
    evidence_lines.append("PENDING")
    evidence_lines.append("")

    # FILES_CHANGED: derived from git show on CODE_COMMIT
    rc, show_out, show_err = run_cmd(
        ["git", "show", "--name-only", "--pretty=format:", code_commit], cwd=repo_root
    )
    if rc != 0:
        print(f"ERROR: git show on CODE_COMMIT failed: {show_err}")
        sys.exit(1)
    changed_files = [f for f in show_out.strip().splitlines() if f.strip()]
    evidence_lines.append("## FILES_CHANGED (in CODE_COMMIT)")
    evidence_lines.append("```")
    for f in changed_files:
        evidence_lines.append(f)
    evidence_lines.append("```")
    evidence_lines.append("")

    # FILES_CHANGED (in EVIDENCE_COMMIT) - will be determined after commit
    evidence_lines.append("## FILES_CHANGED (in EVIDENCE_COMMIT)")
    evidence_lines.append("```")
    evidence_lines.append("PENDING (will be filled after commit)")
    evidence_lines.append("```")
    evidence_lines.append("")

    # INSPECTED_FILES: context files whose contents are embedded for verification
    inspected = [
        "apps_shared/spine/base_spine_adapter.py",
        "apps_lic/engines/lic_spine_adapter.py",
        "apps_rg/engines/rg_spine_adapter.py",
        "tests/unit_min_deps/test_apps_lic_spine_adapter.py",
        "tests/unit_min_deps/test_apps_rg_spine_adapter.py",
        "tests/unit_min_deps/test_spine_cross_app_contract.py",
        "ops_scripts/ci/check_spine_adapter_contract.py",
        "tools/evidence/phase05_06_consolidated_evidence_runner.py",
    ]
    evidence_lines.append("## INSPECTED_FILES (context snapshots, not necessarily changed)")
    evidence_lines.append("```")
    for f in inspected:
        evidence_lines.append(f)
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
        (
            [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_spine_cross_app_contract.py"],
            "Cross-App Contract Tests",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_spine_bypass.py"],
            "Spine Bypass Check",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_spine_adapter_contract.py"],
            "Spine Adapter Contract Guard",
        ),
        (
            [sys.executable, "-m", "pytest", "-q"],
            "Full Test Suite",
        ),
    ]

    for cmd, title in commands:
        evidence_lines.append(f"## {title}")
        evidence_lines.append("```")
        evidence_lines.append(f"$ {' '.join(cmd)}")

        rc, out, err = run_cmd(cmd, cwd=repo_root)
        evidence_lines.append(out)
        if err:
            evidence_lines.append(f"STDERR: {err}")
        if rc != 0:
            evidence_lines.append(f"EXIT CODE: {rc}")

        evidence_lines.append("```")
        evidence_lines.append("")

    # Embed full contents of inspected files
    evidence_lines.append("## INSPECTED_FILE_CONTENTS")
    evidence_lines.append("")

    for filepath in inspected:
        full_path = repo_root / filepath
        evidence_lines.append(f"### {filepath}")
        evidence_lines.append("```")
        content = read_file_content(full_path)
        evidence_lines.append(content)
        evidence_lines.append("```")
        evidence_lines.append("")

    # Write evidence file with LF line endings and no trailing whitespace
    evidence_content = "\n".join(line.rstrip() for line in evidence_lines)
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(evidence_content, encoding="utf-8", newline="\n")

    # Sanity check: evidence file should not start with Python code
    content_start = evidence_file.read_text(encoding="utf-8")[:200]
    if content_start.strip().startswith("#!/usr/bin/env python") or "def main()" in content_start[:200]:
        print("ERROR: Evidence file appears to contain Python code instead of markdown")
        print("This indicates the runner content was written to the evidence file.")
        sys.exit(1)

    print(f"Evidence generated successfully: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")
    print("EVIDENCE_COMMIT: PENDING (will be filled after commit)")
    print(f"Current HEAD: {current_head}")
    print("\nTo complete the evidence contract:")
    print("1. Commit this evidence file")
    print("2. Update EVIDENCE_COMMIT with the new commit hash")
    print("3. Update FILES_CHANGED (in EVIDENCE_COMMIT) with git show output")


if __name__ == "__main__":
    main()
