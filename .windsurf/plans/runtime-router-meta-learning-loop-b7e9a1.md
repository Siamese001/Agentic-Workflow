# Runtime Router Meta-Learning Loop — Closure Plan

> **Plan ID**: `runtime-router-meta-learning-loop-b7e9a1`
> **Tier**: T3 (cross-layer, introduces infrastructure, crosses L0/L2/L3/L4/L5/L6)
> **Owner**: Cascade (drafting), USER (approval + execution sequencing)
> **Created**: 2026-04-24
> **Status**: DRAFT — awaiting approval before execution
> **Supersedes**: Extends ADR-050 (Intelligence Ledger Family) to runtime decisions

---

## Intent (Three Sentences)

The 10 existing ledgers (ADR-050) close the meta-learning loop for Cascade's harness-side decisions but leave all 9 runtime routers (L0 path, C0 retrieval, L3 step, L2 adapter, E4 healer, L5 HITL, UWG write-target, L6 judge, replan, promotion) with zero prediction→outcome binding. This plan extends the same ledger pattern (schema + CI gates + consulting skills + weekly calibrator) to each runtime router so every routing decision is captured with its prediction, bound to its actual outcome within a bounded time window, and fed back into the config-file policy that drives the router. The loop must be closed in a consistent, auditable, CI-enforced shape — not ad-hoc per router.

## Success Criteria (Plan-Wide)

| # | Exit condition | How measured |
|---|---|---|
| S1 | All 9 runtime routers emit decision events to a ledger with the canonical schema | `check_ledger_coverage.py` extended; each router has ≥1 ledger |
| S2 | Each ledger has an outcome binder that fills `outcome_json` + `bound_at` within a router-specific SLA | `check_ledger_freshness.py` extended; bound rate ≥70% within SLA |
| S3 | Each ledger has a calibration script that fills `calibrated_at` + `score_numeric` | Weekly report shows calibrated rows grow > unbound rows |
| S4 | Each router has a config-file policy that a threshold updater can rewrite | Threshold updater has write path; CI dry-run green |
| S5 | Each router has a `ledger-consulter-<router>` skill that reads precedent before decision | Skill invocation logged in L6 spans |
| S6 | Router thresholds measurably improve (false-fire rate, override rate, or success rate) after ≥2 calibration cycles | Weekly report delta trend |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | P0.1, P0.2, P0.3 | Foundation: shared writer/binder/calibrator library | 45k | ADR-050 ledger schema is the correct reusable shape | Todo | Library passes unit tests; 1 reference router integrated |
| W1 | P1.1, P1.2, P1.3 | Quick wins — routers with existing partial emission or clear outcome signals | 55k | Healer already emits OTel; promotion/judge have observable outcomes | Todo | 3 routers writing + binding + calibrating |
| W2 | P2.1, P2.2, P2.3 | L2 resource routers: adapter, L3 step, C0 retrieval | 65k | Each has a single execution chokepoint to wrap | Todo | 3 more routers wired |
| W3 | P3.1, P3.2, P3.3, P3.4 | Structural + disposition routers: L0 path, L5 HITL, UWG target, replan | 80k | L0 routing contracts already exist; UWG has enforcement plane | Todo | 4 remaining routers wired |
| W4 | P4.1, P4.2, P4.3, P4.4 | Close the loop: per-router calibrators + threshold writer + consulting skills + dashboard | 60k | `ledger_weekly_report.py` pattern is extensible | Todo | Full loop operating for all 9 |
| W5 | P5.1, P5.2, P5.3 | Verification + governance: e2e test, CI gates, ADR | 30k | Integration harness exists | Todo | ADR merged, gates green, 1 full cycle run |

