---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\d-bucket-burndown-e4f2c9.md'
original_relative_path: 'd-bucket-burndown-e4f2c9.md'
source_sha256: 67841aec703b765dba5d6c1af320e9c534ca84ae2f46d53fa8b3a18e2f183843
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-02'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# D-Bucket Burndown Wave Plan — ⚠️ RETIRED

Generated: 2026-05-02  ·  **Status: Retired 2026-05-02** (decomposed into 3 per-wave plans)  ·  Companion (historical): `backlog-keep-triage-d2e4f1`

## Retirement Notice

Per Author-Gate 2026-05-02 (session): this aggregator plan was decomposed into three per-wave Live plans so status telemetry cleanly reflects per-wave progress. The aggregator stays Retired in both the on-disk plan file and the Notion Plans-DB row.

| New Plan | Scope | Status |
|---|---|---|
| `d-bucket-w2-burndown-a2c4f1.md` | W2 — 17 rows across 3 plans (max impact 444) | Live |
| `d-bucket-w3-burndown-b3d5e2.md` | W3 — 19 rows across 6 plans (max impact 361) | Live |
| `d-bucket-w4-burndown-c4e6f3.md` | W4 — 77 rows across 32 plans (max impact 229) | Live |

W1 (1 row, `l6-gravity-hybrid-7c4e2a.md`) completed 2026-05-02 via `session-burndown-2026-05-02-c8f3a4` + ADR-095 and is not carried into a new plan.

**Do not add new content here.** All future D-bucket burndown updates land in the three per-wave plans above.

## Historical Context

Remaining 114 D-bucket rows after mechanical pass 2. These represent real engineering work, not admin. Waves below group by plan file and size by combined impact score. Execution is cross-session: W1 first, then stop for review.

## Wave Structure

