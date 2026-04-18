# G3 — Trigger Matrix

Every catalogued pipeline (from `pipeline_catalogue.yaml`) mapped to its triggering surface(s).

**Canonical trigger taxonomy — 9 classes**, split into two bands:

- **6 pipeline-fired classes** used as `kind:` values in `pipeline_catalogue.yaml` — `cli`, `app_entry`, `mcp_tool`, `workflow`, `import`, `internal_call`.
- **3 infrastructural classes** that affect pipeline execution but are not `kind:` values in the YAML — `hook` (Windsurf pre/post hooks), `ci` (GitHub CI workflows), `operator` (env-var kill-switches, HITL approvals).

Earlier drafts used `api` and `cli_or_test` as trigger kinds. Per G3.1 reconciliation, `api` → `internal_call` (programmatic API call from another caller) and `cli_or_test` → `cli` (tests invoke the CLI entry). Test triggering is covered under §5 as a CI/test surface that fires the `cli` band.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

## 1. Pipeline × Trigger matrix

| Pipeline | cli | app_entry | mcp_tool | workflow | import | internal_call | notes |
|---|:-:|:-:|:-:|:-:|:-:|:-:|---|
| PIPE-APP-REQUEST | ✓ | ✓ | — | — | — | — | `python -m apps_*` + `governed_*_run.py` |
| PIPE-EVAL-EXIT | — | — | — | — | — | ✓ | called from PIPE-APP-REQUEST s10 |
| PIPE-EVAL-HITL | — | — | — | — | — | ✓ | from ExitControlGate.ESCALATE_TO_HITL |
| PIPE-HEALING | — | — | — | — | — | ✓ | guardrail failure signals |
| PIPE-INFERENCE-LLM | — | — | — | — | — | ✓ | from PIPE-APP-REQUEST s07, PIPE-HEALING s05 |
| PIPE-INFERENCE-VLLM | — | — | — | — | — | ✓ | from qwen_inference_gateway (6 apps + healers) |
| PIPE-EMBEDDING | — | — | — | — | — | ✓ | retrieval / memory / healing |
| PIPE-VECTOR-RETRIEVAL | — | — | ✓ | — | — | ✓ | `vector_db` MCP tools + retrieval layers |
| PIPE-ADG-GEN | ✓ | — | — | ✓ | — | — | `/adg-redis-refresh` |
| PIPE-ADG-REDIS-INGEST | ✓ | — | — | — | — | ✓ | called by PIPE-ADG-GEN s09 |
| PIPE-MEMORY-LIFECYCLE | ✓ | — | ✓ | — | — | — | `memory` MCP + `purge_sync.py` |
| PIPE-REPLAY | ✓ | — | — | — | — | ✓ | `replay_eval_runner.py` + X1D dimension |
| PIPE-JUDGE-EVAL | — | — | — | — | — | ✓ | `JudgeOrchestrator.evaluate(...)` API |
| PIPE-OBSERVABILITY | — | — | — | — | — | ✓ | `_emit_*` helpers throughout runtime |
| PIPE-APP-BOOTSTRAP-RG | — | — | — | — | ✓ | — | `import apps_rg` side effect |
| PIPE-APP-BOOTSTRAP-EXEC | — | — | — | — | ✓ | — | `import apps_exec` side effect |
| PIPE-SYSTEM-LEARNING | ✓ | — | — | — | — | ✓ | `pipeline_factory.py` + scripts |

## 2. CLI triggers

| Command | Pipeline | Notes |
|---|---|---|
| `python tools/generate_full_adg.py` | PIPE-ADG-GEN | delegates to `tools/generate/generate_full_adg.py::main` |
| `python tools/adg/adg_redis_ingest.py` | PIPE-ADG-REDIS-INGEST | flags: `--force`, `--check`, `--dry-run` |
| `python tools/memory/purge_sync.py` | PIPE-MEMORY-LIFECYCLE | stale-entity purge with telemetry |
| `python tools/adg/adg_stale_guard.py` | SM-09 (not a pipeline) | staleness probe |
| `python -m apps_lic` | PIPE-APP-REQUEST | APP-LIC entry |
| `python -m apps_rg` | PIPE-APP-REQUEST + PIPE-APP-BOOTSTRAP-RG | APP-RG entry (bootstrap runs first) |
| `python -m apps_research` | PIPE-APP-REQUEST | APP-RESEARCH entry |
| `python agentic_core/evaluation/runners/replay_eval_runner.py` | PIPE-REPLAY | |
| `python agentic_core/evaluation/runners/offline_eval_runner.py` | PIPE-JUDGE-EVAL (offline mode) | |
| `tools/diag/*.py` | PIPE-VECTOR-RETRIEVAL + others | diagnostic scripts (out of main runtime) |

