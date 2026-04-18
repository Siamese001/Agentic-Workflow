# G7 — Whole-System Runtime Map

wave: G7
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
adg_snapshot_timestamp: "04182026_0814"

## 1. Integrated counts and topology frame

- Major runtime process surfaces integrated (from G5 backbone): **27**
- Major storage surfaces integrated (from G4 backbone): **33**
- Major control-plane families integrated (from G4b): **7**
- G6 normalization candidates integrated into status model: **14**

Status model used in this map:

- `canonical`
- `special_case`
- `unresolved`

## 2. Major integrated runtime surfaces

| surface_id | surface_type | ownership | main_process_or_runtime_location | main_storage_surfaces_touched | main_control_plane_knobs | major_pipelines_touched | main_failure_domain | related_wave_f_atom_ids | related_wave_f_edge_ids | related_g6_decision | related_residual_ids | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G7-RS-01 | app_runtime_bundle (apps_eval/exec/lic/research/rfp/rg) | repo-managed | `apps_*/__main__.py` in-process runtimes | `STORE-MEMORY-SQLITE-CANONICAL`, `STORE-REDIS-*`, `STORE-CHROMA-CANONICAL` | provider selectors, feature flags, `MEMORY_DB`, Redis keys | `PIPE-APP-REQUEST`, `PIPE-INFERENCE-LLM`, `PIPE-EVAL-EXIT` | FD-01 | `F01.05`, `F02.01`, `F03.01`, `F05.01`, `F06.01` | `INT-F02.01-F01.05-01`, `INT-F05.01-F02.03-01`, `INT-F06.02-F03.01-01` | mixed (`G6-S003`,`G6-S004`,`G6-S005`,`G6-S007`) | `B7-G3-02`, `B7-G3-05` | canonical |
| G7-RS-02 | core_runtime_library_plane | repo-managed | `agentic_core/*` imported in-process | memory/redis/runtime-adg stores | runtime mutation guard, model/provider flags | `PIPE-APP-REQUEST`, `PIPE-HEALING`, `PIPE-OBSERVABILITY` | FD-01 | `F05.01`, `F06.01`, `F07.01`, `F11.01` | `INT-F07.03-F02.01-01` | `G6-S013` | `B7-G6-04` | unresolved |
| G7-RS-03 | adg_generation_and_hotcache | mixed-control | `tools/generate_full_adg.py` + `tools/adg/adg_redis_ingest.py` + ADG MCP | `STORE-ADG-SQLITE`, `STORE-REDIS-ADG-HOT` | `ADG_REDIS_URL`, `ADG_SKIP_*`, ADG_DIR knobs | `PIPE-ADG-GEN`, `PIPE-ADG-REDIS-INGEST` | FD-02 / FD-03 | `F10.02`, `F12.04` | `INT-F12.03-F09.01-01` (indirect policy relation only) | none | `B7-G4-01`, `B7-G4-02` | canonical |
| G7-RS-04 | memory_lifecycle_surface | mixed-control | memory MCP (`tools/memory/adg_memory_server.py`) + memory sqlite files | `STORE-MEMORY-SQLITE-CANONICAL`, duplicate sqlite candidates | `MEMORY_DB`, cleanup windows | `PIPE-MEMORY-LIFECYCLE` | FD-03 / FD-01 | `F12.07`, `F10.02` | `INT-F12.07-F02.01-01` | `G6-S009` | `B7-G4-03`, `B7-G6-03` | unresolved |
| G7-RS-05 | vector_retrieval_embedding_surface | mixed-control | vector_db MCP + in-process retrieval | `STORE-CHROMA-CANONICAL`, `STORE-CHROMA-ARTEFACT`, sparse cache | `VECTOR_DB_*`, `HF_HUB_OFFLINE`, model-download flags | `PIPE-VECTOR-RETRIEVAL`, `PIPE-EMBEDDING` | FD-04 | `F04.01`, `F04.02` | unresolved | `G6-S010` | `B7-G4-05` | special_case |
| G7-RS-06 | redis_cache_coord_surface | operator-managed (runtime) + repo-managed (clients) | local Redis daemon + redis clients/MCP tools | `STORE-REDIS-ADG-HOT`, `STORE-REDIS-COORD`, `STORE-REDIS-RAG`, `STORE-REDIS-CACHE-GENERIC`, `bench:*` | `REDIS_URL`, `REDIS_HOST/PORT/DB`, auth/ssl knobs | `PIPE-APP-REQUEST`, `PIPE-ADG-REDIS-INGEST`, `PIPE-HEALING` | FD-03 | `F10.02` | unresolved | `G6-S011` | `B7-G4-04`, `B7-G4-07` | special_case |
| G7-RS-07 | observability_runtime_adg_surface | repo-managed (code) + operator-managed (collector endpoint) | `tools/otel/*` + `system_learning/runtime_adg/*` + sidecar | `STORE-RUNTIME-ADG-ARTEFACTS` | OTel collector endpoint/env, telemetry toggles | `PIPE-OBSERVABILITY` | FD-05 | `F12.01`, `F12.04`, `F12.08` | `INT-F12.08-F08.03-01` | none | `B7-G3-03` | special_case |
| G7-RS-08 | mcp_transport_plane | mixed-control | 9 python stdio MCP + 2 binary subprocess + 1 external endpoint | touches ADG/memory/redis/vector/git metadata stores depending on MCP | `.windsurf/mcp_config.json` env injection + launcher paths | tool-mediated portions of `PIPE-APP-REQUEST` | FD-06 / FD-07 | `F03.01`, `F11.01` (policy authority context only) | unresolved | `G6-S014` | G5 operational ambiguity set, `B7-G6-05` | unresolved |
| G7-RS-09 | provider_egress_boundary | operator-managed | remote provider endpoints + local vLLM + gateway wrappers | indirect state via eval/outcome stores | provider keys, egress guard toggles | `PIPE-INFERENCE-LLM`, `PIPE-INFERENCE-VLLM` | FD-07 | `F07.01`, `F07.02`, `F11.01` | unresolved | `G6-S008` (for declared-not-wired Pinecone only) | `B7-G2b-02`, `B7-G2b-06`, `B7-G3-05` | unresolved |
| G7-RS-10 | governance_exit_writegate_surface | repo-managed | L5 safety/exit-control + write-gate pathways | reports/evidence/hitl/outcome artifacts and authoritative state writes | `DISABLE_RUNTIME_MUTATION_GUARD`, `SOVEREIGN_AUTO_APPROVE`, `ARCHIVE_BATCH_ACCEPT` | `PIPE-EVAL-EXIT`, `PIPE-EVAL-HITL` | FD-08 | `F08.01`, `F08.02`, `F08.04`, `F09.01`, `F11.04`, `F11.05` | `INT-F08.04-F09.01-01`, `INT-F09.04-F11.04-01` | none | G4b override posture set | unresolved |
| G7-RS-11 | contract_surface_integrity | repo-managed | `agentic_core/L_CONTRACTS/`, `execution_trace_types` duplicates, seams/interfaces | n/a (contract/type surfaces) | n/a | cross-cutting contract use by multiple pipelines | FD-01 / FD-08 | `F08.02`, `F11.05` (execution-trace policy bind intent) | `INT-F08.02-F11.05-01` | `G6-S001`, `G6-S006` | `B7-G6-01`, `B7-G6-02` | unresolved |
| G7-RS-12 | replay_and_system_learning_partial_surfaces | repo-managed | replay runner + `system_learning/*` partial topology | runtime ADG artifacts, memory/read models | replay toggles, learning toggles | `PIPE-REPLAY`, `PIPE-SYSTEM-LEARNING` | FD-05 / FD-01 | `F12.04`, `F12.05` | `INT-F12.05-F12.07-01` | none | `B7-G3-04`, `B7-G3-06` | unresolved |

