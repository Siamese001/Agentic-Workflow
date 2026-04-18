# G3 — Pipelines and State Transitions

## 1. Sub-wave ID, title, one-line purpose

**G3** — *Pipelines and State Transitions*. Catalogue named runtime pipelines, state machines, and their trigger surfaces using G2 wiring and G2b egress maps as the baseline.

## 2. Inputs

- **ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611). `adg_health` = healthy; `graph_projection.stale = false`. Same snapshot as G1/G1b/G2/G2b.
- **G0 planning**: `output_contracts.md` §"Pipeline catalogue schema (G3)", `runtime_scope_map.md`, `dependency_and_risk_register.md`, `wave_g_execution_plan.md`.
- **G1 / G1b**: `component_inventory.yaml`, `layer_embodiment_map.md`, `app_inventory.yaml`, `app_to_core_bindings.md`, `adapter_patterns.md`.
- **G2**: `canonical_request_walk.md` (12-stage skeleton — refined into PIPE-APP-REQUEST), `import_edge_matrix.md` (bridge hubs), `boundary_violations.md` (dynamic-wiring sites), `seam_usage_report.md`.
- **G2b**: `egress_points.yaml` (12 egress points bound into inference pipelines), `provider_inventory.md` (SovereignLLMGateway, ModelRouter, MultiProviderRouterAgent, EmbeddingSovereignAgent), `env_key_consumer_map.md` (kill-switch and config-knob trigger surfaces), `mcp_as_transport.md` (MCP-tool triggers).
- **Repo inspection**: `agentic_core/L5_safety/enforcement/exit_control_gate.py` (525 lines, HITL-001/003), `exit_control_hitl.py` (381 lines, HITL-004 H1–H5), `agentic_core/runtime/engine/agent_engine.py` (297 lines, Observe–Think–Act), `eval_spine.py` (self-declared NON_CANONICAL_EVAL_LAB), `orchestrator_state_retry.py`, `apps_rg/bootstrap_runtime.py`, `apps_exec/_optional_agentic_core.py`, `tools/generate/generate_full_adg.py`, `tools/adg/adg_redis_ingest.py`, `tools/memory/purge_sync.py`, `tools/retrieval/vector_service.py`, `agentic_core/evaluation/judges/orchestrator.py`, `agentic_core/L2_execution/healers/**`, `agentic_core/L6_observability/**`.

## 3. Outputs

- `README.md` — this index.
- `pipeline_catalogue.yaml` — **17 pipelines** conforming to G0 schema.
- `state_machines.md` — **9 state machines** (distinguished from linear pipelines).
- `trigger_matrix.md` — pipeline × trigger cross-reference across 9 trigger classes.

## 4. Stop condition

Met.

- **Every mandatory pipeline family covered**:
  1. Canonical request pipeline → `PIPE-APP-REQUEST` (14 stages, operator trigger → memory write-back)
  2. Healing / retry / escalation → `PIPE-HEALING` (9 stages; uses `SM-03 OrchestratorStateRetry`)
  3. Evaluation / exit-control / UWG → `PIPE-EVAL-EXIT` + `PIPE-EVAL-HITL` (both with state machines SM-01 / SM-02)
  4. Replay / determinism → `PIPE-REPLAY` (partial — see §5)
  5. Memory lifecycle → `PIPE-MEMORY-LIFECYCLE`
  6. ADG regeneration → `PIPE-ADG-GEN` (+ companion `PIPE-ADG-REDIS-INGEST`)
  7. Vector retrieval / embedding → `PIPE-VECTOR-RETRIEVAL` + `PIPE-EMBEDDING`
  8. Provider inference pipelines (distinct) → `PIPE-INFERENCE-LLM` (SovereignLLMGateway path) and `PIPE-INFERENCE-VLLM` (hardened circuit-breaker path)
  9. App-specific bootstrap pipelines → `PIPE-APP-BOOTSTRAP-RG` + `PIPE-APP-BOOTSTRAP-EXEC`
  - Plus `PIPE-JUDGE-EVAL` (canonical evaluation), `PIPE-OBSERVABILITY` (L6), `PIPE-SYSTEM-LEARNING` (partial).
