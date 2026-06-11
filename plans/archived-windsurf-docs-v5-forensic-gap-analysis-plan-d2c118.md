---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\v5-forensic-gap-analysis-plan-d2c118.md'
original_relative_path: 'v5-forensic-gap-analysis-plan-d2c118.md'
source_sha256: 94dc4bd53e38853ede00851bd390dcb19719705766fb2cec018b8c78deb5b85e
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# V5.0 Forensic Gap Analysis — Hardened Execution Plan

Execute a full forensic compliance audit against Prompt v5.0 (V15 Target State), resolving known precondition mismatches and producing a deterministic PASS/FAIL/MISSING report.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Pre-Execution Findings (Critical Blockers)

The audit prompt contains several references that **do not match** the current codebase. These must be reconciled before execution:

| Prompt Reference | Actual State | Impact |
|---|---|---|
| `structure_blueprint.py` (single file) | Package at `agentic_core/L5_safety/config/structure_blueprint/` + shim at `structure_blueprint_config.py` | Hash target must be the package, not a single file |
| Discovery script at `general_scripts/forensic_discovery_prep.py` | At `agentic_core/L0_maintenance/scripts/forensic_discovery_prep.py` | Path correction required |
| Discovery output schema: `meta`, `ssot_validation`, `agents` | Actual output: `audit_meta`, `environment_under_test`, `ignored_artifacts`, `counts` | Field mapping required |
| Expected per-agent fields: `identity`, `mro_chain`, `mixins`, `integrity_hash` | Actual fields: `agent_name`, `mro_signature`, (no separate `mixins`), `file_sha256` | Schema normalization required |
| Known Good Hash in `forensic_discovery_prep.py` | Hash is in `discovery_integrity.sha256` and `FORENSIC_DISCOVERY_INTEGRITY_HASH` in `ssot.py` | Verification path differs |

### Prior Report
A clean gap analysis report exists at `docs/reports/plans/v5_forensic_gap_analysis_report_clean.md` (2026-02-09): 150 ACTIVE, 40 INVALID, near-total MISSING/FAIL on V15 capabilities.

---

## Execution Plan

### Phase 0 — Discovery Integrity Gate

1. **Compute blueprint package hash**: SHA-256 of all `.py` files in `structure_blueprint/` package. Compare against `blueprint_integrity.sha256` (`56ce497e...`).
2. **Compute discovery script hash**: SHA-256 of `forensic_discovery_prep.py`. Compare against `discovery_integrity.sha256` (`b08c3cdb...`) and `FORENSIC_DISCOVERY_INTEGRITY_HASH` in `ssot.py`.
3. **Execute discovery**: `python agentic_core/L0_maintenance/scripts/forensic_discovery_prep.py --out artifacts/forensic_discovery_output.json`
4. **Schema validation**: Validate output against actual schema (v1.3.0). Map fields to prompt-expected names for audit consistency.
5. **Zombie detection**: Cross-check all ACTIVE agents' `file_path` against disk.

### Phase 1 — Scope Freeze

6. Lock scope to discovery output: enumerate ACTIVE, STUB, GHOST, INVALID, SYNTAX_ERROR counts.
7. ACTIVE agents → full audit. Others → auto-FAIL structure integrity, listed in Section 3.

### Phase 2 — Global Framework Audit

8. Audit capabilities **1, 3, 4, 6, 7, 10, 11, 13, 14, 15** system-wide.
9. For each capability: grep/AST-search for required types, schemas, artifacts, mechanisms.
10. Evidence format: `file_path::Class.method (lines X-Y)` or MISSING.
11. Apply P1-P6 gating where specified.

### Phase 3 — Per-Agent Matrix Audit

12. For each ACTIVE agent, audit capabilities **2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 15**.
13. MRO validation using discovery `mro_signature` (safety mixins LEFT rule).
14. Per-agent table with identity, layer, file, integrity hash, SSOT match, MRO chain.

### Phase 4 — Architecture Gate Enforcement (P1-P6)

15. Evaluate P1-P6 violations per capability, only when status changes.

### Phase 5 — Report Emission

16. **Section 1**: Global Framework Audit table (ID / Status / Evidence / Notes).
17. **Section 2**: Per-agent matrix audit (full table per ACTIVE agent).
18. **Section 3**: Forensic Summary (counts, compliance %, FAIL counts, non-ACTIVE list, integrity confirmations).
19. Save final report to `docs/reports/plans/v5_forensic_gap_analysis_report_v2.md`.

---

## Output Constraints

- Status vocabulary: **COMPLIANT**, **MISSING**, **FAIL** only
- No remediation language (no should/recommend/consider/improve/refactor/implement)
- No probabilistic language (no likely/appears/probably/could)
- No flow narration or directory listing
- Evidence-only: file + symbol + line range OR commit hash

---

## Decision Point for User

Before execution, confirm:
- **Option A**: Re-run full discovery + audit from scratch (fresh data, ~150 agents × 20+ capabilities)
- **Option B**: Validate prior report's Phase 0 integrity, then re-audit only (faster, reuses existing discovery)
- **Option C**: Proceed with full fresh run (Option A) but accept the schema mapping as a known deviation

The prior clean report shows near-total MISSING/FAIL for V15 capabilities. A fresh run will produce substantially similar results unless new code has been added since 2026-02-09.

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