## 3. What talks to what (integrated interaction chains)

1. App request chain: app runtime -> L0 routing/L1 planning/L3 orchestration/L2 execution -> provider and data surfaces -> L5 evaluation/exit -> write-gate pathways.
2. ADG maintenance chain: operator/CI trigger -> ADG generator -> snapshot sqlite -> Redis hot-cache ingestion -> ADG MCP query plane.
3. Memory chain: session-start recall -> runtime observations -> memory MCP store -> later-run reasoning consumption.
4. Vector chain: retrieval requests -> vector_db service -> Chroma collections -> embeddings and semantic search.
5. Observability chain: runtime traces/outcomes -> OTel ingest/runtime ADG -> telemetry queries and reports.

## 4. Ownership posture summary

- `repo-managed` dominant: core runtime logic, pipelines, policy logic, and most MCP Python servers.
- `operator-managed` dominant: local daemon lifecycle (Redis), external endpoints/accounts (DeepWiki, Notion, provider APIs, GitKraken remote behaviors).
- `mixed-control` concentration: memory, vector, MCP transport, and network egress boundaries.
- Explicit unresolved ownership formalization remains (`B7-G6-05`).

## 5. Residual visibility in this map

The following remain visible by design (not hidden):

- dead/unwired L_CONTRACTS contract surface (`B7-G6-01`)
- duplicate execution-trace contract ownership (`B7-G6-02`)
- memory SQLite triplet ambiguity (`B7-G4-03` / `B7-G6-03`)
- orphan/vestigial storage artifacts (`B7-G4-02`, `B7-G4-04`, `B7-G4-05`)
- control-plane bypass posture (G4b residual set)
- partial replay and partial system_learning topology (`B7-G3-04`, `B7-G3-06`)
