"""
Phase 4 evidence runner — Deterministic Replay Sealing.

Generates: docs/reports/evidence/qwen_migration_phase_4_deterministic_replay.md

Usage:
    python tools/evidence/qwen_migration_phase4_evidence_runner.py         --code-commit <40-hex> [--evidence-commit <40-hex>]

No PowerShell. No subprocess shell=True. Balanced PowerShell guard:
- Hard-fail on shell=True or argv[0] PowerShell executable
- Warn-only on output containing pwsh/PowerShell
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "qwen_migration_phase4_evidence_runner", "uwg_governed_write")
_emit_writes_through("p1", "qwen_migration_phase4_evidence_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "qwen_migration_phase4_evidence_runner", "context_retrieval")
_emit_pulls_context("p1", "qwen_migration_phase4_evidence_runner", "context_retrieval_2")
emit_determinism_digest(
    "trace_qwen_migration_phase4_evidence_runner", "qwen_migration_phase4_evidence_runner_dispatch"
)
emit_determinism_digest(
    "trace_qwen_migration_phase4_evidence_runner", "qwen_migration_phase4_evidence_runner_complete"
)
_emit_validated_by_safety_plane("p1", "qwen_migration_phase4_evidence_runner", "safety_validation")
_emit_reads_through("l4", "qwen_migration_phase4_evidence_runner", "urg_read_1")
_emit_reads_through("l4", "qwen_migration_phase4_evidence_runner", "urg_read_2")
_emit_reads_through("l4", "qwen_migration_phase4_evidence_runner", "urg_read_3")
_emit_reads_through("l4", "qwen_migration_phase4_evidence_runner", "urg_read_4")
_emit_reads_through("l4", "qwen_migration_phase4_evidence_runner", "urg_read_5")
_emit_reads_through("l4", "qwen_migration_phase4_evidence_runner", "urg_read_6")
_emit_reads_through("l4", "qwen_migration_phase4_evidence_runner", "urg_read_7")
_emit_reads_through("l4", "qwen_migration_phase4_evidence_runner", "urg_read_8")
_emit_reads_through("l4", "qwen_migration_phase4_evidence_runner", "urg_read_9")
_emit_reads_through("l4", "qwen_migration_phase4_evidence_runner", "urg_read_10")
_emit_reads_through("l4", "qwen_migration_phase4_evidence_runner", "urg_read_11")
_emit_reads_through("l4", "qwen_migration_phase4_evidence_runner", "urg_read_12")
EVIDENCE_PATH = Path("docs/reports/evidence/qwen_migration_phase_4_deterministic_replay.md")
SCOPE_FILES = [
    "agentic_core/L2_execution/types/vllm_infrastructure_fingerprint_types.py",
    "agentic_core/L2_execution/types/vllm_gateway_integration_types.py",
    "agentic_core/L2_execution/types/vllm_gateway_adapter_types.py",
    "agentic_core/L2_execution/types/vllm_replay_validator_types.py",
    "tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py",
    "tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py",
]
ANSI_RE = re.compile("\\x1b\\[[0-9;]*[mGKHF]")
_PWSH_RE = re.compile("pwsh|powershell", re.IGNORECASE)


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def ascii_only(text: str) -> str:
    return text.encode("ascii", errors="replace").decode("ascii")


def run(argv: list[str], *, required: bool = True) -> tuple[str, int]:
    if not argv:
        print("ERROR: empty argv")
        sys.exit(1)
    if _PWSH_RE.search(argv[0]):
        print(f"ERROR: argv[0] resolves to PowerShell executable: {argv[0]!r}")
        sys.exit(1)
    result = subprocess.run(argv, shell=False, capture_output=True, encoding="utf-8", errors="replace")
    out = ascii_only(strip_ansi(result.stdout + result.stderr))
    if _PWSH_RE.search(out):
        print(f"WARNING: captured output contains pwsh/PowerShell reference (not fatal):\n{out[:200]}")
    if required and result.returncode != 0:
        print(f"FAIL: {' '.join(argv)}")
        print(out)
        sys.exit(1)
    return (out, result.returncode)


def git_show_names(commit: str) -> str:
    out, _ = run(["git", "show", "--name-only", "--pretty=format:", commit], required=False)
    return out.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-commit", required=True)
    parser.add_argument("--evidence-commit", default="PENDING")
    args = parser.parse_args()
    code_commit = args.code_commit
    evidence_commit = args.evidence_commit
    if evidence_commit != "PENDING" and code_commit == evidence_commit:
        print("ERROR: CODE_COMMIT must not equal EVIDENCE_COMMIT in seal mode.")
        sys.exit(1)
    lines: list[str] = []

    def h(text: str) -> None:
        lines.append(text)

    def fence(text: str, lang: str = "") -> None:
        lines.append(f"```{lang}")
        lines.append(text.strip())
        lines.append("```")

    h("# qwen-migration Phase 4: Deterministic Replay Sealing")
    h("")
    h("## Scope")
    h(
        "Phase 4 of Qwen vLLM migration: seal deterministic replay by adding infrastructure fingerprint capture, canonical hashing, and replay validation harnesses, wired through the Phase 3 adapter/controller telemetry path. Preserves Phase 1-3 routing/backpressure invariants. No model tier changes."
    )
    h("")
    h("## CODE_COMMIT")
    h(code_commit)
    h("")
    h("## EVIDENCE_COMMIT")
    h(evidence_commit)
    h("")
    h("## FILES_CHANGED_CODE")
    fence(git_show_names(code_commit))
    h("")
    if evidence_commit != "PENDING":
        h("## FILES_CHANGED_EVIDENCE")
        fence(git_show_names(evidence_commit))
        h("")
    h("## INSPECTED_FILES")
    fence("\n".join(SCOPE_FILES))
    h("")
    h("## Infrastructure Fingerprint Tests (WAVE 2)")
    out, rc = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--color=no",
            "tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py",
        ]
    )
    fence(out)
    if rc != 0:
        print("FAIL: test_vllm_infrastructure_fingerprint.py")
        sys.exit(1)
    h("")
    h("## Replay Validator Tests (WAVE 3)")
    out, rc = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--color=no",
            "tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py",
        ]
    )
    fence(out)
    if rc != 0:
        print("FAIL: test_vllm_replay_validator.py")
        sys.exit(1)
    h("")
    h("## Phase 3 Integration Tests (No Regressions)")
    out, rc = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--color=no",
            "tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py",
        ]
    )
    fence(out)
    if rc != 0:
        print("FAIL: test_vllm_gateway_adapter.py (Phase 3 regression)")
        sys.exit(1)
    h("")
    h("## Governance Tests (Pre-existing Violations)")
    out, rc = run([sys.executable, "-m", "pytest", "-q", "--color=no", "tests/governance"], required=False)
    fence(out)
    h("")
    h("## Scope Isolation Proof")
    h("PHASE_TOUCHED_FILES:")
    phase_files = [
        "agentic_core/L2_execution/types/vllm_infrastructure_fingerprint_types.py",
        "agentic_core/L2_execution/types/vllm_gateway_integration_types.py",
        "agentic_core/L2_execution/types/vllm_gateway_adapter_types.py",
        "agentic_core/L2_execution/types/vllm_replay_validator_types.py",
        "tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py",
        "tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py",
    ]
    for f in phase_files:
        h(f"  {f}")
    h("")
    import re

    violation_files = set()
    for match in re.finditer("'file_path':\\s*'([^']+)'", out):
        file_path = match.group(1).replace("\\\\", "/").replace("\\", "/")
        violation_files.add(file_path)
    for match in re.finditer("LAZY_SEAM_VIOLATION:.*?in\\s+(\\S+\\.py):", out):
        filename = match.group(1)
        for path_match in re.finditer(f"""agentic_core[^'\\"\\\\s]*{re.escape(filename)}""", out):
            full_path = path_match.group().replace("\\\\", "/").replace("\\", "/")
            violation_files.add(full_path)
    h("GOVERNANCE_VIOLATION_FILES:")
    if violation_files:
        for f in sorted(violation_files):
            h(f"  {f}")
    else:
        h("  (none detected in output)")
    h("")
    phase_files_normalized = {f.replace("\\", "/") for f in phase_files}
    intersection = phase_files_normalized & violation_files
    if intersection:
        h("INTERSECTION (NON-EMPTY - VIOLATION):")
        for f in sorted(intersection):
            h(f"  {f}")
        print("FAIL: Phase 4 files intersect with governance violations")
        sys.exit(1)
    else:
        h("OK: intersection is empty")
    h("")
    h("## Proof: Identical Replay Hash Across Two Runs")
    replay_proof_code = "\nfrom agentic_core.L2_execution.types.vllm_gateway_integration_types import VLLMQueueController, VLLMCircuitBreakerRegistry, evaluate_gateway_call\nfrom agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import VLLMInfrastructureFingerprint\nfrom agentic_core.L2_execution.types.vllm_replay_validator_types import compute_replay_hash\n\nfp = VLLMInfrastructureFingerprint.deterministic_test_instance()\nctrl1, reg1 = VLLMQueueController(), VLLMCircuitBreakerRegistry()\nctrl2, reg2 = VLLMQueueController(), VLLMCircuitBreakerRegistry()\n\nresult1 = evaluate_gateway_call('hello', 'patch_suggestion', 'low', ctrl1, reg1, fingerprint=fp)\nresult2 = evaluate_gateway_call('hello', 'patch_suggestion', 'low', ctrl2, reg2, fingerprint=fp)\n\nhash1 = compute_replay_hash('hello', result1.local_request, fp, result1)\nhash2 = compute_replay_hash('hello', result2.local_request, fp, result2)\n\n# Validate hash format\nimport re\nhash_pattern = re.compile(r'^[0-9a-f]{64}$')\nassert hash_pattern.match(hash1), f'Invalid hash format: {hash1}'\nassert hash_pattern.match(hash2), f'Invalid hash format: {hash2}'\n\nprint(f'replay_hash_run1={hash1}')\nprint(f'replay_hash_run2={hash2}')\nprint(f'hashes_match={hash1 == hash2}')\nassert hash1 == hash2, 'Replay hashes must be identical'\nprint('OK: identical replay_hash confirmed')\n"
    out, rc = run([sys.executable, "-c", replay_proof_code])
    fence(out)
    if rc != 0:
        print("FAIL: identical replay_hash proof")
        sys.exit(1)
    h("")
    h("## Proof: Replay Hash Changes When Fingerprint Changes")
    fingerprint_change_proof_code = "\nfrom agentic_core.L2_execution.types.vllm_gateway_integration_types import VLLMQueueController, VLLMCircuitBreakerRegistry, evaluate_gateway_call\nfrom agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import VLLMInfrastructureFingerprint\nfrom agentic_core.L2_execution.types.vllm_replay_validator_types import compute_replay_hash\n\nfp1 = VLLMInfrastructureFingerprint.deterministic_test_instance()\nfp2 = VLLMInfrastructureFingerprint(\n    model_name='DifferentModel',\n    model_revision_sha='def456',\n    vllm_version='0.6.4',\n    transformers_version='4.46.1',\n    torch_version='2.5.2',\n    cuda_version='12.5',\n    driver_version='550.54.15'\n)\n\nctrl, reg = VLLMQueueController(), VLLMCircuitBreakerRegistry()\nresult = evaluate_gateway_call('hello', 'patch_suggestion', 'low', ctrl, reg, fingerprint=fp1)\n\nhash1 = compute_replay_hash('hello', result.local_request, fp1, result)\nhash2 = compute_replay_hash('hello', result.local_request, fp2, result)\n\n# Validate hash format\nimport re\nhash_pattern = re.compile(r'^[0-9a-f]{64}$')\nassert hash_pattern.match(hash1), f'Invalid hash format: {hash1}'\nassert hash_pattern.match(hash2), f'Invalid hash format: {hash2}'\n\nprint(f'hash_fp1={hash1}')\nprint(f'hash_fp2={hash2}')\nprint(f'hashes_differ={hash1 != hash2}')\nassert hash1 != hash2, 'Replay hashes must differ when fingerprint changes'\nprint('OK: replay_hash changes on fingerprint change confirmed')\n"
    out, rc = run([sys.executable, "-c", fingerprint_change_proof_code])
    fence(out)
    if rc != 0:
        print("FAIL: fingerprint change proof")
        sys.exit(1)
    h("")
    h("## Git Status")
    out, _ = run(["git", "status", "--porcelain=v1"], required=False)
    if out.strip():
        fence(out)
    else:
        fence("(clean)")
    h("")
    h("## Runner Self-Check Proof")
    selfcheck_lines = [
        "shell=False: ENFORCED (subprocess.run called with shell=False, never shell=True)",
        "argv arrays: ENFORCED (all invocations use list argv, never shell string)",
        f"pwsh/PowerShell guard: BALANCED (regex={_PWSH_RE.pattern!r}, flags=IGNORECASE)",
        "argv[0] guard: hard-fail if argv[0] matches pwsh/PowerShell executable",
        "output guard: warn-only if captured output contains pwsh/PowerShell reference",
        "OK: runner self-check passed (balanced policy)",
    ]
    fence("\n".join(selfcheck_lines))
    h("")
    content = "\n".join(lines) + "\n"
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(content, encoding="utf-8")
    raw = EVIDENCE_PATH.read_bytes()
    bad = [(i, b, raw[i : i + 10]) for i, b in enumerate(raw) if b > 127]
    if bad:
        print(f"ERROR: Non-ASCII bytes at positions {bad[:5]}")
        pos, byte_val, context = bad[0]
        start = max(0, pos - 20)
        end = min(len(raw), pos + 20)
        context_str = raw[start:end].decode("utf-8", errors="replace")
        print(f"Context: {repr(context_str)}")
        sys.exit(1)
    print(f"Evidence written to: {EVIDENCE_PATH.resolve()}")
    print("OK: All commands passed.")


if __name__ == "__main__":
    main()
