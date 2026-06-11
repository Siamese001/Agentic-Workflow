---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-eval-harness-terminal-3c9f81.md'
original_relative_path: 'apps-eval-harness-terminal-3c9f81.md'
source_sha256: 64b7f27d4ba09937a961608ec6d90c16f247fb02a8c867c2ece978c725876b1c
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps_* Eval Harness — Terminal Deferred Scope

**Slug:** `apps-eval-harness-terminal-3c9f81`
**Created:** 2026-05-03
**Status:** Completed
**Last Updated:** 2026-05-03
**Completion Note:** All 6 waves executed in one session. 392 tests pass in tests/_apps_contract/ (+41 net). Parity gate green (ERROR=0 WARN=0). 0 stubs remain across all 4 judge slots — full promotion.
**Parent plans (all Completed):**
- `apps-eval-harness-parity-f8d4a2.md`
- `apps-eval-harness-deferred-e4a1b7.md`
- `apps-eval-harness-residual-a2d9c7.md`
- `apps-eval-harness-final-8f3e21.md`

**Owner:** Cursor Agent

## 1. Problem Statement

After four prior plans, three axes remained un-planned in Notion:

1. **Real scoring logic for 3 remaining stub judges** (`response_likelihood`, `brand_voice`, `win_theme_alignment`) — `executive_positioning` already promoted to v2 deterministic heuristic.
2. **Holdout corpus authoring** — `apps_eval/fixtures/holdout/` scaffold exists but is empty.
3. **Legacy YAML deletion audit** — 13 files got `# DEPRECATED` headers in prior plan, but several are actively read by live Python (`apps_eval/config/eval_policies.yaml` by `calibration_drift_detector.py`, `config/routing_thresholds.yaml` by `agentic_core/runtime/config/routing_thresholds.py`, app-specific `*_policies.yaml` by `_taxonomy.py`). Blanket deprecation was premature.

This plan executes pragmatic closure for all three using the same "deterministic heuristic" pattern that promoted `executive_positioning_judge` in the final-8f3e21 plan.

## 2. Goals

- Promote the remaining 3 stub judges to v2 deterministic heuristics.
- Author synthetic holdout seeds clearly marked `SYNTHETIC_SEED_ONLY` (structural placeholder — real holdout corpus still owns a future authoring plan).
- Refine legacy-YAML deprecation: revert `# DEPRECATED` headers on files still actively imported; keep headers only on truly-orphaned files.
- 351+ tests pass; parity gate stays green.

## 3. Non-Goals

- Spearman ≥ 0.80 calibration against human-labeled holdout (needs real corpus + LLM-call budget).
- Actual deletion of legacy YAMLs (separate Author-Gate per file with downstream-consumer audit).
- Real C0 retrieval rewiring (owned by the 4 per-app FEC producer Draft plans).

## 4. Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | W1.P1 | Promote `response_likelihood_judge` stub → v2 deterministic | ~3k | ✅ Done | `IS_STUB=False`; 3 new tests green |
| W2 | W2.P1 | Promote `brand_voice_judge` stub → v2 deterministic | ~3k | ✅ Done | `IS_STUB=False`; 3 new tests green |
| W3 | W3.P1 | Promote `win_theme_alignment_judge` stub → v2 deterministic | ~3k | ✅ Done | `IS_STUB=False`; 3 new tests green |
| W4 | W4.P1 | Author synthetic holdout seeds for 8 apps | ~2k | ✅ Done | 8 holdout seeds, tagged `SYNTHETIC_SEED_ONLY` + `holdout_scaffold` + `do_not_benchmark` |
| W5 | W5.P1 | Refine legacy YAML deprecation (revert on active files) | ~3k | ✅ Done | Reverted 13/13 bogus DEPRECATED headers (all actively imported by live Python) |
| W6 | W6.P1 | Verification — full suite + parity gate | ~2k | ✅ Done | 392 tests pass; gate ERROR=0 WARN=0 |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Est. Tokens | Status |
|---|---|---|---|---|
| W1.P1 | Promote `response_likelihood_judge` | `apps_lic/engines/judges/response_likelihood_judge.py` + test | 3k | ✅ Done |
| W2.P1 | Promote `brand_voice_judge` | `apps_lic/engines/judges/brand_voice_judge.py` + test | 3k | ✅ Done |
| W3.P1 | Promote `win_theme_alignment_judge` | `apps_rfp/engines/judges/win_theme_alignment_judge.py` + test | 3k | ✅ Done |
| W4.P1 | Synthetic holdout seeds | `apps_eval/fixtures/holdout/<app>.jsonl` × 8 | 2k | ✅ Done |
| W5.P1 | Revert bogus DEPRECATED headers | 13 active YAMLs | 3k | ✅ Done |
| W6.P1 | Verification | pytest + parity gate | 2k | ✅ Done |

## 6. Governance

- Constitutional §24 (deferred-scope capture)
- Constitutional §25 (MCP serialization — Notion writes deferred to plan-end)
- Constitutional §31 (SSOT folder routing)

## 7. Author-Gate Decision Points

None — all mechanical execution using the established v2-heuristic pattern.

## 8. Metadata

- Plan file path: `.windsurf/plans/apps-eval-harness-terminal-3c9f81.md`
- Notion Plans row: create on W6 completion with Status=Completed
