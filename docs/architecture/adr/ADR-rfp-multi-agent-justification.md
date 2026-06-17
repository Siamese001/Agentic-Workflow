# ADR-NNN — apps_rfp Multi-Agent Justification

**Status**: Accepted

> **Status**: **Accepted** (2026-05-01)
> **Date**: 2026-04-29 (Proposed) → 2026-05-01 (Accepted)
> **Plan**: `.claude/plans/apps-rfp-first-principles-refactor-9c8d3f.md` (W0/W1.1 evidence) + `.claude/plans/apps-portfolio-integrated-evaluation-7d3a91.md` (W0.1 verification, W2 acceptance)
> **AgentSpec**: `apps_rfp/config/specs/agent_spec.rfp_response.v1.0.0.yaml` (declares `agency.tier=MULTI_AGENT`)
> **Reference contract**: `requirements/contracts/REQ-CROSS-APP-AGENTSPEC-001.contract.yaml`
>
> **Acceptance evidence**: W0.1 verification scan against ADG snapshot `artifacts/adg/adg_indexed_05012026_0632.sqlite` (output: `artifacts/_scan_w0_w1_output.txt`). Cross-orchestrator edge counts across the 5 RFP orchestrators: `writes_to=0`, `emits_side_effect=0`, `resolves_callsite=0`, `controls_flow=0`. The four §Verification checkboxes all pass. The `flows_to=0` caveat is documented in the integrated plan and does not invalidate the tier — it is consistent with the ADR's own Claim 3 (parallel agents whose outputs are independently consumable). Captured in Author-Gate decision K1 of the integrated plan, type=architecture_choice, confidence=0.85, precedent=strong.

## Context

The first-principles design encoded in `REQ-CROSS-APP-AGENTSPEC-001` enforces a "lowest viable agency" rule. `agency.tier=MULTI_AGENT` requires explicit justification because multi-agent topologies introduce known failure modes:

- **Consensus-seeking that hides errors**: Agents with overlapping training data converge on confident wrong answers.
- **Persona bleed across context boundaries**: Anything one agent says becomes context for the next.
- **Cost and latency explosion**: N agents × M turns multiplies invocation cost.
- **Debugging surface bloat**: When the answer is wrong, the failure path includes which agent, which turn, which influence.

The default architecture for any `apps_*` agent is `WORKFLOW` (deterministic pipeline) or `SINGLE_AGENT` (one bounded agent loop). `MULTI_AGENT` is the exception, not the default.

`apps_rfp/` ships with five reasoning surfaces today (per Phase B audit):

- `RfpOrchestrator.py`
- `section_orchestrator.py`
- `enterprise_orchestrator.py`
- `ComplianceMappingAgent.py` (acts as orchestrator over compliance classification)
- `RequirementAnalysisAgent.py` (acts as orchestrator over requirement decomposition)

The question this ADR resolves: **is the existing multi-orchestrator topology defensible as `MULTI_AGENT` under the SSOT spec, or should it collapse to `SINGLE_AGENT` / `WORKFLOW`?**

## Decision

**Adopt `agency.tier=MULTI_AGENT` for `apps_rfp`, conditional on ADG verification at W0.1.**

The defensibility rests on three claims, each verifiable from the static bucket of the ADG (no runtime needed):

### Claim 1 — Three workflows are structurally distinct

Compliance classification, requirement decomposition, and section assembly are not three names for the same thing. Each:

- Consumes a different `EvidencePacket.kind`:
  - Compliance: `policy` + `rule_set` (regulatory constraints)
  - Requirement: `domain` (RFP requirement text) + `tool_constraint` (capability inventory)
  - Section: `example` (prior responses) + `domain` (capability evidence)
- Has a different failure mode:
  - Compliance: misclassifying must-have as optional (regulatory exposure)
  - Requirement: missing implicit requirements (proposal incomplete)
  - Section: boilerplate-padding a section that doesn't apply (proposal weak)
- Has a different escalation trigger:
  - Compliance: severity ≥ blocker → halt
  - Requirement: undecomposable requirement → ask
  - Section: missing capability evidence → decline section

