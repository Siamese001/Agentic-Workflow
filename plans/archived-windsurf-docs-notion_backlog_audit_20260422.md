---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\notion_backlog_audit_20260422.md'
original_relative_path: 'notion_backlog_audit_20260422.md'
source_sha256: d6d02773e903ef315006fc610c2096377ea2cd5fb5a56194ae47e57b14cdf166
recovered_status: LOST_RECOVERED
last_commit: '2dd2ba7efc3'
last_commit_date: '2026-05-15 14:13:16 -0400'
created_date: '2026-04-22'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Notion Backlog Audit — 20260422

Deterministic reconciliation of `.windsurf/plans/*.md` vs Notion Wave/Phase Convergence DB.

## Headline Numbers

- Total disk plans: **79**
- Total Notion rows: **158**
- Plans with >=1 Notion row: **21**
- Plans WITHOUT Notion rows: **58**
- Notion rows pointing to missing plans: **3**
- Rows missing >=1 enriched field: **140**/158

## 1. Plans WITHOUT Notion Coverage

Plan files exist on disk but have ZERO rows in Wave/Phase Convergence.
Each needs review: was Notion tracking requested, or is the plan self-contained?

- `.windsurf/plans/adg-antipattern-hardening-e5a569.md`
- `.windsurf/plans/adg-archive-rca-incomplete-archive.md`
- `.windsurf/plans/adg-chromadb-retrieval-assessment-8a3f2b.md`
- `.windsurf/plans/adg-generation-rca-351a91.md`
- `.windsurf/plans/adg-integrity-gates-e0d532.md`
- `.windsurf/plans/adg-precommit-optimization-review-a1b2c3.md`
- `.windsurf/plans/adg-prompt-assembly-hardening-c4e8a1.md`
- `.windsurf/plans/adg-repair-orchestrator-enhancement-02c1fc.md`
- `.windsurf/plans/agentic-antipattern-tier1-9f2c8a.md`
- `.windsurf/plans/agentic-repo-gap-analysis-351a91.md`
- `.windsurf/plans/apps-lic-e2e-audit-a1b2c3.md`
- `.windsurf/plans/apps-refactoring-wave2-plan-58a2b1.md`
- `.windsurf/plans/artifacts-reorganization-7a3f2d.md`
- `.windsurf/plans/burn-down-syntax-errors-wave-plan-20260406.md`
- `.windsurf/plans/ci-rationalization-a7f3b2.md`
- `.windsurf/plans/codebase-refactoring-deadcode-ssot-a1b2c3.md`
- `.windsurf/plans/consensus-validator-unification-5e9f3a.md`
- `.windsurf/plans/dead-import-refactor-wave-plan-a1b2c3.md`
- `.windsurf/plans/descoped-items-tracker.md`
- `.windsurf/plans/governance-enforcement-table.md`
- `.windsurf/plans/graphdb-enhancement-phase-a-4f2e8b.md`
- `.windsurf/plans/hardcoded-exclusion-burndown-4a8f2c.md`
- `.windsurf/plans/high-wave1-p1-zero-a13f7c.md`
- `.windsurf/plans/l0-context-prompt-retrieval-review-b7c4a2.md`
- `.windsurf/plans/mcp-hardening-antipattern-registry-d05031.md`
- `.windsurf/plans/meta-learning-confidence-audit-b7c4e1.md`
- `.windsurf/plans/method-a-consumer-migration-a3f9c2.md`
- `.windsurf/plans/p0-layer-violation-remediation-7c4e1a.md`
- `.windsurf/plans/p1-wave2-min10-a4c9f1.md`
- `.windsurf/plans/p1p2-burndown-graph-driven-7e4a9c.md`
- `.windsurf/plans/p2-antipattern-remediation-a3f1b7.md`
- `.windsurf/plans/p2-burndown-session-summary-2a8f4c.md`
- `.windsurf/plans/precommit-optimization-regenerated-4b5a2f.md`
- `.windsurf/plans/rebaseline-open-scope-0e2df5.md`
- `.windsurf/plans/refactor_to_interactions_api.md`
- `.windsurf/plans/refactor_to_interactions_api_v3_titanium.md`
- `.windsurf/plans/residual-gap-fix-wave-plan.md`
- `.windsurf/plans/routing-followups-7a2c91.md`
- `.windsurf/plans/scanner-exclusion-sync-two-wave-6d6151.md`
- `.windsurf/plans/semantic-cache-reconciliation-0a0f93.md`
- `.windsurf/plans/semcache-make-live-7a2d4b.md`
- `.windsurf/plans/sequential-thinking-harden-5bf364.md`
- `.windsurf/plans/severity-ssot-migration-a1b2c3.md`
- `.windsurf/plans/sqlite-graphstore-implementation-7a3b2f.md`
- `.windsurf/plans/ssot-consolidation-wave-plan.md`
- `.windsurf/plans/streamline-constants-remaining-waves-6d6151.md`
- `.windsurf/plans/streamline-constants-trace-emitters-d0cb16.md`
- `.windsurf/plans/streamline-constants-waves3-4-migration-d0cb16.md`
- `.windsurf/plans/subatomic_hardening_opportunities.md`
- `.windsurf/plans/test-coverage-improvement-a1b2c3.md`
- `.windsurf/plans/v10-refactoring-implementation-plan-v3.md`
- `.windsurf/plans/wave1-baseline-evidence-d0cb16.md`
- `.windsurf/plans/wave1-p1-remediation-revision-0f0783.md`
- `.windsurf/plans/wave1-verification-report-3d8c2a.md`
- `.windsurf/plans/wave2-l2-native-persistence-0a0f93.md`
- `.windsurf/plans/wave5-closure-report-d0cb16.md`
- `.windsurf/plans/wave_c_plan.md`
- `.windsurf/plans/wave_d_plan.md`

