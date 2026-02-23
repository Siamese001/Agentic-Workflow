# E2E Gemini 2.5 Pro + Qwen vLLM Deterministic Proof

## Scope
End-to-end deterministic proof: Gemini 2.5 Pro path, Qwen vLLM path,
determinism lock, invariant enforcement, negative control.
No external network calls. Production routing + execution surfaces.
Model transport replaced with deterministic stub (minimum seam).
Self-Hash Prohibition compliant: no EVIDENCE_COMMIT field embedded.

## Commits
CODE_COMMIT=b8b9264dd4775848cbd2d38613ab69e03cf6f38c
SEALED_FROM=b8b9264dd4775848cbd2d38613ab69e03cf6f38c

## INSPECTED_FILES
tests/integration_e2e/__init__.py
tests/integration_e2e/test_gemini_qwen_e2e.py
tools/evidence/e2e_gemini_qwen_runner.py
agentic_core/L2_execution/types/vllm_gateway_adapter.py
agentic_core/L2_execution/types/vllm_gateway_integration.py
agentic_core/L2_execution/types/vllm_invariant_contract.py
agentic_core/L2_execution/types/vllm_invariant_verifier.py
agentic_core/L2_execution/types/vllm_replay_validator.py
agentic_core/L2_execution/types/vllm_infrastructure_fingerprint.py
agentic_core/L2_execution/types/llm_replay_types.py

## Pytest Output
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 27 items

tests/integration_e2e/test_gemini_qwen_e2e.py::TestGeminiE2EPath::test_engine_name_exact PASSED [  3%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestGeminiE2EPath::test_no_invariant_violations PASSED [  7%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestGeminiE2EPath::test_failure_type_none PASSED [ 11%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestGeminiE2EPath::test_no_escalation PASSED [ 14%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestGeminiE2EPath::test_route_to_gemini_false PASSED [ 18%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestGeminiE2EPath::test_shadow_classifier_no_change PASSED [ 22%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestGeminiE2EPath::test_replay_hash_is_64hex PASSED [ 25%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestGeminiE2EPath::test_replay_hash_deterministic PASSED [ 29%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestQwenE2EPath::test_engine_name_exact PASSED [ 33%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestQwenE2EPath::test_no_invariant_violations PASSED [ 37%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestQwenE2EPath::test_failure_type_none PASSED [ 40%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestQwenE2EPath::test_no_escalation PASSED [ 44%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestQwenE2EPath::test_route_to_gemini_false PASSED [ 48%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestQwenE2EPath::test_shadow_classifier_no_change PASSED [ 51%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestQwenE2EPath::test_replay_hash_is_64hex PASSED [ 55%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestQwenE2EPath::test_replay_hash_deterministic PASSED [ 59%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestNegativeControlInvariantViolation::test_route_to_gemini_true PASSED [ 62%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestNegativeControlInvariantViolation::test_failure_type_invariant_violation PASSED [ 66%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestNegativeControlInvariantViolation::test_violations_nonempty PASSED [ 70%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestNegativeControlInvariantViolation::test_violation_hash_is_64hex PASSED [ 74%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestNegativeControlInvariantViolation::test_replay_hash_is_64hex PASSED [ 77%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestNegativeControlInvariantViolation::test_replay_hash_deterministic PASSED [ 81%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestNegativeControlInvariantViolation::test_escalation_occurred PASSED [ 85%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestSeamProductionSafety::test_production_path_no_violations_gemini PASSED [ 88%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestSeamProductionSafety::test_production_path_no_violations_qwen PASSED [ 92%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestSeamProductionSafety::test_seam_active_only_when_explicitly_enabled PASSED [ 96%]
tests/integration_e2e/test_gemini_qwen_e2e.py::TestSeamProductionSafety::test_real_verifier_called_on_production_path PASSED [100%]

============================ slowest 10 durations =============================
0.08s setup    tests/integration_e2e/test_gemini_qwen_e2e.py::TestGeminiE2EPath::test_engine_name_exact

(9 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 27 passed in 0.15s ==============================
```

## Gemini Execution
```
engine_name=gemini-2.5-pro
replay_hash=4e8d1d4ced4f1fbd3a2fe0ad2ea21d108620e7fd8aa823993ebd6c6350fadb64
OK: replay_hash validated as 64-hex: 4e8d1d4ced4f1fbd3a2fe0ad2ea21d108620e7fd8aa823993ebd6c6350fadb64
```

## Qwen Execution
```
engine_name=qwen-vllm
replay_hash=a6eea0ac622d267dd3a064327adcb2dcfac9a9f8624914b5664906efd97ab7e8
OK: replay_hash validated as 64-hex: a6eea0ac622d267dd3a064327adcb2dcfac9a9f8624914b5664906efd97ab7e8
```

## Determinism Lock
```
gemini_replay_deterministic=True
qwen_replay_deterministic=True
```

## Negative Control
```
route_to_gemini=True
failure_type=INVARIANT_VIOLATION
violation_hash=9cd6f952efb54428d04ade4145b9da85cef17228a7872b5104a57af82af2cf15
OK: violation_hash validated as 64-hex: 9cd6f952efb54428d04ade4145b9da85cef17228a7872b5104a57af82af2cf15
replay_hash=459ad6aeebdbd91e5675549fe827d109e82d07ddf7269bc8c36b5e575c499bf2
OK: replay_hash validated as 64-hex: 459ad6aeebdbd91e5675549fe827d109e82d07ddf7269bc8c36b5e575c499bf2
```

## Runner Self-Check
```
shell=False enforced: True
PowerShell guard enforced: True
```
