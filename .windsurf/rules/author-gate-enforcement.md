---
trigger: model_decision
description: Apply when an Author-Gate decision point is reached during code authoring (refactoring scope, architecture choice, anti-pattern, deletion, dependency add, test strategy, error handling). Distinct from runtime HITL (ADR-023). Demoted from always_on 2026-05-01 per Anthropic two-tier compliance.
---

# Author-Gate Enforcement — Invariant-Only Stub

> **Terminology**: This rule governs **Author-Gate Decisions** (developer-loop / harness-side, per ADR-023). It is NOT runtime HITL (v30 step [5] ESCALATE in `agentic_core/L5_safety/`). Historical markers (`HITL_PACKET:`) retain their legacy names but refer to Author-Gate events.

> **Canonical SSOT for packet shape**: `.windsurf/schemas/author_gate_packet.schema.json` (plan `author-gate-ssot-consolidation-b7c3e1`). All field names, types, enums, and the `routing.rule_applied` star-count contract live there. This rule defines *when to fire* and *score discipline*; field-level shape questions defer to the schema.

## The Pipeline (constitutional invariant — short form)

When facing an author-gate decision point:

1. **STOP** before action
2. **Generate** all plausible candidates
3. **Score** 0.00–1.00 (`confidence_score`)
4. **Filter** below `surface_threshold` (0.72 prod / 0.60 bootstrap)
5. **Dominance**: top ≥0.85 AND gap ≥0.12 → surface alone
6. **Material distinctness**: collapse cosmetic variants
7. **Surface 1–N options** via `ask_user_question` — analysis INSIDE description, not chat prose. Every surfaced option description MUST satisfy the **four-requirement contract** below. The canonical wire description is `candidate.surface_description` minted by `emit_packet.py`; consumers (renderer, Cascade composition) MUST pass it through unchanged or extend it without dropping any requirement.

   | # | Requirement | Concrete shape | Enforced by |
   |---|---|---|---|
   | 1 | **Cascade clickable** | options reach `ask_user_question` (Windsurf-rendered clickable list, not chat prose) | `post_cascade_ask_user_question_packet_audit.py` (vacuum-closure: invalid packet OR missing packet at high decision-density → severity high/critical) |
   | 2 | **Confidence prefix** | `[confidence=0.NN]` or `[RECOMMENDED ⭐ confidence=0.NN]` at start of `description` | `post_cascade_author_gate_ui_audit.py` invariant 1 |
   | 3 | **Pros/cons (tradeoff segment)** | ` · trade-off: <≥20 chars>` somewhere after the prefix; emitter sets `surface_description_floor` from `key_tradeoffs[0]`, callers may extend via `surface_description` | `post_cascade_author_gate_ui_audit.py` invariant 4 (added by plan `author-gate-four-req-enforcement-c4d2a8`) |
   | 4 | **Dominance star** | `⭐` prefix appears on **exactly one** option iff `routing.rule_applied == "dominance_fires"`, **zero** options otherwise | `post_cascade_author_gate_ui_audit.py` invariants 2 + 3 |

   Failure modes log to `artifacts/windsurf/author_gate_ui_violations.jsonl` (UI invariants 1–4) and `artifacts/windsurf/ask_user_question_packet_violations.jsonl` (vacuum-closure). CI freshness gates: `ops_scripts/ci/author_gate/check_ui_conformance.py` and `ops_scripts/ci/author_gate/check_ask_user_question_packet_freshness.py`.

   **Pipeline Completion Invariant** (plan `author-gate-ui-renderer-hardening-a7f3c2`):

   > ⛔ Every `AUTHOR_GATE_PACKET:` (or legacy `HITL_PACKET:`) emitted in a response **MUST** be followed by an `ask_user_question` tool invocation **in the same response**. A packet without a same-response `ask_user_question` is a critical violation.

   | Direction | Invariant | Enforced by |
   |---|---|---|
   | Packet → Ask | `AUTHOR_GATE_PACKET:` present ⇒ `ask_user_question` present | `post_cascade_author_gate_pipeline_audit.py` → `artifacts/windsurf/author_gate_pipeline_violations.jsonl` |
   | Ask → Packet | `ask_user_question` in AG context ⇒ `AUTHOR_GATE_PACKET:` present | `post_cascade_ask_user_question_packet_audit.py` → `artifacts/windsurf/ask_user_question_packet_violations.jsonl` |

   Pure detection logic: `.windsurf/scripts/_author_gate_pipeline_check.py` (`decide()` function). CI freshness: `ops_scripts/ci/check_author_gate_pipeline_freshness.py` (AGP1, fail-closed by default; `AG_PIPELINE_ADVISORY=1` for warning-only). Bypass: `AG_PIPELINE_AUDIT_BYPASS=1`.

   **Forbidden**: emitting `AUTHOR_GATE_PACKET:` then ending the response without `ask_user_question`; emitting the packet in one response and deferring `ask_user_question` to a follow-up response; relying on the user to manually trigger the question after seeing the packet.

8. **Wait** for explicit user selection
9. **Execute** chosen option; emit `DECISION_CAPTURED:` marker (refactor-class only) as **first plain-text line** of the response

## Canonical-emitter invariant (added 2026-05-03)

