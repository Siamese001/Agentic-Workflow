---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\notion-enforcement-ssot-hardening-e4f8a2.md'
original_relative_path: '_archive\\2026-05\\notion-enforcement-ssot-hardening-e4f8a2.md'
source_sha256: ef4bf9918cb88655ff9cfb646a50bcdb947a27c99ae3b4eee1193681b4d90fd1
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Notion enforcement SSOT hardening (e4f8a2)

## Goal

Remove editor-specific drift for Notion automation, align documentation with archived-database policy, clarify NP16 after ledger archive, and restore optional Cursor write-time signal without duplicating Python implementations.

last_updated: 2026-05-15

## Wave Structure

| Wave | Scope | Outcome | Evidence | Status |
|------|--------|---------|----------|--------|
| W1 | SSOT code | `tools/notion/unified_notion_status_auditor.py` + `notion_bearer_token.py`; `.cursor`/`.windsurf` scripts are thin shims | Same logic single file; shims set `NOTION_STATUS_VIOLATIONS_VENDOR` | ✅ DONE |
| W2 | Docs / AGENTS | NOTION-MAP matches `notion-archived-databases.mdc`; MCP row documents `NOTION_TOKEN` + legacy alias | `check_mcp_sync_integrity.py` OK after `sync_mcp_config.py` server_rows | ✅ DONE |
| W3 | CI NP16 | `check_notion_decision_parity.py` uses `.cursor/state/...` ledger; retired SQLite↔Notion drift; fail-closed only on legacy Notion posts | Direct script run exit 0 | ✅ DONE |
| W4 | Hooks | Cursor `after_agent_notion_status_audit.py`; Windsurf `working_directory` → `.` | `.cursor/hooks.json` + 56× hooks JSON cwd | ✅ DONE |
| W5 | Orphan script contracts | Docstrings on plan status / identity audits state hook non-registration and SSOT paths | `post_cursor_agent_notion_*_audit.py` headers | ✅ DONE |

## Acceptance

- Single implementation file for unified Notion status auditor; shims byte-tiny and identical modulo vendor env.
- `python ops_scripts/ci/check_notion_decision_parity.py` exits 0 (advisory) offline.
- JSON stdin smoke: `python .cursor/scripts/unified_notion_status_auditor.py` exits 0.

## Deferred (non-goals here)

- Collapsing multiple NP* gates into one facade script.
- Rewriting every script that reads `NOTION_API_KEY` first to prefer `NOTION_TOKEN` (shim documents canonical name).

## Runtime receipt

Machine-readable closeout: `artifacts/plan_lifecycle/notion-enforcement-ssot-hardening-e4f8a2_wave_completion_receipt.json` (generated 2026-05-15; `schema_version=plan_wave_runtime_receipt_v1`).

Notion Plans row may be flipped **In Progress → Completed** via (when token available):

`python tools/windsurf/wave_execution_state.py complete --plan notion-enforcement-ssot-hardening-e4f8a2 --note="receipt backfill + runtime markers"`

## Markers (audit trail)

WAVE_COMPLETE: plan=notion-enforcement-ssot-hardening-e4f8a2 wave=1 note="SSOT auditor + bearer token + shims"
WAVE_COMPLETE: plan=notion-enforcement-ssot-hardening-e4f8a2 wave=2 note="AGENTS NOTION-MAP + MCP sync rows + archived-db rule"
WAVE_COMPLETE: plan=notion-enforcement-ssot-hardening-e4f8a2 wave=3 note="NP16 post-archive gate semantics"
WAVE_COMPLETE: plan=notion-enforcement-ssot-hardening-e4f8a2 wave=4 note="Cursor notion hook + Windsurf cwd-relative hooks"
WAVE_COMPLETE: plan=notion-enforcement-ssot-hardening-e4f8a2 wave=5 note="Orphan audit script contract docstrings"
PLAN_COMPLETE: plan=notion-enforcement-ssot-hardening-e4f8a2 note="W1-W5 delivered; receipt artifacts/plan_lifecycle/notion-enforcement-ssot-hardening-e4f8a2_wave_completion_receipt.json; wave_execution_state complete synced Notion Completed"
