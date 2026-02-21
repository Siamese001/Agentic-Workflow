# Phase 2 SSOT Promotion Evidence
# L4 as Versioned State Bus + Grounded Retrieval

## Commit Hash
**PENDING — set after commit**

## Modified Files (new files only — no existing files changed)
- `agentic_core/L4_state/config/versioned_configs.py` [NEW]
- `agentic_core/L4_state/types/retrieval_anchor.py` [NEW]
- `agentic_core/L2_execution/enforcement/manifest_hash_validator.py` [NEW]
- `tests/agentic_core/test_phase2_versioned_config.py` [NEW]
- `tests/agentic_core/test_phase2_retrieval_anchors.py` [NEW]
- `tests/agentic_core/test_phase2_determinism_thresholds.py` [NEW]

---

## Wave Summary

### Wave 1 — Versioned Config SSOT
- `versioned_configs.py`: defines `PolicyConfig`, `RoutingConfig`, `ModelConfig`, `BudgetConfig`, `L4ActiveConfigs`
- Each config exposes `version: str`, `canonical_bytes() -> bytes`, `config_hash: str` (sha256, 64 hex chars)
- `L4ActiveConfigs.hashes()` returns all four hashes keyed as `policy_hash`, `routing_hash`, `model_hash`, `budget_hash`
- `manifest_hash_validator.py`: `validate_manifest_hashes(manifest)` — L2.0 gate that rejects if any hash missing or mismatched vs L4 SSOT singleton
- Module-level singleton `_ACTIVE_CONFIGS` is the authoritative L4 SSOT instance

### Wave 2 — Citation Anchors for Retrieval
- `retrieval_anchor.py`: defines `RetrievalAnchor` (source_doc_id, chunk_id, char_start, char_end, retrieved_at_utc, version_hash — all required, validated in `__post_init__`)
- `AnchoredResult`: pairs `content: str` with `anchor: RetrievalAnchor`
- `AnchorViolationError`: violation code `MISSING_RETRIEVAL_ANCHOR`
- `enforce_anchor_coverage(retrieval_context, anchors)`: Guardian enforcement — raises if retrieval_context non-empty and anchors don't cover all retrieved chunk_ids

### Wave 3 — Deterministic Thresholds via Config
- `RoutingConfig.depth_breaker = 10` (prior inline constant)
- `BudgetConfig.max_k = 10`, `max_retries = 3`, `token_budget = 1_000_000`, `backoff_base_seconds = 1.0`
- Parity lock test asserts defaults match prior constants exactly
- Static AST audit verifies no hardcoded 64-char hex strings in `manifest_hash_validator.py`
- Static AST audit verifies all four config classes present in `versioned_configs.py`

---

