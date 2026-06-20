# apps_rg AIG E2E — Wave 0 RCA Receipt

Plan: [apps-rg-aig-e2e-remediation-e4b7c1.md](../../../.codex/plans/apps-rg-aig-e2e-remediation-e4b7c1.md)
Wave: W0 (Evidence Harness & Truthful Instrumentation)
Generated: 2026-06-07

## Branch provenance

- RCA run captured during chat branch `chat/adg-redis-ssot-b9f4c2` (per plan header).
- W0 implementation branch: the active per-chat branch (branch-per-chat). `apps_rg_e2e` is **not** required.

## Selected-provider policy (AIG E2E)

- Target provider: `external_claude`; model `claude-sonnet-4-6`.
- Qwen/vLLM: diagnostic-only; `NOT_APPLICABLE` in external-Claude lanes (preflight already enforces this).

## Preserved RCA artifact paths (git-ignored tree — paths pinned here)

Run root: `artifacts/apps_rg/e2e_aig_apps_rg_e2e_20260607/`

| Probe | Path |
|---|---|
| Dry run | `.../dryrun` |
| Full product run | `.../full_default` |
| Executive summary (all judges) | `.../section_executive_summary_external_all_judges` |
| Competencies (qwen) | `.../section_competencies_qwen` |
| Unify bullets (external) | `.../section_unify_bullets_external` |
| IBM bullets (external) | `.../section_ibm_bullets_external` |
| InsurTech bullets (external) | `.../section_insurtech_bullets_external` |
| Judge transport probe | `.../judge_transport_probe` |

AIG inputs (sha256 pinned in `tests/_apps_contract/test_apps_rg_aig_e2e_fixtures.py`):
- `apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt`
- `apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md`

## Truthful lane matrix (full_default) — via `tools/apps_rg/summarize_e2e_run.py`

This is the W0 summarizer's corrected three-state classification. It replaces the
`integrated_lane_evidence_status.json` roll-up that reported "1 executed / 10 missing"
with all reasons collapsed to `LANE_DISPATCH_EXIT_ERROR`/`exception`.

| Lane | True state | Note |
|---|---|---|
| competencies | EXECUTED_X3_BLOCK | ran to X3_BLOCK (15→ wrongly bucketed as missing by the roll-up); X2 generic-category/lineage gates failed |
| unify_bullets | PRE_RUN_BLOCKED | own exception (ChromaDB use-after-close, E2E-11) |
| ibm_bullets | PRE_RUN_BLOCKED | own exception (`RustBindingsAPI ... no attribute bindings`, E2E-11) |
| headline, executive_summary, unify_narrative, ibm_narrative, insurtech_bullets, insurtech_narrative, ey_bullets, ey_narrative | MISSING_NOT_ATTEMPTED | never attempted — `prior_abort` from the ibm_bullets crash (E2E-05 poisoning) |

Reproduce: `python tools/apps_rg/summarize_e2e_run.py artifacts/apps_rg/e2e_aig_apps_rg_e2e_20260607/full_default`

## W0 deliverables

- `tools/apps_rg/summarize_e2e_run.py` — three-state lane-status summarizer (full + section).
- `apps_rg/runtime/orchestration/section_lane_executor.py` — per-lane exception trace persistence (`section_exception_trace.json` + enriched `dispatch_result`).
- Tests: `tests/unit/apps_rg/test_summarize_e2e_run.py`, `tests/unit/apps_rg/test_section_exception_trace.py`, `tests/_apps_contract/test_apps_rg_aig_e2e_fixtures.py`.
