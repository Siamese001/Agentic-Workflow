---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\active_backlog_scope_tests_receipt_20260525.md'
original_relative_path: 'active_backlog_scope_tests_receipt_20260525.md'
source_sha256: 1be70d30f714914ceb49a50560d484765e12a1bd8b145145f337b41c668c7e84
recovered_status: LOST_RECOVERED
last_commit: 'a9605090f30'
last_commit_date: '2026-05-24 20:01:19 -0400'
created_date: '2026-05-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Active backlog scope tests — receipt (2026-05-25)

**Manifest:** [active_in_progress_plans_manifest_20260524.md](active_in_progress_plans_manifest_20260524.md)

## Summary

| Bucket | Result |
|--------|--------|
| Contract tests (no live vLLM) | **PASS** — spine PA, no-second-pipeline, x3 finalize, operator outcomes, spine c0 w4/harden (52+ passed in subset) |
| Live subprocess CLI (`test_exec_summary_cli.py`) | **BLOCKED** — `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB` forbidden; needs live qwen_vllm or harness update |
| FEC w5a wire parametrized | **BLOCKED** — `CHROMA_PERSIST_DIR` required for C0.2 hybrid (14 tests) |
| L5 hotspot ratchet | **BLOCKED** — no `artifacts/adg/adg_indexed_*.sqlite` with `mv_hotspot_centrality` |
| Single-spine CI gate | **PASS** — 0 ERROR findings |

## Commands

```text
python ops_scripts/ci/check_apps_rg_single_spine.py -> 0 ERROR
python -m pytest tests/_apps_contract/test_apps_rg_governed_pa_w5.py \
  tests/_apps_contract/test_apps_rg_no_second_pipeline.py \
  tests/unit/apps_rg/test_section_x3_finalize.py \
  tests/_apps_contract/test_executive_summary_operator_outcomes.py -q -> PASS
python -m pytest tests/_apps_contract/test_exec_summary_cli.py -q -> 10 FAIL (stub/vLLM policy)
python ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py -> FAIL (no ADG mv table)
```

## Closeouts completed (disk + Notion)

| Slug | Rationale |
|------|-----------|
| `apps-rg-runtime-substitute-burndown-c4e8f1` | W0–W8 contract closeout; polish deferred |
| `exec-summary-targeting-wiring-closeout-b9e2a4` | W1–W4 wiring + parity proof 233409 |
| `exec-summary-operator-ship-a3f7c2` | Already COMPLETE disk; Notion reconciled |

## Remain In Progress (engineering DoD not met)

| Slug | Open seam |
|------|-----------|
| `apps-rg-spine-only-unification-d8f4a2` | W5 whole-run L3+assembly in spine |
| `apps-rg-proof-pool-c0-ssot-a7f3e2` | Track C5 `X3_ALLOW`; W0–W4 FEC waves |
| `apps-rg-resume-assembly-debt-burndown-56c022` | W4–W5 offline demotion |
| `apps-rg-legacy-dependency-burndown-b7e4a2` | D3 partial, Phase E |
| `l5-fanin-architecture-reduction-e7c4a2` | Ratchet exit after ADG regen |

## Test fix in this session

- [test_one_spine_fec_bridge_w5a.py](../../tests/unit/apps_rg/test_one_spine_fec_bridge_w5a.py): import `build_spine_c0_fec_artifact` (NameError fix for build parametrized tests).
