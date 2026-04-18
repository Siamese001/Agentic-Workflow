# G3 — State Machines

Pipelines vs state machines: a **pipeline** is a linear (or branching) stage list that terminates; a **state machine** holds state across invocations, has explicit states, and has rules for entering / leaving each state. This file enumerates only the real stateful flows.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

## SM-01 — ExitDisposition state (ExitControlGate)

**Module**: `agentic_core/L5_safety/enforcement/exit_control_gate.py` (525 lines).

Not a multi-state holder — it is an **explicit one-shot dispatch** with strong invariants. Catalogued here because every request traverses it and the invariants are critical.

| State / disposition | Meaning | Next |
|---|---|---|
| `ALLOW_RESPONSE` | all 4 dimensions pass, no commit payload | return to operator |
| `DENY_RETURN` | any safety/policy dimension fails | return error to operator |
| `ESCALATE_TO_HITL` | confidence below threshold OR explicit escalation_reason | enter SM-02 (H1 freeze) |
| `COMMIT_TO_UWG` | all dimensions pass + has_commit_payload=True | write via UWG |

**Invariant**: "Every code path produces an explicit ExitDisposition. No silent fallback. No catch-all."

## SM-02 — Authority state (ExitControlHITL H1–H5)

**Module**: `agentic_core/L5_safety/enforcement/exit_control_hitl.py` (381 lines).

Full state machine with freeze / un-freeze transitions.

| State | `authority_state` | `write_auth` | Entry | Exit |
|---|---|---|---|---|
| `H1_FROZEN` | FROZEN | NONE | ESCALATE_TO_HITL disposition | H2 |
| `H2_PACKET_MATERIALIZED` | FROZEN | NONE | bounded packet built from sealed data | H3 |
| `H3_AWAITING_HUMAN` | FROZEN | NONE | packet delivered to human | H4 on response, or indefinite |
| `H4_VALIDATING_RESPONSE` | FROZEN | NONE | human response received (UNTRUSTED DATA) | H5 if validator clears |
| `H5_RECLEARANCE_EVAL` | RE-CLEARING | NONE | L5 validator passed | ALLOW_RESPONSE / DENY_RETURN / COMMIT_TO_UWG |

**Invariants**:
- `MODIFY_DIFF` without re-clear → BLOCKED.
- `APPROVE` bypassing L5 re-clearance → BLOCKED.
- No `SOVEREIGN_AUTO_APPROVE` bypass.
- No `ARCHIVE_BATCH_ACCEPT` bypass.
- No TTY interaction — always materializes a packet.
- Human response is always UNTRUSTED DATA routed through L5 validator before any authority delta.

## SM-03 — OrchestratorStateRetry

**Module**: `agentic_core/L3_orchestration/core/orchestrator_state_retry.py` (45 lines — observed runtime shim).

Simple retry-counter state machine. State is carried across invocations of `.run(payload)`.

| State | `attempts` | `retry_exhausted` | Transition |
|---|---|---|---|
| `FRESH` | 0 | False | reset() or first instantiation |
| `IN_PROGRESS` | 1..max | False | each .run() increments |
| `EXHAUSTED` | > max | True | .run() when attempts > max_attempts |
| `RESET` | 0 | False | .reset() clears state |

**Guard**: `can_retry()` returns `attempts < max_attempts`. Default `max_attempts = 3`.

## SM-04 — CircuitBreaker (hardened vLLM client)

**Module**: `agentic_core/L3_orchestration/inference/qwen_vllm/engines/hardened_vllm_client.py` (370 lines).

Classic three-state circuit breaker.

| State | Accept requests? | Entry | Exit |
|---|---|---|---|
| `CLOSED` | yes | initial or from HALF_OPEN success | failure_count ≥ threshold → OPEN |
| `OPEN` | **no — rejected** | from CLOSED on threshold breach | open_timeout expires → HALF_OPEN |
| `HALF_OPEN` | yes (limited probes) | from OPEN after timeout | probe success → CLOSED; probe fail → OPEN |

Also present in `apps_shared/types/hardened_gemini_executor_types.py` (tenacity + inline CircuitBreaker) and `apps_lic/tools/GoogleSearchClient.py` (CircuitBreakerProtocol injected).

## SM-05 — OptimizationStage (eval_spine — NON_CANONICAL)

**Module**: `agentic_core/runtime/engine/eval_spine.py` (451 lines).

`class OptimizationStage(str, Enum)`. Models in-memory proposal lifecycle for the **non-canonical eval lab** (explicit disclaimer in file header — no durable writes, no UWG handoff).