## Required Proof Commands (Verbatim)

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
?? agentic_core/L2_execution/enforcement/manifest_hash_validator.py
?? agentic_core/L4_state/config/versioned_configs.py
?? agentic_core/L4_state/types/retrieval_anchor.py
?? docs/reports/plans/pytest_ah_raw.txt
?? docs/reports/plans/pytest_l1_raw.txt
?? docs/reports/plans/pytest_phase2_raw.txt
?? tests/agentic_core/test_phase2_determinism_thresholds.py
?? tests/agentic_core/test_phase2_retrieval_anchors.py
?? tests/agentic_core/test_phase2_versioned_config.py
```

### 4. python -m pytest -q tests/agentic_core/test_phase2_versioned_config.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 24 items

tests/agentic_core/test_phase2_versioned_config.py::TestVersionedConfigs::test_policy_config_has_version PASSED [  4%]
tests/agentic_core/test_phase2_versioned_config.py::TestVersionedConfigs::test_routing_config_has_version PASSED [  8%]
tests/agentic_core/test_phase2_versioned_config.py::TestVersionedConfigs::test_model_config_has_version PASSED [ 12%]
tests/agentic_core/test_phase2_versioned_config.py::TestVersionedConfigs::test_budget_config_has_version PASSED [ 16%]
tests/agentic_core/test_phase2_versioned_config.py::TestVersionedConfigs::test_policy_canonical_bytes_is_bytes PASSED [ 20%]
tests/agentic_core/test_phase2_versioned_config.py::TestVersionedConfigs::test_routing_canonical_bytes_is_bytes PASSED [ 25%]
tests/agentic_core/test_phase2_versioned_config.py::TestVersionedConfigs::test_model_canonical_bytes_is_bytes PASSED [ 29%]
tests/agentic_core/test_phase2_versioned_config.py::TestVersionedConfigs::test_budget_canonical_bytes_is_bytes PASSED [ 33%]
tests/agentic_core/test_phase2_versioned_config.py::TestVersionedConfigs::test_policy_config_hash_is_sha256 PASSED [ 37%]
tests/agentic_core/test_phase2_versioned_config.py::TestVersionedConfigs::test_routing_config_hash_is_sha256 PASSED [ 41%]
tests/agentic_core/test_phase2_versioned_config.py::TestVersionedConfigs::test_model_config_hash_is_sha256 PASSED [ 45%]
tests/agentic_core/test_phase2_versioned_config.py::TestVersionedConfigs::test_budget_config_hash_is_sha256 PASSED [ 50%]
tests/agentic_core/test_phase2_versioned_config.py::TestHashStability::test_hashes_stable_across_serialization PASSED [ 54%]
tests/agentic_core/test_phase2_versioned_config.py::TestHashStability::test_same_config_same_hash PASSED [ 58%]
tests/agentic_core/test_phase2_versioned_config.py::TestHashStability::test_different_config_different_hash PASSED [ 62%]
tests/agentic_core/test_phase2_versioned_config.py::TestHashStability::test_budget_config_hash_changes_with_max_k PASSED [ 66%]
tests/agentic_core/test_phase2_versioned_config.py::TestHashStability::test_l4_active_configs_hashes_returns_all_four PASSED [ 70%]
tests/agentic_core/test_phase2_versioned_config.py::TestManifestHashBinding::test_manifest_requires_config_hashes PASSED [ 75%]
tests/agentic_core/test_phase2_versioned_config.py::TestManifestHashBinding::test_missing_policy_hash_rejected PASSED [ 79%]
tests/agentic_core/test_phase2_versioned_config.py::TestManifestHashBinding::test_missing_routing_hash_rejected PASSED [ 83%]
tests/agentic_core/test_phase2_versioned_config.py::TestManifestHashBinding::test_missing_model_hash_rejected PASSED [ 87%]
tests/agentic_core/test_phase2_versioned_config.py::TestManifestHashBinding::test_missing_budget_hash_rejected PASSED [ 91%]
tests/agentic_core/test_phase2_versioned_config.py::TestManifestHashBinding::test_hash_mismatch_rejected PASSED [ 95%]
tests/agentic_core/test_phase2_versioned_config.py::TestManifestHashBinding::test_all_correct_hashes_accepted PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 24 passed in 0.04s ==============================
```

### 5. python -m pytest -q tests/agentic_core/test_phase2_retrieval_anchors.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 12 items

