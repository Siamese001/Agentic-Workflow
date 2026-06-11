---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\ai-checking-ai-coverage-matrix.md'
original_relative_path: 'ai-checking-ai-coverage-matrix.md'
source_sha256: 05ba5b20e692a71c433134769c9d2ef378a568f4c85568c857b04a25a47b5622
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# AI-Checking-AI Gap Coverage Matrix

**Date**: 2026-03-09
**Purpose**: Map each identified gap to the appropriate testing/enforcement strategy

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Coverage Strategy Summary

| Gap ID | Component | Guardian Script | Unit/Integration Tests | Notes |
|--------|-----------|----------------|----------------------|-------|
| **GAP-01** | `JudgeEvaluator` | ✅ **Primary** | ⚠️ **Secondary** | Guardian: AST detects `llm_client` call in scoring path. Unit: validates audit log emission, deterministic anchor logic |
| **GAP-02** | `ReflectionEngine` | ✅ **Primary** | ✅ **Primary** | Guardian: AST detects `_call_llm` invocation. Unit: **critical** for fail-closed circuit breaker semantics |
| **GAP-03** | `ConstitutionalReviewerAgent` | ✅ **Primary** | ⚠️ **Secondary** | Guardian: AST detects `chat_completion_async` in review method. Unit: validates pre-filter logic, silent bypass detection |
| **GAP-04** | `SafetyInspectorAgent._socratic_verify` | ✅ **Primary** | ✅ **Primary** | Guardian: AST detects LLM router call in security scan. Integration: **critical** for prompt injection defense, audit trail |
| **GAP-05** | `RegressionOracleAgent` | ✅ **Primary** | ✅ **Primary** | Guardian: AST detects `genai.Client` in test generator. Unit: **critical** for iteration cap, AST safety check on generated code |
| **GAP-06** | `AnswerCorrectness/Groundedness` | ✅ **Primary** | ⚠️ **Secondary** | Guardian: AST detects `judge` callable invocation. Unit: validates fallback exception handling |
| **GAP-07** | `AgentGym` | ✅ **Primary** | ⚠️ **Secondary** | Guardian: AST detects `JudgeEvaluator` in self-evolution loop. Unit: validates human checkpoint threshold |
| **GAP-08** | `TruthKeeper` | ✅ **Primary** | ❌ **Not needed** | Guardian: AST detects unused `llm_client` field (latent path warning) |
| **GAP-09** | `sprawl_gate.py` | ⚠️ **Partial** | ✅ **Primary** | Guardian: AST can detect embedding library imports. Integration: **critical** for deterministic similarity verification |
| **GAP-10** | `InjectionDetector` | ⚠️ **Partial** | ✅ **Primary** | Guardian: AST can detect ML library imports (`torch`, `sklearn`). Unit: **critical** for deterministic-only enforcement |
| **GAP-11** | Unified audit trail | ❌ **Not applicable** | ✅ **Primary** | Guardian: cannot verify runtime audit emission. Integration: validates schema, emission, CI assertion |

---

## Detailed Coverage Breakdown

### ✅ Guardian Script (AST-based) — **Primary Coverage**

**What it detects**:
- LLM client instantiation (`llm_client`, `genai.Client`, `get_model_client`)
- LLM method calls (`chat_completion_async`, `route_generation`, `validate_content`)
- Calls occurring inside validation/scoring/enforcement methods (name pattern matching: `validate_*`, `score_*`, `evaluate_*`, `check_*`, `review_*`, `judge_*`)
- Unused LLM client fields (latent paths)
- ML library imports (`torch`, `sklearn`, `transformers`, `FlagEmbedding`)

**Gaps it covers**:
- GAP-01, GAP-02, GAP-03, GAP-04, GAP-05, GAP-06, GAP-07, GAP-08
- Partial: GAP-09 (embedding imports), GAP-10 (ML imports)

**Implementation**:
```python
# ops_scripts/ci/scan_llm_validator_calls.py
class LLMValidatorScanner(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        # Check if function name matches validation pattern
        if any(pattern in node.name.lower() for pattern in
               ['validate', 'score', 'evaluate', 'check', 'review', 'judge']):
            # Scan for LLM calls in function body
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    # Check if call target is an LLM method
                    ...
```

**Allowlist structure**:
```json
{
  "allowed_llm_validators": [
    {
      "file": "apps_shared/types/judge_evaluator_types.py",
      "class": "JudgeEvaluator",
      "method": "evaluate_async",
      "justification": "GAP-01 hardened: routes through gateway, emits audit log",
      "hardened_date": "2026-03-09",
      "reviewer": "human"
    }
  ]
}
```

---

### ✅ Unit/Integration Tests — **Primary Coverage**