## 2. Notion Rows Pointing to Non-Existent Plans

Plan File values don't match any current `.md`. Plan renamed, deleted, or mistyped.

- `(in-session work — see commit eccaf033a3)` -- 1 row(s) in Notion
- `(infrastructure — no dedicated plan file; deferred from 2026-04-22 MCP standardization)` -- 1 row(s) in Notion
- `_INDEX_open_scope_inventory` -- 1 row(s) in Notion

## 3. Coverage Per Plan With Notion Rows

| Plan | Rows | Todo | Ready | In-Prog | Done | Blocked | Descoped | Enriched |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `adg-ci-gate-hardening-deferred-b4e3c9` | 12 | 12 | 0 | 0 | 0 | 0 | 0 | 12/12 |
| `adg-gap-remediation-wave-plan-ae5b42` | 15 | 14 | 1 | 0 | 0 | 0 | 0 | 0/15 |
| `antipattern-reclassify-e5a569` | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0/4 |
| `config-drift-reconciliation-6e83dd` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0/1 |
| `config-refactoring-remove-core-a3b2c1` | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0/1 |
| `fact-vec-gap-remediation-bf6908` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0/1 |
| `five-tier-governance-model-a3f7c2` | 56 | 0 | 19 | 0 | 37 | 0 | 0 | 0/56 |
| `harness-enforcement-rename-a8f21c` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0/1 |
| `l0-prompt-retrieval-deferred-triage-d3e8f1` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3/3 |
| `p1-antipattern-burndown-8a3f2b` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0/1 |
| `p1-p4-enforcement-hardening-8a3f2b` | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0/1 |
| `p2-antipattern-burndown-ae0549` | 7 | 5 | 0 | 1 | 1 | 0 | 0 | 0/7 |
| `p2-burndown-wave-9e4c17` | 3 | 1 | 1 | 0 | 0 | 1 | 0 | 0/3 |
| `routing-unification-qwen-abe735` | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0/1 |
| `runtime-hitl-exit-control-c4e7b3` | 7 | 0 | 0 | 0 | 7 | 0 | 0 | 0/7 |
| `ssot-consolidation-cleanup-b7f3a1` | 12 | 8 | 0 | 0 | 0 | 0 | 4 | 0/12 |
| `ssot-violations-sweep-29caf4` | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 1/2 |
| `streamline-constants-territories-d0cb16` | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1/1 |
| `terminal-cleanup-burndown-a7f2d1` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1/1 |
| `test-coverage-backlog-f8f5a7` | 21 | 0 | 18 | 0 | 1 | 1 | 1 | 0/21 |
| `test-folder-strategy-adg-redo-95893f` | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0/4 |

## 4. Rows Missing Enriched Schema Fields

Created before 2026-04-22 19:31 schema enrichment, or created without populating the 5 fields.

