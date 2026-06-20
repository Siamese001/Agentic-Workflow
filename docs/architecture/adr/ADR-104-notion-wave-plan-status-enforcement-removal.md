# ADR-104 — Remove windsurf/cursor-era Notion + wave/phase/plan-status enforcement

- **Status:** Accepted
- **Date:** 2026-06-14
- **Supersedes (in part):** ADR-100 (enforcement-surface-consolidation) — specifically its decision to
  **KEEP** the Notion-status / wave-lifecycle / §36 plan-registration cluster as "load-bearing governance."
- **Branch:** `feat/notion-wave-enforcement-removal`

## Context

The repo accreted a large body of windsurf/cursor-era enforcement around **Notion updates, Notion
status, and "updating SSOT plan phases/waves."** In practice none of it functioned:

- The Notion gates (NP1–NP18, PR1, NP-DONE, WAVE-MARKER, NP-GUARD, PLAN-SUPERSEDE) are **advisory and
  token-gated** — they silently no-op when `NOTION_TOKEN` is unset (i.e. every offline/CI run).
- Several targeted **archived** Notion databases (ADR / MCP / Constitutional / SC-AP / Author-Gate /
  Anti-Pattern registries) that silently swallow writes.
- They enforced a **retired marker scheme** (`PLAN_CREATED`, `WAVE_COMPLETE`, `PHASE_COMPLETE`,
  `PLAN_COMPLETE`, `AUTHORIZATION_DECISION`) already superseded by native `AskUserQuestion` / `spawn_task`.

The operating-model review (145 plans / 0 shipped) is the symptom of this ceremony. ADR-100 had
explicitly *frozen* this cluster as load-bearing; the user directed its removal.

## Decision

Remove **100% of the Notion-coupled + wave/phase plan-status enforcement**, **keep** the self-contained
disk-side plan-markdown lint, and **keep** the (separate, working) Notion-ID literal SSOT hygiene.

**Removed:**
- Hooks/dispatch: `post_write_plan_reconcile` (hooks.json), `plan_driven_closer`,
  `post_agent_wave_lifecycle_capture`, `post_agent_wave_completion_audit`,
  `post_agent_plan_registration_capture`, `post_agent_plan_supersession_retire`,
  `unified_plan_creation_auditor`, `unified_notion_status_auditor`; the `after_file_edit` Notion
  re-sync block; the `pre_mcp_gate` wave-deferral + classification checks; ~13 orphan governance scripts.
- Subsystems: the entire `tools/notion/` (134 files) and `tools/plan_lifecycle/` (wave-state) trees;
  helpers `_notion_canonical`, `_notion_plans_status_check`, `_plan_registration`,
  `_wave_execution_state`, `_plan_supersession`, `_plan_scope_expansion_check`.
- CI: 24 gate files + their registry entries in `run_contract_gates.py`; the T7u pre-commit hook.
- Doctrine: 10 rules (`notion-plans-taxonomy`, `notion-plan-wave-deferral`, `plan-update-enforcement`,
  `notion-archived-databases`, `memory-notion-writeback`, `plan-lifecycle-procedures` + 4 stubs);
  the `plan-governance` and `notion` skills; constitutional **§36 retired**; AGENTS.md/AGENTS.md updates.
- ~42 tests asserting the removed surface.

**Kept (deliberately):**
- Disk-side plan-markdown lint: `check_plan_format_compliance`, `check_plan_wave_summary_top`,
  `check_plan_definition_of_done`, `plan-location.md`, `pre_write_plan_mint_gate`,
  `before_file_edit_branch_guard._is_plan_file`. These are self-contained, never touch Notion, and
  only validate plan-file *shape*.
- Notion-ID literal SSOT hygiene (NOT plan-status enforcement): `_notion_constants.py`,
  `config/notion_databases.yaml`, `check_notion_id_ssot_parity` (NP-IDSSOT),
  `check_external_service_literal_ssot` (AUDIT-3). The `notion` MCP remains for manual page/DB use.
- `post_agent_writeback_audit.py` restored as a **memory-only** advisory (Notion half stripped) because
  it is the `memory_recall` intelligence-ledger writer (separate ADR-050 system) — full deletion was
  over-scoped collateral.

## Consequences

- **Plans are disk-only.** There is no Notion plan registration, status taxonomy, or wave/phase
  lifecycle tracking. The Notion Backlog Items DB is an optional manual durable backlog only
  (constitutional §24).
- Per-Stop / per-MCP / per-edit hook overhead drops (Notion subprocess calls removed).
- Loss of the (non-functional) Notion audit trail for plan status — acceptable, since it never worked.
- Reverses ADR-100's keep-decision for this cluster; ADR-100's other consolidations stand.

## Verification

`python -m json.tool .codex/hooks.json`; the kept live hooks import+run clean on synthetic stdin;
`run_contract_gates.py` references only existing gate files (one pre-existing dangling ref unrelated);
kept disk-side plan tests pass; dangling-reference sweep clean.
