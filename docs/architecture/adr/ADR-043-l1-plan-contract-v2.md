# ADR-043 — L1 Plan Contract v2 (best-practice-aligned planner output)

- **Status**: Accepted (implemented)
- **Decision Date**: 2026-04-23
- **Deciders**: Agentic-Workflow Core (L1 Cognition owners)
- **Impact Layers**: L1 (primary), L0 (consumer), L3 (replan path), L5 (policy envelope)
- **Supersedes**: partial of `L1PlanContract` v1 at `agentic_core/L1_cognition/types/plan_contract_types.py`
- **Related**: `ADR-023-runtime-hitl-exit-control.md` (orthogonal — runtime exit control, not planner output), `ADR-038-budget-envelope.md`, `ADR-039-output-contract-validator.md`
- **Plan**: `.codex/plans/l1-reasoning-bestpractices-gaps-a7b2c9.md`

Current-state note (2026-06-15): implemented by `agentic_core/L1_cognition/types/plan_contract_types.py` (`L1PlanContractV2`) and `agentic_core/L1_cognition/enforcement/plan_semantic_validators.py`, with focused L1 plan contract tests.
- **Source doc**: `docs/reference/_notes/agentic_process_mapping_v34.md` §2

---

## Context

A gap audit of `agentic_process_mapping_v33.md` §2 ("L1 Reasoning + Plan Generation") against published best practices from Anthropic (*Building Effective Agents*, *Claude's Constitution*), OpenAI (*Reasoning Best Practices*, *GPT-5 prompting guide*), and Google (*ADK Planners & Thinking*, *Multi-agent patterns*) surfaced 17 doctrinal gaps and 15 repo gaps. The v33 doctrine was rewritten in the same wave to close the doctrinal gaps. This ADR ratifies the **code-side contract change** that the revised doctrine now requires of L1's output handoff.

### v1 contract (current)

`L1PlanContract` carries 7 fields: `plan_id`, `request_id`, `policy_hash`, `reasoning_mode`, `grounding_required`, `confidence_score`, `steps` (untyped tuple).

### What the doctrine now requires

§2 of v33 specifies **10 published fields** (plus implicit `plan_id` / `request_id` / `policy_hash` plumbing). The in-code contract falls short on:

1. No `proposed_route` — L0 cannot validate route intent before dispatch.
2. No `query_spec` / `task_spec` — C0 retrieval and L2 execution receive untyped step dicts.
3. No `route_risk` — exit gate cannot band risk without re-deriving it.
4. No `declared_assumptions` / `unresolved_gaps` — fact-grading invariant (constitutional §20) cannot be enforced at the contract boundary.
5. No `published_rationale` — no boundary between private L1 scratchpad and what L0/L3 consume.
6. No `planner_telemetry` — planner overhead cannot be measured (Google ADK BP-G5).
7. `steps` is a generic `tuple` — `ExpectedGroundTruth` per step (BP-A4) has nowhere to live.

## Decision

**Promote `L1PlanContract` to v2** with the following shape:

```text
L1PlanContract (v2)
    plan_id                : str
    request_id             : str
    policy_hash            : str
    proposed_route         : Enum{R1A, R1B, R3, R4, R5, CLARIFY}
    reasoning_mode         : Enum{DIRECT, CHAIN_OF_THOUGHT, REACT, DECOMPOSED}
    query_spec             : QuerySpec | None            # required when grounding_required=True
    task_spec              : tuple[PlanStep, ...]        # typed, non-empty
    route_risk             : RouteRisk                   # cost/latency/safety/reversibility
    confidence_score       : float ∈ [0.0, 1.0]
    grounding_required     : bool
    declared_assumptions   : tuple[Assumption, ...]      # each fact-graded
    unresolved_gaps        : tuple[str, ...]
    published_rationale    : str                         # sanitized, scratchpad-redacted
    planner_telemetry      : PlannerTelemetry            # refinements, clock, tokens, critic_iter

PlanStep
    step_id                : str
    description            : str
    expected_ground_truth  : ExpectedGroundTruth         # signal this step should produce

Assumption
    statement              : str
    grade                  : Enum{DIRECTLY_OBSERVED, DERIVED, UNRESOLVED}

RouteRisk
    cost_band              : Enum{LOW, MED, HIGH}
    latency_band           : Enum{LOW, MED, HIGH}
    safety_band            : Enum{LOW, MED, HIGH}
    reversibility          : Enum{READ, ACTION, WRITE}

PlannerTelemetry
    refinements_used       : int
    wall_clock_ms          : int
    token_usage            : int
    critic_iterations      : int
```

### Redaction boundary

The `private_scratchpad` field **must NOT exist** on the published contract. It lives in the L1 engine (`reasoning_plan.ReasoningPlan`) but is stripped by the `ReasoningPlan → L1PlanContract` adapter. Only `published_rationale` crosses to L0.

### Replan semantics

A replan from `[5] EXIT EVAL` produces a **successor** `L1PlanContract` with a new `plan_id` and a `replan_parent_id` pointer (out-of-band header, not a contract field) so L0 can correlate. Replan count is bounded by `budget_enforcer`; exceeding the cap forces a `BEST_EFFORT` or `ABSTAIN` exit (see v33 §2 T3 exit branches).

### Migration

- v1 contract stays importable for **one deprecation cycle** (90 days) via a shim. Callers continue receiving the 7-field shape until they opt in.
- `agentic_core/L1_cognition/types/plan_contract_types.py` adds v2 as `L1PlanContractV2` (frozen dataclass). `L1PlanContract` becomes an alias to v2 after the deprecation window closes.
- A CI gate (`ops_scripts/ci/check_l1_plan_contract_fields.py`) fails closed if v2 required fields are missing in any code path that emits a plan.

## Consequences

### Positive

- L0 validation becomes schema-driven rather than "check whether these 7 fields happen to be present".
- Exit gate ([5]) can band risk and calibrate HITL threshold off `route_risk` + `confidence_score` without re-deriving.
- Thought redaction becomes structural, not a code convention — `published_rationale` is the only human-readable rationale that escapes L1.
- Planner overhead is measurable from day one (GA day is telemetry day).
- Fact grading at the contract boundary composes with constitutional §20.

### Negative / costs

- Schema migration cost for existing callers (reasoning_chokepoint, L0 router, test fixtures).
- 90-day deprecation window increases cognitive load on reviewers during migration.
- `PlanStep.expected_ground_truth` forces planners to actually declare what signal each step will produce — this is more work at plan time, and that is the point.

### Risks

- **R1**: Down-stream consumers read v1 fields by attribute access; shim must preserve attribute paths. *Mitigation*: shim exposes v1 attributes as properties on v2.
- **R2**: `published_rationale` redaction could leak scratchpad if adapter is buggy. *Mitigation*: adapter test suite includes a "scratchpad tokens must not appear" assertion with a known canary string.
- **R3**: Replan loops could still run away if `budget_enforcer` caps are wrong. *Mitigation*: hard cap in contract validator (`replan_depth <= 3`), not just in enforcer.

## Rollout

- **Wave 2** of plan `l1-reasoning-bestpractices-gaps-a7b2c9`: land v2 contract + adapter + shim + CI gate. **Author-Gate required** (schema change).
- **Wave 3**: wire evaluator-optimizer, clarify, replan primitives against v2.
- **Wave 4**: budget, overhead emitter, redaction, dev/sys-msg split.
- **Wave 5**: raise coverage to ≥90% on `plan_contract_types.py`, `reasoning_chokepoint.py`, `plan_creator.py`; SVP Engineering review.

## Rejection criteria (would void this ADR)

- If Author-Gate at W2 rejects the schema change, this ADR becomes Superseded with a record of why.
- If the 90-day shim proves insufficient for external callers, extend (don't skip) deprecation.
- If planner telemetry shows planner-on vs planner-off has no measurable quality lift on DIRECT/R1A routes, the plan-skip triage (v33 §2) stays and planner is bypassed for those routes — not a contract change, a routing policy.

## References

- `docs/reference/_notes/agentic_process_mapping_v34.md` §2 (revised)
- Anthropic — *Building Effective Agents* — evaluator-optimizer, workflow vs agent, stopping conditions
- Anthropic — *Claude's Constitution* — clarify in ambiguity, abstain as first-class
- OpenAI — *Reasoning Best Practices* — planner/doer split, simple prompts, developer vs system message
- OpenAI — *GPT-5 prompting guide* — plan extensively before tool calls, reflect extensively after
- Google — *ADK Planners & Thinking* — BuiltInPlanner vs PlanReActPlanner, `include_thoughts`, overhead measurement, graceful fallback, replanning
- Google — *ADK Multi-agent patterns* — structured state handoff between agents
