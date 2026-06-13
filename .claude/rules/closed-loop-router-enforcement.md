
<!-- Converted from `.claude/rules/closed-loop-router-enforcement.md`. Original Cursor trigger: `model_decision`. -->

# Closed-Loop Router Enforcement — Invariant-Only Stub

> ⛔ **Every routing, promotion, calibration, or feedback decision in the 10-layer matrix MUST emit a structured `ROUTER_DECISION:` event AND a paired `tools.ledgers.hook_helpers.emit_ledger_event` call in the same code path.** Silent emission, missing fields, or promotion without calibration evidence = constitutional violation (§29).

## Invariant

The marker + library-call MUST land together. Audit trail without record = silent. Record without audit trail = unverifiable.

## The 10-router matrix (SSOT)

`(layer, router)` keys: `L0/bandit`, `L0/r5`, `L1/c0`, `L2/cascade`, `L3/shape`, `L3/reroute`, `L4/uwg`, `L5/hitl`, `L6/promo`, `L6/regret`. Each has its own ledger at `artifacts/ledgers/router_<layer>_<router>.sqlite`.

## Marker grammar (minimum)

```
ROUTER_DECISION: layer=<L0..L6> router=<name> decision_id=<uuid> trace_id=<id> route_id=<id> selected=<arm_or_verdict> [field=value ...]
```

Per-router required fields are encoded in `tools/ledgers/hook_helpers.py` — never restate inline.

## Promotion / rollback evidence floor

`L6/promo` MUST NOT emit `verdict=promote` without ALL four:
- `wilson_lower ≥ 0.60`
- `z_score ≥ 1.96`
- `uplift > 0`
- `n ≥ 30`

`L6/regret` cycles MUST emit non-empty `by_layer_json`.

## Where the procedural detail lives

| Concern | Location |
|---|---|
| Full per-router field contracts, library-call invariant, code patterns | (this rule was SSOT — full text preserved in git history at HEAD~1) |
| Audit hook | `.claude/governance/scripts/post_agent_router_decision_audit.py` → `artifacts/governance/router_enforcement_violations.jsonl` |
| CI gate | `ops_scripts/ci/check_router_calibration_evidence.py` (advisory; switch to strict via `ROUTER_CI_GATE_MODE=strict`) |
| Library helper | `tools/ledgers/hook_helpers.emit_ledger_event` |
| Per-router consulting skills | `.claude/skills/ledger-consulter-router-l*/` (12 skills) |
| Bypass | `ROUTER_ENFORCEMENT_BYPASS=1` |

## Forbidden patterns

- Marker without library write (audit trail without record)
- Library write without marker (record without audit trail)
- Missing `decision_id` (outcomes cannot be bound later)
- Hand-assigned `verdict=promote` without Wilson + z + uplift + n
- Direct `sqlite3.connect()` to a router ledger from a router (bypasses fail-soft + idempotency)
- Reusing `decision_id` across decisions
- Buffering markers across decisions

## Constitutional cross-reference

§29 (Closed-loop router evidence mandatory). Parent pattern: `intelligence-ledger-family.md` (ADR-050). Sunset: per-router auto-retires after 90 days zero violations + 4 in-band calibration reports + successor ADR.
