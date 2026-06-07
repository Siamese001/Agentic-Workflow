---
trigger: model_decision
description: Author-Gate enforcement — pipeline steps, four-requirement contract, canonical-emitter invariant, pipeline-completion invariant. Promoted from model_decision 2026-05-09 per DS-2 of plan always-on-budget-compression-ds2-c7f4a3. Demoted from always_on 2026-05-26 (governance-dedup-closeout-e8a4c2 W4). Cursor SSOT: .cursor/rules/author-gate-enforcement.mdc (alwaysApply: false).
---

# Author-Gate Enforcement — Invariant-Only Stub

> **Terminology**: Governs **Author-Gate Decisions** (developer-loop / harness-side, per ADR-023). NOT runtime HITL (v30 step [5] in `agentic_core/L5_safety/`). Historical `HITL_PACKET:` markers retain legacy names.

> **Packet shape SSOT**: `.windsurf/schemas/author_gate_packet.schema.json`. This rule defines *when to fire* and *score discipline*; field-level shape defers to the schema.

## The Pipeline (constitutional invariant — short form)

When facing an author-gate decision point:

1. **STOP** before action
2. **Generate** all plausible candidates
3. **Score** 0.00–1.00 (`confidence_score`)
4. **Filter** below `surface_threshold` (0.72 prod / 0.60 bootstrap)
5. **Dominance**: top ≥0.85 AND gap ≥0.12 → surface alone
6. **Material distinctness**: collapse cosmetic variants
7. **Surface 1–N options** via `ask_user_question` — analysis INSIDE description, not chat prose. Every option MUST satisfy the **four-requirement contract**:
   - **Cursor Agent clickable** — options reach `ask_user_question` (not prose)
   - **Confidence prefix** — `[confidence=0.NN]` or `[RECOMMENDED ⭐ confidence=0.NN]`
   - **Tradeoff segment** — ` · trade-off: <≥20 chars>`
   - **Dominance star** — `⭐` on exactly one option iff dominance fires

   **Pipeline Completion Invariant**: Every `AUTHOR_GATE_PACKET:` MUST be followed by `ask_user_question` in the **same response**. Enforced by `post_cascade_author_gate_pipeline_audit.py` and `post_cascade_ask_user_question_packet_audit.py`. **Forbidden**: packet without same-response ask; deferring to follow-up; relying on user manual trigger. **Bypass**: `AG_PIPELINE_AUDIT_BYPASS=1`.

8. **Wait** for explicit user selection
9. **Execute** chosen option; emit `DECISION_CAPTURED:` marker (refactor-class only) as **first plain-text line** of the response

## Canonical-emitter invariant

> ⛔ `AUTHOR_GATE_PACKET:` MUST be produced by `.windsurf/skills/author-gate-packet-builder/emit_packet.py`. Hand-crafting is FORBIDDEN — the emitter is the SSOT for AG-10 shape. Hand-crafted packets omit fields that `post_cascade_author_gate_capture.py` keys on, causing ledger misses and stale-ledger CI violations (§30).

**Required pipeline**: `refactor-decision-memory` → `author-gate-packet-builder` → `author-gate-ui-renderer` → `ask_user_question` → `DECISION_CAPTURED:` marker.

**Enforcement**: `post_cascade_author_gate_schema_audit.py`, `post_cascade_author_gate_ui_audit.py`. **Bypass**: `AUTHOR_GATE_SCHEMA_BYPASS=1`.

## Marker grammar (refactor-class only)

```
DECISION_CAPTURED: type=<type>, repo_area=<area>, selected=<chosen>, outcome=executed[, confidence=0.NN, gap=0.NN, override=true|false, latency_ms=N, principle=<short>, precedent=<strong|suggestive|none>, exit_criteria=<short>]
```

Required: `type`, `repo_area`, `selected`, `outcome`. Plain text only, own line, top of response.

## Continuous Execution Invariant

Execute continuously WITHOUT stopping UNLESS a genuine Author-Gate decision point is reached. FORBIDDEN: stopping after tool calls, asking permission for deterministic actions, presenting options when there's one correct path.

### Prose Options Menu — Explicit Prohibition