**Token budget total**: ~335k sizing heuristic (self-reported by Cascade based on scope). Token-estimator tooling retired 2026-04-24 — 1M context window removes need for budget gates.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| **P0.0** | ADG hotspot query — verify wave ordering against fan-in / impact | `adg_edge_fanin` per router hotspot + materialized-view consult | Must justify W1 sequencing with real ADG data | 3k | Todo |
| **P0.1** | Shared `RouterLedgerWriter` library | `agentic_core/L6_observability/router_ledger/writer.py` + test | Must not bloat per-router wiring | 15k | Todo |
| **P0.2** | Shared `OutcomeBinder` library + binder SLA contract | `agentic_core/L6_observability/router_ledger/binder.py` + test | Outcome sources differ per router — contract must be abstract | 18k | Todo |
| **P0.3** | Wire `routing_decision_events` table into ADG build (finally ship Wave F2 M3) | `tools/generate_full_adg.py`, reuse existing `routing_decision_events_schema.py` | Schema file already exists; only need caller wiring | 12k | Todo |
| **P1.1** | **Heal router** — outcome binding (retry success / recurrence within 5-min window) | `agentic_core/L2_execution/healers/healing_router.py`, new ledger `heal_router.sqlite` | Already emits spans; add binder + calibrator | 18k | Todo |
| **P1.2** | **Promotion router** — outcome binding (canary regression rate / rollback) | `agentic_core/L4_state/enforcement/promotion_authority.py`, new ledger `promotion.sqlite` | Canary regression is the outcome; binder waits for canary window | 20k | Todo |
| **P1.3** | **Judge router** — outcome binding (human-calibration disagreement rate per judge) | `agentic_core/evaluation/judges/llm_judges.py`, new ledger `judge_selection.sqlite` | Reuses existing judge-calibration cadence (`judge-calibration-cadence.md`) | 17k | Todo |
| **P2.1** | **L2 Adapter router** — capture + bind to adapter invocation outcome (success/latency/retry) | `agentic_core/L2_execution/enforcement/_adapter_registry.py`, new ledger `adapter_selection.sqlite` | Single registry = single chokepoint; easy wrap | 20k | Todo |
| **P2.2** | **L3 Step/Shape router** — capture + bind to step completion (success rate, latency vs predicted) | `agentic_core/L3_orchestration/reasoning/engines/manager_routing.py`, new ledger `l3_step_shape.sqlite` | Parallel vs serial shape is the prediction; step latency is the outcome | 22k | Todo |
| **P2.3** | **C0 Retrieval router** — capture + bind to retrieval quality (groundedness, citation precision) | `agentic_core/L4_state/utils/retrieval/context_retrieval_orchestrator.py`, `infrastructure/reasoning/unified_query_router.py`, new ledger `c0_retrieval.sqlite` | Outcome signal = exit-eval groundedness score (already computed at [5]) | 23k | Todo |
| **P3.1** | **L0 Path router** — capture R1A/R1B/R3/R4/R5 + bind to exit-eval verdict | `agentic_core/L0_routing/reasoning/path_router.py`, `agentic_core/L0_routing/reasoning/agentic_router.py`, new ledger `l0_path.sqlite` | Outcome = did chosen path produce pass/fail/unknown at exit | 25k | Todo |
| **P3.2** | **L5 HITL Approver router** — capture + bind to approver decision (approve/reject/timeout, time-to-decision) | `agentic_core/L5_safety/enforcement/hitl/hitl_escalation_activator.py`, new ledger `hitl_approver.sqlite` | Outcome latency can be hours; binder needs long-poll pattern | 20k | Todo |
| **P3.3** | **UWG Write-Target router** — capture + bind to commit outcome (success/retry/replication lag) | `agentic_core/L4_state/enforcement/promotion_write_gateway.py`, `agentic_core/interfaces/write_gateway.py`, new ledger `uwg_target.sqlite` | Multi-store routing inside UWG; outcome is commit ack | 18k | Todo |
| **P3.4** | **Replan router** — capture replan-vs-abstain-vs-escalate + bind to successor plan success | `agentic_core/runtime/contracts/replan_contract.py`, exit gate, new ledger `replan.sqlite` | Outcome = did successor plan pass exit eval? | 17k | Todo |
| **P4.1** | Per-router calibration scripts (9 files) following `ledger_weekly_report.py` shape | `ops_scripts/calibration/calibrate_<router>.py` × 9 | Must produce calibrated_at + score_numeric for each row | 20k | Todo |
| **P4.2** | Threshold writer — generic tool that takes a calibration report and proposes config rewrites | `tools/routing/threshold_updater.py` | Must NOT auto-write without Author-Gate; proposes diffs only | 15k | Todo |
| **P4.3** | 9 new `ledger-consulter-<router>` skills following `.windsurf/skills/ledger-consulter/` template | `.windsurf/skills/ledger-consulter-<router>/SKILL.md` × 9 | Each router's decision point invokes its consulter | 12k | Todo |
| **P4.4** | Routing-health dashboard + freshness alerts | `tools/routing/health_dashboard.py`, Notion MCP Registry row update | Reuses freshness-report JSON shape | 13k | Todo |
| **P5.1** | End-to-end verification: run full loop for heal router (exemplar) across one real session | Test harness + ledger inspection | Prove prediction→outcome→calibration→threshold-update works once | 10k | Todo |
| **P5.2** | Extend CI gates: `check_ledger_coverage.py`, `check_ledger_freshness.py`, `check_ledger_writer_contract.py` to cover 9 new ledgers | Existing gate files + tests | Ledgers must stay fresh; writer contract enforced | 10k | Todo |
| **P5.3** | **ADR-NNN: Runtime Router Meta-Learning Loop** — formalize the pattern | `docs/architecture/adr/ADR-NNN-runtime-router-meta-learning.md`, Notion ADR Registry post | ADR codifies the writer/binder/calibrator contract so future routers are born uniform | 10k | Todo |

