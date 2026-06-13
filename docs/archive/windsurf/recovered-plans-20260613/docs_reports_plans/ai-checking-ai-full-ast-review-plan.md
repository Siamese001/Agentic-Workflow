# AI-Checking-AI: Full AST Review — Gap Inventory & Implementation Plan

**Date**: 2026-03-09
**Scope**: Full repository AST + behavioral review
**Objective**: Identify every location where an LLM evaluates another AI system's output without deterministic or human-validated safeguards, catalogue gaps, and provide a prioritised remediation plan.

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


## 1. Methodology

1. Grepped all Python files for LLM call patterns: `chat_completion_async`, `llm_client`, `get_model_client`, `genai.Client`, `judge`, `evaluate`, `validate`.
2. Read every hit in context to determine whether the LLM call sits in a **validation / scoring / enforcement path**.
3. Cross-referenced with existing deterministic safeguards (shadow evaluator, arbitration engine, confidence scorer, AST gate, regex overseer).
4. Classified each finding by **severity** (HIGH / MEDIUM / LOW) and **gap type**.

---

## 2. Confirmed "AI-Checking-AI" Locations

### GAP-01 — `JudgeEvaluator` (LM-as-a-Judge)
**File**: `apps_shared/types/judge_evaluator_types.py`
**Severity**: HIGH
**Pattern**: `llm_client` callable scores agent outputs against 7+ `JudgmentCriterion` values (accuracy, completeness, relevance, coherence, factuality, safety, helpfulness). Score ≥ `pass_threshold` (default 0.7) passes the output downstream.
**Existing fallback**: `_heuristic_evaluation` (keyword density, length checks) when `llm_client=None`.
**Gaps**:
- LLM judge verdicts are trusted unconditionally; no cross-validation against ground-truth references.
- `pass_threshold=0.7` is an arbitrary floating-point gate with no deterministic rationale.
- No audit trail entry recording which LLM model produced which verdict.
- Heuristic fallback is never activated when `llm_client` is provided but returns a low-confidence answer.
- No adversarial robustness testing — an adversarial output can be crafted to fool both judge and heuristic.

---

### GAP-02 — `ReflectionEngine` LLM critique path
**File**: `agentic_core/config/core/reflection_config.py`
**Severity**: HIGH
**Pattern**: `_llm_path_evaluate` sends agent output to `gpt-4o-mini` (role: "QA Auditor") when built-in regex criteria are insufficient. The LLM's JSON response (`is_valid`, `confidence`, `reasoning`) is returned directly as the gate verdict.
**Existing fallback**: Circuit breaker (`CircuitBreakerFactory`) — but configured **fail-open** (`is_valid=True`, `confidence_score=0.3`).
**Gaps**:
- `_call_llm` is a **mock implementation** (simulates network delay + heuristic branches) — NOT wired to `SovereignLLMGateway`. Production will silently use the mock.
- Circuit-breaker trips produce `is_valid=True` — a dangerous fail-open posture for safety-critical content.
- No `agent_id` / `AgentExecutionProfile` passed through — bypasses the gateway's audit enforcement.
- No audit log of LLM critique decisions; stats counters are in-memory only.
- `ReflectionConfig.llm_provider/llm_model` fields are not validated against the approved model registry.

---

### GAP-03 — `ConstitutionalReviewerAgent`
**File**: `agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py`
**Severity**: HIGH
**Pattern**: A single `chat_completion_async` call reviews the full `final_draft` against JSON-encoded constitution rules. The LLM decides whether violations exist.
**Gaps**:
- Single LLM call — no consensus, no cross-validation with a second model.
- `enable_constitutional_review=False` causes **silent pass-through** (`review_passed=True`) with only a warning log; no alert or escalation.
- No deterministic pre-filter applied before the LLM sees the draft (e.g., regex for known violation keywords).
- No fallback to deterministic rule-matching if the LLM call fails or times out.
- LLM response parsing failure (malformed JSON) falls into the `heal` path which is under-defined.

---