> ⛔ `AUTHOR_GATE_PACKET:` blocks MUST be produced by the canonical emitter at
> `.windsurf/skills/author-gate-packet-builder/emit_packet.py`. Hand-crafting
> the packet from memory of the schema is FORBIDDEN — the emitter is the
> SSOT for AG-10 shape (`decision_id`, `policy_snapshot`, `context_fingerprint.fp`,
> `routing.{rule_applied,surface_threshold,top_score}`, `precedent.verdict`,
> `reason_code_palette`, per-candidate `signals`/`signal_weights`/`raw_score`).

**Why**: hand-crafted packets typically omit the canonical fields the capture
hook `post_cascade_author_gate_capture.py` keys on, so the row never lands in
`.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite`,
calibration/weekly-report misses the decision, and CI gate
`check_decision_ledger_sqlite_freshness.py` flags the turn as a stale-ledger
violation (constitutional §30).

**Required pipeline** for every Author-Gate emission:

1. `refactor-decision-memory` skill — consult precedent ledger first.
2. `author-gate-packet-builder` skill — build a JSON spec, pipe to
   `emit_packet.py` via stdin; capture stdout (the canonical packet block)
   and emit it inline so `post_cascade_author_gate_capture.py` can parse it.
3. `author-gate-ui-renderer` skill — render the recommendation card.
4. `ask_user_question` — descriptions begin with `[confidence=0.NN]`
   (or `[RECOMMENDED ⭐ confidence=0.NN]` when dominance fires).
5. On user reply — emit `DECISION_CAPTURED:` as the first plain-text line and
   plumb to the SQLite ledger via `tools/capture/append_marker.py`.

**Enforcement**: post-cascade hook
`.windsurf/scripts/post_cascade_author_gate_schema_audit.py` validates the
packet shape on every response and logs non-conformant packets to
`artifacts/windsurf/author_gate_schema_violations.jsonl`. Sibling hook
`post_cascade_author_gate_ui_audit.py` continues to validate the UI side
(option-prefix, gold-star, dominance match).

**Bypass**: `AUTHOR_GATE_SCHEMA_BYPASS=1` env var — logs a `reason="bypass"`
row and lets the response pass. Use only for scripted batch runs.

## Marker grammar (refactor-class only)

```
DECISION_CAPTURED: type=<type>, repo_area=<area>, selected=<chosen>, outcome=executed[, confidence=0.NN, gap=0.NN, override=true|false, latency_ms=N, principle=<short>, precedent=<strong|suggestive|none>, exit_criteria=<short>]
```

Required: `type`, `repo_area`, `selected`, `outcome`. Plain text only, own line, top of response.

## Continuous Execution Invariant

Execute continuously WITHOUT stopping UNLESS a genuine Author-Gate decision point is reached. FORBIDDEN: stopping after tool calls, asking permission for deterministic actions, presenting options when there's one correct path.

## Bypass conditions (no Author-Gate needed)

Typos/whitespace/formatting · single correct solution (syntax/import error) · explicit unambiguous user directive · emergency rollback · auto-fixable lint.

## Silent-marker invariant (added 2026-04-27)

Every refactor-class decision MUST emit a `DECISION_CAPTURED:` marker — even when no options surfaced via `ask_user_question`. The seven trigger types are the gatekeeper: `architecture_choice`, `refactor_scope`, `anti_pattern`, `deletion_strategy`, `dependency_addition`, `test_strategy`, `error_handling`.

## Where the procedural detail lives

| Concern | Location |
|---|---|
| Full AG-10 option shape, packet construction, gold-star format, precedent injection | `.windsurf/skills/author-gate-packet-builder/SKILL.md` |
| Decision-point trigger doctrine (AG-1.1 through AG-1.11) | `.windsurf/rules/author-gate-decision-points.md` |
| SVP calibration thresholds (band-by-band) | `.windsurf/rules/author-gate-svp-calibration.md` |
| Refactor decision precedent | `.windsurf/skills/refactor-decision-memory/SKILL.md` |
| Capture hook (live) | `.windsurf/scripts/post_cascade_author_gate_capture.py` |
| Miss detector | `.windsurf/scripts/post_cascade_author_gate_miss_detector.py` |
| Hook-independent fallback | `tools/capture/append_marker.py` + `tools/capture/queue_to_ledger.py` |
| Pre-session staleness check | `tools/capture/ledger_staleness_check.py` |
| CI gate | `ops_scripts/ci/check_capture_queue_freshness.py` |
| Decision ledger SSOT | `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite` |
| Inline-capture queue | `artifacts/capture/markers.jsonl` |
| Bypass | `AUTHOR_GATE_STALE_BYPASS=1` (queue) |

## Calibration-driven triggers

Empirical Wilson CI evidence in `docs/reports/calibration/<YYYY-Www>.md` MAY require an Author-Gate when: a band has `n ≥ 20` AND CI miss > 0.05 from nominal range, OR ≥2 bands in same ledger are mis-calibrated. Action: `decision_type=architecture_choice`. Smaller deltas auto-tune silently.

## Constitutional cross-reference

§6 (Author-Gate for ambiguous decisions). §30 (Author-Gate capture health mandatory). Sibling `.windsurf/rules/anti-pattern-author-gate.md` for the anti-pattern subcase. ADR-023 separates this from runtime HITL.