---

## Gap Register (What's Missing Today vs What This Plan Builds)

| Gap (proven in prior turn) | Closing Phase |
|---|:-:|
| 8 of 9 runtime routers emit nothing | P1.1, P1.2, P1.3, P2.1–P2.3, P3.1–P3.4 |
| `calibrated_at IS NULL` on all 30 existing rows | P4.1 |
| `routing_decision_events` table never created on disk | P0.3 |
| No threshold-update mechanism | P4.2 |
| No consulting skill for runtime routers | P4.3 |
| No e2e proof any loop closes | P5.1 |
| No ADR formalizing the pattern | P5.3 |

---

## Router-by-Router Prediction & Outcome Design

This table is the contract — it is what P1.*, P2.*, P3.* each implement concretely. The outcome column is the hardest part of each phase; it dictates the binder SLA.

| # | Router | Prediction captured | Outcome bound | Outcome source | Bind SLA | Feedback target (config file) |
|---|---|---|---|---|:-:|---|
| 1 | **L0 Path** | Chosen R1A/R1B/R3/R4/R3-R4-mgd/R5 + confidence | Exit-eval verdict {pass/warn/fail} + path-replay flag | Exit gate [5] `ExitDecision` | run+5s | `config/routing_thresholds.yaml` |
| 2 | **C0 Retrieval** | Index set chosen (vector/BM25/graph/hybrid) + k | Groundedness + citation precision | Exit gate final-response metrics | run+5s | `config/retrieval_policy.yaml` (to be created) |
| 3 | **L3 Step/Shape** | Serial vs parallel vs map-reduce + fan-out width | Step completion rate + latency ratio (actual/predicted) | L2 E5 sealed artifacts | step+timeout | `config/l3_shape_policy.yaml` (to be created) |
| 4 | **L2 Adapter** | Adapter class chosen for capability | Adapter invocation {success/timeout/error} + latency | L2 E5 seal | step+timeout | `config/capability_adapters.yaml` (to be created) |
| 5 | **E4 Healer** | Heal tier + target model + gate | Repair {success/fail} + recurrence within 5-min window | Subsequent step outcome | step+5min | Existing `config/healer_strategies.yaml` |
| 6 | **L5 HITL** | Approver bucket chosen + escalation class | Approver {approve/reject/timeout/override} + time-to-decision | HITL decision ledger | HITL window (≤24h) | `config/hitl_approvers.yaml` (to be created) |
| 7 | **UWG Target** | Chosen L4 store + shard | Commit {ack/retry/replication-fail} + consistency verify | L4 commit receipt | commit+30s | `config/write_targets.yaml` (to be created) |
| 8 | **L6 Judge** | Judge class selected for rubric/trace | Human-calibration disagreement for that judge-rubric pair | Judge calibration cadence | weekly | Existing `config/judges/rubrics.yaml` |
| 9 | **Replan** | Replan-vs-abstain-vs-BEST-EFFORT choice | Successor plan verdict from exit gate | Exit gate [5] of successor run | successor+5s | `config/replan_policy.yaml` (to be created) |
| — | **Promotion** (bonus, not in original 9 but listed prior turn) | Shadow→canary→canonical gate decision | Canary regression rate + rollback flag | Canary window monitor | canary window (≥24h) | `config/promotion_gates.yaml` |

---

## Shared Infrastructure Design (W0)

### Contract 1 — `RouterLedgerWriter` (P0.1)

```python
class RouterLedgerWriter:
    """Canonical writer for runtime router decisions.
    
    Mirrors ADR-050 schema. One writer instance per ledger file.
    Writes are fire-and-forget best-effort; failures MUST NOT break routing.
    """
    def record_decision(
        self,
        *,
        event_kind: str,           # e.g. "l0_path_decision"
        prediction: dict,          # JSON-serializable prediction payload
        metadata: dict | None = None,
        session_id: str | None = None,
        scope: list[dict] | None = None,  # file/symbol/layer scope
    ) -> str:                      # returns event_id (ULID)
        ...
```

