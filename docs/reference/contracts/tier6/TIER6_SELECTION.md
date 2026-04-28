# Tier 6 Selection — Final 21 Step 1 Requirements

- Tier:** TIER6
- Selected count:** 21
- Excludes:** all REQ_IDs already selected in Tier 0..5 (129 rows).
- Coverage:** Tier 0..6 = 17 + 15 + 22 + 25 + 25 + 25 + 21 = 150 = full Step 1 universe.

## Selection rationale

Tier 6 captures the residual Step 1 universe after Tier 0..5 selections.
Of the 21 rows, 7 are RELEASE_BLOCKING `MUST` requirements whose proof artifacts
(E2E proof bundle, runtime-to-regression dataset feed, human-calibration metadata,
weak-support refinement, route-path coverage matrix) are not yet harness-produced;
Tier 6 enforces the contract that the harness records this gap rather than masking
it. The remaining 14 are `REFERENCE / NON_BLOCKING_REFERENCE` parent/child
traceability surfaces (overview reference, traceability matrix, coverage matrix).

## Priority rank table

| Rank | REQ_ID | Layer | Strength | Release Gate | Risk Category |
|---:|---|---|---|---|---|
| 1 | `REQ-C0-WEAK-SUPPORT-REFINEMENT-001` | C0 | MUST | RELEASE_BLOCKING | retrieval_boundary |
| 2 | `REQ-E2E-ACCEPTANCE-COMMANDS-001` | E2E | MUST | RELEASE_BLOCKING | evaluation_integrity |
| 3 | `REQ-E2E-GOLDEN-PATH-001` | E2E | MUST | RELEASE_BLOCKING | evaluation_integrity |
| 4 | `REQ-E2E-ROUTE-PATH-COVERAGE-001` | E2E | MUST | RELEASE_BLOCKING | coverage_integrity |
| 5 | `REQ-EXIT-RUNTIME-TO-REGRESSION-001` | Exit | MUST | RELEASE_BLOCKING | evaluation_integrity |
| 6 | `REQ-L6-HUMAN-CALIBRATION-001` | L6 | MUST | RELEASE_BLOCKING | calibration_integrity |
| 7 | `REQ-C0-OVERVIEW-REFERENCE-001` | C0 | REFERENCE | NON_BLOCKING_REFERENCE | documentation_integrity |
| 8 | `REQ-C0-TRACEABILITY-MATRIX-REF-001` | C0 | REFERENCE | NON_BLOCKING_REFERENCE | reference_integrity |
| 9 | `REQ-E2E-OVERVIEW-REFERENCE-001` | E2E | REFERENCE | NON_BLOCKING_REFERENCE | documentation_integrity |
| 10 | `REQ-E2E-REQ-TO-EVIDENCE-COMPILER-001` | Traceability | REFERENCE | NON_BLOCKING_REFERENCE | reference_integrity |
| 11 | `REQ-EXIT-OVERVIEW-REFERENCE-001` | Exit | REFERENCE | NON_BLOCKING_REFERENCE | documentation_integrity |
| 12 | `REQ-L0-OVERVIEW-REFERENCE-001` | L0 | REFERENCE | NON_BLOCKING_REFERENCE | documentation_integrity |
| 13 | `REQ-L1-OVERVIEW-REFERENCE-001` | L1 | REFERENCE | NON_BLOCKING_REFERENCE | documentation_integrity |
| 14 | `REQ-L2-COVERAGE-MATRIX-REF-001` | L2 | REFERENCE | NON_BLOCKING_REFERENCE | coverage_integrity |
| 15 | `REQ-L4-OVERVIEW-REFERENCE-001` | L4 | REFERENCE | NON_BLOCKING_REFERENCE | documentation_integrity |
| 16 | `REQ-L5-V5-COVERAGE-MATRIX-REF-001` | L5 | REFERENCE | NON_BLOCKING_REFERENCE | coverage_integrity |
| 17 | `REQ-L6-OVERVIEW-REFERENCE-001` | L6 | REFERENCE | NON_BLOCKING_REFERENCE | documentation_integrity |
| 18 | `REQ-L6-V6-COVERAGE-MATRIX-REF-001` | L6 | REFERENCE | NON_BLOCKING_REFERENCE | coverage_integrity |
| 19 | `REQ-PA-OVERVIEW-REFERENCE-001` | PA | REFERENCE | NON_BLOCKING_REFERENCE | documentation_integrity |
| 20 | `REQ-PA-TRACEABILITY-MATRIX-REF-001` | PA | REFERENCE | NON_BLOCKING_REFERENCE | reference_integrity |
| 21 | `REQ-U0-OVERVIEW-REFERENCE-001` | U0 | REFERENCE | NON_BLOCKING_REFERENCE | documentation_integrity |

