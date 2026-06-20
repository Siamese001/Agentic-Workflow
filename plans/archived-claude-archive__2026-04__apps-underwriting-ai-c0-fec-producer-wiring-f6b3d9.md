---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-04\\apps-underwriting-ai-c0-fec-producer-wiring-f6b3d9.md'
original_relative_path: '_archive\\2026-04\\apps-underwriting-ai-c0-fec-producer-wiring-f6b3d9.md'
source_sha256: ab789b9fc27f4d42a07d7e3fd32400e2ca9f1677cb8c0bc724396d3a7504e400
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_underwriting_ai C0 FEC Producer Wiring

**Slug:** `apps-underwriting-ai-c0-fec-producer-wiring-f6b3d9`
**Created:** 2026-05-03
**Status:** Completed
**Completed:** 2026-05-03
**Owner:** Cascade
**Pattern source:** `.windsurf/plans/apps-qna-c0-fec-producer-wiring-d4f1e8.md` (Completed).

## 1. Problem Statement

`apps_underwriting_ai` is a grounded app (document-parsing + DecisionPacket-assembly pipeline). Its cert path already adopts `maybe_invoke_exit_eval` (parent plan apps-eval-harness-deferred-e4a1b7 W1), but ships `final_evidence_contract = {}`. Closes BLOCKER #4 for apps_underwriting_ai — the highest-leverage of the 4 remaining because parser-provenance is already extracted and easy to surface as FEC sources.

## 2. Goals

- Real FEC producer at `apps_underwriting_ai/cert/fec_producer.py`.
- Side-effect registration via `apps_underwriting_ai/cert/__init__.py`.
- Update `apps_underwriting_ai/__main__.py` to call `resolve_fec("apps_underwriting_ai", run_ctx)` with parser-derived sources before `maybe_invoke_exit_eval` (currently ships `final_evidence_contract: {}` per `_build_exit_receipts_from_uw_result`).
- Underwriting-specific FEC fields: `retrieval_sources` = parsed document ids / section anchors from `DecisionPacket.provenance`; `template_ids` = decision-template ids; `grounded=True` when parser returned non-empty provenance.
- 7 contract tests.
- Zero regressions in `tests/_apps_contract/`.

## 3. Non-Goals

- Rewriting document parsers.
- Rubric dim changes.
- LLM-judge calibration.

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | W1.P1–W1.P3 | Producer + registration + receipts wiring + tests | ~7k | ✅ Done | 8/8 tests pass; 359/359 suite green |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Producer + registration | `apps_underwriting_ai/cert/{__init__,fec_producer}.py` (new) | DecisionPacket.provenance shape | 3k | ✅ Done |
| W1.P2 | Receipts wiring | `apps_underwriting_ai/__main__.py` `_build_exit_receipts_from_uw_result` (edit) | Preserve fail-soft of existing hook adoption | 2k | ✅ Done |
| W1.P3 | Contract tests | `tests/_apps_contract/test_apps_underwriting_ai_fec_producer.py` (new) | Registry isolation | 2k | ✅ Done |

## 6. Verification Evidence

- `python -m pytest tests/_apps_contract/test_apps_underwriting_ai_fec_producer.py -v` — **8 passed**
- `python -m pytest tests/_apps_contract/ -q` — **359 passed, 0 regressions**
- Source extraction ladder: explicit `c0_retrieval_sources` override → `uw_result.register.rows[].source_doc` → `uw_result.request.statements[].document_id` → empty (template_only)
- Cross-test fix: hardened `test_resolver_round_trip` in BOTH apps_qna + apps_underwriting_ai tests to call `register_producer` explicitly instead of relying on `sys.modules`-cached side-effect import (side-effect fires once per session; `clear_registry` between tests loses it)

## 6. Deliverables

schema_version=1.0 FEC dict; grounded path populated from parser provenance (likely green on first run since parsers already emit provenance); 7 tests.

## 7. Governance

Constitutional §6: deterministic pattern replication. Fail-soft throughout. Exit hook already adopted → smallest edit surface of the 4 remaining apps.
