---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\qwen-rollout-test-coverage-gaps-d2a4f8-f9e3c2.md'
original_relative_path: 'qwen-rollout-test-coverage-gaps-d2a4f8-f9e3c2.md'
source_sha256: 125d18a766a69547eb3197d2bcb2ce51760df1f56ee01af149c23e07529c97b4
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: qwen-rollout-test-coverage-gaps-d2a4f8-f9e3c2
plan_type: refactor
---

# Qwen Rollout Test Coverage Gaps — d2a4f8-f9e3c2

> Addresses verification gaps discovered during completion review of `qwen-rollout-followup-burndown-d2a4f8`. Closes the test-coverage hole for `GenerationEngine` Qwen-first cascade and validates the "W1 determinism floor 5/5 green" claim.

---

## Context (SCQA)

- **Situation**: Plan `qwen-rollout-followup-burndown-d2a4f8` (Status: Live/Waiting) implemented P1.1 — Qwen-first cascade in `apps_lic/engines/generation_engine.py`. The code is complete with 9 verified ADG import edges, fail-soft error handling, guardian-exempted broad exceptions, and JUDGE_DECISION marker emission. Claimed success criteria includes "W1 determinism floor 5/5 still green (5 passed, 0.36s)".

- **Complication**: Upon verification, three gaps emerged: (1) No `test_generation_engine.py` exists — the module has zero automated test coverage; (2) The `_try_qwen_generation()` method and `generator=qwen_local` discriminator are unverified by any test; (3) The "5/5 green" claim references `tests/system_learning/waves/w1_determinism_test.py` which tests `EmbeddingServiceFactory`, not `GenerationEngine` — a false positive signal.

- **Question**: How do we close the test-coverage gap for `GenerationEngine` Qwen wiring while preserving the fail-soft semantics and deterministic fallback guarantees?

- **Answer**: Author a focused test suite for `GenerationEngine` covering: unit-isolated fallback paths, mocked Qwen-success paths, preflight failure branches, and a determinism proof that actually exercises the `execute()` method — not a different module.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_lic/engines/generation_engine.py` | Implementation under test | ✅ Verified |
| ADG node 2717 + 9 import edges | Structural evidence of dependencies | ✅ Verified |
| `qwen-rollout-followup-burndown-d2a4f8.md` | Parent plan with claims to validate | ✅ On disk |
| `tests/system_learning/waves/w1_determinism_test.py` | Misattributed "5/5 green" source | ✅ Analyzed |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1–P1.3 | Unit test scaffold + fallback path coverage | ~3k | pytest, unittest.mock available | 🔲 TODO | `test_generation_engine.py` exists with ≥8 tests, all passing |
| W2 | P2.1–P2.2 | Mocked Qwen-success paths + marker emission verification | ~2k | `openai` SDK mockable | 🔲 TODO | `_try_qwen_generation` covered; `JUDGE_DECISION` marker verified |
| W3 | P3.1 | True determinism proof for `GenerationEngine.execute()` | ~1.5k | Test runs twice, compares output | 🔲 TODO | Same input → same output proven; fixes false-positive claim |

**Total: ~6.5k tokens across 3 waves**

---

## Out Of Scope

- Modifying production code in `generation_engine.py` — tests only
- Fixing the parent plan's "W1 determinism floor 5/5" claim text — document in W3 verification output
- Testing `QwenLLMClient` async adapter (already has test coverage via predecessor plan)
- E2E integration tests against real vLLM — unit tests with mocks only

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Test file scaffold | `tests/unit/apps/apps_lic/engines/test_generation_engine.py` (create) | SSOT routing: must land in `tests/unit/apps/apps_lic/engines/` per `ssot-folder-enforcement.md` | ~1k | 🔲 TODO |
| P1.2 | Fallback path unit tests | Same file — 4 tests: empty prompt, preflight fail, SDK absent, empty response | Guardian exemptions require `# guardian: allow-broad-exception` in test mocks | ~1k | 🔲 TODO |
| P1.3 | Deterministic scaffold verification | Same file — 2 tests: scaffold output shape, template signature stability | Hash stability across Python versions | ~1k | 🔲 TODO |
| P2.1 | Mocked Qwen-success path | Same file — 2 tests: mocked `openai.OpenAI` success, `generator=qwen_local` assertion | Mocking sync `openai.OpenAI` client | ~1k | 🔲 TODO |
| P2.2 | Marker emission verification | Same file — 2 tests: success marker emitted, failure marker emitted | `tools.capture.append_marker` mock; session hint verification | ~1k | 🔲 TODO |
| P3.1 | True determinism proof | Same file — 1 test: run `execute()` twice with identical input, compare outputs | Fixes parent plan's misattributed "5/5 green" claim | ~1.5k | 🔲 TODO |

