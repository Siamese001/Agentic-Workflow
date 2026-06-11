---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\d-bucket-w4-burndown-c4e6f3.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\d-bucket-w4-burndown-c4e6f3.md'
source_sha256: b03c2eb42df14328fad9ff968274168e141458dd525e0c3a52e89752e42dfbeb
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: d-bucket-w4-burndown-c4e6f3
plan_type: tracker
---

# D-Bucket W4 Burndown — 77 rows across 32 plans

- **Status**: Live
- **Generated**: 2026-05-02 (decomposed from retired `d-bucket-burndown-e4f2c9.md` per AG 2026-05-02)
- **Max Impact**: 229
- **Est. Days**: 25

## Context (SCQA)

- **Situation** — 77 D-bucket backlog rows span 32 child plans. Max individual impact 229 — W4 is the long-tail bucket. All Draft as of 2026-05-02.
- **Complication** — 32 plans is an unmanageable single-session scope. Many rows have `max_impact=0` (score-below-floor rows that landed in D bucket by auto-triage rule, not priority).
- **Question** — which W4 sub-phases are worth executing vs descoping?
- **Answer** — this plan is the long-tail tracker. Execute by impact rank; reserve the right to descope entire sub-phases when review shows no-value work.

## Phase-Level Summary — by descending max impact

