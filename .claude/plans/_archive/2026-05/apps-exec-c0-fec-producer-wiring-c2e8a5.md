# apps_exec C0 FEC Producer Wiring

**Slug:** `apps-exec-c0-fec-producer-wiring-c2e8a5`
**Created:** 2026-05-03
**Status:** Completed
**Completed:** 2026-05-03
**Owner:** Cascade
**Pattern source:** `.windsurf/plans/apps-qna-c0-fec-producer-wiring-d4f1e8.md` (Completed).

## 1. Problem Statement

`apps_exec` is a grounded app (brief-assembly pipeline for executive content). Its cert path ships `final_evidence_contract = {}`; Exit X1D falls back to NOT_APPLICABLE. Closes BLOCKER #4 for apps_exec.

## 2. Goals

- Real FEC producer at `apps_exec/cert/fec_producer.py`.
- Side-effect registration via `apps_exec/cert/__init__.py`.
- Cert entrypoint in `apps_exec/__main__.py` calls `resolve_fec("apps_exec", run_ctx)`.
- Exec-specific FEC fields: `retrieval_sources` = research snippets feeding the brief; `template_ids` = brief-template ids; `grounded=True` when brief-assembly used non-empty sources.
- 7 contract tests.
- Zero regressions in `tests/_apps_contract/`.

## 3. Non-Goals

- Rewriting brief-assembly engine.
- Rubric dim changes.
- LLM-judge calibration.

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | W1.P1–W1.P3 | Producer + registration + cert-path wiring + tests | ~7k | ✅ Done | 7/7 tests pass; 366/366 suite green |

## 6. Verification Evidence

- `python -m pytest tests/_apps_contract/test_apps_exec_fec_producer.py -v` — **7 passed**
- `python -m pytest tests/_apps_contract/ -q` — **366 passed, 0 regressions**
- Source ladder: `c0_retrieval_sources` override → `research_snippets` → empty (template_only)
- Cert path now registers producer via side-effect import + computes FEC via `resolve_fec("apps_exec", _run_ctx)` inside `governed_run` L2_execute span (reserved for future exit-hook adoption)

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Producer + registration | `apps_exec/cert/{__init__,fec_producer}.py` (new) | Snippet-citation extraction | 3k | ⏳ Todo |
| W1.P2 | Cert entrypoint wiring | `apps_exec/__main__.py` (edit) | Cert path may need exit-hook adoption | 2k | ⏳ Todo |
| W1.P3 | Contract tests | `tests/_apps_contract/test_apps_exec_fec_producer.py` (new) | Registry isolation | 2k | ⏳ Todo |

## 6. Deliverables

schema_version=1.0 FEC dict; forward-compat grounded path; 7 tests.

## 7. Governance

Constitutional §6: deterministic pattern replication. Fail-soft throughout.