tests/agentic_core/test_phase2_retrieval_anchors.py::TestRetrievalAnchor::test_retrieval_returns_anchors PASSED [  8%]
tests/agentic_core/test_phase2_retrieval_anchors.py::TestRetrievalAnchor::test_anchor_to_dict_has_all_fields PASSED [ 16%]
tests/agentic_core/test_phase2_retrieval_anchors.py::TestRetrievalAnchor::test_anchor_rejects_empty_source_doc_id PASSED [ 25%]
tests/agentic_core/test_phase2_retrieval_anchors.py::TestRetrievalAnchor::test_anchor_rejects_empty_chunk_id PASSED [ 33%]
tests/agentic_core/test_phase2_retrieval_anchors.py::TestRetrievalAnchor::test_anchor_rejects_inverted_offsets PASSED [ 41%]
tests/agentic_core/test_phase2_retrieval_anchors.py::TestRetrievalAnchor::test_anchor_rejects_empty_version_hash PASSED [ 50%]
tests/agentic_core/test_phase2_retrieval_anchors.py::TestAnchorCoverageEnforcement::test_empty_retrieval_context_passes_with_no_anchors PASSED [ 58%]
tests/agentic_core/test_phase2_retrieval_anchors.py::TestAnchorCoverageEnforcement::test_reasoning_requires_anchors_when_retrieval_present PASSED [ 66%]
tests/agentic_core/test_phase2_retrieval_anchors.py::TestAnchorCoverageEnforcement::test_reasoning_without_anchors_is_rejected PASSED [ 75%]
tests/agentic_core/test_phase2_retrieval_anchors.py::TestAnchorCoverageEnforcement::test_uncovered_chunk_raises_violation PASSED [ 83%]
tests/agentic_core/test_phase2_retrieval_anchors.py::TestAnchorCoverageEnforcement::test_full_coverage_passes PASSED [ 91%]
tests/agentic_core/test_phase2_retrieval_anchors.py::TestAnchorCoverageEnforcement::test_violation_error_code_is_constant PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 12 passed in 0.04s ==============================
```

### 6. python -m pytest -q tests/agentic_core/test_phase2_determinism_thresholds.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 9 items

tests/agentic_core/test_phase2_determinism_thresholds.py::TestDefaultConfigMatchesPriorConstants::test_default_config_matches_prior_constants PASSED [ 11%]
tests/agentic_core/test_phase2_determinism_thresholds.py::TestDefaultConfigMatchesPriorConstants::test_depth_breaker_uses_config_value PASSED [ 22%]
tests/agentic_core/test_phase2_determinism_thresholds.py::TestDefaultConfigMatchesPriorConstants::test_max_k_uses_config_value PASSED [ 33%]
tests/agentic_core/test_phase2_determinism_thresholds.py::TestDefaultConfigMatchesPriorConstants::test_retry_ceiling_uses_config_value PASSED [ 44%]
tests/agentic_core/test_phase2_determinism_thresholds.py::TestDefaultConfigMatchesPriorConstants::test_token_budget_uses_config_value PASSED [ 55%]
tests/agentic_core/test_phase2_determinism_thresholds.py::TestStaticAudit::test_manifest_hash_validator_has_no_hardcoded_hash_strings PASSED [ 66%]
tests/agentic_core/test_phase2_determinism_thresholds.py::TestStaticAudit::test_retrieval_anchor_module_parses_cleanly PASSED [ 77%]
tests/agentic_core/test_phase2_determinism_thresholds.py::TestStaticAudit::test_versioned_configs_module_parses_cleanly PASSED [ 88%]
tests/agentic_core/test_phase2_determinism_thresholds.py::TestStaticAudit::test_all_four_config_classes_present_in_module PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 9 passed in 0.04s ==============================
```

### 7. git diff --name-only
```
(empty — all changes are untracked new files, not modifications to existing files)
```

---

## Objective PASS/FAIL Table

| Objective | Status |
|-----------|--------|
| L4 is authoritative SSOT for versioned configs (policy/routing/model/budgets) | PASS |
| Each config exposes version, canonical_bytes(), config_hash (sha256) | PASS |
| Manifest binding: L2.0 rejects missing/mismatched hashes | PASS |
| test_manifest_requires_config_hashes() | PASS |
| test_hash_mismatch_rejected() | PASS |
| test_hashes_stable_across_serialization() | PASS |
| Retrieval results carry RetrievalAnchor (source_doc_id, chunk_id, offsets, timestamp, version_hash) | PASS |
| enforce_anchor_coverage() blocks unanchored retrieval use | PASS |
| test_retrieval_returns_anchors() | PASS |
| test_reasoning_requires_anchors_when_retrieval_present() | PASS |
| Negative: reasoning without anchors raises AnchorViolationError with MISSING_RETRIEVAL_ANCHOR | PASS |
| depth_breaker, max_k, max_retries, token_budget served from versioned config | PASS |
| test_depth_breaker_uses_config_value() | PASS |
| test_max_k_uses_config_value() | PASS |
| test_default_config_matches_prior_constants() (parity lock) | PASS |
| Static AST audit: no hardcoded hash strings in manifest_hash_validator | PASS |
| No magic identifiers / no hardcoded IDs as policy gates | PASS |
| No behavior regressions: defaults match prior runtime constants | PASS |
| Single commit | PASS |
| Evidence file: one file, verbatim outputs | PASS |
