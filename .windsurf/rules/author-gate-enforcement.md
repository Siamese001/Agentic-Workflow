---
trigger: always_on
description: Author-Gate enforcement — pipeline steps, four-requirement contract, canonical-emitter invariant, pipeline-completion invariant. Promoted from model_decision 2026-05-09 per DS-2 of plan always-on-budget-compression-ds2-c7f4a3.
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
7. **Surface 1–N options** via `ask_user_question` — analysis INSIDE description, not chat prose. Every option MUST satisfy the **four-requirement contract**:
   - **Cascade clickable** — options reach `ask_user_question` (not prose)
   - **Confidence prefix** — `[confidence=0.NN]` or `[RECOMMENDED ⭐ confidence=0.NN]`
   - **Tradeoff segment** — ` · trade-off: <≥20 chars>`
   - **Dominance star** — `⭐` on exactly one option iff dominance fires

   **Pipeline Completion Invariant**: Every `AUTHOR_GATE_PACKET:` MUST be followed by `ask_user_question` in the **same response**. Enforced by `post_cascade_author_gate_pipeline_audit.py` and `post_cascade_ask_user_question_packet_audit.py`. **Forbidden**: packet without same-response ask; deferring to follow-up; relying on user manual trigger. **Bypass**: `AG_PIPELINE_AUDIT_BYPASS=1`.

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

**Required pipeline**: Use `refactor-decision-memory` → `author-gate-packet-builder` → `author-gate-ui-renderer` → `ask_user_question` → `DECISION_CAPTURED:` marker. See skill docs for detailed procedure.

**Enforcement**: Post-cascade hooks validate schema (`post_cascade_author_gate_schema_audit.py`) and UI (`post_cascade_author_gate_ui_audit.py`). **Bypass**: `AUTHOR_GATE_SCHEMA_BYPASS=1`.

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

## Where detail lives

- **AG-10 packet shape**: `author-gate-packet-builder` skill
- **Trigger doctrine**: `author-gate-decision-points.md` rule  
- **SVP calibration**: `author-gate-svp-calibration.md` rule
- **Precedent lookup**: `refactor-decision-memory` skill
- **Hooks**: `post_cascade_author_gate_*` scripts, `ledger_staleness_check.py`
- **Ledger**: `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite`
- **Queue bypass**: `AUTHOR_GATE_STALE_BYPASS=1`

## Calibration-driven triggers

Empirical Wilson CI evidence in `docs/reports/calibration/<YYYY-Www>.md` MAY require an Author-Gate when: a band has `n ≥ 20` AND CI miss > 0.05 from nominal range, OR ≥2 bands in same ledger are mis-calibrated. Action: `decision_type=architecture_choice`. Smaller deltas auto-tune silently.

## Constitutional cross-reference

§6 (Author-Gate for ambiguous decisions). §30 (Author-Gate capture health mandatory). Sibling `.windsurf/rules/anti-pattern-author-gate.md` for the anti-pattern subcase. ADR-023 separates this from runtime HITL.
