---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\notion_backlog_audit_20260430.md'
original_relative_path: 'notion_backlog_audit_20260430.md'
source_sha256: 4a7592cc30e923b2f96817c5c57c3ce9aafdcab2810b8eb1855de26d4067a5ef
recovered_status: LOST_RECOVERED
last_commit: '2dd2ba7efc3'
last_commit_date: '2026-05-15 14:13:16 -0400'
created_date: '2026-04-30'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Notion Backlog Audit — 20260430

Deterministic reconciliation of `.windsurf/plans/*.md` vs Notion Wave/Phase Convergence DB.

## Headline Numbers

- Total disk plans: **117**
- Total Notion rows: **473**
- Plans with >=1 Notion row: **45**
- Plans WITHOUT Notion rows: **72**
- Notion rows pointing to missing plans: **73**
- Rows missing >=1 enriched field: **178**/473

## 1. Plans WITHOUT Notion Coverage

Plan files exist on disk but have ZERO rows in Wave/Phase Convergence.
Each needs review: was Notion tracking requested, or is the plan self-contained?

- `.windsurf/plans/adg-antipattern-hardening-e5a569.md`
- `.windsurf/plans/adg-chromadb-retrieval-assessment-8a3f2b.md`
- `.windsurf/plans/adg-enforcement-hardening-p1-p8-7e9c4a.md`
- `.windsurf/plans/adg-fail-aggregating-gate-chain-9d4e1f.md`
- `.windsurf/plans/adg-generation-rca-351a91.md`
- `.windsurf/plans/adg-precommit-optimization-review-a1b2c3.md`
- `.windsurf/plans/adg-repair-orchestrator-enhancement-02c1fc.md`
- `.windsurf/plans/adg-three-bucket-authority-model-7e2a91.md`
- `.windsurf/plans/adg-three-graph-harness-e57cc7.md`
- `.windsurf/plans/adg-truth-expansion-r5w1-a8f3c2.md`
- `.windsurf/plans/agentic-antipattern-tier1-9f2c8a.md`
- `.windsurf/plans/agentic-repo-gap-analysis-351a91.md`
- `.windsurf/plans/apps-eval-first-principles-refactor-7b9f1d.md`
- `.windsurf/plans/apps-exec-first-principles-refactor-5e6a4b.md`
- `.windsurf/plans/apps-lic-first-principles-refactor-8a3c2e.md`
- `.windsurf/plans/apps-research-first-principles-refactor-2f5e7a.md`
- `.windsurf/plans/apps-rfp-first-principles-refactor-9c8d3f.md`
- `.windsurf/plans/apps-rg-first-principles-refactor-7e9c4a.md`
- `.windsurf/plans/apps-runtime-first-principles-e6ba58.md`
- `.windsurf/plans/apps-underwriting-ai-first-principles-refactor-4b1c8e.md`
- `.windsurf/plans/artifacts-reorganization-7a3f2d.md`
- `.windsurf/plans/assurance-p1-gates-ab4758.md`
- `.windsurf/plans/author-gate-ledger-hardening-1f4c8a.md`
- `.windsurf/plans/c0-context-engine-wiring-fix-9e42a1.md`
- `.windsurf/plans/codebase-refactoring-deadcode-ssot-a1b2c3.md`
- `.windsurf/plans/consensus-validator-unification-5e9f3a.md`
- `.windsurf/plans/dead-import-refactor-wave-plan-a1b2c3.md`
- `.windsurf/plans/docs-reference-tier-split-a3c9f1.md`
- `.windsurf/plans/exit-eval-spine-gap-ce683b.md`
- `.windsurf/plans/exit-eval-v5-gap-c0aa47.md`
- `.windsurf/plans/hardcoded-exclusion-burndown-4a8f2c.md`
- `.windsurf/plans/hotspot-coverage-pipeline-c4e8d2.md`
- `.windsurf/plans/l0-authority-burndown-3a7b21.md`
- `.windsurf/plans/l1-reasoning-bestpractices-gaps-a7b2c9.md`
- `.windsurf/plans/mcp-hardening-antipattern-registry-d05031.md`
- `.windsurf/plans/mcp-serial-defense-l2l5-7d4f1a.md`
- `.windsurf/plans/mcp-skill-installation-2ee0d2.md`
- `.windsurf/plans/meta-learning-confidence-audit-b7c4e1.md`
- `.windsurf/plans/next-step-gate-ci-workflow-8733a6.md`
- `.windsurf/plans/notion-backlog-human-scoring-e7a941.md`
- `.windsurf/plans/notion-backlog-residual-cleanup-c3d8f2.md`
- `.windsurf/plans/notion-backlog-schema-refactor-7c3d9e.md`
- `.windsurf/plans/p0-layer-violation-remediation-7c4e1a.md`
- `.windsurf/plans/p1p2-burndown-graph-driven-7e4a9c.md`
- `.windsurf/plans/p2-antipattern-remediation-a3f1b7.md`
- `.windsurf/plans/p2-burndown-session-summary-2a8f4c.md`
- `.windsurf/plans/precommit-optimization-regenerated-4b5a2f.md`
- `.windsurf/plans/prompt-assembly-detailed-spec-gaps-7c9f3a.md`
- `.windsurf/plans/qwen-confidence-routing-hardening-d4e7b1.md`
- `.windsurf/plans/rag-semantic-chunker-gap-c4f1a8.md`
- `.windsurf/plans/refactor_to_interactions_api.md`
- `.windsurf/plans/refactor_to_interactions_api_v3_titanium.md`
- `.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`
- `.windsurf/plans/runtime-evidence-foundation-54ad39.md`
- `.windsurf/plans/runtime-gate-coverage-hardening-7e3f1a.md`
- `.windsurf/plans/runtime-otel-spec-coverage-7c4d2a.md`
- `.windsurf/plans/scanner-exclusion-sync-two-wave-6d6151.md`
- `.windsurf/plans/semantic-cache-reconciliation-0a0f93.md`
- `.windsurf/plans/shadow-eval-v6-gap-d4a9c2.md`
- `.windsurf/plans/sqlite-graphstore-implementation-7a3b2f.md`
- `.windsurf/plans/ssot-consolidation-wave-plan.md`
- `.windsurf/plans/streamline-constants-trace-emitters-d0cb16.md`
- `.windsurf/plans/streamline-constants-waves3-4-migration-d0cb16.md`
- `.windsurf/plans/subatomic_hardening_opportunities.md`
- `.windsurf/plans/test-coverage-improvement-a1b2c3.md`
- `.windsurf/plans/test-coverage-waves-f8f5a7.md`
- `.windsurf/plans/three-bucket-gap-remediation-069806.md`
- `.windsurf/plans/v10-refactoring-implementation-plan-v3.md`
- `.windsurf/plans/w4-p8-guardrail-family-e93f8a.md`
- `.windsurf/plans/wave1-baseline-evidence-d0cb16.md`
- `.windsurf/plans/wave1-p1-remediation-revision-0f0783.md`
- `.windsurf/plans/wave2-l2-native-persistence-0a0f93.md`

