---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\github-workflows-consolidation-c4f7a9.md'
original_relative_path: '_archive\\2026-05\\github-workflows-consolidation-c4f7a9.md'
source_sha256: de902d66551805ccecbdb9bbf64fad81230b71bc61e7822eb1704c033562acd3
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# GitHub Workflows Consolidation — `32 → 15`

**Slug:** `github-workflows-consolidation-c4f7a9`
**Status:** In Progress
**Owner:** solo `main`-only repo

## 1. Goal

Reduce `.github/workflows/` from 32 files to 15 by deleting tier-shim workflows that are 100 % subsumed by the master aggregator and folding 6 single-purpose contract gates into one `contract-gates.yml`. Preserve every distinct check; eliminate cold-start tax.

## 2. Audit Evidence

`scripts/verify_all_requirements_gates.py` lines 53–67 already shells out to all 15 tier verifier scripts. Coverage matrix (verified 2026-05-06):

| Workflow | Subsumed by | Action |
|---|---|---|
| 11 × `tier*-enforcement-gate.yml` + `tier*-runtime-proof-gate.yml` + `tier-gate-hardening.yml` | `verify_all_requirements_gates.py` | DELETE |
| `all-requirements-gate.yml` | aggregator itself | RENAME → `contract-gates.yml` |
| `all-requirements-merkle-root.yml` | depends on aggregator | FOLD as final step |
| `subprocess-timeout-gate.yml` | mirrors T7h pre-commit hook | FOLD |
| `pytest-config-ssot.yml` | triple-covered | FOLD |
| `infra_wiring_check.yml` | triple-covered | FOLD |
| `config-sync-gates.yml` | 6/7 covered; `check_exclusion_sync.py` unique | FOLD (after Step A) |
| `guardian-tests.yml` | not folded — heavier pytest surface, path-filtered | KEEP |

## 3. Files In Scope

- **Modify:** `ops_scripts/ci/run_contract_gates.py` (add `check_exclusion_sync.py`)
- **Create:** `.github/workflows/contract-gates.yml`
- **Delete:** 17 workflow files (see Wave 3)

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | A | Add `check_exclusion_sync.py` to `run_contract_gates.py` | ~1k | Pending | Script registered as a gate entry |
| W2 | B | Author `contract-gates.yml` consolidating 6 workflows | ~3k | Pending | YAML-valid; all 6 step bodies preserved verbatim |
| W3 | C | Delete 17 redundant workflow files | ~1k | Pending | `ls .github/workflows/*.yml` returns 15 files |
| W4 | D | Verify | ~1k | Pending | `python -c "import yaml; yaml.safe_load(open('.github/workflows/contract-gates.yml'))"` exits 0 |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| A | Register `check_exclusion_sync` | `ops_scripts/ci/run_contract_gates.py` | Find correct group | 1k | Pending |
| B | Author consolidated workflow | `.github/workflows/contract-gates.yml` | Step ordering matters (aggregator → merkle last) | 3k | Pending |
| C | Delete 17 redundant files | `.github/workflows/tier*.yml`, `tier-gate-hardening.yml`, `all-requirements-*.yml`, `subprocess-timeout-gate.yml`, `pytest-config-ssot.yml`, `infra_wiring_check.yml`, `config-sync-gates.yml` | Use `git rm` | 1k | Pending |
| D | Verify YAML + count | `.github/workflows/` | None | 1k | Pending |

## 6. Files To Delete (W3)

```
.github/workflows/tier0-enforcement-gate.yml
.github/workflows/tier1-enforcement-gate.yml
.github/workflows/tier2-enforcement-gate.yml
.github/workflows/tier0-runtime-proof-gate.yml
.github/workflows/tier1-runtime-proof-gate.yml
.github/workflows/tier2-runtime-proof-gate.yml
.github/workflows/tier3-runtime-proof-gate.yml
.github/workflows/tier4-runtime-proof-gate.yml
.github/workflows/tier5-runtime-proof-gate.yml
.github/workflows/tier6-runtime-proof-gate.yml
.github/workflows/tier-gate-hardening.yml
.github/workflows/all-requirements-gate.yml
.github/workflows/all-requirements-merkle-root.yml
.github/workflows/subprocess-timeout-gate.yml
.github/workflows/pytest-config-ssot.yml
.github/workflows/infra_wiring_check.yml
.github/workflows/config-sync-gates.yml
```

## 7. Non-Goals

- Not touching: `adg-ci-gates.yml`, `runtime-certification.yml`, `agentic-core-auditability.yml`, `apps-e2e-harness-nightly.yml`, `apps-fortknox-keyless-sign.yml`, `fortknox-nightly.yml`, `judge-calibration.yml`, `calibration-drift.yml`, `notion-plan-file-drift-nightly.yml`, `author-gate-gates.yml`, `hitl-integrity-gate.yml`, `eval-harness.yml`, `l3-otel-reconciliation.yml`, `underwriting_holdout_gate.yml`, `guardian-tests.yml`.
- Not changing trigger semantics for non-deleted workflows.
- Not adding new gate logic — only relocation/consolidation.

## 8. Success Criteria

- `.github/workflows/*.yml` count = 15 (was 32; deleted 17).
- `contract-gates.yml` parses as valid YAML.
- `check_exclusion_sync.py` registered in `run_contract_gates.py`.
- No verifier script referenced by a deleted workflow loses CI coverage.