### GAP-04 — `SafetyInspectorAgent` Socratic Judge
**File**: `agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py`
**Severity**: HIGH
**Pattern**: `_socratic_verify` sends a 2000-character code snippet plus a natural-language question to `llm_router_mcp_client.validate_content`. The LLM's "YES"/"NO" response decides whether a regex-detected security violation is real or suppressed as false positive.
**Gaps**:
- **Adversarial prompt injection risk**: a malicious file can embed text that causes the LLM to answer "NO", suppressing real violations.
- No audit log of Socratic Judge verdicts — suppressed violations leave no trace.
- No rate limiting or circuit breaker around the MCP LLM call in the security-critical scan path.
- Code snippet (up to 2000 chars) is exfiltrated to an external LLM endpoint — potential data leak.
- Ambiguous responses (not "YES"/"NO") default to "YES" (flag violation) — inconsistent with security-first principle.

---

### GAP-05 — `RegressionOracleAgent` / `RegressionTestGenerator`
**File**: `agentic_core/L5_safety/reasoning/RegressionOracleAgent.py`
**Severity**: MEDIUM
**Pattern**: `RegressionTestGenerator` uses Gemini 2.5 (`genai.Client`) to generate `pytest` cases for changed methods. A self-correction loop (`run_and_correct_test`) re-invokes the LLM when generated tests fail.
**Gaps**:
- LLM-generated test code is executed without static analysis or sandboxing (code injection risk).
- Self-correction loop has no hard iteration cap visible at orchestration level; infinite retry is possible.
- Generated tests may have trivially low coverage (LLM hallucinates passing assertions).
- No deterministic coverage-threshold check after LLM test generation.
- Gemini client initialisation is guarded by `GEMINI_API_KEY` but failures degrade silently to `genai_available=False` with no fallback test-generation strategy.

---

### GAP-06 — `AnswerCorrectness` / `Groundedness` optional judge
**Files**: `agentic_core/utils/workflow_engines/answer_correctness.py`, `groundedness.py`
**Severity**: MEDIUM
**Pattern**: Both metrics accept an optional `judge: Callable[[str, str], float]` at construction. When provided, the judge's float replaces the deterministic token-F1 score unconditionally.
**Gaps**:
- No type-level enforcement that `judge` is deterministic; an LLM callable can be injected silently.
- No circuit breaker or exception handling if `judge` callable raises — propagates unhandled to caller.
- No audit trail recording which evaluation path (heuristic vs. judge) was used for a given run.

---

### GAP-07 — `AgentGym` LLM-driven self-evolution
**File**: `agentic_core/L3_orchestration/engines/agent_gym_engine.py`
**Severity**: MEDIUM
**Pattern**: `AgentGym` accepts a `JudgeEvaluator` instance that gates agent performance benchmarking. Benchmark results drive "capability gap identification" and "improvement recommendations" — i.e., LLM judge drives agent self-modification decisions.
**Gaps**:
- The LLM judge feeding self-evolution decisions creates a closed feedback loop with no human checkpoint.
- No deterministic baseline (golden-state majority vote) required before judge score triggers improvement.
- `GoldenStateEvaluator` import falls back to a stub that always returns score=0.5, allowing misconfiguration.

---

### GAP-08 — `TruthKeeper` latent LLM path
**File**: `agentic_core/L1_cognition/validators/truth_keeper_validator.py`
**Severity**: LOW
**Pattern**: Constructor accepts `llm_client` for docstring-code consistency validation. The current implementation only uses AST (checks for missing docstrings). The LLM path is structurally present but inactive.
**Gaps**:
- `llm_client` field is stored but never called — the intended LLM validation path is unimplemented, leaving a false sense of coverage.
- If activated in future, there is no governance contract specifying what the LLM may assert.

---

### GAP-09 — `sprawl_gate.py` embedding similarity in CI
**File**: `artifacts/dedup/sprawl_gate.py` (invoked from `.github/workflows/agent-sprawl-check.yml`)
**Severity**: MEDIUM
**Pattern**: CI step passes `--max-code-sim 0.85 --max-prompt-sim 0.85`. If `sprawl_gate.py` uses embedding similarity (LLM-derived vectors), CI gate outcomes depend on an AI model.
**Gaps**:
- Implementation of similarity computation is not confirmed deterministic (needs verification).
- Embedding models change over time; CI results would be non-reproducible.
- No pinned model version or hash-validated embedding cache documented.

