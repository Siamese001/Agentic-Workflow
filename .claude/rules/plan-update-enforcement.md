
<!-- Converted from `.claude/rules/plan-update-enforcement.md`. Original Cursor trigger: `always_on`. -->

> See `plan-governance` skill for full procedural guidance on plan updates.

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
| Four-step discipline | `plan-governance` skill §2 |
| DISCOVERED_SCOPE marker | `plan-governance` skill §2 |
| SCOPE_EXPANSION marker | `plan-governance` skill §2 |
| Required plan updates | `plan-governance` skill §2 |

## Bypass

- `SCOPE_AUTHORIZATION_BYPASS=1` — override all checks (logged)
- `PLAN_SCOPE_AUDIT_BYPASS=1` — skip post-cursor_agent hook
- `AUTH_MARKER_RECENCY_SEC=<seconds>` — adjust window (default: 300)

---

**Core invariant preserved.** Full procedures: `.claude/skills/plan-governance/SKILL.md` (W2 governance dedupe).
