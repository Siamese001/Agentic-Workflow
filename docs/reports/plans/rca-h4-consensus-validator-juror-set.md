# RCA — H4: `consensus_validator.py` Has Its Own Juror Set + Threshold

**Plan reference:** `.windsurf/plans/routing-followups-7a2c91.md` (Phase F3.3)
**Parent gap:** `.windsurf/plans/routing-unification-qwen-abe735.md` §6 H4
**Status:** RCA only — parent plan §9 NON-GOAL; code change requires dedicated plan
**Date:** 2026-04-21

---

## 1. Observed State

File: `@c:\Git\Agentic-Workflow\agentic_core\L1_cognition\enforcement\consensus_validator.py`

Two hardcoded values parallel to routing SSOT:

| Symbol | Line | Value |
|---|---|---|
| `MAJORITY_THRESHOLD` | 188 | `0.66` |
| Default `providers` list | 213 | `[OPENAI_MODEL_ID, ANTHROPIC_MODEL_ID, GEMINI_PRO_MODEL_ID]` |

Class: `ConsensusEngine` (used across L1 cognitive safety checks). Method `_call_juror(model_name, Artifact, prompt)` dispatches per-provider calls independently of `HealingRouter`.

## 2. Violation of Routing SSOT

- **Routing SSOT (Wave 1):** all model IDs flow from `@c:\Git\Agentic-Workflow\agentic_core\L0_routing\config\model_registry.py`. `consensus_validator.py` imports these model IDs correctly (✅ per code read — uses `OPENAI_MODEL_ID` etc., not hardcoded strings).
- **Routing dispatch SSOT (Wave 2):** all model-dispatch decisions should flow through `HealingRouter`. `consensus_validator.py` maintains its own dispatch loop bypassing the router.
- **Confidence-threshold SSOT:** `path_constants.HEALING_CONFIDENCE_X/Y` (the W1 SSOT) are separate from `MAJORITY_THRESHOLD = 0.66` because they answer different questions:
  - `HEALING_CONFIDENCE_*` = confidence-based tier selection
  - `MAJORITY_THRESHOLD` = consensus threshold for juror voting

The **0.66** value is not arbitrary — it's 2-of-3 majority for a 3-juror set. It is internally consistent for consensus voting but still represents a **duplicate confidence-threshold surface** per parent §6 H4.

## 3. Why This Is a Parent Plan NON-GOAL

Parent plan `.windsurf/plans/routing-unification-qwen-abe735.md` §9 Non-Goals explicitly states:

> Not touching `consensus_validator.py` (H4) or `system_learning/confidence/engine.py` (H5)

Reason: consensus voting and healing routing are semantically distinct concerns. Unifying them prematurely risks conflating:
- Tier selection (router) — based on confidence that a heal will succeed
- Consensus validation (validator) — based on multi-model agreement on artifact safety

A naive merge ("use HealingRouter for jurors too") would couple heal-routing decisions to safety-check decisions, violating SoC.

## 4. Recommended Fix (dedicated plan required)

A **consensus-unification plan** separate from routing-unification would:

1. **Surface duplicate threshold concern as an ADR** — explicitly document why `MAJORITY_THRESHOLD` stays at L1 cognition while `HEALING_CONFIDENCE_*` stays at L0 routing
2. **Audit juror set** — 3 providers is hardcoded; evaluate whether this is a routing decision (use W5 Flash/Pro split) or a governance decision (static)
3. **Determine OTEL schema alignment** — consensus votes should emit `consensus.v1.vote` spans, independently of `heal_router.v1` from F2
4. **Consider elevation of `MAJORITY_THRESHOLD` to `path_constants`** — if any other code path duplicates 0.66, move to SSOT

Estimated size: 12k tokens. Separate parent plan required per §9.

## 5. Next Action

**Do not execute** without explicit authorization to waive parent plan §9 non-goal. When a consensus-unification initiative is scheduled, open a dedicated plan and link this RCA from §1.

## 6. Provenance

ADG Provenance: backend=sqlite (grep match lines 188, 213 of source file; no fan-in query needed for RCA)
Constitutional compliance: §9 respected — no code changes proposed in this plan; parent plan non-goal preserved.