**What they validate**:
- **Runtime semantics** (fail-open vs. fail-closed logic)
- **Data flow** (prompt sanitization, taint analysis)
- **Exception handling** (fallback behavior, circuit breaker trips)
- **Audit trail** (log emission, schema compliance)
- **Iteration caps** (self-correction loop bounds)
- **Human checkpoint** (enqueue to `HumanReviewQueueEnforcer`)
- **Deterministic equivalence** (embedding vs. Jaccard similarity)

**Gaps they cover**:
- GAP-02 (fail-closed semantics), GAP-04 (injection defense), GAP-05 (iteration cap, AST safety), GAP-09 (similarity determinism), GAP-10 (ML vs. regex), GAP-11 (audit schema)
- Secondary: GAP-01, GAP-03, GAP-06, GAP-07

**Example test structure**:
```python
# tests/unit/test_reflection_engine_fail_closed.py
def test_circuit_breaker_fail_closed_for_required_criteria():
    """GAP-02: Circuit breaker must fail-closed for required criteria."""
    engine = ReflectionEngine()

    # Simulate circuit open
    with patch.object(engine.circuit_breaker, 'call', side_effect=CircuitOpenError):
        result = await engine.evaluate(
            content={"data": "test"},
            criteria=[ValidationCriterion(name="test", is_required=True, ...)]
        )

    assert result.is_valid == False  # MUST fail closed
    assert "circuit_breaker_fallback" in result.validation_type
```

---

## Coverage Gaps Requiring Both Strategies

| Gap | Guardian Role | Unit/Integration Role | Why Both? |
|-----|--------------|---------------------|-----------|
| **GAP-02** | Detect `_call_llm` call | Validate fail-closed semantics | AST can't evaluate `is_valid=True` vs `False` |
| **GAP-04** | Detect LLM call in scan path | Validate prompt sanitization | AST can't trace data flow (taint analysis) |
| **GAP-05** | Detect `genai.Client` usage | Validate iteration cap, AST safety check | AST can't count loop iterations or inspect generated code |
| **GAP-09** | Detect embedding imports | Validate deterministic similarity | AST can't verify algorithm equivalence |
| **GAP-10** | Detect ML imports | Validate regex-only enforcement | AST can't prove absence of ML at runtime |

---

## Recommended Test Structure

```
tests/
├── guardian/
│   ├── test_no_new_llm_validators.py          # GAP-01 to GAP-08 structural detection
│   └── test_llm_validator_allowlist_sync.py   # Allowlist integrity check
├── unit/
│   ├── test_reflection_engine_fail_closed.py  # GAP-02 semantics
│   ├── test_judge_evaluator_audit.py          # GAP-01 audit trail
│   ├── test_socratic_judge_injection.py       # GAP-04 prompt defense
│   ├── test_regression_oracle_caps.py         # GAP-05 iteration + AST safety
│   ├── test_metric_judge_fallback.py          # GAP-06 exception handling
│   └── test_agent_gym_checkpoint.py           # GAP-07 human gate
└── integration/
    ├── test_sprawl_gate_determinism.py        # GAP-09 similarity verification
    ├── test_injection_detector_no_ml.py       # GAP-10 ML exclusion
    └── test_ai_check_audit_trail.py           # GAP-11 end-to-end audit
```

---

## CI Enforcement Strategy

```yaml
# .github/workflows/ai-checking-ai-guardrail.yml
name: AI-Checking-AI Guardrail

on: [push, pull_request]

jobs:
  guardian-scan:
    runs-on: ubuntu-latest
    steps:
      - name: AST Scan for New LLM Validators
        run: |
          python ops_scripts/ci/scan_llm_validator_calls.py \
            --allowlist ops_scripts/ci/llm_validator_allowlist.json \
            --fail-on-new

      - name: Run Guardian Tests
        run: pytest -xvv tests/guardian/

      - name: Run Unit Tests (AI-Check Coverage)
        run: |
          pytest -xvv tests/unit/test_reflection_engine_fail_closed.py
          pytest -xvv tests/unit/test_socratic_judge_injection.py
          pytest -xvv tests/unit/test_regression_oracle_caps.py

      - name: Validate Audit Trail Schema
        run: pytest -xvv tests/integration/test_ai_check_audit_trail.py
```

---

## Summary

| Strategy | Gaps Covered (Primary) | Gaps Covered (Secondary) | Cannot Cover |
|----------|----------------------|------------------------|--------------|
| **Guardian Script** | 8 (GAP-01 to GAP-08) | 2 partial (GAP-09, GAP-10) | GAP-11 (runtime audit), fail-open semantics, data flow |
| **Unit Tests** | 6 (GAP-02, GAP-04, GAP-05, GAP-09, GAP-10, GAP-11) | 4 (GAP-01, GAP-03, GAP-06, GAP-07) | Structural detection of new LLM calls |
| **Combined** | **All 11 gaps** | — | — |

**Conclusion**: Guardian script provides **structural detection** (prevents new violations). Unit/integration tests provide **semantic validation** (ensures hardened behavior). Both are required for complete coverage.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