## Per-row metadata

### 1. `REQ-C0-WEAK-SUPPORT-REFINEMENT-001`

- **Source matrix**: `03A_C0_REQ_MATRIX.md`
- **Owner**: C0 / WeakSupport
- **Strength / Release**: MUST / RELEASE_BLOCKING
- **Risk**: retrieval_boundary
- **Requirement**: C0 MUST detect weak support and trigger declared refinement before sealing the evidence contract.
- **Why Tier 6**: Final-tier release-blocking requirement that depends on artifacts (E2E proof bundle, regression dataset feed, calibration metadata) which the harness does not yet produce. Tier 6 captures and tracks the gap; closure is a future prompt.
- **Likely evidence**: Static reference module + targeted fixture test + deterministic trace + replay pair + negative-control fixture for retrieval_boundary.

### 2. `REQ-E2E-ACCEPTANCE-COMMANDS-001`

- **Source matrix**: `99_E2E_REQ_MATRIX.md`
- **Owner**: E2E / AcceptanceBundle
- **Strength / Release**: MUST / RELEASE_BLOCKING
- **Risk**: evaluation_integrity
- **Requirement**: E2E acceptance MUST produce the declared proof bundle.
- **Why Tier 6**: Final-tier release-blocking requirement that depends on artifacts (E2E proof bundle, regression dataset feed, calibration metadata) which the harness does not yet produce. Tier 6 captures and tracks the gap; closure is a future prompt.
- **Likely evidence**: Static reference module + targeted fixture test + deterministic trace + replay pair + negative-control fixture for evaluation_integrity.

### 3. `REQ-E2E-GOLDEN-PATH-001`

- **Source matrix**: `99_E2E_REQ_MATRIX.md`
- **Owner**: E2E / GoldenPath
- **Strength / Release**: MUST / RELEASE_BLOCKING
- **Risk**: evaluation_integrity
- **Requirement**: E2E golden-path runtime proof MUST exercise U0→L1→L0→C0→PA→L2→Exit→L6 once per run.
- **Why Tier 6**: Final-tier release-blocking requirement that depends on artifacts (E2E proof bundle, regression dataset feed, calibration metadata) which the harness does not yet produce. Tier 6 captures and tracks the gap; closure is a future prompt.
- **Likely evidence**: Static reference module + targeted fixture test + deterministic trace + replay pair + negative-control fixture for evaluation_integrity.

### 4. `REQ-E2E-ROUTE-PATH-COVERAGE-001`

- **Source matrix**: `99_E2E_REQ_MATRIX.md`
- **Owner**: E2E / RouteCoverage
- **Strength / Release**: MUST / RELEASE_BLOCKING
- **Risk**: coverage_integrity
- **Requirement**: E2E proofs MUST cover each declared L0 route class at least once.
- **Why Tier 6**: Final-tier release-blocking requirement that depends on artifacts (E2E proof bundle, regression dataset feed, calibration metadata) which the harness does not yet produce. Tier 6 captures and tracks the gap; closure is a future prompt.
- **Likely evidence**: Static reference module + targeted fixture test + deterministic trace + replay pair + negative-control fixture for coverage_integrity.

### 5. `REQ-EXIT-RUNTIME-TO-REGRESSION-001`

- **Source matrix**: `05_EXIT_REQ_MATRIX.md`
- **Owner**: Exit / RuntimeToRegression
- **Strength / Release**: MUST / RELEASE_BLOCKING
- **Risk**: evaluation_integrity
- **Requirement**: Exit MUST emit runtime exhaust eligible for the regression dataset flow.
- **Why Tier 6**: Final-tier release-blocking requirement that depends on artifacts (E2E proof bundle, regression dataset feed, calibration metadata) which the harness does not yet produce. Tier 6 captures and tracks the gap; closure is a future prompt.
- **Likely evidence**: Static reference module + targeted fixture test + deterministic trace + replay pair + negative-control fixture for evaluation_integrity.

### 6. `REQ-L6-HUMAN-CALIBRATION-001`

- **Source matrix**: `06_L6_REQ_MATRIX.md`
- **Owner**: L6 / HumanCalibration
- **Strength / Release**: MUST / RELEASE_BLOCKING
- **Risk**: calibration_integrity
- **Requirement**: L6 MUST seal eval records with declared human-calibration metadata.
- **Why Tier 6**: Final-tier release-blocking requirement that depends on artifacts (E2E proof bundle, regression dataset feed, calibration metadata) which the harness does not yet produce. Tier 6 captures and tracks the gap; closure is a future prompt.
- **Likely evidence**: Static reference module + targeted fixture test + deterministic trace + replay pair + negative-control fixture for calibration_integrity.

### 7. `REQ-C0-OVERVIEW-REFERENCE-001`