## 3. MCP-tool triggers

Per G2b `mcp_as_transport.md`:

| MCP tool | Pipeline |
|---|---|
| `vector_db.semantic_search` / `query_collection` / `embed_text` | PIPE-VECTOR-RETRIEVAL |
| `memory.mem_recall_session_start` / `create_entities` / `add_observations` / `search_nodes` / `mem_cleanup_stale` / `mem_import_adg_context` | PIPE-MEMORY-LIFECYCLE |
| `adg_sqlite.adg_health` / `adg_node` / `adg_nodes_by_file` / `adg_edge_fanin` / `adg_edge_fanout` | (infra probe — not a pipeline) |
| `pytest_mcp.run_tests` / `discover_tests` / `analyze_test_coverage` | (test-triggered; see §5 below) |
| `enhanced_http.http_get` / `http_post` / `batch_requests` | **Cascade-driven programmatic HTTP** (no repo-side pipeline; per constitutional rule) |
| `otel_mcp.otel_trace` / `otel_anomalies` / `otel_policy_decisions` | PIPE-OBSERVABILITY (read side) |
| `redis.*` | (infra probe) |
| `notion.API-*` | Cascade ↔ Notion (outside repo runtime) |
| `GitKraken.*` | Cascade ↔ git host (outside repo runtime) |
| `deepwiki.*` | Cascade ↔ external MCP URL |
| `task_manager.*` | Cascade ↔ task tracker (outside repo) |
| `filesystem.*` | Cascade ↔ local FS (outside repo runtime) |

## 4. Workflow triggers

From `.windsurf/workflows/*.md`:

| Workflow | Pipeline |
|---|---|
| `/adg-redis-refresh` | PIPE-ADG-GEN → PIPE-ADG-REDIS-INGEST |
| `/adg-repair-loop` | PIPE-HEALING (graph-first repair variant) |
| `/adg-test-triage-gate` | PIPE-JUDGE-EVAL (ADG fan-in triage) |
| `/adg-timeout-recovery` | PIPE-HEALING (timeout subset) |
| `/memory-purge-sync` | PIPE-MEMORY-LIFECYCLE |
| `/structured-reasoning` | (meta — governs Cascade, not runtime) |
| `/mcp-failure-rca` | (meta — RCA workflow) |
| `/hitl-decision-gate` | (meta — Cascade HITL before tool calls) |

## 5. Test / CI triggers

| Trigger | Pipeline |
|---|---|
| `pytest tests/` | fires PIPE-APP-BOOTSTRAP-RG on any `import apps_rg`; fires PIPE-APP-BOOTSTRAP-EXEC on any `import apps_exec`; fires PIPE-APP-REQUEST in integration tests; fires PIPE-OBSERVABILITY via `_emit_*` |
| `.github/workflows/adg-ci-gates.yml` | CI gate — calls `python ops_scripts/ci/run_contract_gates.py` |
| `.github/workflows/guardian-tests.yml` | guardian assertions |
| `.github/workflows/infra_wiring_check.yml` | boundary-violation gates |
| pre-commit hooks (`.pre-commit-config.yaml`) | line-ending, trailing whitespace, pytest config SSOT |

**CI does NOT directly fire runtime pipelines** — it fires analysis / gate scripts (`ops_scripts/ci/**`). Those scripts import runtime modules but do not execute PIPE-APP-REQUEST.

## 6. Hook / side-effect triggers

