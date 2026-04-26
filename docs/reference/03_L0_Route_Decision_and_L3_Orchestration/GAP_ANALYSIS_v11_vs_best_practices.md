========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 03_L0_Route_Decision_and_L3_Orchestration
Canonical file: GAP_ANALYSIS_v11_vs_best_practices.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: GAP_ANALYSIS_v11_vs_best_practices.md
Owner summary: L0 routing plus optional L3 orchestration. L0 emits exactly one deterministic RouteContract; L3 expands managed workflows only when execution_form requires it.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

# L0 Routing — Gap Analysis: v11 vs OpenAI / Anthropic / Google / Production Best Practices

**Date:** 2026-04-24
**Baseline:** `03_L0_Route_Decision_Switching_L3 v11.md`, `R1B Semantic Cache.md`, `C0 - Retrieval/*`
**Target:** `03_L0_Route_Decision_Switching_L3 v12.md` (remediated)
**Method:** Direct read of vendor docs + production-practice literature (see §Sources).

---

## 1. Executive Summary

v11 is strong on the **dispatcher contract** (route as a deterministic emission, not the work itself),
on **multi-tier cache layering** (R1B prose), and on **forward-only L3 orchestration**. It is weak
on five vectors where public best practice has converged since early 2025:

1. **Model-tier cascading** (cheap-first, escalate-on-low-confidence) is entirely absent.
2. **Route telemetry and calibration** are implied but not schematized.
3. **Named workflow patterns** beyond dispatcher/workflow (parallelization, evaluator-optimizer,
   HITL) are missing as first-class routes.
4. **Resilience** (multi-provider fallback, cold-start handling, loop detection, SLO budgets) is
   under-specified — R5 "abstain" is the only explicit recovery path.
