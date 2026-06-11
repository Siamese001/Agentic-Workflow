---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\apps-agentic-core-coverage-audit-b4e5f1.md'
original_relative_path: 'apps-agentic-core-coverage-audit-b4e5f1.md'
source_sha256: d1a2d166a8d0b70fbe3e6263fada5f857fae901acf0db0386e10d058d173d99f
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps_* ↔ Agentic_Core Coverage Audit — 2026-04-26

Plan: `.windsurf/plans/apps-agentic-core-convergence-b4e5f1.md`
Method: **Direct SQLite query** of `artifacts/adg/adg_indexed_04252026_0843.sqlite` (346 MB). Joined `edges` (relation_type='imports') against `nodes.resolved_path` to count distinct source files per app per `agentic_core/<bucket>/`. Per constitutional §28 — SQLite-direct is the canonical fallback when MCP is unreachable or §25 serialization forbids a second MCP call. **Grep is FORBIDDEN for dependency analysis when SQLite snapshot is local.**
Snapshot: `adg_indexed_04252026_0843.sqlite` (2026-04-25, 346 MB). 155,484 import edges in graph.

## Methodology Note (corrects prior grep-based draft)

A prior version of this report used `grep_search` text matching. That violated constitutional §22, §23, §28. This version uses the canonical ADG `edges` table — same surface as `mcp1_adg_*`. Numbers below are ground truth. Every prior estimate that conflicted with these numbers is rejected.

## 1. Coverage Matrix (distinct source files per app importing each agentic_core bucket)

Counts = `COUNT(DISTINCT edges.source_file)` for `WHERE edges.relation_type='imports' AND edges.source_file LIKE '<app>/%' AND nodes.resolved_path LIKE 'agentic_core/<bucket>/%'`.

| `agentic_core` bucket | apps_eval | apps_exec | apps_lic | apps_research | apps_rfp | apps_rg | apps_shared | apps_underwriting_ai |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **L0_routing** (101 modules) | 4 | 2 | 4 | 1 | 1 | 7 | **26** | 0 |
| **L1_cognition** (147) | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 0 |
| **L2_execution** (231) | 1 | 1 | 2 | 3 | 1 | 8 | 4 | 0 |
| **L3_orchestration** (196) | 3 | 1 | 1 | 2 | 1 | 2 | 3 | 0 |
| **L4_state** (133) | 0 | 1 | 3 | 1 | 1 | 2 | 5 | 0 |
| **L5_safety** (429) | 2 | 1 | 1 | 1 | 1 | 2 | 3 | 1 |
| **L6_observability** (92) | **0** | **0** | **0** | 1 | **0** | **0** | 1 | **0** |
| **runtime** (72) | 2 | 26 | 40 | 19 | 2 | **111** | **108** | 1 |
| **base_agents** (13) | 0 | 0 | **5** | 0 | 0 | **0** | 6 | 0 |
| **mixins** (53) | 1 | 1 | 9 | 1 | 1 | 4 | 1 | 0 |
| **adg** (155) | 2 | 2 | 3 | 1 | 2 | 3 | 3 | 0 |
| **interfaces** (27) | 0 | 0 | 9 | 0 | 0 | 8 | 4 | 0 |
| **prompt_governance** (45) | 0 | 0 | 2 | 0 | 0 | 1 | 0 | 0 |
| **evaluation** (53) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **knowledge** (98) | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| **utils** (65) | 0 | 0 | 2 | 0 | 0 | 1 | 0 | 0 |
| **case_memory, embeddings, gateway, agents, cache, seams, tracing, visualization, cloud_native, core, config, L_CONTRACTS** (combined ~80) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## 1a. Roll-Ups

**Total `imports` edges from app → `agentic_core/*`** (signal of consumption depth):

| App | Import edges | Distinct source files | Total .py modules in app | Reach % |
|---|---:|---:|---:|---:|
| apps_underwriting_ai | **2** | **1** | 75 | **1.3%** |
| apps_rfp | 26 | 5 | 57 | 8.8% |
| apps_eval | 33 | 8 | 63 | 12.7% |
| apps_research | 266 | 22 | 56 | 39.3% |
| apps_lic | 2,335 | 42 | 97 | 43.3% |
| apps_exec | 532 | 27 | 60 | 45.0% |
| apps_shared | 5,818 | 117 | 171 | 68.4% |
| apps_rg | **6,931** | 115 | 166 | **69.3%** |

