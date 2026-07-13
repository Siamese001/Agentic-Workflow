---
plan_id: apps-rg-spearman-l6-calibration-spine-c8f4a2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_apps_rg: true
core_addition_author_gate_required: true
author_gate_receipt_ref: "artifacts/governance/core_addition_author_gate/apps-rg-spearman-l6-calibration-spine-c8f4a2.json"
created: 2026-07-13
owner: Codex
---

# apps_rg Spearman L6 Calibration Spine

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: PARTIALLY_COMPLETE_DATA_BLOCKED
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W8
LAST_UPDATED: 2026-07-13

## Objective

Calibrate the active core-owned `apps_rg` executive-positioning judge in L6.4,
route any future-run baseline through G29, the gauntlet, and UWG, and let Exit
consume only an approved L4 baseline without computing Spearman or mutating the
completed run.

## Status Tables

### Wave Progress

| Wave | Focus | Status |
|---|---|---|
| W0 | Baseline and contract freeze at `e9c3afb63de1e5f8b53d53b13d1021b2e8729e24` | Completed |
| W1 | Canonical judge identity and production scoring adapter | Completed |
| W2 | Human semantic holdout | Blocked on reviewer-authored corpus |
| W3 | Evidence-bound Spearman engine | Completed |
| W4 | L6.4 calibration and seal integration | Completed |
| W5 | Post-boundary reachability | Completed |
| W6 | RCA, G29, gauntlet, UWG, and L4 baseline contract | Completed |
| W7 | Future-run Exit consumption | Completed |
| W8 | CI gates and end-to-end proof | Completed, semantic promotion held by W2 |

### Data Dependency

No authorized human semantic holdout was present at W0. This change must not
manufacture reviewer provenance or convert synthetic fixtures into promotion
evidence. Dataset and semantic-threshold gates therefore remain advisory and
report `INSUFFICIENT` until a versioned corpus has at least 40 rows, two reviewer
references per row, required adjudication receipts, and leakage checks.

## Invariants

1. Spearman is computed only in L6.4, never in Exit.
2. A fresh timestamp without evidence is `INSUFFICIENT`, not `CURRENT`.
3. Synthetic labels are never promotion eligible.
4. L6 emits proposals and receipts; it never writes L4 directly.
5. G29 and the gauntlet precede UWG promotion.
6. Exit reads only an approved, unexpired, identity-matched future-run baseline.
7. The active identity is `rg::executive_positioning_judge::v1` at
   `agentic_core.runtime.judges.resume_judges.executive_positioning`.
8. Executive positioning remains informational-only and cannot autonomously
   authorize a current-run disposition.

## Definition of Done

- Runtime, registry, roster, calibration runner, and CI share one judge identity.
- Reusable L6 code emits rho, p-value, sample count, identities, evidence digests,
  structured failure codes, and a deterministic result digest.
- `run_6b` supports explicit calibration modes and seals reliability lineage.
- Weak or invalid calibration produces RCA evidence and cannot promote.
- The L4 baseline contract requires promotion and UWG receipts and is hydrated
  only by the UWG-side registration adapter.
- Exit contains no Spearman or holdout-loading code and bounds future-run use.
- Five `apps_rg` CI gates cover identity, dataset, calibration, placement, and
  promotion; data-dependent gates fail closed when explicitly promoted.
- Unit and end-to-end tests prove no current-run rescue and no direct L4 write.

## Execution Closeout

### Implemented

- One canonical runtime and calibration identity for
  `rg::executive_positioning_judge::v1`.
- Evidence-bound L6 Spearman results with explicit calibration modes, dataset
  identity, reviewer provenance, deterministic digests, failure reasons, and
  synthetic-label promotion exclusion.
- L6.4 reliability sealing, weak-calibration RCA, G29/gauntlet promotion gates,
  UWG-only app-domain registration, and replayable L4 approved baselines.
- Post-Exit sealed-exhaust reachability and future-run read-only Exit use with
  bounded reliability postures.
- Five registered CI gates for identity, dataset, calibration, placement, and
  promotion, including explicit fail-closed environment switches.

### Verification

- Focused L6, judge, adapter, Exit, CI, and end-to-end suite: `445 passed`.
- Core author-gate schema and negative-control suite: `43 passed`.
- App-domain UWG registration slice: `8 passed, 1 deselected`.
- New Python files: Ruff clean; changed runtime and test surfaces: compileall
  exit `0`.
- Core-Addition Author Gate: `15 path(s) scanned, 0 findings, 0 receipt errors`.
- `RG-SPEARMAN-IDENTITY` and `RG-SPEARMAN-L6-PLACEMENT`: PASS, exit `0`.
- Dataset, calibration, and promotion gates: advisory while W2 is absent; each
  exits `1` when its fail-closed switch is enabled.
- Operational calibration command: exit `2`, `status=INSUFFICIENT`, `n=0`,
  `promotion_eligible=false`.

### External Blockers

- DoD-2 is not met. No authorized versioned corpus with at least 40 human
  semantic rows, two reviewer refs per row, adjudication receipts, and leakage
  evidence exists. No labels or reviewer provenance were fabricated.
- The exact broad pytest command reached 97% and exited `1` on the unchanged
  underwriting rationale judge making a live Anthropic request that exceeded
  pytest's 180-second timeout. The same run passed this plan's Spearman CI tests
  8/8 and exposed broad pre-existing cross-app contract failures.
- `run_contract_gates.py` exits `1` before this plan's registered gates on the
  unchanged `u0-app-customization` skill-description quality check.

### Remaining Completion Step

W2 must be completed by authorized reviewers. After the immutable holdout is
published, rerun the operational calibration, promote dataset/calibration/
promotion gates to fail closed, obtain G29 and gauntlet approval, commit the
baseline through UWG, and rerun this plan's semantic promotion proof.
