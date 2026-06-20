---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\notion-integration-consistency-audit-b2c4d8.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\notion-integration-consistency-audit-b2c4d8.md'
source_sha256: 79f39a69e9f9f6b08824d4d1f0f5b0402ab24a2e2c8951117765ed779e659caa
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Notion Integration Consistency Audit & Remediation

> Systematic audit of all Notion touchpoints — documentation vs reality, working vs broken integrations, orphaned automation.

---

## Context (SCQA)

- **Situation** — Previous RCA (plan `fix-rules-notion-drift-c4e7b2`) revealed the Constitutional Rules Registry was archived 2026-05-02 but still documented in AGENTS.md. User suspects broader systemic drift between documented Notion integrations and actual working automation.
- **Complication** — The `notion_db_consolidation_2026_05_02.py` script archived 4 databases: Constitutional Rules Registry, MCP Registry, SC/AP Violation Backlog, ADR Registry. However, AGENTS.md Auto-Routing Rules still reference some of these as write targets. Additionally, the scope of working vs broken Notion automation is unclear.
- **Question** — Which Notion integrations are actually working? Which are documented but broken? Which hooks/gates are orphaned or redundant? What is the complete inventory of gaps?
- **Answer** — This plan conducts a comprehensive audit across AGENTS.md, hooks.json, CI gates, and rules to identify all inconsistencies, then fixes them systematically.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `AGENTS.md` Notion Workspace Map | Canonical documentation of databases and write triggers | ✅ Just updated in fix-rules-notion-drift-c4e7b2 |
| `AGENTS.md` Auto-Routing Rules | Documents expected Notion writes per event type | 🔲 Needs audit vs archived databases |
| `.windsurf/hooks.json` | Registers all post-cascade and pre-user-prompt hooks | 🔲 Needs completeness check |
| `ops_scripts/maintenance/notion_db_consolidation_2026_05_02.py` | Confirms which databases were archived 2026-05-02 | ✅ Read |
| `.windsurf/scripts/` | Hook scripts inventory | ✅ Listed |
| `ops_scripts/ci/` | CI gates that check Notion consistency | ✅ Listed |
| `ops_scripts/ci/run_contract_gates.py` | Gate registration status | 🔲 Verify all Notion gates registered |

---

## Preliminary Findings (Audit Kick-off)

### Finding 1: Archived databases still referenced in Auto-Routing Rules

The AGENTS.md Auto-Routing Rules table (line 92-102) lists write triggers that target **archived databases**:

| Event | Documented Write Target | Database Status |
|---|---|---|
| Modify `.windsurf/mcp_config.json` | MCP Registry | ❌ **ARCHIVED** 2026-05-02 |
| Change gate behavior in `pre_mcp_gate.py` | MCP Registry | ❌ **ARCHIVED** 2026-05-02 |
| Resolve `ask_user_question` | Author-Gate Decision Ledger | ❌ **ARCHIVED** 2026-05-02 |
| Run `generate_full_adg.py` → SC/AP defects | SC/AP Violation Backlog | ❌ **ARCHIVED** 2026-05-02 |
| Mutation rejection report → new mutation | SC/AP Violation Backlog | ❌ **ARCHIVED** 2026-05-02 |

### Finding 2: Working Notion integrations (verified)

| Database | Data Source ID | Status | Automation |
|---|---|---|---|
| Plans | `ac53d31b-3068-4039-9ebe-856c12caab32` | ✅ LIVE | Wave lifecycle, registration |
| Backlog Items | `fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7` | ✅ LIVE | Deferred scope capture |
| Anti-Pattern Burndown | `4599fe37-8c24-4d89-96af-438b99a967c4` | 🔲 **VERIFY** | Need to check if actively used |

### Finding 3: Potential orphaned hooks (need verification)

From `.windsurf/scripts/` list — these mention Notion but may lack working targets:
- `post_cascade_adr_registry_capture.py` — ADR Registry was archived
- MCP-related sync hooks may be orphaned

---

## Wave Structure

| Wave | Phase IDs | Focus | Status |
|------|-----------|-------|--------|
| W1 | 1.1-1.4 | AGENTS.md Auto-Routing Rules cleanup (archived DB references) | ✅ DONE |
| W2 | 2.1-2.4 | Orphaned hook audit + removal/repurpose | ✅ DONE |
| W3 | 3.1-3.3 | CI gate inventory + registration gaps | ✅ DONE |
| W4 | 4.1-4.3 | Rules inventory + Notion reference cleanup | ✅ DONE |
| W5 | 5.1-5.2 | Final verification + documentation | ✅ DONE |