This is **role separation**, not three names for the same task.

### Claim 2 — Integration is via typed contracts, not shared state

The MULTI_AGENT tier is defensible only when the agents communicate through **typed contracts** with no shared mutable state. ADG W0.1 must verify:

- No `writes_to` semantic edges between the three orchestrators on shared objects
- No common mutable singleton consumed by all three (e.g., a shared "RFP context dict" that each can mutate)
- Inter-orchestrator boundaries cross via `flows_to` edges that reference structured payloads (RFP-section contracts), not free-form prose

If W0.1 finds shared mutable state, **the tier MUST drop to `SINGLE_AGENT` or `WORKFLOW`** and this ADR is rejected.

### Claim 3 — Parallelism is genuine, not decorative

Compliance, requirement, and section workflows can run **in parallel** for the same RFP. They consume the same input (the RFP document) but produce orthogonal outputs (compliance map, requirement tree, section drafts). This is the structural test for justified parallelism: parallel agents whose outputs are independently consumable, not parallel agents whose outputs need merging by a fourth agent.

`agency.parallel_tool_calls=true` reflects this. `WORKFLOW` tier cannot express parallel sub-workflows; that's a real expressivity gap.

## Consequences

### Positive

- The existing multi-orchestrator topology is preserved without forcing collapse to a less expressive tier.
- The three workflows can evolve their rubrics, tool sets, and escalation policies independently.
- Parallelism reduces wall-clock latency for large RFPs.

### Negative

- Multi-agent topology requires more rigorous testing than workflow tier.
  - Mitigation: `apps_rfp/tests/matrix/` must include adversarial cases for each of the three workflows independently AND for cross-workflow contracts.
- Higher LLM invocation cost (3 workflows × multiple turns).
  - Mitigation: `evals.min_release_thresholds` are tighter than workflow-tier defaults to compensate.
- Persona bleed risk if the three workflows share too much context.
  - Mitigation: tone_bounds are strict (`max_persona_tokens=64`); each workflow's evidence packets are typed and scoped.

### Neutral

- HITL is required for `agency_tier_promotion`. Future moves (e.g., to `MULTI_AGENT` with cross-workflow consensus) require a fresh ADR.

## Alternatives Considered

1. **`agency.tier=SINGLE_AGENT`** — Single orchestrator dispatches all three workflows internally. Rejected: collapses three distinct failure modes into one logging surface; loses parallelism; doesn't reflect the actual code topology.

2. **`agency.tier=WORKFLOW`** — Pure deterministic pipeline. Rejected: each of the three workflows internally has model-driven decisions (compliance severity classification, requirement decomposition heuristics, section boilerplate matching) that are not deterministic; forcing them to be would degrade quality.

3. **Three independent `AgentSpec` instances**, one per workflow, with a thin orchestration layer. Considered viable but defers the problem; the orchestration layer is itself an agent and would need its own spec. Net complexity is higher than declaring one MULTI_AGENT spec with the three workflows as bounded sub-agents.

## Verification (post W0.1)

This ADR moves to **Accepted** only after `apps_rfp` ADG hotspot scan W0.1 confirms:

- [ ] No shared mutable state across orchestrator boundaries
- [ ] `flows_to` edges between workflows reference structured payloads only
- [ ] Each workflow has independent escalation triggers (no shared escalation queue with shared mutable cursor)
- [ ] No `emits_side_effect` edges from one workflow into another's failure surface

If any of those fail, this ADR moves to **Rejected** and the spec's `agency.tier` is downgraded.

## References

- First-principles design conversation 2026-04-29
- `requirements/contracts/REQ-CROSS-APP-AGENTSPEC-001.contract.yaml` (SPEC-INV-001)
- `apps_rfp/config/specs/agent_spec.rfp_response.v1.0.0.yaml`
- `.claude/plans/apps-rfp-first-principles-refactor-9c8d3f.md` (W1.2)
- `docs/reports/adg/apps_rfp_hotspots_<ts>.md` (W0.1 evidence)
