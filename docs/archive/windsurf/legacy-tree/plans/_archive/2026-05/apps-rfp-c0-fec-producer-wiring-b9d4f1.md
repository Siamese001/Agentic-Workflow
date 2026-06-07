# apps_rfp C0 FEC Producer Wiring

**Slug:** `apps-rfp-c0-fec-producer-wiring-b9d4f1`
**Created:** 2026-05-03
**Status:** Completed
**Completed:** 2026-05-03
**Owner:** Cascade
**Pattern source:** `.windsurf/plans/apps-qna-c0-fec-producer-wiring-d4f1e8.md` (Completed).

## 1. Problem Statement

`apps_rfp` is a grounded app (hop proposal-assembly pipeline). Its cert path ships `final_evidence_contract = {}`; Exit X1D falls back to NOT_APPLICABLE. Closes BLOCKER #4 for apps_rfp.

## 2. Goals

- Real FEC producer at `apps_rfp/cert/fec_producer.py`.
- Side-effect registration via `apps_rfp/cert/__init__.py`.
- Cert entrypoint in `apps_rfp/__main__.py` calls `resolve_fec("apps_rfp", run_ctx)`.
- RFP-specific FEC fields: `retrieval_sources` = RFP document sections cited; `template_ids` = proposal-template ids; `grounded=True` when proposal-assembly hop returned citations.
- 7 contract tests.
- Zero regressions in `tests/_apps_contract/`.

## 3. Non-Goals

- Rewriting proposal-assembly engine.
- Rubric dim changes.
- LLM-judge calibration.

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | W1.P1–W1.P3 | Producer + registration + cert-path wiring + tests | ~7k | ✅ Done | 8/8 tests pass; 400/400 suite green |

## Verification Evidence

- 8 new tests pass; 400/400 apps_contract suite green
- apps_rfp had the exit hook + seam already adopted (seam marker in `_build_exit_receipts`); this plan filled the seam via new `_build_fec_for_receipts()` helper calling `resolve_fec("apps_rfp", run_ctx)` with fail-soft exception handling
- Source ladder: `c0_retrieval_sources` → `rfp_sections_cited` → `proposal_result.sections_cited` → template_only
- Closes BLOCKER #4 for apps_rfp — FEC now flows into `maybe_invoke_exit_eval` instead of empty dict

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Producer + registration | `apps_rfp/cert/{__init__,fec_producer}.py` (new) | Section-citation extraction | 3k | ⏳ Todo |
| W1.P2 | Cert entrypoint wiring | `apps_rfp/__main__.py` (edit) | Cert path may need exit-hook adoption | 2k | ⏳ Todo |
| W1.P3 | Contract tests | `tests/_apps_contract/test_apps_rfp_fec_producer.py` (new) | Registry state isolation | 2k | ⏳ Todo |

## 6. Deliverables

schema_version=1.0 FEC dict; forward-compat grounded path; 7 tests mirroring apps_qna shape.

## 7. Governance

Constitutional §6: deterministic pattern replication. Fail-soft throughout.
