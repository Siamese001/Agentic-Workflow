---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\runtime-cert-hardened-w0-deferred-scope.md'
original_relative_path: 'runtime-cert-hardened-w0-deferred-scope.md'
source_sha256: f966ac472d928c855d677dc31fbe3f9bbcaa10d6b19a65e6dc3ebf9fd55a18f6
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Runtime Certification Hardened Matrix — Deferred Scope

- Plan slug: `runtime-cert-hardened-w0-deferred-scope`
- Parent plan: `runtime-cert-hardened-w0-7e3c9a` (W0-W4 COMPLETE)
- Status: W5 Complete, W6-W8 Remaining (deferred scope)
- Tier: T3
- Created: 2026-05-08

## Summary

This plan captures all deferred scope from the completion of `runtime-cert-hardened-w0-7e3c9a.md`. The parent plan successfully delivered W0-W4 (certification matrix through G-1/G-29 gates). This deferred plan contains the remaining waves that were out of scope for the initial delivery but are required for full 100% hardened certification.

## Deferred Scope (W5-W8 + Future)

| Wave | Phase IDs | Focus | Est. Tokens | Blocking On | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W5 | W5.1-W5.4 | Merkle root finalization + artifact chain | ~15k | W4 G-1/G-29 proven | ✅ DONE | Per prompt §117-120 |
| W6 | W6.1-W6.4 | Certification reports + closeout docs | ~15k | W5 done | Pending | Per prompt §121-125 |
| W7 | (deferred) | Final certification language gate | ~15k | W6 done | Not Started | Per prompt §126-130 |
| W8 | (deferred) | Full 100% hardened certification stamp | ~15k | W7 done | Not Started | Per prompt §131-138 |

## W5 Detail — Merkle Root Finalization (§117-120)

**Requirements:**
- RTC-REQ-031: Merkle root non-empty and complete
- RTC-REQ-122: Merkle tree depth ≥ 3
- RTC-REQ-123: Artifact payload hash recomputation (DONE in W0 - extend)
- RTC-REQ-124: All artifacts indexed in merkle tree

**Deliverables:** ✅ ALL DELIVERED
- `ops_scripts/ci/verify_merkle_root.py` — verify tree depth and completeness ✅
- `ops_scripts/ci/verify_merkle_consistency.py` — verify no duplicate/hollow nodes ✅
- `tests/runtime/test_merkle_finalization.py` — merkle tree validation tests ✅
- Evidence artifacts: `merkle_tree.json`, `merkle_root.txt` ✅

**Requirements Met:**
- RTC-REQ-031: Merkle root non-empty and complete ✅
- RTC-REQ-122: Merkle tree depth ≥ 3 ✅
- RTC-REQ-124: All artifacts indexed, no duplicates/hollow nodes ✅

**Deferred Reason:** Requires W0-W4 evidence artifacts to be stable before merkle tree can be finalized.

## W6 Detail — Certification Reports (§121-125)

**Requirements:**
- RTC-REQ-125: Certification report generation
- RTC-REQ-126: Proof bundle assembly
- RTC-REQ-127: Downgraded rows report (DONE in W0 - extend)
- RTC-REQ-128: Gap analysis report

**Deliverables:**
- `scripts/generate_certification_report.py` — HTML/markdown report generation
- `scripts/assemble_proof_bundle.py` — zip/tar of all evidence
- `tests/runtime/test_certification_reports.py` — report validation
- Output: `docs/reports/certification_report_YYYY-MM-DD.html`

**Deferred Reason:** Requires W5 merkle finalization for complete report.

## W7 Detail — Final Language Gate (§126-130)

**Requirements:**
- RTC-REQ-129: "100% hardened" certification language validator
- RTC-REQ-130: Forbidden term detection ("runtime certified", "certified", etc.)
- RTC-REQ-131: Evidence summary generation
- RTC-REQ-132: Final signoff checklist

**Deliverables:**
- `scripts/verify_certification_language.py` — validate no prohibited terms
- `scripts/verify_final_signoff.py` — checklist validation
- `tests/runtime/test_certification_language.py` — language gate tests
- GATES.md update with G-1/G-29 redaction status

**Deferred Reason:** Requires W6 reports for final language validation.

## W8 Detail — 100% Certification Stamp (§131-138)

**Requirements:**
- RTC-REQ-133: Final certification stamp generation
- RTC-REQ-134: Signed certification bundle (mock sig for CI)
- RTC-REQ-135: Certification registry entry
- RTC-REQ-136: Public attestation placeholder
- RTC-REQ-137: CI pipeline final gate
- RTC-REQ-138: Certification lock (read-only after stamp)

**Deliverables:**
- `scripts/generate_certification_stamp.py` — stamp file generation
- `scripts/verify_certification_lock.py` — verify read-only state
- `tests/runtime/test_certification_stamp.py` — stamp validation
- Final artifacts: `CERTIFICATION_STAMP.json`, `ATTESTATION.md`

**Deferred Reason:** Requires all previous waves for final stamp.

## Non-Goals (Explicitly Out of Scope)

1. **Real cryptographic signatures** — Mock signatures only for CI
2. **External attestation services** — Placeholder documentation only
3. **Production OTel collector** — W3 probes verify presence, not production config
4. **BGE-M3 production deployment** — W1 probes verify model, not prod infra
5. **New requirement rows beyond 86** — CSV is bound at 86 rows
6. **Waves beyond W8** — W8 is the certification completion boundary

## Success Criteria

- [ ] W5: Merkle tree validates with depth ≥ 3, all artifacts indexed
- [ ] W6: Certification report generates with all proof bundles
- [ ] W7: Language gate passes (no prohibited terms in any artifact)
- [ ] W8: Certification stamp generates, CI gate passes, lock engaged

## Dependency Chain

```
W0 (matrix) → W1 (cache) → W2b (live) → W3 (otel) → W4 (gates) → W5 (merkle) → W6 (reports) → W7 (language) → W8 (stamp)
     ✅              ✅            ✅            ✅            ✅            ❌            ❌            ❌            ❌
```

## Implementation Notes

- This plan should be activated when parent plan W0-W4 is proven stable
- Estimated total effort: ~60k tokens (4 waves × 15k each)
- All verifiers should follow W0 pattern: fail-closed with honest outcomes
- Evidence artifacts must be compatible with W0-W4 existing structure

## References

- Parent plan: `.windsurf/plans/runtime-cert-hardened-w0-7e3c9a.md`
- Source CSV: `docs/reference/contracts/certification/runtime_certification_requirements_100_percent_hardened.csv`
- Implementation prompt: `docs/reference/windsurf_runtime_certification_implementation_prompt.md`
- GAPS.md: `artifacts/runtime/requirements_proof/GAPS.md`

---

**DEFERRED_SCOPE_CAPTURED:** 2026-05-08  
**ACTIVATION_TRIGGER:** Parent plan W0-W4 proven stable in production
