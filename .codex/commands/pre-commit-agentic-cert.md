---
workflow_id: pre-commit-agentic-cert
slash_command: /pre-commit-agentic-cert
version: "1.0"
tier: 2
description: |
  Pre-commit governance validation. Runs governance tests, scans for
  leakage, validates receipts, and ensures no direct L4 write or app
  X3 emission. Blocks commit if violations found.
---

# /pre-commit-agentic-cert Workflow

## Slash-Command Purpose

Run comprehensive pre-commit governance validation to ensure all changes comply with the app-agnostic core architecture. This is the final gate before committing changes that touch `agentic_core/` or cross the core/apps_* boundary.

## Ordered Steps

### Step 1: Run Governance Tests

Execute governance test suite:

```bash
python -m pytest tests/governance/ -v --tb=short
```

Key tests:
- `test_agentic_core_static_boundary.py` — No app policy in shared core
- `test_no_app_specific_literals_in_core.py` — Literal scan
- `test_apps_runtime_package_contracts.py` — Package validation
- `test_no_direct_l4_write_bypass.py` — No direct L4 writes
- `test_no_app_exit_x3_emission.py` — No app X3 emission

### Step 2: Run Static Leakage Scanner

Scan for forbidden patterns:

```python
scanner = CoreLeakageScanner()

# Scan all staged files
violations = []
for file in staged_files:
    if file.startswith('agentic_core/'):
        findings = scanner.scan(file)
        violations.extend(findings)

# Forbidden patterns
PATTERNS = {
    'app_id_branching': r'if\s+app_id\s*==\s*["\']',
    'hardcoded_apps': r'["\']apps_\w+["\']',
    'app_routes': r'R4_MANAGED_DRAFT|R1_RESUME_GENERATION',
    'cache_bypass': r'final_draft_r\da_bypass',
    'direct_l4_write': r'L4State\.write\(|durable_write\(',
    'app_x3_emit': r'emit_x3\(|X3Disposition\(',
}
```

### Step 3: Validate Receipts

Verify all required receipts exist:

```python
receipt_auditor = ReceiptAuditor()

# Check for boundary receipts
for core_file in changed_core_files:
    receipt_path = f"artifacts/governance/boundary_receipts/*_{core_file.replace('/', '_')}.json"
    if not glob(receipt_path):
        violations.append(f"Missing boundary receipt for {core_file}")

# Verify receipt contents
for receipt_file in glob("artifacts/governance/boundary_receipts/*.json"):
    receipt = load_json(receipt_file)
    
    # Validate schema
    if not receipt_auditor.validate_schema(receipt, 'boundary'):
        violations.append(f"Invalid receipt schema: {receipt_file}")
    
    # Verify files covered
    for file in receipt.get('changed_files', []):
        if file in staged_files and file not in receipt['classifications']:
            violations.append(f"File {file} not classified in {receipt_file}")
```

### Step 4: Validate No Direct L4 Write

Check apps don't bypass UWG:

```python
# Scan apps_* for direct L4 writes
for file in staged_app_files:
    content = read_file(file)
    
    if 'L4State.write(' in content or 'durable_write(' in content:
        violations.append({
            'file': file,
            'violation': 'DIRECT_L4_WRITE',
            'severity': 'CRITICAL',
            'message': 'Apps must not write L4 directly; use Exit X3C -> UWG'
        })
```

### Step 5: Validate No App X3 Emission

Check apps don't emit X3:

```python
# Scan apps_* for X3 emission
for file in staged_app_files:
    content = read_file(file)
    
    if 'emit_x3(' in content or 'X3Disposition(' in content:
        violations.append({
            'file': file,
            'violation': 'APP_X3_EMISSION',
            'severity': 'CRITICAL',
            'message': 'Only agentic_core Exit may emit X3; use Exit profile'
        })
```

### Step 6: Generate Certification Report

Create pre-commit certification:

```json
{
  "certification_version": "1.0",
  "workflow": "/pre-commit-agentic-cert",
  "timestamp": "<ISO8601>",
  "commit_hash": "<staged_commit>",
  
  "staged_files": {
    "agentic_core": [...],
    "apps_lic": [...],
    "apps_rg": [...],
    "other": [...]
  },
  
  "governance_tests": {
    "tests_run": 5,
    "tests_passed": 5,
    "tests_failed": 0
  },
  
  "leakage_scan": {
    "files_scanned": <n>,
    "violations_found": <n>,
    "violations": [...]
  },
  
  "receipt_validation": {
    "receipts_required": <n>,
    "receipts_found": <n>,
    "receipts_valid": <n>
  },
  
  "direct_l4_write_check": {
    "files_checked": <n>,
    "violations": []
  },
  
  "app_x3_emission_check": {
    "files_checked": <n>,
    "violations": []
  },
  
  "certification_status": "PASS|BLOCK",
  "blocking_violations": [...],
  
  "bypass_available": "PRE_COMMIT_CERT_BYPASS=1"
}
```

## Files Inspected

| File Pattern | Purpose |
|--------------|---------|
| `agentic_core/**/*.py` | Core files for leakage |
| `apps_lic/**/*.py` | App files for direct writes |
| `apps_rg/**/*.py` | App files for direct writes |
| `apps_qna/**/*.py` | App files for direct writes |
| `apps_research/**/*.py` | App files for direct writes |
| `tests/governance/*.py` | Governance tests |
| `artifacts/governance/boundary_receipts/*.json` | Boundary receipts |
| `artifacts/governance/migration_receipts/*.json` | Migration receipts |

## Classification Categories

Categories validated:

- `GENERIC_CORE_RUNTIME` — Core must remain generic
- `GENERIC_INFRASTRUCTURE` — Infrastructure allowed
- `TEMPORARY_THIN_ADAPTER` — Must have receipt
- `CORE_APP_SPECIFIC_LEAKAGE` — **BLOCK**
- `APPS_CONTRACT` — App files checked for direct writes
- `APPS_TEST` — Tests must pass
- `RECEIPT_ALLOWED` — Receipts validated

## Expected Receipt

Path:
```
artifacts/governance/pre_commit_cert/<timestamp>_<commit_short>.json
```

## Stop Conditions

This workflow **STOPS** (blocks commit) when:

- Any governance test fails
- Leakage scan finds violations
- Required receipt missing
- Receipt validation fails
- Direct L4 write detected in apps_*
- App X3 emission detected in apps_*
- User explicitly cancels

## Success Criteria

- [ ] All governance tests pass
- [ ] Leakage scan clean
- [ ] All required receipts present and valid
- [ ] No direct L4 writes in apps_*
- [ ] No app X3 emission in apps_*
- [ ] Certification report generated
- [ ] Status: PASS

## Bypass

Emergency bypass:
```bash
PRE_COMMIT_CERT_BYPASS=1 git commit -m "..."
```

This logs a warning but allows commit. Use only in exceptional circumstances.

## Output

```
PRE_COMMIT_AGENTIC_CERT: status=<PASS|BLOCK>, violations=<count>, cert=<path>
```

## CI Enforcement

This workflow is invoked automatically by:
- `.codex/hooks.json` pre-commit hook (W3)
- CI gate in `ops_scripts/ci/run_contract_gates.py` (W4)

## Related

- Skill: `receipt-auditor` (Step 3)
- Skill: `core-boundary-audit` (leakage detection)
- Workflow: `/core-boundary-audit`
- Rule: `.codex/rules/agentic-core-glob-lock.md`