## 2. Notion Rows Pointing to Non-Existent Plans

Plan File values don't match any current `.md`. Plan renamed, deleted, or mistyped.

- `(in-session work — see commit eccaf033a3)` -- 1 row(s) in Notion
- `(no dedicated plan - trivial fix - see Blocking Items for 3-option remediation)` -- 1 row(s) in Notion
- `(no plan file — completed in-session per memory-notion-writeback rule)` -- 1 row(s) in Notion
- `.windsurf/plans/closed-loop-router-fleet-rollout-d8f2a3` -- 2 row(s) in Notion
- `.windsurf/plans/l2-cascade-router-closed-loop-wiring-c4d8a1` -- 1 row(s) in Notion
- `.windsurf/plans/mcp-serial-defense-l2l5-7d4f1a` -- 1 row(s) in Notion
- `.windsurf/plans/notion-backlog-human-scoring-e7a941` -- 5 row(s) in Notion
- `.windsurf/plans/notion-backlog-residual-cleanup-c3d8f2` -- 5 row(s) in Notion
- `NEW:adg-mcp-reopen-hardening (to be created)` -- 4 row(s) in Notion
- `_INDEX_open_scope_inventory` -- 1 row(s) in Notion
- `adg-coverage-hardening-phase0-e6b295` -- 2 row(s) in Notion
- `adg-dead-code-waves-efg-b2e4f7` -- 6 row(s) in Notion
- `adg-gate-unblock-prose-plans-c7e1a9` -- 1 row(s) in Notion
- `adg-l0-raw-execution-cleanup` -- 1 row(s) in Notion
- `adg-l5-bypass-cleanup` -- 1 row(s) in Notion
- `adg-l5-healer-design-decision (NEW — to be scaffolded)` -- 1 row(s) in Notion
- `adg-mcp-reopen-hardening` -- 1 row(s) in Notion
- `adg-seam-test-coherence-cleanup` -- 1 row(s) in Notion
- `adg-stub-test-dedup-7c3f91` -- 2 row(s) in Notion
- `adg-trace-replay-eval-ratchet` -- 1 row(s) in Notion
- `adg-wiring-ci-hardening-7a5d84` -- 2 row(s) in Notion
- `agent-deprecation-migration-d7a3f2` -- 9 row(s) in Notion
- `anthropic-alignment-followups (NEW)` -- 5 row(s) in Notion
- `author-gate-meta-learning-hardening-a8f2b1 (parent plan)` -- 1 row(s) in Notion
- `author-gate-meta-learning-outcome-wiring-c3e1f7` -- 1 row(s) in Notion
- `cache-r1ab-residuals-8c4e2a` -- 3 row(s) in Notion
- `d7-anchor-tuning` -- 1 row(s) in Notion
- `d7-remaining-folder-cleanup` -- 1 row(s) in Notion
- `decision-ledger-hardening-w1w5-b3a81c` -- 1 row(s) in Notion
- `fact-vec-gap-remediation-bf6908` -- 1 row(s) in Notion
- `five-tier-governance-model-a3f7c2` -- 56 row(s) in Notion
- `hybrid-search-adg-seed-impl` -- 1 row(s) in Notion
- `l0-prompt-retrieval-deferred-triage-d3e8f1` -- 3 row(s) in Notion
- `l1-reasoning-bestpractices-svp-review-a7b2c9` -- 1 row(s) in Notion
- `l2-execute-best-practices-gap-b7c4e2` -- 5 row(s) in Notion
- `l2-execute-v2-agent-conformance-c8e4f1` -- 7 row(s) in Notion
- `l5-g15-rule-disposition-annotation` -- 1 row(s) in Notion
- `l5-governance-best-practice-gap-4615ae` -- 21 row(s) in Notion
- `l5-production-wiring-uwg-orchestrator` -- 1 row(s) in Notion
- `llm-judge-hardening-b5e319` -- 5 row(s) in Notion
- `mcp-destructive-gate-preflight-e9a14b` -- 3 row(s) in Notion
- `multi: runtime-adg-tier2-emit-sites-b3e9a7 + runtime-adg-tier2h-tier3-c4d8e2 + runtime-adg-tier3-broader-adoption-8f2d1c + system-learning-activation-path-a5e2f1` -- 1 row(s) in Notion
- `otel-runtime-adg-ingest-7a3f12` -- 2 row(s) in Notion
- `p1-antipattern-burndown-8a3f2b` -- 1 row(s) in Notion
- `p2-antipattern-burndown-ae0549` -- 7 row(s) in Notion
- `post-cursor-agent-watchdog-hardening` -- 2 row(s) in Notion
- `post-wave10-roadmap-a1e7f2` -- 5 row(s) in Notion
- `prompt-reception-followups-a7b3c4` -- 15 row(s) in Notion
- `pytest-server-functional-tests` -- 1 row(s) in Notion
- `query-progress-bar-backlog` -- 1 row(s) in Notion
- `qwen-adoption-waves-a7f3c2` -- 4 row(s) in Notion
- `r1b-semantic-cache-best-practices-gap-a7c3e1` -- 3 row(s) in Notion
- `repo-adg-graph-collection-retire-d9f483` -- 2 row(s) in Notion
- `request-intake-w7-deferred-4c8e1f` -- 9 row(s) in Notion
- `routing-unification-qwen-abe735` -- 4 row(s) in Notion
- `runtime-adg-acceleration-b4f2a1` -- 2 row(s) in Notion
- `runtime-adg-coverage-audit-4f7a21 (audit) | NEW:runtime-adg-trace-binding-remediation (remediation — not yet drafted)` -- 1 row(s) in Notion
- `runtime-adg-tier1-trace-binding-c9b84d (this remediation) | runtime-adg-coverage-audit-4f7a21 (prior audit)` -- 1 row(s) in Notion
- `runtime-adg-tier2-emit-sites-b3e9a7` -- 1 row(s) in Notion
- `runtime-hitl-exit-control-c4e7b3` -- 7 row(s) in Notion
- `sc1-structural-block-closure-f9e3b1` -- 4 row(s) in Notion
- `ssot-and-guardian-backlog-f1a5c4` -- 2 row(s) in Notion
- `system-learning-activation-path-a5e2f1` -- 1 row(s) in Notion
- `terminal-cleanup-burndown-a7f2d1` -- 1 row(s) in Notion
- `test-coverage-backlog-f8f5a7` -- 13 row(s) in Notion
- `test-coverage-hotspots-8f2a1c` -- 5 row(s) in Notion
- `test-folder-strategy-adg-redo-95893f` -- 4 row(s) in Notion
- `w6-1-tooling-guardian-codemod-d4e8a7` -- 3 row(s) in Notion
- `w6-w7-continuation-a7b3d2` -- 2 row(s) in Notion
- `w7-p1-adr-tooling-followup-b5c9e2` -- 3 row(s) in Notion
- `wave-e-adg-card-projection-2df148` -- 2 row(s) in Notion
- `windsurf-hook-dedup-fix-c9d3a2` -- 1 row(s) in Notion
- `windsurf-hook-outage-2026-04-23` -- 1 row(s) in Notion