## 2. Five Critical Gaps

### G1 — `apps_underwriting_ai` is structurally orphaned (severity: **critical**)

UWAI imports `agentic_core` exactly **2 times** total (`L5_safety.enforcement` once, `runtime.entry` once). It does not consume:

- `runtime.contracts` (the contract surface every other app uses 1-218 times)
- `apps_shared.integrations.governed_app_runner.GovernedAppRunner` (the canonical L1→L0→C0→L2→L5+L6 spine)
- `SovereignBaseAgent`
- mixins
- ADG
- L6 observability

Any plan that says "wire substrate to all apps_*" is meaningless until UWAI is reconnected.

### G2 — `agentic_core/L6_observability/` is bypassed by parallel `apps_shared` substrate (severity: **critical**)

Canonical L6 surfaces in `agentic_core/L6_observability/`:

- `decision_events_schema.py` (canonical decision event schema)
- `decision_outcome_backfill.py`
- `decision_provenance.py`
- `regret_accounting.py`
- `flywheel_promoter.py`
- `judge_drift.py`
- `routing_calibration_metrics.py`
- `consensus_otel.py`
- `otel_runtime_ingest.py`
- `cascade_telemetry.py`
- `heal_router_otel.py`
- `promotion_gates.py`

Total app source files importing `L6_observability` (ADG SQLite ground truth): **2** distinct files across all 7 apps (1 in `apps_research`, 1 in `apps_shared`). `apps_rg` — which has 6,931 import edges into `agentic_core` — has **zero** imports of L6. `apps_lic`, `apps_eval`, `apps_exec`, `apps_rfp`, `apps_underwriting_ai` all have **zero** imports of L6.

Apps emit telemetry via the parallel `apps_shared` substrate instead:

| Canonical (`agentic_core`) | Parallel (`apps_shared`) |
|---|---|
| `agentic_core/mixins/tracing_mixin.py` | `apps_shared/mixins/apps_tracing_mixin.py` (uses `apps_shared.utils.open_telemetry_tracing_adapter_util` instead of L6 ingest) |
| `agentic_core/L6_observability/decision_events_schema.py` | `apps_shared/types/feedback_loop_types.py` (parallel feedback/event schema) |
| `agentic_core/L6_observability/regret_accounting.py` | `apps_shared/types/feedback_loop_orchestrator_types.py` |
| `agentic_core/L6_observability/cascade_telemetry.py` | `apps_*/_telemetry.py` per-app shims |

Per `adg-canonical-invariants.md` §3: STATE_NODE / Observability Surface antipattern — "parallel observability = silent inconsistency across runs". The original `apps-metrics-feedback-substrate-7c9e3d.md` plan would have entrenched this bypass.

### G3 — `L4_state` and UWG durable-write boundary are bypassed (severity: **high**)

- Total `L4_state.*` imports across all 7 apps: **9**.
- Apps write artifacts directly to repo-root and uncontrolled subdirs:
  - `reports/executive/exec_brief_*.md`
  - `reports/research/research_brief_*.md`
  - `rfp/proposal_*.md`
  - `eval/eval_*.{json,md,csv}`
  - `output_*.json` at repo root (10+ files)
- No app routes durable artifact writes through `agentic_core/L4_state/` or UWG.
- Per L5 doctrine (`docs/reference/00_L5_Policy_Plane/00.2_*.md` §G2 capability_sandbox; `00.5_*.md` §10 external_commit) and constitutional invariant "UWG is sole durable write path", every artifact written today bypasses governance.
- This is not a metrics problem; it is a state-plane problem. Metrics about ungoverned writes are second-order noise.

### G4 — Massive dead/duplicated `agentic_core` surface (severity: **high**)

| Submodule | Files | App imports | Verdict |
|---|---:|---:|---|
| `agentic_core/knowledge/` | 301 | 3 (only apps_rg) | Largely dead or unwired |
| `agentic_core/evaluation/` | 59 | 7 (only apps_eval) | Single-app capability |
| `agentic_core/prompt_governance/` | 132 | 3 | Largely dead or unwired |
| `agentic_core/case_memory/` | 4 | 0 | Dead from app perspective |
| `agentic_core/embeddings/` | 9 | 0 | Dead from app perspective |
| `agentic_core/gateway/` | 1 | 0 | Dead from app perspective |
| `agentic_core/agents/` | 5 | 0 | Dead from app perspective |
| `agentic_core/cache/` | 20 | 0 | Dead from app perspective |
| `agentic_core/seams/` | 7 | 0 | Dead from app perspective |
| `agentic_core/tracing/` | 1 | 0 | Dead from app perspective |
| `agentic_core/visualization/` | 1 | 0 | Dead from app perspective |
| `agentic_core/cloud_native/` | 1 | 0 | Dead from app perspective |
| `agentic_core/core/` | 2 | 0 | Dead from app perspective |

