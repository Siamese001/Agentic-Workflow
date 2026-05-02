# apps_underwriting_ai Activation — e8a3c5

> Closes P5.1 from the burndown plan `qwen-rollout-followup-burndown-d2a4f8`.
> Activates the LLM-bearing decision-explainability surface in
> `apps_underwriting_ai`. Compliance posture: deterministic verdict path
> remains the legally-binding mechanism; Qwen-judge enriches the
> human-readable `rationale` field only.

## Status

- **Plan**: `apps-underwriting-ai-activation-e8a3c5`
- **Created**: 2026-05-02
- **Owner**: Cascade
- **Predecessor**: `qwen-rollout-followup-burndown-d2a4f8` P5.1
- **Status**: Live

## Compliance Posture (NON-NEGOTIABLE FLOOR)

For a regulated underwriting domain, the legally-binding verdict path
MUST be deterministic. This plan does NOT delegate the verdict
(`APPROVE` / `REFER` / `INSUFFICIENT_EVIDENCE` / etc.) to the LLM. The
LLM is wired ONLY to the human-readable `rationale` field on
`DecisionPacket`. Specifically:

- `DecisionPacketAssembler.assemble()` continues to compute the verdict
  via the existing deterministic heuristic (skeleton today; richer
  actuarial logic in future).
- After verdict is decided, a Qwen-first cascade attempts to GENERATE
  a richer rationale paragraph contextualized to the evidence refs +
  feature summary + reconciliation state. Any failure (preflight, SDK,
  gateway, empty response, content-policy guard) falls through to the
  pre-existing template rationale.
- `gate_violations`, `evidence_refs`, `feature_summary`, `verdict` are
  NEVER touched by the LLM. They are deterministic outputs.
- Future hardening (W3): pair Qwen with frontier-API second-judge on
  the high-risk subset (REFER / DENY verdicts) when production traffic
  begins. Gated on Wilson-CI agreement metrics across 4-week rolling
  window — same pattern as predecessor W4 P4.4.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1–P1.3 | Decision-rationale Qwen-first wiring (LLM-bearing surface only) | ~3k | DecisionPacketAssembler.assemble() is the only LLM call site this wave | pending | Live evidence: Qwen produces a richer rationale for an APPROVE/REFER/INSUFFICIENT_EVIDENCE case; deterministic verdict path unchanged; smoke test green |
| W2 | P2.1 | Rubric YAML at `apps_underwriting_ai/policy/rubrics/judge_underwriting_decision.yaml` | ~1k | Rubric-location policy from predecessor W1 P1.5 (app owns its HOP-specific rubrics) | pending | YAML file readable; loads via standard YAML parser; rubric_id = `underwriting_decision_rationale_v1` |
| W3 | P3.1 | Frontier-API second-judge pairing (deferred — trigger-conditioned) | ~0 | Wilson-CI agreement < 0.85 OR provider keys not yet available | passive | Deferred; documented as future hardening |
| W4 | P4.1 | Full HOP pipeline activation (separate workstream — not this plan) | ~0 | Out of scope | deferred | Activation of profile_analysis / research / sender_grounding / routing / validation / qa_report / integration stages tracked separately |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Rubric YAML authoring | `apps_underwriting_ai/policy/rubrics/judge_underwriting_decision.yaml` (NEW) + parent dirs | Deciding rubric content for a regulated-domain explainability judge — bias toward narrow scope (rationale clarity, factual grounding in evidence_refs, no fabrication of feature values) | 1k | pending |
| P1.2 | Wire Qwen-first cascade in DecisionPacketAssembler.assemble() | `apps_underwriting_ai/engines/decision_packet_assembler.py` | Sync openai.OpenAI cascade matching W2/W3/W5/burndown-P1.1 pattern; preserve frozen DecisionPacket immutability by deciding verdict + rationale before construction | 2k | pending |
| P1.3 | Live smoke verification | inline Python test against real Qwen-32B | Confirm verdict path deterministic; rationale enriched only on Qwen accept | 1k | pending |
| P3.1 | Frontier second-judge pairing | passive — deferred | Same trigger pattern as predecessor W4 P4.4 | 0 | passive |
| P4.1 | Full HOP pipeline activation | passive — deferred | 7 of 9 stages still placeholder | 0 | deferred |

## ADG_HOTSPOT_REPORT

Single-file edit to `decision_packet_assembler.py` plus one new YAML.
The decision_packet_assembler is a downstream consumer (low fan-out).
No layer crossings, no new ADG hotspot.

## ADG_GRAPH_LAYER_EVIDENCE

`apps_underwriting_ai/engines/hop_assemble_decision_engine.py` already
calls `DecisionPacketAssembler.assemble()` — the substrate edge from
HOP5 to the assembler is in place. This wave inserts a Qwen call
INSIDE the assembler before `DecisionPacket(...)` construction; no
new edges, no fan-in or fan-out change.

## Decision Log

- **2026-05-02 18:13 UTC** — Plan created. Compliance-posture floor
  set: LLM touches `rationale` only; verdict path stays deterministic.
  Future-hardening trigger (frontier pairing) deferred to passive.
  Full-app activation (7 placeholder engines) explicitly out of
  scope — separate workstream.

## Burndown Order

1. **P1.1 + P1.2 + P1.3** (this session) — rubric + cascade wiring + live smoke.
2. **P2.1** — folded into P1.1 (rubric file authored as part of W1).
3. **P3.1, P4.1** — passive / deferred.
