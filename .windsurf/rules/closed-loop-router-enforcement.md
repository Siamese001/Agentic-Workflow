---
trigger: always_on
---

> **Cascade always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Cascade enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

# Closed-Loop Router Enforcement — 10-Layer Verification

> ⛔ **Every routing, promotion, calibration, or feedback decision in the 10-layer
> matrix (L0-bandit … L6-regret) MUST emit a structured `ROUTER_DECISION:` event
> bound to a per-router ledger.** Silent emission, missing fields, or promotion
> without calibration evidence is a constitutional violation (§28).

This rule mirrors the Author-Gate enforcement stack but applies to the
**production agent runtime** — not Cascade's authoring loop. See ADR-050
(intelligence ledger family) for the parent pattern.

## Why this exists

Closed-loop verification depends on each router emitting prediction +
outcome telemetry on every decision, persistently, with full provenance.
Without enforcement:

- Provider/model/tool/connector substitutions go silent (constitutional §23)
- Promotions fire without Wilson + z + uplift evidence
- Rollbacks fire without regret accounting
- Calibration drifts unnoticed across waves
- Cross-router feedback (router → meta-learner → next-decision) breaks

## The 10-Router Matrix (SSOT)

| # | Layer | Router | Persistent rows | Eval gate output | Meta-learner update | Router feedback |
|---|---|---|---:|---|---|---|
| 1 | L0 | `bandit` | 480 | Thompson 5000× | α/β replay | per-NS route winner |
| 2 | L0 | `r5` | 240 | Brier per reason | demote toxicity_flagged | trigger set shrunk |
| 3 | L1 | `c0` | in-mem | mode/k/coverage | bandit posterior | hybrid + k=3 + 0.80 |
| 4 | L2 | `cascade` | in-mem | EU + Brier + fingerprint | demote 3 providers | cascade tier excludes |
| 5 | L3 | `shape` | 60×3 | p95 + amplitude + skip | per-class max_iter | iter caps 3/7/5 |
| 6 | L3 | `reroute` | in-mem | ceiling + disagree + cert | alarm fired | block d2,d4 |
| 7 | L4 | `uwg` | in-mem | class + miss + atomic | 2nd-judge gate | 2/4 fire |
| 8 | L5 | `hitl` | 50 + 4 probes | FP rate + escape rate | per-reason FP | demote pii_leak |
| 9 | L6 | `promo` | in-mem | Wilson + z + uplift | promote/rollback verdict | promote_bus signal |
| 10 | L6 | `regret` | in-mem | per-dec + by-layer | top offender | next-cycle priority |

The `(layer, router)` tuple is the **routing key** for ledger writes and
calibration reports. Each tuple has its own ledger
(`artifacts/ledgers/router_<layer>_<router>.sqlite` once W2 lands) and its own
weekly calibration report.

## The ROUTER_DECISION marker contract