## 3. Coverage Per Plan With Notion Rows

| Plan | Rows | Todo | Ready | In-Prog | Done | Blocked | Descoped | Enriched |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `adg-architectural-p0-violations-cleanup-bced9c` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0/1 |
| `adg-cascading-ratchet-defer-exit-a41828` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0/1 |
| `adg-ci-gate-hardening-deferred-b4e3c9` | 12 | 12 | 0 | 0 | 0 | 0 | 0 | 12/12 |
| `adg-gap-remediation-wave-plan-ae5b42` | 15 | 13 | 0 | 0 | 1 | 0 | 1 | 0/15 |
| `adg-tree-sitter-parser-exploration-b1c517` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0/1 |
| `adg-wiring-ci-dispatcher-hardening-b2f4a1` | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5/5 |
| `adg-write-sovereignty-cleanup-8bf0da` | 6 | 1 | 0 | 0 | 5 | 0 | 0 | 6/6 |
| `anthropic-rag-gaps-7f3c2a` | 6 | 2 | 0 | 0 | 3 | 0 | 0 | 6/6 |
| `antipattern-reclassify-e5a569` | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0/4 |
| `audit-uncovered-gates-and-remediation-627368` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0/1 |
| `author-gate-meta-learning-hardening-a8f2b1` | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 1/1 |
| `c0-context-assembly-best-practices-b7c3a1` | 6 | 2 | 0 | 3 | 1 | 0 | 0 | 6/6 |
| `chromadb-bge-retrieval-hardening-e9aa09` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1/1 |
| `config-drift-reconciliation-6e83dd` | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0/1 |
| `config-refactoring-remove-core-a3b2c1` | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0/1 |
| `cot-reflexion-self-consistency-config-7a3f1c` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1/1 |
| `gap-closure-test-impl-b77a11` | 12 | 11 | 0 | 0 | 1 | 0 | 0 | 0/12 |
| `harness-enforcement-rename-a8f21c` | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0/1 |
| `hybrid-search-adg-seed-rerank-c58e21` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1/1 |
| `judge-surface-harmonization-b9d3a7` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1/1 |
| `l0-routing-calibration-gap-audit-b3c9d4` | 15 | 5 | 0 | 0 | 3 | 7 | 0 | 15/15 |
| `l5-v4-g04-identity-propagation-0b9d22` | 7 | 0 | 0 | 0 | 7 | 0 | 0 | 7/7 |
| `llm-as-judge-hardening-anthropic-e7b1a4` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1/1 |
| `llm-judge-hardening-followups-f2c8e1` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1/1 |
| `moe-agentic-architecture-d4e9a2` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1/1 |
| `notion-schema-refactor-cleanup-9f2e4a` | 8 | 1 | 0 | 0 | 7 | 0 | 0 | 8/8 |
| `p1-p4-enforcement-hardening-8a3f2b` | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0/1 |
| `p2-burndown-wave-9e4c17` | 3 | 2 | 0 | 0 | 0 | 1 | 0 | 0/3 |
| `phase-b-blocker-burndown-a8c4f1` | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0/4 |
| `prompt-assembly-best-practices-gap-b4e1c2` | 15 | 3 | 0 | 0 | 12 | 0 | 0 | 15/15 |
| `prompt-assembly-few-shot-exemplars-9c4e2b` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1/1 |
| `prompt-assembly-reception-hardening-9c4e2b` | 8 | 0 | 0 | 0 | 8 | 0 | 0 | 8/8 |
| `prompt-categories-coverage-audit-b8f5d3` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1/1 |
| `repo-tech-debt-wave1-b3c8d1` | 7 | 1 | 0 | 0 | 6 | 0 | 0 | 7/7 |
| `runtime-adg-tier1-5-span-naming-a31bcf` | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 1/1 |
| `runtime-adg-tier2h-tier3-c4d8e2` | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 1/1 |
| `runtime-adg-tier3-broader-adoption-8f2d1c` | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 2/2 |
| `sc1-audit-to-enforce-promotion-b4e9d7` | 2 | 1 | 0 | 0 | 0 | 0 | 1 | 2/2 |
| `scorer-otel-autosource-layer-b-c5e4d1` | 5 | 4 | 0 | 0 | 0 | 1 | 0 | 5/5 |
| `shadow-learning-bestpractice-gap-7b3e4c` | 7 | 0 | 0 | 0 | 7 | 0 | 0 | 7/7 |
| `ssot-consolidation-cleanup-b7f3a1` | 12 | 8 | 0 | 0 | 0 | 0 | 4 | 0/12 |
| `ssot-violations-sweep-29caf4` | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 1/2 |
| `streamline-constants-territories-d0cb16` | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1/1 |
| `three-bucket-otel-view-5db409` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0/3 |
| `windsurf-maintenance-2026-q2-0f3564` | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 0/7 |