> ⛔ **Presenting options as Markdown prose is FORBIDDEN.** The following patterns are NOT Author-Gate and MUST NOT be used to present decisions to the user:
> - Bold-labeled options: `**Option A —**`, `**Option B —**`, `**A. Continue...**`
> - Markdown tables of options without `ask_user_question`
> - "Recommended Next Phase/Step/Wave/Action" menus in prose
>
> These patterns produce **zero decision capture** — no ledger entry, no packet, no user-clickable interface. They are indistinguishable from Cursor Agent making the decision unilaterally.
>
> **Correct path**: If a genuine decision point exists → invoke the full pipeline: `refactor-decision-memory` → `author-gate-packet-builder` → `author-gate-ui-renderer` → `ask_user_question`. If no genuine decision exists → continue execution per the Continuous Execution Invariant above.
>
> **Detection**: `post_cascade_author_gate_miss_detector.py` Signal 5 (`prose_options_menu`, weight +3) fires when ≥2 option-menu patterns appear without `DECISION_CAPTURED` or `AUTHOR_GATE_PACKET`.

## Bypass conditions (no Author-Gate needed)

Typos/whitespace/formatting · single correct solution (syntax/import error) · explicit unambiguous user directive · emergency rollback · auto-fixable lint.

## Silent-marker invariant

Every refactor-class decision MUST emit a `DECISION_CAPTURED:` marker — even when no options surfaced via `ask_user_question`. The seven trigger types: `architecture_choice`, `refactor_scope`, `anti_pattern`, `deletion_strategy`, `dependency_addition`, `test_strategy`, `error_handling`.

## Anti-Pattern Author-Gate Extension

Anti-patterns detected by the ADG burndown gate require the same Author-Gate pipeline with anti-pattern-specific extensions:

### Scope

| Pattern | Guardian Comment |
|---------|------------------|
| `magic_configuration` | `# guardian: allow-magic-configuration` |
| `silent_swallower` | `# guardian: allow-silent-swallower` |
| `global_mutation` | `# guardian: allow-global-mutation` |
| `direct_prompt_compilation` | `# guardian: allow-direct-prompt-compilation` |
| `config_with_logic` | `# guardian: allow-config-with-logic` |
| `path_fragility` | `# guardian: allow-path-fragility` |

**Format**: Hyphens only, module-level placement.

### Anti-Pattern Approval Protocol

When ADG burndown gate (`T3a`) detects new violations:

```python
ask_user_question(
    question=f"ADG detected {count} new anti-pattern violations. Select approach?",
    options=[
        {"label": "Approve All", "description": "Accept all violations with guardian comments. Pros: Unblocks work. Cons: Adds debt. ⭐ RECOMMENDED if unavoidable and documented."},
        {"label": "Reject All", "description": "Revert all changes. Pros: Zero debt. Cons: Work blocked. ⭐ RECOMMENDED if alternatives exist."},
        {"label": "Review Details", "description": "Show breakdown before deciding. Pros: Informed. Cons: Slower. ⭐ RECOMMENDED for first-time violations."}
    ]
)
```

**Commit prefix**: `Author-Gate-APPROVED: <count> anti-pattern violations`

### Integration

- `ops_scripts/ci/_adg_burndown_gate.py` — Violation detection
- `post_cascade_author_gate_audit.py` — Approval pipeline
- `.pre-commit-config.yaml` — T3a ratchet enforcement

---

## Where detail lives

AG-10 shape: `author-gate-packet-builder` skill. Triggers: `author-gate-decision-points.md`. SVP calibration: `author-gate-svp-calibration.md`. Precedent: `refactor-decision-memory` skill. Ledger: `.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite`. Bypass: `AUTHOR_GATE_STALE_BYPASS=1`.

## Calibration-driven triggers

Wilson CI evidence in `docs/reports/calibration/<YYYY-Www>.md` MAY require an Author-Gate when a band has `n ≥ 20` AND CI miss > 0.05, OR ≥2 bands mis-calibrated. Action: `decision_type=architecture_choice`. Smaller deltas auto-tune silently.

## Constitutional cross-reference

§6, §30. ADR-023 separates from runtime HITL.