- **State machines identified and distinguished from pipelines**: 9 SMs in `state_machines.md`, each with states, entry/exit conditions, and invariants. Linear pipelines explicitly not claimed as state machines.
- **Trigger matrix covers** CLI, app_entry, MCP tool, workflow, import side-effect, internal_call, hook, CI, and operator env-var trigger classes. `trigger_matrix.md` §§1–9.
- **G2 canonical_request_walk.md refined into named pipeline** (`PIPE-APP-REQUEST` inherits its 12-stage skeleton with 2 additional stages for bootstrap and memory write-back).
- **G2b egress points bound**: `PIPE-INFERENCE-LLM` cites EGRESS-OPENAI/ANTHROPIC/GEMINI-01; `PIPE-INFERENCE-VLLM` cites EGRESS-QWEN-VLLM-LOCAL-01; `PIPE-EMBEDDING` cites EGRESS-GEMINI-01/EGRESS-HF-HUB-01; `PIPE-VECTOR-RETRIEVAL` uses MCP vector_db; `PIPE-ADG-REDIS-INGEST` cites EGRESS-REDIS-01.
- **Schema validation**: every pipeline entry records `id`, `title`, `triggers`, `inputs`, `stages`, `outputs`, `terminal_condition`, `source_modules`, `embodies_atoms`, `embodies_edges`, `notes`.
- **Dynamic-dispatch stages declared explicitly** (`trigger_matrix.md` §8): ModelRouter dispatch, healing_router strategy selection, judge routing, L0-seam → L5-validator `importlib`.
- **Gaps recorded honestly** — see §5.

## 5. Risks encountered during execution

- **PIPE-REPLAY is partial**. Observed primitives (`replay_eval_runner.py`, `emit_replay_key`, `emit_determinism_digest`) are sufficient to name the pipeline but the full replay topology (digest canonicalization, divergence scoring, mismatch triage) is not fully enumerated in this pass. Recorded as an honest gap in `pipeline_catalogue.yaml` note.
- **PIPE-SYSTEM-LEARNING is partial**. `system_learning/` has 28+ subpackages (`adapters`, `arbitration`, `confidence`, `correlation`, `embedding`, `enforcement`, `engines`, `fingerprinting`, `golden`, `invariants`, `meta_learning`, `ml_integration`, `monitoring`, `output`, `policy`, `provenance`, `runtime`, `runtime_adg`, `snapshots`, `state`, `stores`, `telemetry`, `types`, `validators`). Only `system_learning/pipelines/` traced at G3. Deeper enumeration deferred to G3b.
- **eval_spine.py is NON_CANONICAL**. The file header explicitly states: "EVAL-PIPELINE SCOPE: NON_CANONICAL_EVAL_LAB ... no durable writes, no UWG handoff, no L5 exit gate." G3 records its OptimizationStage as SM-05 but does NOT treat `commit_optimization()` as a real runtime commit. The CANONICAL evaluation path is `PIPE-JUDGE-EVAL` + `PIPE-EVAL-EXIT`.
- **PIPE-OBSERVABILITY L6→lower-layer reads** — G2 `boundary_violations.md` flagged 44 L6→L0/L2 `L6_downstream_mutation` breaches. G3 catalogues the pipeline but notes L6 is not a pure observer in practice.
- **Bootstrap pipelines are import side-effects** — `PIPE-APP-BOOTSTRAP-RG` and `PIPE-APP-BOOTSTRAP-EXEC` fire on module import, not from a deliberate trigger. Recorded in `trigger_matrix.md` §6 as medium risk.
- **Dynamic dispatch in ModelRouter** — cannot statically enumerate every provider-selection branch. Recorded per G2b §R-G-02; G3 names the dispatch point (stage s06) but does not trace all branches.
- **No v1.4 atom/edge IDs were cross-referenced**. `embodies_atoms` and `embodies_edges` are empty arrays for every pipeline (per schema tolerance — array is allowed empty). Wave F v1.4 canonical ID resolution is deferred to G7 traceability.
- **Linear-pipeline-vs-state-machine ambiguity** resolved: `state_machines.md` §10 explicitly lists what is NOT a state machine to pre-empt confusion.

## 6. B7 candidates surfaced

