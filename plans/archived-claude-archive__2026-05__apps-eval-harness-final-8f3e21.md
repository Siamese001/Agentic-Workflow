---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-eval-harness-final-8f3e21.md'
original_relative_path: '_archive\\2026-05\\apps-eval-harness-final-8f3e21.md'
source_sha256: 74c88393a01de2d9fc9e13471fcb359ff8a92f3970433d08b37c68a9fb9e2ef3
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps_* Eval Harness — Final Deferred Scope

**Slug:** `apps-eval-harness-final-8f3e21`
**Created:** 2026-05-03
**Status:** Completed
**Last Updated:** 2026-05-03
**Completion Note:** All 5 waves executed in one session. 351 tests pass in `tests/_apps_contract/` (+39 net). Parity gate green (ERROR=0 WARN=0).
**Parent plans:**
- `apps-eval-harness-parity-f8d4a2.md` (Completed)
- `apps-eval-harness-deferred-e4a1b7.md` (Completed)
- `apps-eval-harness-residual-a2d9c7.md` (Completed)

**Owner:** Cursor Agent

## 1. Problem Statement

Three prior plans closed 9 of 10 BLOCKERs and all structural scaffolding. Four axes remained deferred because each needs concrete per-app work:

1. **Per-app FEC producers** (BLOCKER #4 tail) — 5 grounded apps need producers registered at module import.
2. **One real LLM-judge promotion** — demonstrate the stub→real transition using a deterministic heuristic (no LLM call budget required for the promotion *pattern*).
3. **Seed fixture corpus** — `apps_eval/fixtures/dev/` has empty scaffold; drop minimal synthetic seeds (labeled SYNTHETIC) so downstream pipelines have something to iterate against.
4. **Legacy YAML deprecation markers** — 13 legacy files identified by W4 audit; add deprecation header comments (not deletion).

## 2. Goals

- Register no-op FEC producers for all 5 grounded apps (concrete per-app wiring).
- Promote `apps_rg.engines.judges.executive_positioning_judge` from stub → real deterministic heuristic.
- Author synthetic seed fixtures under `apps_eval/fixtures/dev/<app>.jsonl` for each of 8 apps.
- Add `# DEPRECATED — migrate to config/domain_contract/` header to each of 13 legacy YAMLs.
- 312+ tests pass; parity gate stays green.

## 3. Non-Goals

- Real C0 retrieval rewiring (still owned by per-app plans).
- Real LLM-judge calibration against human-labeled holdout (owns its own plan).
- Legacy YAML deletion (owns its own Author-Gate).
- Holdout corpus authoring (release-gate path; out of scope here).

## 4. Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | W1.P1 | Register FEC producers for 5 grounded apps | ~4k | ✅ Done | `registered_app_ids()` returns all 5 grounded app ids |
| W2 | W2.P1 | Promote executive_positioning_judge stub → real | ~4k | ✅ Done | v2 deterministic heuristic landed; `promoted_count()` ≥ 1 |
| W3 | W3.P1 | Seed synthetic dev fixtures for 8 apps | ~4k | ✅ Done | 8 .jsonl seeds under `apps_eval/fixtures/dev/` |
| W4 | W4.P1 | Legacy YAML deprecation markers | ~3k | ✅ Done | 13/13 legacy YAMLs carry `# DEPRECATED` header |
| W5 | W5.P1 | Verification — full suite + parity gate | ~2k | ✅ Done | 351 tests pass; parity gate ERROR=0 WARN=0 |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Est. Tokens | Status |
|---|---|---|---|---|
| W1.P1 | Register FEC producers for grounded apps | `apps_shared/cert/grounded_fec_producers.py` (new) + test | 4k | ✅ Done |
| W2.P1 | Promote `executive_positioning_judge` | `apps_rg/engines/judges/executive_positioning_judge.py` + test | 4k | ✅ Done |
| W3.P1 | Seed synthetic dev fixtures | `apps_eval/fixtures/dev/<app>.jsonl` × 8 + test | 4k | ✅ Done |
| W4.P1 | Deprecation headers on legacy YAMLs | 13 YAML files | 3k | ✅ Done |
| W5.P1 | Full verification | pytest + parity gate | 2k | ✅ Done |

## 6. Governance

- Constitutional §24 (deferred-scope capture — this plan IS the pickup)
- Constitutional §25 (MCP serialization — Notion writes deferred to plan-end)
- Constitutional §31 (SSOT folder routing)

## 7. Author-Gate Decision Points

None — all mechanical follow-through.

## 8. Metadata

- Plan file path: `.cursor/plans/apps-eval-harness-final-8f3e21.md`
- Notion Plans row: create on W5 completion
