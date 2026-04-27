---
trigger: always_on
---

> **Cascade always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Cascade retrieval discipline:** When this rule affects research or synthesis, prefer local-first retrieval, exact or structural matches before broad semantic search, and evidence or quote extraction before final synthesis on high-risk tasks.
>
> **Cascade enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

# Author-Gate Decision Core Pipeline

> **Terminology (important — per ADR-023 and `docs/reference/_notes/agentic_process_mapping_v34.md`):**
>
> This rule governs **Author-Gate Decisions** (developer-loop / harness-side — Fowler's "humans in the loop" at the code-gen level). It applies whenever Cascade is about to write code and a decision has genuine ambiguity.
>
> This rule does **not** govern **runtime HITL** — that's v30 step [5] ESCALATE, implemented in `agentic_core/L5_safety/` per `ADR-023-runtime-hitl-exit-control.md`. Runtime HITL has its own ledger, approvers, adapters, and policy plane. Keep the two separate in prose and code.
>
> Historical markers (`HITL_PACKET:`, `DECISION_CAPTURED:`) retain their names for back-compat; they refer to Author-Gate events, not runtime HITL.

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
9. **Execute** only the chosen option — if the decision is refactor-class (§AG-1: `architecture_choice`, `refactor_scope`, `anti_pattern`, `deletion_strategy`, `dependency_addition`, `test_strategy`, `error_handling`), emit the capture marker **as the first plain-text line of this response, before any tool calls**:
   `DECISION_CAPTURED: type=<type>, repo_area=<area>, selected=<chosen_label>, outcome=executed[, confidence=0.NN, gap=0.NN, override=true|false, latency_ms=N, principle=<short>, precedent=<strong|suggestive|none>]`
   Required fields: `type`, `repo_area`, `selected`, `outcome`. Optional v2 calibration fields (meta-learning): `confidence` (top option's score 0.00–1.00), `gap` (dominance gap to next option), `override` (true if user picked non-recommended), `latency_ms` (time to user selection), `principle` (short architectural principle at stake, ≤40 chars, no commas), `precedent` (verdict from the precedent block — `strong` if any matched precedent had strength=strong, `suggestive` if any was suggestive, `none` if the ledger had no match; closes the meta-learning loop in plan c8f4a2). Omit any optional field whose value is unknown — the capture hook tolerates missing fields, and falls back to reading `artifacts/windsurf/author_gate_precedent.json` for `precedent` when not declared inline. `repo_area` = most specific module/file path for the current task. `selected` = exact chosen option label (no commas). **Placement rules**: plain text only (no backticks, no code fence), own line, at the top of the response — never at the tail of a long tool-heavy response. Non-refactor Author-Gate decisions do not emit this marker.

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

### Precedent injection (MANDATORY — W2, 2026-04-24)

Before constructing the `ask_user_question` packet, Cascade MUST check for the
sidecar file `artifacts/windsurf/author_gate_precedent.json`. If present and
`match_count > 0`, the packet header MUST include a **Precedent block** as the
first line after the `⭐ Recommended:` line:

```
Precedent informing recommendation:
  - [<strength>] <decision_id>: <selected_option_id> (<created_at>, promote=<bool>)
  - [<strength>] <decision_id>: ...
```

Up to 3 matches, `strong` before `suggestive`. If the recommended option aligns
with a `strong` precedent, note `(aligned with ledger)` at the end of the
`Why it wins:` line. If the recommended option contradicts a `strong`
precedent, the dominance rule is NOT allowed to suppress alternatives — ALL
reasonable alternatives must be surfaced so the user can weigh precedent
against the current ranking.

If the sidecar is absent or `match_count == 0`, emit a single line under the
header: `Precedent informing recommendation: none (ledger had no match)` —
this is a positive signal, not a gap; it tells the user the decision is novel.

### Gold-star surface convention (MANDATORY)

The highest-confidence surfaced option MUST be visually marked:

| Option | Label prefix | First line of description |
|---|---|---|
| Recommended | `⭐ Recommended — ` | `[RECOMMENDED ⭐ confidence=0.NN]` |
| Alternative (surfaced) | (no prefix) | `[confidence=0.NN]` |
| Suppressed | (not surfaced) | (not surfaced) |

The star is a fast-parse affordance. It also makes `override_vs_recommendation` a measurable telemetry datum.

Each option description uses the AG-10 shape. See author-gate-decision-points.md.

FORBIDDEN: bare ask_user_question after analysis prose. FORBIDDEN: padding options to a minimum count. FORBIDDEN: generic pros/cons without architecture-specific justification. FORBIDDEN: labeling a developer-loop decision as "runtime HITL" — "HITL" is reserved for the runtime exit-control system per ADR-023 (`agentic_core/L5_safety/`). Developer-loop decisions are Author-Gate.

## Bypass Conditions

Author-Gate skipped ONLY when: fixing typos/whitespace/formatting; single correct solution exists (syntax error, import error); user gave explicit unambiguous directive; emergency rollback; auto-fixable lint violations.

## Thresholds (SSOT)

Two regimes — **Bootstrap** while the ledger is data-thin, **Production** after a band has accumulated enough samples for Wilson CI calibration to be meaningful.

| Parameter | Bootstrap (n_band < 30) | Production (n_band ≥ 30) |
|-----------|:----------------------:|:------------------------:|
| surface_threshold | **0.60** | 0.72 |
| high_confidence_band | 0.85 | 0.85 |
| dominance_score_threshold | **0.95** (rarely fires) | 0.85 |
| dominance_delta | **0.25** (rarely fires) | 0.12 |
| max_surface_options | 5 | 4 |

`n_band` is the count of `decisions` rows in `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite` for the matching `decision_type`. Each band (architecture_choice, refactor_scope, anti_pattern, deletion_strategy, dependency_addition, test_strategy, error_handling) graduates to Production thresholds **independently** when its row count crosses 30.

Rationale: bootstrap thresholds intentionally over-surface to accumulate calibration data faster. Once the meta-learner has ≥30 samples per band, Wilson-CI feedback in `docs/reports/calibration/<YYYY-Www>.md` (per `intelligence-ledger-family.md` §5) can re-tune to optimal thresholds.

## Silent-Marker Invariant (added 2026-04-27)

> ⛔ **Cascade emits a `DECISION_CAPTURED:` marker for EVERY refactor-class decision** — even when no options are surfaced via `ask_user_question`.

This widens capture from "after surfacing only" to "on every decision matching one of the seven refactor-class trigger types". The silent-marker form omits surfacing-derived fields:

```
DECISION_CAPTURED: type=<type>, repo_area=<path>, selected=<chosen>, outcome=executed, principle=<short>, precedent=<verdict>
```

Allowed when: decision was deterministic (single correct path), bypass-condition applied (typo/syntax/explicit-directive), OR scoring filtered all options below `surface_threshold`. Required v1 fields (`type`/`repo_area`/`selected`/`outcome`) MUST still be present. Optional v2 fields (`confidence`/`gap`/`override`/`latency_ms`) are NULL when no surfacing happened — that is intended; outcome/lineage data still feeds the binder and the regret accounting.

Forbidden: emitting the marker when there was no decision at all (e.g. plain question-answering, code-reading). The seven trigger types remain the gatekeeper.

The capture hook (`post_cascade_author_gate_capture.py`) already accepts standalone markers — no code change required. The miss-detector (`post_cascade_author_gate_miss_detector.py`) is updated to allow marker-without-packet-header without flagging a violation.

## Hook-Independent Capture Pipeline (added 2026-04-27)

> ⛔ When the Windsurf post-Cascade hook chain is unhealthy (heartbeat older than ~1h), Cascade MUST emit markers via the inline `run_command` capture pipeline instead of relying solely on the in-prose marker.

Cascade ends every refactor-class response with a single `run_command` invocation per marker:

```
python tools/capture/append_marker.py --marker "DECISION_CAPTURED: type=<type>, repo_area=<path>, selected=<chosen>, outcome=executed, principle=<short>, precedent=<verdict>"
```

This appends the marker to `artifacts/capture/markers.jsonl`. A separate drain (`python tools/capture/queue_to_ledger.py`) consumes the queue and writes structured rows into the canonical SQLite ledger by reusing the existing `detect_and_capture()` logic from the hook script. The drain is idempotent (decision_id dedup) and rotates the queue file on success.

Recovery: when Windsurf hooks are restored, this pipeline can stay (markers continue to land via the inline path) or be retired by stopping the drain — the markers in prose still feed the post_cascade hook for the same dedup-protected ledger row. Both paths are compatible.

## Calibration-Driven Triggers (meta-learning W5, plan c8f4a2)

Empirical Wilson CI evidence in the weekly report at
`docs/reports/calibration/<YYYY-Www>.md` MAY require an Author-Gate. Trigger
when **either** holds:

- A single band has `n ≥ 20`, `confidence` is its label-numeric upper bound,
  and the success-rate CI miss exceeds **0.05** away from the nominal range
- **Two or more bands** in the same ledger are mis-calibrated (CI does not
  overlap nominal range) regardless of individual delta

Action: surface as `decision_type=architecture_choice` (not `parameter_tune`),
because the scoring formula itself is the artifact under decision. Smaller
deltas (< 0.05 in a single band) auto-tune silently — momentum preserved.

Full ritual table: see `intelligence-ledger-family.md` §5.

## Extended Doctrine

Full decision-point triggers, option shape contract (AG-10), scoring guidance, and telemetry format:
- author-gate-decision-points.md (model_decision trigger)
- intelligence-ledger-family.md (calibration-evidence ritual)