---

### GAP-10 — `InjectionDetector` implementation unknown
**File**: `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`
**Severity**: MEDIUM
**Pattern**: `SovereignLLMGateway.__init__` instantiates `InjectionDetector()`. If this uses an ML classifier, it is AI-checking-AI in the security path.
**Gaps**:
- `InjectionDetector` implementation not reviewed — must be verified to use only deterministic pattern matching.
- If ML-based: model version, update cadence, and fallback behaviour must be documented.

---

### GAP-11 — No unified audit trail for AI-check decisions
**Severity**: HIGH (cross-cutting)
**Pattern**: Each AI-checking-AI component (JudgeEvaluator, ReflectionEngine, ConstitutionalReviewerAgent, Socratic Judge) maintains independent logging or no logging at all.
**Gaps**:
- No central store correlating which LLM call produced which validation verdict.
- No replay capability for auditing why a specific output was passed or failed.
- `HumanReviewQueueEnforcer` exists but no component enqueues items when AI-check confidence is low.

---

## 3. Existing Deterministic Safeguards (Good Patterns)

The following components are correctly implemented without AI-checking-AI:

| Component | File | Method |
|-----------|------|---------|
| `ShadowEvaluator` | `system_learning/validators/shadow_evaluator.py` | Numeric metric comparison with fixed thresholds |
| `ArbitrationEngine` | `system_learning/arbitration/engine.py` | Weighted deterministic scoring |
| `HealingConfidenceScorer` | `system_learning/confidence/engine.py` | Fixed threshold escalation table |
| `ConfCalibRiskGate` | `agentic_core/L5_safety/enforcement/conf_calib_gate.py` | Pure rules, no ML |
| `VerificationGate` | `agentic_core/L5_safety/enforcement/verification_gate.py` | AST parse + node existence check |
| `ConstitutionalOverseer` | `agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py` | Compiled regex allowlist |
| `TestGeneratorAgent` | `agentic_core/L5_safety/reasoning/TestGeneratorAgent.py` | AST parse + template generation |
| Layer Sovereignty CI | `.github/workflows/layer-sovereignty-enforcement.yml` | Inline `ast` module import checks |
| `HumanReviewQueueEnforcer` | `agentic_core/L5_safety/enforcement/human_review_queue_enforcer.py` | Human-in-the-loop queue (underused) |

---

## 4. Implementation Plan

### Phase 1 — Audit & Harden `JudgeEvaluator` (GAP-01)
**Priority**: CRITICAL
**Effort**: 1 session

**Steps**:
1. Add `judge_model_id: str` field to `JudgeEvaluator` constructor (required when `llm_client` is provided).
2. Enforce that `judge_model_id` is in the approved model registry via `SovereignLLMGateway._is_policy_approved_model`.
3. Emit a structured audit log entry (to `SovereignLLMGateway.audit_log`) for every LLM judge call: timestamp, model, criteria, score, verdict.
4. Add a `deterministic_anchor: float | None` parameter — when provided, the LLM score must be within ±0.15 of the anchor (computed from token-F1 heuristic); if not, flag for human review.
5. Add a `min_heuristic_agreement: bool` option: require heuristic to also pass before LLM pass is accepted.
6. Write guardian test: `tests/guardian/test_judge_evaluator_not_ai_checking_ai.py` asserting that `JudgeEvaluator` without `llm_client` produces deterministic, reproducible scores.

---

### Phase 2 — Fix `ReflectionEngine` (GAP-02)
**Priority**: CRITICAL
**Effort**: 1 session

**Steps**:
1. Replace mock `_call_llm` with a real call routed through `SovereignLLMGateway.route_generation`, passing a registered `agent_id`.
2. Change circuit-breaker fallback from **fail-open** (`is_valid=True`) to **fail-closed** (`is_valid=False`) for all criteria marked `is_required=True`; fail-open only for optional criteria.
3. Add structured audit log emission for every LLM critique: timestamp, model, content hash, verdict, confidence.
4. Validate `ReflectionConfig.llm_model` against the approved model registry on `ReflectionEngine.__init__`.
5. Write regression test: `tests/unit/test_reflection_engine_circuit_breaker.py` asserting that when the circuit opens, required criteria fail closed.

