# W1 Phase 6 — Requirement-Architecture Alignment Report

**Date:** 2026-04-30
**Scope:** Semantic cache reuse certification matrix
**Author-Gate predecessor:** `artifacts/certification/author_gate_w1p5_decision.json` (APPROVED)

## Summary

W1p5 introduced a layered safety-veto architecture (lexical pre-veto + LLM-judge)
for semantic cache reuse and the user approved C-primary as the sanctioned W1
path on 2026-04-30. The certification matrix, however, still modeled semantic
cache reuse as a single dense-similarity proof. W1p6 closes that mismatch:

- **Old requirement interpretation (RTC-REQ-055):** A cache reuse is "safe" iff
  dense cosine similarity above the configured threshold produces correct
  semantic equivalence. The `R1B_PRODUCTION_THRESHOLD_PROOF` subclaim gates this
  row and has remained `CALIBRATION_GAP` since W1p4 because SEMCACHE-THRESH-001
  is `PENDING_APPROVAL`.

- **New requirement interpretation (RTC-REQ-059):** A cache reuse is "safe" iff
  (a) an approved model produces dense candidates, and (b) a fail-closed safety
  veto blocks near-miss false positives before reuse. The dense threshold is
  reclassified as a **candidate-generation** gate — its role is to admit pairs
  into the veto pipeline, not to assert final semantic equivalence.

Both rows coexist. RTC-REQ-055 keeps its W1p4 finding verbatim and continues to
report `PARTIAL`. RTC-REQ-059 carries the new architecture and may be certified
`ACCEPTED` on its own evidence.

## Why dense-only threshold proof remains CALIBRATION_GAP

The W1p4 finding (see `.claude/plans/rtc-w1-phase4-threshold-adr-b4c9e1.md`
and `docs/architecture/adr/SEMCACHE-THRESH-001.md`) documented that at the
current configured threshold of 0.95, the sweep on the calibration dataset
produces false positives on the adversarial lexical-overlap and opposite-intent
classes. Lowering the threshold was explicitly not approved. Raising it
destroys recall. The SEMCACHE-THRESH-001 ADR is therefore still
`PENDING_APPROVAL`.

That finding has not changed. The composer still reports
`R1B_PRODUCTION_THRESHOLD_PROOF = CALIBRATION_GAP`. Overwriting it would silently
erase W1p4 evidence — forbidden.

## Why dense+veto safe reuse may be certified separately

The veto layer (`R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF = PASS`) now catches the
same adversarial false positives that make the dense-only threshold
unreachable. Evidence:

- Probe `probe_semantic_cache_veto.py`:
  - `primary_veto_mode = C_PRIMARY_LLM_JUDGE`
  - `llm_judge_invocation_count > 0` (LLM judge actually ran, not bypassed)
  - `rubric_hash` recorded (deterministic rubric version)
  - `false_negatives = 0` (no adversarial pair escaped)

- Probe `probe_threshold_sweep_with_veto.py` `metrics_table` at the configured
  threshold:
  - `unsafe_fp_count = 0` (no unsafe reuses admitted)
  - `hard_negative_allowed_count = 0` (no adversarial pairs passed through)

- Fail-closed invariants (tests in
  `tests/runtime/test_veto_fail_closed.py` — 15/15 pass):
  - LLM judge timeout blocks reuse
  - LLM judge malformed output blocks reuse
  - LLM judge `UNCERTAIN` verdict blocks reuse
  - Unrecognized verdict values block reuse
  - Lexical bypass: LLM judge alone still catches hard negatives
  - Author-Gate-pending prevents `PASS` classification

- Author-Gate approval recorded at
  `artifacts/certification/author_gate_w1p5_decision.json` with explicit
  scope clauses that this approval does **not** extend to:
  - SEMCACHE-THRESH-001 recalibration
  - Integrated runtime / OTEL / replay certification
  - RTC-REQ-055 `ACCEPTED` status

These invariants are orthogonal to the dense-threshold equivalence question.
Safety is a property of (candidate generation + veto), not of the threshold
alone. A new requirement captures that decomposition.

## Subclaim taxonomy (post-W1p6)

```
LEGACY_RTC_REQ_055_SUBCLAIMS — gates RTC-REQ-055/056/057/058
  ├── R1B_DENSE_SIMILARITY_COMPOSITION_PROOF       (inherits threshold=CALIBRATION_GAP)
  ├── R1B_APPROVED_MODEL_PROOF
  ├── R1B_PRODUCTION_THRESHOLD_PROOF               (CALIBRATION_GAP — W1p4 pinned)
  ├── R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF
  ├── R1B_NEGATIVE_CONTROL_PROOF
  ├── R1B_TERMINAL_EXIT_PROOF
  └── R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF          (W1p5 addition)

RTC_REQ_059_SUBCLAIMS — gates RTC-REQ-059 (new)
  ├── R1B_SAFE_REUSE_COMPOSITE_PROOF                (W1p6 — new)
  ├── R1B_APPROVED_MODEL_PROOF
  ├── R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF
  ├── R1B_NEGATIVE_CONTROL_PROOF
  ├── R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF
  └── R1B_TERMINAL_EXIT_PROOF

NOT in RTC_REQ_059 gating:
  × R1B_DENSE_SIMILARITY_COMPOSITION_PROOF  (inherits threshold, not needed for safety)
  × R1B_PRODUCTION_THRESHOLD_PROOF          (role: candidate-gen, not equivalence)
```

