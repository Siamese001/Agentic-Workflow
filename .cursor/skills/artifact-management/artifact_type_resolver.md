# Artifact Type Resolver

Maps artifact types to their canonical SSOT directories.

## Canonical Mappings

| Artifact Type | Canonical Directory | Notes |
|---|---|---|
| Execution plans | `.cursor/plans/` | Naming: `<name>-<6hex>.md` |
| RCA documents | `.cursor/plans/` | Same dir as plans |
| Evidence files | `.cursor/plans/` | One per phase |
| Governance reports | `.cursor/plans/` | |
| Architecture docs | `docs/architecture/` | ADRs in `docs/architecture/adr/` |
| Telemetry reports | `docs/reports/telemetry/` | |
| Freeze reports | `data/freeze_reports/` | |
| Test files | `tests/<category>/` | Match existing test directory structure |
| CI scripts | `ops_scripts/ci/` | |
| ADG artifacts | `artifacts/adg/` | SQLite, JSON snapshots |
| Memory artifacts | `artifacts/memory/` | SQLite only |

## Resolution Algorithm

1. Identify artifact type from content / filename
2. Look up canonical directory above
3. Verify path is under repository root
4. Verify first component is in PROJECT_ROOT_WHITELIST
5. If no match found → STOP, ask user for target directory

## Forbidden Locations

- `docs/reports/plans/` — reports directory, not plans
- `C:\Users\*` — user-home paths never receive project artifacts
- `.cursor/`, `.vscode/` — IDE system directories
