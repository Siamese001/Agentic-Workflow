---
trigger: model_decision
description: Core invariant only — Scope expansion authorization requires AUTHORIZATION_DECISION marker. Full procedures moved to plan-lifecycle-procedures.md (W3.P3 2026-05-12). Demoted from always_on 2026-05-26 (governance-dedup-closeout-e8a4c2 W4). Cursor SSOT: .cursor/rules/plan-update-enforcement.mdc (alwaysApply: false).
---

> See `plan-lifecycle-procedures.md` for full procedural guidance on plan updates.

# Plan Update Enforcement — Core Invariant

## The Rule

> **Documentation ≠ Authorization.** A plan update filed after work completes is retroactive permission, not governance.

## The Invariant (Always-On)

**No new work on discovered scope until `AUTHORIZATION_DECISION` emitted AND plan file updated.**

### Required Marker

```
AUTHORIZATION_DECISION: plan=<slug-6hex> decision=ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED authorized_by=<user|author_gate|self> decisive_reason="<justification>"
```

## Full Procedures

| Topic | Location |
|-------|----------|
| Four-step discipline | `plan-lifecycle-procedures.md` §2 |
| DISCOVERED_SCOPE marker | `plan-lifecycle-procedures.md` §2 |
| SCOPE_EXPANSION marker | `plan-lifecycle-procedures.md` §2 |
| Required plan updates | `plan-lifecycle-procedures.md` §2 |

## Bypass

- `SCOPE_AUTHORIZATION_BYPASS=1` — override all checks (logged)
- `PLAN_SCOPE_AUDIT_BYPASS=1` — skip post-cascade hook
- `AUTH_MARKER_RECENCY_SEC=<seconds>` — adjust window (default: 300)

---

**Core invariant preserved.** Full procedures moved to `plan-lifecycle-procedures.md` (W3.P3 2026-05-12).