---

## Gap Register

**GAP-1: Zero test coverage for GenerationEngine**
- 0 tests exist for the module; 209 lines of production code untested
- Risk: Qwen-first cascade could regress silently; fail-soft paths could break
- Closes with: P1.1–P1.3, P2.1–P2.2

**GAP-2: `_try_qwen_generation` success path unverified**
- Method has 8 failure returns but success path only exercised in production
- Risk: Qwen availability preflight passes but actual call fails untested
- Closes with: P2.1 (mocked success path)

**GAP-3: False-positive determinism claim**
- Parent plan claims "W1 determinism floor 5/5 green" citing `w1_determinism_test.py`
- That test covers `EmbeddingServiceFactory`, not `GenerationEngine`
- Risk: Stakeholders believe HOP5 generation is deterministic-proven when it is not
- Closes with: P3.1 (true determinism proof for actual module)

---

## ADG_HOTSPOT_REPORT

| Node | Layer | Fan-In | Impact Score | Archetype | Surface Intersection |
|------|-------|--------|--------------|-----------|---------------------|
| `apps_lic/engines/generation_engine.py` (2717) | L_APP | 0 (new code) | N/A (test gap, not hotspot) | — | — |

Note: This plan is test-coverage backfill, not refactoring. No production hotspot analysis required per plan_type rules.

---

## ADG_GRAPH_LAYER_EVIDENCE

For test mock verification:
- **Semantic edge**: `imports(openai)` at line 106 — must be mockable in tests
- **Semantic edge**: `from_import(is_qwen_available)` at line 92 — preflight check requires `vllm_health_probe` mock
- **Semantic edge**: `from_import(QWEN_LOCAL_MODEL_ID, VLLM_BASE_URL)` at line 111 — config constants
- **Semantic edge**: `from_import(append_marker)` at line 190 — marker emission verification point

---

## Execution Plan

### Phase P1.1 — Test File Scaffold
**Scope**: Create `tests/unit/apps/apps_lic/engines/test_generation_engine.py` with imports, fixtures, and base test class.

**Commands**:
```bash
# Verify path per SSOT folder routing
python .windsurf/scripts/_ssot_folder_check.py tests/unit/apps/apps_lic/engines/test_generation_engine.py --exists=false

# Create test file (manual — not implemented in this plan)
```

**Acceptance**:
- [ ] File exists at `tests/unit/apps/apps_lic/engines/test_generation_engine.py`
- [ ] Imports: `pytest`, `unittest.mock.patch`, `GenerationEngine`
- [ ] Fixture: `gen_engine()` returns `GenerationEngine()` instance

### Phase P1.2 — Fallback Path Unit Tests
**Scope**: 4 tests covering all fail-soft branches.

**Commands**:
```bash
pytest tests/unit/apps/apps_lic/engines/test_generation_engine.py -v -k "fallback"
```

**Acceptance**:
- [ ] `test_empty_prompt_returns_scaffold` — empty string prompt → scaffold
- [ ] `test_preflight_unavailable_returns_scaffold` — `is_qwen_available()=False` → scaffold
- [ ] `test_openai_import_error_returns_scaffold` — `ImportError` on `import openai` → scaffold
- [ ] `test_model_registry_import_error_returns_scaffold` — `ImportError` on registry import → scaffold

### Phase P1.3 — Deterministic Scaffold Verification
**Scope**: 2 tests verifying deterministic output shape.

**Commands**:
```bash
pytest tests/unit/apps/apps_lic/engines/test_generation_engine.py -v -k "scaffold"
```

