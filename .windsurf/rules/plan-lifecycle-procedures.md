---
trigger: model_decision
description: Use when interacting with plan lifecycle operations — registration, updates, wave execution, deferrals, identity verification, backlog linkage. Procedural companion to always-on invariants plan-location.md and notion-plans-taxonomy.md.
---

# Plan Lifecycle Procedures

> Procedural guidance for plan lifecycle management. **Always-on invariants are in plan-location.md (SSOT location) and notion-plans-taxonomy.md (status taxonomy).**

---

## 1. Plan Registration (§36)

### Invariant
Every `.windsurf/plans/<slug>-<6hex>.md` MUST have a Notion Plans DB row before wave execution.

### Required Marker
When creating a plan:
```
PLAN_CREATED: slug=<slug-6hex> path=.windsurf/plans/<slug>-<6hex>.md status=Not Started|In Progress
```

### Chokepoint Block
`tools/windsurf/wave_execution_state.py start` refuses unregistered plans:
```
BLOCKED: plan <slug> not registered in Notion Plans DB.
Required: API-post-page into Plans DB
Bypass: PLAN_REGISTRATION_BYPASS=1
```

### Query Before Claim
> Cascade MUST NOT assert registration status without live `API-query-data-source` call in same response.

---

## 2. Plan Update Authorization (Scope Expansion)

### Four-Step Discipline

```
Step 1: DISCOVERED_SCOPE marker   — Document before any work
Step 2: AUTHORIZATION_DECISION     — ACCEPTED / DEFERRED / SPLIT / REJECTED
Step 3: Plan file updates          — Tables, DoD, last_updated
Step 4: SCOPE_EXPANSION marker     — Execute only after Step 3
```

### Markers

**Discovery** (before any new work):
```
DISCOVERED_SCOPE: plan=<slug> wave=<N> phase=<M> gap="<description>" impact="<severity>"
```

**Authorization** (same response as discovery):
```
AUTHORIZATION_DECISION: plan=<slug> decision=ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED authorized_by=<user|author_gate|self> decisive_reason="<justification>"
```

**Expansion** (after all updates complete):
```
SCOPE_EXPANSION: plan=<slug> reason="<summary>" added="<waves/phases/gaps>" authorized="yes"
```

### Decision Semantics

| Decision | When | Plan Update | Continues? |
|----------|------|-------------|------------|
| ACCEPTED | Critical-path, in-charter | Yes — all updates | On expanded scope |
| DEFERRED | Time/volume gated | No — emit DEFERRED_SCOPE | Original only |
| SPLIT_TO_NEW_PLAN | Too large | No — new plan | Original only |
| REJECTED | Gold-plating/off-charter | No | Original only |

---

## 3. Wave Execution & Deferral

### Notion Wave Deferral Protocol

> ⛔ **During multi-wave execution: NO Notion MCP calls. Defer ALL writes until final wave completes.**

**Wave lifecycle via direct HTTP** (sanctioned non-MCP path):
1. **Wave 1 start**: `wave_execution_state.py start --plan <slug>` → Status=`In Progress`
2. **During execution**: NO MCP writes (blocked by `pre_mcp_gate.check_notion_wave_deferral()`)
3. **After each wave**: `wave_execution_state.py wave-progress --wave N` → Summary append
4. **Final wave**: `wave_execution_state.py complete` → Status=`Completed`
5. **Post-completion**: Batch MCP writes one-per-block

### Required Markers

```
WAVE_COMPLETE: plan=<slug-6hex> wave=<N> note="<files>, <tests>, <scope>"
PHASE_COMPLETE: plan=<slug-6hex> phase=<id> note="<one-liner>"
PLAN_COMPLETE: plan=<slug-6hex> note="<final outcome>"
```

### Retrospective Plans

> ⛔ **NEVER call `wave_execution_state.py start` on retrospective plans.**

**Correct protocol**:
1. Write plan to `.windsurf/plans/<slug>.md`
2. Register via `API-post-page` with `status=Completed`
3. Emit `PLAN_COMPLETE: plan=<slug>`
4. Do NOT emit `PLAN_CREATED:`

---

## 4. Plan Identity Verification

### Prevention Pattern

When targeting Notion plan pages, **query by slug before `API-patch-page`**:

```python
# 1. Identify intended slug
intended_slug = "my-plan-slug"

# 2. Query Plans DB for canonical page_id
page = query_notion_plans_db(slug=intended_slug)
actual_page_id = page["id"]

# 3. Verify match
if not ids_match(actual_page_id, targeted_page_id):
    raise PlanIdentityMismatch(f"Slug {intended_slug} resolves to {actual_page_id}")

# 4. Proceed with verified ID
mcp7_API-patch-page(page_id=actual_page_id, properties={...})
```

### When to Verify

| Scenario | Action |
|----------|--------|
| Status update for single plan | Verify slug → page_id match |
| Bulk updates | Verify each slug |
| Page ID from memory >5 min old | Re-query |
| Page ID from another session | Always re-query |
| Any uncertainty | Query first |

---

## 5. Backlog-Plan Linkage

### Invariant
Every Backlog Items row MUST have:
- (a) `Plan` relation to Plans DB page, OR
- (b) non-empty `Plan File` slug

Rows with neither are "true orphans" (CI gate NP3 violation).

### Fix Procedure

1. Run `tools/notion/backfill_backlog_plan_relation.py` to re-link rows
2. If orphans remain: `tools/notion/apply_orphan_disposition.py` to route to catch-all
3. Re-run gate to confirm zero violations

### Authoritative Source Policy

- **Status**: Plan-derived wins ONLY when Backlog Status is scorer-default (`Draft`)
- **Layer**: Backlog value is authoritative (Plans DB has no Layer)
- **Plan File**: Backlog slug is canonical (format differs from Plans)

---

## Bypass Reference

| Bypass | Effect | Use When |
|--------|--------|----------|
| `PLAN_REGISTRATION_BYPASS=1` | Skip wave-start block | Scripted batch, emergency |
| `SCOPE_AUTHORIZATION_BYPASS=1` | Skip update auth checks | Emergency override |
| `NOTION_WAVE_DEFERRAL_BYPASS=1` | Allow MCP mid-wave | User-requested reads only |
| `NOTION_PLAN_IDENTITY_BYPASS=1` | Skip ID verification | Debug only |

---

## Related Rules

| Rule | Purpose |
|------|---------|
| `plan-location.md` | SSOT location, format requirements, Notion status discipline |
| `notion-plans-taxonomy.md` | Status canonicalization, transition matrix |
| `deferred-scope-capture.md` | DEFERRED_SCOPE markers (§24) |
| `scope-containment.md` | Scope boundaries (§18) |

---

**Procedural companion to always-on invariants.**
