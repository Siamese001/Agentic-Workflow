---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\test_file_rebalancing_report.md'
original_relative_path: 'test_file_rebalancing_report.md'
source_sha256: c5f42ec935c047ec4b29a344dffe81858badf2f242bd76195a7774d2debd643e
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-12'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Test File Rebalancing Report

## Summary

Refactored 16 oversized/fragmented test files across `tests/` into right-sized shards.
All originals deleted after exact collection-count verification.

---

## Splits (oversized → shards)

| Original | Tests | → Shards | Tests |
|----------|-------|----------|-------|
| `adg/test_meta_learning_bus.py` (122 fn, 16 cls) | 122 | `test_meta_learning_bus_types.py`, `test_meta_learning_bus_engines.py`, `test_meta_learning_bus_pipeline.py` | 122 |
| `adg/test_prompt_provenance_system.py` (119 fn, 13 cls) | 119 | `test_prompt_provenance_types.py`, `test_prompt_provenance_engines.py`, `test_prompt_provenance_integration.py` | 119 |
| `adg/test_bge_embedding_extension.py` + `test_bge_embedding_creative.py` (214 fn) | 214 | `test_bge_embedding_types.py`, `test_bge_embedders.py`, `test_bge_registry.py` | 214 |
| `system_learning/test_gap_fixes.py` (133 fn, 24 cls) | 133 | `test_gap_fixes_core.py`, `test_gap_fixes_advanced.py` | 133 |
| `unit/test_semantic_cache_activation.py` (106 fn, 11 cls) | 106 | `test_semantic_cache_mixin.py` (34), `test_semantic_cache_deep.py` (72) | 106 |

---

## Merges (fragmented families → single file)

| Family (originals) | Tests | → Merged | Tests |
|--------------------|-------|----------|-------|
| `unit_min_deps/test_replay_harness_{artifact_registry,core_determinism,crypto_clock,state_protocol}.py` (4 files) | 39 | `test_replay_harness_contracts.py` | 39 |
| `unit_min_deps/test_meta_learning_pipeline_{commit_path,healing_intake_wiring,ingests_phase9_artifacts,path_d_wiring,pattern_wiring,proposal_only,writes_l4b}.py` (7 files) | 30 | `test_meta_learning_pipeline_wiring.py` | 30 |
| `unit_min_deps/test_vllm_{canonical_payload_lock,invariant_contract,invariant_verifier,replay_tamper_roundtrip,replay_with_violations}.py` (5 files) | 33 | `test_vllm_contracts.py` (22), `test_vllm_replay.py` (11) | 33 |

---

## Validation

All output files verified with `pytest --collect-only -q`. Zero test count delta on every task.

| Output file | Collected |
|-------------|-----------|
| `tests/unit/test_semantic_cache_mixin.py` | 34 |
| `tests/unit/test_semantic_cache_deep.py` | 72 |
| `tests/unit_min_deps/test_replay_harness_contracts.py` | 39 |
| `tests/unit_min_deps/test_meta_learning_pipeline_wiring.py` | 30 |
| `tests/unit_min_deps/test_vllm_contracts.py` | 22 |
| `tests/unit_min_deps/test_vllm_replay.py` | 11 |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

