---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\backlog-keep-triage-d2e4f1.md'
original_relative_path: '_archive\\2026-05\\backlog-keep-triage-d2e4f1.md'
source_sha256: 4018374bc095ae5318d37ed7df2610d51e41ad0c65e7a881990874ba28b71c11
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Backlog Triage — KEEP-bucket Wave Plan

Generated: 2026-05-02  ·  Status: Live

## Context

Companion to `bulk_flip_stale_drafts` (2026-05-02): of the 298 Draft rows in the Backlog Items DB, 89 were closed (commit-attested) and 54 retired (plan deleted). The remaining ~155 are triaged here.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W1 | A.1 | Annotate 7 time/dep-gated rows: stays Draft, recorded reason | 4000 | Rows have explicit gating language in Blocking Items | Live | All A-rows have Evidence stamped `[TRIAGE 2026-05-02] bucket=A` |
| W2 | B.1 | Annotate 3 BACKLOG/future-idea rows: stays Draft, recorded reason | 2000 | Rows tagged MCP-BACKLOG / NEXT·P* / FUTURE | Live | All B-rows stamped `bucket=B` |
| W3 | C.1 | Retire 22 soft-closure rows (work likely done, no commit attestation) | 4000 | Soft-match on 'implemented/complete/landed' without commit SHA; spot-check via audit log | Live | C-rows flipped to Retired with reason |
| W4 | D.1 | Surface 124 unblocked rows ranked by Impact Score for next-session pickup | 1000 | No mutation; ranking only | Live | Top-N table emitted in this plan |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| A.1 | Annotate gated Drafts | Notion Backlog Items DB (7 rows) | None — pure annotation | 4000 | Live |
| B.1 | Annotate BACKLOG-tagged Drafts | Notion Backlog Items DB (3 rows) | None — pure annotation | 2000 | Live |
| C.1 | Retire soft-closure Drafts | Notion Backlog Items DB (22 rows) | False-positive risk if 'complete' refers to phase title | 4000 | Live |
| D.1 | Rank unblocked work queue | Notion Backlog Items DB (124 rows) | None — read-only | 1000 | Live |

## Files In Scope

- `tools/notion/triage_keep_drafts.py` — this triage script
- `tools/notion/bulk_flip_stale_drafts.py` — predecessor (already executed 2026-05-02)
- Notion Backlog Items DB (data source `fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7`)

## Bucket Detail

### Bucket A — Time/Dependency-Gated (7 rows)

- `[--]` [P2] W4 — HOP4 + HOP7 source deletion (90-day deprecation gate)
- `[P3]` [P3] 2026-07-27 audit per-router constitutional 29 auto-retire eligibility
- `[P3]` [P3] 2026-07-26 audit constitutional 30 auto-retire eligibility
- `[P4]` [P4] 2026-07-21 remove anti-pattern-hitl-gate.md deprecated shim
- `[P1]` [P1] Runtime gate G01-G29 invocation map tests (00C.9)
- `[P1]` [P1] L5 runtime certification binding tests (00A.8)
- `[UNSCORED]` W2 RH2 — Structured CompiledPromptArtifact + Anthropic & OpenAI adapters

### Bucket B — BACKLOG / Future Ideas (3 rows)

- `[P3]` [P3] MCP-BACKLOG — time (BACKLOG)
- `[P2]` [PLAN] apps_lic LinkedIn response-rate maximization — 10 enhancement opportuniti
- `[--]` [NEXT·P3] W2 — Triage 905 write-sovereignty residue into 3 groups

### Bucket C — Soft Closure (likely done) (22 rows)

