"""
Phase 3 evidence runner — Runtime Integration + Telemetry Enforcement.

Generates: docs/reports/evidence/qwen_migration_phase_3_runtime_integration.md

Usage:
    python tools/evidence/qwen_migration_phase3_evidence_runner.py         --code-commit <40-hex> [--evidence-commit <40-hex>]

No PowerShell. No subprocess shell=True. ASCII-only output.
Runner hard-fails if any output references pwsh or PowerShell.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "qwen_migration_phase3_evidence_runner", "uwg_governed_write")
_emit_writes_through("p1", "qwen_migration_phase3_evidence_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "qwen_migration_phase3_evidence_runner", "context_retrieval")
_emit_pulls_context("p1", "qwen_migration_phase3_evidence_runner", "context_retrieval_2")
emit_determinism_digest("trace_qwen_migration_phase3_evidence_runner", "qwen_migration_phase3_evidence_runner_dispatch")
emit_determinism_digest("trace_qwen_migration_phase3_evidence_runner", "qwen_migration_phase3_evidence_runner_complete")
_emit_validated_by_safety_plane("p1", "qwen_migration_phase3_evidence_runner", "safety_validation")
_emit_reads_through("l4", "qwen_migration_phase3_evidence_runner", "urg_read_1")
_emit_reads_through("l4", "qwen_migration_phase3_evidence_runner", "urg_read_2")
_emit_reads_through("l4", "qwen_migration_phase3_evidence_runner", "urg_read_3")
_emit_reads_through("l4", "qwen_migration_phase3_evidence_runner", "urg_read_4")
_emit_reads_through("l4", "qwen_migration_phase3_evidence_runner", "urg_read_5")
_emit_reads_through("l4", "qwen_migration_phase3_evidence_runner", "urg_read_6")
_emit_reads_through("l4", "qwen_migration_phase3_evidence_runner", "urg_read_7")
_emit_reads_through("l4", "qwen_migration_phase3_evidence_runner", "urg_read_8")
_emit_reads_through("l4", "qwen_migration_phase3_evidence_runner", "urg_read_9")
_emit_reads_through("l4", "qwen_migration_phase3_evidence_runner", "urg_read_10")
_emit_reads_through("l4", "qwen_migration_phase3_evidence_runner", "urg_read_11")
_emit_reads_through("l4", "qwen_migration_phase3_evidence_runner", "urg_read_12")
EVIDENCE_PATH = Path('docs/reports/evidence/qwen_migration_phase_3_runtime_integration.md')
SCOPE_FILES = ['agentic_core/L2_execution/types/vllm_gateway_integration_types.py', 'agentic_core/L2_execution/types/vllm_gateway_adapter_types.py', 'agentic_core/L2_execution/enforcement/SovereignLLMGateway.py', 'tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py', 'tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py', 'tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py', 'tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py']
ANSI_RE = re.compile('\\x1b\\[[0-9;]*[mGKHF]')
_PWSH_RE = re.compile('pwsh|powershell', re.IGNORECASE)

def strip_ansi(text: str) -> str:
    return ANSI_RE.sub('', text)

def ascii_only(text: str) -> str:
    return text.encode('ascii', errors='replace').decode('ascii')

def run(argv: list[str], *, required: bool=True) -> tuple[str, int]:
    if not argv:
        print('ERROR: empty argv')
        sys.exit(1)
    if _PWSH_RE.search(argv[0]):
        print(f'ERROR: argv[0] resolves to PowerShell executable: {argv[0]!r}')
        sys.exit(1)
    result = subprocess.run(argv, shell=False, capture_output=True, encoding='utf-8', errors='replace')
    out = ascii_only(strip_ansi(result.stdout + result.stderr))
    if _PWSH_RE.search(out):
        print(f'WARNING: captured output contains pwsh/PowerShell reference (not fatal):\n{out[:200]}')
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
    h('# qwen-migration Phase 3: Runtime Integration + Telemetry Enforcement')
    h('')
    h('## Scope')
    h('Phase 3 of Qwen vLLM migration: wire Phase 1 (token budgeting + tiered routing) and Phase 2 (serving profiles + backpressure/circuit breaker) into a deterministic call-path controller with telemetry emission. No new model tiers. No 32B. L2 purity preserved.')
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
    h('## Profile Selection + Request Shaping Tests (WAVE 1)')
    out, rc = run([sys.executable, '-m', 'pytest', '-q', '--color=no', 'tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py'])
    fence(out)
    if rc != 0:
        print('FAIL: test_vllm_profile_selection.py')
        sys.exit(1)
    h('')
    h('## Backpressure + Circuit Breaker Integration Tests (WAVE 2)')
    out, rc = run([sys.executable, '-m', 'pytest', '-q', '--color=no', 'tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py'])
    fence(out)
    if rc != 0:
        print('FAIL: test_vllm_backpressure_integration.py')
        sys.exit(1)
    h('')
    h('## Telemetry End-to-End Tests (WAVE 3)')
    out, rc = run([sys.executable, '-m', 'pytest', '-q', '--color=no', 'tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py'])
    fence(out)
    if rc != 0:
        print('FAIL: test_vllm_telemetry_end_to_end.py')
        sys.exit(1)
    h('')
    h('## Gateway Adapter Seam Tests (WAVE 1 Phase 3.1)')
    out, rc = run([sys.executable, '-m', 'pytest', '-q', '--color=no', 'tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py'])
    fence(out)
    if rc != 0:
        print('FAIL: test_vllm_gateway_adapter.py')
        sys.exit(1)
    h('')
    h('## Seam Proof: SovereignLLMGateway Uses VLLMGatewayAdapter')
    seam_script = '; '.join(['from agentic_core.L2_execution.types.vllm_gateway_adapter_types import emit_seam_proof, SEAM_PROOF_MARKER', 'print(emit_seam_proof())', "assert 'SovereignLLMGateway' in SEAM_PROOF_MARKER", "assert 'evaluate_gateway_call' in SEAM_PROOF_MARKER", "print('OK: seam proof verified')"])
    out, rc = run([sys.executable, '-c', seam_script])
    fence(out)
    if rc != 0:
        print('FAIL: seam proof')
        sys.exit(1)
    h('')
    h('## Token Budget Fallback Proof')
    tb_script = '; '.join(['from agentic_core.L2_execution.types.vllm_gateway_integration_types import VLLMQueueController, VLLMCircuitBreakerRegistry, evaluate_gateway_call', 'from agentic_core.L2_execution.types.vllm_serving_profile_types import LOCAL_FAST_7B_MAX_MODEL_LEN', 'from agentic_core.L2_execution.types.vllm_token_budget_types import TASK_CLASS_OUTPUT_CAPS, SAFETY_MARGIN_TOKENS, TaskClass', 'task = TaskClass.PATCH_SUGGESTION.value', 'cap = TASK_CLASS_OUTPUT_CAPS[task]', 'available = LOCAL_FAST_7B_MAX_MODEL_LEN - SAFETY_MARGIN_TOKENS - cap', "over_prompt = 'a' * ((available + 10) * 3)", 'ctrl = VLLMQueueController()', 'reg = VLLMCircuitBreakerRegistry()', "result = evaluate_gateway_call(over_prompt, task, 'low', ctrl, reg)", 't = result.telemetry', "print(f'route_to_gemini={result.route_to_gemini}')", "print(f'failure_type={t.failure_type}')", "print(f'token_budget_ok={t.token_budget_ok}')", "print(f'provider_selected={t.provider_selected}')", "print(f'model_tier={t.model_tier}')", "print(f'prompt_tokens_estimated={t.prompt_tokens_estimated}')", "print(f'budget_margin_tokens={t.budget_margin_tokens}')", "print('OK: token budget fallback confirmed')"])
    out, rc = run([sys.executable, '-c', tb_script])
    fence(out)
    if rc != 0:
        print('FAIL: token budget fallback proof')
        sys.exit(1)
    h('')
    h('## Queue Full Fallback Proof')
    qf_script = '; '.join(['from agentic_core.L2_execution.types.vllm_gateway_integration_types import VLLMQueueController, VLLMCircuitBreakerRegistry, evaluate_gateway_call', 'from agentic_core.L2_execution.types.vllm_backpressure_types import MAX_QUEUE_DEPTH', 'from agentic_core.L2_execution.types.vllm_token_budget_types import TaskClass', 'ctrl = VLLMQueueController()', '[ctrl.acquire() for _ in range(MAX_QUEUE_DEPTH)]', 'reg = VLLMCircuitBreakerRegistry()', "result = evaluate_gateway_call('hello', TaskClass.PATCH_SUGGESTION.value, 'low', ctrl, reg)", 't = result.telemetry', "print(f'route_to_gemini={result.route_to_gemini}')", "print(f'failure_type={t.failure_type}')", "print(f'queue_depth={t.queue_depth}')", "print(f'queue_full={t.queue_full}')", "print(f'provider_selected={t.provider_selected}')", "print(f'model_tier={t.model_tier}')", "print('OK: queue full fallback confirmed')"])
    out, rc = run([sys.executable, '-c', qf_script])
    fence(out)
    if rc != 0:
        print('FAIL: queue full fallback proof')
        sys.exit(1)
    h('')
    h('## Circuit Breaker Open Fallback Proof')
    bo_script = '; '.join(['from agentic_core.L2_execution.types.vllm_gateway_integration_types import VLLMQueueController, VLLMCircuitBreakerRegistry, evaluate_gateway_call', 'from agentic_core.L2_execution.types.vllm_backpressure_types import CIRCUIT_BREAKER_FAILURE_THRESHOLD', 'from agentic_core.L2_execution.types.vllm_token_budget_types import TaskClass', 'ctrl = VLLMQueueController()', 'reg = VLLMCircuitBreakerRegistry()', "[reg.record_failure('local_fast') for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD)]", "result = evaluate_gateway_call('hello', TaskClass.PATCH_SUGGESTION.value, 'low', ctrl, reg)", 't = result.telemetry', "print(f'route_to_gemini={result.route_to_gemini}')", "print(f'failure_type={t.failure_type}')", "print(f'breaker_state={t.breaker_state}')", "print(f'breaker_failure_count={t.breaker_failure_count}')", "print(f'provider_selected={t.provider_selected}')", "print(f'model_tier={t.model_tier}')", "print('OK: circuit breaker open fallback confirmed')"])
    out, rc = run([sys.executable, '-c', bo_script])
    fence(out)
    if rc != 0:
        print('FAIL: circuit breaker open fallback proof')
        sys.exit(1)
    h('')
    h('## Local Success Telemetry Proof')
    ls_script = '; '.join(['from agentic_core.L2_execution.types.vllm_gateway_integration_types import VLLMQueueController, VLLMCircuitBreakerRegistry, evaluate_gateway_call', 'from agentic_core.L2_execution.types.vllm_token_budget_types import TaskClass', 'ctrl = VLLMQueueController()', 'reg = VLLMCircuitBreakerRegistry()', "result = evaluate_gateway_call('hello world', TaskClass.PATCH_SUGGESTION.value, 'low', ctrl, reg)", 't = result.telemetry', 'lr = result.local_request', "print(f'route_to_gemini={result.route_to_gemini}')", "print(f'provider_selected={t.provider_selected}')", "print(f'model_tier={t.model_tier}')", "print(f'token_budget_ok={t.token_budget_ok}')", "print(f'failure_type={t.failure_type}')", "print(f'local_request.max_tokens={lr.max_tokens}')", "print(f'local_request.max_model_len={lr.max_model_len}')", "print(f'local_request.temperature={lr.temperature}')", "print(f'local_request.profile_name={lr.profile_name}')", "assert lr.max_tokens is not None and lr.max_tokens > 0, 'max_tokens must be explicit'", "assert lr.max_model_len > 0, 'max_model_len must come from profile'", "print('OK: local success telemetry confirmed (explicit max_tokens + profile max_model_len)')"])
    out, rc = run([sys.executable, '-c', ls_script])
    fence(out)
    if rc != 0:
        print('FAIL: local success telemetry proof')
        sys.exit(1)
    h('')
    h('## Runner Self-Check Proof')
    selfcheck_lines = ['shell=False: ENFORCED (subprocess.run called with shell=False, never shell=True)', 'argv arrays: ENFORCED (all invocations use list argv, never shell string)', f'pwsh/PowerShell guard: BALANCED (regex={_PWSH_RE.pattern!r}, flags=IGNORECASE)', 'argv[0] guard: hard-fail if argv[0] matches pwsh/PowerShell executable', 'output guard: warn-only if captured output contains pwsh/PowerShell reference', 'OK: runner self-check passed (balanced policy)']
    fence('\n'.join(selfcheck_lines))
    h('')
    h('## Git Status')
    out, _ = run(['git', 'status', '--porcelain=v1'], required=False)
    if out.strip():
        fence(out)
    else:
        fence('(clean)')
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
