# Final resume aggregation product proof — W5–W7

**Status: PARTIAL** — structural aggregation and package X3 disposition are proof-complete; **product ALLOW is correctly blocked** by REVIEW/mock lanes, cross-section WARN policy, and package-level REAL_LLM gates.

## Scope delivered

| Wave | Deliverable | Result |
|------|-------------|--------|
| W5 | Coherent rollup policy + lane compatibility matrix | [coherent_rollup_policy.json](../../artifacts/apps_rg/runtime_proofs/final_resume_assembly/coherent_rollup_policy.json) |
| W6 | REVIEW-lane policy (ALLOW / REVIEW / BLOCKED / MOCK_PLUMBING_ONLY) | [review_lane_policy.json](../../artifacts/apps_rg/runtime_proofs/final_resume_assembly/review_lane_policy.json) |
| W7 | Final assembler + package X3 + receipt v2 | [final_resume_receipt.json](../../artifacts/apps_rg/runtime_proofs/final_resume_assembly/final_resume_receipt.json), [resume_package_receipt.json](../../artifacts/apps_rg/runtime_proofs/resume_package/resume_package_receipt.json) |

## Coherent rollup (W5)

- **Rollup pin:** `coherent_aggregation_pin=true`, date prefix `20260518` via [build_coherent_aggregation_rollup.py](../../tools/apps_rg/build_coherent_aggregation_rollup.py).
- **JD / briefing / base resume:** coherent across lanes (`jd_digest_coherent`, `briefing_digest_coherent`, shared `base_resume_digest`).
- **SRFS / proof pool:** per-lane `proof_pool_digest` differs by section selection; **policy anchor** is shared `proof_pool_ref` to the master fact ledger (ibm_bullets uses base-resume ref — recorded in matrix).
- **Same-run policy:** `same_run_coherent=false` but `same_date_prefix_coherent=true` → **acceptable** with explicit reason: *all lane run_id date prefixes match* under coherent pin.
- **Preflight:** all gates PASS; pool receipts PASS; no `x2_failed > 0`; no blocked X3.

## REVIEW-lane policy (W6)

| Class | Lanes | Product ALLOW |
|-------|-------|---------------|
| ALLOW | unify_narrative, competencies | eligible |
| REVIEW | ibm_bullets | not ALLOW; `product_review_required=true` |
| MOCK_PLUMBING_ONLY | headline, executive_summary, unify_bullets, ibm_narrative | not ALLOW; plumbing/mock |
| BLOCKED | (none) | assembly would fail |

`product_review_required=true` on receipt and package receipt. REVIEW lanes are **not hidden**.

## WARN policy

Cross-section gates: structural PASS with WARN on `x2_cross_section_exact_duplicate`, `x2_cross_section_same_claim_different_wording`, `x2_cross_section_x3_review_present`. **WARN ≠ PASS for product** (`cross_section_x2_product_pass=false`). L2 snapshots were not modified.

## Package X3 (W7)

- **Structural X2:** PASS (`gates_all_pass=true`, `structural_x2_all_pass=true`).
- **Cross-section X2:** structural PASS; product blocked by WARN.
- **Package disposition:** `X3_BLOCKED_DETERMINISTIC_GATES` (OFFLINE_CONTRACT_STUB on headline, unify_bullets, ibm_narrative).
- **product_allow_claimed:** `false` (assembly receipt + package receipt).

## Commands (exit 0)

```text
python -m compileall apps_rg -q
python tools/apps_rg/build_coherent_aggregation_rollup.py --write
python -m apps_rg.runtime.assembly.final_resume_assembler
python -m apps_rg.runtime.package.resume_package_x3
pytest tests/unit/apps_rg -k "aggregation or overlap or final_resume or claim_ledger or run_fingerprint or package_x3" -q --tb=short
pytest tests/_apps_contract -k "apps_rg and (aggregation or overlap or final_resume or claim_ledger or run_fingerprint or cross_section_x2 or package_x3)" -q --tb=short
git diff HEAD -- agentic_core
```

## Explicit non-claims

- JD/briefing digests are targeting coherence only, not runtime proof.
- Structural assembly PASS does not imply product ALLOW.
- R1B section cache was not used.
- `agentic_core` was not modified.
