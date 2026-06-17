# ADR (design addendum W2): Reasoning execution control plane

**Status:** Accepted (implementation W3)  
**Related plan:** `.claude/plans/reasoning-execution-control-plane-f4e9a2.md`  
**Audit:** `docs/reports/reasoning_execution_audit.md`

## Problem

Receipt states (`APPLIED` / `DEGRADED` / `UNSUPPORTED` / `IGNORED`) record what happened, but **do not alone encode governance**. **Requirement level** decides **consequence**.

## ReasoningControlRequirement (authoritative fields)

Each requested control is described by:

| Field | Meaning |
|-------|---------|
| `control_name` | Stable string (`temperature`, `cot_paths`, …) |
| `requested` | Whether this control is active for this attempt |
| `requirement_level` | `OPTIONAL` \| `REQUIRED` \| `POLICY_REQUIRED` \| `QUALITY_REQUIRED` |
| `allowed_surfaces` | Non-empty subset of `TRANSPORT` \| `PROMPT` \| `ORCHESTRATION` \| `POLICY` |
| `fallback_allowed` | If true, resolver may narrow without hard failure where policy allows |
| `downgrade_disposition` | `WARN` \| `REVIEW` \| `BLOCK` when requirement not met |
| `decisive_reason_when_not_applied` | Human/machine readable reason template when not `APPLIED` |

## Receipt states (per control)

- **APPLIED** — Runtime behavior matches intent on an allowed surface **with proof** (transport observed payload ref, prompt/BOM ref, or orchestration loop counter > 0 as applicable).
- **DEGRADED** — Partial application (e.g. temperature clamped) with proof of actual.
- **UNSUPPORTED** — Provider/transport cannot apply on any allowed surface for this attempt.
- **IGNORED** — Declared but **not executed** (or stripped before wire); **must not** be labeled `APPLIED`.

## Consequence rules (deterministic)

| Situation | Outcome |
|-----------|---------|
| `OPTIONAL` + `UNSUPPORTED` | Aggregate may `WARN` only |
| `REQUIRED` + `UNSUPPORTED` \| `IGNORED` | `REVIEW` or `BLOCK` per `downgrade_disposition` |
| `POLICY_REQUIRED` + `UNSUPPORTED` \| `IGNORED` | **`BLOCK`** (hard governance) |
| `QUALITY_REQUIRED` + `UNSUPPORTED` \| `IGNORED` | **Quality certification denied** — X1D cannot claim full reasoning certification (`reasoning_quality_certification_allowed` is false) |
| Provider stripped control | Record `IGNORED` or `UNSUPPORTED`, **never** `APPLIED` |
| Orchestration control, no loop/sample/branch execution | `IGNORED` + decisive reason |
| Prompt-only control | Proof = prompt/BOM/slot digest reference |
| Transport control | Proof = observed outbound subset (dict); scratchpad **must not** appear |

## Authority boundaries

- **L2** compiles **already-authorized** intent into a plan + receipt; **does not widen** authority.
- **Resolver** may only **narrow or degrade**; never upgrade requirement level.
- **No `apps_*` literals** in generic modules under `agentic_core/runtime/reasoning/`.
- **No direct L4 writes.**

## Wire target (W3)

First integration: `SovereignLLMGateway.generate_with_reasoning` attaches `ReasoningExecutionReceipt` (serialized) on the response under `_reasoning_execution_receipt` and raises `ReasoningGovernanceError` on `POLICY_REQUIRED` violations / `BLOCK`.

## Exit integration (W4)

When the L2 / N1 normalization path embeds the same primitive under `exec_trace.reasoning_execution_receipt`, **`eval_x1d`** downgrades a **`PASS` to `WARN`** with **`REASONING_QUALITY_NOT_CERTIFIABLE`** if `quality_certification_denied` is true (helper: `reasoning_quality_certification_allowed`). Malformed embeds are ignored (backward compatible).

## Future

- Mirror receipt into `SealedL2Artifact` / N5 packet builders when the governed path seals `exec_trace`.
- App-local adapter if `apps_rg` remains off-gateway (does **not** move app literals into core).
