---
slug: notion-wave-lifecycle-deferred-scope
title: Notion Wave Lifecycle — Deferred Scope Items
author: Cascade
status: Deferred
created: 2026-05-10
updated: 2026-05-10
tags: [notion, plans, deferred-scope, oauth, backfill, backlog]
dod_exempt: false
parent_plan: notion-wave-lifecycle-autosync-f4a2b8
---

# Notion Wave Lifecycle — Deferred Scope Items

> Deferred scope from `notion-wave-lifecycle-autosync-f4a2b8.md` W1-W5 implementation. DO NOT IMPLEMENT until parent plan is verified in production.

## 1. Problem Statement

The parent plan (`notion-wave-lifecycle-autosync-f4a2b8.md`) implemented automatic Notion wave-lifecycle updates via direct HTTP calls, solving the drift problem for new plans. However, three items were intentionally deferred to keep the parent plan bounded and deliverable.

This plan captures those deferred items for future implementation.

## 2. Deferred Scope Items

### Item 1: Notion OAuth-Hosted MCP (Variant C)

**Current State:** The Notion MCP is configured as a local stdio server using `npx @notionhq/notion-mcp-server`. This is "Variant A" — local stdio with MCP serialization constraints.

**Gap:** Even with the direct-HTTP workaround implemented in the parent plan, the fundamental limitation remains: remote MCPs are subject to the §25 serialization rule (one-per-response, no batching). While local stdio MCPs can batch, the Notion MCP's tool naming (`^API-` pattern) triggers the serialization audit.

**Proposed Solution:** Evaluate and potentially migrate to an OAuth-hosted Notion MCP server (Variant C) where the MCP runs on a remote server with OAuth authentication. This would:
- Remove the local stdio process management burden
- Potentially allow different serialization behavior
- Enable shared state across multiple Cascade instances

**Blockers:**
- Requires setting up/hosting an OAuth MCP server (notion-mcp-server with OAuth flow)
- Need to verify if OAuth-hosted variant actually resolves §25 serialization (may not if tool names remain the same)
- Security review of OAuth token management vs. current `NOTION_TOKEN` env var approach

**Decision Gate:** Author-Gate required before implementation — the cost/benefit of OAuth hosting vs. current direct-HTTP solution needs explicit evaluation.

**Files Touched:** `.windsurf/mcp_config.json`, new OAuth callback handler, documentation updates.

---

### Item 2: Historical Plan Backfill

**Current State:** Hundreds of existing plans in the Notion Plans DB have drift (on-disk status ≠ Notion status) because they were created before the auto-sync mechanism existed.

**Gap:** The new auto-sync only applies to plans going forward. Historical drift remains unaddressed.

**Proposed Solution:** Run `tools/notion/repair_notion_plan_statuses.py` (already exists) as a one-time batch operation to:
1. Enumerate all `.windsurf/plans/*.md` files
2. Parse their frontmatter for `status` field
3. Compare to Notion Plans DB `Status` property
4. Patch Notion to match on-disk state where drift detected

**Precedent:** This script already exists and was used for the 2026-05-03 "Draft"→"Not Started" migration. It can be repurposed for general drift repair.

**Blockers:**
- Need to verify the script handles all edge cases (deleted plans, archived plans, status values that no longer exist)
- Manual review of high-impact plans before batch patching
- Communication to any humans who might have manually edited Notion statuses

**Decision Gate:** Low-risk batch operation, but requires:
- Dry-run to preview changes
- Backup of current Notion Plans DB state
- Small-scale test (10 plans) before full batch

**Files Touched:** `tools/notion/repair_notion_plan_statuses.py` (enhancements), potentially new `tools/notion/backfill_historical_plans.py` wrapper.

---

### Item 3: Backlog Items Mid-Plan Writeback (Clarification)

**Current State:** `post_cascade_deferred_scope_capture.py` already handles Notion writeback for Backlog Items when `DEFERRED_SCOPE:` markers are emitted.

**Gap:** The parent plan mentioned this as "already handled," but there's potential confusion about whether the wave-lifecycle auto-sync chain should also update Backlog Items (not just Plans DB).

**Clarification Needed:**
- Plans DB = wave/phase lifecycle (this plan's scope)
- Backlog Items DB = individual work items, their P-bands, and their completion status
- The two databases serve different purposes and have different update cadences

**Proposed Action:** Verify that `post_cascade_deferred_scope_capture.py` is correctly:
1. Parsing `DEFERRED_SCOPE:` markers from Cascade responses
2. Scoring P1..P5 using the deferred-scope scorer
3. Posting to Backlog Items DB with correct P-band
4. Linking back to the parent plan via `Plan` relation

**If Gaps Found:** Create follow-up plan to fix `post_cascade_deferred_scope_capture.py` integration.

**Decision Gate:** Verify-only; if gaps found, separate plan required.

**Files Touched:** `post_cascade_deferred_scope_capture.py` (if fixes needed), verification tests.

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | P1.1, P1.2 | OAuth-hosted MCP evaluation | ~4k | Deferred |
| W2 | P2.1, P2.2 | Historical plan backfill script | ~3k | Deferred |
| W3 | P3.1 | Backlog Items writeback verification | ~2k | Deferred |

Total: ~9k tokens.

## 4. Definition of Done

| DoD | Item | Verification |
|-----|------|--------------|
| DoD-1 | OAuth decision captured | Author-Gate packet emitted and captured; decision recorded in ledger |
| DoD-2 | Historical backfill complete | `repair_notion_plan_statuses.py` dry-run shows 0 remaining drift items |
| DoD-3 | Backlog Items verified | `post_cascade_deferred_scope_capture.py` test suite passes; live verification shows DEFERRED_SCOPE markers post to Backlog Items DB |

## 5. Risks and Dependencies

- **Risk:** OAuth-hosted MCP may not actually solve §25 serialization if the tool naming pattern remains `^API-`. Mitigation: POC before full implementation.
- **Risk:** Historical backfill could overwrite human-edited statuses. Mitigation: Dry-run and preview all changes.
- **Dependency:** Parent plan (`notion-wave-lifecycle-autosync-f4a2b8`) must be verified stable in production before this plan activates.

## 6. Cross-References

- Parent Plan: `.windsurf/plans/notion-wave-lifecycle-autosync-f4a2b8.md`
- Rule: `.windsurf/rules/notion-plan-wave-deferral.md` (sanctioned non-MCP path)
- Script: `tools/notion/repair_notion_plan_statuses.py` (existing backfill capability)
- Hook: `.windsurf/scripts/post_cascade_deferred_scope_capture.py` (Backlog Items writeback)

---

**Status:** Deferred — awaiting parent plan production verification
**Next Review:** 2026-05-17 (one week post-parent-completion) or upon explicit user request
