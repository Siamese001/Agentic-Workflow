---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\notion-plan-identity-deferred-scope-a3b7e2.md'
original_relative_path: 'notion-plan-identity-deferred-scope-a3b7e2.md'
source_sha256: b18286f0fc5d7546adc39ca3ecddbc038d45f64ea2e1537908f250a25de8dd72
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-10'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: notion-plan-identity-deferred-scope-a3b7e2
plan_type: tracker
---

# Notion Plan Identity Verification — Deferred Scope

Deferred items from `notion-plan-identity-verification-enforcement-f2a9c1` that are tracked but not yet implemented.

---

## DS-1: Real-time Notion Webhook Integration

**Status:** ⏸ Deferred  
**Priority:** LOW  
**Effort:** ~20k tokens  
**Gated by:** Volume thresholds (only worthwhile if >500 plans or >100 status changes/day)

**Problem:** Current polling-based verification queries Notion DB on each status change. At current volume (~130 plans, ~10 changes/day), this is acceptable but adds latency.

**Proposed Solution:** Webhook from Notion → local handler that maintains a cached slug→page_id mapping, updated in real-time as plans are created/modified.

**Acceptance:**
- Webhook endpoint at `/webhooks/notion/plans`
- Cached mapping updated within 5 seconds of Notion change
- Verification uses cache (no API call) for 95% of lookups

**Blocked until:** Plan volume exceeds 500 or status changes exceed 100/day

---

## DS-2: Automatic Rollback of Detected Anomalies

**Status:** ⏸ Deferred  
**Priority:** MEDIUM  
**Effort:** ~15k tokens  
**Gated by:** Confidence in anomaly detection (requires 30 days of NP8 gate data)

**Problem:** Current detection only logs anomalies. Manual intervention required to rollback mis-targeted status changes.

**Proposed Solution:** Automated rollback for HIGH severity anomalies (IDENTITY_MISMATCH):
1. Detect mismatch via post-cascade audit
2. Query Notion for status before change (version history)
3. Revert to previous status with comment annotation
4. Notify operator via log + optional Slack/email

**Acceptance:**
- Rollback completes within 60 seconds of detection
- Original status preserved (including timestamp of change)
- Rollback annotated with reason: "Auto-rollback: plan identity mismatch detected"
- Operator notification includes before/after states

**Safety requirements:**
- Only auto-rollback if confidence > 0.95 (known mismatch pattern)
- Skip rollback if plan has been modified since anomaly detected
- Bypass: `NOTION_AUTO_ROLLBACK_BYPASS=1`
- Log all rollback attempts to `artifacts/windsurf/auto_rollback.jsonl`

**Blocked until:** 30 days of NP8 gate data shows < 1% false positive rate

---

## DS-3: Cross-Reference Enforcement in Related Rules

**Status:** ⏸ Deferred  
**Priority:** LOW  
**Effort:** ~5k tokens

**Problem:** Rule cross-links exist but aren't enforced. Other rules may be updated without updating `notion-plan-identity-verification.md`.

**Proposed Solution:** Add link validation to CI gate that verifies:
- All cross-referenced rules exist
- All referenced sections exist in target rules
- No broken links after rule edits

**Acceptance:**
- CI gate fails if cross-reference broken
- Suggests fix with file path and line number

---

## DS-4: Memory MCP Integration for Pattern Persistence

**Status:** ⏸ Deferred  
**Priority:** LOW  
**Effort:** ~8k tokens

**Problem:** Prevention pattern lives in rule file but isn't in persistent memory for cross-session recall.

**Proposed Solution:** Create Memory MCP entity:
```
Entity: PreventionPattern
Name: notion-plan-identity-verification
Observations:
  - "Always verify plan identity by querying Notion DB when page IDs uncertain"
  - "2026-05-10 incident: marked wrong plans as Deferred due to stale page IDs"
  - "Root cause: relied on context instead of live query"
Relations:
  - prevents: notion-status-confusion
  - implemented_by: notion-plan-identity-verification-enforcement-f2a9c1
```

---

## Deferred Scope Summary

| DS | Item | Priority | Effort | Blocked By |
|----|------|----------|--------|------------|
| DS-1 | Real-time webhook | LOW | ~20k | Volume thresholds |
| DS-2 | Auto-rollback | MEDIUM | ~15k | 30 days NP8 data |
| DS-3 | Cross-reference enforcement | LOW | ~5k | ✅ DONE (RULE-XREF gate created, 1 broken ref found in apps-folder-taxonomy.md) |
| DS-4 | Memory MCP integration | LOW | ~8k | ✅ DONE (Entity NotionPlanIdentityVerification created with 12 observations, 3 relations) |

---

## Activation Criteria

This deferred scope plan activates when ANY of:
- Plan volume exceeds 500 (triggers DS-1 evaluation)
- 30 days NP8 data collected with < 1% FP rate (triggers DS-2)
- Cross-reference CI gate fails in another plan (triggers DS-3)
- Memory MCP pattern search shows recall gaps (triggers DS-4)

---

STATUS_FLIP: notion-plan-identity-deferred-scope-a3b7e2 notion_id=35c27693-f55c-8105-acc7-c121fe6860e4 from=Deferred to=In Progress at=2026-05-10T18:18:00Z reason="DS-3 and DS-4 completed, 2/4 deferred items done"

PLAN_CREATED: slug=notion-plan-identity-deferred-scope-a3b7e2 notion_id=35c27693-f55c-8105-acc7-c121fe6860e4 path=.windsurf/plans/notion-plan-identity-deferred-scope-a3b7e2.md status=Not Started tier=T3 layer=L_OPS parent_plan=notion-plan-identity-verification-enforcement-f2a9c1
