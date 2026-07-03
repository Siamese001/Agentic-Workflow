# AGENTS.md Tier-1 companion (procedural SSOT)

> **Moved from root `AGENTS.md` in W1** (`cursor-governance-two-tier-b4e8f2`) per Option A.  
> Tier-1 `AGENTS.md` keeps invariants + autogen tables; this file holds procedural detail.  
> **Edit SSOT for rules:** `.codex/rules/*.md` only — legacy editor rule names are historical references, not edit targets.

## Notion — manual MCP use only (no plan-status enforcement)

The windsurf/cursor-era Notion plan-status / registration / wave-lifecycle enforcement was
**removed** (`notion-wave-enforcement-removal`): the auto-sync hooks, the NP-series CI gates, the
`PLAN_CREATED`/`WAVE_COMPLETE`/`PHASE_COMPLETE`/`PLAN_COMPLETE` marker chain, and
`tools/notion/` are all gone. The `notion` MCP remains for **manual page/DB read+write only**.

Everything is filesystem SSOT — never mirrored to Notion:

| Content | Canonical Path | Notion? |
|---------|----------------|---------|
| Rules | `.codex/rules/*.md` | NO |
| ADRs | `docs/architecture/adr/*.md` | NO |
| Plans | `plans/<slug>-<6hex>.md` | NO (disk-only) |
| Calibration | `docs/reports/calibration/<YYYY-Www>.md` | NO |

The Notion Backlog Items DB is an *optional manual* durable backlog (constitutional §24) —
never enforced, never for plan status. Editing `.mcp.json` still runs
`python .codex/governance/scripts/sync_mcp_config.py` (no Notion write).

## MCP sync enforcement

| Gate | Command |
|------|---------|
| Strict sync | `python ops_scripts/ci/check_mcp_sync_integrity.py` |
| Coverage | `python ops_scripts/ci/check_agents_mcp_coverage.py` |
| Editor parity | `python ops_scripts/ci/check_mcp_editor_parity.py` |
| legacy editor SSOT check | `python .codex/governance/scripts/sync_mcp_config.py --check` |

Regenerate: `python .codex/governance/scripts/sync_mcp_config.py` (refreshes AGENTS autogen blocks + global MCP copy).

## Intelligence ledgers (ADR-050)

Nine SQLite ledgers under `artifacts/ledgers/`. Consult via `LedgerConsulter("<name>").lookup(...)` before acting. (memory_recall retired — notion-wave-enforcement-removal.)

| Ledger | Writer | Consulting skill |
|--------|--------|------------------|
| tool_routing | post_agent_adg_audit | ledger-consulter-tool-routing |
| refactor_outcome | post_commit_outcome_binder | ledger-consulter-refactor-outcome |
| prompt_classifier | pre_prompt_classifier + binder | ledger-consulter-prompt-classifier |
| mcp_invocation | post_mcp_audit | ledger-consulter-mcp-invocation |
| hotspot_defect | hotspot_defect_join | ledger-consulter-hotspot-defect |
| deferred_scope_calibration | deferred_scope_poller | ledger-consulter-deferred-scope-calibration |
| guardian_exemption | post_write_audit | ledger-consulter-guardian-exemption |
| progress_eta | tools/progress_display | ledger-consulter-progress-eta |
| test_selection | post_run_audit + binder | ledger-consulter-test-selection |

Invariants: `tools/ledgers/hook_helpers.emit_ledger_event` only; fail-soft; idempotent. Rule: `.codex/rules/intelligence-ledger-family.md`. Weekly: `python ops_scripts/calibration/ledger_weekly_report.py`.

## App-agnostic core governance

**Law:** `agentic_core` = generic spine; `apps_*` customize via U0 `runtime_customization_package`. App logic in core = leakage unless documented thin adapter + migration receipt.

| Component | Owner |
|-----------|-------|
| Contracts, spine, U0 handoff, GateMesh, Exit, UWG, L6 consumer, proof infra | `agentic_core` |
| Ingress, customization package, profiles, tests, receipts | `apps_*` |

**Allowed core changes:** generic contracts, profile resolver, route interpreter, GateMesh, Exit enforcer, UWG, L6 consumer, proof infra, anti-bypass.

**Forbidden in core:** app-specific route/cache/Exit/judge/L6 logic; hardcoded `app_id` branches.

**Receipts:** `artifacts/governance/migration_receipts/<timestamp>_<change_id>.json` for boundary-sensitive core edits.

Scoped AGENTS: `agentic_core/AGENTS.md`, `apps_lic/AGENTS.md`, `apps_rg/AGENTS.md`, `apps_qna/AGENTS.md`, `apps_research/AGENTS.md`.

Rules: `agentic-core-static.md`, `agentic-core-glob-lock.md`, `apps-customization.md`, `boundary-audit-required.md`.

## Pytest plugin autoload

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` globally — prepend `-p <import-name>` in `pytest.ini` `addopts` before plugin flags. Do not duplicate `-p` for modules already loaded via `conftest.py` `pytest_plugins`. Precedent: 2026-04-30 xdist/timeout explicit `-p xdist` only.

## Apps test surfaces

Unit `tests/unit/<app>/`, integration `tests/<app>/`, contract `tests/_apps_contract/test_<app>_*.py`. No `apps_*/tests/`. Rule: `.codex/rules/apps-test-surface-taxonomy.md`, ADR-082.
