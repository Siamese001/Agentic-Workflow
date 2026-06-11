---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\descoped-items-tracker.md'
original_relative_path: 'descoped-items-tracker.md'
source_sha256: ea7f419bc5bcf7c50822dbc19d3af3995f5354913a153e84eda4f19cd5836294
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-07'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Descoped Items Tracker — Five-Tier Governance Refactor

Items removed or descoped from `five-tier-governance-model-a3f7c2.md` during the clean separation rewrite. Preserved here to avoid scope loss.

---

## Items Moved Between Waves (Not Lost)

| Item | From | To | Rationale |
|------|------|----|-----------|
| ADG blast radius (PP-17) | Wave 2 (Phase 2.9) | Wave 3 (Phase 3.2) | Belongs in structural truth layer, not policy layer |
| Pre-commit slim-down | Wave 3 (Phase 3.2) | Wave 4 (Phase 4.1) | Pre-commit is Tier 4 local ratchet, not Tier 3 structural |
| ADG evidence gate | Wave 3 (Phase 3.3) | Wave 4 (Phase 4.1) merged | Consumed into pre-commit slim-down as evidence check |
| PP-6 plan format (ownership) | T1 hard gate (Phase 1.2) | T2 policy (Phase 2.9) | Plan format is policy, not platform interception. Classifier in Phase 1.4 warns only. |

## Items Redefined (Not Removed)

| Item | Original | Redefined To | Rationale |
|------|----------|-------------|-----------|
| Phase 1.4 `pre_user_prompt` | HARD GATE (exit 2) | ADVISORY CLASSIFIER (exit 0 always) | Implementation text said "exit 0 on all edge cases" — contradicted hard gate label |
| Phase 1.5 MCP drift detection | YAML→JSON drift check | JSON-native lint (schema, env vars, tool count, risky edit notice) | Once YAML archived (W2.7), drift is meaningless — replaced with JSON-native validation |
| Phase 1.2 MCP config protection | Blanket DENY (exit 2 on all `mcp_config.json` writes) | Tiered: ALLOW (schema-valid) / REQUIRE_APPROVAL (risky) / DENY (delete only) | Blanket deny contradicts JSON-as-SSOT; normal config maintenance must be possible |
| H-6 graceful degradation | Blanket fail-open (exit 0 on all errors) | Risk-based: fail-closed for critical pre-hooks, fail-open for advisory hooks | Universal fail-open weakens safety-critical gates |
| Phase 1.6 PID tracking | Assumed native PID in payload | Best-effort PID via OS process table lookup | Windsurf `post_run_command` payload has `command_line` + `cwd` only, no PID |
| Phase 1.8 session-end cleanup | "Cleanup on session end" | "Response-tail cleanup attempt" | `post_cascade_response` fires per-response, not per-session; not guaranteed session-end |

## Items Genuinely Descoped

| Item | Original Phase | Reason | Risk | Recovery Path |
|------|---------------|--------|------|---------------|
| MCP registry as YAML (`config/mcp_registry.yaml`) | Phase 2.4 | Replaced by Markdown doc (`docs/guides/MCP_Registry.md`) — simpler, no parsing | LOW | Could recreate YAML if machine-readable format needed |
| 8-point per-MCP audit checklist | Phase 2.5 | Over-engineered. Collapsed to lightweight version/deprecation check | LOW | Original checklist in git history if needed |
| YAML SSOT detailed research (4 sources) | Phase 2.7 | Research completed but detailed findings compressed. Full findings preserved in git history of Phase 2.7 | LOW | `git log --all -- five-tier-governance-model-a3f7c2.md` for full RAG findings |
| MCP config sovereignty script | Phase 2.7 | Archiving `check_mcp_config_sovereignty.py` — it prevents JSON edits, but JSON IS SSOT | LOW | Restore from `tools/archive/` if JSON SSOT changes |
| Detailed MCP config SSOT diagram | Phase 2.7 | The 3-step SSOT diagram (Step 3) compressed to single-line description | LOW | Full diagram in git history |
| Detailed exception handling vocabulary (Columns 1-5) | Phase 2.6 | Compressed from full vocabulary with examples to compact reference | LOW | Full vocabulary in `docs/reference/Python/Error & Exception Handling.md` |

## Items Added (New Scope)

| Item | Phase | Rationale |
|------|-------|-----------|
| `pre_user_prompt` hook | Wave 1 (Phase 1.4) | Scope enforcement at prompt time — catch early |
| `post_run_command` audit hook | Wave 1 (Phase 1.6) | PID tracking for zombie cleanup |
| `post_mcp_tool_use` audit hook | Wave 1 (Phase 1.7) | MCP telemetry for observability |
| ADG Scope Clarification | Wave 3 (Phase 3.1) | Explicit boundary: ADG = structural truth, no governance |
| Refactor Accelerator Design | Wave 3 (Phase 3.3) | New layer consuming ADG for change planning |
| Refactor Accelerator MVP | Wave 3 (Phase 3.4) | Ranked candidates, migration sequences, impacted tests |
| Approval & Exception Policy | Wave 2 (Phase 2.10) | Formal ALLOW/DENY/REQUIRE_APPROVAL/ESCALATE classes |
| CI Promotion Authority | Wave 4 (Phase 4.5) | Explicit measurable promotion criteria for Tier 5 |
| 15-step E2E Verification | Wave 4 (Phase 4.6) | Expanded from 11 to 15 steps covering all 5 tiers |

---

## Architectural Decisions Captured

1. **Pre-hooks = hard gates, post-hooks = advisory only**: Post-hooks NEVER block. They log, audit, and clean up.
2. **ADG stripped of governance semantics**: No approval/deny/Author-Gate in ADG. It produces structural evidence only.
3. **Refactor Accelerator is separate from ADG**: RA consumes ADG outputs but lives in `tools/refactor_accelerator/`, not in ADG core.
4. **Tier 2 owns ALL policy**: Approval classes, exception handling policy, risk categories — all in Tier 2 rules/docs.
5. **Tier 5 = sole promotion authority**: Explicit, measurable criteria. No other tier can promote code.
