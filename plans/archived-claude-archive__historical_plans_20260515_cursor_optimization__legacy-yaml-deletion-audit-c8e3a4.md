---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\legacy-yaml-deletion-audit-c8e3a4.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\legacy-yaml-deletion-audit-c8e3a4.md'
source_sha256: 5c50874425841f386163024b4f4bd2040113242245c9fc75c357354f3b388a9c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Legacy YAML Deletion — Per-File Downstream-Consumer Audit

**Slug:** `legacy-yaml-deletion-audit-c8e3a4`
**Created:** 2026-05-03
**Status:** Completed
**Last Updated:** 2026-05-03
**Author-Gate Closeout:** `dec_19dedcd1c109ebf25` (option_a_lock_in_doctrine, conf 0.91). CI gate `ops_scripts/ci/check_legacy_yaml_no_silent_delete.py` blocks deletion of any of the 13 enumerated YAML files unless an Author-Gate marker referencing `legacy-yaml-deletion-audit-c8e3a4` AND the file path appears in `artifacts/capture/markers.jsonl`. Per-file deletion remains explicit Author-Gate work; silent deletion is now mechanically prevented.
**Completion Note:** All 13 files classified via `ops_scripts/maintenance/legacy_yaml_disposition.py` DISPOSITIONS table. Result: **3 CANONICAL_SSOT** (`config/routing_thresholds.yaml`, `apps_eval/config/eval_policies.yaml`, `apps_rg/config/rg_thresholds.yaml`) + **10 MIGRATION_CANDIDATE** (per-app policies/thresholds with migration target `config/domain_contract/`). Per-file header stamps written. No deletions executed — each MIGRATION_CANDIDATE requires its own Author-Gate to progress to deletion. 430 tests pass; parity gate green.
**Parent arc:** `apps-eval-harness-final-8f3e21` (deprecation headers added) + `apps-eval-harness-terminal-3c9f81` W5 (bogus headers reverted because files ARE active).

**Owner:** Cascade

## 1. Problem Statement

The 13 legacy YAML files (`*_policies.yaml`, `*_thresholds.yaml` across 7 apps + `config/routing_thresholds.yaml`) were blanket-marked `# DEPRECATED` in plan `apps-eval-harness-final-8f3e21` W4, then **reverted in its successor** `apps-eval-harness-terminal-3c9f81` W5 because a grep audit proved EVERY file is actively imported by live Python. Blanket deletion is not safe.

This plan lands a per-file downstream-consumer audit + Author-Gate per file to deprecate-then-delete OR formally promote to canonical SSOT.

## 2. Files In Scope (13)

| # | File | Known consumer |
|---|---|---|
| 1 | `apps_eval/config/eval_policies.yaml` | `ops_scripts/calibration/calibration_drift_detector.py` |
| 2 | `apps_eval/config/eval_thresholds.yaml` | `tools/apps_proof/generate_compact_app_contracts.py` (string match only — verify) |
| 3 | `apps_exec/config/exec_policies.yaml` | apps_exec engines/config (verify) |
| 4 | `apps_exec/config/exec_thresholds.yaml` | apps_exec engines/config (verify) |
| 5 | `apps_lic/config/lic_policies.yaml` | apps_lic engines/config (verify) |
| 6 | `apps_lic/config/lic_thresholds.yaml` | apps_lic engines/config (verify) |
| 7 | `apps_research/config/research_policies.yaml` | apps_research engines/config (verify) |
| 8 | `apps_research/config/research_thresholds.yaml` | apps_research engines/config (verify) |
| 9 | `apps_rfp/config/rfp_policies.yaml` | apps_rfp engines/config (verify) |
| 10 | `apps_rfp/config/rfp_thresholds.yaml` | apps_rfp engines/config (verify) |
| 11 | `apps_rg/config/rg_policies.yaml` | apps_rg engines/config (verify) |
| 12 | `apps_rg/config/rg_thresholds.yaml` | apps_rg engines/config (verify) |
| 13 | `config/routing_thresholds.yaml` | `agentic_core/runtime/config/routing_thresholds.py` — **NOT legacy; canonical** |

## 3. Goals

- Per file, answer: is this **(a) canonical SSOT** (re-label, not delete), **(b) deprecated with migration path** (schedule deletion), or **(c) truly orphaned** (delete immediately)?
- For (b): land migration to `config/domain_contract/` per-app directory before deletion.
- For (c): delete in a wave gated by Author-Gate.
- For (a): re-classify — remove from "legacy" label, document as canonical.

## 4. Wave Summary (13 waves — one per file)

| Wave | File | Expected disposition | Status |
|---|---|---|---|
| W1 | `config/routing_thresholds.yaml` | **(a) canonical** — re-classify | Todo |
| W2 | `apps_eval/config/eval_policies.yaml` | **(a) canonical** (drift detector) or migrate to `apps_eval/config/domain_contract/` | Todo |
| W3 | `apps_eval/config/eval_thresholds.yaml` | Audit | Todo |
| W4–W9 | Per-app `<app>_policies.yaml` × 6 (rg, lic, rfp, research, exec, eval) | Audit each | Todo |
| W10–W13 | Per-app `<app>_thresholds.yaml` × 4 remaining | Audit each | Todo |

Each wave: (1) grep audit downstream consumers; (2) classify a/b/c; (3) emit Author-Gate packet with disposition; (4) execute disposition; (5) test.

## 5. Non-Goals

- Bulk deletion (banned — precedent in `apps-eval-harness-terminal-3c9f81` W5).
- Renaming without migration (breaks downstream imports).

## 6. Governance

- Constitutional §8 (guardian exemptions require Author-Gate)
- Constitutional §24 (deferred-scope capture)
- `author-gate-enforcement.md` — disposition per file requires AG packet

## 7. Risks

| Risk | Mitigation |
|---|---|
| Delete a file, break live Python | Per-file grep audit + integration tests BEFORE deletion |
| Rename a canonical file to "deprecated" | Classify (a) explicitly and add `# CANONICAL SSOT` header |
| 13 waves × AG packet × test cycle is slow | Acceptable — correctness > speed |

## 8. Metadata

- Plan file path: `.windsurf/plans/legacy-yaml-deletion-audit-c8e3a4.md`
- Notion Plans row: Draft on creation
- Activation trigger: ready to execute this session; however queued behind the 4 per-app FEC producer plans for priority.
