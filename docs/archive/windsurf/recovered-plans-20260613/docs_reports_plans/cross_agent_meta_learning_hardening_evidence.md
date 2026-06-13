# Cross-Agent Meta-Learning FAISS Hardening

## Scope

Three gaps identified by full codebase audit (all agents, not just execute_ssot-aligned):

- **G_RS**: `EmbeddingRetentionScheduler.run_once()` — no `persist_to_disk()` after rebuild
- **G_HI**: `historical_ingestion_orchestrator.ingest_and_build_indexes_with_embedder()` — no `persist_to_disk()` after build
- **G_MLA**: `MetaLearningAgent.strategy_weights` — in-memory only, lost on restart

Files changed (4):
- `agentic_core/L1_cognition/reasoning/MetaLearningAgent.py`
- `system_learning/engines/embedding_retention_scheduler.py`
- `system_learning/engines/historical_ingestion_orchestrator.py`
- `tests/system_learning/test_cross_agent_meta_learning_hardening.py`

## CODE_COMMIT

882ab0e27e9ef527ceea6e4a8e5fe820a8e9c1ad

## EVIDENCE_COMMIT

1e912091b9bd29db3e68f9e3eeadaff7ace2dc18

## FILES_CHANGED_CODE

agentic_core/L1_cognition/reasoning/MetaLearningAgent.py
system_learning/engines/embedding_retention_scheduler.py
system_learning/engines/historical_ingestion_orchestrator.py
tests/system_learning/test_cross_agent_meta_learning_hardening.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/cross_agent_meta_learning_hardening_evidence.md

## INSPECTED_FILES

- agentic_core/L1_cognition/reasoning/MetaLearningAgent.py
- system_learning/engines/embedding_retention_scheduler.py
- system_learning/engines/historical_ingestion_orchestrator.py
- system_learning/engines/local_faiss_store.py
- system_learning/config/embedding_storage_layout.py
- agentic_core/L1_cognition/memory/healing_memory_retriever.py
- tests/system_learning/test_cross_agent_meta_learning_hardening.py
- tests/system_learning/test_faiss_bge_hardening.py

## Pytest Targeted Suite

$ python -m pytest -q --color=no tests/system_learning/test_cross_agent_meta_learning_hardening.py tests/system_learning/test_faiss_bge_hardening.py

48 passed, 69 warnings in 0.46s

## AntiPattern Check

$ python ops_scripts/ci/check_anti_patterns.py

[OK] 2223 existing violations, 0 new violations

## Gap Table

| Gap ID | Component | Root Cause | Fix Applied |
|--------|-----------|------------|-------------|
| G_RS | EmbeddingRetentionScheduler.run_once() | rebuild() updates in-memory index but never calls persist_to_disk(); pruned state lost on restart | Added persist_base_path param; persist_to_disk() called after rebuild in both rolling_window and predicate modes |
| G_HI | historical_ingestion_orchestrator.ingest_and_build_indexes_with_embedder() | populate_from_jsonl() calls finalize_build() (in-memory only); no persist_to_disk() call; all indexes lost at process exit | Added persist_to_disk() for healing_contexts_v1, telemetry_events_v1, dpo_pairs_v1 using EmbeddingStorageLayout paths |
| G_MLA | MetaLearningAgent.strategy_weights | Pure in-memory dict reset to defaults on every restart; no persistence mechanism | Added strategy_weights_file constructor param, _load_strategy_weights(), _save_strategy_weights(); auto-saves after update_strategy_weights() |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

