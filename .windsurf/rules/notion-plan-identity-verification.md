# Notion Plan Identity Verification

> **Prevention:** Always verify plan identity by querying Notion DB when page IDs are uncertain.

---

## The Rule (One Line)

**When targeting a Notion plan page for status updates, if the page ID is not 100% certain, query the Plans DB by slug before any `API-patch-page` call.**

---

## Why This Exists

### 2026-05-10 Incident

During a plan status update session, I mistakenly marked the wrong plans as "Deferred":

| Intended Target | Actually Updated | Impact |
|-----------------|------------------|--------|
| `l6-alignment-deferred-scope-c5e8a7` | `author-gate-ask-ui-consolidated-a1e3f7` | Completed plan wrongly marked Deferred |
| `l5-cert-ref-deferred-scope-f3a1b8` | `w6-emit-contract-enrichment-d8b2a4` | Completed plan wrongly marked Deferred |

**Root cause:** I used stale Notion page IDs from context instead of querying the database to verify the correct page for each slug.

**Resolution:** Manual correction required — reverted both plans back to "Completed" and marked the correct plans as "Deferred".

---

## Prevention Pattern

### Correct Approach

```python
# 1. Identify the plan slug you intend to update
intended_slug = "l6-alignment-deferred-scope-c5e8a7"

# 2. Query Notion Plans DB to get the canonical page_id
page = query_notion_plans_db(slug=intended_slug)
actual_page_id = page["id"]  # e.g., "35b27693-f55c-8189-8827-c3dec80f05fa"

# 3. Verify match before API call
if not ids_match(actual_page_id, targeted_page_id):
    raise PlanIdentityMismatch(
        f"Intended {intended_slug} resolves to {actual_page_id[:8]}... "
        f"but targeting {targeted_page_id[:8]}..."
    )

# 4. Proceed with verified page ID
mcp7_API-patch-page(page_id=actual_page_id, properties={...})
```

### Incorrect Approach (What Went Wrong)

```python
# WRONG: Using page ID from memory/context without verification
targeted_page_id = "35c27693-f55c-81a4-93a9-f485347bedcb"  # From context (WRONG!)
mcp7_API-patch-page(page_id=targeted_page_id, properties={...})
# Result: Updated author-gate-ask-ui-consolidated instead of l6-alignment-deferred-scope
```

---

## When to Apply

| Scenario | Action Required |
|----------|-----------------|
| Status update for single plan | Verify slug → page_id match |
| Bulk status updates (multiple plans) | Verify each slug individually |
| Page ID from memory >5 minutes old | Re-query to verify |
| Page ID passed from another session | Always re-query |
| Any uncertainty about page ID | Query first, proceed after verification |

---

## Implementation Reference

### Verification Helper

**File:** `.windsurf/scripts/pre_notion_plan_write_gate.py`

```python
from pre_notion_plan_write_gate import verify_plan_identity

result = verify_plan_identity(
    intended_slug="my-plan-slug",
    targeted_page_id="35b27693-f55c-..."
)

if not result.ok:
    print(f"MISMATCH: {result.message}")
    # Block operation or warn based on policy
```

### Post-Cascade Audit

**File:** `.windsurf/scripts/post_cascade_notion_plan_identity_audit.py`

Scans Cascade response for `mcp7_API-patch-page` calls targeting Plans DB, verifies each call's page_id matches the intended slug from context.

**Logs:** `artifacts/windsurf/plan_identity_violations.jsonl`

---

## Environment Variables

| Variable | Effect |
|----------|--------|
| `NOTION_PLAN_IDENTITY_BYPASS=1` | Skip verification (logs warning) |
| `NOTION_PLAN_IDENTITY_FAIL_CLOSED=1` | Exit 2 on mismatch (default: warn only) |
| `NOTION_PLAN_IDENTITY_AUDIT_BYPASS=1` | Skip post-cascade audit |

---

## Cross-References

- **Status taxonomy:** `.windsurf/rules/notion-plans-taxonomy.md`
- **Deferred scope writeback:** `.windsurf/rules/deferred-scope-capture.md` § "Notion Writeback"
- **Plan registration:** `.windsurf/rules/plan-registration-enforcement.md`
- **Implementation plan:** `.windsurf/plans/notion-plan-identity-verification-enforcement-f2a9c1.md`

---

## Enforcement Stack

| Layer | Mechanism | Timing |
|-------|-----------|--------|
| Pre-write | `pre_notion_plan_write_gate.py` | Before API call (manual invocation) |
| Post-cascade | `post_cascade_notion_plan_identity_audit.py` | After each Cascade response |
| CI gate | `check_notion_plan_status_anomalies.py` | Periodic audit |
| Rule | This document | Permanent reference |

---

## Rule Metadata

- **Type:** Procedural (governance)
- **Trigger:** Any Notion Plans DB status update
- **Enforcement:** Hook + audit + CI gate
- **Created:** 2026-05-10
- **Related Plan:** `notion-plan-identity-verification-enforcement-f2a9c1`

---

> **Remember:** The 2 minutes spent querying Notion to verify a page ID is infinitely cheaper than the 30 minutes spent diagnosing and correcting a mis-targeted status update across 130+ plans.
