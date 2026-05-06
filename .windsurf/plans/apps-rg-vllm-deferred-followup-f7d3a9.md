# Deferred Scope — apps_rg Interactive Wizard + vLLM/Synthesis Cascade Followups

**Slug**: `apps-rg-vllm-deferred-followup-f7d3a9`
**Status**: Not Started
**Tier**: T2 (cross-cutting: code + behavioral rule + ops)
**Parent context**: Session 2026-05-06 — surfaced while shipping `apps-rg-interactive-wizard-a3e7c1` (Completed) and the apps_research synthesis cascade hardening (commit `c4970b6ddb`).

## Goal

Track and bound the deferred-scope items surfaced during the 2026-05-06 session covering apps_rg interactive wizard rollout and the apps_research Qwen→Gemini cascade. None of these are blocking; each represents a follow-on opportunity. **Do NOT implement** — this plan is for capture only.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| W1 | P1.1 | Sibling-app interactive wizards (apps_underwriting_ai, apps_qna, apps_rfp, apps_research, apps_lic, apps_exec) | ~2400 (6 apps × ~400) | Not Started | Each app has TTY-only wizard prompting for app-specific mandatory inputs; cross-company / cross-target contamination guards extended; rule scope updated |
| W2 | P2.1 | Stale `apps_rg/scripts/` cleanup | ~150 | Not Started | 60+ stale `generated_resume_*.json` archived or deleted; Blend360 `company_research.json` removed; `job_description.json` stub replaced or removed |
| W3 | P3.1 | Qwen Docker auto-restart-on-reboot policy | ~200 | Not Started | `docker run` `--restart unless-stopped` applied to `local-qwen-vllm`; verified survives Windows host reboot; topology doc updated |
| W4 | P4.1 | apps_research synthesis cascade — add OpenAI/Anthropic tiers | ~800 | Not Started | `_openai_synthesize` and `_anthropic_synthesize` follow same shape as `_qwen_synthesize` / `_gemini_synthesize`; cascade order Qwen→Gemini-Pro→Gemini-Flash→OpenAI→Anthropic→stub; env-driven model selection |
| W5 | P5.1 | Retire `archives/wsl2_vllm_legacy_2026-05-06/` (or formalize as audit reference) | ~80 | Not Started | Either delete the gitignored archive entirely OR commit it as a formal historical reference under `docs/architecture/historical/` |
| W6 | P6.1 | Always-on rule promotion for `apps-rg-interactive-discipline.md` (after sibling apps land) | ~150 | Not Started — BLOCKED on W1 | §33 token-budget gate passes after content trim; trigger flips `model_decision` → `always_on`; sibling apps explicitly listed in rule body |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Sibling app wizards | 6 × `apps_*/__main__.py` + 6 × test files | Each app has different "mandatory inputs" — apps_underwriting_ai needs different inputs than apps_qna; design needs canonical helper module to avoid 6× duplication | ~2400 | Not Started |
| P2.1 | apps_rg/scripts cleanup | ~62 stale JSON artifacts | Distinguish historically-valuable evidence (preserve) vs noise (delete); archive folder vs delete decision | ~150 | Not Started |
| P3.1 | Qwen restart policy | `docker inspect` config + topology doc | `--restart unless-stopped` requires docker stop/rm/run cycle; preserve env vars + GPU mapping | ~200 | Not Started |
| P4.1 | LLM cascade extension | `apps_research/engines/company_brief_engine.py` + `.env.example` | Two new SDKs (openai, anthropic); shared cascade-iteration helper to reduce duplication; env vars `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_MODEL`, `ANTHROPIC_MODEL` | ~800 | Not Started |
| P5.1 | WSL2 archive disposition | `archives/wsl2_vllm_legacy_2026-05-06/` | Gitignored — either retire entirely or formalize; user choice | ~80 | Not Started |
| P6.1 | Rule always-on flip | `.windsurf/rules/apps-rg-interactive-discipline.md` frontmatter | Requires §33 budget headroom; W1 must land first to make rule worth always-on cost | ~150 | Not Started |