---

### Phase 3 — Harden `ConstitutionalReviewerAgent` (GAP-03)
**Priority**: HIGH
**Effort**: 1 session

**Steps**:
1. Add a **deterministic pre-filter** before the LLM call: scan `final_draft` for regex patterns derived from the constitution rules (fast-reject path). If pre-filter finds a clear violation, skip LLM and return `review_passed=False`.
2. Replace silent pass-through when `enable_constitutional_review=False` with a logged warning + `HumanReviewQueueEnforcer` enqueue (flagging the bypass).
3. Add a **second-opinion gate**: if LLM returns `review_passed=True` with confidence < 0.8, enqueue item for async human review while allowing execution to continue (audit trail only).
4. Add JSON schema validation of LLM response before trusting `violations_found`.
5. Write invariant test: `tests/architecture/test_constitutional_reviewer_no_silent_bypass.py`.

---

### Phase 4 — Harden `SafetyInspectorAgent` Socratic Judge (GAP-04)
**Priority**: HIGH
**Effort**: 1 session

**Steps**:
1. Add structured audit log for every Socratic Judge call: file path, pattern matched, LLM verdict, timestamp.
2. Add prompt injection defense: sanitize the code snippet before embedding in the prompt (escape special tokens, strip known injection patterns using `InjectionDetector`).
3. Add a **rate limit**: maximum N Socratic Judge calls per scan run; above limit, default to "YES" (conservative flag).
4. Add a circuit breaker (fail-closed: return "YES") with a short timeout (5 seconds).
5. Limit code snippet to 500 characters (not 2000) and exclude lines matching credential patterns before sending.
6. Write guardian test: `tests/guardian/test_socratic_judge_audit_trail.py` asserting every verdict is logged.

---

### Phase 5 — Harden `RegressionOracleAgent` (GAP-05)
**Priority**: MEDIUM
**Effort**: 1 session

**Steps**:
1. Add a `max_correction_iterations: int = 3` cap to `run_and_correct_test` — hard-stop after 3 LLM correction attempts, emit `REGRESSION_CHECK_FAIL` signal.
2. Before executing LLM-generated test code: run AST parse to detect dangerous nodes (`ast.Call` to `os.system`, `subprocess`, `exec`, `eval`). Reject if found.
3. After test execution, compute coverage using `coverage.py` and fail if coverage < configured threshold (default 60%).
4. Emit structured audit log for each generated test: LLM model, prompt hash, generated code hash, pass/fail.
5. Add fallback template-based test generator (no LLM) for simple getter/setter methods detected via AST.
6. Write invariant test: `tests/architecture/test_regression_oracle_iteration_cap.py`.

---

### Phase 6 — Harden `AnswerCorrectness` / `Groundedness` (GAP-06)
**Priority**: MEDIUM
**Effort**: 0.5 session

**Steps**:
1. Add `judge_is_deterministic: bool = True` parameter to both constructors. If `False`, require explicit `audit_logger` parameter.
2. Wrap `judge` callable invocation in a `try/except` with deterministic fallback to token-F1.
3. Add `evaluation_path` field to the return structure indicating `"heuristic"` vs `"judge"`.
4. Write unit test: `tests/unit/test_metric_judge_fallback.py` asserting fallback triggers on exception.

---

### Phase 7 — Harden `AgentGym` self-evolution loop (GAP-07)
**Priority**: MEDIUM
**Effort**: 1 session

**Steps**:
1. Require `require_golden_consensus: bool = True` flag — before a `JudgeEvaluator` score triggers an improvement recommendation, at least 3 golden cases must agree.
2. Add a `human_checkpoint_threshold: float = 0.6` — recommendations below this score must be enqueued in `HumanReviewQueueEnforcer` before any self-modification.
3. Add structured audit log for every benchmark session: scenario, judge score, whether human checkpoint was triggered.
4. Write guardian test: `tests/guardian/test_agent_gym_human_checkpoint.py`.

---

