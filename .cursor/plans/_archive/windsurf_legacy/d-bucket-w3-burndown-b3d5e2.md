---
plan_id: d-bucket-w3-burndown-b3d5e2
plan_type: tracker
---

# D-Bucket W3 Burndown — 19 rows across 6 plans

- **Status**: Live
- **Generated**: 2026-05-02 (decomposed from retired `d-bucket-burndown-e4f2c9.md` per AG 2026-05-02)
- **Max Impact**: 361
- **Est. Days**: 6

## Context (SCQA)

- **Situation** — 19 D-bucket backlog rows span 6 child plans. All Draft as of 2026-05-02 (no reconciliation sweep performed — rows may contain silent closures).
- **Complication** — W3 spans ADG architecture, routing calibration, runtime ADG coverage, and MCP hardening — wildly different surfaces.
- **Question** — sequence these 6 phases by impact / dependency?
- **Answer** — start with `audit-uncovered-gates` (P1/P2 highest impact 361) and `repo-tech-debt-wave1` (6 rows, mixed P1-P3); defer `NEW:` phases until their parent plans exist on disk.

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W3.audit-uncovered-gates | Burn down `audit-uncovered-gates-and-remediation-627368.md` D-rows | 2 rows: P2:1, P1:1 | Max impact 361 — highest in W3 | 6 000 | 🔲 TODO |
| W3.repo-tech-debt-wave1 | Burn down `repo-tech-debt-wave1-b3c8d1.md` D-rows | 6 rows: P1:2, P3:2, P2:2 | Broad tech-debt scope | 18 000 | 🔲 TODO |
| W3.l0-routing-calibration | Burn down `l0-routing-calibration-gap-audit-b3c9d4.md` D-rows | 5 rows: P3:2, P1:1, P2:2 | L0 routing calibration data gaps | 15 000 | 🔲 TODO |
| W3.runtime-adg-coverage | Burn down `runtime-adg-coverage-audit-4f7a21.md` + `runtime-adg-trace-binding-remediation-d7e8f9.md` D-rows | 1 row: P2:1 | Remediation plan now drafted 2026-05-02 | 3 000 | 🔲 TODO (plan drafted; awaiting AG) |
| W3.c0-context-assembly | Burn down `c0-context-assembly-best-practices-b7c3a1.md` D-rows | 2 rows: P2:2 | C0 retrieval/context assembly | 6 000 | 🔲 TODO |
| W3.adg-mcp-reopen-hardening | Burn down `adg-mcp-reopen-hardening-e8f9a0.md` D-rows | 3 rows: P2:3 | Plan drafted 2026-05-02 | 9 000 | 🔲 TODO (plan drafted; awaiting AG) |

## Out Of Scope

- W2 or W4 burndown rows (separate plans)
- Drafting parent plans for `NEW:*` phases — that is Author-Gate scope per-phase

## Recommended Entry

Start with `W3.audit-uncovered-gates` (highest impact). Query Notion for current row status first — some may have silently closed since aggregator last synced.

## Success Criteria

- [ ] All 19 rows either Completed or re-scoped (NEW plans drafted or rows descoped)
- [ ] This plan's Notion row flips Completed when scope resolves

## References

- Parent (retired): `.windsurf/plans/d-bucket-burndown-e4f2c9.md`
- Sibling waves: `d-bucket-w2-burndown-a2c4f1.md`, `d-bucket-w4-burndown-c4e6f3.md`
