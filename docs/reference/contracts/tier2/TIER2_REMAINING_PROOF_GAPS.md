# Tier 2 Remaining Proof Gaps

Static inventory of Tier 2 rows still BLOCKED after the negative-control
mapping pass. **Selection + linkage metadata only.** No proof, coverage,
or readiness claims are made. The gaps listed here are not closed.

No runtime behavior, tests, proof harness, replay machinery, or OTEL
exporter were executed.

## Headline

- Tier 2 total: **22**
- LINKED_LITERAL: **6**
- BLOCKED: **16**

## Blocker Counts (after negative-control mapping)

| Blocker | Count |
|---|---:|
| NEEDS_REPLAY_FIELD | 12 |
| NEEDS_ARTIFACT_FIELD | 8 |
| NEEDS_NEGATIVE_CONTROL | 8 |
| NEEDS_OTEL_SPAN | 8 |
| NEEDS_CODE_REF | 4 |
| NEEDS_VALIDATOR_REF | 4 |
| NEEDS_TEST_MAPPING | 4 |
| NEEDS_EXPECTED_FAIL_REASON | 0 |
| NEEDS_STEP1_ROW | 0 |
| NO_LINK | 0 |

## LINKED_LITERAL Rows (6)

- REQ-U0-VALIDATED-REQUEST-HANDOFF-001
- REQ-U0-ANTI-BYPASS-001
- REQ-L1-PLAN-CONTRACT-HANDOFF-001
- REQ-C0-EVIDENCE-FETCH-001
- REQ-EXIT-NO-OVERLAP-RUNTIME-GATES-001
- REQ-E2E-CONTRACT-EMISSION-001

## Blocked Rows (16) — Per-Row Minimum Missing Proof

### Batch A — Single-blocker rows (6)

| REQ_ID | Blocker | Minimum missing proof |
|---|---|---|
| REQ-L2-PTC-SANDBOX-001 | NEEDS_OTEL_SPAN | Dedicated OTEL spans module for PTC sandbox entry / exit. |
| REQ-L2-VERIFY-THEN-EXECUTE-001 | NEEDS_OTEL_SPAN | OTEL spans module for L2 local-critique / verify-then-execute verdict. |
| REQ-PA-PROVIDER-AWARE-RENDER-001 | NEEDS_OTEL_SPAN | OTEL spans module for PA provider-aware rendering (template id, provider id). |
| REQ-PA-AIRLOCK-SECURITY-001 | NEEDS_OTEL_SPAN | OTEL spans module for PA airlock verdict / score. |
| REQ-L6-SIGNAL-FUSION-RCA-001 | NEEDS_REPLAY_FIELD | Replay pair for L6 signal-fusion / RCA input determinism (existing gauntlet-future pair covers a sibling concern, not the input boundary). |
| REQ-E2E-MUTATION-BOUNDARY-001 | NEEDS_REPLAY_FIELD | Replay pair for `boundary_faults/proof_bundle.json` (two deterministic runs). |

### Batch B — Two-blocker rows (2)

| REQ_ID | Blockers | Minimum missing proof |
|---|---|---|
| REQ-C0-NO-EXECUTE-001 | NEEDS_ARTIFACT_FIELD, NEEDS_REPLAY_FIELD | C0-no-execute attestation artifact + replay pair proving zero tool / model invocations at C0. |
| REQ-L5-HITL-RECLEARANCE-001 | NEEDS_NEGATIVE_CONTROL, NEEDS_REPLAY_FIELD | Negative-control test driving a governance-flagged input to L2 without reclearance and asserting rejection; replay pair on the RC-HITL scenario. |

### Batch C — Three-blocker rows (4)

| REQ_ID | Blockers | Minimum missing proof |
|---|---|---|
| REQ-L3-L2-STEP-HANDOFF-001 | NEEDS_NEGATIVE_CONTROL, NEEDS_OTEL_SPAN, NEEDS_REPLAY_FIELD | L3->L2 step-checkpoint OTEL spans; replay-from-checkpoint determinism pair; negative-control proving missing-checkpoint resume aborts. |
| REQ-L4-CACHE-STATE-001 | NEEDS_ARTIFACT_FIELD, NEEDS_NEGATIVE_CONTROL, NEEDS_REPLAY_FIELD | Cache-invalidation audit artifact carrying contract_id per event; replay pair; negative-control proving ad-hoc invalidation rejected. |
| REQ-L5-RISK-TIER-BANDS-001 | NEEDS_ARTIFACT_FIELD, NEEDS_NEGATIVE_CONTROL, NEEDS_REPLAY_FIELD | Risk-tier assignment audit artifact (every value maps to a published band id); replay pair; negative-control proving ad-hoc score rejected. |
| REQ-U0-ORIGIN-TRUST-INJECTION-001 | NEEDS_ARTIFACT_FIELD, NEEDS_NEGATIVE_CONTROL, NEEDS_REPLAY_FIELD | U0 origin-trust injection receipt artifact (origin + trust label); replay pair; negative-control proving missing trust-label is rejected or quarantined. |

### Batch D — Five-blocker row (1)

| REQ_ID | Blockers | Minimum missing proof |
|---|---|---|
| REQ-L4-RETRIEVAL-SURFACE-001 | NEEDS_ARTIFACT_FIELD, NEEDS_CODE_REF, NEEDS_REPLAY_FIELD, NEEDS_TEST_MAPPING, NEEDS_VALIDATOR_REF | Dedicated retrieval-surface read-only guard module under `agentic_core/L4_state/retrieval_surface/` + its validator + dedicated test + scan artifact proving no non-UWG path mutates the surface + replay pair. Today no retrieval-surface module exists in `L4_state`. |

### Batch E — Seven-blocker rows (3)

These three rows currently rely on **module topology** to enforce the
contract — there is no dedicated boundary-guard module, validator, or
test that asserts the absence directly.

| REQ_ID | Blockers (all 7 NEEDS_* items) | Minimum missing proof |
|---|---|---|
| REQ-L0-NO-RETRIEVAL-001 | code, validator, test, OTEL, artifact, replay, negative-control | Dedicated L0 no-retrieval boundary-guard module + validator + test + OTEL spans + scan artifact proving zero retrieval spans at L0 + replay pair + synthetic L0-retrieval-attempt negative-control. |
| REQ-L1-NO-RETRIEVAL-001 | code, validator, test, OTEL, artifact, replay, negative-control | Same shape, scoped to L1 cognition. |
| REQ-L1-NO-EXECUTE-001 | code, validator, test, OTEL, artifact, replay, negative-control | Same shape, scoped to L1 never-executes-tool-or-model. |

## Suggested Batch Grouping

| Batch | Effort signal | Rows |
|---|---|---|
| **A** | 1 blocker each — quickest wins | 6 |
| **B** | 2 blockers each | 2 |
| **C** | 3 blockers each | 4 |
| **D** | 5 blockers, single row | 1 |
| **E** | 7 blockers each — topology-only contracts | 3 |

## Statement

This document is a static gap inventory derived from the Tier 2
enforcement-gate output. It does not claim any of these rows are
closed, partially closed, or near closure. The Tier 2 enforcement gate
remains BLOCKED. Closure of any row requires the listed proof artifact,
test, or reference to be authored under a separate task.