## 4. Rows Missing Enriched Schema Fields

Created before 2026-04-22 19:31 schema enrichment, or created without populating the 5 fields.

| Plan | Phase | Wave | Status | Title | Missing Fields |
|---|---|---|---|---|---|
| `(in-session work — see commit eccaf033a3)` | F0.1 | F0 | Done | F0 — MCP fleet hardening (outage RCA + fleet-health probe) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `_INDEX_open_scope_inventory` | INV | INDEX |  | Open Scope Inventory — Full Corpus Sweep 2026-04-22 | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-architectural-p0-violations-cleanup-bced9c` | NEXT-a3d31c11 | W-NEXT | Todo | [P3] Remediate the 3 SC-1 + 2 P0 architectural violations surfaced during W8 val | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-cascading-ratchet-defer-exit-a41828` | NEXT-fc4463f6 | W-NEXT | Todo | [P4] Extend defer-exit pattern to SC-1 / agentic-antipattern / dead-prod-imports | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | GAP-AGG | AGG | Descoped | AGGREGATE: adg-gap-remediation-wave-plan-ae5b42 — 18 open-scope items | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W0 | W0 | Todo | [P3] Unblock pipeline + MCP (fix build_artifact + sqlite_backend imports) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W1 | W1 | Todo | [P3] Layer classification — resolve L_UNKNOWN nodes | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W10 | W10 | Done | Coverage-to-code-path linkage (branch-level covers edges) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W11 | W11 | Todo | [P3] Secret access telemetry (reads_secret edge instrumentation) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W12 | W12 | Todo | [P1] HITL decision log (hitl_decision edges in SQLite) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W13 | W13 | Todo | [P3] Call graph from profiling (profiler-derived calls edges) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W2 | W2 | Todo | [P2] P1 layer inversion fix (GovernanceAgent L5→L_OPS) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W3 | W3 | Todo | [P3] P1–P4 table augmentation (SQLite-only new rows) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W4 | W4 | Todo | [P3] God module decomposition (sovereign_severity_types.py) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W5 | W5 | Todo | [P3] P2 hotspot reduction (lower ratchet ceiling ≥20%) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W6 | W6 | Todo | [P3] M1–M3 enforce-mode promotion | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W7 | W7 | Todo | [P2] Write-path runtime audit (writes_through/writes_to ratio) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W8 | W8 | Todo | [P3] Dynamic call resolution (static scanner extension) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-gap-remediation-wave-plan-ae5b42` | W9 | W9 | Todo | [P3] OTel span → ADG edge ingestion pipeline | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-l0-raw-execution-cleanup` | W1.1 | W1 | Done | [P1] v_p0_l0_raw_execution P0 3 L0 raw execution sites bypass orchestrator | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-l5-bypass-cleanup` | W1.1 | W1 | Todo | [P1] C2_l5_bypass_pview P0 L5 safety plane bypass | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-seam-test-coherence-cleanup` | W1.1 | W1 | Todo | [P2] G2_seam_test_export_coherence P1 6 test export coherence violations | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-trace-replay-eval-ratchet` | W1.1 | W1 | Todo | [P2] 8_trace_replay_eval P1 ratchet regression 593 trace-replay coverage gaps | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `adg-tree-sitter-parser-exploration-b1c517` | NEXT-6ae6bd6f | W-NEXT | Todo | [P4] Explore tree-sitter as ADG parser pass | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `antipattern-reclassify-e5a569` | W1 | W1 | Done | Severity SQL update (multi_writer.py, ArtifactPaths.py) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `antipattern-reclassify-e5a569` | W2 | W2 | Done | Wire 4 antipattern edge_kinds in RepairRoute.py | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `antipattern-reclassify-e5a569` | W3 | W3 | Done | violation_edges filter + table fix + p2 check in generate_full_adg.py | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `antipattern-reclassify-e5a569` | W4 | W4 | Done | Regression coverage (2 test files) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `audit-uncovered-gates-and-remediation-627368` | W3.J1 | W3 | Todo | [P2] J1_canonical_pipeline_wiring P0 6 manifest violations on canonical pipeline | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `config-drift-reconciliation-6e83dd` | GAP-AGG | AGG | Descoped | AGGREGATE: config-drift-reconciliation-6e83dd — 7 open-scope items | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `config-refactoring-remove-core-a3b2c1` | GAP-2 | GAP | Done | [VALIDATED RESOLVED 2026-04-22] config-refactoring GAP-2: was 66 files, now 1 | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `fact-vec-gap-remediation-bf6908` | GAP-AGG | AGG | Descoped | AGGREGATE: fact-vec-gap-remediation-bf6908 — 7 open-scope items | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 0.1 | W0 | Done | MCP Green Light | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.1 | W1 | Todo | [P3] Pre-Run Gate (HARD) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.2 | W1 | Todo | [P2] Pre-Write Gate (HARD) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.3 | W1 | Todo | [P3] Pre-MCP Gate (HARD) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.4 | W1 | Todo | [P3] Pre-Prompt Classifier (ADVISORY) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.5 | W1 | Todo | [P2] Post-Write Audit (ADVISORY) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.6 | W1 | Todo | [P3] Post-Run Audit (ADVISORY) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.7 | W1 | Todo | [P3] Post-MCP Audit (ADVISORY) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 1.8 | W1 | Todo | [P3] Post-Cursor-Agent Cleanup (ADVISORY) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.1 | W2 | Todo | [P2] Fix Rules (Policy) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.10 | W2 | Done | Approval & Exception Policy | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.2 | W2 | Todo | [P2] Policy Cleanup | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.3 | W2 | Done | Constitutional §§13/§14 | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.4 | W2 | Todo | [P3] MCP Registry SSOT | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.5 | W2 | Todo | [P3] MCP Config Version Check | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.6 | W2 | Done | Exception Vocabulary | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.7 | W2 | Todo | [P3] MCP Config Simplification | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.8 | W2 | Todo | [P1] HITL SVP Calibration | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | 2.9 | W2 | Done | Plan Format Enforcement | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
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
| `five-tier-governance-model-a3f7c2` | GAP-AGG | AGG | Descoped | AGGREGATE: five-tier-governance-model-a3f7c2 — 24 open-scope items | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.1 | W2.5 | Done | Extract utils/ | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.2 | W2.5 | Done | Extract archiving/ | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.3 | W2.5 | Done | Extract validation/ | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.4 | W2.5 | Done | Extract reporting/ | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.5 | W2.5 | Done | Extract integration/ | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.6 | W2.5 | Done | Extract core/ + main.py | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `five-tier-governance-model-a3f7c2` | M.7 | W2.5 | Done | Modularization Verification | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `gap-closure-test-impl-b77a11` | W1.1 | W1 | Todo | [P1] L5 runtime certification binding tests (00A.8) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `gap-closure-test-impl-b77a11` | W1.3 | W1 | Todo | [P1] L4 blueprint policy version migration tests (00B.9) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `gap-closure-test-impl-b77a11` | W2.1 | W2 | Todo | [P1] Runtime gate G01-G29 invocation map tests (00C.9) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `gap-closure-test-impl-b77a11` | W2.2 | W2 | Todo | [P2] PA authority red-team slot verification tests (PA.8) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `gap-closure-test-impl-b77a11` | W3.1 | W3 | Done | L2 sequencer orchestrator contract tests (04.0) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `gap-closure-test-impl-b77a11` | W3.2 | W3 | Todo | [P2] L2 StateDiffCandidate mutation intent tests (04.9) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `gap-closure-test-impl-b77a11` | W3.3 | W3 | Todo | [P2] L2 verify-then-execute local critique tests (04.10) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `gap-closure-test-impl-b77a11` | W3.4 | W3 | Todo | [P1] L3-L2 step handoff checkpoint resume tests (03.9) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `gap-closure-test-impl-b77a11` | W4.1 | W4 | Todo | [P2] PTC v2 sandbox hardening tests (04.7) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `gap-closure-test-impl-b77a11` | W5.1 | W5 | Todo | [P2] L6 memory promotion interface tests (06.9) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `gap-closure-test-impl-b77a11` | W6.1 | W6 | Todo | [P2] E2E mutation testing boundary faults tests (99.9) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `gap-closure-test-impl-b77a11` | W6.2 | W6 | Todo | [P2] E2E fixtures replay harness commands tests (99.10) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `harness-enforcement-rename-a8f21c` | GAP-AGG | AGG | Descoped | AGGREGATE: harness-enforcement-rename-a8f21c — 5 open-scope items | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p1-antipattern-burndown-8a3f2b` | GAP-AGG | AGG | Descoped | AGGREGATE: p1-antipattern-burndown-8a3f2b — 6 open-scope items | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p1-p4-enforcement-hardening-8a3f2b` | GAP-1 | GAP | Done | [VALIDATED RESOLVED 2026-04-22] p1-p4-enforcement GAP-1: P2 Blocks Commit wordin | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W0 | W0 | Done | ADG Triage: Per-category counts and file distribution | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W1 | W1 | Done | Infrastructure: Ratchet baseline + P2 classify rule | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W2 | W2 | Done | Burn return_none_swallow (~303 locations) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W3 | W3 | Done | Burn log_and_swallow (~739 locations) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W4 | W4 | Done | Burn silent_exception_swallow (~530 locations) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W5 | W5 | Done | Burn broad_exception_catch (~2,981 locations) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-antipattern-burndown-ae0549` | W6 | W6 | Done | Regenerate ADG, verify gate passes, update ratchet | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-burndown-wave-9e4c17` | 5.1 | W5 | Todo | [P3] W5 — Post-W4 resnapshot to refresh ADR-024 Part B promotion counts | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-burndown-wave-9e4c17` | 6.1 | W6 | Blocked | ADR-024 Part B — SURFACE_OVERRIDE manifest + ratchet ceiling update | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `p2-burndown-wave-9e4c17` | 7.1 | W7 | Todo | [P3] W7 — P3 long-tail (style) antipattern burndown | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `phase-b-blocker-burndown-a8c4f1` | W2.1 | W2 | Todo | [P1] 2_authority_boundary P0 17 cross-layer authority breaches | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `phase-b-blocker-burndown-a8c4f1` | W4.1 | W4 | Todo | [P1] 4_capability_egress P0 outbound calls bypass capability adapter | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `phase-b-blocker-burndown-a8c4f1` | W5.2 | W5 | Todo | [P1] C1_uwg_bypass_pview P0 single row UWG bypass pview | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `phase-b-blocker-burndown-a8c4f1` | W5.3 | W5 | Todo | [P1] v_p0_write_bypass_uwg P0 state write does not flow through L4 UWG | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P1 | W4 | Done | Runtime HITL W4: Slack + Orkes + Email Magic-Link Adapters | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P1 | W3 | Done | Runtime HITL W3: Adapter Base + Notion Adapter + E2E | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P1 | W2 | Done | Runtime HITL W2: exit_controller + SQLite Ledger + OTel | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P1 | W1 | Done | Runtime HITL W1: Policy Classifier + YAML SSOT | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P5.1-P5.3 | W5 | Done | Runtime HITL W5: App Integration (apps_lic, apps_exec, apps_uw) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P6.1-P6.3 | W6 | Done | Runtime HITL W6: Shadow-Eval Quality + UWG-Mediated Drafts | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `runtime-hitl-exit-control-c4e7b3` | P7.1-P7.2 | W7 | Done | Runtime HITL W7: Audit Chain + ed25519 + SOC2 + CI Integrity Gate | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `sc1-structural-block-closure-f9e3b1` | W7.1-ADR | W7 | Done | [P1] W7 W7.1-ADR — ADR-051 SC-1 structural block remediation + companion plan au | dependencies |
| `sc1-structural-block-closure-f9e3b1` | W7.1-P0 | W7 | Done | [P1] W7 W7.1-P0 — SC-1 subtype classifier + report (3 violations, massive de-sco | dependencies |
| `sc1-structural-block-closure-f9e3b1` | W7.1-P1 | W7 | Done | [P2] W7.1-P1 — 3 UWG-bypass sites fixed (ensure_dir pattern across L3 exit_contr | dependencies |
| `sc1-structural-block-closure-f9e3b1` | W7.1-P4 | W7 | Done | [P1] W7.1-P4 — SC-1 closure validated: ALL 7 P-views return 0 rows (full SC-1 ga | dependencies |
| `ssot-and-guardian-backlog-f1a5c4` | W6.2a | W6 | Done | [P2] W6 W6.2a — prefix SSOT codemod applied to artifacts/adg literal (17 files,  | dependencies |
| `ssot-and-guardian-backlog-f1a5c4` | W6.3-P0 | W6 | Done | [P3] W6 W6.3-P0 — C_SUBSTRING SSOT triage classifier + 82-site report | dependencies |
| `ssot-consolidation-cleanup-b7f3a1` | 1.1 | Wave 1 | Todo | [P3] Delete build_sovereign_territories() + all private helpers | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 1.2 | Wave 1 | Todo | [P3] Delete lifecycle trace emit block (import-time side effects) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 1.3 | Wave 1 | Todo | [P3] Update 2 test files consuming build_sovereign_territories | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 2.1 | Wave 2 | Todo | [P3] Remove all *_subfolders keys from LAYER_OVERRIDES | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 2.2 | Wave 2 | Todo | [P3] Remove LCD subfolder builder pipeline (_build_lcd_subfolders_template) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 3.1 | Wave 3 | Todo | [P3] Clean structure_blueprint_config.py shim (remove deleted symbol refs) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 3.2 | Wave 3 | Todo | [P3] Clean init.py re-exports (remove re-exports of removed symbols) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | 4.1 | Wave 4 | Todo | [P3] Run tests, pre-commit, regenerate ADG — full verification | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | Wave 1 | Wave 1 | Descoped | Dead code removal (delete build_sovereign_territories + helpers) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | Wave 2 | Wave 2 | Descoped | LAYER_OVERRIDES slim (routing-only, remove subfolder trees) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | Wave 3 | Wave 3 | Descoped | Shim + package cleanup (structure_blueprint_config.py, init.py) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-consolidation-cleanup-b7f3a1` | Wave 4 | Wave 4 | Descoped | Verification + ADG regen (green CI) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `ssot-violations-sweep-29caf4` | GAP-A | GAP | Done | ssot-sweep: 34 grandfathered hardcoded-exclusion sites (long-tail) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D0.1 | D0 | Done | D0 — Fix gap-report Symbol-import detection (prerequisite for D1+) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D1.1–D1.3 | D1 |  | [P1] Wave D1 — L0 + L5 tail (×2.0 multiplier) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D1b.1 | D1b |  | [P1] Wave D1b.1 — L1 + L_OPS starvation microwaves | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D2.1–D2.2 | D2 |  | [P2] Wave D2 — L3 + L4 tail (×1.75 multiplier) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D3.1 | D3 |  | [P3] Wave D3 — L1 + L2 tail (×1.0 multiplier) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D4.1 | D4 |  | [P3] Wave D4 — L_RUNTIME + L_SHARED + L_PG + L_INFRA hotspots | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | D5.1 | D5 |  | [P4] Wave D5 — L6 observability tail (×0.75 multiplier) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | DESCOPE | — | Descoped | DESCOPE — L_UNKNOWN (80 modules, 96% gap — likely dead code) | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | E1.1–E1.4 | E1 | Todo | [P2] Wave E1 — apps_* coverage | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | E2.1 | E2 |  | [P3] Wave E2 — L_TOOLS + L_OPS + L_SL hotspots | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | GAP-AGG | AGG | Descoped | AGGREGATE: test-coverage-backlog-f8f5a7 — post Wave-C residual gap (3434 unteste | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | M.1 | M |  | [P5] Wave M.1 — MCP-7: convert path-launched servers to module form | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-coverage-backlog-f8f5a7` | S.1 | S | Blocked | [P5] Wave S.1 — GAP-6: review stashed UTC→ET autofixer diffs | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-folder-strategy-adg-redo-95893f` | P1 | Wave 1 | Done | ADG verification + L3/L4 mirror extraction | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-folder-strategy-adg-redo-95893f` | P2 | Wave 2 | Done | Topology decision (centralized vs hybrid) using external literature | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-folder-strategy-adg-redo-95893f` | P3 | Wave 3 | Done | ASCII mirror + repo-specific rules + migration steps | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `test-folder-strategy-adg-redo-95893f` | P4 | Wave 4 | Done | Final plan formatting + acceptance checks | sub_wave, dependencies, success_criteria, files_in_scope, parent_plan_summary |
| `three-bucket-otel-view-5db409` | W10.1 | W10 | Todo | Schema graduation to column-level NOT NULL after 4-week green window | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `three-bucket-otel-view-5db409` | W11.1 | W11 | Todo | Prompt-slot registry resolver pending canonical declarative manifest | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `three-bucket-otel-view-5db409` | W9.1 | W9 | Todo | GenAI SIG semconv migration across 20 OTel emit sites | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `w6-1-tooling-guardian-codemod-d4e8a7` | W6.1-PROD | W6 | Done | [P2] W6.1 production CLOSED — 100pct guardian coverage L0-L6/L_APP/etc (massive  | dependencies |
| `w6-1-tooling-guardian-codemod-d4e8a7` | W6.1-TOOLING-DONE | W6 | Done | [P2] W6.1-Tooling Guardian Codemod DONE — 100pct coverage across ALL 1313 sites  | dependencies |
| `w6-1-tooling-guardian-codemod-d4e8a7` | W6.1-TOOLING-PLAN | W6 | Todo | [P4] W6.1-Tooling Guardian Codemod — dedicated plan queued (863 offline-tooling  | dependencies |
| `w6-w7-continuation-a7b3d2` | W6-W7-CONTINUATION-P0 | W6-W7 | In Progress | [P2] W6-W7 Continuation — Batch Closure Plan (W6.2b+c, W6.3-P1, W7.1-P0) | dependencies |
| `w6-w7-continuation-a7b3d2` | W6.2bc-W6.3-P1-CLOSURE | W6 | Done | [P4] W6 W6.2b-c + W6.3-P1 — CLOSED as no-migration-needed (context review) | dependencies |
| `w7-p1-adr-tooling-followup-b5c9e2` | ADR-051-AMEND | W7 | Done | [P3] ADR-051 Amendment — scope collapse from 54 to 3 violations + SC-1 plan revi | dependencies |
| `w7-p1-adr-tooling-followup-b5c9e2` | W6.3-TOOLING | W6 | Done | [P3] W6.3-Tooling — triage classifier 4 context filters (30→8 ACCIDENTAL_CONCAT, | dependencies |
| `w7-p1-adr-tooling-followup-b5c9e2` | W7-FOLLOWUP-P0 | W7 | In Progress | [P2] W7.1-P1 + ADR-051 revision + triage classifier enhancement — follow-up plan | dependencies |
| `windsurf-maintenance-2026-q2-0f3564` | NEXT-193ef507 | W-NEXT | Todo | [P4] 2026-07-27 re-run quarterly plan archival | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `windsurf-maintenance-2026-q2-0f3564` | NEXT-3601f39c | W-NEXT | Todo | [P3] 2026-07-27 audit per-router constitutional 29 auto-retire eligibility | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `windsurf-maintenance-2026-q2-0f3564` | NEXT-4876c7bb | W-NEXT | Todo | [P4] 2026-07-21 remove anti-pattern-hitl-gate.md deprecated shim | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `windsurf-maintenance-2026-q2-0f3564` | NEXT-9526d00f | W-NEXT | Todo | [P5] monitor anthropics/claude-agent-sdk-typescript#41 for fix (constitutional 2 | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `windsurf-maintenance-2026-q2-0f3564` | NEXT-c381d51b | W-NEXT | Todo | [P3] 2026-05-04 drop --advisory from staleness gate (graduate to strict) | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `windsurf-maintenance-2026-q2-0f3564` | NEXT-c7cd388b | W-NEXT | Todo | [P3] 2026-07-26 audit constitutional 30 auto-retire eligibility | sub_wave, dependencies, success_criteria, parent_plan_summary |
| `windsurf-maintenance-2026-q2-0f3564` | NEXT-c8e79b3f | W-NEXT | Todo | [P3] 2026-04-28 verify Author-Gate capture criterion 3 (24h non-zero captured/da | sub_wave, dependencies, success_criteria, parent_plan_summary |

---
Generated by `tools/reports/audit_notion_backlog_coverage.py` at 2026-04-30T01:20:28.077251+00:00.
Re-run: `python tools/reports/audit_notion_backlog_coverage.py`