- `[--]` [P2] W-LQ — L5 v4 Full Wire-In Chain (L through Q) — 6 consecutive waves
- `[--]` [P3] HITL → Author-Gate rename sweep (harness-side active surface)
- `[--]` [META] Wave E — Push to origin/main
- `[--]` [META] Wave D — Band-extraction for 68 unscorable
- `[--]` [META] Wave C — Rewrite 3 PARTIAL Blocking Items
- `[--]` [META] Wave B — Investigate 4 questionable scores
- `[--]` [META] Wave A — Apply 4 valid Pass 1 scores
- `[--]` [P1] W1-W5 — Author-Gate meta-learning end-to-end hardening
- `[--]` [P4] F1 F1.1 — Seed golden queue + real trial counts in capability runner
- `[--]` [P2] F5 F5.2 — Heartbeat-driven MCP restart supervisor
- ... and 12 more (see audit log)

### Bucket D — Genuinely Unblocked (124 rows)

- `[P5]` [P5] FINAL — FINAL_SIGNED_CERTIFICATION via cosign keyless (Sigstore Fulcio + Gi
- `[P2]` [P2] Wire on-disk SQLite decision ledger as true SSOT (Notion -> mirror)
- `[--]` [P3] W3 — HOP1 archetype_classifier.yaml + classifier-chain refactor
- `[--]` [P3] ADG Truth Expansion R5 Wave 1 — A8 + A6 + A12
- `[--]` [P3] Notion Backlog Schema Refactor — typed fields + projection pattern
- `[--]` [P3] next-step-gate-ci-workflow — run notion-plan-file-drift nightly
- `[P3]` [P3] Prompt-slot registry resolver pending canonical declarative manifest
- `[P5]` [P4] Schema graduation to column-level NOT NULL after 4-week green window
- `[P1]` [P1] C2_l5_bypass_pview P0 L5 safety plane bypass
- `[P2]` [P2] G2_seam_test_export_coherence P1 6 test export coherence violations
- ... and 114 more (see audit log)

## D-Bucket Ranked Work Queue (next-session candidates)

| Rank | Band | Impact | Title | Plan File |
|---:|---|---:|---|---|
| 1 | P1 | 676.6 | [P1] 2_authority_boundary P0 17 cross-layer authority breaches | `l6-gravity-hybrid-7c4e2a.md` |
| 2 | P1 | 443.9 | [P1] L4 blueprint policy version migration tests (00B.9) | `gap-closure-test-impl-b77a11.md` |
| 3 | P1 | 404.5 | [P1] L3-L2 step handoff checkpoint resume tests (03.9) | `gap-closure-test-impl-b77a11.md` |
| 4 | P1 | 390.3 | [P1] C2_l5_bypass_pview P0 L5 safety plane bypass | `.cursor/plans/adg-architectural-p0-violations-cl` |
| 5 | P1 | 384.1 | [P1] 4_capability_egress P0 outbound calls bypass capability adapter | `phase-b-blocker-burndown-a8c4f1.md` |
| 6 | P1 | 360.8 | [P1] W7 W7.4 — D7 gate over-flags subsystems dispatched via dynamic im | `.cursor/plans/audit-uncovered-gates-and-remediat` |
| 7 | P1 | 351.9 | [P1] W-LATER SSOT-HARDCODING-W2 — DEFERRED top 10 hardcoded path liter | `repo-tech-debt-wave1-b3c8d1.md` |
| 8 | P1 | 336.1 | [P1] W2 W2.P1 — move similarity_threshold and abstain threshold litera | `l0-routing-calibration-gap-audit-b3c9d4.md` |
| 9 | P1 | 318.8 | [P1] v_p0_write_bypass_uwg P0 state write does not flow through L4 UWG | `phase-b-blocker-burndown-a8c4f1.md` |
| 10 | P1 | 318.8 | [P1] C1_uwg_bypass_pview P0 single row UWG bypass pview | `phase-b-blocker-burndown-a8c4f1.md` |

## ADG_GRAPH_LAYER_EVIDENCE

Not applicable — this is a backlog-governance plan, not a code refactor. No agentic_core mutations. ADG snapshot unchanged. Constitutional §22 graph-layer evidence requirement applies to T2/T3 *refactoring* plans only.

## ADG_HOTSPOT_REPORT

Not applicable — see above.
