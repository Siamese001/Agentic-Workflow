# Phase 4 Evidence — Meta-Learning Write Governance + Compatibility

## Commit Hash
**7fd290e31** — phase4: ML write envelope enforcement + versioned compatibility + MLCacheConfig

## Modified / New Files
- `agentic_core/L2_execution/types/ml_write_intent.py` [NEW]
- `agentic_core/L2_execution/types/ml_pattern_record.py` [NEW]
- `agentic_core/L4_state/config/versioned_configs.py` [MODIFIED — added MLCacheConfig + get_ml_cache_config()]
- `tests/agentic_core/test_phase4_ml_write_envelope.py` [NEW]
- `tests/agentic_core/test_phase4_ml_compatibility.py` [NEW]
- `tests/agentic_core/test_phase4_ml_cache_policy.py` [NEW]

---

## Wave Summary

### Wave 1 — ML Write Envelope Enforcement (L2.2 Sandbox)
- `ml_write_intent.py`: `MLWriteIntent` dataclass with `kind` ("pattern_store"|"cache_set"), `payload` (dict), `requires_commit=True` (enforced), `intent_hash` (sha256 of canonical_bytes, auto-computed)
- `MLWriteEnvelopeViolation`: raised with code `ML_WRITE_OUTSIDE_SANDBOX` when intent executed outside sandbox
- `MLWriteIntentExecutor`: context manager that activates `_SANDBOX_ACTIVE` flag; `execute()` checks flag and raises if not inside context
- `execute_ml_write_intent_outside_sandbox()`: explicit enforcement function — always raises if sandbox not active
- Sandbox state restored on exception (`__exit__` always clears `_SANDBOX_ACTIVE`)

### Wave 2 — Versioned Pattern Compatibility (Domain + Policy/Model Hash)
- `ml_pattern_record.py`: `MLPatternRecord` dataclass with `schema_version`, `domain_id`, `domain_hash` (sha256 of domain_id), `policy_hash`, `model_hash`, `pattern_id`, `payload`, `record_hash` (sha256 of canonical_bytes excluding itself)
- `PatternCompatibilityError`: carries `violation_code` — `DOMAIN_HASH_MISMATCH`, `POLICY_HASH_MISMATCH`, or `MODEL_HASH_MISMATCH`
- `enforce_pattern_compatibility(record, query_domain_id, active_policy_hash, active_model_hash)`: checks domain → policy → model in order; raises deterministically on first mismatch; no silent fallback
- `MLPatternRecord.build()`: factory that computes `domain_hash` and `record_hash` automatically from L4 active config hashes

### Wave 3 — Versioned ML Cache Policy + Default Parity
- `versioned_configs.py` `MLCacheConfig`: `version`, `default_ttl_seconds=3600`, `max_entries=1000`, `eviction_mode="lru"` — all included in `canonical_bytes()` (sorted keys) and `config_hash` (sha256)
- `get_ml_cache_config()`: module-level singleton accessor
- Parity lock: `default_ttl_seconds=3600`, `max_entries=1000`, `eviction_mode="lru"` match prior hardcoded behavior
- Static AST audit: `MLCacheConfig` class present in `versioned_configs.py`; `default_ttl_seconds` field declared inside class; literal `3600` does not appear outside `MLCacheConfig` body

---

## Required Proof Commands (Verbatim, captured from clean tree after commit 7fd290e31)

### 1. python --version
```
Python 3.12.10
```

### 2. python -m pytest --version
```
pytest 9.0.2
```

### 3. git status --porcelain=v1  (must be empty)
```

```

### 4. git diff --name-only  (must be empty)
```

```

### 5. git rev-parse HEAD
```
7fd290e3161629b0821c2e64d63df7b91dc08f99
```

### 6. git log -1 --oneline
```
7fd290e31 (HEAD -> Codemap_defects) phase4: ML write envelope enforcement + versioned compatibility + MLCacheConfig
```

### 7. python -m pytest -q tests/agentic_core/test_phase4_ml_write_envelope.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 17 items

tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteIntent::test_build_pattern_store_intent PASSED [  5%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteIntent::test_build_cache_set_intent PASSED [ 11%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteIntent::test_intent_hash_stable PASSED [ 17%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteIntent::test_intent_hash_differs_by_kind PASSED [ 23%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteIntent::test_invalid_kind_raises PASSED [ 29%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteIntent::test_requires_commit_false_raises PASSED [ 35%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteIntent::test_non_dict_payload_raises PASSED [ 41%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteIntent::test_canonical_bytes_deterministic PASSED [ 47%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteSandbox::test_sandbox_inactive_by_default PASSED [ 52%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteSandbox::test_sandbox_active_inside_context PASSED [ 58%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteSandbox::test_sandbox_inactive_after_context PASSED [ 64%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteSandbox::test_ml_write_allowed_inside_commit_sandbox PASSED [ 70%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteSandbox::test_ml_write_blocked_outside_commit_sandbox PASSED [ 76%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteSandbox::test_direct_write_outside_sandbox_raises PASSED [ 82%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteSandbox::test_violation_error_carries_violation_code PASSED [ 88%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteSandbox::test_sandbox_restores_state_on_exception PASSED [ 94%]
tests/agentic_core/test_phase4_ml_write_envelope.py::TestMLWriteSandbox::test_cache_set_allowed_inside_sandbox PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 17 passed in 0.05s ==============================
```

### 8. python -m pytest -q tests/agentic_core/test_phase4_ml_compatibility.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 17 items

tests/agentic_core/test_phase4_ml_compatibility.py::TestMLPatternRecord::test_build_produces_valid_record PASSED [  5%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestMLPatternRecord::test_domain_hash_is_deterministic PASSED [ 11%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestMLPatternRecord::test_different_domains_produce_different_hashes PASSED [ 17%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestMLPatternRecord::test_record_hash_stable PASSED [ 23%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestMLPatternRecord::test_record_hash_changes_with_payload PASSED [ 29%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestMLPatternRecord::test_canonical_bytes_excludes_record_hash PASSED [ 35%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestMLPatternRecord::test_rejects_empty_domain_id PASSED [ 41%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestMLPatternRecord::test_rejects_bad_schema_version PASSED [ 47%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestPatternCompatibilityEnforcement::test_compatible_pattern_passes PASSED [ 52%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestPatternCompatibilityEnforcement::test_pattern_retrieval_filters_by_domain_hash PASSED [ 58%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestPatternCompatibilityEnforcement::test_pattern_retrieval_rejects_policy_hash_mismatch PASSED [ 64%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestPatternCompatibilityEnforcement::test_pattern_retrieval_rejects_model_hash_mismatch PASSED [ 70%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestPatternCompatibilityEnforcement::test_domain_mismatch_takes_priority_over_policy PASSED [ 76%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestPatternCompatibilityEnforcement::test_apps_rg_domain_compatible_with_apps_rg_query PASSED [ 82%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestPatternCompatibilityEnforcement::test_violation_code_constants PASSED [ 88%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestPatternCompatibilityEnforcement::test_policy_hash_from_active_config_matches PASSED [ 94%]
tests/agentic_core/test_phase4_ml_compatibility.py::TestPatternCompatibilityEnforcement::test_model_hash_from_active_config_matches PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 17 passed in 0.07s ==============================
```

### 9. python -m pytest -q tests/agentic_core/test_phase4_ml_cache_policy.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 16 items

tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfig::test_ml_cache_config_has_required_fields PASSED [  6%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfig::test_ml_cache_config_has_canonical_bytes PASSED [ 12%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfig::test_ml_cache_config_has_config_hash PASSED [ 18%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfig::test_canonical_bytes_deterministic PASSED [ 25%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfig::test_config_hash_stable PASSED [ 31%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfig::test_config_hash_changes_with_ttl PASSED [ 37%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfig::test_config_hash_changes_with_max_entries PASSED [ 43%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfig::test_config_hash_changes_with_eviction_mode PASSED [ 50%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfig::test_get_ml_cache_config_returns_singleton PASSED [ 56%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfig::test_ml_cache_ttl_comes_from_versioned_config PASSED [ 62%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfig::test_default_cache_config_matches_prior_behavior PASSED [ 68%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfig::test_canonical_bytes_sorted_keys PASSED [ 75%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfigStaticAudit::test_ml_cache_config_class_present_in_versioned_configs PASSED [ 81%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfigStaticAudit::test_get_ml_cache_config_function_present PASSED [ 87%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfigStaticAudit::test_default_ttl_field_present_in_class PASSED [ 93%]
tests/agentic_core/test_phase4_ml_cache_policy.py::TestMLCacheConfigStaticAudit::test_no_banned_hardcoded_ttl_outside_config_class PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 16 passed in 0.06s ==============================
```

---

## PASS/FAIL Table

| Objective | Test / Proof | Status |
|-----------|-------------|--------|
| git status empty (clean tree) | proof cmd 3 | PASS |
| git diff empty (clean tree) | proof cmd 4 | PASS |
| git rev-parse HEAD = 7fd290e3161629b0821c2e64d63df7b91dc08f99 | proof cmd 5 | PASS |
| git log -1 --oneline matches commit | proof cmd 6 | PASS |
| MLWriteIntent kind validated ("pattern_store"\|"cache_set" only) | test_invalid_kind_raises | PASS |
| MLWriteIntent requires_commit=True enforced | test_requires_commit_false_raises | PASS |
| MLWriteIntent payload must be dict | test_non_dict_payload_raises | PASS |
| intent_hash is sha256 of canonical_bytes, stable | test_intent_hash_stable | PASS |
| Sandbox inactive by default | test_sandbox_inactive_by_default | PASS |
| Sandbox active inside MLWriteIntentExecutor context | test_sandbox_active_inside_context | PASS |
| Sandbox deactivates after context exit | test_sandbox_inactive_after_context | PASS |
| ML write allowed inside commit sandbox | test_ml_write_allowed_inside_commit_sandbox | PASS |
| Negative: ML write blocked outside commit sandbox → MLWriteEnvelopeViolation | test_ml_write_blocked_outside_commit_sandbox | PASS |
| Negative: direct write outside sandbox raises ML_WRITE_OUTSIDE_SANDBOX | test_direct_write_outside_sandbox_raises | PASS |
| Sandbox restores state on exception | test_sandbox_restores_state_on_exception | PASS |
| MLPatternRecord has domain_hash, policy_hash, model_hash, record_hash | test_build_produces_valid_record | PASS |
| domain_hash deterministic (sha256 of domain_id) | test_domain_hash_is_deterministic | PASS |
| Different domains produce different domain_hashes | test_different_domains_produce_different_hashes | PASS |
| record_hash excludes itself from canonical_bytes | test_canonical_bytes_excludes_record_hash | PASS |
| Compatible pattern (matching domain+policy+model) passes | test_compatible_pattern_passes | PASS |
| Negative: pattern_retrieval_filters_by_domain_hash → DOMAIN_HASH_MISMATCH | test_pattern_retrieval_filters_by_domain_hash | PASS |
| Negative: pattern_retrieval_rejects_policy_hash_mismatch → POLICY_HASH_MISMATCH | test_pattern_retrieval_rejects_policy_hash_mismatch | PASS |
| Negative: pattern_retrieval_rejects_model_hash_mismatch → MODEL_HASH_MISMATCH | test_pattern_retrieval_rejects_model_hash_mismatch | PASS |
| Domain mismatch takes priority over policy mismatch | test_domain_mismatch_takes_priority_over_policy | PASS |
| MLCacheConfig has version, default_ttl_seconds, max_entries, eviction_mode | test_ml_cache_config_has_required_fields | PASS |
| MLCacheConfig.canonical_bytes() deterministic with sorted keys | test_canonical_bytes_sorted_keys | PASS |
| MLCacheConfig.config_hash is sha256, stable | test_config_hash_stable | PASS |
| config_hash changes with TTL, max_entries, eviction_mode | test_config_hash_changes_with_ttl + _max_entries + _eviction_mode | PASS |
| get_ml_cache_config() returns singleton | test_get_ml_cache_config_returns_singleton | PASS |
| TTL comes from versioned config (not hardcoded) | test_ml_cache_ttl_comes_from_versioned_config | PASS |
| Parity lock: default_ttl=3600, max_entries=1000, eviction_mode="lru" | test_default_cache_config_matches_prior_behavior | PASS |
| AST: MLCacheConfig class present in versioned_configs.py | test_ml_cache_config_class_present_in_versioned_configs | PASS |
| AST: default_ttl_seconds field declared inside MLCacheConfig | test_default_ttl_field_present_in_class | PASS |
| AST: literal 3600 does not appear outside MLCacheConfig body | test_no_banned_hardcoded_ttl_outside_config_class | PASS |
| Total: 50 tests, 0 failures | all three test files | PASS |
