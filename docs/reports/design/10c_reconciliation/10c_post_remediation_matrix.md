# 10C Post-Remediation Requirement Matrix

> Generated: 2026-04-30T18:23:07.299226+00:00
> Git HEAD: `1f157bd273090232a681951e43f76b0aad5682ae` (dirty=True)
> Source bundles: `artifacts/requirements/proof_bundles/10c-req-*.json` (200 files)
> Merkle root: `6d49fb6988a6eabe6907eb5a58be469f154a05742046a57296566d3f88b1f940`

## 1. Headline numbers

| Metric | Count |
|---|---:|
| Total rows | **200** |
| EVIDENCE_PRESENT (any depth) | 198 |
| ACCEPTED_WITH_CAVEAT (pedagogical) | 2 |
| Spans seen (expected_span captured) | **0** |
| Composition proofs SATISFIED | **2** |

## 2. actual_proof_depth distribution

| Depth tier | Count | Meaning |
|---|---:|---|
| `E4_NEGATIVE_CONTROL` | 198 | Negative/fail-closed control in metadata; synthetic test fixtures |
| `E5_COMPOSITION_PROOF` | 2 | Production components composed with provenance chain (W2 harness) |

## 3. Harness outcome distribution (W3 sweep)

| outcome | count |
|---|---:|
| `NO_SPANS_EMITTED` | 198 |
| `NO_HARNESS` | 2 |

## 4. Bundles upgraded by W2 composition harnesses

- **10C-REQ-077**: composition SATISFIED, depth=`E5_COMPOSITION_PROOF`. Components reached: 3.
- **10C-REQ-128**: composition SATISFIED, depth=`E5_COMPOSITION_PROOF`. Components reached: 2.

## 5. Honest residuals (per anti-cheat §8)

Most existing `test_10c_req_*.py` tests use synthetic `SpanReceipt` fixtures
(see `tests/fixtures/proof_evidence/otel_span_receipt.py` docstring) and do
not exercise real OTel SDK emit paths. The W1 harness ran cleanly against
all 200 test files but captured zero spans for 198 of them.

This is **honest residual gap**, not a harness defect. Closing the gap
to `E6.5_INTEGRATED_RUNTIME` requires upgrading each affected test to:

1. Install or attach to a real OTel `TracerProvider`
2. Invoke production code (e.g., `L2SpanEmitter.span(...)`) instead of
   constructing synthetic `SpanReceipt`s
3. Assert the captured span matches the expected name + attributes

The W2 composition harness pattern (see `tools/proof/composition_proof_*.py`)
demonstrates one viable approach for individual REQs that justify the work.

## 6. Reproduction

```
# Re-run sweep (idempotent at fixed git HEAD)
python -m tools.proof.sweep_otel_evidence --no-progress

# Re-apply W2 composition results
python -m tools.proof.apply_composition_results

# Re-compute merkle root + regenerate this matrix
python -m tools.proof.regenerate_matrix_and_merkle
```

## 7. Provenance

- Plan: `.windsurf/plans/10c-proof-depth-remediation-a9f9af.md`
- Source overlay: `C:\Users\amita\Documents\10c_requirement_proof_depth_certification_overlay.xlsx`
- W1 harness: `tools/proof/otel_collector_proof.py` + `tools/proof/_pytest_otel_capture_plugin.py`
- W2 composition harnesses: `tools/proof/composition_proof_semantic_cache.py`, `tools/proof/composition_proof_provenance_chain.py`
- W3 sweep tool: `tools/proof/sweep_otel_evidence.py`
- W4+W5 generator: `tools/proof/regenerate_matrix_and_merkle.py` (this script)