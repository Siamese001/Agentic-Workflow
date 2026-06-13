# Phase 9 Evidence — Replay & Forensics: ReplayBundle + ReplayVerifier + Gateway Emission

## Commit Hash
**0f0a0d4a6** — phase9: ReplayBundle + ReplayBundleStore + ReplayVerifier + emitter + tests

## Modified / New Files
- `agentic_core/L4_state/types/replay_bundle_types.py` [NEW — Wave 1: ReplayBundle + build_replay_bundle()]
- `agentic_core/L4_state/enforcement/replay_bundle_store.py` [NEW — Wave 2: ReplayBundleStore + ReplayVerifier + ReplayVerificationError + VerifiedReplay]
- `agentic_core/L4_state/engines/replay_bundle_emitter.py` [NEW — Wave 3: emit_replay_bundle() gateway emission]
- `tests/agentic_core/test_phase9_replay_bundle_model.py` [NEW — Wave 1: 29 tests]
- `tests/agentic_core/test_phase9_replay_verifier.py` [NEW — Wave 2: 21 tests]
- `tests/agentic_core/test_phase9_end_to_end_gateway_replay.py` [NEW — Wave 3: 21 tests]

---

## Wave Summary

### Wave 1 — ReplayBundle Model (Hashed, Minimal, Sufficient)
- `ReplayBundle`: dataclass with `schema_version` (enforced == 1), `mission_id` (non-empty), `execution_start_tick` (>= 0), `execution_end_tick` (>= start), `manifest_hash` (non-empty), `active_config_hashes` (dict, keys sorted in canonical_bytes), `retrieval_used` (bool), `citation_hash` (required iff retrieval_used=True), `prior_detection_signal_hash` (str, empty if none), `prior_violation_event_hashes` (sorted list[str]), `tool_intent_hashes` (sorted list[str]), `tool_result_hashes` (sorted list[str]), `replay_hash` (sha256 of canonical_bytes excluding replay_hash)
- `canonical_bytes()`: excludes `replay_hash`; sorts all list fields; sorts `active_config_hashes` keys; no volatile fields
- `build_replay_bundle()`: factory with sensible defaults
- Sorting: lists passed in any order produce identical `replay_hash` after normalisation

### Wave 2 — L4 Store + ReplayVerifier (Integrity + Prior-Only)
- `ReplayBundleStore`: in-process dict store keyed by `replay_hash`; idempotent; non-mutating to knowledge index
- `ReplayVerifier.verify()`: checks (1) hash integrity via recomputation, (2) component presence in provided registries, (3) prior-only constraints (`prior_signal_tick < execution_start_tick`, all `prior_violation_ticks < execution_start_tick`)
- `ReplayVerificationError(code, detail)`: typed exception with codes: `REPLAY_HASH_MISMATCH`, `MISSING_CITATION_HASH`, `MISSING_CONFIG_HASH`, `MISSING_SIGNAL_HASH`, `MISSING_VIOLATION_HASH`, `MISSING_INTENT_HASH`, `MISSING_RESULT_HASH`, `SAME_CYCLE_SIGNAL`, `SAME_CYCLE_VIOLATION`
- `VerifiedReplay`: result dataclass with `replay_hash`, `mission_id`, ticks, `checks_passed`

### Wave 3 — End-to-End Gateway Emission + Non-Mutating Guarantees
- `emit_replay_bundle()`: builds + persists `ReplayBundle` to `ReplayBundleStore`; non-mutating to knowledge index
- Case A: no retrieval, no tools → bundle emitted, verifier passes with `hash_integrity`
- Case B: retrieval used → `citation_hash` present in bundle, verifier passes with `citation_hash_present`
- Case C: inject same-cycle signal/violation at `execution_start_tick` → verifier fails with `SAME_CYCLE_SIGNAL`/`SAME_CYCLE_VIOLATION`
- Static AST audit: zero `upsert`/`setex` calls in both `replay_bundle_emitter.py` and `replay_bundle_store.py`

---

## Required Proof Commands (Verbatim, captured from clean tree after commit 0f0a0d4a6)

### 1. python --version
```
Python 3.12.10
```

### 2. python -m pytest --version
```
pytest 9.0.2
```

### 3. git status --porcelain=v1
```

```
(EMPTY — clean working tree)

### 4. git diff --name-only
```

```
(EMPTY — no unstaged changes)

### 5. git rev-parse HEAD
```
0f0a0d4a69553495e7038baf9db0814bc036d66c
```

### 6. git log -1 --oneline
```
0f0a0d4a6 (HEAD -> Codemap_defects) phase9: ReplayBundle + ReplayBundleStore + ReplayVerifier + emitter + tests
```

### 7. python -m pytest -q tests/agentic_core/test_phase9_replay_bundle_model.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 29 items

tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleHashStable::test_replay_bundle_hash_stable PASSED [  3%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleHashStable::test_hash_changes_with_mission_id PASSED [  6%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleHashStable::test_hash_changes_with_manifest_hash PASSED [ 10%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleHashStable::test_hash_changes_with_config_hashes PASSED [ 13%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleHashStable::test_hash_changes_with_ticks PASSED [ 17%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleHashStable::test_hash_changes_with_violation_hashes PASSED [ 20%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleHashStable::test_replay_hash_excluded_from_canonical_bytes PASSED [ 24%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleHashStable::test_canonical_bytes_deterministic PASSED [ 27%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleHashStable::test_hash_with_retrieval_used_and_citation PASSED [ 31%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleHashStable::test_hash_changes_with_citation_hash PASSED [ 34%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleSortingDeterministic::test_replay_bundle_sorting_deterministic PASSED [ 37%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleSortingDeterministic::test_violation_hashes_stored_sorted PASSED [ 41%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleSortingDeterministic::test_intent_hashes_stored_sorted PASSED [ 44%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleSortingDeterministic::test_result_hashes_stored_sorted PASSED [ 48%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleSortingDeterministic::test_config_hashes_keys_sorted_in_canonical_bytes PASSED [ 51%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleSortingDeterministic::test_empty_lists_allowed PASSED [ 55%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleRequiresCitationHashWhenRetrievalUsed::test_replay_bundle_requires_citation_hash_when_retrieval_used PASSED [ 58%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleRequiresCitationHashWhenRetrievalUsed::test_retrieval_used_false_no_citation_hash_ok PASSED [ 62%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleRequiresCitationHashWhenRetrievalUsed::test_retrieval_used_true_with_citation_hash_ok PASSED [ 65%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleRequiresCitationHashWhenRetrievalUsed::test_invalid_schema_version_raises PASSED [ 68%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleRequiresCitationHashWhenRetrievalUsed::test_empty_mission_id_raises PASSED [ 72%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleRequiresCitationHashWhenRetrievalUsed::test_empty_manifest_hash_raises PASSED [ 75%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleRequiresCitationHashWhenRetrievalUsed::test_negative_start_tick_raises PASSED [ 79%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleRequiresCitationHashWhenRetrievalUsed::test_end_tick_before_start_tick_raises PASSED [ 82%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleRequiresCitationHashWhenRetrievalUsed::test_non_dict_config_hashes_raises PASSED [ 86%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestReplayBundleRequiresCitationHashWhenRetrievalUsed::test_non_list_violation_hashes_raises PASSED [ 89%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestBuildReplayBundleFactory::test_factory_produces_valid_bundle PASSED [ 93%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestBuildReplayBundleFactory::test_factory_defaults_no_retrieval PASSED [ 96%]
tests/agentic_core/test_phase9_replay_bundle_model.py::TestBuildReplayBundleFactory::test_to_dict_contains_all_fields PASSED [100%]

============================ slowest 10 durations =============================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 29 passed in 0.07s ==============================
```

### 8. python -m pytest -q tests/agentic_core/test_phase9_replay_verifier.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 21 items

tests/agentic_core/test_phase9_replay_verifier.py::TestReplayBundleStore::test_store_and_fetch PASSED [  4%]
tests/agentic_core/test_phase9_replay_verifier.py::TestReplayBundleStore::test_fetch_missing_returns_none PASSED [  9%]
tests/agentic_core/test_phase9_replay_verifier.py::TestReplayBundleStore::test_idempotent_store PASSED [ 14%]
tests/agentic_core/test_phase9_replay_verifier.py::TestReplayBundleStore::test_count_increments PASSED [ 19%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsMissingComponent::test_verifier_rejects_missing_component PASSED [ 23%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsMissingComponent::test_verifier_rejects_missing_config_hash PASSED [ 28%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsMissingComponent::test_verifier_rejects_missing_signal_hash PASSED [ 33%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsMissingComponent::test_verifier_rejects_missing_violation_hash PASSED [ 38%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsMissingComponent::test_verifier_rejects_missing_intent_hash PASSED [ 42%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsMissingComponent::test_verifier_rejects_missing_result_hash PASSED [ 47%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsMissingComponent::test_verifier_passes_when_all_hashes_present PASSED [ 52%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsHashTampering::test_verifier_rejects_hash_tampering PASSED [ 57%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsHashTampering::test_verifier_passes_on_untampered_bundle PASSED [ 61%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsHashTampering::test_verified_replay_carries_mission_id PASSED [ 66%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsHashTampering::test_verified_replay_carries_ticks PASSED [ 71%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsSameCycleInfluence::test_verifier_rejects_same_cycle_influence PASSED [ 76%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsSameCycleInfluence::test_verifier_rejects_future_signal PASSED [ 80%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsSameCycleInfluence::test_verifier_passes_prior_signal PASSED [ 85%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsSameCycleInfluence::test_verifier_rejects_same_cycle_violation PASSED [ 90%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsSameCycleInfluence::test_verifier_passes_prior_violation PASSED [ 95%]
tests/agentic_core/test_phase9_replay_verifier.py::TestVerifierRejectsSameCycleInfluence::test_verifier_no_signal_hash_skips_prior_only_check PASSED [100%]

============================ slowest 10 durations =============================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 21 passed in 0.06s ==============================
```

### 9. python -m pytest -q tests/agentic_core/test_phase9_end_to_end_gateway_replay.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 21 items

tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseANoRetrievalNoTools::test_bundle_emitted_no_retrieval_no_tools PASSED [  4%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseANoRetrievalNoTools::test_bundle_persisted_and_fetchable PASSED [  9%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseANoRetrievalNoTools::test_verifier_passes_case_a PASSED [ 14%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseANoRetrievalNoTools::test_bundle_hash_stable_case_a PASSED [ 19%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseANoRetrievalNoTools::test_no_retrieval_citation_hash_empty PASSED [ 23%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseBRetrievalUsed::test_bundle_emitted_with_retrieval PASSED [ 28%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseBRetrievalUsed::test_verifier_passes_case_b PASSED [ 33%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseBRetrievalUsed::test_citation_hash_in_canonical_bytes PASSED [ 38%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseBRetrievalUsed::test_bundle_with_prior_violations_and_tools PASSED [ 42%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseBRetrievalUsed::test_verifier_passes_with_all_registries PASSED [ 47%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseCInjectSameCycleSignal::test_verifier_fails_same_cycle_signal_deterministically PASSED [ 52%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseCInjectSameCycleSignal::test_verifier_fails_same_cycle_violation_deterministically PASSED [ 57%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestCaseCInjectSameCycleSignal::test_verifier_fails_tampered_hash_deterministically PASSED [ 61%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestStaticAuditNonMutatingEmitter::test_emitter_module_exists PASSED [ 66%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestStaticAuditNonMutatingEmitter::test_store_module_exists PASSED [ 71%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestStaticAuditNonMutatingEmitter::test_emitter_contains_zero_upsert_calls PASSED [ 76%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestStaticAuditNonMutatingEmitter::test_store_module_contains_zero_upsert_calls PASSED [ 80%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestStaticAuditNonMutatingEmitter::test_emitter_imports_replay_bundle_store PASSED [ 85%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestStaticAuditNonMutatingEmitter::test_emitter_imports_build_replay_bundle PASSED [ 90%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestStaticAuditNonMutatingEmitter::test_store_module_defines_verifier PASSED [ 95%]
tests/agentic_core/test_phase9_end_to_end_gateway_replay.py::TestStaticAuditNonMutatingEmitter::test_store_module_defines_verification_error PASSED [100%]

============================ slowest 10 durations =============================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 21 passed in 0.06s ==============================
```

---

## PASS/FAIL Table

| Objective | Test / Proof | Status |
|-----------|-------------|--------|
| git status --porcelain=v1 is EMPTY | proof cmd 3 | PASS |
| git diff --name-only is EMPTY | proof cmd 4 | PASS |
| git rev-parse HEAD = 0f0a0d4a69553495e7038baf9db0814bc036d66c | proof cmd 5 | PASS |
| **Obj 1: ReplayBundle hash stable** | test_replay_bundle_hash_stable | PASS |
| **Obj 1: Sorting deterministic — lists in any order produce same hash** | test_replay_bundle_sorting_deterministic | PASS |
| **Obj 1: citation_hash required when retrieval_used=True** | test_replay_bundle_requires_citation_hash_when_retrieval_used | PASS |
| **Obj 1: replay_hash excluded from canonical_bytes** | test_replay_hash_excluded_from_canonical_bytes | PASS |
| **Obj 2: store_replay_bundle + fetch_replay_bundle** | test_store_and_fetch | PASS |
| **Obj 2: store is idempotent** | test_idempotent_store | PASS |
| **Obj 2: verifier rejects missing citation_hash** | test_verifier_rejects_missing_component | PASS |
| **Obj 2: verifier rejects missing config_hash** | test_verifier_rejects_missing_config_hash | PASS |
| **Obj 2: verifier rejects hash tampering (REPLAY_HASH_MISMATCH)** | test_verifier_rejects_hash_tampering | PASS |
| **Obj 2: verifier rejects same-cycle signal (SAME_CYCLE_SIGNAL)** | test_verifier_rejects_same_cycle_influence | PASS |
| **Obj 2: verifier rejects same-cycle violation (SAME_CYCLE_VIOLATION)** | test_verifier_rejects_same_cycle_violation | PASS |
| **Obj 2: verifier passes prior signal (tick < start)** | test_verifier_passes_prior_signal | PASS |
| **Obj 3: Case A — no retrieval, no tools → bundle emitted, verifier passes** | test_verifier_passes_case_a | PASS |
| **Obj 3: Case B — retrieval used → citation_hash present, verifier passes** | test_verifier_passes_case_b | PASS |
| **Obj 3: Case C — same-cycle signal injection → verifier fails deterministically** | test_verifier_fails_same_cycle_signal_deterministically | PASS |
| **Obj 3: bundle persisted and fetchable from store** | test_bundle_persisted_and_fetchable | PASS |
| **Static audit: zero upsert/setex in emitter** | test_emitter_contains_zero_upsert_calls | PASS |
| **Static audit: zero upsert/setex in store** | test_store_module_contains_zero_upsert_calls | PASS |
| **Total: 71 tests, 0 failures** | all three test files | PASS |

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