Each row is either a deletion candidate (governed by `agent-deletion-gate` for any `*Agent.py`) or unwired capability that should be carrying app load.

### G5 — `SovereignBaseAgent` skipped by 5/7 apps (severity: **high**)

Canonical agent base class: `agentic_core/base_agents/SovereignBaseAgent.py`.

| App | Imports | Status |
|---|---:|---|
| `apps_lic` | 5 | OK |
| `apps_shared` | 6 | OK (via base hierarchy) |
| `apps_eval` | 0 | Skips |
| `apps_exec` | 0 | Skips |
| `apps_research` | 0 | Skips |
| `apps_rfp` | 0 | Skips |
| `apps_rg` | 0 | Skips (despite 45 engines + multiple custom executor strategies) |
| `apps_underwriting_ai` | 0 | Skips |

Implications per L5 doctrine:

- `principal_chain` propagation absent
- `capability_token` binding absent
- `sandbox_envelope` binding absent
- `replay_envelope` binding absent
- side-effect class declaration absent
- governed dispatch boundary absent

This means the L5 capability/sandbox/replay infrastructure the doctrine assumes is **structurally absent** from those agents — not that it was added and bypassed, that it was never wired.

## 3. Pattern: Parallel Systems in `apps_shared`

| Canonical `agentic_core` surface | Parallel in `apps_shared` | Status |
|---|---|---|
| `agentic_core/mixins/tracing_mixin.py` | `apps_shared/mixins/apps_tracing_mixin.py` | Wraps with extra layer |
| `agentic_core/L6_observability/decision_events_schema.py` | `apps_shared/types/feedback_loop_types.py` | Duplicate event/feedback schema |
| `agentic_core/base_agents/SovereignBaseAgent` | `apps_shared/reasoning/Base*Agent.py` (5 base classes) | Parallel base hierarchy |
| `agentic_core/knowledge/retrieval` | `apps_shared/integrations/governed_app_runner._c0_retrieve` (custom inline) | Bespoke C0 retrieval |
| `agentic_core/L4_state` | direct disk writes to `reports/`, `eval/`, `output_*.json` | No L4/UWG path |
| `agentic_core/L5_safety/policy` (waivers, exemptions) | per-app `enforcement/*Strategy.py` | Per-app policy reinvention |

## 4. Conclusion

Five structural gaps must be resolved before any cross-cutting metrics/feedback work can be load-bearing. The original `apps-metrics-feedback-substrate-7c9e3d.md` plan was tactically reasonable but would have reinforced G2 (parallel observability) and ignored G1, G3, G4, G5.

The convergence program plan `.windsurf/plans/apps-agentic-core-convergence-b4e5f1.md` orders the work so each gap is resolved on canonical surfaces before metrics/feedback layer on top.

## 5. ADG Verification — completed via direct SQLite

This audit was redone using direct `sqlite3` queries against `artifacts/adg/adg_indexed_04252026_0843.sqlite` — the canonical ADG snapshot, same surface that `mcp1_adg_*` exposes. Per constitutional §28 (added 2026-04-26), this is the REQUIRED fallback when MCP is unavailable or §25 serialization forbids a second MCP call. Grep is FORBIDDEN for dependency analysis when SQLite is reachable.

Query shape:
```python
SELECT COUNT(DISTINCT e.source_file)
FROM edges e
JOIN nodes n ON n.id = e.dst_id
WHERE e.relation_type = 'imports'
  AND e.source_file LIKE '<app>/%'
  AND n.resolved_path LIKE 'agentic_core/<bucket>/%'
```

Convergence program W1.P0 will run additional `mv_graph_reverse_dependency_hotspots` and `mv_dependency_cone_risk` queries against the G4 deletion candidates — same SQLite snapshot, no new MCP calls required.

A prior version of this report used `grep_search` and produced different (lower) numbers. Those numbers are rejected as non-authoritative per constitutional §22 ("ADG wins conflicts: if graph facts disagree with text search / intuition, the graph is authoritative").