## R1B_SAFE_REUSE_COMPOSITE_PROOF — PASS conditions

Emitted `PASS` only when **all** of:

1. `R1B_APPROVED_MODEL_PROOF = PASS`
2. `R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF = PASS`
3. `R1B_NEGATIVE_CONTROL_PROOF = PASS`
4. `R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF = PASS`
5. `R1B_TERMINAL_EXIT_PROOF = PASS`
6. `threshold_sweep_results_with_veto.metrics_table` at configured threshold
   shows `unsafe_fp_count = 0`
7. Same row shows `hard_negative_allowed_count = 0`
8. `veto_evaluation_report.metrics.false_negatives = 0`

Any `UNKNOWN`/`ERROR`/timeout/parse-failure in veto invocation counters is
already fail-closed by construction (`VetoStatus.is_blocking()` returns True
for all of these), so veto evidence cannot reach `PASS` if these occur.

## Matrix changes

| Item | Before W1p6 | After W1p6 |
|---|---|---|
| Canonical row count | 86 | 87 |
| `CANONICAL_REQUIREMENT_COUNT` | 86 | 87 |
| Rows added | — | `RTC-REQ-059` |
| Rows modified | — | None (RTC-REQ-055 unchanged) |
| Subclaims added | — | `R1B_SAFE_REUSE_COMPOSITE_PROOF` |
| Subclaim catalog order | ALL includes 6+veto | ALL includes 6+veto+composite |
| Legacy gating | `CORE_SUBCLAIMS` | `LEGACY_RTC_REQ_055_SUBCLAIMS` (new name, same contents) |

## Verifier chain — post-W1p6 (no `--allow-missing-evidence`)

```
compose_semantic_cache_subclaims.py                 exit 0
verify_semantic_cache_certification.py --strict     exit 1  (RTC-REQ-055 PARTIAL retained)
verify_runtime_certification_acceptance.py          exit 0  (87/87 legal)
verify_runtime_certification_matrix.py              exit 0  (87 rows, sha 37bcaa4d7551)
verify_source_divergence.py                         exit 0  (4 peers agree, 0 divergences)
```

Final row statuses:

| Row | `final_acceptance_status` | `actual_proof_depth` | Notes |
|---|---|---|---|
| RTC-REQ-055 | PARTIAL | E0_REQUIREMENT_TEXT | Dense-only legacy; W1p4 CALIBRATION_GAP preserved |
| RTC-REQ-056 | PENDING | E0_REQUIREMENT_TEXT | Runtime scope not claimed |
| RTC-REQ-057 | PENDING | E0_REQUIREMENT_TEXT | OTEL scope not claimed |
| RTC-REQ-058 | PENDING | E0_REQUIREMENT_TEXT | Replay scope not claimed |
| **RTC-REQ-059** | **ACCEPTED** | **E5_COMPOSITION_PROOF** | **New safe-reuse composite proof** |

## Anti-cheat invariants preserved

- RTC-REQ-055 acceptance caveat still names `R1B_PRODUCTION_THRESHOLD_PROOF:CALIBRATION_GAP` — the W1p4 finding is not hidden
- Threshold ADR SEMCACHE-THRESH-001 is still `PENDING_APPROVAL`
- No threshold override env var is set or tolerated
- Dataset v2.0 (100 pairs, 6 classes) remains intact — no adversarial pairs removed
- RTC-REQ-059 `ACCEPTED` status is earned via independent evidence, not by inheritance from the dense-only path
- W2 (integrated runtime), W3 (OTEL/replay), and W4 (full cert) scopes all remain unclaimed

## References

- Author-Gate decision: `artifacts/certification/author_gate_w1p5_decision.json`
- Veto policy: `artifacts/certification/semantic_cache_veto_policy.json`
- Threshold ADR (unchanged): `docs/architecture/adr/SEMCACHE-THRESH-001.md` (status: PENDING_APPROVAL)
- Subclaim catalog: `agentic_core/runtime/prove_requirements/r1b_subclaim_schema.py`
- Composer rule 9: `scripts/compose_semantic_cache_subclaims.py::_map_safe_reuse_composite_proof`
- Hardened CSV: `docs/reference/contracts/certification/runtime_certification_requirements_100_percent_hardened.csv` (87 rows)
- Evidence probes: `tools/certification/evidence/probe_semantic_cache_veto.py`, `probe_threshold_sweep_with_veto.py`
- Tests: `tests/runtime/test_safe_reuse_composite.py` (new), `tests/runtime/test_veto_fail_closed.py` (unchanged, 15/15 pass)
