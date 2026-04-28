# Runtime ADG Coverage Audit — 20260428_055900

**Plan**: `.windsurf/plans/runtime-adg-coverage-audit-4f7a21.md`
**Runtime ADG dir**: `C:/Git/Agentic-Workflow/agentic_core/L4_state/memory/runtime_adg`

## 1. Emitter inventory

- Agent classes discovered: **173**
- Files calling `get_tracer(`: **21**
- Files calling `start_span(` / `as_current_span(`: **25**
- Files using lifecycle emit contract (`emit_*` / `record_execution_trace`): **1528**
- Files calling `.persist(<snapshot>)`: **3**
- Union of any emit signature: **1535** files

### Emit sites by top-level package

| Package | Files with emit signature |
|---|---|
| `agentic_core/` | 1068 |
| `system_learning/` | 155 |
| `apps_rg/` | 112 |
| `apps_shared/` | 110 |
| `apps_lic/` | 39 |
| `apps_eval/` | 15 |
| `apps_exec/` | 14 |
| `apps_rfp/` | 10 |
| `apps_research/` | 9 |
| `apps_underwriting_ai/` | 2 |
| `infrastructure/` | 1 |

### Snapshot persist() call sites

- `agentic_core/L3_orchestration/reasoning/engines/orchestrator_engine.py`
- `agentic_core/L6_observability/otel_runtime_ingest.py`
- `system_learning/runtime_adg/auto_persistence.py`

## 2. Trace-index integrity

- Snapshots in `_index.json`: **1922**
- Snapshots bound to a trace_id: **89**
- Snapshots UNBOUND (no trace_id): **1833** (**95.4%**)
- Empty-string keys in `_trace_index.json`: **0**
- Empty-string values in `_trace_index.json`: **0**
- Dangling trace-index entries (value not in `_index.json`): **0**
- Missing content-addressed files on disk: **0**

## 3. Snapshot schema sampling (N=5)

| Hash | Size | trace_id? | snapshot_id? | Nodes | Edges |
|---|---|---|---|---|---|
| `76ebf103ac2278f1` | 1264 | ✅ | ✅ | 1 | 1 |
| `b6c934e0618eb6d5` | 1358 | ✅ | ✅ | 1 | 1 |
| `af579ec6cef82196` | 1376 | ✅ | ✅ | 1 | 1 |
| `c188272171390e21` | 1262 | ✅ | ✅ | 1 | 1 |
| `fa8608403dbfde5b` | 1308 | ✅ | ✅ | 1 | 1 |

## 4. Gap classification

- **Priority band**: P2
- **Impact**: Severe: the overwhelming majority of persisted snapshots cannot be joined back to a trace. Healing-chain and OTEL-driven meta-learning run on incomplete data.

### Recommended remediation (out of scope for this audit)

1. Audit `FileBackedRuntimeADGStore.persist()` callers; enforce `trace_id` is non-empty before commit.
2. Add a guardrail in `system_learning/runtime_adg/store.py` that rejects snapshots with empty or missing `trace_id`.
3. Back-fill `_trace_index.json` by inspecting snapshot payloads that DO contain a `trace_id` field even if the index didn't record it.

## 5. DEFERRED_SCOPE marker

DEFERRED_SCOPE: plan=NEW:runtime-adg-trace-binding-remediation wave=RT1 phase=RT1.1 layer=L4 fan_in=3 surface=Observability coverage_gap_pct=95.4 est_tokens=9000 reason=runtime ADG snapshots unbound from trace IDs