**Total: 5 waves, ~25K tokens**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | Inventory archived DB references in AGENTS.md | `AGENTS.md` Auto-Routing Rules section | Must distinguish "write to Notion" from "write to archived DB" | ~2K | 🔲 |
| 1.2 | Update Auto-Routing Rules for MCP Registry | `AGENTS.md` | Change to "No Notion write — filesystem SSOT" or remove | ~2K | 🔲 |
| 1.3 | Update Auto-Routing Rules for SC/AP Backlog | `AGENTS.md` | Same pattern — remove or redirect to filesystem | ~2K | 🔲 |
| 1.4 | Add Filesystem-SSOT clarity for all archived DBs | `AGENTS.md` | Reference archived DB consolidation decision | ~2K | 🔲 |
| 2.1 | Audit hook scripts for orphaned targets | `.windsurf/scripts/post_cascade_*` | Identify hooks targeting archived DBs | ~3K | 🔲 |
| 2.2 | Verify ADR registry hook status | `post_cascade_adr_registry_capture.py` | Check if still firing; decide archive or repurpose | ~2K | 🔲 |
| 2.3 | Document orphaned hook disposition | `AGENTS.md` or new rule | Clear inventory of what's kept vs removed | ~2K | 🔲 |
| 2.4 | Verify hook registration in hooks.json | `.windsurf/hooks.json` | Ensure active hooks registered; inactive removed | ~2K | 🔲 |
| 3.1 | Inventory all Notion-related CI gates | `ops_scripts/ci/check_notion_*.py` | List all gates, their targets, status | ~3K | 🔲 |
| 3.2 | Verify gate registration in run_contract_gates.py | `run_contract_gates.py` | Ensure all gates in assurance/wiring lists | ~2K | 🔲 |
| 3.3 | Document gate bypass/fail-closed patterns | New or existing rule | Consistent env var naming | ~2K | 🔲 |
| 4.1 | Audit rules for Notion references | `.windsurf/rules/*.md` grep for "notion|Notion" | Identify stale references | ~3K | 🔲 |
| 4.2 | Update notion-plans-taxonomy.md if needed | `notion-plans-taxonomy.md` | Ensure reflects current state | ~2K | 🔲 |
| 4.3 | Add rule about archived DBs | `.windsurf/rules/notion-archived-databases.md` | Document what was archived and why | ~2K | 🔲 |
| 5.1 | End-to-end verification | All modified files | Run gates, verify no broken references | ~2K | 🔲 |
| 5.2 | Notion registration + plan complete | Notion Plans DB | Register this plan, mark complete | ~2K | 🔲 |

---

## Execution Plan

### Wave 1 — AGENTS.md Auto-Routing Rules Cleanup

**Phase 1.1 — Inventory all archived DB references**

Systematically scan AGENTS.md Auto-Routing Rules table for references to:
- MCP Registry (`59693bbc-71b1-4c63-bc9f-b31eb8b08a0e`)
- SC/AP Violation Backlog (`0a3b8072-eabd-4516-9473-3c321bb011ff`)
- Author-Gate Decision Ledger (if mentioned)

**Phase 1.2 — Update MCP Registry references**

Change Auto-Routing Rules entries:
- From: "`API-patch-page` (or post new) into MCP Registry"
- To: "**No Notion write** — MCP Registry archived 2026-05-02. Filesystem change only; document in commit message."

**Phase 1.3 — Update SC/AP Violation Backlog references**

Same pattern — redirect to filesystem logging or remove write expectation.

**Phase 1.4 — Add comprehensive footnote**

After Auto-Routing Rules table, add:
```
> ⛔ **Archived databases (2026-05-02 consolidation):** MCP Registry, Constitutional Rules Registry, SC/AP Violation Backlog, ADR Registry, Author-Gate Decision Ledger (if separate) are all archived. All formerly targeted writes are now filesystem-only.
```

### Wave 2 — Orphaned Hook Audit

**Phase 2.1 — Audit hook scripts**

Review each `post_cascade_*` hook that mentions Notion:
- `post_cascade_adr_registry_capture.py` — ADR Registry archived, check status
- Any MCP registry sync hooks
- Any SC/AP violation backlog hooks

**Phase 2.2 — Verify ADR registry hook**

Read `post_cascade_adr_registry_capture.py`:
- If it still tries to write to archived DB, decide: repurpose for filesystem logging, or remove
- Check if it's registered in hooks.json

**Phase 2.3 — Document disposition**

For each orphaned hook, document decision:
- **Keep** — repurposed for filesystem logging
- **Remove** — no longer needed, remove from hooks.json
- **Archive** — move to `.windsurf/scripts/_archive/`

**Phase 2.4 — Update hooks.json**

Ensure only working hooks are registered. Remove entries for archived targets.