5. **Principle prose** ("start with one agent", "handoff vs agent-as-tool", "hallucination
   amplification risk") is not stated, so practitioners reading v11 in isolation re-derive or
   mis-apply these invariants.

None of these are structural defects in v11 — the dispatcher model holds — but each is a concrete
gap against the current public state of the art.

---

## 2. Gap Register

| # | Gap | Severity | Primary Source | Remediated In |
|---|-----|----------|----------------|---------------|
| G1  | No model-tier cascade (Haiku→Sonnet→Opus, cost-capability routing) inside executor routes | HIGH   | Anthropic "Building Effective Agents", Tian Pan 2025 | v12 §R-CASC + §Route Contract `cost_tier` |
| G2  | No confidence-based cascade (cheap model first, escalate on low confidence) | HIGH   | Tian Pan 2025, Redis LLMOps 2026 | v12 §R-CASC §CONFIDENCE-ESCALATION |
| G3  | No parallelization route (sectioning / voting / guardrail fan-out) as first-class option | MEDIUM | Anthropic, Google ADK Parallel Fan-Out | v12 §R-PAR |
| G4  | No evaluator-optimizer / generator-critic loop route for qualitative refinement | MEDIUM | Anthropic "Evaluator-optimizer", Google ADK LoopAgent | v12 §R-LOOP |
| G5  | HITL is buried in Exit Control; no explicit route for high-stakes / irreversible actions | MEDIUM | Google ADK HITL pattern, ADR-023 | v12 §R-HITL |
| G6  | No multi-provider fallback chain; R5 is terminal abstain only | MEDIUM | Tian Pan "Single provider dependency" pitfall | v12 §Fallback Chain |
| G7  | Route-decision telemetry schema undefined (features used, classifier confidence, downstream quality) | HIGH   | Arthur.ai guardrails, Tian Pan "observability pitfall" | v12 §Route Telemetry Contract |
| G8  | Confidence-threshold calibration discipline not specified; thresholds implied by intuition | HIGH   | Tian Pan "empirically calibrated thresholds are non-negotiable" | v12 §Calibration Discipline |
| G9  | Cold-start / new-intent-type safeguard missing; classifier low-confidence has no conservative default | MEDIUM | Tian Pan "routing cold starts" | v12 §Cold-Start Safeguard |
| G10 | Loop / no-progress detection missing (agent-efficiency signal on repeated nodes) | MEDIUM | Galileo "Debug AI Agents" | v12 §Loop Guard |
| G11 | Handoff vs agent-as-tool distinction not made; R3/R4 conflates ownership transfer with manager-calls-helper | LOW    | OpenAI Agents SDK "Orchestration and handoffs" | v12 §Handoff vs Agent-as-Tool |
| G12 | "Start with one agent, split when contract changes" principle not stated | LOW    | OpenAI Agents SDK, Anthropic | v12 §Single-Agent-First Principle |
| G13 | Semantic cache hallucination-amplification risk not surfaced at top level (buried in R1B) | LOW    | Tian Pan, existing `R1B Semantic Cache.md` | v12 §R1B callout |
| G14 | No normative Route Contract schema (fields, versioning, HMAC, cost_tier, fallback_chain) | HIGH   | Synthesis across all sources | v12 §Route Contract Schema |
| G15 | No route-level SLO / budget enforcement (latency budget, token budget, cost cap per route) | MEDIUM | Tian Pan "cascade latency accumulation" | v12 §Route SLO & Budget |

Severity legend: HIGH = doctrine-level, must remediate now; MEDIUM = practice-level; LOW = clarity.

---

## 3. What v11 Already Gets Right (do not regress)

Preserved verbatim in v12:

- **Dispatcher-not-executor**: "L0 decides the path, but it does not itself do retrieval, think deeply, or perform the work." This is the core invariant; vendor patterns (OpenAI triage agent, Google CoordinatorAgent) agree.
- **Route contract emission** (selected route, confidence, reason codes, freshness class, cache policy, execution form): aligns with OpenAI "delegated ownership" and Anthropic "tailored, well-documented interfaces."
- **R1A exact cache → R1B semantic cache → C0 grounded read** layering: matches Tian Pan recommended implementation order (semantic cache first, then intent routing).
- **R1B hybrid fusion + policy gates**: already addresses Tian Pan's "hallucination amplification" concern; only gap is that this is not called out at the top-level v11.
- **Forward-only L3 with no backward edges**: preempts loop bugs at the orchestration layer.
- **L4 read-only from L0 perspective**: matches Anthropic "managed agents" virtualization.
- **Fail-fast ingress** (tenant/ACL/region/expiry): matches Arthur.ai guardrail-first pattern.

---

## 4. Source Matrix

| Source | Key Contribution | Pulled In As |
|---|---|---|
| Anthropic, "Building Effective Agents" (resources.anthropic.com) | Workflow taxonomy: prompt-chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer | G3, G4, G12 |
| Anthropic, "Effective harnesses for long-running agents" | Context-management discipline across windows (applies to L3 more than L0 but reinforces route-contract discipline) | G14 |
| Anthropic, "Scaling Managed Agents" | Session / harness / sandbox virtualization | Confirms L0 = harness routing layer |
| OpenAI Agents SDK, "Orchestration and handoffs" | Handoff (ownership transfer) vs `agent.asTool()` (manager-calls-helper); "add specialists only when the contract changes" | G11, G12 |
| OpenAI Cookbook, "Orchestrating Agents: Routines and Handoffs" | Routines as state machines; dynamic swap of instructions+tools | Confirms route-contract-as-state |
| Google ADK, "Developer's guide to multi-agent patterns" | Named patterns: Sequential, Coordinator/Dispatcher, Parallel Fan-Out/Gather, Hierarchical decomposition, Generator+Critic, Iterative refinement (LoopAgent), HITL | G3, G4, G5 |
| Tian Pan, "LLM Routing and Model Cascades" (Nov 2025) | Routing vs cascading distinction; confidence calibration; semantic-cache invalidation; layered-architecture order; production pitfalls | G1, G2, G6, G7, G8, G9, G15 |
| Redis, "LLMOps Guide 2026" | Semantic classification before routing; rate-limit + budget caps | G15 |
| Arthur.ai, "Best Practices for Building Agents | Part 5 - Guardrails" | Guardrails as telemetry events; failure-rate monitoring | G7 |
| Galileo, "How to Debug AI Agents: 10 Failure Modes" | Loop detection, Agent Efficiency score, repeated-span grouping | G10 |
| Introl, "Prompt Caching Infrastructure 2025" | Provider-side prefix caching (90% cost reduction, 85% latency reduction) | Reinforces existing R1B Tier 1 prose |

---

## 5. Wave Plan (implementation)

| Wave | Gaps | Deliverables |
|------|------|--------------|
| **W1** HIGH-severity schema work | G14, G7, G1, G8 | v12 §Route Contract Schema, §Route Telemetry Contract, §Cost-Tier Cascade, §Calibration Discipline |
| **W2** New first-class routes | G3, G4, G5, G2 | v12 §R-PAR (parallelization), §R-LOOP (evaluator-optimizer), §R-HITL, §R-CASC (confidence escalation) |
| **W3** Resilience & observability | G6, G9, G10, G15 | v12 §Fallback Chain, §Cold-Start Safeguard, §Loop Guard, §Route SLO & Budget |
| **W4** Principles & clarity | G11, G12, G13 | v12 §Single-Agent-First Principle, §Handoff vs Agent-as-Tool, §R1B top-level callout |

All four waves ship together in a single new file `03_L0_Route_Decision_Switching_L3 v12.md` to avoid
mid-doctrine drift. v11 is retained unchanged as historical reference.

---

## 6. Non-Goals (explicitly out of scope)

- **Code changes to `agentic_core/L0_routing/`** — v11 and v12 are reference/doctrinal artifacts;
  the code layer's alignment to v12 is a separate plan (track as DEFERRED_SCOPE in the wave/phase DB).
- **Retiring v11** — preserved for provenance; v12 header links back.
- **New C0 retrieval doctrine** — gaps inside C0 sub-folder are a separate review.
- **Runtime HITL wiring (ADR-023)** — v12 R-HITL route merely names the exit; the runtime exit-control
  contract is owned by `agentic_core/L5_safety/` per ADR-023.
