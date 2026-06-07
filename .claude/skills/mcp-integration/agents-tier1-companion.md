# AGENTS.md Tier-1 companion (procedural SSOT)

> **Moved from root `AGENTS.md` in W1** (`cursor-governance-two-tier-b4e8f2`) per Option A.  
> Tier-1 `AGENTS.md` keeps invariants + autogen tables; this file holds procedural detail.  
> **Edit SSOT for rules:** `.claude/rules/*.mdc` only — Windsurf rules mirror is read-only (see repo `windsurf/rules/README.md`).

## Notion — filesystem SSOT vs Notion rows

| Content | Canonical Path | Notion Mirror? |
|---------|----------------|----------------|
| Rules | `.claude/rules/*.mdc` | NO (archived 2026-05-02) |
| ADRs | `docs/architecture/adr/*.md` | NO |
| Plans | `.claude/plans/<slug>-<6hex>.md` | Plans DB row only |
| Calibration | `docs/reports/calibration/<YYYY-Www>.md` | NO |

Do not sync rules or ADRs to Notion. Archived DBs: MCP Registry, Constitutional Rules, SC/AP Violations, ADR Registry, Author-Gate Ledger, Anti-Pattern Burndown — see `.claude/rules/notion-archived-databases.md`.

### Plans + Backlog taxonomy

Five-status taxonomy, Plans invariants, Backlog Snapshot (`34b27693-f55c-81b4-93ba-efec5755a20e`, `python tools/notion/snapshot_renderer.py --regenerate`): **`.claude/rules/notion-plans-taxonomy.md`**.

### Auto-routing (proactive)

| Event | Filesystem | Notion |
|-------|------------|--------|
| New plan `.claude/plans/<slug>-<6hex>.md` | Plan markdown | Plans DB via `tools.notion.plan_creation_helper.create_plan_in_notion` — Status **Not Started** |
| New ADR `docs/architecture/adr/` | Markdown SSOT | No write |
| Edit `.mcp.json` | JSON SSOT | No write; run `python .claude/governance/scripts/sync_mcp_config.py` |
| Author-Gate decision | `.claude/state/refactor_decisions/*.sqlite` | No write (ledger archived) |
| ADG SC/AP defects | `artifacts/adg/*.sqlite` | No write |
| Wave start | n/a | Emit `WAVE_START: plan=<slug-6hex> wave=<N>` + `python tools/windsurf/wave_execution_state.py start` / `wave-progress` |
| Wave complete | Plan table (hook) | Emit `WAVE_COMPLETE: plan=<slug-6hex> wave=<N> note="..."` |

Full wave lifecycle: `.claude/rules/plan-lifecycle-procedures.md`, `.claude/rules/wave-completion-discipline.md`.

## MCP sync enforcement

| Gate | Command |
|------|---------|
| Strict sync | `python ops_scripts/ci/check_mcp_sync_integrity.py` |
| Coverage | `python ops_scripts/ci/check_agents_mcp_coverage.py` |
| Editor parity | `python ops_scripts/ci/check_mcp_editor_parity.py` |
| Cursor SSOT check | `python .claude/governance/scripts/sync_mcp_config.py --check` |

Regenerate: `python .claude/governance/scripts/sync_mcp_config.py` (refreshes AGENTS autogen blocks + global MCP copy).

## Intelligence ledgers (ADR-050)

Ten SQLite ledgers under `artifacts/ledgers/`. Consult via `LedgerConsulter("<name>").lookup(...)` before acting.

| Ledger | Writer | Consulting skill |
|--------|--------|------------------|
| tool_routing | post_cursor_agent_adg_audit | ledger-consulter-tool-routing |
| refactor_outcome | post_commit_outcome_binder | ledger-consulter-refactor-outcome |
| prompt_classifier | pre_prompt_classifier + binder | ledger-consulter-prompt-classifier |
| mcp_invocation | post_mcp_audit | ledger-consulter-mcp-invocation |
| hotspot_defect | hotspot_defect_join | ledger-consulter-hotspot-defect |
| deferred_scope_calibration | deferred_scope_poller | ledger-consulter-deferred-scope-calibration |
| guardian_exemption | post_write_audit | ledger-consulter-guardian-exemption |
| progress_eta | tools/progress_display | ledger-consulter-progress-eta |
| memory_recall | post_cursor_agent_writeback_audit | ledger-consulter-memory-recall |
| test_selection | post_run_audit + binder | ledger-consulter-test-selection |

Invariants: `tools/ledgers/hook_helpers.emit_ledger_event` only; fail-soft; idempotent. Rule: `.claude/rules/intelligence-ledger-family.md`. Weekly: `python ops_scripts/calibration/ledger_weekly_report.py`.

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

Unit `tests/unit/<app>/`, integration `tests/<app>/`, contract `tests/_apps_contract/test_<app>_*.py`. No `apps_*/tests/`. Rule: `.claude/rules/apps-test-surface-taxonomy.md`, ADR-082.