| Hook | Effect | Pipeline |
|---|---|---|
| `pre_mcp_gate` | blocks all MCP calls until `mem_recall_session_start` runs | indirectly PIPE-MEMORY-LIFECYCLE s01 |
| `pre_run_gate.py` | blocks PowerShell commands before subprocess | no direct pipeline |
| `pre_prompt_classifier.py` | injects SR_MANDATE for T2/T3 tasks | meta — governs Cascade |
| `post_cascade_adg_audit.py` | retroactive ADG-first violation detection | writes to `artifacts/windsurf/adg_first_violations.jsonl` |
| `import apps_rg` (module-load side effect) | runs `bootstrap_runtime.py` | PIPE-APP-BOOTSTRAP-RG |
| `import apps_exec` (module-load side effect) | runs `_optional_agentic_core.py` | PIPE-APP-BOOTSTRAP-EXEC |

## 7. Operator triggers

Distinct from CLI — "operator" = human-in-the-loop outside of a shell command.

| Surface | Pipeline |
|---|---|
| Human approves HITL packet | PIPE-EVAL-HITL (H4 input validation) |
| Human sets `EGRESS_GUARD_DISABLED=1` | mutates PIPE-INFERENCE-LLM s03 (egress guard bypass) — B7-G2b-06 |
| Human sets `ADG_SKIP_REDIS=1` | mutates PIPE-ADG-GEN s09 (skip Redis auto-ingest) |
| Human sets `ADG_SKIP_GIT=1` | mutates PIPE-ADG-GEN s10 (skip auto-commit) |
| Human sets `SOVEREIGN_AUTO_APPROVE=1` | **has NO effect on PIPE-EVAL-HITL** (per exit_control_hitl.py invariant) |
| Human runs `/memory-purge-sync` | PIPE-MEMORY-LIFECYCLE s06 |

## 8. Dynamic-dispatch stage shape

Per G2 §Class 3, these stages have runtime-variable shape:

| Stage | Dispatch source | Effect |
|---|---|---|
| PIPE-APP-REQUEST s06 (model_routing) | `ModelRouter` data tables | provider chosen at runtime from TaskComplexity + budget |
| PIPE-HEALING s04 (strategy_select) | `healing_router.py` + registry | strategy chosen from heal classifier output |
| PIPE-JUDGE-EVAL s03 (route_judges) | rubric metadata | deterministic vs LLM branch chosen per rubric |
| L0 seams → L5 validators | `importlib.import_module` (20+ matches in L0 seams) | validator instantiated dynamically |

## 9. Trigger-surface risk

| Trigger class | Risk level | Rationale |
|---|---|---|
| CLI | low | explicit, audited, in shell history |
| app_entry (`python -m apps_*`) | low | user-initiated |
| mcp_tool | medium | Cascade can trigger at will; enhanced_http egresses arbitrarily |
| workflow | low | user-initiated |
| import side-effect | **medium** | test runners trigger bootstrap shims unexpectedly; G1b adapter patterns B+D |
| internal_call | low | observable via trace |
| operator (env var) | **high** | `EGRESS_GUARD_DISABLED` kill-switch has no audit; B7-G2b-06 |
| hook | medium | meta-governance; pre_mcp_gate is critical |
| CI | low | read-only gates, no runtime execution |

## 10. Summary

- **17 pipelines** catalogued (see `pipeline_catalogue.yaml`).
- **9 state machines** catalogued (see `state_machines.md`).
- **9 trigger classes** in canonical taxonomy (per §1):
  - 6 pipeline-fired (appear as `kind:` in YAML): `cli`, `app_entry`, `mcp_tool`, `workflow`, `import`, `internal_call`.
  - 3 infrastructural (do not appear as `kind:`): `hook`, `ci`, `operator`.
- **Biggest surface**: `internal_call` (most pipelines are fired from within other pipelines — consistent with layered runtime).
- **Highest-risk surface**: operator env-var kill-switches (`EGRESS_GUARD_DISABLED`, `DISABLE_RUNTIME_MUTATION_GUARD`, `ADG_SKIP_*`).
- **Only autonomous external-egress trigger**: `enhanced_http` MCP tool (Cascade → any URL).
