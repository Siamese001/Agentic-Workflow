# Windsurf Deprecation Inventory - 2026-06-07

Plan: `.cursor/plans/windsurf-deprecation-cursor-ssot-b6e4a9.md`

## Snapshot

Initial file-class inventory of `.windsurf/**`:

| Class | Count | Target State |
|-------|-------|--------------|
| `.windsurf/plans` | 544 | Historical archive or deletion after duplicate/provenance review |
| `.windsurf/scripts` | 165 | Migrate live tools to `.cursor/scripts`, `ops_scripts`, or `tools`; delete legacy copies |
| `.windsurf/skills` | 76 | `.cursor/skills` is SSOT; delete legacy copies after gap check |
| `.windsurf/rules` | 56 | `.cursor/rules/*.mdc` is SSOT; delete legacy copies after parity check |
| `.windsurf/schemas` | 54 | `.cursor/schemas` is SSOT; live loaders/tests must not read `.windsurf/schemas` |
| `.windsurf/state` | 32 | `.cursor/state` or `artifacts/cursor` for retained state; otherwise delete |
| `.windsurf/workflows` | 25 | Migrate to `.cursor/skills` or retire |
| `.windsurf/templates` | 2 | `.cursor/templates` is SSOT |
| `.windsurf/reminders` | 1 | Archive or delete |
| Root `.windsurf` files | 3 | `hooks.json`, `mcp_config.json`, `RULES_INDEX.md` are deprecated |

## Implemented In This Pass

- Root `AGENTS.md` now names `.cursor/mcp.json` and `.cursor/rules/*.mdc` as SSOT.
- Notion DB routing metadata no longer calls `.windsurf/rules` or `.windsurf/mcp_config.json` authoritative.
- Author-Gate schema loader and renderer read `.cursor/schemas`.
- Ledger schema registry reads `.cursor/schemas` and points hook/skill references at Cursor paths.
- Focused ledger tests seed SQLite fixtures from `.cursor/schemas`.
- Governance artifact append helpers write `artifacts/cursor` only.
- MCP parity/sovereignty gates validate Cursor SSOT without requiring Windsurf peers.
- `check_no_active_windsurf_changes.py` blocks staged active `.windsurf` workflow edits.
- Legacy scripts needed for provenance fallback were copied to `.cursor/scripts/_legacy_windsurf`.
- The complete legacy tree was archived to `docs/archive/windsurf/legacy-tree`.
- Active references were migrated to Cursor or archive paths with `tools/migration/deprecate_windsurf_refs.py`.
- The live `.windsurf` directory was deleted after readiness passed.

## Closeout State

`check_windsurf_deletion_readiness.py` reports:

```json
{
  "deletion_safe": true,
  "blockers": []
}
```

Retained Windsurf-era material is archive-only:

| Path | Purpose |
|------|---------|
| `docs/archive/windsurf/legacy-tree` | Full historical tree archive from before deletion |
| `.cursor/scripts/_legacy_windsurf` | Compatibility/provenance copy of legacy script helpers |

No live `.windsurf` directory remains.

## Verification

- `python ops_scripts/ci/check_windsurf_deletion_readiness.py`
- `python ops_scripts/ci/check_no_active_windsurf_changes.py`
- `python ops_scripts/ci/check_mcp_sync_integrity.py`
- `python ops_scripts/ci/check_mcp_editor_parity.py`
- `python ops_scripts/ci/check_mcp_config_sovereignty.py`
- `python ops_scripts/ci/check_skill_frontmatter.py`
- `PYTHONPATH=. python ops_scripts/ci/check_plan_format_compliance.py --strict --paths .cursor/plans/windsurf-deprecation-cursor-ssot-b6e4a9.md`
- `python -m py_compile` on the touched migration/check/schema/ledger scripts
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout -q tests/unit/agentic_core/L2_execution/healers/test_l2_cascade_router_ledger.py tests/unit/agentic_core/L0_routing/reasoning/test_l0_path_agentic_closed_loop.py tests/unit/agentic_core/L0_routing/reasoning/test_namespace_bandit_closed_loop.py` (`50 passed`)
