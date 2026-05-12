---
name: receipt-auditor
description: |
  Use when verifying migration or governance receipts before committing changes.
  Ensures receipts are complete, valid, and meet audit compliance requirements.
---

# Receipt Auditor Skill

## Purpose

Verify the existence, validity, and completeness of governance receipts required for boundary-sensitive changes. Ensures every `agentic_core` modification is documented with proper classification, tests, and migration path.

## When to Use

Invoke this skill when:
- Before claiming task completion
- Before commit on core-boundary work
- `/pre-commit-agentic-cert` workflow validation
- CI receipt validation step
- `/core-boundary-audit` workflow step

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `receipt_path` | str | Yes | Path to receipt to audit |
| `receipt_type` | Enum | Yes | boundary, migration, customization, verification |
| `changed_files` | List[str] | Yes | Files that were modified |

## Steps

### Step 1: Verify Receipt Exists

Check file exists at expected path:
```python
import os
import json

if not os.path.exists(receipt_path):
    raise ReceiptMissingError(f"Receipt not found: {receipt_path}")

with open(receipt_path) as f:
    receipt = json.load(f)
```

### Step 2: Verify Changed Files Listed

Receipt must list all files changed:
```python
# Required field: changed_files or files_created/files_modified
assert 'changed_files' in receipt or ('files_created' in receipt and 'files_modified' in receipt)

# Verify all actual changes are covered
for file in changed_files:
    assert file in receipt.get('changed_files', []) or \
           file in receipt.get('files_created', []) or \
           file in receipt.get('files_modified', []), \
           f"File {file} not covered in receipt!"
```

### Step 3: Verify Tests Listed

Receipt must document test coverage:
```python
# Required: tests_added_or_updated OR test_coverage_explanation
tests = receipt.get('tests_added_or_updated', [])
explanation = receipt.get('test_coverage_explanation', '')

assert tests or explanation, "Receipt must list tests or explain why not applicable"

# If tests listed, verify they exist
for test_path in tests:
    assert os.path.exists(test_path), f"Test file missing: {test_path}"
```

### Step 4: Verify Known Gaps Listed

Receipt must document known gaps:
```python
# Required: known_gaps (can be empty list)
known_gaps = receipt.get('known_gaps', [])
# Empty list is valid if no gaps

# If gaps listed, each must have remediation plan
for gap in known_gaps:
    assert 'description' in gap, "Gap must have description"
    assert 'remediation' in gap or 'deferral_justification' in gap, \
           "Gap must have remediation plan or deferral justification"
```

### Step 5: Verify No Undocumented Core Changes

Cross-check receipt against actual changes:
```python
# Get all agentic_core/ changes
core_changes = [f for f in changed_files if f.startswith('agentic_core/')]

# If core changes exist, receipt must explain them
if core_changes:
    assert 'classification' in receipt or 'classifications' in receipt, \
           "Core changes require classification in receipt"
    
    # Verify classifications cover all core changes
    classifications = receipt.get('classifications', {})
    for change in core_changes:
        assert change in classifications, \
               f"Core change {change} not classified in receipt"
```

### Step 6: Validate Receipt Schema

Verify receipt matches expected schema by type:

**Boundary Receipt Schema:**
```json
{
  "receipt_version": "1.0",
  "audit_id": "uuid",
  "timestamp": "ISO8601",
  "changed_files": ["..."],
  "classifications": {"file": "classification"},
  "forbidden_literals_found": [],
  "outcome": "ALLOW|...",
  "receipts_verified": []
}
```

**Migration Receipt Schema:**
```json
{
  "receipt_version": "1.0",
  "binding_file": "path",
  "classification": "TEMPORARY_THIN_ADAPTER",
  "migration_target": "description",
  "target_location": "path",
  "app_profile_refs": [],
  "expected_completion": "date",
  "acceptance_criteria": []
}
```

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `receipt_valid` | bool | Overall validity |
| `schema_valid` | bool | Matches expected schema |
| `files_covered` | bool | All changes documented |
| `tests_covered` | bool | Tests listed or explained |
| `gaps_documented` | bool | Known gaps listed |
| `core_changes_explained` | bool | Core changes justified |
| `errors` | List[str] | Any validation failures |

## Blocking Conditions

This skill **BLOCKS** when:
- Receipt does not exist at expected path
- Receipt schema validation fails
- Changed files not listed in receipt
- Tests not listed and no explanation provided
- Known gaps not documented
- Core changes lack classification
- Core `CORE_APP_SPECIFIC_LEAKAGE` lacks migration plan
- TEMPORARY_THIN_ADAPTER lacks current receipt

## Required Receipt Paths

| Receipt Type | Path Pattern |
|--------------|--------------|
| Boundary | `artifacts/governance/boundary_receipts/<ts>_<id>.json` |
| Migration | `artifacts/governance/migration_receipts/<ts>_<binding>.json` |
| Customization | `artifacts/governance/customization_receipts/<ts>_<app>_<type>.json` |
| Verification | `artifacts/governance/verification_receipts/<ts>_<app>_package.json` |
| Wave | `artifacts/governance/<wave>_receipt.json` |

## Acceptance Criteria

- [ ] Receipt exists at expected path
- [ ] Receipt schema is valid
- [ ] All changed files listed
- [ ] All core changes classified
- [ ] Tests listed or explained
- [ ] Known gaps documented with remediation
- [ ] No undocumented core changes

## Classification Categories Used

- `RECEIPT_ALLOWED` — Receipts themselves
- `TEMPORARY_THIN_ADAPTER` — Bindings with receipts
- `CORE_APP_SPECIFIC_LEAKAGE` — Must have migration receipt
- `GENERIC_INFRASTRUCTURE` — Should have receipt for audit

## Related

- Workflow: `/pre-commit-agentic-cert`
- Skill: `core-boundary-audit` (produces receipts this skill audits)
