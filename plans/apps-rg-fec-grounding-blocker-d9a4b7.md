---
plan_type: platform_core_change
slug: apps-rg-fec-grounding-blocker-d9a4b7
status: In Progress
ai_summary: "Resolve the AIG E2E grounding blocker chain: FEC bridge alignment + citation distribution; G23 verified done."
dod_exempt: false
supersedes: []
---

# AIG E2E Grounding Blocker Chain — FEC/proof-pool + G23

## Supersedes
| Predecessor slug | Reason |
|---|---|
| _None — net-new plan._ | |

## Context (SCQA)

- **Situation.** After the C0.2 dense+sparse fixes, the AIG full-resume E2E now reaches REAL_LLM on
  every generating lane and **ey_bullets fully ALLOWs** — but 5 lanes block on **grounding** gates.
- **Complication.** Three roots: **(R3) G23 JD propagation**, **(R1) FEC bridge ⊄ canonical
  allowed-set** (`prompt_c0_ids⊄fec`), **(R2) generation cites too narrowly** (competencies grounded
  all 8 categories to one cert fact; `claim_ledger_coverage_100` / `source_fact_coverage_100`).
- **Question.** Which are real, and in what order do we fix them to reach a full AIG resume?
- **Answer.** **R3 is already resolved** (verified: the AIG JD propagated to every lane's targeting
  artifacts; the `DEFAULT_SSOT` log was import-time noise). Remaining work: a logging-hygiene fix for
  the misleading warning, then R1 (bridge↔FEC alignment) and R2 (citation distribution), each as a
  scoped fix + re-run, since they touch the proof-contract pipeline.

## Status Tables

### Wave Progress
| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W0 | P0 | **R3 verify + logging hygiene** — confirm G23 propagates; silence import-time DEFAULT_SSOT warning | ~20k | run artifacts carry AIG JD | 🔄 In Progress | AIG JD in all lane targeting (✅ verified); warning only fires on real-run DEFAULT_SSOT |
| W1 | P1 | **R1 — FEC bridge ⊆ canonical allowed-set** (`prompt_c0_ids⊄fec`) | ~90k | identify authoritative C0 stage | ⬜ Not Started | bridge surfaces only FEC-allowed ids; gate passes on competencies/ibm/headline |
| W2 | P2 | **R2 — citation distribution** (generator grounds across FEC, not one fact) | ~110k | prompt/proof-pool shaping | ⬜ Not Started | claim_ledger_coverage_100 + source_fact_coverage_100 pass; competencies cites ≥3 facts |
| W3 | P3 | Re-run AIG + reassess; iterate until lanes ALLOW | ~80k | — | ⬜ Not Started | ≥ N lanes ALLOW; full resume emits generated_resume.json |

### Phase-Level Summary
| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P0 | R3 verify + hygiene | `jd_resolution.py` | warning is cosmetic but misleads diagnosis | ~20k | 🔄 |
| P1 | R1 bridge↔FEC | `c0/evidence_room.py`, `evidence/canonical_section_evidence_set.py`, `spine/c0_fec_compose.py` | which C0 stage is authoritative for allowed_fact_ids | ~90k | ⬜ |
| P2 | R2 citation | prompt assembly + proof-pool presentation | generation-quality; iterative | ~110k | ⬜ |
| P3 | Re-run loop | — | fix→re-run→repeat | ~80k | ⬜ |

## Findings (from the AIG E2E run `full_resume_7fc542e3e9e1`)
- **R3 (G23): RESOLVED.** AIG JD signature present in `ingress_raw.json`, top + per-lane
  `validated_request.json`, exec_summary `targeting_context_parity_receipt.json` /
  `targeting_ingress_receipt.json`. Zero DEFAULT_SSOT in run targeting. The warning is from the
  module-level `JD_TEXT_DEFAULT = resolve_jd_for_lanes()` (no-arg) computed at import.
- **R1:** `collect_prompt_c0_fact_ids` reads `section_fec_bridge` (built `evidence_room.py:426`);
  the gate compares against `runtime_payload.allowed_fact_ids` (set `canonical_section_evidence_set.py:173`).
  These are computed at different C0 stages → bridge carries ids the canonical allow-set dropped.
- **R2:** competencies had 11 FEC facts available but cited `fact_certs_001` for all 8 categories.

## Definition of Done
| # | Criterion | Verification |
|---|---|---|
| 1 | G23 verified: AIG JD in all lane targeting artifacts | run-artifact grep (✅) |
| 2 | DEFAULT_SSOT warning fires only on real-run resolution (not module import) | import-smoke shows no warning; run with empty JD does |
| 3 | R1: `prompt_c0_ids_subset_of_fec` passes on competencies/ibm/headline | re-run gate result |
| 4 | R2: claim/source coverage gates pass; competencies cites ≥3 distinct facts | re-run gate result |
| 5 | Full AIG resume emits `generated_resume.json` (or strictly more lanes ALLOW than baseline=1) | live re-run |

## Safety / Invariants
- R1/R2 touch the proof-contract pipeline → scoped fix + re-run per stage; never weaken grounding.
- No re-run needed for R3 — the existing run is already AIG-targeted; reassess R1/R2 with its data.
