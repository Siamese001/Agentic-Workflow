---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\notion-schema-refactor-cleanup-9f2e4a.md'
original_relative_path: '_archive\\2026-05\\notion-schema-refactor-cleanup-9f2e4a.md'
source_sha256: b5e8ed5999cbf08d4918072c3114fc679e616eb67f55ca20153a99b26a84b5c0
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: notion-schema-refactor-cleanup-9f2e4a
plan_type: infra
---

# Notion Backlog Schema Refactor — Cleanup Followups

Consolidated followups emerging from W1/W2/W3 of `notion-backlog-schema-refactor-7c3d9e`. Each row below corresponds to a `DEFERRED_SCOPE:` marker that post_cascade_deferred_scope_capture.py auto-posts to Wave/Phase Convergence with a scorer-assigned priority.

---

## Evidence Sources

| Source | Why | Status |
|---|---|---|
| Plans DS (`ac53d31b-3068-4039-9ebe-856c12caab32`) | Contains 7 Proposed rows needing resolution | ✅ |
| Backlog DS post-W3 | 220 rows linked to Plans; 4 P2 rows reference `adg-mcp-reopen-hardening` | ✅ |
| `tools/priority/deferred_scope_scorer.py` | Scorer SSOT — assigns P1..P5 | ✅ |

---

## Phase-Level Summary

| Phase ID | Title | Scope | Pain | Est. Tokens | Status |
|---|---|---|---|---|---|
| C1.1 | Promote `adg-mcp-reopen-hardening` to real plan file | 4 backlog rows reference a NEW: slug; plan file missing on disk | PP-1 orphan plan | 4k | 🔲 TODO |
| C2.1 | Promote `anthropic-alignment-followups` to real plan file | Proposed Plans row; no file on disk | PP-2 | 3k | 🔲 TODO |
| C3.1 | Promote `hybrid-search-adg-seed-impl` to real plan file | Proposed Plans row; referenced by 1 P1 backlog row (E.F1.1) | PP-3 | 3k | 🔲 TODO |
| C4.1 | Promote `query-progress-bar-backlog` to real plan file | Proposed Plans row; referenced by §16 ratchet work | PP-4 | 2k | 🔲 TODO |
| C5.1 | Archive garbage slugs + index marker in Plans DS | 3 slugs: `(in-session work...)`, `(no dedicated plan...)`, `_INDEX_open_scope_inventory`; relink affected backlog rows to proper plan | PP-5 stale provenance | 2k | 🔲 TODO |

**Total: 14k tokens, 5 phases.**

---

## Execution Plan

### C1 — `adg-mcp-reopen-hardening` plan promotion
Scope: 4 backlog rows (W1.1, W1.2, W2.1, W2.2) with impact scores 215/254/139/254 depend on this plan. Create plan file summarizing the 4 phases and flip Plans row Status Proposed→Active.

### C2–C4 — Other proposed-plan promotions
Same pattern as C1 for each remaining Proposed row.

### C5 — Garbage slug archival
Update Backlog rows pointing to garbage slugs to point at real plans (determine by reading each row's `Parent Plan Summary` / `Blocking Items`); then archive the 3 Plans DS rows (set Status=Archived).

---

## Rules

- No deletion of Plans rows — Archive only (preserves relation integrity).
- New plan files use 6hex suffix convention.
- Emit `DEFERRED_SCOPE:` markers for each phase so the post-hook mirrors to Notion.

---

## Success Criteria

- [ ] 4 new plan files exist under `.windsurf/plans/`
- [ ] 4 Proposed→Active in Plans DS
- [ ] 3 garbage Plans rows Archived with backlog rows relinked
- [ ] 0 Proposed rows with `Exists On Disk=false` remain

---

## Rollback Strategy

1. Delete new plan files (`.windsurf/plans/*.md`).
2. Flip Plans DS rows back to Proposed.
3. Relation integrity preserved throughout — no data loss path.
