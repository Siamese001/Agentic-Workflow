# G4b — Kill Switches and Risk Ranking

ADG snapshot: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

This file focuses only on runtime control surfaces that can materially bypass policy/guard behavior or alter critical pipeline stages.

## 1. Critical kill-switches (ranked)

| Rank | Key | Severity | Reader(s) | Pipeline impact | Store impact | Why critical |
|---:|---|---|---|---|---|---|
| 1 | `EGRESS_GUARD_DISABLED` | **critical** | `agentic_core/L2_execution/enforcement/network_egress_guard.py` | Mutates `PIPE-INFERENCE-LLM` and `PIPE-APP-REQUEST` egress enforcement stages | indirect | Disables REQ-414 egress guard checks; known B7-G2b-06 (no audit trail requirement) |
| 2 | `DISABLE_RUNTIME_MUTATION_GUARD` | **critical** | `agentic_core/L0_routing/enforcement/runtime_mutation_guard.py` | Weakens core runtime mutation protection during pipeline bootstrap | none | Bypasses REQ-417 guard at installation path |
| 3 | `SOVEREIGN_AUTO_APPROVE` | **critical** | `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py` | Can auto-approve destructive archival ops in HITL-adjacent flows | `STORE-HITL` (approval records) | Governance override; intentionally ignored by `hitl_gate.py` and `exit_control_hitl.py` but active in archival gatekeeper |
| 4 | `ARCHIVE_BATCH_ACCEPT` | **high** | same as above | Same branch class as `SOVEREIGN_AUTO_APPROVE` | `STORE-HITL` | Batch destructive-op auto-approval |
| 5 | `ADG_SKIP_SELF_TEST` | **high** | `tools/generate/generate_full_adg.py` / scanner | Mutates `PIPE-ADG-GEN` validation stages | ADG artefact quality path | Can suppress scanner self-test guardrails |
| 6 | `ADG_SKIP_REDIS` | **high** | `tools/generate/generate_full_adg.py` | Skips `PIPE-ADG-GEN` stage `s09` ingest | `STORE-REDIS-ADG-HOT` | Leaves ADG cache cold; query latency/behavior drift |
| 7 | `VECTOR_DB_ALLOW_MODEL_DOWNLOAD` | **high** | `tools/retrieval/vector_config.py`, `embedder.py` | Changes embedding pipeline branch to online download path | `STORE-CHROMA-CANONICAL` | Converts offline deterministic behavior into external-fetch path |

## 2. High-risk non-bypass toggles

| Key | Severity | Risk type |
|---|---|---|
| `MEMORY_DB` | high | Store-selection drift (three candidate sqlite files in G4) |
| `VECTOR_DB_CHROMA_PATH` | high | Vector store-binding drift (canonical vs artefact path risk) |
| `ADG_REDIS_URL` / `REDIS_*` | high | Endpoint drift and cache partition mismatch |
| `HF_HUB_OFFLINE` | medium | Determinism drift (offline vs fetch behavior) |
| `OTEL_MCP_ALLOW_MOCK_TRACES` | medium | Test-mode leakage into runtime observability |

## 3. Pipeline-shape modifiers (explicit G3 cross-links)

| Key | Affected pipeline(s) | Stage-level effect |
|---|---|---|
| `EGRESS_GUARD_DISABLED` | `PIPE-INFERENCE-LLM`, `PIPE-APP-REQUEST` | bypasses egress guard enforcement before provider call |
| `ADG_SKIP_REDIS` | `PIPE-ADG-GEN` | skips `s09` cache ingest branch |
| `ADG_SKIP_GIT` | `PIPE-ADG-GEN` | skips post-generation git automation branch |
| `ADG_SKIP_SELF_TEST` | `PIPE-ADG-GEN` | skips scanner self-test/validation branch |
| `VECTOR_DB_ALLOW_MODEL_DOWNLOAD` / `HF_HUB_OFFLINE` | `PIPE-EMBEDDING`, `PIPE-VECTOR-RETRIEVAL` | toggles offline-only vs online model-fetch branch |
| `VECTOR_DB_ENABLE_STARTUP_PREWARM` | `PIPE-EMBEDDING` | startup prewarm branch enabled/disabled |
| `OTEL_MCP_ALLOW_MOCK_TRACES` | `PIPE-OBSERVABILITY` | mock trace mode branch |

## 4. Store-binding modifiers (explicit G4 cross-links)

| Key | Store ID(s) |
|---|---|
| `MEMORY_DB` | `STORE-MEMORY-SQLITE-CANONICAL`, `STORE-MEMORY-SQLITE-DUPLICATE`, `STORE-MEMORY-UNIFIED-DB` |
| `VECTOR_DB_CHROMA_PATH` | `STORE-CHROMA-CANONICAL`, `STORE-CHROMA-ARTEFACT`, `STORE-CHROMA-SPARSE` |
| `ADG_REDIS_URL`, `ADG_SKIP_REDIS` | `STORE-REDIS-ADG-HOT` |
| `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_URL`, `REDIS_PASSWORD` | `STORE-REDIS-CACHE-GENERIC`, `STORE-REDIS-COORD`, `STORE-REDIS-RAG` |
| `VECTOR_DB_COUNT_CACHE_TTL` | `STORE-CHROMA-CANONICAL` (service cache behavior) |

## 5. Risk controls

1. Treat all **critical** keys as change-controlled knobs (ticket + traceability note).
2. Disallow `EGRESS_GUARD_DISABLED=1` outside controlled debug/test runs.
3. Require restart after mutating `import_time` / `process_start` keys.
4. Keep `VECTOR_DB_ALLOW_MODEL_DOWNLOAD=0` + `HF_HUB_OFFLINE=1` as baseline for deterministic offline behavior.
5. Pin `MEMORY_DB` to canonical artefact path until G4 B7-G4-03 is resolved.
6. Verify Redis hot sentinel (`adg:v1:<ts>:_hot`) after any ADG regeneration where `ADG_SKIP_REDIS` is not intentionally set.

## 6. Relationship to existing B7 items

This wave does not introduce net-new architectural B7 items. It operationalizes existing risk signals:

- **B7-G2b-06** (`EGRESS_GUARD_DISABLED` audit gap)
- **B7-G4-03** (`MEMORY_DB` ambiguity across three sqlite files)
- **B7-G4-07** (Redis operational posture / no TTL discipline)
