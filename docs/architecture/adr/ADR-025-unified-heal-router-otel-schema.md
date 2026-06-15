# ADR-025 — Unified `heal_router.v1` OTEL Schema

**Status:** ACCEPTED (implemented; residual projection work may remain)
**Date:** 2026-04-21
**Accepted:** 2026-06-15 status reconciliation
**Deciders:** Routing-unification plan owner; apps_* orchestrator owners
**Impact layers:** L2 (healers), L3 (qwen_vllm), L4 (state), L6 (observability)
**Supersedes:** N/A — additive
**Relates to:** ADR-019 (ADG materialized views); Wave F2 of `routing-followups-7a2c91.md`

> **Implementation evidence (2026-06-15):** `agentic_core/L6_observability/heal_router_otel.py`,
> `agentic_core/L6_observability/runtime_trace/heal_router_otel.py`, and the
> `test_heal_router_otel*` unit tests exist. This ADR is no longer merely
> proposed; any remaining work should be tracked as implementation follow-up.

---

## 1. Context

Wave 1–6 of `routing-unification-qwen-abe735.md` unified routing decision logic
in `HealingRouter` with the `RoutingDecision` dataclass (gate_applied,
gemini_subtier, cost_demoted, target_model). However, telemetry remains
fragmented across **four** incompatible schemas:

| # | File | Surface | Shape | Emits |
|---|------|---------|-------|-------|
| 1 | `@c:\Git\Agentic-Workflow\agentic_core\L3_orchestration\inference\qwen_vllm\telemetry.py` (99 lines) | `QwenInferenceTelemetry` | Session-based: `QwenInferenceMetric(timestamp, app_name, model_id, metric_name, value)` + `QwenSessionMetrics` | Runtime per-request metrics |
| 2 | `@c:\Git\Agentic-Workflow\agentic_core\L3_orchestration\inference\qwen_vllm\config\qwen_telemetry.py` | Qwen config-side telemetry | Config validation events | Startup-time |
| 3 | `@c:\Git\Agentic-Workflow\agentic_core\L2_execution\healers\heal_classifier_model.py` (119 lines) | `HealClassifierTelemetry` | Classifier events (recommended_tier, heal_confidence, outcome_success) | ML shadow-mode |
| 4 | `@c:\Git\Agentic-Workflow\agentic_core\L4_state\config\vllm_routing_predicates.py` (130 lines) | `_emit_applies_guardrail`, `_emit_records_execution_trace`, `_emit_snapshots_state` | Runtime contract lifecycle | Routing invariant enforcement |

### Problems

1. **No unified routing-decision span** — a single `HealingRouter.route()`
   call produces 0–N events in 4 different schemas with no shared trace_id
2. **W6 calibration tool** reads JSONL (HealClassifierTelemetry subset) and
   cannot cross-reference runtime metrics from schema #1
3. **W6 P6.2 cost_demoted field** has no canonical OTEL attribute home
4. **ADG materialized views** (RCA H9) cannot be built — no canonical
   `routing_decision_events` table to aggregate
5. **apps_* orchestrators** each emit their own spans inconsistently,
   making cross-app routing comparison impossible

---

## 2. Decision

Introduce a single unified OTEL span hierarchy `heal_router.v1` that every
routing decision flows through. The existing 4 schemas remain as
**feeders** (not sources of truth) during a 30-day compat window, then
become aliases.

### Span Hierarchy

```
heal_router.v1.route                         [root — one per HealingRouter.route() call]
├── heal_router.v1.score                     [confidence scoring]
├── heal_router.v1.gate                      [gate evaluation; 0-N children: gate_0, gate_1, ...]
├── heal_router.v1.subtier_selection         [Flash/Pro selection, W5]
├── heal_router.v1.cost_demotion             [W6 P6.2 — only if context.cost_budget_remaining_usd was provided]
└── heal_router.v1.dispatch                  [dispatch_to_executor]
    ├── heal_router.v1.dispatch.deterministic   [HIGH tier]
    ├── heal_router.v1.dispatch.qwen            [MEDIUM tier]
    ├── heal_router.v1.dispatch.gemini_flash    [LOW tier, Flash]
    ├── heal_router.v1.dispatch.gemini_pro      [LOW tier, Pro]
    └── heal_router.v1.dispatch.hitl            [HITL tier]
```

### Required Attributes (all spans)

| Attribute | Type | Source | Example |
|---|---|---|---|
| `routing.trace_id` | string (uuid4) | generated at `route()` entry | `3f5a…` |
| `routing.tier` | string | `RoutingDecision.tier.name` | `LOW` |
| `routing.gate_applied` | string | `RoutingDecision.gate_applied` | `GATE_1_RETRY_OVERRIDE` |
| `routing.gemini_subtier` | string | `RoutingDecision.gemini_subtier` | `FLASH` |
| `routing.cost_demoted` | bool | `RoutingDecision.cost_demoted` | `false` |
| `routing.target_model` | string | `RoutingDecision.target_model` | `gemini-2.0-flash-001` |
| `routing.app_name` | string | dispatch-time `app_name` | `healing_router` |
| `routing.confidence_score` | float | `ConfidenceScore.score` | `0.42` |

### Optional Attributes (dispatch spans only)

| Attribute | Applies when | Purpose |
|---|---|---|
| `routing.cost_usd` | dispatch succeeded and provider cost known | W6 cost tracking |
| `routing.tokens_in` / `routing.tokens_out` | dispatch succeeded | throughput analysis |
| `routing.latency_ms` | always | performance tracking |
| `routing.error_code` | dispatch failed | failure classification |
| `routing.dry_plan` | `true` when gateway absent (W5 P5.2) | distinguishes mock from real |