| State | Meaning |
|---|---|
| `PROPOSED` | optimization proposal registered |
| `GATED` | gates evaluated (groundedness / P@K / MRR / NDCG / completeness / drift) |
| `APPROVED` | all gates passed |
| `COMMITTED` | `commit_optimization()` called — in-memory only |
| `REJECTED` | any gate failed |

**Invariant**: "`commit_optimization()` mutates in-memory OptimizationProposal stage only; no durable writes, no UWG handoff, no L5 exit gate." — this is NOT the canonical evaluation pipeline (that is PIPE-JUDGE-EVAL + PIPE-EVAL-EXIT).

## SM-06 — MemoryEntity lifecycle

**Module**: `tools/memory/sqlite_memory_store.py` + `tools/memory/purge_sync.py`.

Entities persist in `artifacts/memory/knowledge_graph.sqlite` across Windsurf restarts.

| State | Description | Transition rule |
|---|---|---|
| `FRESH` | created within current retention window | time advances |
| `STALE` | `updated_at` older than `older_than_days` (default 7 or 30) | `mem_cleanup_stale` removes unless protected |
| `PROTECTED` | entityType in PROTECTED_TYPES set | NEVER deleted by cleanup |

**Protected types**: `ArchitectureLayer`, `ProjectContext`, `ConstitutionalRule`, `EpisodicEvent`, `ProceduralPattern`, `ArchitecturalDecision`.

## SM-07 — Redis hot-cache sentinel

**Module**: `tools/adg/adg_redis_ingest.py`.

| State | Redis key | Meaning |
|---|---|---|
| `COLD` | `adg:v1:<ts>:_hot` absent | cache not populated for snapshot |
| `HOT` | `adg:v1:<ts>:_hot = 1` | ingest complete; ADG MCP hits cache directly |
| `DEGRADED` | `_hot` set but keys missing | partial ingest — not observed in code but possible |

`--check` exits 0 if HOT, 1 if COLD. `--force` flushes old snapshot keys before re-ingesting.

## SM-08 — Dashboard health aggregate

**Module**: `agentic_core/L6_observability/utils/dashboard/dashboard_aggregate.py`.

| State | Meaning |
|---|---|
| `HEALTHY` | all component health flags OK |
| `DEGRADED` | at least one non-critical component flag raised |
| `CRITICAL` | one or more critical flags raised |
| `UNKNOWN` | health signals not yet collected |

Not a transition machine per-se — a rollup. Catalogued because it is the visible health state of the runtime.

## SM-09 — ADG snapshot staleness

**Module**: `tools/adg/adg_stale_guard.py` + `mcp1_adg_health`.

| State | Source | Meaning |
|---|---|---|
| `FRESH` | `graph_projection.stale = false` | projection matches on-disk SQLite mtime |
| `STALE` | `graph_projection.stale = true` | SQLite newer than projection; `adg_reload` needed |
| `MISSING` | no snapshot file | ADG never regenerated |

Transition: PIPE-ADG-GEN produces a new snapshot → projection becomes stale until `adg_reload` is called.

## 10. What is NOT a state machine

- `api_gateway_integration.py` `GatewayMetrics` — rolling metrics, not state transitions.
- `SovereignLLMGateway` ProviderType enum — dispatch selector, not a stateful machine.
- `FailureSignal` — a data object, not a machine.
- The HTTP retry loop in `enhanced_http` tools — retries are per-call, no cross-call state.

## 11. Summary

| ID | Module | Canonical-runtime? | Notes |
|---|---|---|---|
| SM-01 | `exit_control_gate.py` | Yes | single-shot dispatch with invariants |
| SM-02 | `exit_control_hitl.py` | Yes | H1–H5 freeze/re-clear machine |
| SM-03 | `orchestrator_state_retry.py` | Yes | 45-line retry counter |
| SM-04 | `hardened_vllm_client.py` | Yes | 3-state circuit breaker (also in hardened_gemini) |
| SM-05 | `eval_spine.py` OptimizationStage | **No — non-canonical** | in-memory only |
| SM-06 | `sqlite_memory_store.py` + `purge_sync.py` | Yes (persistent across sessions) | |
| SM-07 | `adg_redis_ingest.py` hot sentinel | Yes | COLD/HOT/DEGRADED |
| SM-08 | `dashboard_aggregate.py` | Yes | health rollup |
| SM-09 | `adg_stale_guard.py` | Yes | FRESH/STALE/MISSING |

**9 state machines** in the runtime. Pipelines without state machines (PIPE-ADG-GEN, PIPE-VECTOR-RETRIEVAL, PIPE-EMBEDDING, PIPE-OBSERVABILITY, app bootstrap pipelines) are purely linear / tree-shaped stage lists.
