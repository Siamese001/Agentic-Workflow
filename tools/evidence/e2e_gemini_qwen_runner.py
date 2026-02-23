"""
Phase 2 Evidence Runner: E2E Gemini 2.5 Pro + Qwen vLLM Deterministic Proof.

Waves 1-3:
  Wave 1 — Run pytest targeted suite; print full output verbatim.
  Wave 2 — In-process inline extraction + per-hash validations.
  Wave 3 — Runner self-check + PowerShell guard.

Evidence file: docs/reports/evidence/e2e_gemini_qwen_proof.md
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Self-check: assert no PowerShell in argv[0] of any subprocess call
# ---------------------------------------------------------------------------
_SHELL_FALSE_ENFORCED = True  # All subprocess calls in this runner use shell=False


def _assert_no_powershell(argv: list[str]) -> None:
    """Hard-fail if argv[0] resolves to a PowerShell executable."""
    if not argv:
        return
    basename = Path(argv[0]).name.lower()  # guardian: allow-path_fragility
    if basename in ("pwsh", "pwsh.exe", "powershell", "powershell.exe"):
        print(f"ERROR: PowerShell executable detected in argv[0]: {argv[0]}")
        sys.exit(1)


def run(argv: list[str], required: bool = True) -> tuple[str, int]:
    """Run command via subprocess.run(argv, shell=False) and return (stdout, exit_code)."""
    _assert_no_powershell(argv)
    result = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,  # BINDING: shell=False always
    )
    combined = result.stdout + result.stderr
    # Strip ANSI escape sequences
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    combined = ansi_escape.sub("", combined)
    # Replace non-ASCII with '?'
    combined = combined.encode("ascii", errors="replace").decode("ascii")
    if required and result.returncode != 0:
        print(f"FAIL: command exited {result.returncode}: {' '.join(argv)}")
        print(combined)
        sys.exit(1)
    return combined, result.returncode


def validate_hex64(value: str, field_name: str) -> None:
    """Hard-fail if value does not match ^[0-9a-f]{64}$."""
    pattern = re.compile(r"^[0-9a-f]{64}$")
    if not pattern.match(value):
        print(f"ERROR: {field_name} is not 64-hex: {value!r}")
        sys.exit(1)


def ascii_only(text: str) -> str:
    """Replace any non-ASCII bytes with '?'."""
    return text.encode("ascii", errors="replace").decode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description="E2E Gemini/Qwen evidence runner")
    parser.add_argument("--code-commit", required=True, help="40-hex CODE_COMMIT")
    parser.add_argument("--evidence-commit", default=None, help="40-hex EVIDENCE_COMMIT (seal mode)")
    args = parser.parse_args()

    evidence_lines: list[str] = []

    def h(line: str = "") -> None:
        evidence_lines.append(ascii_only(line))

    def fence(content: str) -> None:
        h("```")
        h(content.rstrip())
        h("```")

    # -----------------------------------------------------------------------
    # Wave 1 — Print scope + run pytest
    # -----------------------------------------------------------------------
    print("TEST_SCOPE=TARGETED")
    print("TEST_TARGETS:")
    print("  python -m pytest -q tests/integration_e2e/test_gemini_qwen_e2e.py")
    print()

    pytest_argv = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--color=no",
        "-m",
        "e2e",
        "tests/integration_e2e/test_gemini_qwen_e2e.py",
    ]
    pytest_out, pytest_rc = run(pytest_argv, required=False)

    print("=== PYTEST OUTPUT ===")
    print(pytest_out)
    print("=====================")

    if pytest_rc != 0:
        print(f"FAIL: pytest exited {pytest_rc}")
        sys.exit(1)

    print("OK: pytest passed (exit 0)")
    print()

    # -----------------------------------------------------------------------
    # Wave 2 — In-process inline extraction + per-hash validations
    # -----------------------------------------------------------------------
    # Import the pipeline helper directly from the test module
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # guardian: allow-global_mutation
    from tests.integration_e2e.test_gemini_qwen_e2e import (
        ENGINE_GEMINI,
        ENGINE_QWEN,
        _make_forced_invariant_violation,
        run_e2e_pipeline,
    )

    # --- Gemini execution ---
    gemini_r1 = run_e2e_pipeline(route_override=ENGINE_GEMINI)
    gemini_r2 = run_e2e_pipeline(route_override=ENGINE_GEMINI)
    gemini_engine = gemini_r1["engine_name"]
    gemini_replay = gemini_r1["replay_hash"]
    gemini_deterministic = gemini_r1["replay_hash"] == gemini_r2["replay_hash"]

    validate_hex64(gemini_replay, "gemini_replay_hash")

    print("=== GEMINI EXECUTION ===")
    print(f"  engine_name={gemini_engine}")
    print(f"  replay_hash={gemini_replay}")
    print(f"  OK: replay_hash validated as 64-hex: {gemini_replay}")
    print()

    # --- Qwen execution ---
    qwen_r1 = run_e2e_pipeline(route_override=ENGINE_QWEN)
    qwen_r2 = run_e2e_pipeline(route_override=ENGINE_QWEN)
    qwen_engine = qwen_r1["engine_name"]
    qwen_replay = qwen_r1["replay_hash"]
    qwen_deterministic = qwen_r1["replay_hash"] == qwen_r2["replay_hash"]

    validate_hex64(qwen_replay, "qwen_replay_hash")

    print("=== QWEN EXECUTION ===")
    print(f"  engine_name={qwen_engine}")
    print(f"  replay_hash={qwen_replay}")
    print(f"  OK: replay_hash validated as 64-hex: {qwen_replay}")
    print()

    # --- Determinism lock ---
    if not gemini_deterministic:
        print("FAIL: gemini replay_hash not deterministic across re-run")
        sys.exit(1)
    if not qwen_deterministic:
        print("FAIL: qwen replay_hash not deterministic across re-run")
        sys.exit(1)

    print("=== DETERMINISM LOCK ===")
    print(f"  gemini_replay_deterministic={gemini_deterministic}")
    print(f"  qwen_replay_deterministic={qwen_deterministic}")
    print()

    # --- Negative control ---
    neg_result = run_e2e_pipeline(
        route_override=ENGINE_GEMINI,
        force_invariant_fail=True,
        forced_violation=_make_forced_invariant_violation(),
    )
    neg_result2 = run_e2e_pipeline(
        route_override=ENGINE_GEMINI,
        force_invariant_fail=True,
        forced_violation=_make_forced_invariant_violation(),
    )

    neg_route_to_gemini = neg_result["route_to_gemini"]
    neg_failure_type = neg_result["failure_type"]
    neg_violations = neg_result["invariant_violations"]
    neg_replay = neg_result["replay_hash"]
    neg_replay2 = neg_result2["replay_hash"]

    if not neg_route_to_gemini:
        print("FAIL: negative control route_to_gemini must be True")
        sys.exit(1)
    if neg_failure_type != "INVARIANT_VIOLATION":
        print(f"FAIL: negative control failure_type must be 'INVARIANT_VIOLATION', got {neg_failure_type!r}")
        sys.exit(1)
    if len(neg_violations) < 1:
        print("FAIL: negative control must have >= 1 violation")
        sys.exit(1)

    violation_hash = neg_violations[0].violation_hash()
    validate_hex64(violation_hash, "violation_hash")
    validate_hex64(neg_replay, "negative_control_replay_hash")

    if neg_replay != neg_replay2:
        print(f"FAIL: negative control replay_hash not deterministic: {neg_replay} != {neg_replay2}")
        sys.exit(1)

    print("=== NEGATIVE CONTROL ===")
    print(f"  route_to_gemini={neg_route_to_gemini}")
    print(f"  failure_type={neg_failure_type}")
    print(f"  violation_hash={violation_hash}")
    print(f"  OK: violation_hash validated as 64-hex: {violation_hash}")
    print(f"  replay_hash={neg_replay}")
    print(f"  OK: replay_hash validated as 64-hex: {neg_replay}")
    print()

    # -----------------------------------------------------------------------
    # Wave 3 — Runner self-check + PowerShell guard
    # -----------------------------------------------------------------------
    print("=== RUNNER SELF-CHECK ===")
    print(f"  shell=False enforced: {_SHELL_FALSE_ENFORCED}")
    print("  PowerShell guard: hard-fail on argv[0] containing pwsh/powershell")
    print("  All subprocess calls use shell=False")
    print()

    # Check if captured output contains PowerShell/pwsh text (warn only)
    if "powershell" in pytest_out.lower() or "pwsh" in pytest_out.lower():
        print("WARNING: 'PowerShell/pwsh' text detected in captured output (warn only, not a fail)")
    else:
        print("  OK: no PowerShell/pwsh text in captured output")
    print()

    # -----------------------------------------------------------------------
    # Build evidence file
    # -----------------------------------------------------------------------
    h("# E2E Gemini 2.5 Pro + Qwen vLLM Deterministic Proof")
    h("")
    h("## Scope")
    h("End-to-end deterministic proof: Gemini 2.5 Pro path, Qwen vLLM path,")
    h("determinism lock, invariant enforcement, negative control.")
    h("No external network calls. Production routing + execution surfaces.")
    h("Model transport replaced with deterministic stub (minimum seam).")
    h("")

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

    # FILES_CHANGED_CODE
    h("## FILES_CHANGED_CODE")
    out, _ = run(["git", "show", "--name-only", "--pretty=format:", args.code_commit])
    h(out.strip())
    h("")

    if args.evidence_commit:
        h("## FILES_CHANGED_EVIDENCE")
        out, _ = run(["git", "show", "--name-only", "--pretty=format:", args.evidence_commit])
        h(out.strip())
        h("")

    h("## INSPECTED_FILES")
    for f in [
        "tests/integration_e2e/__init__.py",
        "tests/integration_e2e/test_gemini_qwen_e2e.py",
        "tools/evidence/e2e_gemini_qwen_runner.py",
        "agentic_core/L2_execution/types/vllm_gateway_adapter.py",
        "agentic_core/L2_execution/types/vllm_gateway_integration.py",
        "agentic_core/L2_execution/types/vllm_invariant_contract.py",
        "agentic_core/L2_execution/types/vllm_invariant_verifier.py",
        "agentic_core/L2_execution/types/vllm_replay_validator.py",
        "agentic_core/L2_execution/types/vllm_infrastructure_fingerprint.py",
        "agentic_core/L2_execution/types/llm_replay_types.py",
    ]:
        h(f)
    h("")

    # Pytest output
    h("## Pytest Output")
    h("```")
    h("TEST_SCOPE=TARGETED")
    h("TEST_TARGETS:")
    h("  python -m pytest -q tests/integration_e2e/test_gemini_qwen_e2e.py")
    h("```")
    h("")
    fence(pytest_out)
    h("")

    # Gemini execution
    h("## Gemini Execution")
    h("```")
    h(f"engine_name={gemini_engine}")
    h(f"replay_hash={gemini_replay}")
    h(f"OK: replay_hash validated as 64-hex: {gemini_replay}")
    h("```")
    h("")

    # Qwen execution
    h("## Qwen Execution")
    h("```")
    h(f"engine_name={qwen_engine}")
    h(f"replay_hash={qwen_replay}")
    h(f"OK: replay_hash validated as 64-hex: {qwen_replay}")
    h("```")
    h("")

    # Determinism lock
    h("## Determinism Lock")
    h("```")
    h(f"gemini_replay_deterministic={gemini_deterministic}")
    h(f"qwen_replay_deterministic={qwen_deterministic}")
    h("```")
    h("")

    # Negative control
    h("## Negative Control")
    h("```")
    h(f"route_to_gemini={neg_route_to_gemini}")
    h(f"failure_type={neg_failure_type}")
    h(f"violation_hash={violation_hash}")
    h(f"OK: violation_hash validated as 64-hex: {violation_hash}")
    h(f"replay_hash={neg_replay}")
    h(f"OK: replay_hash validated as 64-hex: {neg_replay}")
    h("```")
    h("")

    # Runner self-check
    h("## Runner Self-Check")
    h("```")
    h(f"shell_false_enforced={_SHELL_FALSE_ENFORCED}")
    h("powershell_guard=hard-fail on argv[0] containing pwsh/powershell")
    h("all_subprocess_calls_shell_false=True")
    h("```")
    h("")

    # Git status
    h("## Git Status")
    git_status, _ = run(["git", "status", "--porcelain"], required=False)
    if git_status.strip():
        fence(git_status)
    else:
        h("(clean)")
    h("")

    # Write evidence file
    evidence_path = Path("docs/reports/evidence/e2e_gemini_qwen_proof.md")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)

    content = "\n".join(evidence_lines)

    # ASCII-only byte scan
    for i, byte_val in enumerate(content.encode("utf-8")):
        if byte_val > 0x7F:
            print(f"ERROR: Non-ASCII byte at position {i}: {hex(byte_val)}")
            print(f"Context: {content[max(0, i - 50) : i + 50]!r}")
            sys.exit(1)

    evidence_path.write_text(content, encoding="utf-8")
    print(f"Evidence written to: {evidence_path.absolute()}")
    print("OK: All commands passed.")


if __name__ == "__main__":
    main()