### Phase 8 — Verify `sprawl_gate.py` and `InjectionDetector` (GAP-09, GAP-10)
**Priority**: MEDIUM
**Effort**: 0.5 session

**Steps**:
1. Read `artifacts/dedup/sprawl_gate.py` fully; if similarity is embedding-based, replace with deterministic Jaccard or AST structural diff.
2. Read `InjectionDetector` implementation; if ML-based, add documentation of model source, version, and update policy, plus a deterministic regex pre-filter that must pass before ML is invoked.
3. Pin any embedding model to a specific version hash in `pyproject.toml`.

---

### Phase 9 — Unified AI-Check Audit Trail (GAP-11)
**Priority**: HIGH (cross-cutting)
**Effort**: 1 session

**Steps**:
1. Create `agentic_core/L5_safety/audit/ai_check_audit.py` — a singleton audit log emitter writing structured JSON records to `observability/audit/ai_check_decisions.jsonl`.
2. Schema: `{timestamp, component, model_id, input_hash, verdict, confidence, human_enqueued, trace_id}`.
3. Wire `JudgeEvaluator`, `ReflectionEngine`, `ConstitutionalReviewerAgent`, `SafetyInspectorAgent._socratic_verify`, `RegressionOracleAgent` to emit records via this emitter.
4. Add CI step in `agent-sprawl-check.yml` to assert `ai_check_decisions.jsonl` has zero entries with `confidence < 0.5 AND human_enqueued == false`.
5. Write guardian test: `tests/guardian/test_ai_check_audit_schema.py`.

---

### Phase 10 — Add AST-Based CI Governance Check (new invariant)
**Priority**: HIGH
**Effort**: 0.5 session

**Steps**:
1. Create `ops_scripts/ci/scan_llm_validator_calls.py` — AST walker that identifies every function where an LLM callable is invoked inside a validation/scoring/enforcement path.
2. Maintain an allowlist (`ops_scripts/ci/llm_validator_allowlist.json`) of permitted (hardened) AI-check sites.
3. CI step fails if any un-allowlisted LLM validator call is detected.
4. Add to `.github/workflows/adg-invariant-scan.yml`.
5. Write test: `tests/architecture/test_no_new_llm_validators.py`.

---

## 5. Remediation Priority Matrix

| Gap | Severity | Phase | Blocking? |
|-----|----------|-------|-----------|
| GAP-11 Unified audit trail | HIGH | 9 | No |
| GAP-01 JudgeEvaluator | HIGH | 1 | No |
| GAP-02 ReflectionEngine fail-open | HIGH | 2 | No |
| GAP-03 ConstitutionalReviewerAgent | HIGH | 3 | No |
| GAP-04 Socratic Judge injection risk | HIGH | 4 | Yes — security path |
| GAP-05 RegressionOracle iteration cap | MEDIUM | 5 | No |
| GAP-09 sprawl_gate embeddings | MEDIUM | 8 | No |
| GAP-10 InjectionDetector ML? | MEDIUM | 8 | No |
| GAP-06 Metric judge fallback | MEDIUM | 6 | No |
| GAP-07 AgentGym self-evolution | MEDIUM | 7 | No |
| GAP-08 TruthKeeper latent LLM | LOW | Defer | No |

**Recommended execution order**: Phase 4 → Phase 2 → Phase 3 → Phase 1 → Phase 9 → Phase 10 → Phase 5 → Phase 8 → Phase 6 → Phase 7.

---

## 6. Acceptance Criteria (per gap, after remediation)

- All LLM-based validation calls route through `SovereignLLMGateway` with a registered `agent_id`.
- All fail-open circuit breakers in safety-critical paths are replaced with fail-closed.
- Every AI-check decision emits a structured record to `observability/audit/ai_check_decisions.jsonl`.
- The `HumanReviewQueueEnforcer` receives an item whenever AI-check confidence < 0.5.
- CI AST scanner (`scan_llm_validator_calls.py`) passes with zero un-allowlisted LLM validator calls.
- All new guardian tests pass in `pytest -x tests/guardian/ tests/architecture/`.
- No `ShadowRegression` raised by `ShadowEvaluator` after any remediation change.

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