| Plan | Phase | Wave | Status | Title | Missing Fields |
|---|---|---|---|---|---|
| `(in-session work — see commit eccaf033a3)` | F0.1 | F0 | Done | F0 — MCP fleet hardening (outage RCA + fleet-health probe) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `(infrastructure — no dedicated plan file; deferred from 2026-04-22 MCP standardization)` | M.1 | M | Ready | [P5] Wave M.1 — MCP-7: convert path-launched servers to module form | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `_INDEX_open_scope_inventory` | INV | INDEX | Ready | Open Scope Inventory — Full Corpus Sweep 2026-04-22 | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | GAP-AGG | AGG | Ready | AGGREGATE: adg-gap-remediation-wave-plan-ae5b42 — 18 open-scope items | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W0 | W0 | Todo | Unblock pipeline + MCP (fix build_artifact + sqlite_backend imports) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W1 | W1 | Todo | Layer classification — resolve L_UNKNOWN nodes | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W10 | W10 | Todo | Coverage-to-code-path linkage (branch-level covers edges) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W11 | W11 | Todo | Secret access telemetry (reads_secret edge instrumentation) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W12 | W12 | Todo | HITL decision log (hitl_decision edges in SQLite) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W13 | W13 | Todo | Call graph from profiling (profiler-derived calls edges) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W2 | W2 | Todo | P1 layer inversion fix (GovernanceAgent L5→L_OPS) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W3 | W3 | Todo | P1–P4 table augmentation (SQLite-only new rows) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W4 | W4 | Todo | God module decomposition (sovereign_severity_types.py) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W5 | W5 | Todo | P2 hotspot reduction (lower ratchet ceiling ≥20%) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W6 | W6 | Todo | M1–M3 enforce-mode promotion | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W7 | W7 | Todo | Write-path runtime audit (writes_through/writes_to ratio) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W8 | W8 | Todo | Dynamic call resolution (static scanner extension) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W9 | W9 | Todo | OTel span → ADG edge ingestion pipeline | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `antipattern-reclassify-e5a569` | W1 | W1 | Todo | Severity SQL update (multi_writer.py, ArtifactPaths.py) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `antipattern-reclassify-e5a569` | W2 | W2 | Todo | Wire 4 antipattern edge_kinds in RepairRoute.py | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `antipattern-reclassify-e5a569` | W3 | W3 | Todo | violation_edges filter + table fix + p2 check in generate_full_adg.py | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `antipattern-reclassify-e5a569` | W4 | W4 | Todo | Regression coverage (2 test files) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `config-drift-reconciliation-6e83dd` | GAP-AGG | AGG | Ready | AGGREGATE: config-drift-reconciliation-6e83dd — 7 open-scope items | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `config-refactoring-remove-core-a3b2c1` | GAP-2 | GAP | Done | [VALIDATED RESOLVED 2026-04-22] config-refactoring GAP-2: was 66 files, now 1 | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `fact-vec-gap-remediation-bf6908` | GAP-AGG | AGG | Ready | AGGREGATE: fact-vec-gap-remediation-bf6908 — 7 open-scope items | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 0.1 | W0 | Done | MCP Green Light | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.1 | W1 | Ready | Pre-Run Gate (HARD) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.2 | W1 | Ready | Pre-Write Gate (HARD) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.3 | W1 | Ready | Pre-MCP Gate (HARD) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.4 | W1 | Ready | Pre-Prompt Classifier (ADVISORY) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.5 | W1 | Ready | Post-Write Audit (ADVISORY) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.6 | W1 | Ready | Post-Run Audit (ADVISORY) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.7 | W1 | Ready | Post-MCP Audit (ADVISORY) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.8 | W1 | Ready | Post-Cursor-Agent Cleanup (ADVISORY) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.1 | W2 | Ready | Fix Rules (Policy) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.10 | W2 | Ready | Approval & Exception Policy | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.2 | W2 | Ready | Policy Cleanup | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.3 | W2 | Ready | Constitutional §§13/§14 | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.4 | W2 | Ready | MCP Registry SSOT | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.5 | W2 | Ready | MCP Config Version Check | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.6 | W2 | Ready | Exception Vocabulary | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.7 | W2 | Ready | MCP Config Simplification | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.8 | W2 | Ready | HITL SVP Calibration | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.9 | W2 | Ready | Plan Format Enforcement | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 3.1 | W3 | Done | ADG Scope Clarification | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 3.2 | W3 | Done | ADG Structural Outputs | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 3.3 | W3 | Done | Refactor Accelerator Design | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 3.4 | W3 | Done | Refactor Accelerator MVP | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 3.5 | W3 | Done | Write-time Syntax Gate | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 3.6 | W3 | Done | Guardian Idempotency | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 3.7 | W3 | Done | Guardian Quality Scanner | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 4.1 | W4 | Done | Pre-commit Slim-down | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 4.2 | W4 | Done | Dead Script Archival | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 4.3 | W4 | Done | Wire Missing Gates | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 4.4 | W4 | Done | Eliminate cmd /c | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 4.5 | W4 | Done | CI Promotion Authority | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 4.6 | W4 | Done | End-to-End Verification | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.1 | W5 | Done | Archive ADG Severity Hooks | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.10 | W5 | Done | Archive ADG Root One-Shot Scripts | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.11 | W5 | Done | Archive ADG MCP Duplicates + Stubs | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.12 | W5 | Done | Archive tools/ One-Shot Graveyard | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.13 | W5 | Done | Fix Hardcoded Paths | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.14 | W5 | Done | tools/ Consolidation + Expanded Verification | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.2 | W5 | Done | Archive MCP YAML Infrastructure | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.3 | W5 | Done | Archive Orphan Hook Scripts | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.4 | W5 | Done | Archive One-Shot MCP Scripts | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.5 | W5 | Done | Rewire RepairOrchestrator | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.6 | W5 | Done | Archive Deprecated Windsurf Workflows | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.7 | W5 | Done | Archive Deprecated CI Workflows | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.8 | W5 | Done | Clean Pre-Commit Config | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 5.9 | W5 | Done | Dangling Reference Sweep | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | GAP-15 | GAP | Done | [VALIDATED GATE ADDED 2026-04-22] five-tier-gov GAP-15: check_terminal_cleanup.p | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | GAP-24 | GAP | Done | [VALIDATED RESOLVED 2026-04-22] five-tier-gov GAP-24: phase-summary table now ma | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | GAP-AGG | AGG | Ready | AGGREGATE: five-tier-governance-model-a3f7c2 — 24 open-scope items | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.1 | W2.5 | Done | Extract utils/ | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.2 | W2.5 | Done | Extract archiving/ | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.3 | W2.5 | Done | Extract validation/ | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.4 | W2.5 | Done | Extract reporting/ | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.5 | W2.5 | Done | Extract integration/ | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.6 | W2.5 | Done | Extract core/ + main.py | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.7 | W2.5 | Done | Modularization Verification | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `harness-enforcement-rename-a8f21c` | GAP-AGG | AGG | Ready | AGGREGATE: harness-enforcement-rename-a8f21c — 5 open-scope items | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p1-antipattern-burndown-8a3f2b` | GAP-AGG | AGG | Ready | AGGREGATE: p1-antipattern-burndown-8a3f2b — 6 open-scope items | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p1-p4-enforcement-hardening-8a3f2b` | GAP-1 | GAP | Done | [VALIDATED RESOLVED 2026-04-22] p1-p4-enforcement GAP-1: P2 Blocks Commit wordin | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W0 | W0 | Done | ADG Triage: Per-category counts and file distribution | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W1 | W1 | In Progress | Infrastructure: Ratchet baseline + P2 classify rule | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W2 | W2 | Todo | Burn return_none_swallow (~303 locations) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W3 | W3 | Todo | Burn log_and_swallow (~739 locations) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W4 | W4 | Todo | Burn silent_exception_swallow (~530 locations) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W5 | W5 | Todo | Burn broad_exception_catch (~2,981 locations) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W6 | W6 | Todo | Regenerate ADG, verify gate passes, update ratchet | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-burndown-wave-9e4c17` | 5.1 | W5 | Ready | W5 — Post-W4 resnapshot to refresh ADR-024 Part B promotion counts | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-burndown-wave-9e4c17` | 6.1 | W6 | Blocked | ADR-024 Part B — SURFACE_OVERRIDE manifest + ratchet ceiling update | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-burndown-wave-9e4c17` | 7.1 | W7 | Todo | W7 — P3 long-tail (style) antipattern burndown | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `routing-unification-qwen-abe735` | P1 | W1 | Done | Routing Unification (Qwen) — COMPLETE (Waves 1-6 + F1-F3) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P1 | W4 | Done | Runtime HITL W4: Slack + Orkes + Email Magic-Link Adapters | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P1 | W3 | Done | Runtime HITL W3: Adapter Base + Notion Adapter + E2E | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P1 | W2 | Done | Runtime HITL W2: exit_controller + SQLite Ledger + OTel | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P1 | W1 | Done | Runtime HITL W1: Policy Classifier + YAML SSOT | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P5.1-P5.3 | W5 | Done | Runtime HITL W5: App Integration (apps_lic, apps_exec, apps_uw) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P6.1-P6.3 | W6 | Done | Runtime HITL W6: Shadow-Eval Quality + UWG-Mediated Drafts | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P7.1-P7.2 | W7 | Done | Runtime HITL W7: Audit Chain + ed25519 + SOC2 + CI Integrity Gate | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 1.1 | Wave 1 | Todo | Delete build_sovereign_territories() + all private helpers | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 1.2 | Wave 1 | Todo | Delete lifecycle trace emit block (import-time side effects) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 1.3 | Wave 1 | Todo | Update 2 test files consuming build_sovereign_territories | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 2.1 | Wave 2 | Todo | Remove all *_subfolders keys from LAYER_OVERRIDES | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 2.2 | Wave 2 | Todo | Remove LCD subfolder builder pipeline (_build_lcd_subfolders_template) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 3.1 | Wave 3 | Todo | Clean structure_blueprint_config.py shim (remove deleted symbol refs) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 3.2 | Wave 3 | Todo | Clean init.py re-exports (remove re-exports of removed symbols) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 4.1 | Wave 4 | Todo | Run tests, pre-commit, regenerate ADG — full verification | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | Wave 1 | Wave 1 | Descoped | Dead code removal (delete build_sovereign_territories + helpers) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | Wave 2 | Wave 2 | Descoped | LAYER_OVERRIDES slim (routing-only, remove subfolder trees) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | Wave 3 | Wave 3 | Descoped | Shim + package cleanup (structure_blueprint_config.py, init.py) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | Wave 4 | Wave 4 | Descoped | Verification + ADG regen (green CI) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-violations-sweep-29caf4` | GAP-A | GAP | Blocked | ssot-sweep: 34 grandfathered hardcoded-exclusion sites (long-tail) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D0.1 | D0 | Done | D0 — Fix gap-report Symbol-import detection (prerequisite for D1+) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D1.1 | D1 | Ready | D1.1 — L5 reasoning tail (gap rows 31–60, fan-in 2–3) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D1.1–D1.3 | D1 | Ready | [P1] Wave D1 — L0 + L5 tail (×2.0 multiplier) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D1.2 | D1 | Ready | D1.2 — L5 enforcement gates coverage | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D1.3 | D1 | Ready | D1.3 — L0 routing tail | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D1b.1 | D1b | Ready | [P1] Wave D1b.1 — L1 + L_OPS starvation microwaves | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D2.1-D2.2 | D2 | Ready | D2 — L3 orchestration + L4 state hotspots (×1.75) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D2.1–D2.2 | D2 | Ready | [P2] Wave D2 — L3 + L4 tail (×1.75 multiplier) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D3.1 | D3 | Ready | [P3] Wave D3 — L1 + L2 tail (×1.0 multiplier) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D3.1 | D3 | Ready | D3 — L1 cognition + L2 execution (×1.0) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D4.1 | D4 | Ready | [P3] Wave D4 — L_RUNTIME + L_SHARED + L_PG + L_INFRA hotspots | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D4.1 | D4 | Ready | D4 — Cross-cutting: L_RUNTIME + L_SHARED + L_PG + L_INFRA | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D5.1 | D5 | Ready | [P4] Wave D5 — L6 observability tail (×0.75 multiplier) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D5.1 | D5 | Ready | D5 — L6 observability tail (×0.75) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | DESCOPE | — | Descoped | DESCOPE — L_UNKNOWN (80 modules, 96% gap — likely dead code) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | E1.1-E1.4 | E1 | Ready | E1 — apps_* coverage (78 files: eval/exec/research/rfp) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | E1.1–E1.4 | E1 | Ready | [P2] Wave E1 — apps_* coverage | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | E2.1 | E2 | Ready | [P3] Wave E2 — L_TOOLS + L_OPS + L_SL hotspots | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | E2.1 | E2 | Ready | E2 — L_TOOLS + L_OPS + L_SL hotspots | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | GAP-AGG | AGG | Ready | AGGREGATE: test-coverage-backlog-f8f5a7 — post Wave-C residual gap (3434 unteste | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | S.1 | S | Blocked | [P5] Wave S.1 — GAP-6: review stashed UTC→ET autofixer diffs | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-folder-strategy-adg-redo-95893f` | P1 | Wave 1 | Done | ADG verification + L3/L4 mirror extraction | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-folder-strategy-adg-redo-95893f` | P2 | Wave 2 | Done | Topology decision (centralized vs hybrid) using external literature | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-folder-strategy-adg-redo-95893f` | P3 | Wave 3 | Done | ASCII mirror + repo-specific rules + migration steps | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-folder-strategy-adg-redo-95893f` | P4 | Wave 4 | Done | Final plan formatting + acceptance checks | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |

---
Generated by `tools/reports/audit_notion_backlog_coverage.py` at 2026-04-22T19:42:30.808241+00:00.
Re-run: `python tools/reports/audit_notion_backlog_coverage.py`
