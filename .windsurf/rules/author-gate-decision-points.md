---
trigger: model_decision
description: Use this rule when a Author-Gate decision point is reached to apply the correct trigger pattern, option shape, scoring guidance, and telemetry format.
---

> See `.windsurf/RULES_INDEX.md#always-on-discipline` for shared retrieval / enforcement guidance.

# Author-Gate Decision Points — Full Doctrine

## §AG-1: Mandatory Decision Point Triggers

### 1.1 Code Architecture Decisions
TRIGGER: Multiple viable architectural approaches AND at least one clears surface_threshold = 0.72.
Score by: SVP priorities (operational simplicity, dependency hygiene, zero-regression) vs blast radius, reversibility, test surface.
If one approach dominates: surface it alone — do not append a "keep current" strawman.

### 1.2 Refactoring Scope
TRIGGER: Refactoring could affect multiple files AND scope genuinely varies in risk/coverage.
Score by: blast radius, reversibility, test surface change, dependencies to update, time to validate.
If minimal scope dominates (score ≥ 0.85, gap ≥ 0.12): surface only minimal — do not fabricate moderate/comprehensive alternatives.

### 1.3 Anti-Pattern Introduction
TRIGGER: Before introducing any anti-pattern instance (pre_write_gate has already blocked; this Author-Gate determines resolution path).
Assess whether the specific anti-pattern can be narrowed without a guardian comment first.
If narrowing is feasible: dominance rule fires — surface only narrow-exception option.
If narrowing genuinely infeasible: score guardian-comment vs restructure.

### 1.4 Test Modification Strategy
TRIGGER: Test failure has two or more genuinely credible repair paths with different correctness implications.
Classify root cause first (production bug, stale reference, semantic update, policy regression).
In most cases root cause resolves ambiguity — Author-Gate only when two repair classes are both plausible.

### 1.5 Dependency Addition
TRIGGER: Adding a new external dependency where in-house alternative is non-trivial or an existing dep may serve.
Check existing deps/utilities first. If they fully cover the need — no Author-Gate.
Score external package lower if: narrow feature surface, transitive deps, version conflicts.

### 1.6 File/Module Deletion
TRIGGER: Before deleting or archiving any production file.
Check references. Check deprecation status (90-day period).
If zero references + deprecation elapsed: dominance fires for archive.
If active references remain: Author-Gate between deprecate-first and keep-as-shim — delete is not a credible candidate.

### 1.7 Configuration Changes
TRIGGER: Before modifying governance/policy configuration where value or scope is genuinely ambiguous.
If change is already decided (user specified value): no Author-Gate — just apply it.
Do not add "keep current" as an option when config change is the stated goal.

### 1.8 Error Handling Strategy
TRIGGER: Error handling strategy is genuinely ambiguous — fail-closed vs retry vs escalate each have credible arguments.
Classify error type first: transient infrastructure, invalid input, missing config, resource exhaustion, external API.
Constitutional default: fail-closed scores highest unless error is demonstrably transient.
Invalid input/missing config: fail-closed dominates — do not generate retry or escalate as candidates.

### 1.9 Performance Optimization Trade-offs
TRIGGER: Only when optimization materially changes correctness risk or operational complexity AND two approaches have meaningfully different risk profiles.
If optimization is clearly superior (measured speedup, no correctness risk): implement, no Author-Gate.
Generate candidates only when trade-offs are non-trivial (caching staleness risk, parallelism ordering risk).

### 1.10 ADG Regeneration Timing
TRIGGER: ADG staleness creates genuine risk of incorrect blast-radius analysis for current task.
If ADG is fresh (newer than HEAD): no Author-Gate — proceed.
If ADG is stale AND T2/T3 refactoring: regenerate immediately, no Author-Gate — this is the only correct answer.
Author-Gate only if regeneration cost is significant AND task can safely proceed with known-stale graph.

