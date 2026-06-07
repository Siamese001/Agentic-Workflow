# L7 Route-Family Closure — Certify Remaining 8/9 Families

> **Plan slug**: `l7-route-family-closure-d3e8f1`
> **Plan path**: `.windsurf/plans/l7-route-family-closure-d3e8f1.md`
> **Parent plan**: `agentic-core-signoff-hardening-b8e2c4` (AUTHORITY.md §4 deferral)
> **Status**: Completed — 2026-05-03

PLAN_CREATED: slug=l7-route-family-closure-d3e8f1 path=.windsurf/plans/l7-route-family-closure-d3e8f1.md

## 1. Background

The agentic_core certification bundle (`trust_level: SIGNED_PROOF`) declares L7 scope as
1/9 route families certified + 1/9 fixture_only + 8/9 not_certified. This is self-declared in
every per-chain spine proof via `l7_route_family_coverage_summary`.

The per-chain proof verifier is `ops_scripts.ci.verify_agentic_core_l7_route_family_coverage`,
and 13 L7 evidence files already exist under
`certification/agentic_core/integrated_runtime/<chain>_latest/fortknox_l7_evidence/`
(RTC-REQ-070, 071, 080, 081, 090–097, 123 — covering assertions like
`no_direct_durable_write_from_L2`, L7_AUDITABILITY controls).

The gap is that 8 of the 9 route families have no completed spine proof producing
`certification_status: certified`. The 1 certified family and 1 fixture_only family already pass.

## 2. Scope

### 2.1 In scope

- Identify the 9 L7 route families and determine which 1 is certified and which 8 are not.
- For each of the 8 not_certified families: author or run the required spine harness to produce
  `certification_status: certified` evidence, produce `l7_evidence/*.json` artifacts, and emit
  the required assertions.
- Recompile the bundle against the new evidence; re-sign; verify both verifiers exit 0.
- Update `certification/agentic_core/AUTHORITY.md` to reflect new L7 coverage (9/9 certified).

### 2.2 Out of scope

- Per-component agentic_core standalone harnesses (separate plan `agentic-core-standalone-harnesses-f2c7a9`).
- Changes to apps_rg overlay evidence rows.
- OTEL collector receipt (separate plan `otel-collector-cert-receipt-b4d2e6`).

## 3. Files In Scope

### Read
- `certification/agentic_core/integrated_runtime/*/fortknox_l7_evidence/*.json` (13 existing files)
- `certification/agentic_core/integrated_runtime/*/agentic_core_spine_proof.json` (per-chain proofs, `l7_route_family_coverage_summary`)
- `ops_scripts/ci/verify_agentic_core_l7_route_family_coverage.py` (coverage verifier)
- `certification/requirements_source.json` (RTC-REQ-07x, 08x, 09x, 12x L7 rows)
- `certification/evidence_assertions.jsonl`

### Write
- New `l7_evidence/*.json` per not_certified family (one per chain, per family)
- New assertions in `certification/evidence_assertions.jsonl`
- Updated `certification/agentic_core/compiler_output/*` (rebuilt signed bundle)
- Updated `certification/agentic_core/AUTHORITY.md` (L7 coverage section)

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | P1.1 | Map 9 route families; identify 8 not_certified; read coverage verifier contract | ~4k | Planned | Table: family name → current status → required harness/evidence type |
| W2 | P2.1–P2.8 | Author L7 evidence + assertions for each of the 8 not_certified families | ~30k | Planned | Each family: `l7_evidence/*.json` on disk; assertion emitted; verifier accepts |
| W3 | P3.1, P3.2 | Recompile + re-sign + verify | ~4k | Planned | `l7_route_family_coverage_summary.certified == 9`; bundle verifier PASS; signature VERIFIED |
| W4 | P4.1 | Update AUTHORITY.md + closeout report | ~3k | Planned | AUTHORITY.md §2.2 updated; closeout report at `docs/reports/runtime_cert/l7_closure/<YYYY-Www>.md` |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Map route families | Read spine proofs + coverage verifier | Families may be identified by route_id string or enum — need to reconcile | ~4k | Planned |
| P2.1–P2.8 | L7 evidence per family (×8) | One evidence JSON + one assertion per family per chain | Per-family harness may require running the spine for that route family | ~4k each | Planned |
| P3.1 | Recompile bundle | `certification/evidence_assertions.jsonl` + compiler | Freshness windows on assertions may require re-running within the window | ~2k | Planned |
| P3.2 | Re-sign + verify | `tools/cert/sign_with_ephemeral_key.py` + both verifiers | git_dirty flag; use `--allow-dirty-git` or commit first | ~2k | Planned |
| P4.1 | AUTHORITY.md + closeout | `certification/agentic_core/AUTHORITY.md` + closeout report | — | ~3k | Planned |

## 6. Success Criteria

- [ ] `l7_route_family_coverage_summary.certified == 9` in all per-chain spine proofs.
- [ ] All 13+ L7 evidence files pass the coverage verifier.
- [ ] Bundle recompiled; 102 rows still SIGNED_OFF; bundle verifier PASS; signature VERIFIED.
- [ ] `certification/agentic_core/AUTHORITY.md` §2.2 updated to 9/9 certified.
- [ ] Closeout report written at `docs/reports/runtime_cert/l7_closure/<YYYY-Www>.md`.

## 7. References

- Parent plan `agentic-core-signoff-hardening-b8e2c4` — AUTHORITY.md §4 deferral
- `certification/agentic_core/integrated_runtime/latest/fortknox_l7_evidence/` — existing evidence
- `ops_scripts/ci/verify_agentic_core_l7_route_family_coverage.py` — coverage verifier
- Constitutional §32 (Fort Knox certification integrity)
