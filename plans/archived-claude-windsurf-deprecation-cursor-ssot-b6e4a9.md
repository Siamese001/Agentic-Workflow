---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\windsurf-deprecation-cursor-ssot-b6e4a9.md'
original_relative_path: 'windsurf-deprecation-cursor-ssot-b6e4a9.md'
source_sha256: b042753d414fe426f6f37374929fbb2e11788fe2fcc5eac5ebdb220091945aec
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: windsurf-deprecation-cursor-ssot-b6e4a9
plan_type: governance
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: true
touches_plan_templates: true
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Windsurf deprecation to Cursor SSOT

Deprecate all active `.windsurf` workflow surfaces - plans, skills, workflows, rules, hooks, scripts, schemas, state, templates, reminders, indexes, and `AGENTS.md` references - so Cursor is the only active governance and agent workflow SSOT.

> **plan_id discipline:** `plan_id` = filename stem `windsurf-deprecation-cursor-ssot-b6e4a9`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W6
LAST_COMPLETED_WAVE: W6
LAST_UPDATED: 2026-06-07

PLAN_CREATED: slug=windsurf-deprecation-cursor-ssot-b6e4a9 path=.cursor/plans/windsurf-deprecation-cursor-ssot-b6e4a9.md status=Not Started
PLAN_COMPLETE: plan=windsurf-deprecation-cursor-ssot-b6e4a9 note="Live .windsurf tree deleted after archive, active references migrated to Cursor/archive paths, and deletion readiness plus focused governance/tests passed."

---

## Context (SCQA)

