# Descoped Items Tracker — Five-Tier Governance Refactor

Items removed or descoped from `five-tier-governance-model-a3f7c2.md` during the clean separation rewrite. Preserved here to avoid scope loss.

---

## Items Moved Between Waves (Not Lost)

| Item | From | To | Rationale |
|------|------|----|-----------|
| ADG blast radius (PP-17) | Wave 2 (Phase 2.9) | Wave 3 (Phase 3.2) | Belongs in structural truth layer, not policy layer |
| Pre-commit slim-down | Wave 3 (Phase 3.2) | Wave 4 (Phase 4.1) | Pre-commit is Tier 4 local ratchet, not Tier 3 structural |
| ADG evidence gate | Wave 3 (Phase 3.3) | Wave 4 (Phase 4.1) merged | Consumed into pre-commit slim-down as evidence check |

## Items Genuinely Descoped

| Item | Original Phase | Reason | Risk | Recovery Path |
|------|---------------|--------|------|---------------|
| MCP registry as YAML (`config/mcp_registry.yaml`) | Phase 2.4 | Replaced by Markdown doc (`docs/reference/MCP_Registry.md`) — simpler, no parsing | LOW | Could recreate YAML if machine-readable format needed |
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
2. **ADG stripped of governance semantics**: No approval/deny/HITL in ADG. It produces structural evidence only.
3. **Refactor Accelerator is separate from ADG**: RA consumes ADG outputs but lives in `tools/refactor_accelerator/`, not in ADG core.
4. **Tier 2 owns ALL policy**: Approval classes, exception handling policy, risk categories — all in Tier 2 rules/docs.
5. **Tier 5 = sole promotion authority**: Explicit, measurable criteria. No other tier can promote code.