### 1.11 Certification Claim (`certification_claim`) — Constitutional §32
TRIGGER: Before claiming (in prose or as a tool invocation) that any `RTC-REQ-*` is SIGNED_OFF, FINAL_SIGNED_CERTIFICATION, "certified", or that the bundle `trust_level` has been upgraded.
Cascade MUST run `scripts/compile_requirement_signoff.py` + `scripts/verify_final_requirement_signoff_bundle.py` in the same response and include the resulting `trust_level` and `merkle_root` in the Author-Gate packet.
Precedent: all prior certification decisions live in the ADR Registry (Notion MCP) and under `docs/architecture/adr/ADR-*-runtime-cert-*.md`.
Recommended option defaults to: "Run the compiler + bundle verifier, then report their actual output verbatim — no prose summary until the tools have spoken."
If compiler / verifier output disagrees with the claim: dominance fires against the claim (do not surface "assert anyway" as a credible candidate).
If the mutation-rejection report (`artifacts/certification/fortknox_mutation_rejection_report.json`) is older than the report being claimed: require regeneration before proceeding — no Author-Gate on this sub-decision, it is the only correct answer.
Telemetry: emit `DECISION_CAPTURED: type=certification_claim, repo_area=certification, selected=<verbatim_output|refused_to_claim>, outcome=executed, ...`.
Advisory rule: `.windsurf/rules/fortknox-certification-discipline.md`. Skill: `.windsurf/skills/fortknox-evidence/SKILL.md`.

---

## §Author-Gate-9: Confidence Thresholds (SSOT reference)

surface_threshold: 0.72
high_confidence_band: 0.85
dominance_score_threshold: 0.85
dominance_delta: 0.12
max_surface_options: 4

Scoring anchors:
- ≥ 0.85: Clearly correct, reversible, blast radius contained, SVP priorities align
- 0.72–0.84: Credible and defensible but non-trivial tradeoffs or unknowns
- < 0.72: Significant unknowns, high blast radius, or conflicts with constitutional constraints

---

## §AG-10: Option Shape Contract

Every surfaced option MUST include these fields. Generic pros/cons are FORBIDDEN.

- **decision_thesis**: One sentence. What this option does and why someone would rationally choose it. Must reference actual system/component.
- **value_to_goal**: Concrete value for the stated objective, tied to current request/repo state.
- **key_tradeoffs**: 3–5 precise tradeoffs framed as "Gains X, but increases Y because Z" — every claim tied to this specific architecture.
- **execution_impact**: Files/layers touched; localized vs cross-cutting; test surface expansion; backward compatibility.
- **risk_profile**: Primary failure mode; blast radius (files/layers/callers); detectability; reversibility.
- **time_to_value**: Immediate (this session) / near-term (requires follow-on) / delayed (requires data).
- **why_not_default** (non-top options only): Why not automatically chosen.
- **recommendation_delta** (non-top options only): Why it ranks lower than the top option.

Banned weak phrasing unless followed by architecture-specific explanation:
more flexible, more scalable, simpler, more robust, easier to maintain, higher effort, lower risk, better long-term.

---

## §Author-Gate-11: Telemetry (included in question field)

Every Author-Gate invocation MUST include in the packet header:

    Candidates evaluated: N
    Suppressed (low confidence): X (scored below 0.72)
    Suppressed (non-distinct): Y (collapsed into surviving option)
    Surfaced: M
    Top confidence score: <score>
    Confidence delta (top vs next): <delta or N/A if single option>

---

## MAXIM

- Signal over count. One strong option beats three padded alternatives.
- Dominance fires cleanly. When the answer is clear, surface it and say so.
- Threshold gates confidence. Below 0.72 means clarify, replan, or abstain.
- Distinctness is required. Cosmetic variants do not warrant separate options.
- Analysis is executive-grade. Every claim tied to actual architecture, not generic software advice.
- Wait for choice. When Author-Gate fires, do not proceed without user selection.
