---
dod_exempt: true
---

# Notion Audit Deferred Scope

> Followup plan for items deferred from `notion-integration-consistency-audit-b2c4d8`.
> All three items require user decision or live Notion query before execution.

---

## Parent Plan

`notion-integration-consistency-audit-b2c4d8` — completed 2026-05-11, commit `9dc3f7f1ba`

---

## Wave Structure

| Wave | Phase IDs | Focus | Status |
|------|-----------|-------|--------|
| W1 | 1.1 | Verify Anti-Pattern Burndown active status | ✅ DONE |
| W2 | 2.1-2.2 | Hook deletion decisions (per-hook user approval) | ✅ DONE |
| W3 | 3.1 | Hook repurposing decisions finalization | ✅ DONE (subsumed into W2) |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | Anti-Pattern Burndown live status check | `AGENTS.md`, `notion-archived-databases.md` | — | ~1K | ✅ 404 confirmed; both files updated |
| 2.1 | Audit remaining hook scripts for Notion writes | `.cursor/scripts/*.py` | — | ~2K | ✅ All 10 Notion-writing hooks target active DBs only |
| 2.2 | Decide keep/retire per hook | n/a | — | ~0 | ✅ No dead writes found; no Author-Gate decisions needed |
| 3.1 | Finalize repurpose vs delete | n/a | — | ~0 | ✅ Subsumed — W2 already clean |

---

## Deferred Items Detail

### DS-1 — Anti-Pattern Burndown active status

**Source**: `notion-integration-consistency-audit-b2c4d8` Verification-vs-Deferral table  
**Issue**: Finding 2 in the parent plan listed Anti-Pattern Burndown DB (`4599fe37-8c24-4d89-96af-438b99a967c4`) as `🔲 VERIFY` — not confirmed active.  
**Action needed**:
1. Query the DB via `API-query-data-source` with `data_source_id=4599fe37-8c24-4d89-96af-438b99a967c4`
2. If empty or stale (no rows updated in 30d): update AGENTS.md Notion Workspace Map to mark it archived
3. If active: confirm automation is wired correctly and document

**Risk**: Low — read-only query. Worst case the DB is empty and we update one AGENTS.md table row.

---

### DS-2 — Hook script deletion decisions (user approval per file)

**Source**: `notion-integration-consistency-audit-b2c4d8` Verification-vs-Deferral table  
**Issue**: W2 repurposed two hooks but did NOT delete any scripts. Several `.cursor/scripts/` files may now be dead weight.  
**Candidates to review** (not deleted in W2, need explicit per-file decision):

| Script | Concern | Recommended Action |
|---|---|---|
| `post_cursor_agent_adr_registry_capture.py` | Repurposed to filesystem-only log — still registered in hooks.json | Keep as-is (provides audit trail) |
| Any script referencing `AUTHOR_GATE_LEDGER_DB_ID` | Author-Gate Ledger archived | Audit and remove Notion write paths |
| Any script referencing `ADR_REGISTRY_DB_ID` | ADR Registry archived | Remove write paths (read-only ref OK) |

**Action needed**: Enumerate remaining scripts with archived DB references, present per-file Author-Gate decisions.

---

### DS-3 — Hook repurposing decisions finalization

**Source**: `notion-integration-consistency-audit-b2c4d8` Verification-vs-Deferral table  
**Issue**: W2 made two repurposing decisions (`post_cursor_agent_adr_registry_capture` → filesystem-only, `post_write_mcp_config_sync` → remove Notion block). Other hooks may have partial Notion writes that need the same treatment.  
**Action needed**:
1. Run `grep -l "AUTHOR_GATE_LEDGER_DB_ID\|ADR_REGISTRY_DB_ID\|MCP_REGISTRY_DB_ID\|SCAP_VIOLATION_DB_ID" .cursor/scripts/*.py`
2. For each hit: Author-Gate decision — repurpose to filesystem-only vs delete vs keep with guardian exemption

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | Anti-Pattern Burndown status confirmed | Live Notion query → 404 → archived | ✅ |
| DoD-2 | All hook scripts with archived DB refs audited | Grep found 0 hook scripts with archived DB ID constants | ✅ |
| DoD-3 | Per-hook keep/retire/repurpose decisions captured | No dead writes found; no Author-Gate decisions needed | ✅ |
| DoD-4 | AGENTS.md updated if Anti-Pattern Burndown archived | Strikethrough row added; notion-archived-databases.md updated | ✅ |

---

## Rollback Strategy

- Revert any hook script changes: `git checkout .cursor/scripts/<name>.py`
- Restore hooks.json registration: `git checkout .cursor/hooks.json`
- This plan makes no CI gate or rule changes

---

## Non-Goals

- ❌ No new Notion databases
- ❌ No CI gate changes
- ❌ No rule changes beyond AGENTS.md Workspace Map update if needed
