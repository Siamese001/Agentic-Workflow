---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\d-bucket-w2-burndown-a2c4f1.md'
original_relative_path: '_archive\\2026-05\\d-bucket-w2-burndown-a2c4f1.md'
source_sha256: 2330058c5ac4530eee30d4ce26ec0f18fc5786910fc94712c78a6ebe6fcc0448
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: d-bucket-w2-burndown-a2c4f1
plan_type: tracker
---

# D-Bucket W2 Burndown — 17 rows across 3 plans

- **Status**: Live
- **Generated**: 2026-05-02 (decomposed from retired `d-bucket-burndown-e4f2c9.md` per AG 2026-05-02)
- **Max Impact**: 444
- **Est. Days**: 5

## Context (SCQA)

- **Situation** — 17 D-bucket backlog rows span 3 child plans. As of 2026-05-02: 1 row Completed (04.0 L2 sequencer orchestrator), 4 runtime-cert rows wired-advisory via Phase E.1 (still gated on Phase E-strict + Phase F), 12 genuinely open rows.
- **Complication** — rows are heterogeneous (P1 UWG/capability violations + P2 L2 tests + P3 architectural clean-up); previous aggregator plan mixed waves and could never close cleanly.
- **Question** — how to drive W2 rows to Done without re-aggregating across unrelated concerns?
- **Answer** — this plan is the single-wave tracker for W2. Close row-by-row. Plan flips Completed when all 17 rows Done or re-scoped.

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W2.phase-b-blocker | Burn down `phase-b-blocker-burndown-a8c4f1.md` D-rows | 3 P1 rows: `v_p0_write_bypass_uwg`, `4_capability_egress`, `C1_uwg_bypass_pview` | Write-surface P0 violations; UWG bypass | 9 000 | 🔲 TODO (highest standalone value; not gated) |
| W2.gap-closure-test-impl | Burn down `gap-closure-test-impl-b77a11.md` D-rows | 12 rows: 1 Completed + 4 runtime-cert (Phase-F-gated) + 7 L2/E2E P2 tests | Heterogeneous; 4 rows depend on Phase F delivery | 36 000 | 🔄 PARTIAL (1 Done) |
| W2.adg-architectural-p0 | Burn down `adg-architectural-p0-violations-cleanup-bced9c.md` D-rows | 2 rows: P1 UWG-bypass pview + P3 SC-1/P0 remediation | SC-1 gravity violations surfaced during W8 | 6 000 | 🔲 TODO |

## Rows In Scope

### `phase-b-blocker-burndown-a8c4f1.md` (3 P1 rows, all Draft, max impact 384)

| Band | Impact | Title |
|---|---:|---|
| P1 | 384 | `4_capability_egress` P0 outbound calls bypass capability adapter |
| P1 | 319 | `v_p0_write_bypass_uwg` P0 state write does not flow through L4 UWG |
| P1 | 319 | `C1_uwg_bypass_pview` P0 single row UWG bypass pview |

### `gap-closure-test-impl-b77a11.md` (12 rows, mixed status, max impact 444)

| Band | Impact | Status | Title | Note |
|---|---:|---|---|---|
| P2 | 287 | ✅ Completed | `L2 sequencer orchestrator contract tests (04.0)` | ADG-VERIFIED CLOSURE 2026-05-02 |
| P1 | 661 | Phase-F-gated | `Runtime gate G01-G29 invocation map tests (00C.9)` | Phase E.1 advisory wired; flip-to-strict + Phase F required |
| P1 | 612 | Phase-F-gated | `L5 runtime certification binding tests (00A.8)` | same |
| P1 | 444 | Phase-F-gated | `L4 blueprint policy version migration tests (00B.9)` | same |
| P1 | 405 | Phase-F-gated | `L3-L2 step handoff checkpoint resume tests (03.9)` | same |
| P2 | 286 | Draft | `L2 StateDiffCandidate mutation intent tests (04.9)` | |
| P2 | 277 | Draft | `PA authority red-team slot verification tests (PA.8)` | |
| P2 | 254 | Draft | `PTC v2 sandbox hardening tests (04.7)` | |
| P2 | 240 | Draft | `L2 verify-then-execute local critique tests (04.10)` | |
| P2 | 161 | Draft | `E2E fixtures replay harness commands tests (99.10)` | |
| P2 | 161 | Draft | `E2E mutation testing boundary faults tests (99.9)` | |
| P2 | — | Draft | `06.9` interface tests (from aggregator truncation) | verify title |

### `adg-architectural-p0-violations-cleanup-bced9c.md` (2 rows, max impact 390)

| Band | Impact | Title |
|---|---:|---|
| P1 | 390 | P1 architectural P0 violation (to re-verify title via Notion query) |
| P3 | 0 | `Remediate the 3 SC-1 + 2 P0 architectural violations surfaced during W8 validation` |

## Out Of Scope

- W3 or W4 burndown rows (separate plans)
- Phase E fail-closed flip (separate plan `runtime-cert-e1-fail-closed-ci-gate-c71f3d.md` — Author-Gate APPROVED, requires 30-day advisory data)
- Phase F scanner / promotion (gated on Phase E flip)

## Recommended Entry

**Start with `phase-b-blocker` phase** — 3 P1 rows, non-gated, ~9k tokens, closes 3 P0 constitutional violations. Author focused T2 plan at `.cursor/plans/phase-b-blocker-3p1-burndown-<6hex>.md` with ADG_HOTSPOT_REPORT + ADG_GRAPH_LAYER_EVIDENCE.

## Success Criteria

- [ ] All 17 rows either Completed or re-scoped (moved to Phase F plan for the 4 gated ones)
- [ ] This plan's Notion row flips Completed when scope resolves

## References

- Parent (retired): `.cursor/plans/d-bucket-burndown-e4f2c9.md`
- Phase E.1 status: `docs/architecture/adr/ADR-080-runtime-cert-phase-d-planning.md` §9
- ADG canonical invariants: `.cursor/rules/adg-canonical-invariants.md`