All 9 router phases use this single writer. No per-router writer code.

### Contract 2 — `OutcomeBinder` (P0.2)

```python
class OutcomeBinder:
    """Binds observed outcome to a prior prediction within SLA.
    
    Each router provides an outcome source (callable) + bind key.
    Binder runs as background task; idempotent.
    """
    def bind(
        self,
        *,
        event_id: str,
        outcome: dict,             # JSON-serializable outcome payload
        score_band: str | None,    # "hit" | "partial" | "miss" | "unknown"
        latency_ms: int,
    ) -> None:
        ...
```

Three binder patterns:
- **Sync bind** (L0, C0, L2, E4, L3): bind within same run at exit gate
- **Near-sync bind** (UWG, Replan): bind on commit-ack or successor run
- **Async long-poll bind** (HITL, Promotion, Judge): bind when external signal arrives; binder is a cron/periodic job

### Contract 3 — `RouterCalibrator` (P4.1)

```python
class RouterCalibrator:
    """Computes score_numeric + calibrated_at from bound prediction/outcome pairs.
    
    One calibrator per router. Weekly cron. Emits a calibration report
    (JSON) consumed by the threshold updater (P4.2).
    """
    def calibrate_window(
        self,
        *,
        ledger_path: Path,
        window_start: datetime,
        window_end: datetime,
    ) -> CalibrationReport:
        ...
```

### Contract 4 — `ThresholdUpdater` (P4.2)

Reads CalibrationReport → proposes diff to router's config YAML → **never auto-applies**. Surfaces via Author-Gate for the user to accept/reject. Writes a `promotion_packet` to the Author-Gate Decision Ledger.

---

## Why Reuse ADR-050 Schema (Not a New One)

The existing `events` table shape is:
- `prediction_json` + `outcome_json` + `bound_at` + `calibrated_at` + `score_band` + `score_numeric`
- `event_kind` is the discriminator — "l0_path_decision" vs "tool_routing_decision" vs "heal_route_decision" etc.

Using one schema across harness AND runtime routers gives:
1. One set of CI gates (coverage/freshness/writer-contract)
2. One weekly report shape
3. One consulting-skill template
4. One mental model for future routers
5. Zero schema migration cost when runtime routers need the same calibration tooling ADR-050 built

The alternative (new schema per runtime router) duplicates infrastructure and forks the audit surface. Rejected.

---

## Non-Goals (Bounded Scope)

- **Not building new observability plane** — uses existing OTel + SQLite + ADR-050 ledger infra
- **Not auto-applying threshold changes** — threshold updater proposes; user approves via Author-Gate
- **Not replacing existing routers** — only adds capture + binding layers around them
- **Not touching L6 Shadow Evaluation** — that loop already exists (see `evaluation-promotion-gate.md`); this plan ONLY adds runtime-router learning
- **Not building cross-router learning** — each router calibrates against its own outcome signal. Cross-router optimization is deferred (NEXT_STEP, not this plan)

---

## Dependencies & Ordering Rules

1. **W0 MUST complete before W1** — shared library is prerequisite
2. **W1, W2, W3 are partition-parallel** — each router phase is independent after W0
3. **W4 depends on at least 1 router from W1/W2/W3 being fully wired** — P4.1 calibrator needs real ledger rows to calibrate against
4. **W5 is terminal** — depends on W4

---

## Risk Register

