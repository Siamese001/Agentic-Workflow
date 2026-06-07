---
name: core-boundary-audit
description: |
  Use when auditing files in agentic_core to detect app-specific leakage.
  Validates governance compliance and boundary integrity.
---

# Core Boundary Audit Skill

## Purpose

Audit files changed in a task to classify them according to the governance model and detect app-specific leakage into `agentic_core`.

This skill enforces the core architecture law: **Apps customize inputs. Core enforces contracts.**

## When to Use

Invoke this skill when:
- Any `agentic_core/**` file is modified
- A PR touches both `agentic_core/` and `apps_*/`
- New binding files are added
- App-specific literals appear in core
- Before claiming task completion on core-boundary work
- `/core-boundary-audit` workflow is triggered

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `changed_files` | List[str] | Yes | Files modified in current task |
| `baseline_audit_path` | str | No | Path to W0 baseline audit JSON |
| `existing_receipts_dir` | str | No | `artifacts/governance/migration_receipts/` |

## Steps

### Step 1: List Changed Files

```python
git diff --name-only HEAD~1  # or task branch
git status --porcelain
```

Identify all files in `agentic_core/` that were touched.

### Step 2: Classify Each File

For each `agentic_core/` file, classify using:

| Classification | Criteria | Action |
|----------------|----------|--------|
| `APPS_DECLARATIVE_CONFIG` | App YAML/JSON profiles | Not applicable - these belong in `apps_*/` |
| `APPS_CONTRACT` | App ingress contracts | Not applicable - these belong in `apps_*/` |
| `APPS_TEST` | App test files | Not applicable - these belong in `tests/` |
| `DOC_ALLOWED` | Documentation files | Allowed in core if generic |
| `RECEIPT_ALLOWED` | Migration receipts | Allowed in `artifacts/governance/` |
| `GENERIC_CORE_RUNTIME` | Generic spine code | Allowed with receipt |
| `GENERIC_INFRASTRUCTURE` | Cross-app infrastructure | Allowed with receipt |
| `TEMPORARY_THIN_ADAPTER` | `*_binding.py` with receipt | Allowed if receipt current |
| `CORE_APP_SPECIFIC_LEAKAGE` | Hardcoded app logic | **BLOCK - requires migration** |
| `MIGRATION_REQUIRED` | Identified for W5 | Document for migration |
| `MIGRATION_EXCEPTION` | Emergency exemption | Allowed if approved + deadline |

### Step 3: Scan for Forbidden Literals

Search `agentic_core/` changed files for:

```python
FORBIDDEN_PATTERNS = [
    r'if\s+app_id\s*==\s*["\']apps_\w+["\']',
    r'app_id\s*==\s*["\']apps_\w+["\']',
    r'["\']apps_lic["\']',
    r'["\']apps_rg["\']',
    r'["\']apps_qna["\']',
    r'R4_MANAGED_DRAFT',  # app-specific route names
    r'R3R4_MANAGED_RESEARCH_THEN_DRAFT',
    r'final_draft_r1a_bypass',
    r'final_draft_r1b_bypass',
    r'linkedin_send',
    r'email_outbox_send',
]
```

### Step 4: Verify Receipts

For `TEMPORARY_THIN_ADAPTER` files:
- Check receipt exists at `artifacts/governance/migration_receipts/`
- Verify receipt is not expired
- Verify migration target is documented

### Step 5: Determine Outcome

| Outcome | Condition | Next Action |
|---------|-----------|-------------|
| `ALLOW` | No core changes, or all generic | Proceed |
| `ALLOW_WITH_GENERIC_REFACTOR` | Core changes are generic | Write receipt, proceed |
| `BLOCK_MOVE_TO_APPS_CONFIG` | App-specific logic in core | Move to apps_*/config/, write receipt |
| `BLOCK_ROLLBACK_REQUIRED` | Leakage without path | Rollback, write receipt |

### Step 6: Write Receipt

If outcome requires receipt:

```json
{
  "receipt_version": "1.0",
  "audit_id": "uuid",
  "timestamp": "2026-05-11T12:00:00Z",
  "changed_files": [...],
  "classifications": {...},
  "forbidden_literals_found": [...],
  "receipts_verified": [...],
  "outcome": "ALLOW|ALLOW_WITH_GENERIC_REFACTOR|BLOCK_MOVE_TO_APPS_CONFIG|BLOCK_ROLLBACK_REQUIRED",
  "action_taken": "...",
  "next_steps": [...]
}
```

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `classification_report` | Dict[str, str] | File → classification mapping |
| `outcome` | Enum | ALLOW, ALLOW_WITH_GENERIC_REFACTOR, BLOCK_MOVE_TO_APPS_CONFIG, BLOCK_ROLLBACK_REQUIRED |
| `receipt_path` | str | Path to written receipt |
| `violations` | List[Dict] | Any leakage found |

## Blocking Conditions

This skill **BLOCKS** when:
- `CORE_APP_SPECIFIC_LEAKAGE` detected without migration plan
- `TEMPORARY_THIN_ADAPTER` file lacks current receipt
- New `if app_id == "..."` pattern added to core
- Hardcoded app-specific constants added to core
- Receipt validation fails

## Required Receipt Path

Boundary audit receipts:
```
artifacts/governance/boundary_receipts/<timestamp>_<audit_id>.json
```

Migration receipts (for TEMPORARY_THIN_ADAPTER):
```
artifacts/governance/migration_receipts/<timestamp>_<binding_name>.json
```

## Acceptance Criteria

- [ ] All `agentic_core/` files classified
- [ ] All `apps_*/` files correctly categorized as app-owned
- [ ] No `CORE_APP_SPECIFIC_LEAKAGE` without blocking action
- [ ] All `TEMPORARY_THIN_ADAPTER` have verified receipts
- [ ] Receipt written to canonical path
- [ ] Outcome documented and actionable

## Related

- Workflow: `/core-boundary-audit`
- Rule: `.windsurf/rules/boundary-audit-required.md`
- Rule: `.windsurf/rules/agentic-core-glob-lock.md`
