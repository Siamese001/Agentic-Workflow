---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-qna-c0-fec-producer-wiring-d4f1e8.md'
original_relative_path: 'apps-qna-c0-fec-producer-wiring-d4f1e8.md'
source_sha256: 077a5a062c51d8979908d8f15a6d2592a743fa7d3d72e9321c3e68100fd74d7f
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_qna C0 FEC Producer Wiring

**Slug:** `apps-qna-c0-fec-producer-wiring-d4f1e8`
**Created:** 2026-05-03
**Status:** Completed
**Last Updated:** 2026-05-03
**Owner:** Cascade
**Parent plans:**
- `.windsurf/plans/apps-eval-harness-parity-f8d4a2.md` (Completed — BLOCKER #4 deferred)
- `.windsurf/plans/apps-eval-harness-residual-a2d9c7.md` (Completed — registry landed, producers deferred)

## 1. Problem Statement

`apps_shared.cert.fec_producer` registry has existed since residual-a2d9c7 but
no grounded app registers a real producer. Cert runs ship an empty
`final_evidence_contract = {}`, so the Exit pipeline's X1D gate falls back
to NOT_APPLICABLE and the rubric's FEC-dependent dims can't score.

BLOCKER #4 needs per-app producers for `apps_qna`, `apps_research`, `apps_rfp`,
`apps_exec`, `apps_underwriting_ai`. This plan lands the first one (apps_qna)
as a **demonstrated pattern** the other 4 can copy.

## 2. Goals

- Real FEC producer for apps_qna at `apps_qna/cert/fec_producer.py`.
- Auto-registration via `apps_qna/cert/__init__.py` side-effect import.
- Cert entrypoint (`apps_qna/__main__.py`) populates `ExitReviewPacket.final_evidence_contract` from the producer instead of `{}`.
- Contract tests cover: registration side-effect, template-only path, grounded path (forward-compat for when C0 wires), empty/malformed inputs never raise, resolver round-trip, no shared mutable state.
- Zero regressions in `tests/_apps_contract/`.

## 3. Non-Goals

- Real C0 retrieval wiring — apps_qna remains template-deterministic. Producer is designed to upgrade cleanly when `c0_retrieval_sources` is populated upstream.
- Producers for the other 4 grounded apps — each owns its own per-app plan.
- Rubric dim changes — existing dims consume whatever shape FEC ships.

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1.P1–W1.P3 | Producer + cert wiring + tests | ~6k | Shared registry exists; cert hook adopted | ✅ Done | 7 new tests pass; 319 total green |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | FEC producer module | `apps_qna/cert/fec_producer.py` (new), `apps_qna/cert/__init__.py` (new) | Defensive coercion for malformed context | 3k | ✅ Done |
| W1.P2 | Cert entrypoint wiring | `apps_qna/__main__.py` (edit) | Side-effect import ordering; preserve fail-soft | 1k | ✅ Done |
| W1.P3 | Contract tests + regression sweep | `tests/_apps_contract/test_apps_qna_fec_producer.py` (new) | Registry state leaking across tests | 2k | ✅ Done |

## 6. Verification Evidence

- `python -m pytest tests/_apps_contract/test_apps_qna_fec_producer.py -v` — **7 passed**
- `python -m pytest tests/_apps_contract/ -q` — **319 passed, 0 regressions** (+7 from this plan)
- FEC shape conforms to `ExitReviewPacket.final_evidence_contract` dict contract
- Producer coerces non-Mapping / non-list inputs; never raises
- Each call returns a fresh dict (verified by mutation-isolation test)

## 7. Files Changed

**Created**
- `apps_qna/cert/__init__.py`
- `apps_qna/cert/fec_producer.py`
- `tests/_apps_contract/test_apps_qna_fec_producer.py`

**Modified**
- `apps_qna/__main__.py` — imports `apps_qna.cert` for side-effect registration, calls `resolve_fec("apps_qna", run_ctx)` to populate receipts

## 8. Pattern for Remaining Grounded Apps

Other 4 grounded apps (`apps_research`, `apps_rfp`, `apps_exec`, `apps_underwriting_ai`)
copy this exact shape:

1. `apps_<name>/cert/fec_producer.py` — `produce_fec(run_context) -> dict`
2. `apps_<name>/cert/__init__.py` — side-effect `register_producer("apps_<name>", produce_fec)`
3. In `apps_<name>/__main__.py` cert path: `import apps_<name>.cert` + `resolve_fec("apps_<name>", ctx)` before `maybe_invoke_exit_eval`
4. Tests mirror `test_apps_qna_fec_producer.py` shape

Each app requires its own plan because retrieval-source extraction differs by app.

## 9. Non-Goals Fence

- No C0 retrieval refactor in apps_qna
- No rubric dim changes
- No producers for the other 4 apps (each gets its own plan)
- No real LLM-judge Spearman calibration

## 10. Governance

- Constitutional §6 Author-Gate: no ambiguous decisions — pattern copied from shared registry docstring
- Constitutional §17 Memory: writeback to persistent memory on completion
- Fail-soft: producer errors degrade to empty FEC (logged), never break cert bundle
