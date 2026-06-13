# CI Ratchet and Scorecard Plan
**Generated:** 2026-04-08
**Purpose:** CI scan scripts and ratchet system to prevent infrastructure wiring regression

## Executive Summary

CI enforcement mechanisms to maintain infrastructure wiring compliance. Includes scan scripts, ratchet countdowns, and scorecard tracking.

**Components:** Scan script, Ratchet system, Scorecard
**Enforcement Point:** Pre-commit hook and CI gate

---

## Scan Script: infra_wiring_scan.py

**Location:** `ops_scripts/ci/infra_wiring_scan.py`

**Function:** Scan for direct infra imports in forbidden layers

**Logic:**
1. Scan all Python files in agentic_core/ and apps_*/ (exclude apps_shared/)
2. Detect direct imports: redis, chromadb, sqlite3, boto3, openai, anthropic, httpx, requests
3. Exclude files in tools/ and infrastructure/ (allowed there)
4. Report violations with file path, line number, and import pattern
5. Exit with error code 1 if violations found (blocks commit)

**Usage:**
```bash
python ops_scripts/ci/infra_wiring_scan.py
```

**Exit Codes:**
- 0: No violations (pass)
- 1: Violations found (fail)
- 2: Scan error (fail)

---

## Ratchet System

### Ratchet #1: Direct apps_* Infra Access
**Current Count:** 1 (ChromaDB in apps_rfp)
**Target Count:** 0
**Countdown:** IMMEDIATE
**Enforcement:** BLOCK COMMIT

**Description:** apps_* surfaces must not directly import raw infrastructure clients.

**Ratchet Logic:**
- Countdown decrements on each commit
- At countdown = 0, block commits with violations
- Current state: 1 violation → block immediately

### Ratchet #2: Raw Use Outside Owner Layers
**Current Count:** 0
**Target Count:** 0
**Countdown:** N/A (already compliant)
**Enforcement:** WARNING → BLOCK

**Description:** Raw infra usage must be in owner layer or tools/infrastructure only.

### Ratchet #3: Zero-Caller Infra Surfaces
**Current Count:** 0
**Target Count:** 0
**Countdown:** N/A (already compliant)
**Enforcement:** WARNING

**Description:** Dormant infra surfaces should be removed or activated.

### Ratchet #4: Mixed Wrapped/Raw Usage
**Current Count:** 1 (ChromaDB)
**Target Count:** 0
**Countdown:** After Repair #001
**Enforcement:** WARNING → BLOCK

**Description:** Same infra used both directly and via adapter is inconsistent.

---

## Scorecard Format

**Location:** `artifacts/infra_wiring_scorecard.json`

**Schema:**
```json
{
  "timestamp": "2026-04-08T17:00:00Z",
  "total_infra_surfaces": 10,
  "approved_active": 7,
  "active_miswired": 2,
  "dormant_unwired": 1,
  "experimental_isolated": 0,
  "deprecated_pending_removal": 0,
  "compliance_score": 90,
  "violations": {
    "p0": 1,
    "p1": 0,
    "p2": 0,
    "p3": 0
  },
  "ratchets": [
    {
      "name": "apps_* direct infra access",
      "current": 1,
      "target": 0,
      "countdown": 0,
      "status": "BLOCK"
    },
    {
      "name": "raw use outside owner layers",
      "current": 0,
      "target": 0,
      "countdown": 0,
      "status": "COMPLIANT"
    },
    {
      "name": "zero-caller infra",
      "current": 0,
      "target": 0,
      "countdown": 0,
      "status": "COMPLIANT"
    },
    {
      "name": "mixed wrapped/raw usage",
      "current": 1,
      "target": 0,
      "countdown": 5,
      "status": "WARNING"
    }
  ]
}
```

---

## CI Integration

### Pre-commit Hook
**Location:** `.git/hooks/pre-commit` (managed via pre-commit framework)

**Script:** `ops_scripts/ci/infra_wiring_scan.py`

**Behavior:**
- Runs on every commit
- Blocks commit if violations found
- Updates scorecard if compliant

### CI Gate
**Location:** `.github/workflows/infra_wiring_check.yml`

**Script:** `ops_scripts/ci/infra_wiring_scan.py`

**Behavior:**
- Runs on every PR
- Blocks merge if violations found
- Fails build if scorecard compliance < 100%

---

## Implementation Steps

1. Create scan script: `ops_scripts/ci/infra_wiring_scan.py`
2. Add pre-commit hook configuration
3. Create CI workflow: `.github/workflows/infra_wiring_check.yml`
4. Initialize scorecard: `artifacts/infra_wiring_scorecard.json`
5. Add to CI pipeline

---

## Next Steps

Execute Repair #001 from Phase 4, then implement CI ratchet system.