## Files In Scope

**Code (W1)**:
- `apps_underwriting_ai/__main__.py`, `apps_qna/__main__.py`, `apps_rfp/__main__.py`, `apps_research/__main__.py`, `apps_lic/__main__.py`, `apps_exec/__main__.py`
- `apps_shared/cli/interactive_wizard.py` (new — canonical helper to avoid 6× duplication)

**Code (W2)**:
- `apps_rg/scripts/*.json` (audit + selective deletion)

**Code (W3)**:
- Docker config (no repo file change beyond `docs/architecture/qwen-vllm-topology.md`)

**Code (W4)**:
- `apps_research/engines/company_brief_engine.py`
- `.env.example`
- New: `apps_research/engines/_openai_synthesize.py`, `apps_research/engines/_anthropic_synthesize.py` (or inline)

**Code (W5)**:
- `archives/wsl2_vllm_legacy_2026-05-06/` (delete or move to `docs/architecture/historical/`)

**Code (W6)**:
- `.windsurf/rules/apps-rg-interactive-discipline.md` (frontmatter only)

**Tests (W1)**:
- `tests/_apps_contract/test_apps_*_interactive_wizard.py` (one per app)

## Non-Goals

- Hook-based enforcement of the wizard discipline (rejected during initial design as too heuristic for single-app concerns; revisit only if sibling apps reveal pattern)
- Auto-detection of "user explicitly authorized" vs "Cascade inferred" (NLP-hard; not a viable enforcement layer)
- Real LLM-judge implementations for the apps_eval-harness backlog (separate plan: see memory `5ba9ca42` — STILL DEFERRED list)
- C0 FEC producer wiring for grounded apps (separate plan, blocker #4 in apps_eval-harness audit)
- apps_underwriting_ai analyst attestation flip from `PROVENANCE_PENDING` → `VERIFIED_ANALYST_ATTESTED` (separate plan: requires qualified-owner sign-off; not Cascade work)

## Success Criteria

- ✅ Each wave has a Notion row registered with Status, AI Summary, Plan File Path
- ✅ When implementation begins, plan-registration enforcement (§36) does not fire
- ✅ Hotspot ranking shows none of these touch L0/L5 critical layers (so no §22 ADG_GRAPH_LAYER_EVIDENCE blocker)
- ✅ Each wave is independently deployable (no cross-wave blocking dependencies except W6 → W1)

## ADG Graph Layer Evidence

Not required at this scope — capture-only plan. When any wave is activated, the activator's plan MUST add the `## ADG_GRAPH_LAYER_EVIDENCE` section per constitutional §22.

## Pattern Source

Same shape as `apps-rg-interactive-wizard-a3e7c1` (the parent plan). Same shape as `plan-location.md`, `ssot-folder-enforcement.md`, `mcp-serialization.md` (helper logic + conditional rule + durable test surface).

## Constitutional Cross-Reference

- §6 (Author-Gate for ambiguous decisions — sibling apps will face same wizard need)
- §18 (no hidden scope expansion — these are explicitly listed as deferred, not "while I'm here" creep)
- §22 (ADG_GRAPH_LAYER_EVIDENCE required when any wave activates)
- §24 (deferred-scope capture — this plan IS the capture artifact)
- §33 (W6 gated on always-on token budget)
- §36 (plan must be registered in Notion before wave starts)

## Notion Registration

- Database: Plans DB (`6aba34d9-4d0b-4f4c-b956-b2bdea541ca9`)
- Status: `Not Started` (option id `503df59f-85d4-4ac0-baae-e457d0354b6f`, gray)
- AI Summary: bullet-style per `notion-plans-taxonomy.md` invariant
- Exists On Disk: true
- Plan File Path: `.windsurf/plans/apps-rg-vllm-deferred-followup-f7d3a9.md`