| Wave | Plans | Row Count | Max Impact | Est. Days | Status |
|---|---|---:|---:|---:|---|
| W1 | `l6-gravity-hybrid-7c4e2a.md` (1) | 1 | 677 | 1 | ✅ Done 2026-05-02 (row already Completed via session-burndown-2026-05-02-c8f3a4 + ADR-095) |
| W2 | `gap-closure-test-impl-b77a11.md` (12; 1 already Completed, 4 P1 runtime-cert rows now Phase-F-gated — Phase E.1 advisory gate delivered 2026-05-02 per `runtime-cert-e1-*.md` family + ADR-080 §9 E row ✅), `adg-architectural-p0-violations-cleanup-bced9c.md` (2), `phase-b-blocker-burndown-a8c4f1.md` (3) | 17 | 444 | 5 | 🔄 In Progress — Phase E.1 wired 2026-05-02; remaining W2 rows = 3 non-gated phase-b P1 + 2 adg-architectural + 8 L2-test P2 |
| W3 | `audit-uncovered-gates-and-remediation-627368.md` (2), `repo-tech-debt-wave1-b3c8d1.md` (6), `l0-routing-calibration-gap-audit-b3c9d4.md` (5), `runtime-adg-coverage-audit-4f7a21.md | 19 | 361 | 6 | Draft |
| W4 | `anthropic-rag-gaps-7f3c2a.md` (2), `windsurf-maintenance-2026-q2-0f3564.md` (1), `prompt-assembly-best-practices-gap-b4e1c2.md` (14), `adg-three-bucket-unified-c4f8e2.md` (5), `sc | 77 | 229 | 25 | Draft |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1.l6-gravity-hybrid-7c | Burn down l6-gravity-hybrid-7c4e2a.md D-rows | Notion rows attached to l6-gravity-hybrid-7c4e2a.md — 1 items | bands={'P1': 1}; max impact 677 | 3000 | Draft |
| W2.gap-closure-test-imp | Burn down gap-closure-test-impl-b77a11.md D-rows | Notion rows attached to gap-closure-test-impl-b77a11.md — 12 items | bands={'P2': 9, 'P1': 2, 'P3': 1}; max impact 444 | 36000 | Draft |
| W2.adg-architectural-p0 | Burn down adg-architectural-p0-violations-cleanup-bced9c.md D-rows | Notion rows attached to adg-architectural-p0-violations-cleanup-bced9c.md — 2 items | bands={'P1': 1, 'P3': 1}; max impact 390 | 6000 | Draft |
| W2.phase-b-blocker-burn | Burn down phase-b-blocker-burndown-a8c4f1.md D-rows | Notion rows attached to phase-b-blocker-burndown-a8c4f1.md — 3 items | bands={'P1': 3}; max impact 384 | 9000 | Draft |
| W3.audit-uncovered-gate | Burn down audit-uncovered-gates-and-remediation-627368.md D-rows | Notion rows attached to audit-uncovered-gates-and-remediation-627368.md — 2 items | bands={'P2': 1, 'P1': 1}; max impact 361 | 6000 | Draft |
| W3.repo-tech-debt-wave1 | Burn down repo-tech-debt-wave1-b3c8d1.md D-rows | Notion rows attached to repo-tech-debt-wave1-b3c8d1.md — 6 items | bands={'P1': 2, 'P3': 2, 'P2': 2}; max impact 352 | 18000 | Draft |
| W3.l0-routing-calibrati | Burn down l0-routing-calibration-gap-audit-b3c9d4.md D-rows | Notion rows attached to l0-routing-calibration-gap-audit-b3c9d4.md — 5 items | bands={'P3': 2, 'P1': 1, 'P2': 2}; max impact 336 | 15000 | Draft |
| W3.runtime-adg-coverage | Burn down runtime-adg-coverage-audit-4f7a21.md (audit) | NEW:runtime-adg-trace-binding-remediation (remediation — not yet drafted) D-rows | Notion rows attached to runtime-adg-coverage-audit-4f7a21.md (audit) | NEW:runtime-adg-trace-binding-remediation (remediation — not yet drafted) — 1 items | bands={'P2': 1}; max impact 297 | 3000 | Draft |
| W3.c0-context-assembly- | Burn down c0-context-assembly-best-practices-b7c3a1.md D-rows | Notion rows attached to c0-context-assembly-best-practices-b7c3a1.md — 2 items | bands={'P2': 2}; max impact 254 | 6000 | Draft |
| W3.NEW:adg-mcp-reopen-h | Burn down NEW:adg-mcp-reopen-hardening (to be created) D-rows | Notion rows attached to NEW:adg-mcp-reopen-hardening (to be created) — 3 items | bands={'P2': 3}; max impact 254 | 9000 | Draft |
| W4.anthropic-rag-gaps-7 | Burn down anthropic-rag-gaps-7f3c2a.md D-rows | Notion rows attached to anthropic-rag-gaps-7f3c2a.md — 2 items | bands={'P3': 1, 'P2': 1}; max impact 229 | 6000 | Draft |
| W4.windsurf-maintenance | Burn down windsurf-maintenance-2026-q2-0f3564.md D-rows | Notion rows attached to windsurf-maintenance-2026-q2-0f3564.md — 1 items | bands={'P2': 1}; max impact 220 | 3000 | Draft |
| W4.prompt-assembly-best | Burn down prompt-assembly-best-practices-gap-b4e1c2.md D-rows | Notion rows attached to prompt-assembly-best-practices-gap-b4e1c2.md — 14 items | bands={'--': 10, 'P2': 3, 'P3': 1}; max impact 204 | 42000 | Draft |
| W4.adg-three-bucket-uni | Burn down adg-three-bucket-unified-c4f8e2.md D-rows | Notion rows attached to adg-three-bucket-unified-c4f8e2.md — 5 items | bands={'P3': 4, 'P5': 1}; max impact 148 | 15000 | Draft |
| W4.sc1-audit-to-enforce | Burn down sc1-audit-to-enforce-promotion-b4e9d7.md D-rows | Notion rows attached to sc1-audit-to-enforce-promotion-b4e9d7.md — 1 items | bands={'P3': 1}; max impact 144 | 3000 | Draft |
| W4.notion-schema-refact | Burn down notion-schema-refactor-cleanup-9f2e4a.md D-rows | Notion rows attached to notion-schema-refactor-cleanup-9f2e4a.md — 8 items | bands={'P5': 1, 'P3': 2, '--': 5}; max impact 130 | 24000 | Draft |
| W4.scorer-otel-autosour | Burn down scorer-otel-autosource-layer-b-c5e4d1.md D-rows | Notion rows attached to scorer-otel-autosource-layer-b-c5e4d1.md — 4 items | bands={'P4': 1, 'P3': 3}; max impact 106 | 12000 | Draft |
| W4.chromadb-bge-retriev | Burn down chromadb-bge-retrieval-hardening-e9aa09.md D-rows | Notion rows attached to chromadb-bge-retrieval-hardening-e9aa09.md — 1 items | bands={'P3': 1}; max impact 100 | 3000 | Draft |
| W4.fortknox-100pct-stat | Burn down fortknox-100pct-static-runtime-gap-9a3d4f.md D-rows | Notion rows attached to fortknox-100pct-static-runtime-gap-9a3d4f.md — 1 items | bands={'P5': 1}; max impact 50 | 3000 | Draft |
| W4.decision-router-poli | Burn down decision-router-policy-tables-b3a4d2.md D-rows | Notion rows attached to decision-router-policy-tables-b3a4d2.md — 1 items | bands={'--': 1}; max impact 0 | 3000 | Draft |
| W4.adg-truth-expansion- | Burn down adg-truth-expansion-r5w1-a8f3c2 D-rows | Notion rows attached to adg-truth-expansion-r5w1-a8f3c2 — 1 items | bands={'--': 1}; max impact 0 | 3000 | Draft |
| W4.notion-backlog-schem | Burn down notion-backlog-schema-refactor-7c3d9e D-rows | Notion rows attached to notion-backlog-schema-refactor-7c3d9e — 1 items | bands={'--': 1}; max impact 0 | 3000 | Draft |
| W4.next-step-gate-ci-wo | Burn down next-step-gate-ci-workflow-8733a6 D-rows | Notion rows attached to next-step-gate-ci-workflow-8733a6 — 1 items | bands={'--': 1}; max impact 0 | 3000 | Draft |
| W4.adg-tree-sitter-pars | Burn down adg-tree-sitter-parser-exploration-b1c517.md D-rows | Notion rows attached to adg-tree-sitter-parser-exploration-b1c517.md — 1 items | bands={'P4': 1}; max impact 0 | 3000 | Draft |
| W4.mcp-serial-defense-l | Burn down mcp-serial-defense-l2l5-7d4f1a.md D-rows | Notion rows attached to mcp-serial-defense-l2l5-7d4f1a.md — 1 items | bands={'--': 1}; max impact 0 | 3000 | Draft |
| W4.adg-cascading-ratche | Burn down adg-cascading-ratchet-defer-exit-a41828.md D-rows | Notion rows attached to adg-cascading-ratchet-defer-exit-a41828.md — 1 items | bands={'P4': 1}; max impact 0 | 3000 | Draft |
| W4.notion-backlog-human | Burn down notion-backlog-human-scoring-e7a941.md D-rows | Notion rows attached to notion-backlog-human-scoring-e7a941.md — 5 items | bands={'P3': 5}; max impact 0 | 15000 | Draft |
| W4.shadow-learning-best | Burn down shadow-learning-bestpractice-gap-7b3e4c.md D-rows | Notion rows attached to shadow-learning-bestpractice-gap-7b3e4c.md — 2 items | bands={'--': 2}; max impact 0 | 6000 | Draft |
| W4.runtime-adg-tier3-br | Burn down runtime-adg-tier3-broader-adoption-8f2d1c.md D-rows | Notion rows attached to runtime-adg-tier3-broader-adoption-8f2d1c.md — 1 items | bands={'P5': 1}; max impact 0 | 3000 | Draft |
| W4.adg-wiring-ci-dispat | Burn down adg-wiring-ci-dispatcher-hardening-b2f4a1.md D-rows | Notion rows attached to adg-wiring-ci-dispatcher-hardening-b2f4a1.md — 5 items | bands={'P1': 1, 'P2': 2, 'P3': 2}; max impact 0 | 15000 | Draft |
| W4.judge-surface-harmon | Burn down judge-surface-harmonization-b9d3a7.md D-rows | Notion rows attached to judge-surface-harmonization-b9d3a7.md — 1 items | bands={'P2': 1}; max impact 0 | 3000 | Draft |
| W4.llm-judge-hardening- | Burn down llm-judge-hardening-followups-f2c8e1.md D-rows | Notion rows attached to llm-judge-hardening-followups-f2c8e1.md — 1 items | bands={'P1': 1}; max impact 0 | 3000 | Draft |
| W4.llm-as-judge-hardeni | Burn down llm-as-judge-hardening-anthropic-e7b1a4.md D-rows | Notion rows attached to llm-as-judge-hardening-anthropic-e7b1a4.md — 1 items | bands={'P1': 1}; max impact 0 | 3000 | Draft |
| W4.moe-agentic-architec | Burn down moe-agentic-architecture-d4e9a2.md D-rows | Notion rows attached to moe-agentic-architecture-d4e9a2.md — 1 items | bands={'P1': 1}; max impact 0 | 3000 | Draft |
| W4.prompt-assembly-few- | Burn down prompt-assembly-few-shot-exemplars-9c4e2b.md D-rows | Notion rows attached to prompt-assembly-few-shot-exemplars-9c4e2b.md — 1 items | bands={'P2': 1}; max impact 0 | 3000 | Draft |
| W4.prompt-categories-co | Burn down prompt-categories-coverage-audit-b8f5d3.md D-rows | Notion rows attached to prompt-categories-coverage-audit-b8f5d3.md — 1 items | bands={'P1': 1}; max impact 0 | 3000 | Draft |
| W4.cot-reflexion-self-c | Burn down cot-reflexion-self-consistency-config-7a3f1c.md D-rows | Notion rows attached to cot-reflexion-self-consistency-config-7a3f1c.md — 1 items | bands={'P1': 1}; max impact 0 | 3000 | Draft |
| W4.hybrid-search-adg-se | Burn down hybrid-search-adg-seed-rerank-c58e21.md D-rows | Notion rows attached to hybrid-search-adg-seed-rerank-c58e21.md — 1 items | bands={'P3': 1}; max impact 0 | 3000 | Draft |
| W4.ssot-violations-swee | Burn down ssot-violations-sweep-29caf4.md D-rows | Notion rows attached to ssot-violations-sweep-29caf4.md — 2 items | bands={'P3': 1, 'UNSCORED': 1}; max impact 0 | 6000 | Draft |
| W4.p2-burndown-wave-9e4 | Burn down p2-burndown-wave-9e4c17.md D-rows | Notion rows attached to p2-burndown-wave-9e4c17.md — 2 items | bands={'P3': 2}; max impact 0 | 6000 | Draft |
| W4.ssot-consolidation-c | Burn down ssot-consolidation-cleanup-b7f3a1.md D-rows | Notion rows attached to ssot-consolidation-cleanup-b7f3a1.md — 8 items | bands={'P3': 8}; max impact 0 | 24000 | Draft |

## Files In Scope

- Notion Backlog Items DB (data source `fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7`)
- Each plan file referenced above under `.windsurf/plans/`
- `tools/notion/burndown_d_bucket.py` — this driver

## ADG_GRAPH_LAYER_EVIDENCE

Not applicable — governance plan. ADG evidence lives in each child plan.

## ADG_HOTSPOT_REPORT

Not applicable — see above.

## W1 Detail — top-impact plan (start here)

### `l6-gravity-hybrid-7c4e2a.md` — 1 rows

| Band | Impact | Title |
|---|---:|---|
| P1 | 677 | [P1] 2_authority_boundary P0 17 cross-layer authority breaches |
