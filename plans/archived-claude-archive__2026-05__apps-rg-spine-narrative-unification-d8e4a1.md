---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-spine-narrative-unification-d8e4a1.md'
original_relative_path: '_archive\\2026-05\\apps-rg-spine-narrative-unification-d8e4a1.md'
source_sha256: ce6d7e43d13320131b38e1c328bb56367485bd33f8c28e84f26ac0248fde18c6
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg Spine/Narrative Unification — Single-Dir + Sealed L2/Exit/L6 Receipts

> Plan ID: `apps-rg-spine-narrative-unification-d8e4a1`
> Tier: T3 (cross-layer apps_rg → agentic_core)
> Status: In Progress
> Created: 2026-05-07

PLAN_CREATED: slug=apps-rg-spine-narrative-unification-d8e4a1 layer=L_APP+L_RUNTIME

## Problem Statement

apps_rg runs split artifacts across two dirs and fail to seal R4 spine receipts:

- **Spine dir**: `runs/r4_<resume_hash[:8]>/` — receives identity, c0, route_contract, how_trace
- **Narrative dir**: `runs/<YYYYMMDD_HHMMSS>/` — receives generated_resume, run_report, scorecards, DOCX
- **Result**: HowTrace reports `success: false` with 5 blocking gaps (`U0_INTAKE_validated_request_missing`, `R1B_L3_bypass_receipt_missing`, `R1B_L2_terminal_ret_packet_missing`, `EXIT_X3_packet_or_disposition_missing`, `L6_runtime_exhaust_or_trace_snapshot_missing`)

L2 hops execute correctly; the spine never seals their output as `terminal_ret_packet.json`.

## Root Cause

1. **Path bug**: `apps_rg/scripts/generate_resume.py:279` invents its own timestamp dir, ignoring the `artifact_dir` set by `apps_rg/__main__.py:259`
2. **Shape bug**: `GenerateResumeStep` returns a generic dict; spine cannot project it into `TerminalRetPacket` envelope

## Wave Structure

| Wave | Phases | Focus | Est. Tokens | Status |
|---|---|---|---|---|
| W1 | P1, P2 | Plumb `artifact_dir` through L2 callable into `generate_resume.main(out_dir=...)` | ~3k | Pending |
| W2 | P3 | Make `GenerateResumeStep` return `terminal_ret_packet`-shaped result | ~2k | Pending |
| W3 | P4, P5 | Spine writes `terminal_ret_packet.json`, `exit_review_packet.json`, `x3_disposition_receipt.json`, `runtime_exhaust_bundle.json`, `runtime_trace_snapshot.json` | ~4k | Pending |
| W4 | P6 | Re-run apps_rg, verify `success: true` and zero blocking gaps | ~1k | Pending |

## Phase-Level Summary

| Phase | Title | Scope | Pain Points | Tokens | Status |
|---|---|---|---|---|---|
| P1 | Thread artifact_dir into raw_request | `apps_rg/__main__.py` | Must not break R1A cache key (artifact_dir is NOT part of replay key) | ~1k | Pending |
| P2 | `generate_resume.main(out_dir)` accepts override | `apps_rg/scripts/generate_resume.py` | Backward-compat for direct CLI invocation | ~2k | Pending |
| P3 | `GenerateResumeStep` reads context['artifact_dir'], returns sealed envelope | `apps_rg/l2_recipe/steps.py` | Step adapter shape change | ~2k | Pending |
| P4 | R4 entrypoint writes terminal_ret_packet.json | `agentic_core/.../integrated_r4_deterministic_pipeline_run.py` | Don't break R5 terminal path | ~2k | Pending |
| P5 | R4 entrypoint writes exit_review_packet, x3_disposition, exhaust, trace_snapshot | same | Schema fields per existing canonical contracts | ~2k | Pending |
| P6 | Verification re-run | none (verify only) | None | ~1k | Pending |

## Files In Scope

- `apps_rg/__main__.py`
- `apps_rg/scripts/generate_resume.py`
- `apps_rg/l2_recipe/steps.py`
- `agentic_core/runtime/l2_recipe_resolver.py`
- `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py`

## ADG_HOTSPOT_REPORT

| Node | Layer | Fan-In | Archetype | Surface | Impact |
|---|---|---|---|---|---|
| `_composite_l2_callable` | L_RUNTIME | 1 (R4 entrypoint) | ORCHESTRATOR | Execution | Medium |
| `GenerateResumeStep` | L_APP | 1 (recipe registry) | ORCHESTRATOR | Execution | Medium |
| `run_integrated_r4_deterministic_pipeline` | L_RUNTIME | 1 (apps_rg `__main__`) | CENTRAL_DEPENDENCY | Execution+Observability | High |
| `generate_resume.main` | L_APP | 1 (L2 step) | ORCHESTRATOR | Execution | Medium |

## ADG_GRAPH_LAYER_EVIDENCE

(Skipped — single-app fix, scope is narrow; ADG MCP not strictly required per constitutional §22 narrow-scope exception.)

## Success Criteria

1. ✅ Single dir per run (no split)
2. ✅ HowTrace `success: true`
3. ✅ Zero blocking gaps in HowTrace
4. ✅ All 5 spine receipts present: `terminal_ret_packet.json`, `exit_review_packet.json`, `x3_disposition_receipt.json`, `runtime_exhaust_bundle.json`, `runtime_trace_snapshot.json`
5. ✅ `Amit_Ayer_Resume.docx` still produced

## Bypass Declarations

- `PLAN_REGISTRATION_BYPASS=1` — in-session bug fix; Notion Plans DB registration deferred (constitutional §36)
- `NOTION_WAVE_DEFERRAL_BYPASS=1` — N/A; no Notion calls planned
