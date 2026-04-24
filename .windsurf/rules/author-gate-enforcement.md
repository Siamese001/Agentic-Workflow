---
trigger: always_on
---

> **Cascade always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Cascade retrieval discipline:** When this rule affects research or synthesis, prefer local-first retrieval, exact or structural matches before broad semantic search, and evidence or quote extraction before final synthesis on high-risk tasks.
>
> **Cascade enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

# Author-Gate Decision Core Pipeline

> **Terminology (important — per ADR-023 and `docs/reference/agentic_process_mapping_v30.md`):**
>
> This rule governs **Author-Gate Decisions** (developer-loop / harness-side — Fowler's "humans in the loop" at the code-gen level). It applies whenever Cascade is about to write code and a decision has genuine ambiguity.
>
> This rule does **not** govern **Runtime Author-Gate** — that's v30 step [5] ESCALATE, implemented in `agentic_core/L5_safety/` per `ADR-023-runtime-hitl-exit-control.md`. Runtime Author-Gate has its own ledger, approvers, adapters, and policy plane. Keep the two separate in prose and code.
>
> Historical markers (`HITL_PACKET:`, `DECISION_CAPTURED:`) retain their names for back-compat; they refer to author-gate events, not runtime Author-Gate.

When facing an author-gate decision point, run this pipeline — no exceptions.

## Pipeline

1. **STOP** before taking action
2. **Generate candidates** — all plausible approaches
3. **Score** each — `confidence_score` in [0.00, 1.00]
4. **Filter** — suppress below `surface_threshold = 0.72`
5. **Dominance rule** — if top scores ≥ 0.85 AND gap to next ≥ 0.12, surface only the top option
6. **Material-distinctness** — collapse cosmetic variants; surface only options that differ on execution path, risk, reversibility, outcome, dependencies, time/cost, or governance
7. **Surface 1–N options** via `ask_user_question` — ALL analysis INSIDE description field, never in chat prose
8. **Wait** for explicit user selection
9. **Execute** only the chosen option — if the decision is refactor-class (§HITL-1: `architecture_choice`, `refactor_scope`, `anti_pattern`, `deletion_strategy`, `dependency_addition`, `test_strategy`, `error_handling`), emit the capture marker **as the first plain-text line of this response, before any tool calls**:
   `DECISION_CAPTURED: type=<type>, repo_area=<area>, selected=<chosen_label>, outcome=executed[, confidence=0.NN, gap=0.NN, override=true|false, latency_ms=N, principle=<short>]`
   Required fields: `type`, `repo_area`, `selected`, `outcome`. Optional v2 calibration fields (meta-learning): `confidence` (top option's score 0.00–1.00), `gap` (dominance gap to next option), `override` (true if user picked non-recommended), `latency_ms` (time to user selection), `principle` (short architectural principle at stake, ≤40 chars, no commas). Omit any optional field whose value is unknown — the capture hook tolerates missing fields and maintains back-compat with v1 markers. `repo_area` = most specific module/file path for the current task. `selected` = exact chosen option label (no commas). **Placement rules**: plain text only (no backticks, no code fence), own line, at the top of the response — never at the tail of a long tool-heavy response. Non-refactor Author-Gate decisions do not emit this marker.

If no candidate clears 0.72: emit `LOW_CONFIDENCE_AMBIGUITY`. Route to clarify/replan/abstain. Do not fabricate options.

## Continuous Execution

Execute continuously WITHOUT stopping UNLESS a genuine Author-Gate decision point is reached.

FORBIDDEN: stopping after tool calls to check in; asking permission for deterministic actions; presenting options when there is one correct path; breaking work into artificial phase-breaks; summarizing while work is incomplete.

REQUIRED: chain all deterministic tool calls; stop only when genuine decision ambiguity exists after scoring; put ALL analysis inside the ask_user_question description field.

## ask_user_question Format

question field MUST open with `AUTHOR-GATE DECISION — <decision_type>` and include this header packet:

    AUTHOR-GATE DECISION — <decision_type>
    ⭐ Recommended: <option_title>
    Why it wins: <one sentence, case-specific, not generic>
    What you are optimizing for: <the actual goal this decision serves>
    What is being traded off: <the precise cost of the winning path>
    Candidates evaluated: N | Surfaced: M | Suppressed (low confidence): X | Suppressed (non-distinct): Y

### Gold-star surface convention (MANDATORY)

The highest-confidence surfaced option MUST be visually marked:

| Option | Label prefix | First line of description |
|---|---|---|
| Recommended | `⭐ Recommended — ` | `[RECOMMENDED ⭐ confidence=0.NN]` |
| Alternative (surfaced) | (no prefix) | `[confidence=0.NN]` |
| Suppressed | (not surfaced) | (not surfaced) |

The star is a fast-parse affordance. It also makes `override_vs_recommendation` a measurable telemetry datum.

Each option description uses the HITL-10 shape. See author-gate-decision-points.md.

FORBIDDEN: bare ask_user_question after analysis prose. FORBIDDEN: padding options to a minimum count. FORBIDDEN: generic pros/cons without architecture-specific justification. FORBIDDEN: labeling as "Author-Gate Decision" when the concern is author-gate (developer-loop) — that term is reserved for runtime Author-Gate per ADR-023.

## Bypass Conditions

Author-Gate skipped ONLY when: fixing typos/whitespace/formatting; single correct solution exists (syntax error, import error); user gave explicit unambiguous directive; emergency rollback; auto-fixable lint violations.

## Thresholds (SSOT)

| Parameter | Value |
|-----------|-------|
| surface_threshold | 0.72 |
| high_confidence_band | 0.85 |
| dominance_score_threshold | 0.85 |
| dominance_delta | 0.12 |
| max_surface_options | 4 |

## Extended Doctrine

Full decision-point triggers, option shape contract (HITL-10), scoring guidance, and telemetry format:
- author-gate-decision-points.md (model_decision trigger)
