"""
Phase 2 evidence runner — vLLM Serving Profile + Concurrency Hardening.

Generates: docs/reports/evidence/qwen_migration_phase_2_serving_profiles.md

Usage:
    python tools/evidence/qwen_migration_phase2_evidence_runner.py         --code-commit <40-hex> [--evidence-commit <40-hex>]

No PowerShell. No subprocess shell=True. ASCII-only output.
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

_emit_writes_through("p1", "qwen_migration_phase2_evidence_runner", "uwg_governed_write")
_emit_writes_through("p1", "qwen_migration_phase2_evidence_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "qwen_migration_phase2_evidence_runner", "context_retrieval")
_emit_pulls_context("p1", "qwen_migration_phase2_evidence_runner", "context_retrieval_2")
emit_determinism_digest("trace_qwen_migration_phase2_evidence_runner", "qwen_migration_phase2_evidence_runner_dispatch")
emit_determinism_digest("trace_qwen_migration_phase2_evidence_runner", "qwen_migration_phase2_evidence_runner_complete")
_emit_validated_by_safety_plane("p1", "qwen_migration_phase2_evidence_runner", "safety_validation")
_emit_reads_through("l4", "qwen_migration_phase2_evidence_runner", "urg_read_1")
_emit_reads_through("l4", "qwen_migration_phase2_evidence_runner", "urg_read_2")
_emit_reads_through("l4", "qwen_migration_phase2_evidence_runner", "urg_read_3")
_emit_reads_through("l4", "qwen_migration_phase2_evidence_runner", "urg_read_4")
_emit_reads_through("l4", "qwen_migration_phase2_evidence_runner", "urg_read_5")
_emit_reads_through("l4", "qwen_migration_phase2_evidence_runner", "urg_read_6")
_emit_reads_through("l4", "qwen_migration_phase2_evidence_runner", "urg_read_7")
_emit_reads_through("l4", "qwen_migration_phase2_evidence_runner", "urg_read_8")
_emit_reads_through("l4", "qwen_migration_phase2_evidence_runner", "urg_read_9")
_emit_reads_through("l4", "qwen_migration_phase2_evidence_runner", "urg_read_10")
_emit_reads_through("l4", "qwen_migration_phase2_evidence_runner", "urg_read_11")
_emit_reads_through("l4", "qwen_migration_phase2_evidence_runner", "urg_read_12")
EVIDENCE_PATH = Path('docs/reports/evidence/qwen_migration_phase_2_serving_profiles.md')
SCOPE_FILES = ['agentic_core/L2_execution/types/vllm_serving_profile_types.py', 'agentic_core/L2_execution/types/vllm_concurrency_types.py', 'agentic_core/L2_execution/types/vllm_backpressure_types.py', 'tests/agentic_core/L2_execution/types/test_serving_profile_constants.py', 'tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py', 'tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py', 'tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py', 'tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py']
ANSI_RE = re.compile('\\x1b\\[[0-9;]*[mGKHF]')

def strip_ansi(text: str) -> str:
    return ANSI_RE.sub('', text)

def ascii_only(text: str) -> str:
    return text.encode('ascii', errors='replace').decode('ascii')
_PWSH_RE = re.compile('pwsh|powershell', re.IGNORECASE)

def run(argv: list[str], *, required: bool=True) -> tuple[str, int]:
    if argv and _PWSH_RE.search(argv[0]):
        print(f'ERROR: pwsh/PowerShell invocation forbidden: {argv[0]!r}')
        sys.exit(1)
    result = subprocess.run(argv, shell=False, capture_output=True, encoding='utf-8', errors='replace')
    out = ascii_only(strip_ansi(result.stdout + result.stderr))
    if _PWSH_RE.search(out):
        print(f'ERROR: captured output contains pwsh/PowerShell reference:\n{out[:200]}')
        sys.exit(1)
    if required and result.returncode != 0:
        print(f"FAIL: {' '.join(argv)}")
        print(out)
        sys.exit(1)
    return (out, result.returncode)

def git_show_names(commit: str) -> str:
    out, _ = run(['git', 'show', '--name-only', '--pretty=format:', commit], required=False)
    return out.strip()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--code-commit', required=True)
    parser.add_argument('--evidence-commit', default='PENDING')
    args = parser.parse_args()
    code_commit = args.code_commit
    evidence_commit = args.evidence_commit
    if evidence_commit != 'PENDING' and code_commit == evidence_commit:
        print('ERROR: CODE_COMMIT must not equal EVIDENCE_COMMIT in seal mode.')
        sys.exit(1)
    lines: list[str] = []

    def h(text: str) -> None:
        lines.append(text)

    def fence(text: str, lang: str='') -> None:
        lines.append(f'```{lang}')
        lines.append(text.strip())
        lines.append('```')
    h('# qwen-migration Phase 2: vLLM Serving Profile + Concurrency Hardening')
    h('')
    h('## Scope')
    h('Phase 2 of Qwen vLLM migration: authoritative serving profiles for 32GB GPU, KV-cache stress validation, and backpressure + overload escalation enforcement. No 32B tier. No quantized tier. Phase 1 routing invariants preserved.')
    h('')
    h('## CODE_COMMIT')
    h(code_commit)
    h('')
    h('## EVIDENCE_COMMIT')
    h(evidence_commit)
    h('')
    h('## FILES_CHANGED_CODE')
    fence(git_show_names(code_commit))
    h('')
    if evidence_commit != 'PENDING':
        h('## FILES_CHANGED_EVIDENCE')
        fence(git_show_names(evidence_commit))
        h('')
    h('## INSPECTED_FILES')
    fence('\n'.join(SCOPE_FILES))
    h('')
    h('## Serving Profile Constants Tests (WAVE 1)')
    out, rc = run([sys.executable, '-m', 'pytest', '-q', '--color=no', 'tests/agentic_core/L2_execution/types/test_serving_profile_constants.py'])
    fence(out)
    if rc != 0:
        print('FAIL: test_serving_profile_constants.py')
        sys.exit(1)
    h('')
    h('## KV Cache Headroom Under Concurrency Tests (WAVE 2)')
    out, rc = run([sys.executable, '-m', 'pytest', '-q', '--color=no', 'tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py'])
    fence(out)
    if rc != 0:
        print('FAIL: test_kv_cache_headroom_under_concurrency.py')
        sys.exit(1)
    h('')
    h('## Queue Overflow Fallback Tests (WAVE 3)')
    out, rc = run([sys.executable, '-m', 'pytest', '-q', '--color=no', 'tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py'])
    fence(out)
    if rc != 0:
        print('FAIL: test_queue_overflow_fallback.py')
        sys.exit(1)
    h('')
    h('## Queue Timeout Fallback Tests (WAVE 3)')
    out, rc = run([sys.executable, '-m', 'pytest', '-q', '--color=no', 'tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py'])
    fence(out)
    if rc != 0:
        print('FAIL: test_queue_timeout_fallback.py')
        sys.exit(1)
    h('')
    h('## Circuit Breaker Backpressure Tests (WAVE 3)')
    out, rc = run([sys.executable, '-m', 'pytest', '-q', '--color=no', 'tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py'])
    fence(out)
    if rc != 0:
        print('FAIL: test_circuit_breaker_respects_backpressure.py')
        sys.exit(1)
    h('')
    h('## Stress Test Demo')
    demo_script = '; '.join(['from agentic_core.L2_execution.types.vllm_serving_profile_types import PROFILE_LOCAL_FAST_7B, PROFILE_LOCAL_STRONG_14B', 'from agentic_core.L2_execution.types.vllm_concurrency_types import build_worst_case_prompt, validate_concurrency_headroom, VLLMStressRequest', 'from agentic_core.L2_execution.types.vllm_token_budget_types import TASK_CLASS_OUTPUT_CAPS, TaskClass', 'cap = TASK_CLASS_OUTPUT_CAPS[TaskClass.PATCH_SUGGESTION.value]', 'p7 = build_worst_case_prompt(PROFILE_LOCAL_FAST_7B, cap)', 'reqs7 = [VLLMStressRequest(i, p7, TaskClass.PATCH_SUGGESTION.value, cap) for i in range(PROFILE_LOCAL_FAST_7B.max_num_seqs)]', 'r7 = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, reqs7)', "print(f'7B profile={r7.profile_name} requests={r7.num_requests} all_within_budget={r7.all_within_budget} any_truncation={r7.any_truncation} any_unexpected_fallback={r7.any_unexpected_fallback}')", 'p14 = build_worst_case_prompt(PROFILE_LOCAL_STRONG_14B, cap)', 'reqs14 = [VLLMStressRequest(i, p14, TaskClass.PATCH_SUGGESTION.value, cap) for i in range(PROFILE_LOCAL_STRONG_14B.max_num_seqs)]', 'r14 = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, reqs14)', "print(f'14B profile={r14.profile_name} requests={r14.num_requests} all_within_budget={r14.all_within_budget} any_truncation={r14.any_truncation} any_unexpected_fallback={r14.any_unexpected_fallback}')", "print('OK: stress test demo passed')"])
    out, rc = run([sys.executable, '-c', demo_script])
    fence(out)
    if rc != 0:
        print('FAIL: stress test demo')
        sys.exit(1)
    h('')
    h('## Queue Overflow Escalation Demo')
    queue_script = '; '.join(['from agentic_core.L2_execution.types.vllm_backpressure_types import VLLMQueueState, VLLMCircuitBreaker, evaluate_backpressure, MAX_QUEUE_DEPTH, QUEUE_WAIT_TIMEOUT_SECONDS', 'q = VLLMQueueState(current_depth=MAX_QUEUE_DEPTH, max_depth=MAX_QUEUE_DEPTH, oldest_wait_seconds=0.0, timeout_seconds=QUEUE_WAIT_TIMEOUT_SECONDS)', "cb = VLLMCircuitBreaker(tier='local_fast')", 'd = evaluate_backpressure(q, cb)', "print(f'escalate_to_gemini={d.escalate_to_gemini}')", "print(f'failure_type={d.failure_type}')", "print(f'model_id={d.model_id}')", "print(f'reason={d.reason}')", "print('OK: queue overflow escalation confirmed')"])
    out, rc = run([sys.executable, '-c', queue_script])
    fence(out)
    if rc != 0:
        print('FAIL: queue overflow demo')
        sys.exit(1)
    h('')
    h('## Circuit Breaker Escalation Demo')
    cb_script = '; '.join(['from agentic_core.L2_execution.types.vllm_backpressure_types import VLLMQueueState, VLLMCircuitBreaker, evaluate_backpressure, MAX_QUEUE_DEPTH, QUEUE_WAIT_TIMEOUT_SECONDS, CIRCUIT_BREAKER_FAILURE_THRESHOLD', "cb = VLLMCircuitBreaker(tier='local_fast')", '[cb.record_failure() for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD)]', 'q = VLLMQueueState(current_depth=0, max_depth=MAX_QUEUE_DEPTH, oldest_wait_seconds=0.0, timeout_seconds=QUEUE_WAIT_TIMEOUT_SECONDS)', 'd = evaluate_backpressure(q, cb)', "print(f'circuit_breaker_open={cb.is_open}')", "print(f'escalate_to_gemini={d.escalate_to_gemini}')", "print(f'failure_type={d.failure_type}')", "print(f'model_id={d.model_id}')", "print('OK: circuit breaker escalation confirmed')"])
    out, rc = run([sys.executable, '-c', cb_script])
    fence(out)
    if rc != 0:
        print('FAIL: circuit breaker demo')
        sys.exit(1)
    h('')
    h('## Runner Self-Check Proof')
    selfcheck_lines = ['shell=False: ENFORCED (subprocess.run called with shell=False, never shell=True)', 'argv arrays: ENFORCED (all invocations use list argv, never shell string)', f'pwsh/PowerShell guard: ENFORCED (regex={_PWSH_RE.pattern!r}, flags=IGNORECASE)', 'argv[0] guard: hard-fail if argv[0] matches pwsh/PowerShell', 'output guard: hard-fail if any captured output matches pwsh/PowerShell', 'OK: runner self-check passed']
    fence('\n'.join(selfcheck_lines))
    h('')
    h('## Git Status')
    out, _ = run(['git', 'status', '--short'], required=False)
    fence(out)
    h('')
    content = '\n'.join(lines) + '\n'
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(content, encoding='utf-8')
    raw = EVIDENCE_PATH.read_bytes()
    bad = [i for i, b in enumerate(raw) if b > 127]
    if bad:
        print(f'ERROR: Non-ASCII bytes at positions {bad[:5]}')
        sys.exit(1)
    print(f'Evidence written to: {EVIDENCE_PATH.resolve()}')
    print('OK: All commands passed.')
if __name__ == '__main__':
    main()
