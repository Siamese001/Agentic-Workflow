# Final resume aggregation hardening W1–W4

**Generated:** 2026-05-18T23:23:00Z  
**Status:** PASS (with coherent rollup pin — see operator note)

## Summary

Implemented W1–W4 aggregation hardening under `apps_rg/runtime/aggregation/` and wired into [final_resume_assembler.py](apps_rg/runtime/assembly/final_resume_assembler.py):

| Wave | Deliverable |
|------|-------------|
| W1 | [run_fingerprint.py](apps_rg/runtime/aggregation/run_fingerprint.py), [preflight.py](apps_rg/runtime/aggregation/preflight.py) — orchestration fingerprint + fail-closed preflight |
| W2 | [section_sealed_index.py](apps_rg/runtime/aggregation/section_sealed_index.py) — `section_digest`, extended `source_artifact_refs` (usage ledger, pool receipt, claim ledgers, proof_pool) |
| W3 | [cross_section_x2.py](apps_rg/runtime/aggregation/cross_section_x2.py) — overlap classes + kept/removed ledgers (L2 snapshots unchanged) |
| W4 | Receipt v2, sidecar artifacts, contract tests |

## Operator note (coherent rollup)

Default per-lane `latest_successful_real` pointers may lack `x2_source_fact_pool_receipt.json` or mix run dates. Before assembly proof:

```bash
python tools/apps_rg/build_coherent_aggregation_rollup.py --write
python -m apps_rg.runtime.assembly.final_resume_assembler
```

## Runtime proof (this pass)

```text
python tools/apps_rg/build_coherent_aggregation_rollup.py --write  → exit 0
python -m apps_rg.runtime.assembly.final_resume_assembler          → exit 0, gates_all_pass=True
orchestration_id=c55e027a27c6f2a6d500fac33677bb77
final_resume_hash=f3329b586891c8e39b85114789727cab867e74501067b651c72c18c3f852e0cf
```

## Fail-closed gates

| Gate family | Blocks assembly when |
|-------------|----------------------|
| Preflight | Missing proof artifacts, pool receipt not PASS, section x2_failed>0, blocked X3, product_quality FAIL under REVIEW |
| Structural `final_resume_x2` | Section order/snapshot/hash/digest (unchanged + `x2_section_digest_present`) |
| Cross-section X2 | FAIL verdict only (exact duplicate advisory WARN; repeated_metric FAIL if ≥3 sections) |

## JD / briefing

Usage ledgers mark JD/briefing as `TARGETING_INPUT` / `CONTEXT_INPUT`. Fingerprint records coherent `jd_digest` / `briefing_digest` across lanes. Assembly does not ingest JD text as proof.

## Overlap policy

- **kept/removed/rewritten** ledgers are audit-only; embedded `l2_output_snapshot` is never stripped.
- **exact_duplicate** → WARN (count recorded); escalate to FAIL when product policy requires.
- **same_claim_different_wording**, **near_duplicate** → WARN.
- **repeated_metric** (≥3 sections) → FAIL.

## Explicit non-claims

- `product_allow_claimed: false` on receipt v2.
- REVIEW X3 lanes may be present; not product ALLOW.
- Does not invoke R1B section cache.
- `agentic_core` untouched.

Machine-readable: [final_resume_aggregation_hardening_w1_w4_manifest.json](final_resume_aggregation_hardening_w1_w4_manifest.json)
