# apps_lic Graph-Claim Gate + Judge Re-Scope

plan_format: v2
slug: apps-lic-graph-claim-gate-rescope-c4e1a9
owner: claude (Siamese001)
branch: claude-apps-lic-graph-claims-ssot
created: 2026-06-16

## Wave Status
| Wave | State | Summary |
|---|---|---|
| W1 | COMPLETE | Deterministic draft-level metric-grounding X2 gate (commit 8777ae1264, +co-mingled 1ddde12b4e); 3 new + 37 regression green |
| W2 | COMPLETE | Re-scoped `evidence_claim_support` + `ceo_evidence_overclaim_risk` rubric roles to the non-metric/strategic residual; `rubric_id`/`threshold`/matrix unchanged; 23 tests green. FOLLOW-UP: live-judge recalibration vs human labels before promotion (judge-calibration-cadence) — NOT self-certified. |

## Phase Status
| Phase | State | Summary |
|---|---|---|
| P1 W1 gate | IN_PROGRESS | add `validate_draft_metrics_against_packet` (sender_proof_graph) + `GATE_GENERATED_METRIC_GROUNDED` (validation_exit) |
| P2 W1 tests | TODO | ungrounded metric blocks · grounded-only passes · NOT_APPLICABLE when SSOT down / no graph-linked skills |
| P3 W2 rubric rescope | TODO | narrow overclaim + evidence-support rubrics; flag calibration follow-up |

## Context
The apps_rg `augmented_skills_graph` is the single SSOT for sender claim language + metrics. Commit `bfdd7daf05` made metric-faithfulness deterministic at **corpus load** (curated proof-point `claim_text`). The LLM `ceo_evidence_overclaim_risk` / `evidence_claim_support` judges still nominally cover "is this claim supported" — now largely redundant with the deterministic metric grounding. This plan (W1) extends the deterministic SSOT to the **L2-generated draft** (the under-declaration / generator-drift case corpus-load can't see) and (W2) narrows the judges to their true residual (non-metric framing + target-company strategic claims).

## Files In Scope
- `apps_lic/engines/sender_proof_graph.py` (W1)
- `apps_lic/engines/validation_exit.py` (W1)
- `tests/apps_lic/test_graph_claim_ssot.py` (W1, W2)
- `apps_lic/engines/x1d_judge_policy.py` (W2)
- `apps_lic/config/domain_contract/validation_exit.v1.yaml` + rubric YAMLs (W2)

## W1 — Deterministic draft-level metric-grounding gate
1. `sender_proof_graph.validate_draft_metrics_against_packet(draft_text, *, packet)`: aggregate `apps_rg_skill_ids` across `packet.selected_proof_points`; if the shared SSOT is unavailable OR no graph-linked skills, return NOT_APPLICABLE (fail-soft, consistent with the corpus-load gate); else run `claim_metrics_are_graph_grounded(draft_text, skill_ids)` and return PASS / BLOCKED + ungrounded tokens.
2. `validation_exit.run_x2_validation`: add `GATE_GENERATED_METRIC_GROUNDED`, applicable only when SSOT available + skill links present; block severity; evidence = ungrounded tokens + packet id.

## W2 — Judge rubric re-scope (no judge removed)
1. Narrow `ceo_evidence_overclaim_risk` rubric → non-metric framing over-reach + target-company/strategic claims (drop the metric-support sub-criterion the deterministic gate now owns).
2. Narrow `evidence_claim_support` rubric → non-metric semantic support (a real but unsupported non-numeric claim). Keep it in the policy matrix.
3. Note: rubric changes require judge recalibration before promotion (judge-calibration-cadence) — flag, do not self-certify.

## Definition of Done
1. `validate_draft_metrics_against_packet` runs `claim_metrics_are_graph_grounded` over the selected candidate draft, gated on SSOT availability + graph-linked skills.
2. `GATE_GENERATED_METRIC_GROUNDED` wired into `run_x2_validation`: blocks an ungrounded generated metric; NOT_APPLICABLE when SSOT down / no skill links.
3. W1 unit tests pass: ungrounded metric blocks · grounded-only passes · NA-when-SSOT-absent · NA-when-no-skill-links.
4. W2: `ceo_evidence_overclaim_risk` + `evidence_claim_support` rubrics narrowed to non-metric / strategic residual; no judge removed from the policy matrix; calibration follow-up flagged.
5. Existing apps_lic `validation_exit` + graph-claim test suites stay green (no regression in the other X2 gates).
6. No `agentic_core` edits — change stays in the apps_lic overlay.