**Acceptance**:
- [ ] `test_scaffold_output_shape` — returns dict with `draft_message`, `body`, `register`, `template_signature`, `attempts`, `generator`
- [ ] `test_template_signature_stable` — same prompt → same 8-char SHA1 prefix

### Phase P2.1 — Mocked Qwen-Success Path
**Scope**: 2 tests with mocked `openai.OpenAI` client.

**Commands**:
```bash
pytest tests/unit/apps/apps_lic/engines/test_generation_engine.py -v -k "qwen"
```

**Acceptance**:
- [ ] `test_qwen_success_returns_generated_text` — mocked client returns text → `body` contains text, `generator=qwen_local`
- [ ] `test_qwen_empty_response_returns_scaffold` — mocked client returns empty → falls through to scaffold

### Phase P2.2 — Marker Emission Verification
**Scope**: 2 tests verifying `JUDGE_DECISION` markers.

**Commands**:
```bash
pytest tests/unit/apps/apps_lic/engines/test_generation_engine.py -v -k "marker"
```

**Acceptance**:
- [ ] `test_qwen_success_emits_accepted_marker` — success path calls `append_marker` with `accepted=True`
- [ ] `test_qwen_failure_emits_fallback_marker` — failure path calls `append_marker` with `accepted=False, fallback_reason=...`

### Phase P3.1 — True Determinism Proof
**Scope**: 1 test running `execute()` twice with identical input.

**Commands**:
```bash
pytest tests/unit/apps/apps_lic/engines/test_generation_engine.py::test_determinism_proof -v
```

**Acceptance**:
- [ ] `test_determinism_proof` — same input dict → byte-identical output dict (both runs)
- [ ] Document: "This test validates the actual `GenerationEngine` determinism claim from parent plan d2a4f8"

---

## Rules

- No production code edits — tests only
- All tests must pass in isolation (`pytest -x`) and suite (`pytest tests/unit/apps/apps_lic/engines/`)
- Mock external dependencies; do not require real vLLM
- Include `guardian: allow-broad-exception` comment pattern where tests mock exception paths
- Document the parent plan misattribution in P3.1 docstring

---

## Success Criteria

- [ ] 9 tests total in `test_generation_engine.py` (P1.2: 4, P1.3: 2, P2.1: 2, P2.2: 2, P3.1: 1; note P2.1 includes scaffold fallback = 1 test overlap, total 9)
- [ ] All tests pass: `pytest tests/unit/apps/apps_lic/engines/test_generation_engine.py -v`
- [ ] Coverage report: `pytest --cov=apps_lic.engines.generation_engine --cov-report=term-missing`
- [ ] No `GenerationEngine` lines uncovered in fail-soft or success paths

---

## Implementation Commands

```bash
# Full verification sequence (to be run after implementation)
pytest tests/unit/apps/apps_lic/engines/test_generation_engine.py -v --tb=short
pytest tests/unit/apps/apps_lic/engines/ -v --tb=short
python ops_scripts/ci/run_contract_gates.py
```

---

## Rollback Strategy

If tests fail or coverage is incomplete:
1. Mark failing tests with `@pytest.mark.xfail(reason="...", strict=True)` — not skip
2. Document uncovered lines in plan §5 as deferred scope
3. Do NOT delete test file — partial coverage better than zero

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Test count | ≥9 | `pytest --collect-only` count |
| Line coverage | ≥90% | `pytest --cov` output |
| All tests pass | 100% | `pytest` exit 0 |
| False-positive claim documented | 1 | P3.1 docstring cites parent plan misattribution |

---

## Cursor Agent Alignment Checks

- SSOT folder routing verified for test file path
- No gold-plating: tests only, no production edits
- ADG-first: import edges verified for mock points
- Scope containment: stays within `tests/unit/apps/apps_lic/engines/`

---

## DECISION_CAPTURED: Plan Created

Plan authored: 2026-05-03  
Target: Close test coverage gaps in `qwen-rollout-followup-burndown-d2a4f8`  
Scope: `tests/unit/apps/apps_lic/engines/test_generation_engine.py` creation (9 tests)  
Complexity: T2 (multi-file, test-only)  
Next action: Await user APPROVAL before W1 implementation
