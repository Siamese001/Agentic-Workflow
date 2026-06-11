---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\exit-eval-v6-gaps-d7a3f1.md'
original_relative_path: 'exit-eval-v6-gaps-d7a3f1.md'
source_sha256: f5675571245021fbc8440842559973ab6f3006bc28116788d0e2a18698a931fb
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Exit Evaluation v6 — Gap Closure

Status: In Progress
Plan ID: exit-eval-v6-gaps-d7a3f1
Source spec: `docs/reference/05_Exit_Evaluation_&_Control/05_Live_Runtime_Exit_Control_&_Evaluation_v6.md`

## Goal

Implement gaps against v6 spec without breaking existing v4/v5 modules in `agentic_core/L3_orchestration/exit_eval/`. Land a clean, testable v6 surface that future composition roots can adopt.

## Gap Inventory vs. v6 Spec

| Section | Existing | Gap → Action |
|---|---|---|
| 5.0 INPUTS RECEIVED — required receipts + immediate fails | Not implemented | NEW `v6/preflight.py` |
| 5.1 N1–N5 PRE-FLIGHT NORMALIZATION (ExitReviewPacket) | Not implemented | NEW `v6/preflight.py` |
| X1A Policy Manifest + Threshold + Grader Roster | Partial (rubric.py) | NEW `v6/x1_gates.py::eval_x1a` |
| X1B Task Completion + Format + Instruction-Follow | Partial | NEW `v6/x1_gates.py::eval_x1b` |
| X1C Sandbox + Mutation + Side-Effect + Egress | Partial | NEW `v6/x1_gates.py::eval_x1c` |
| X1D Groundedness + Citation + Support | Existing graders | NEW `v6/x1_gates.py::eval_x1d` (reuse contracts) |
| X1E Process / Tool / Retry / Handoff | Partial | NEW `v6/x1_gates.py::eval_x1e` |
| X1F Adversarial / Injection / Jailbreak / Leak | Partial | NEW `v6/x1_gates.py::eval_x1f` |
| X1G Consistency Modifier (pass^k) | Existing (consistency.py) | Wrap in `v6/x1_gates.py::eval_x1g` |
| X1H Replay & Determinism Integrity | **Missing** | NEW `v6/x1_gates.py::eval_x1h` |
| X1I Observability Complete | **Missing** | NEW `v6/x1_gates.py::eval_x1i` |
| X1J Write Eligibility (UWG Pre-Commit) | **Missing** | NEW `v6/x1_gates.py::eval_x1j` |
| X2 Aggregate Decision Matrix | Implicit in pipeline | NEW `v6/x2_matrix.py` |
| X3A DENY / REROUTE packet | Existing envelope | NEW `v6/x3_dispositions.py::build_x3a` |
| X3B ESCALATE / HITL packet + H1-H4 + L5 re-clear | Partial | NEW `v6/x3_dispositions.py::build_x3b` + `v6/hitl.py` |
| X3C COMMIT REQUEST → UWG packet + U1-U5 | Partial | NEW `v6/x3_dispositions.py::build_x3c` |
| X3D ALLOW / FINISH packet | Partial | NEW `v6/x3_dispositions.py::build_x3d` |
| X3E SAFE ABSTAIN / CLARIFY (v6 redefines) | Conflict — v5 X3E=BREAK_GLASS | NEW `v6` enum splits |

## Wave Structure

| Wave | Phase IDs | Focus | Est | Status |
|---|---|---|---|---|
| W1 | 1.1 | Types + ExitReviewPacket + GateVerdict + X3 enum | 4000 | Done |
| W2 | 2.1 | Preflight (5.0 + 5.1 N1-N5) | 3000 | Done |
| W3 | 3.1 | X1A-J gate evaluators | 8000 | Done |
| W4 | 4.1 | X2 aggregate decision matrix | 3000 | Done |
| W5 | 5.1 | X3A-E packet builders + HITL flow | 5000 | Done |
| W6 | 6.1 | Tests | 6000 | Done |
| W7 | 7.1 | Format + commit + push | 1000 | Done |

## Phase-Level Summary

| Phase | Title | Scope | Pain | Est | Status |
|---|---|---|---|---|---|
| 1.1 | Types | v6/types.py | Naming conflict with v5 | 4000 | Done |
| 2.1 | Preflight | v6/preflight.py | 7 immediate-fail conditions | 3000 | Done |
| 3.1 | X1 gates | v6/x1_gates.py | 10 evaluators | 8000 | Done |
| 4.1 | X2 matrix | v6/x2_matrix.py | hard-fail / escalate / allow / commit | 3000 | Done |
| 5.1 | X3 + HITL | v6/x3_dispositions.py + v6/hitl.py | packet shape + L5 re-clear | 5000 | Done |
| 6.1 | Tests | tests/.../v6/test_*.py | preflight + each X1 + X2 + X3 + HITL | 6000 | Done |
| 7.1 | Land | git | none | 1000 | Done |

## Out of Scope

- Production composition-root wiring (NEXT_STEP follow-up).
- LLM judge integration (existing v5 graders cover this).
- HITL adapter wiring (existing v5 has Slack/Notion/Orkes adapters).