Every router emission MUST conform to this plain-text grammar (logged to OTEL,
stdout, or its host's structured log channel):

```
ROUTER_DECISION: layer=<L0..L6> router=<name> decision_id=<uuid> trace_id=<id> route_id=<id> selected=<arm_or_verdict> [field=value ...]
```

**Required fields** (every router):

| Field | Type | Meaning |
|---|---|---|
| `layer` | `L0` … `L6` | Architectural layer |
| `router` | identifier | One of the 10 router names from the matrix |
| `decision_id` | uuid4 | Unique per-decision id |
| `trace_id` | string | Spans the run; ties to OTEL trace |
| `route_id` | string | Logical route this decision serves |
| `selected` | string | The chosen arm / verdict / target |

**Per-router required fields** (in addition to common):

| Router | Required additional fields |
|---|---|
| `L0/bandit` | `ns`, `posterior_alpha`, `posterior_beta` |
| `L0/r5` | `reason_code`, `brier_score` |
| `L1/c0` | `mode`, `k`, `coverage_score` |
| `L2/cascade` | `tier`, `provider`, `eu_score`, `brier_score` |
| `L3/shape` | `class`, `iter_count`, `p95_latency_ms`, `amplitude` |
| `L3/reroute` | `ceiling_band`, `disagree_count`, `cert_status` |
| `L4/uwg` | `class`, `miss_count`, `atomic` |
| `L5/hitl` | `reason_code`, `fp_rate`, `escape_rate` |
| `L6/promo` | `verdict` (`promote`/`rollback`), `wilson_lower`, `z_score`, `uplift`, `n` |
| `L6/regret` | `top_offender`, `regret_value`, `by_layer_json` |

**Placement rules**: plain text only; one per line; emitted at decision time
(not buffered across decisions); `decision_id` is canonical and used for
later outcome binding.

## The Library-Call Invariant

Routers MUST also write to their ledger via
`tools.ledgers.hook_helpers.emit_ledger_event` in the **same call path** that
emits the marker. The marker is the audit trail; the library call is the
durable record. They MUST not diverge.

Pattern:

```python
from tools.ledgers.hook_helpers import emit_ledger_event

def decide(...):
    decision_id = uuid.uuid4().hex
    selected = pick_arm(...)
    # 1. Durable record
    emit_ledger_event(
        ledger="router_l0_bandit",     # registered name
        event_kind="route_decision",
        prediction={"selected": selected, "posterior": ...},
        repo_area="agentic_core/L0_routing/bandit.py",
    )
    # 2. Audit trail (OTEL or stdout)
    log.info(f"ROUTER_DECISION: layer=L0 router=bandit decision_id={decision_id} "
             f"trace_id={trace_id} route_id={route_id} selected={selected} ...")
    return selected
```

Direct `sqlite3.connect()` calls bypass fail-soft, idempotency, and
thread-safety contracts. Forbidden — same as `intelligence-ledger-family.md` §1.

## Promotion / Rollback Evidence Floor

`L6/promo` MUST NOT emit `verdict=promote` without all four:
`wilson_lower ≥ 0.60`, `z_score ≥ 1.96`, `uplift > 0`, `n ≥ 30`.

`L6/regret` MUST emit per cycle with non-empty `by_layer_json`. A regret cycle
without per-layer attribution is a cycle that cannot teach anything — silent
violation under §28.

## Forbidden Patterns

- ❌ Emitting marker without library write (audit trail without record)
- ❌ Library write without marker (record without audit trail)
- ❌ Missing `decision_id` — outcomes cannot be bound later
- ❌ Hand-assigned promote verdict without Wilson + z + uplift fields
- ❌ Direct `sqlite3.connect()` to a router ledger from a router
- ❌ Buffering markers across multiple decisions (loses ordering)
- ❌ Reusing `decision_id` across different decisions
- ❌ Suppressing marker emission via env var without `LEDGER_WRITER_BYPASS=1`
  (the bypass mechanism is shared across all 10 ledgers)

## Cascade-side Audit Hook

When Cascade edits code in any router-implementing file
(matched by `agentic_core/L[0-6]*/.*router*\.py$`,
`*bandit*.py`, `*promo*.py`, `*regret*.py`,
`agentic_core/L6_observability/routing_*.py`,
`agentic_core/L6_observability/regret_accounting.py`,
`agentic_core/L6_observability/flywheel_promoter.py`,
`agentic_core/L6_observability/promotion_gates.py`,
`agentic_core/L6_observability/heal_router_otel.py`),
the response MUST contain either:

- A `ROUTER_DECISION:` marker (when the edit is being demonstrated end-to-end), OR
- An explicit reference to `emit_ledger_event(ledger="router_..."`

The post-hook `.windsurf/scripts/post_cascade_router_decision_audit.py`
detects edits-without-evidence and logs to
`artifacts/windsurf/router_enforcement_violations.jsonl`. Fail-open: missing
evidence does not block Cascade, but appears in the weekly enforcement report.

## CI Gate

`ops_scripts/ci/check_router_calibration_evidence.py` is the deterministic
fail-closed layer. It refuses to pass if any router-implementing file changed
in the last 7 days without a corresponding calibration report at
`docs/reports/calibration/routers/<layer>_<router>/<YYYY-Www>.md`.

Calibration reports are produced weekly by per-router scripts in
`ops_scripts/calibration/router_<layer>_<router>_calibration.py` (W3
expansion). Until those scripts ship, the gate runs in **advisory mode**
(exit 0, but emits a banner) — controlled by
`ROUTER_CI_GATE_MODE=advisory|strict`.

## Bypass

`ROUTER_ENFORCEMENT_BYPASS=1` — logs a bypass row and skips both the
post-hook and the CI gate. Same shape as other constitutional bypass
mechanisms. Use for scripted batch runs, smoke tests, or acknowledged
exploratory sessions.

## Sunset

Auto-retires per-router when:

- 90 consecutive days of zero violations in the violations log AND
- 4 consecutive weekly calibration reports show within-band drift AND
- A successor mechanism (e.g., L6-promo's own self-attestation gate) is
  documented in an ADR

Same lifecycle pattern as `mcp-serialization.md`. Per-router sunset
controlled by `.windsurf/config/router_enforcement_ttl.json`.

## Constitutional Tie-in

Constitutional rule §28 codifies the invariant. See `constitutional.md`.
Related: `intelligence-ledger-family.md` (parent pattern, ADR-050),
`author-gate-enforcement.md` (sibling pattern, developer-loop).
