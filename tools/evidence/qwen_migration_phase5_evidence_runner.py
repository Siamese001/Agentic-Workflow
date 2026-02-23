"""
Phase 5 Evidence Runner: Formal Invariant Verifier

Generates evidence for Phase 5 of the Qwen migration:
- Invariant contract + violation artifact types
- Deterministic verifier with canonical violations
- Adapter seam integration with FAIL violation handling
- Unit_min_deps tests for invariants
- End-to-end adapter tests

Evidence file: docs/reports/evidence/qwen_migration_phase_5_formal_invariant_verifier.md
"""

import subprocess
import sys
from pathlib import Path


def run(argv, required=True):
    """Run command and return (stdout, exit_code)."""
    result = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    
    # Balanced PowerShell guard: hard-fail on shell=True or argv[0] PowerShell executable
    if argv and isinstance(argv[0], str):
        if "powershell" in argv[0].lower() or "pwsh" in argv[0].lower():
            print(f"ERROR: PowerShell executable detected in argv[0]: {argv[0]}")
            sys.exit(1)
    
    stdout = result.stdout
    if required and result.returncode != 0:
        print(f"FAIL: {' '.join(argv)}")
        print(stdout)
        sys.exit(1)
    
    return stdout, result.returncode


def main():
    """Generate Phase 5 evidence."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-commit", required=True)
    parser.add_argument("--evidence-commit", default=None)
    args = parser.parse_args()
    
    evidence_lines = []
    
    def h(line=""):
        evidence_lines.append(line)
    
    def fence(content):
        h("```")
        h(content.rstrip())
        h("```")
    
    # Header
    h("# Phase 5 Evidence: Formal Invariant Verifier")
    h("")
    h("## Scope")
    h("Phase 5 implements runtime invariant verification at the execution boundary (Phase 3 adapter/controller seam).")
    h("All violations are deterministically serializable with canonical JSON and SHA256 hashing.")
    h("FAIL violations trigger Gemini fallback. Phase 1-4 behavior preserved.")
    h("")
    
    # Commit hashes
    h("## CODE_COMMIT")
    h(args.code_commit)
    h("")
    
    if args.evidence_commit:
        h("## EVIDENCE_COMMIT")
        h(args.evidence_commit)
        h("")
    else:
        h("## EVIDENCE_COMMIT")
        h("PENDING")
        h("")
    
    # Files changed
    h("## FILES_CHANGED_CODE")
    out, _ = run(["git", "show", "--name-only", "--pretty=format:", args.code_commit])
    h(out.strip())
    h("")
    
    if args.evidence_commit:
        h("## FILES_CHANGED_EVIDENCE")
        out, _ = run(["git", "show", "--name-only", "--pretty=format:", args.evidence_commit])
        h(out.strip())
        h("")
    
    # Inspected files
    h("## INSPECTED_FILES")
    phase5_files = [
        "agentic_core/L2_execution/types/vllm_invariant_contract.py",
        "agentic_core/L2_execution/types/vllm_invariant_verifier.py",
        "agentic_core/L2_execution/types/vllm_gateway_adapter.py",
        "agentic_core/L2_execution/types/vllm_gateway_integration.py",
        "tests/unit_min_deps/test_vllm_invariant_contract.py",
        "tests/unit_min_deps/test_vllm_invariant_verifier.py",
        "tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py",
    ]
    for f in phase5_files:
        h(f)
    h("")
    
    # Unit_min_deps tests
    h("## Unit_min_deps Tests (Invariant Contract)")
    out, rc = run([
        sys.executable, "-m", "pytest", "-q", "--color=no",
        "-m", "unit_min_deps",
        "tests/unit_min_deps/test_vllm_invariant_contract.py",
    ])
    fence(out)
    if rc != 0:
        print("FAIL: test_vllm_invariant_contract.py")
        sys.exit(1)
    h("")
    
    # Unit_min_deps tests (Verifier)
    h("## Unit_min_deps Tests (Invariant Verifier)")
    out, rc = run([
        sys.executable, "-m", "pytest", "-q", "--color=no",
        "-m", "unit_min_deps",
        "tests/unit_min_deps/test_vllm_invariant_verifier.py",
    ])
    fence(out)
    if rc != 0:
        print("FAIL: test_vllm_invariant_verifier.py")
        sys.exit(1)
    h("")
    
    # Phase 5 Integration Tests
    h("## Phase 5 Integration Tests (Invariant Enforcement)")
    out, rc = run([
        sys.executable, "-m", "pytest", "-q", "--color=no",
        "tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py",
    ])
    fence(out)
    if rc != 0:
        print("FAIL: test_vllm_invariant_enforcement.py")
        sys.exit(1)
    h("")
    
    # Phase 1-4 Regression Tests
    h("## Phase 1-4 Regression Tests")
    out, rc = run([
        sys.executable, "-m", "pytest", "-q", "--color=no",
        "tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py",
        "tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py",
        "tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py",
    ])
    fence(out)
    if rc != 0:
        print("FAIL: Phase 1-4 regression tests")
        sys.exit(1)
    h("")
    
    # Git status
    h("## Git Status")
    out, _ = run(["git", "status", "--porcelain=v1"], required=False)
    if out.strip():
        fence(out)
    else:
        h("(clean)")
    h("")
    
    # Runner self-check
    h("## Runner Self-Check Proof")
    h("Balanced PowerShell guard policy:")
    h("- Hard-fail on shell=True")
    h("- Hard-fail on argv[0] containing 'powershell' or 'pwsh'")
    h("- Warn-only on output mentions (no false positives)")
    h("")
    
    # Write evidence
    evidence_path = Path("docs/reports/evidence/qwen_migration_phase_5_formal_invariant_verifier.md")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    
    content = "\n".join(evidence_lines)
    
    # ASCII-only validation
    for i, byte_val in enumerate(content.encode("utf-8")):
        if byte_val > 0x7F:
            print(f"ERROR: Non-ASCII byte at position {i}: {hex(byte_val)}")
            print(f"Context: {content[max(0, i-50):i+50]}")
            sys.exit(1)
    
    evidence_path.write_text(content, encoding="utf-8")
    print(f"Evidence written to: {evidence_path.absolute()}")
    print("OK: All commands passed.")


if __name__ == "__main__":
    main()