- **Source matrix**: `03A_C0_REQ_MATRIX.md`
- **Owner**: C0 / Overview
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: documentation_integrity
- **Requirement**: C0 parent file is reference for parent/child traceability.
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 8. `REQ-C0-TRACEABILITY-MATRIX-REF-001`

- **Source matrix**: `03A_C0_REQ_MATRIX.md`
- **Owner**: C0 / Traceability
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: reference_integrity
- **Requirement**: C0 traceability matrix is the reference parent/child surface for C0 requirements.
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 9. `REQ-E2E-OVERVIEW-REFERENCE-001`

- **Source matrix**: `99_E2E_REQ_MATRIX.md`
- **Owner**: E2E / Overview
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: documentation_integrity
- **Requirement**: E2E parent file is reference for parent/child traceability.
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 10. `REQ-E2E-REQ-TO-EVIDENCE-COMPILER-001`

- **Source matrix**: `99_E2E_REQ_MATRIX.md`
- **Owner**: Traceability / EvidenceCompiler
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: reference_integrity
- **Requirement**: Requirements-to-runtime-evidence compiler is the canonical traceability surface for E2E.
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 11. `REQ-EXIT-OVERVIEW-REFERENCE-001`

- **Source matrix**: `05_EXIT_REQ_MATRIX.md`
- **Owner**: Exit / Overview
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: documentation_integrity
- **Requirement**: Exit parent file is reference for parent/child traceability.
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 12. `REQ-L0-OVERVIEW-REFERENCE-001`

- **Source matrix**: `03_L0_L3_REQ_MATRIX.md`
- **Owner**: L0 / Overview
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: documentation_integrity
- **Requirement**: L0/L3 parent file is reference for parent/child traceability.
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 13. `REQ-L1-OVERVIEW-REFERENCE-001`

- **Source matrix**: `02_L1_PLAN_REQ_MATRIX.md`
- **Owner**: L1 / Overview
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: documentation_integrity
- **Requirement**: L1 reasoning/plan parent file is reference for parent/child traceability.
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 14. `REQ-L2-COVERAGE-MATRIX-REF-001`

- **Source matrix**: `04_L2_REQ_MATRIX.md`
- **Owner**: L2 / Traceability
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: coverage_integrity
- **Requirement**: L2 coverage matrix is the reference parent/child surface (no claims carried into Step 1).
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 15. `REQ-L4-OVERVIEW-REFERENCE-001`

- **Source matrix**: `00B_L4_UWG_REQ_MATRIX.md`
- **Owner**: L4 / Overview
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: documentation_integrity
- **Requirement**: L4 state archive overview is reference for parent/child traceability.
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 16. `REQ-L5-V5-COVERAGE-MATRIX-REF-001`

- **Source matrix**: `00A_L5_REQ_MATRIX.md`
- **Owner**: L5 / Traceability
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: coverage_integrity
- **Requirement**: v5 coverage matrix is referenced as L5 traceability surface (no claims carried into Step 1).
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 17. `REQ-L6-OVERVIEW-REFERENCE-001`

- **Source matrix**: `06_L6_REQ_MATRIX.md`
- **Owner**: L6 / Overview
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: documentation_integrity
- **Requirement**: L6 parent file is reference for parent/child traceability.
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 18. `REQ-L6-V6-COVERAGE-MATRIX-REF-001`

- **Source matrix**: `06_L6_REQ_MATRIX.md`
- **Owner**: L6 / Traceability
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: coverage_integrity
- **Requirement**: v6 coverage matrix is the reference parent/child surface (no claims carried into Step 1).
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 19. `REQ-PA-OVERVIEW-REFERENCE-001`

- **Source matrix**: `03B_PA_REQ_MATRIX.md`
- **Owner**: PA / Overview
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: documentation_integrity
- **Requirement**: PA parent file is reference for parent/child traceability.
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 20. `REQ-PA-TRACEABILITY-MATRIX-REF-001`

- **Source matrix**: `03B_PA_REQ_MATRIX.md`
- **Owner**: PA / Traceability
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: reference_integrity
- **Requirement**: PA traceability matrix is the reference parent/child surface for PA requirements.
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.

### 21. `REQ-U0-OVERVIEW-REFERENCE-001`

- **Source matrix**: `01_U0_INTAKE_REQ_MATRIX.md`
- **Owner**: U0 / Overview
- **Strength / Release**: REFERENCE / NON_BLOCKING_REFERENCE
- **Risk**: documentation_integrity
- **Requirement**: U0 request intake parent file is reference for parent/child traceability.
- **Why Tier 6**: Final-tier reference row. Captured here so the Step 1 universe (150) is fully tier-classified; non-blocking traceability surface only.
- **Likely evidence**: Reference parent/child surface; no runtime evidence required.
