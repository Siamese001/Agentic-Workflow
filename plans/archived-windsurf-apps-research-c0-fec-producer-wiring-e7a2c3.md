---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-research-c0-fec-producer-wiring-e7a2c3.md'
original_relative_path: 'apps-research-c0-fec-producer-wiring-e7a2c3.md'
source_sha256: 1a8d90c3739d2a35539d1547f80f40cd20131015f85ff5a1fbd3d7fe35522ab7
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_research C0 FEC Producer Wiring

**Slug:** `apps-research-c0-fec-producer-wiring-e7a2c3`
**Created:** 2026-05-03
**Status:** Completed
**Completed:** 2026-05-03
**Owner:** Cascade
**Pattern source:** `.windsurf/plans/apps-qna-c0-fec-producer-wiring-d4f1e8.md` (Completed) — demonstrated template.

## 1. Problem Statement

`apps_research` is a grounded app (hop pipeline: profile/research/sender/draft/delivery). Its cert path ships `ExitReviewPacket.final_evidence_contract = {}`, so the Exit pipeline's X1D gate falls back to NOT_APPLICABLE and the rubric's FEC-dependent dims can't score. This plan closes BLOCKER #4 for apps_research.

## 2. Goals

- Real FEC producer at `apps_research/cert/fec_producer.py`.
- Side-effect registration via `apps_research/cert/__init__.py`.
- Cert entrypoint in `apps_research/__main__.py` calls `resolve_fec("apps_research", run_ctx)` and populates `final_evidence_contract` before `maybe_invoke_exit_eval`.
- Research-specific FEC fields: `retrieval_sources` extracted from hop research artifacts (sources cited by research_hop); `template_ids` from prompt-assembly manifest; `grounded=True` when research_hop returned non-empty sources.
- 7 contract tests mirroring apps_qna pattern.
- Zero regressions in `tests/_apps_contract/`.

## 3. Non-Goals

- Rewriting the research hop pipeline.
- Rubric dim changes.
- Real LLM-judge calibration.

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | W1.P1–W1.P3 | Producer module + side-effect registration + cert-path wiring + tests | ~7k | ✅ Done | 8/8 tests pass; 374/374 suite green |

## Verification Evidence

- 8 new tests pass; 374/374 apps_contract suite green
- Source ladder: `c0_retrieval_sources` → `hop_citations` → `research_result.hop_citations` → template_only
- Cert entrypoint registers producer + computes FEC via `resolve_fec("apps_research", _run_ctx)` inside `governed_run`

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Producer + registration | `apps_research/cert/{__init__,fec_producer}.py` (new) | Source-id extraction from hop artifacts | 3k | ⏳ Todo |
| W1.P2 | Cert entrypoint wiring | `apps_research/__main__.py` (edit) | Cert path may not yet adopt exit hook — adopt if needed | 2k | ⏳ Todo |
| W1.P3 | Contract tests | `tests/_apps_contract/test_apps_research_fec_producer.py` (new) | Registry-state isolation | 2k | ⏳ Todo |

## 6. Deliverables

- `apps_research/cert/fec_producer.py` — `produce_fec(run_context) -> dict` with schema_version=1.0 shape.
- Forward-compatibility: real sources + templates populate grounded=True when present.
- Tests: registration side-effect, template-only path, grounded path, malformed-inputs-safe, resolver round-trip, mutation isolation, distinct return per call.

## 7. Governance

- Constitutional §6: no Author-Gate required — deterministic pattern replication.
- Fail-soft: producer errors → empty FEC (logged), never break cert bundle.