---

## 3. Canonical Event Table

To feed materialized views (RCA H9 / F2.3), a relational projection:

```sql
CREATE TABLE routing_decision_events (
  routing_trace_id        TEXT PRIMARY KEY,
  timestamp               TIMESTAMP NOT NULL,
  app_name                TEXT NOT NULL,
  tier                    TEXT NOT NULL,       -- HIGH | MEDIUM | LOW | HITL
  gate_applied            TEXT NOT NULL,
  gemini_subtier          TEXT,                -- NULL unless tier=LOW
  cost_demoted            BOOLEAN NOT NULL DEFAULT FALSE,
  target_model            TEXT NOT NULL,
  confidence_score        REAL,
  cost_usd                REAL,
  cost_budget_remaining_usd REAL,
  latency_ms              INTEGER,
  outcome_success         BOOLEAN,
  dry_plan                BOOLEAN NOT NULL DEFAULT FALSE,
  error_code              TEXT
);

CREATE INDEX idx_routing_timestamp ON routing_decision_events(timestamp);
CREATE INDEX idx_routing_app_tier ON routing_decision_events(app_name, tier);
CREATE INDEX idx_routing_gate ON routing_decision_events(gate_applied);
```

Materialized views from RCA H9 then build on this table.

---

## 4. Migration Path (30-day compat window)

**Phase M1 (week 1):** Add unified emitter to `HealingRouter`
- New module: `agentic_core/L6_observability/heal_router_otel.py`
- Class: `HealRouterTelemetryEmitter` with `emit_route_span(decision)` method
- Called from `HealingRouter.route()` last statement before return
- Existing 4 schemas continue emitting unchanged (no consumer impact)

**Phase M2 (weeks 2–3):** Alias existing schemas
- `QwenInferenceTelemetry.record_inference_metric()` internally also emits
  a `heal_router.v1.dispatch.qwen` span
- `HealClassifierTelemetry.record_classification()` aliases to
  `heal_router.v1.score` span
- `vllm_routing_predicates._emit_*` wrap with `heal_router.v1` child spans
- No behavior change for existing callers

**Phase M3 (week 4):** Switch MV data source
- ADG generator ingests from `routing_decision_events` (fed by unified spans)
- F2.3 materialized views come online
- W6 `calibrate_thresholds.py` migrates from JSONL → MV query

**Phase M4 (post-30-days):** Deprecate non-unified emission paths
- Mark non-unified emitters with `DeprecationWarning`
- Consumer migration window begins

---

## 5. Consequences

### Positive

- Single `routing_trace_id` links every event across all 4 schemas
- W6 cost tracking + P6.2 demotion become first-class OTEL attributes
- RCA H9 materialized views become implementable
- apps_* orchestrators gain a standard routing-span attribute set

### Negative

- 4-week compat window is disciplined but real overhead
- New module `heal_router_otel.py` adds L6 surface area
- Backward-compat during M1–M3 means dual-emission (2× span volume temporarily)

### Risks

| Risk | Mitigation |
|---|---|
| OTEL span volume explosion | Attribute sampling (1:10 for child spans); keep root span always-on |
| `routing_trace_id` collision | uuid4 (2^122 space) — collision probability negligible |
| Schema drift in existing emitters during M1–M3 | Alias mapping captured in unit tests; CI gate forbids new fields without ADR update |
| apps_* orchestrator breakage | M1 is purely additive; no consumer code changes required until M4 |

---

## 6. Alternatives Considered

### Alt 1: Collapse 4 schemas immediately

Rejected. High consumer impact; violates the 30-day compat window discipline
from parent plan §8 rollback checkpoints.

### Alt 2: Leave all 4 schemas, add routing_trace_id as an extra attribute everywhere

Rejected. Preserves drift; does not solve the MV-blocker (RCA H9).

### Alt 3: Use Prometheus metrics instead of OTEL spans

Rejected. Prometheus is pull-based metric-only; cannot represent the
parent-child span relationship that routing decisions need for causality
tracking.

---

## 7. Implementation Checkpoints

| Checkpoint | Plan phase | Success criterion |
|---|---|---|
| `heal_router_otel.py` module exists with `HealRouterTelemetryEmitter` | F2.3 | Unit tests pass; no consumer impact |
| `HealingRouter.route()` emits `heal_router.v1.route` span | F2.3 | 124-test baseline green |
| `routing_decision_events` table populated | F2.3 | ADG snapshot contains table |
| MVs from RCA H9 are queryable | F2.3 + F3.6 verification | `adg_sqlite.adg_violations` returns routing-specific rows |

---

## 8. Non-Goals

- Not replacing the W6 `tools/routing/calibrate_thresholds.py` JSONL reader
  in this ADR — that migration is M3
- Not forcing apps_* orchestrators to adopt `heal_router.v1` spans in their
  own call sites — they consume routing spans but don't have to emit them
- Not changing `SovereignLLMGateway` interface — routing-span emission
  wraps the gateway, doesn't replace it

---

## 9. References

- Parent plan: `.windsurf/plans/routing-followups-7a2c91.md` F2.2
- RCA H9: `docs/reports/plans/rca-h9-mv-routing-materialized-views.md`
- Constitutional §22 (ADG graph layer primary)
- ADR-019 (ADG materialized views — predecessor pattern)
