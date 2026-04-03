---
name: ssot-write-gate
description: Validates artifact target paths against SSOT sovereign territories before any file write. Use before writing any .md, .json, or .py artifact to disk. Blocks writes to user home directories, paths outside PROJECT_ROOT_WHITELIST, or any non-SSOT location. Resolves canonical paths by artifact type.
enforcement_layer: pre-commit
enforcement_timing: after_work
enforcement_type: structural
---

# SSOT Write Gate Skill

Validates every artifact write target against SSOT sovereign territories before the write executes.

## Files

- **`path_validation_checklist.md`** — Pre-write checklist. Given a target path, validates: (1) path is inside repository root, (2) root folder is in PROJECT_ROOT_WHITELIST, (3) artifact type maps to correct SSOT directory. BLOCKS write if any check fails.

- **`artifact_type_resolver.md`** — Lookup table mapping artifact type → canonical SSOT path. Plans → `.windsurf/plans/`. Evidence → `.windsurf/plans/`. Telemetry → `docs/reports/telemetry/`. Freeze reports → `data/freeze_reports/`. Governance → `docs/reports/governance/`.

## When to use

- Before writing ANY `.md` plan, report, or evidence file
- Before writing ANY `.json` artifact, registry, or snapshot
- Before writing ANY `.py` script to a directory not yet confirmed as SSOT-approved
- When a path contains `C:\Users\`, or any absolute user-home path

## Path Validation Rules (ALL must pass)

1. **Repository root check** — Path MUST be under `c:\Git\Agentic-Workflow\`
2. **Whitelist check** — First path component MUST be in `PROJECT_ROOT_WHITELIST`:
   `agentic_core`, `apps_rg`, `apps_lic`, `apps_shared`, `ops_scripts`, `tests`, `docs`, `data`, `tools`, `artifacts`, `system_learning`, `.windsurf`
3. **Artifact type check** — Artifact type MUST match canonical directory per `artifact_type_resolver.md`
4. **No user-home paths** — NEVER write to paths under `C:\Users\<username>\`

## Canonical Paths Quick Reference

| Artifact Type | Canonical Path |
|---|---|
| Plans / evidence / RCAs | `.windsurf/plans/` |
| Governance reports | `docs/reports/governance/` |
| Telemetry | `docs/reports/telemetry/` |
| Freeze reports | `data/freeze_reports/` |
| Architecture docs | `docs/architecture/` |
| Test files | `tests/<category>/` |

## Constitutional Requirements Enforced

- **§8:** All plans and reports MUST reside in `.windsurf/plans/`
- **§2.1:** Evidence files MUST be within repository sovereign territories
- **IDE system paths:** `.windsurf/plans/`, `.windsurf/skills/`, `.windsurf/workflows/`