| Phase | Plan | Rows | Bands | Max Impact | Tokens | Status |
|---|---|---:|---|---:|---:|---|
| W4.anthropic-rag-gaps | `anthropic-rag-gaps-7f3c2a.md` | 2 | P3:1, P2:1 | 229 | 6 000 | 🔲 TODO |
| W4.windsurf-maintenance | `windsurf-maintenance-2026-q2-0f3564.md` | 1 | P2:1 | 220 | 3 000 | 🔲 TODO |
| W4.prompt-assembly-best-practices | `prompt-assembly-best-practices-gap-b4e1c2.md` | 14 | --:10, P2:3, P3:1 | 204 | 42 000 | 🔲 TODO (10 unscored — triage first) |
| W4.adg-three-bucket-unified | `adg-three-bucket-unified-c4f8e2.md` | 5 | P3:4, P5:1 | 148 | 15 000 | 🔲 TODO |
| W4.sc1-audit-to-enforce | `sc1-audit-to-enforce-promotion-b4e9d7.md` | 1 | P3:1 | 144 | 3 000 | 🔲 TODO |
| W4.notion-schema-refactor | `notion-schema-refactor-cleanup-9f2e4a.md` | 8 | P5:1, P3:2, --:5 | 130 | 24 000 | 🔲 TODO |
| W4.scorer-otel-autosource | `scorer-otel-autosource-layer-b-c5e4d1.md` | 4 | P4:1, P3:3 | 106 | 12 000 | 🔲 TODO |
| W4.chromadb-bge-retrieval | `chromadb-bge-retrieval-hardening-e9aa09.md` | 1 | P3:1 | 100 | 3 000 | 🔲 TODO |
| W4.fortknox-100pct-static-runtime | `fortknox-100pct-static-runtime-gap-9a3d4f.md` | 1 | P5:1 | 50 | 3 000 | 🔲 TODO |
| W4.decision-router-policy | `decision-router-policy-tables-b3a4d2.md` | 1 | --:1 | 0 | 3 000 | 🟡 triage (unscored) |
| W4.adg-truth-expansion | `adg-truth-expansion-r5w1-a8f3c2` | 1 | --:1 | 0 | 3 000 | 🟡 triage |
| W4.notion-backlog-schema | `notion-backlog-schema-refactor-7c3d9e` | 1 | --:1 | 0 | 3 000 | 🟡 triage |
| W4.next-step-gate-ci | `next-step-gate-ci-workflow-8733a6` | 1 | --:1 | 0 | 3 000 | 🟡 triage |
| W4.adg-tree-sitter | `adg-tree-sitter-parser-exploration-b1c517.md` | 1 | P4:1 | 0 | 3 000 | 🔲 TODO |
| W4.mcp-serial-defense | `mcp-serial-defense-l2l5-7d4f1a.md` | 1 | --:1 | 0 | 3 000 | 🟡 triage |
| W4.adg-cascading-ratchet | `adg-cascading-ratchet-defer-exit-a41828.md` | 1 | P4:1 | 0 | 3 000 | 🔲 TODO |
| W4.notion-backlog-human-scoring | `notion-backlog-human-scoring-e7a941.md` | 5 | P3:5 | 0 | 15 000 | 🔲 TODO |
| W4.shadow-learning-bestpractice | `shadow-learning-bestpractice-gap-7b3e4c.md` | 2 | --:2 | 0 | 6 000 | 🟡 triage |
| W4.runtime-adg-tier3 | `runtime-adg-tier3-broader-adoption-8f2d1c.md` | 1 | P5:1 | 0 | 3 000 | 🔲 TODO |
| W4.adg-wiring-ci-dispatcher | `adg-wiring-ci-dispatcher-hardening-b2f4a1.md` | 5 | P1:1, P2:2, P3:2 | 0 | 15 000 | 🔲 TODO (P1 row — re-verify impact) |
| W4.judge-surface-harmonization | `judge-surface-harmonization-b9d3a7.md` | 1 | P2:1 | 0 | 3 000 | 🔲 TODO |
| W4.llm-judge-hardening-followups | `llm-judge-hardening-followups-f2c8e1.md` | 1 | P1:1 | 0 | 3 000 | 🔲 TODO |
| W4.llm-as-judge-hardening-anthropic | `llm-as-judge-hardening-anthropic-e7b1a4.md` | 1 | P1:1 | 0 | 3 000 | 🔲 TODO |
| W4.moe-agentic-architecture | `moe-agentic-architecture-d4e9a2.md` | 1 | P1:1 | 0 | 3 000 | 🔲 TODO |
| W4.prompt-assembly-few-shot | `prompt-assembly-few-shot-exemplars-9c4e2b.md` | 1 | P2:1 | 0 | 3 000 | 🔲 TODO |
| W4.prompt-categories-coverage | `prompt-categories-coverage-audit-b8f5d3.md` | 1 | P1:1 | 0 | 3 000 | 🔲 TODO |
| W4.cot-reflexion-self-consistency | `cot-reflexion-self-consistency-config-7a3f1c.md` | 1 | P1:1 | 0 | 3 000 | 🔲 TODO |
| W4.hybrid-search-adg-seed-rerank | `hybrid-search-adg-seed-rerank-c58e21.md` | 1 | P3:1 | 0 | 3 000 | 🔲 TODO |
| W4.ssot-violations-sweep | `ssot-violations-sweep-29caf4.md` | 2 | P3:1, UNSCORED:1 | 0 | 6 000 | 🔲 TODO |
| W4.p2-burndown-wave | `p2-burndown-wave-9e4c17.md` | 2 | P3:2 | 0 | 6 000 | 🔲 TODO |
| W4.ssot-consolidation-cleanup | `ssot-consolidation-cleanup-b7f3a1.md` | 8 | P3:8 | 0 | 24 000 | 🔲 TODO |

## Out Of Scope

- W2 or W3 burndown rows
- Drafting parent plans (each child plan already exists on disk or is named)
- Automated reconciliation — rows requires Notion query before work begins

## Recommended Entry

1. First pass: triage 🟡 rows (unscored / `bands={--:N}`) — sweep Notion, score or descope.
2. Execute top-3-impact phases: `anthropic-rag-gaps` (229), `windsurf-maintenance` (220), `prompt-assembly-best-practices` (204 with 10 unscored to triage).
3. Descope aggressively: any row with `max_impact=0` AND `bands={P4/P5/--}` is a candidate for descope or merging with a higher-priority plan.

## Success Criteria

- [ ] Triage pass complete: no 🟡 rows remain
- [ ] All 77 rows either Completed or re-scoped / descoped
- [ ] This plan's Notion row flips Completed when scope resolves

## References

- Parent (retired): `.windsurf/plans/d-bucket-burndown-e4f2c9.md`
- Sibling waves: `d-bucket-w2-burndown-a2c4f1.md`, `d-bucket-w3-burndown-b3d5e2.md`
