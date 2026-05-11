---
trigger: model_decision
globs: ["agentic_core/**"]
tier: 1
description: |
  Before editing any file under agentic_core/, require generic justification 
  and boundary receipt. This is a model-decision rule that activates when 
  Cascade detects agentic_core files changed.
---

# agentic_core Editing Guard

> ⛔ **Model-Decision Gate**: Before editing any `agentic_core/**` file, verify the change is generic infrastructure with proper documentation.

## When This Rule Fires

This rule activates when:
- `edit` or `write_to_file` targets a path matching `agentic_core/**`
- `multi_edit` includes `agentic_core/**` paths
- `run_command` runs scripts that modify `agentic_core/`

## Required Pre-Edit Checklist

Before any `agentic_core/` edit:

- [ ] File classification complete:
  - [ ] `GENERIC_INFRASTRUCTURE` — no app-specific refs
  - [ ] `TEMPORARY_THIN_ADAPTER` — `*_binding.py` with migration receipt
  - [ ] `CORE_APP_SPECIFIC_LEAKAGE` — must migrate, not edit in place
  
- [ ] If `TEMPORARY_THIN_ADAPTER`: migration receipt exists at `artifacts/governance/migration_receipts/`
- [ ] Change justification: "This applies to all apps_* because..."
- [ ] No hardcoded app_id checks being added
- [ ] No hardcoded apps_*/apps_rg/apps_qna literals being added
- [ ] Tests cover the generic behavior (not app-specific)

## Blocked Edits (Require Migration Instead)

These edits are **BLOCKED** — must follow `/migrate-app-binding-to-generic-core` workflow:

- Adding `if app_id == "..."` to `agentic_core/`
- Adding app-specific route name constants to `agentic_core/`
- Adding app-specific cache policy to `agentic_core/`
- Adding app-specific Exit gate lists to `agentic_core/`
- Extending `*_binding.py` with new app-specific logic

## Allowed Edits (With Receipt)

These edits are **ALLOWED** with boundary receipt:

- Extending generic profile resolver
- Adding generic contract propagation
- Adding generic GateMesh checks
- Fixing bugs in generic enforcement
- Refactoring TEMPORARY_THIN_ADAPTER toward GENERIC_READY

## Receipt Template

Required file: `artifacts/governance/migration_receipts/<timestamp>_<change_id>.json`

```json
{
  "receipt_version": "1.0",
  "change_id": "uuid",
  "timestamp": "2026-05-11T12:00:00Z",
  "agentic_core_files_changed": [
    "agentic_core/path/to/file.py"
  ],
  "classification": "GENERIC_INFRASTRUCTURE",
  "justification": "This change applies to all apps_* because...",
  "app_specific_literals_added": [],
  "tests_added_or_updated": [
    "tests/unit/agentic_core/test_*.py"
  ],
  "boundary_audit_passed": true,
  "migration_receipts_affected": [],
  "known_gaps": [],
  "author_gate_approved": true
}
```

## Enforcement

- **Local**: Pre-write hook (W3) will scan `agentic_core/` edits
- **CI**: Governance tests (W4) will fail on undocumented core changes
- **Audit**: Receipt required for any boundary-sensitive change

## Bypass

Emergency bypass: `AGENTIC_CORE_EDIT_BYPASS=1` — logs warning, proceeds.

## Related

- `.windsurf/rules/agentic-core-static.md` — Core architecture law
- `.windsurf/rules/boundary-audit-required.md` — Audit triggers
- `agentic_core/AGENTS.md` — Core boundary rules