- **Situation** - Root `AGENTS.md` and Cursor governance now identify `.cursor/**` as the active SSOT for rules, skills, hooks, MCP routing, and plans.
- **Complication** - The repo still contains a large `.windsurf/**` tree and many active references to it. Initial inventory on 2026-06-07 found 958 `.windsurf` files: 544 plans, 165 scripts, 76 skills, 56 rules, 54 schemas, 32 state files, 25 workflows, 2 templates, 1 reminder, `hooks.json`, `mcp_config.json`, and `RULES_INDEX.md`. Repo-wide search also found runtime/config/test references to `.windsurf/schemas`, `.windsurf/scripts`, `.windsurf/plans`, and `.windsurf/rules`.
- **Question** - How do we deprecate Windsurf artifacts without breaking runtime schema loads, historical plan provenance, hook behavior, or governance CI?
- **Answer** - Execute an inventory-first, staged deprecation: freeze new `.windsurf` writes, migrate active runtime dependencies to Cursor or neutral repo locations, archive historical plans and docs, replace agent guidance with Cursor-only instructions, then add enforcement that blocks reintroduction except for explicitly approved historical archives.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1-W0.4 | Registration, baseline inventory, risk ledger | ~6k | Notion Plans row can be registered before execution | DONE | Inventory receipt exists; Notion registration writeback unavailable in this Codex session |
| W1 | W1.1-W1.5 | Freeze and guidance update | ~8k | Cursor rules remain active SSOT | DONE | Agents/docs say `.windsurf` is deprecated; staged guard blocks new active `.windsurf` workflow edits |
| W2 | W2.1-W2.6 | Runtime dependency migration | ~16k | Schemas/scripts used by tests and runtime can move to neutral `tools/`, `config/`, or `.cursor/` paths | DONE | Schema, governance log, MCP gate, and focused test consumers migrated |
| W3 | W3.1-W3.5 | Plan and provenance archive | ~12k | Historical plans can be archived without Notion row mutation unless separately approved | DONE | Legacy plan tree archived under `docs/archive/windsurf/legacy-tree`; `.cursor/plans` remains executable SSOT |
| W4 | W4.1-W4.5 | Skills, workflows, hooks, rules retirement | ~14k | Cursor equivalents exist or can be created as redirect/deprecation stubs | DONE | No active agent procedure requires `.windsurf/skills`, `.windsurf/workflows`, `.windsurf/rules`, or `.windsurf/hooks.json` |
| W5 | W5.1-W5.4 | Config, state, reminders, docs cleanup | ~10k | `.cursor/mcp.json` is the only MCP config SSOT | DONE | Legacy config/state/reminder/template/index files archived, and live `.windsurf` removed |
| W6 | W6.1-W6.4 | Verification and deletion/archive closeout | ~8k | Prior waves completed or deferred with markers | DONE | Search, tests, governance checks, and closeout receipt prove Cursor-only active governance |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Register plan in Notion Plans DB before wave execution | DEFERRED - Notion MCP unavailable in this Codex session |
| W0.2 | Generate full `.windsurf/**` inventory with hashes, file classes, and last-modified dates | DONE |
| W0.3 | Classify each reference as runtime dependency, test fixture, governance instruction, historical citation, or ignored noise | DONE |
| W0.4 | Build retention matrix: migrate, archive, delete, compatibility-only, or defer | DONE |
| W1.1 | Update root `AGENTS.md` Windsurf language from mirror/SSOT to deprecated legacy/compatibility-only | DONE |
| W1.2 | Update `.cursor/rules/**` and `.cursor/skills/**` instructions that still point to `.windsurf` as active | DONE |
| W1.3 | Add a guard that blocks new `.windsurf/plans`, `.windsurf/skills`, `.windsurf/workflows`, `.windsurf/rules`, and `.windsurf/hooks.json` changes | DONE |
| W1.4 | Allow only approved archive paths and compatibility files through the guard | DONE |
| W1.5 | Emit freeze receipt listing allowed remaining `.windsurf` classes | DONE |
| W2.1 | Move canonical schemas from `.windsurf/schemas` to durable config/schema locations | DONE - `.cursor/schemas` already populated and now used by patched consumers |
| W2.2 | Update schema loaders, tests, comments, and generated docs to use new schema paths | DONE |
| W2.3 | Migrate still-used `.windsurf/scripts` functionality to `tools/cursor`, `tools/governance`, or other existing tool namespaces | DONE |
| W2.4 | Replace `tools/windsurf/*` names or mark them compatibility wrappers around Cursor-native modules | DONE |
| W2.5 | Update tests that read `.windsurf` fixtures to use copied fixtures or neutral schema paths | DONE |
| W2.6 | Run focused tests for author-gate schemas, ledgers, plan lifecycle, and routing calibration | DONE |
| W3.1 | Compare `.windsurf/plans` with `.cursor/plans` and identify duplicate, missing, and historical-only plans | DONE |
| W3.2 | Move historical-only plans to an explicit archive or delete after provenance review | DONE |
| W3.3 | Replace active plan references with `.cursor/plans` equivalents where they exist | DONE |
| W3.4 | Convert surviving historical plan citations to archive citations or neutral "legacy plan ref" text | DONE |
| W3.5 | Confirm `.cursor/plans` remains the only executable plan location | DONE |
| W4.1 | Map `.windsurf/skills/*` to `.cursor/skills/*` equivalents and identify gaps | DONE |
| W4.2 | Retire or migrate `.windsurf/workflows/*`, including structured-reasoning and Tavily workflows | DONE |
| W4.3 | Retire `.windsurf/rules/*` after Cursor `.mdc` equivalents are verified | DONE |
| W4.4 | Remove `.windsurf/hooks.json` from active dispatch and migrate any unique hook coverage | DONE |
| W4.5 | Regenerate Cursor rules/skills indexes and verify no Windsurf active-procedure drift | DONE |
| W5.1 | Decide final status of `.windsurf/mcp_config.json`: delete, archive, or compatibility-only generated mirror | DONE - archived, not retained live |
| W5.2 | Migrate `.windsurf/state` data needed by current tools to `artifacts/`, `.cursor/state`, or durable DB locations | DONE |
| W5.3 | Archive or delete `.windsurf/templates`, `.windsurf/reminders`, and `.windsurf/RULES_INDEX.md` | DONE |
| W5.4 | Update docs, reports, config comments, and generated blocks that still call `.windsurf` a filesystem SSOT | DONE |
| W6.1 | Run repo-wide `rg` verification for `.windsurf`, `Windsurf`, and `windsurf` | DONE |
| W6.2 | Run governance checks for Cursor native config, rules index, plan format, and hook wiring | DONE |
| W6.3 | Run focused unit tests for migrated schemas/scripts plus any touched runtime paths | DONE |
| W6.4 | Produce closeout receipt with removed, migrated, retained, and deferred files | DONE |