- **B7-G3-01** — `eval_spine.py` OptimizationStage (SM-05) and `commit_optimization()` are declared non-canonical yet use the canonical-sounding `commit_*` naming. Risk: future callers mistake it for the real UWG commit path. Recommend either renaming or a runtime guard that rejects `commit_optimization()` calls from non-lab contexts. G7 owns.
- **B7-G3-02** — `PIPE-APP-BOOTSTRAP-RG` and `PIPE-APP-BOOTSTRAP-EXEC` mutate `sys.modules` on import (G1b adapter patterns B+D). No v1.4 atom scopes "import side-effects that synthesize agentic_core.* modules". Decide whether this is expected or a B7 missing atom.
- **B7-G3-03** — `PIPE-OBSERVABILITY` L6 pipeline includes reads from L0/L2 that G2 flagged as `L6_downstream_mutation` breaches. Either v1.4 needs an edge `L6 MAY read L0 shared constants` or the code needs refactoring. Propagates G2 B7.
- **B7-G3-04** — `PIPE-REPLAY` is partial. Full replay topology needs enumeration in G3b or a dedicated replay wave. If replay determinism is a constitutional claim (X1D dimension), the underlying pipeline must be traceable end-to-end.
- **B7-G3-05** — `PIPE-INFERENCE-LLM` retry posture is `retries=3` default with **no circuit breaker** at the SovereignLLMGateway layer. Per-provider hardened wrappers (hardened_vllm, hardened_gemini) have circuit breakers; the canonical gateway does not. Either promote circuit breaker to gateway or add an atom that requires per-provider adapters to own circuit protection. G7 decides.
- **B7-G3-06** — `PIPE-SYSTEM-LEARNING` is partial; `system_learning/` has substantial surface area not yet traced. If any production decision depends on these pipelines (meta-learning → promotion → commit), G3b must complete the catalogue.

## 7. Hand-off note for G3b and G4

### For G3b (deeper pipeline traceability)

- Complete **PIPE-REPLAY** — replay_eval_runner full stage enumeration, divergence scoring, digest canonicalization.
- Complete **PIPE-SYSTEM-LEARNING** — trace each of `system_learning/{adapters, arbitration, confidence, correlation, meta_learning, enforcement, policy, runtime, validators}`.
- Trace ModelRouter's actual dispatch branches (data-driven) for the three most-used apps (APP-RG, APP-LIC, APP-EXEC).
- Attach `embodies_atoms` / `embodies_edges` to each pipeline using the F v1.4 canonical IDs.
- Trace PIPE-APP-REQUEST for each concrete app (APP-EVAL, APP-EXEC, APP-LIC, APP-RESEARCH, APP-RFP, APP-RG, APP-SHARED, APP-UNDERWRITING-AI) to confirm stage shape matches the generic skeleton.

### For G4 (storage topology)

- PIPE outputs list every durable artefact at pipeline-stage granularity: ADG SQLite snapshots (`adg_indexed_<ts>.sqlite`, 4 JSON tiers, `graphsnap`), Redis namespace `adg:v1:<ts>:*`, memory SQLite (`artifacts/memory/knowledge_graph.sqlite`), ChromaDB (`data/cache/chromadb/`), runtime-ADG trace files, dashboard snapshot payloads, verdict store, approval ledger. G4 is the canonical owner.
- Memory purge sync telemetry (`docs/reports/telemetry/memory_purge_<ts>.json`) is a recurring G4 artefact.
- Retention policies (how many ADG snapshots kept, memory cleanup windows, Redis TTL) are not in G3 — G4 responsibility.

### Sign-off status

- **G3 is ready for sign-off**.
- **G3b can start immediately.**
- **G4 can start in parallel with G3b** (G4 depends only on G3 pipeline output-artefact names, which are frozen in `pipeline_catalogue.yaml`).

## Summary counts

| Dimension | Value |
|---|---:|
| Pipelines catalogued | **17** |
| State machines | **9** |
| Mandatory pipeline families covered | 9 / 9 |
| Trigger classes mapped | 9 total — 6 pipeline-fired (`cli`, `app_entry`, `mcp_tool`, `workflow`, `import`, `internal_call`) + 3 infrastructural (`hook`, `ci`, `operator`) |
| Dynamic-dispatch stages flagged | 4 |
| B7 candidates surfaced | 6 |
| Partial pipelines (honest gaps) | 2 (PIPE-REPLAY, PIPE-SYSTEM-LEARNING) |