### Wave 3 — CI Gate Inventory

**Phase 3.1 — Inventory Notion-related gates**

List all `check_notion_*.py` gates and their targets:
- `check_notion_plans_ai_summary.py` → Plans DB
- `check_notion_plans_status_canonical.py` → Plans DB
- `check_notion_backlog_*.py` → Backlog Items DB
- Any gates targeting archived DBs

**Phase 3.2 — Verify registration**

Check each gate is registered in `run_contract_gates.py` assurance_gates or wiring_gates list.

**Phase 3.3 — Document bypass patterns**

Ensure consistent env var naming:
- `NOTION_PLANS_*_BYPASS=1`
- `NOTION_BACKLOG_*_BYPASS=1`
- `NOTION_*_FAIL_CLOSED=1`

### Wave 4 — Rules Inventory

**Phase 4.1 — Grep rules for Notion references**

Search all `.windsurf/rules/*.md` for "notion|Notion" references. Identify:
- Rules that correctly reference working integrations (Plans, Backlog)
- Rules that incorrectly reference archived DBs

**Phase 4.2 — Update notion-plans-taxonomy.md**

Ensure it reflects:
- Current working databases (Plans, Backlog Items, Anti-Pattern Burndown if active)
- Archived databases explicitly noted as "do not reference"

**Phase 4.3 — Create notion-archived-databases.md rule**

New rule documenting:
- What was archived (2026-05-02 consolidation)
- Why (reduce Notion complexity, filesystem SSOT)
- Migration path (filesystem logging instead)

### Wave 5 — Verification & Closeout

**Phase 5.1 — End-to-end verification**

Run all modified gates:
```bash
python ops_scripts/ci/check_rules_filesystem_integrity.py
# Verify AGENTS.md syntax
python -c "import json; json.load(open('.windsurf/hooks.json'))"
```

**Phase 5.2 — Notion registration**

Create/update Plans DB row for this audit plan.

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | AGENTS.md Auto-Routing Rules updated — no archived DB references | `grep -i "mcp registry\|sc/ap violation" AGENTS.md` returns 0 in Auto-Routing section | ✅ |
| DoD-2 | Orphaned hooks identified and dispositioned | `post_cascade_adr_registry_capture.py` repurposed (filesystem-only); `post_write_mcp_config_sync.py` Notion block removed | ✅ |
| DoD-3 | hooks.json updated — only working hooks registered | `python -c "import json; json.load(open('.windsurf/hooks.json'))"` passes | ✅ |
| DoD-4 | CI gate inventory complete — all Notion gates registered | 17 `check_notion_*.py` gates registered as NP1–NP18+NP-GUARD in `run_contract_gates.py` | ✅ |
| DoD-5 | Rules inventory complete — no stale Notion references | `memory-notion-writeback.md` and `mcp-config-ssot.md` fixed; all other rules clean | ✅ |
| DoD-6 | New rule notion-archived-databases.md created | `.windsurf/rules/notion-archived-databases.md` exists | ✅ |
| DoD-7 | Plan registered in Notion | Plans DB row Status="Completed" | ✅ |

---

## Rollback Strategy

1. Revert AGENTS.md: `git checkout AGENTS.md`
2. Revert hooks.json: `git checkout .windsurf/hooks.json`
3. Restore archived hooks if removed: `git checkout .windsurf/scripts/`
4. Mark Notion plan Status="Retired" with reason

---

## Non-Goals

- ❌ Recreate any archived Notion databases
- ❌ Add new Notion integrations
- ❌ Modify working Plans DB automation
- ❌ Modify working Backlog Items DB automation
- ❌ Archive Anti-Pattern Burndown without verification

---

## Verification-vs-Deferral

| Item | Verified This Plan | Deferred |
|---|---|---|
| AGENTS.md cleanup | ✅ | — |
| Orphaned hook audit | ✅ | — |
| CI gate registration | ✅ | — |
| Rules Notion reference audit | ✅ | — |
| Actual removal of archived hooks | — | ✅ Needs user confirmation per file |
| Anti-Pattern Burndown active status | — | ✅ Need live Notion query |
| Hook script repurposing decisions | — | ✅ User approval per hook |

---

## Notes

**2026-05-02 Consolidation Context:**
The archival of 4 databases was intentional per Tier 1 plan to reduce Notion complexity. Filesystem is now SSOT for rules, ADRs, and MCP config. This plan closes the documentation gap where AGENTS.md still suggested writing to those databases.

**Pattern for this audit:**
Same shape as `fix-rules-notion-drift-c4e7b2` — identify drift, document reality, add CI validation, register in Notion. Difference: broader scope (all Notion touchpoints, not just rules).