---

## Deprecation Policy

### Active SSOT

| Surface | Active SSOT after this plan | Windsurf target state |
|---------|-----------------------------|-----------------------|
| Agent guidance | `AGENTS.md` + `.cursor/rules/*.mdc` | No active instruction role |
| Plans | `.cursor/plans/*.md` | Historical archive or deletion |
| Skills | `.cursor/skills/*/SKILL.md` | Deleted after gap check or archived as provenance |
| Workflows | `.cursor/skills/*` or documented tool procedure | Deleted after migration |
| Hooks | `.cursor/hooks.json` + `.cursor/hooks/**` | Deleted after coverage parity |
| MCP config | `.cursor/mcp.json` | Compatibility-only mirror or deleted |
| Schemas | `config/**`, `tools/**`, or package-local schema directory | Deleted after consumers migrate |
| Scripts | `tools/**` or `.cursor/hooks/**` | Deleted or compatibility wrapper removed |
| State | `artifacts/**`, DB, or generated cache ignored by git | Deleted or migrated |
| Rules index | `.cursor/RULES_INDEX.md` | Deleted |

### Retention Rules

- No `.windsurf` file may remain authoritative after W6.
- Any retained `.windsurf` path must be listed in the closeout receipt with owner, reason, expiry, and guard allowlist entry.
- Historical citations to old plans are allowed only when they are clearly labeled legacy provenance and do not instruct agents to execute from `.windsurf`.
- Runtime/test code must not load schemas, configs, or executable scripts from `.windsurf` after W2 unless a compatibility shim is explicitly time-boxed.
- The implementation must not bulk-delete before inventory and migration receipts exist.

---

## Initial Inventory Snapshot

Captured 2026-06-07 with `rg --files .windsurf` and a file-class count.

| Class | Count | Notes |
|-------|-------|-------|
| `.windsurf/plans` | 544 | Largest surface; includes active-looking historical plans and `_archive` subtrees |
| `.windsurf/scripts` | 165 | Several active references from tools and hook/audit code |
| `.windsurf/skills` | 76 | Includes MCP stubs, structured reasoning, testing, author-gate, graph analysis |
| `.windsurf/rules` | 56 | Cursor `.mdc` equivalents must be verified before deletion |
| `.windsurf/schemas` | 54 | Active runtime/test consumers found; migrate before deletion |
| `.windsurf/state` | 32 | Includes plan registration cache and marker/state files |
| `.windsurf/workflows` | 25 | Agent workflow procedures; migrate or retire |
| `.windsurf/templates` | 2 | Plan and skill templates |
| `.windsurf/reminders` | 1 | Historical reminder |
| Root `.windsurf` files | 3 | `hooks.json`, `mcp_config.json`, `RULES_INDEX.md` |

---

## Verification Commands

Run from repo root after each relevant wave.

```bash
python ops_scripts/ci/check_windsurf_deletion_readiness.py
python ops_scripts/ci/check_no_active_windsurf_changes.py
python ops_scripts/ci/check_mcp_sync_integrity.py
python ops_scripts/ci/check_mcp_editor_parity.py
python ops_scripts/ci/check_mcp_config_sovereignty.py
python ops_scripts/ci/check_skill_frontmatter.py
python .cursor/scripts/check_cursor_native_config.py
python .cursor/scripts/generate_rules_index.py --check
python ops_scripts/ci/check_plan_format_compliance.py --strict --paths .cursor/plans/windsurf-deprecation-cursor-ssot-b6e4a9.md
```

Focused tests are selected after W0 inventory, but must include all touched schema loaders, plan lifecycle code, hook dispatch code, and runtime consumers that previously read `.windsurf/**`.

Closeout verification on 2026-06-07 additionally ran:

```bash
python -m py_compile tools/migration/deprecate_windsurf_refs.py ops_scripts/ci/check_windsurf_deletion_readiness.py ops_scripts/ci/check_no_active_windsurf_changes.py ops_scripts/ci/check_mcp_editor_parity.py ops_scripts/ci/check_mcp_config_sovereignty.py ops_scripts/ci/check_cursor_governance_mirror_health.py ops_scripts/ci/check_skill_frontmatter.py ops_scripts/ci/check_decision_required.py ops_scripts/ci/check_agentic_core_addition.py ops_scripts/ci/_governance_paths.py .cursor/scripts/sync_mcp_config.py tools/author_gate/schema_loader.py tools/author_gate/render_template.py tools/ledgers/schema_registry.py tools/ledgers/_bootstrap_skills.py tools/ledgers/writer.py tools/ledgers/router_helper.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout -q tests/unit/agentic_core/L2_execution/healers/test_l2_cascade_router_ledger.py tests/unit/agentic_core/L0_routing/reasoning/test_l0_path_agentic_closed_loop.py tests/unit/agentic_core/L0_routing/reasoning/test_namespace_bandit_closed_loop.py
```

---

## Acceptance Criteria

- Root `AGENTS.md` no longer calls `.windsurf/rules` a filesystem SSOT or `.windsurf/mcp_config.json` an active mirror unless compatibility-only with expiry is explicitly documented.
- `.cursor/**` is the only active location for plans, rules, skills, hooks, and MCP procedure.
- No production code or tests require `.windsurf/schemas` or `.windsurf/scripts` as canonical inputs.
- New `.windsurf` workflow artifacts are blocked by CI or hook checks, except explicitly allowlisted archive/compatibility paths.
- Repo-wide search has no unclassified `.windsurf` references.
- Closeout receipt lists every migrated, archived, deleted, retained, and deferred artifact class.

---

## Out Of Scope

- Changing product behavior in `agentic_core`, `apps_rg`, or app packages except path migrations required to remove `.windsurf` dependencies.
- Rewriting historical plan content beyond relocation, citation updates, or archive headers.
- Deleting user or generated worktree changes unrelated to this deprecation effort.
- Notion bulk status reconciliation unless separately authorized after filesystem deprecation is complete.

---

## Risks

| Risk | Mitigation |
|------|------------|
| Runtime code loads `.windsurf/schemas` | W2 migrates schemas first and runs focused tests before deletion |
| Historical plan provenance is lost | W3 archives or preserves citations before removing executable plan status |
| Hooks lose coverage during rename | W4 requires hook parity receipt and focused hook tests |
| Search remains noisy because old comments cite `.windsurf/plans` | W3/W5 classify historical citations separately from active instructions |
| Compatibility mirror becomes permanent | W6 closeout requires owner, expiry, and allowlist entry for every retained path |

---

## Open Decisions

1. CLOSED - `.windsurf/mcp_config.json` was archived under `docs/archive/windsurf/legacy-tree` and removed from the live tree.
2. CLOSED - historical `.windsurf/plans` were preserved under `docs/archive/windsurf/legacy-tree/plans`; executable plan SSOT remains `.cursor/plans`.
3. CLOSED - schemas remain under `.cursor/schemas` for this deprecation pass, with consumers migrated away from `.windsurf/schemas`.
4. CLOSED - legacy Windsurf script behavior needed for provenance was copied to `.cursor/scripts/_legacy_windsurf`; active callers now use Cursor/archive paths.

---

## Closeout Receipt

| Class | Final State | Notes |
|-------|-------------|-------|
| Live `.windsurf/**` | DELETED | Removed after `check_windsurf_deletion_readiness.py` returned `deletion_safe: true` |
| Historical legacy tree | ARCHIVED | Preserved at `docs/archive/windsurf/legacy-tree` |
| Legacy scripts | COMPATIBILITY ARCHIVE | Preserved at `.cursor/scripts/_legacy_windsurf` for historical/provenance fallback only |
| Schemas | MIGRATED | Active consumers read `.cursor/schemas` |
| MCP config | MIGRATED | `.cursor/mcp.json` is the only active MCP SSOT |
| Plans | MIGRATED/ARCHIVED | `.cursor/plans` is executable SSOT; legacy plans are archive-only |
| Skills, rules, hooks, workflows | RETIRED | Cursor rules, skills, and hooks are active; legacy copies are archive-only |
| Enforcement | ACTIVE | `ops_scripts/ci/check_no_active_windsurf_changes.py` blocks staged active `.windsurf` workflow reintroduction |

Deferred external writeback: Notion Plans registration/status update could not be performed because the Notion MCP was not available in this Codex session.
