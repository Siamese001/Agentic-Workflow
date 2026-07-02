# Path Validation Checklist

Run all five checks before writing any artifact. A single failure = STOP.

## Checklist

1. **Repository root** — path starts with `c:\Git\Agentic-Workflow\` (or equivalent REPO_ROOT)
2. **Whitelist** — first path component is in PROJECT_ROOT_WHITELIST:
   `agentic_core`, `apps_rg`, `apps_lic`, `apps_shared`, `ops_scripts`, `tests`, `docs`, `data`, `tools`, `artifacts`, `system_learning`, `plans`, `.codex`
3. **Artifact type match** — file type maps to canonical directory (see `artifact_type_resolver.md`)
4. **No IDE-system paths** — path does not contain `.cursor/`, `.vscode/`, `C:\Users\`
5. **No conflict** — will not silently overwrite an existing canonical artifact

## Canonical Quick Reference

| Artifact Type | Canonical Path |
|---|---|
| Plans | `plans/` |
| Evidence / RCAs | `docs/reports/` or `artifacts/` |
| Architecture docs | `docs/architecture/` |
| Telemetry reports | `docs/reports/telemetry/` |
| Freeze reports | `data/freeze_reports/` |
| Test files | `tests/<category>/` |
| CI scripts | `ops_scripts/ci/` |

## Forbidden Patterns

- `docs/reports/plans/` — for evidence/reports only, never plans
- `.codex/plans/` — archive-only, never new active plans
- Any absolute user-home path
- Any path outside the repository root
