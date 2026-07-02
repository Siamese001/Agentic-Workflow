---
name: "source-command-core-boundary-audit"
description: "|"
---

# source-command-core-boundary-audit

Use this skill when the user asks to run the migrated source command `core-boundary-audit`.

## Command Template

# /core-boundary-audit Workflow

## Slash-Command Purpose

Run comprehensive boundary audit to classify all changed files according to the governance model and detect app-specific leakage into `agentic_core`. This is the canonical procedure for validating core/apps_* boundary integrity.

## Ordered Steps

### Step 1: Run git diff

```bash
git diff --name-only HEAD~1
git status --porcelain
```

Capture all files changed in current task/branch.

### Step 2: List Changed Files

Enumerate all files:
```python
changed_files = [
    # From git diff
]

core_files = [f for f in changed_files if f.startswith('agentic_core/')]
app_files = [f for f in changed_files if f.startswith('apps_')]
rule_files = [f for f in changed_files if f.startswith('.codex/rules/')]
skill_files = [f for f in changed_files if f.startswith('.codex/skills/')]
```

### Step 3: Classify Core Changes

For each `agentic_core/` file, classify using categories:

| Classification | Criteria | Action |
|----------------|----------|--------|
| `APPS_DECLARATIVE_CONFIG` | N/A (wrong location) | Move to apps_*/ |
| `APPS_CONTRACT` | N/A (wrong location) | Move to apps_*/ |
| `APPS_TEST` | N/A (wrong location) | Move to tests/ |
| `DOC_ALLOWED` | Documentation, generic | Allow |
| `RECEIPT_ALLOWED` | Governance receipts | Allow |
| `GENERIC_CORE_RUNTIME` | Generic spine code | Allow with receipt |
| `GENERIC_INFRASTRUCTURE` | Cross-app infrastructure | Allow with receipt |
| `TEMPORARY_THIN_ADAPTER` | *_binding.py with receipt | Allow if receipt current |
| `CORE_APP_SPECIFIC_LEAKAGE` | Hardcoded app logic | **BLOCK** |
| `MIGRATION_REQUIRED` | Identified for migration | Document |
| `MIGRATION_EXCEPTION` | Emergency exemption | Allow if approved |

### Step 4: Scan for App-Specific Leakage

Search `agentic_core/` files for forbidden patterns:

```python
FORBIDDEN_PATTERNS = {
    'app_id_branching': [
        r'if\s+app_id\s*==\s*["\']apps_\w+["\']',
        r'app_id\s*==\s*["\']apps_\w+["\']',
    ],
    'hardcoded_app_names': [
        r'["\']apps_lic["\']',
        r'["\']apps_rg["\']',
        r'["\']apps_qna["\']',
        r'["\']apps_research["\']',
    ],
    'app_specific_routes': [
        r'R4_MANAGED_DRAFT',
        r'R3R4_MANAGED_RESEARCH_THEN_DRAFT',
        r'R1_RESUME_GENERATION',
    ],
    'app_specific_cache': [
        r'final_draft_r1a_bypass',
        r'final_draft_r1b_bypass',
        r'linkedin_send',
        r'email_outbox_send',
    ],
    'app_specific_gates': [
        r'APPS_LIC_EXIT_GATES',
        r'APPS_RG_EXIT_GATES',
        r'G21_APPS_LIC_SPECIFIC',
    ],
}
```

Log each finding with file, line number, pattern type.

### Step 5: Write Receipt

Generate boundary receipt:

```json
{
  "receipt_version": "1.0",
  "audit_id": "<uuid>",
  "timestamp": "<ISO8601>",
  "workflow": "/core-boundary-audit",
  
  "changed_files": {
    "all": [...],
    "agentic_core": [...],
    "apps_lic": [...],
    "apps_rg": [...],
    "apps_qna": [...],
    "apps_research": [...]
  },
  
  "classifications": {
    "agentic_core/file.py": "GENERIC_INFRASTRUCTURE",
    "...": "TEMPORARY_THIN_ADAPTER"
  },
  
  "forbidden_literals_found": [
    {
      "file": "agentic_core/L0_routing/selector.py",
      "line": 42,
      "pattern": "app_id == 'apps_lic'",
      "classification": "CORE_APP_SPECIFIC_LEAKAGE"
    }
  ],
  
  "receipts_verified": [
    {
      "file": "agentic_core/L0_routing/apps_lic_l0_binding.py",
      "receipt_path": "artifacts/governance/migration_receipts/...",
      "current": true
    }
  ],
  
  "outcome": "ALLOW|ALLOW_WITH_GENERIC_REFACTOR|BLOCK_MOVE_TO_APPS_CONFIG|BLOCK_ROLLBACK_REQUIRED",
  
  "action_required": "...",
  "next_steps": [...],
  
  "verification": {
    "boundary_audit_passed": true|false,
    "leakage_detected": true|false,
    "receipts_valid": true|false
  }
}
```

## Files Inspected

| File Pattern | Purpose |
|--------------|---------|
| `agentic_core/**/*.py` | Core Python files |
| `agentic_core/**/*.yaml` | Core YAML configs |
| `agentic_core/**/apps_*_*.py` | App-specific bindings |
| `.codex/rules/*.md` | Rule changes |
| `.codex/skills/**/SKILL.md` | Skill changes |
| `apps_*/**` | App files (for reference) |

## Classification Categories

Full category set used:

- `APPS_DECLARATIVE_CONFIG` — App profiles belong in apps_*/
- `APPS_CONTRACT` — App contracts belong in apps_*/
- `APPS_TEST` — App tests belong in tests/
- `DOC_ALLOWED` — Generic documentation
- `RECEIPT_ALLOWED` — Governance receipts
- `GENERIC_CORE_RUNTIME` — Generic spine
- `GENERIC_INFRASTRUCTURE` — Cross-app infra
- `TEMPORARY_THIN_ADAPTER` — Bindings with receipts
- `CORE_APP_SPECIFIC_LEAKAGE` — Leakage requiring migration
- `MIGRATION_REQUIRED` — Scheduled for W5
- `MIGRATION_EXCEPTION` — Emergency approved

## Expected Receipt

Path:
```
artifacts/governance/boundary_receipts/<timestamp>_<audit_id>.json
```

## Stop Conditions

This workflow **STOPS** (blocks) when:

- `CORE_APP_SPECIFIC_LEAKAGE` detected without migration plan
- New `if app_id == "..."` added to core
- New app-specific constants added to core
- `TEMPORARY_THIN_ADAPTER` lacks current receipt
- Receipt validation fails
- User explicitly cancels

## Success Criteria

- [ ] All files classified
- [ ] Core files scanned for leakage
- [ ] Forbidden literals identified or none found
- [ ] Receipts verified for temporary adapters
- [ ] Outcome determined
- [ ] Receipt written to canonical path
- [ ] No blocking leakage detected

## Output

```
CORE_BOUNDARY_AUDIT: outcome=<OUTCOME>, receipt=<path>, leakage=<count>
```

## Related

- Skill: `core-boundary-audit`
- Rule: `.codex/rules/boundary-audit-required.md`
- Rule: `.codex/rules/agentic-core-glob-lock.md`

## MANUAL MIGRATION REQUIRED

Migrated from source command `core-boundary-audit` into a Codex skill. Invoke it as `$source-command-core-boundary-audit` and manually rewrite any slash-command behavior that depended on provider-specific runtime expansion.

Review unsupported command metadata manually: `slash_command`, `tier`, `version`, `workflow_id`.