| Risk | Mitigation |
|---|---|
| Binder SLA misses → `bound_at IS NULL` piles up (same failure as today's 10 ledgers) | P5.2 CI gate `check_ledger_binding_rate.py` fails CI if bind rate <70% over 7-day window |
| Per-router calibrator logic drifts | Shared `RouterCalibrator` base class with router-specific `score_band_fn` only |
| Threshold updater auto-applies and destabilizes routing | Hard constraint: UPDATER NEVER WRITES. Produces Author-Gate packet only. Codified in ADR P5.3. |
| Ledger volume grows unbounded | Sharded by month; retention = 90 days calibrated / 30 days unbound (same as ADR-050) |
| Router emission adds hot-path latency | Writer is fire-and-forget via daemon thread (same pattern as `DeferredLoader` v3 — precedent in memory) |
| HITL / Promotion bind takes hours-to-days | Long-poll binder runs as cron; tests use time-compressed fixtures |

---

## ADG_GRAPH_LAYER_EVIDENCE

> Per constitutional §22, T3 plans must cite ADG graph-layer primitives driving scope. This is a **feature-addition** plan, not a refactoring plan, but the structural touch-points are still ADG-observable.

Materialized views and semantic edges consulted (to be verified in W0 P0.0):
- `mv_hotspot_centrality` — to confirm which routers are central (high fan-in) and therefore priority for W1 (healer router has high fan-in — matches W1.P1.1 sequencing)
- `mv_graph_reverse_dependency_hotspots` — confirms `healing_router.py` has many callers (justifies P1.1 priority)
- `mv_exemptions_near_critical_paths` — ensures no new anti-pattern exemptions are introduced by writer wiring
- Semantic edge `emits_side_effect` — every new writer call site emits a side effect; ADG will track via Wave F2 M3 wiring (P0.3)
- P-view `v_p0_write_bypass_uwg` — UWG router phase (P3.3) MUST NOT introduce a bypass; cross-reference at phase gate

## ADG_HOTSPOT_REPORT

| Hotspot | Layer | Fan-in | Archetype | Surface | Impact | Phase |
|---|:-:|:-:|---|---|:-:|:-:|
| `healing_router.py` | L2 | (ADG query pending W0.P0.0) | ORCHESTRATOR | Execution | HIGH | P1.1 |
| `path_router.py` | L0 | (ADG query pending) | CENTRAL_DEPENDENCY | Execution | HIGH | P3.1 |
| `promotion_write_gateway.py` | L4 | (ADG query pending) | STATE_NODE | Write | HIGH | P3.3 |
| `context_retrieval_orchestrator.py` | L4 | (ADG query pending) | CENTRAL_DEPENDENCY | State | MED | P2.3 |
| `llm_judges.py` | evaluation | (ADG query pending) | SAFETY_GATEKEEPER | Observability | MED | P1.3 |
| `hitl_escalation_activator.py` | L5 | (ADG query pending) | SAFETY_GATEKEEPER | Security | HIGH | P3.2 |

**W0.P0.0 blocks W1** — the ADG queries above must populate before execution to validate the impact ordering. (ADG verification step, not token estimation — that tooling was retired 2026-04-24.)

---

## Verification Plan (W5)

P5.1 demonstrates the full loop for the healer router:
1. Trigger a known-failing step → heal router picks a tier → records prediction to ledger
2. Healer attempts repair → records outcome via binder → `bound_at` fills within 5 min
3. Run calibrator manually → `calibrated_at` fills + score_numeric computed
4. Run threshold updater → produces proposed-diff packet (but does NOT write)
5. Inspect ledger: 1 row fully closed end-to-end

Evidence bundle: `docs/reports/plans/runtime-router-meta-learning-loop-b7e9a1/evidence-w5-p5-1.md` with SQL dumps.

---

## Rollback Strategy

Each router phase is independently reversible:
1. Writer calls are wrapped in `try/except` — disabling the writer disables emission cleanly
2. Ledger files can be dropped without production impact (router still functions)
3. Feature flag `ROUTER_META_LEARNING_ENABLED=0` globally disables all binder/calibrator crons

Per-phase rollback = revert the writer wiring commit; ledger data preserved for forensics.

---

## Deferred Scope (not this plan)

- Cross-router correlation (e.g., "when L0 picks R3 and C0 picks hybrid, groundedness drops 10%") — separate follow-up
- RL-based auto-threshold tuning — out of scope; this plan intentionally keeps human-in-the-loop via Author-Gate
- Runtime-ADG (otel_mcp) integration with this ledger — deferred; this plan uses SQLite ledgers only
- Per-tenant routing calibration — all routing assumes single-tenant today

---

## Execution Gate

**BEFORE starting W1**, the user must:
1. Approve this plan shape ✅ (2026-04-24)
2. Confirm the 9 config-file destinations (5 new YAMLs listed in Router-by-Router table) ✅ (2026-04-24)
3. Accept that W0 P0.0 is blocking ADG hotspot verification ✅ (2026-04-24 — user approved and retired the token-estimator requirement)

**APPROVED 2026-04-24. Execution may proceed starting at W0.P0.0.**

---

## Change Log

| Date | Change | Author |
|---|---|---|
| 2026-04-24 | Initial draft | Cascade (on user request) |
