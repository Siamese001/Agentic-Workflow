# Tier 2 Selection — Step 1 Aggregation

Selection-only artifact. Identifies the next 22 highest-risk REQ_IDs
across U0, L1, L0/L3, C0, PA, L2, Exit, L4/UWG, L5, L6, and E2E that
are NOT already in Tier 0 (17 rows) or Tier 1 (15 rows).

This is **not proof**, **not implementation**, and **not a Tier 2 gate**.
No runtime behavior, replay machinery, OTEL exporter, or proof harness
was executed. No new tests were authored. Tier 2 evidence work is
intentionally deferred.

## Counts

- Tier 0 excluded: 17
- Tier 1 excluded: 15
- Tier 2 selected: **22** (within the 15-25 envelope)

## Surface Coverage

| Surface | Count |
|---|---:|
| U0 | 3 |
| L1 | 3 |
| L0 | 1 |
| L3 | 1 |
| C0 | 2 |
| PA | 2 |
| L2 | 2 |
| Exit | 1 |
| L4 | 2 |
| L5 | 2 |
| L6 | 1 |
| E2E | 2 |

## Risk Category Counts

| Category | Count |
|---|---:|
| authority_bypass | 4 |
| intake_integrity | 2 |
| prompt_boundary | 2 |
| origin_trust | 1 |
| planning_integrity | 1 |
| orchestration_integrity | 1 |
| retrieval_boundary | 1 |
| sandbox_integrity | 1 |
| execution_safety | 1 |
| output_disposition | 1 |
| write_sovereignty | 1 |
| cache_integrity | 1 |
| schema_integrity | 1 |
| gate_integrity | 1 |
| learning_firewall | 1 |
| proof_false_confidence | 1 |
| audit_traceability | 1 |

## Selected REQ_IDs by Priority Rank

| Rank | REQ_ID | Surface | Strength | Risk Category |
|---:|---|---|---|---|
| 1 | REQ-U0-VALIDATED-REQUEST-HANDOFF-001 | U0 | ONLY | intake_integrity |
| 2 | REQ-U0-ANTI-BYPASS-001 | U0 | MUST_NOT | intake_integrity |
| 3 | REQ-U0-ORIGIN-TRUST-INJECTION-001 | U0 | MUST | origin_trust |
| 4 | REQ-L1-PLAN-CONTRACT-HANDOFF-001 | L1 | ONLY | planning_integrity |
| 5 | REQ-L1-NO-RETRIEVAL-001 | L1 | MUST_NOT | authority_bypass |
| 6 | REQ-L1-NO-EXECUTE-001 | L1 | MUST_NOT | authority_bypass |
| 7 | REQ-L0-NO-RETRIEVAL-001 | L0 | MUST_NOT | authority_bypass |
| 8 | REQ-L3-L2-STEP-HANDOFF-001 | L3 | MUST | orchestration_integrity |
| 9 | REQ-C0-EVIDENCE-FETCH-001 | C0 | ONLY | retrieval_boundary |
| 10 | REQ-C0-NO-EXECUTE-001 | C0 | MUST_NOT | authority_bypass |
| 11 | REQ-PA-PROVIDER-AWARE-RENDER-001 | PA | ONLY | prompt_boundary |
| 12 | REQ-PA-AIRLOCK-SECURITY-001 | PA | MUST | prompt_boundary |
| 13 | REQ-L2-PTC-SANDBOX-001 | L2 | MUST | sandbox_integrity |
| 14 | REQ-L2-VERIFY-THEN-EXECUTE-001 | L2 | MUST | execution_safety |
| 15 | REQ-EXIT-NO-OVERLAP-RUNTIME-GATES-001 | Exit | MUST_NOT | output_disposition |
| 16 | REQ-L4-RETRIEVAL-SURFACE-001 | L4 | MUST_NOT | write_sovereignty |
| 17 | REQ-L4-CACHE-STATE-001 | L4 | ONLY | cache_integrity |
| 18 | REQ-L5-RISK-TIER-BANDS-001 | L5 | ONLY | schema_integrity |
| 19 | REQ-L5-HITL-RECLEARANCE-001 | L5 | MUST | gate_integrity |
| 20 | REQ-L6-SIGNAL-FUSION-RCA-001 | L6 | ONLY | learning_firewall |
| 21 | REQ-E2E-MUTATION-BOUNDARY-001 | E2E | MUST | proof_false_confidence |
| 22 | REQ-E2E-CONTRACT-EMISSION-001 | E2E | MUST | audit_traceability |

The full per-row detail (source matrix, requirement text, why_tier2, and
the four likely-gap fields — test, artifact, replay, negative-control)
lives in `TIER2_SELECTION.json` next to this file.

## Statement

No proof claims are made. Selection only. No Tier 2 gate is created here.
