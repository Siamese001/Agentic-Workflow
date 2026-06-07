
<!-- Converted from `.claude/rules/author-gate-enforcement.md`. Original Cursor trigger: `always_on`. -->

# Author-Gate Enforcement — Invariant-Only Stub

> **Terminology**: Governs **Author-Gate Decisions** (developer-loop / harness-side, per ADR-023). NOT runtime HITL (v30 step [5] in `agentic_core/L5_safety/`). Historical `HITL_PACKET:` markers retain legacy names.

> **Packet shape SSOT**: `.claude/schemas/author_gate_packet.schema.json`. This rule defines *when to fire* and *score discipline*; field-level shape defers to the schema.

## Pipeline (Tier 1 — do not duplicate here)

When facing an author-gate decision point, follow **`.claude/rules/003-cursor-author-gate-hitl.md`** (always-on). This rule adds emitter/schema enforcement, continuous-execution discipline, anti-pattern extensions, and calibration — not a second pipeline.

**Four-requirement contract** (enforced on every surfaced option): clickable via `ask_user_question`; confidence prefix; ` · trade-off:` segment; exactly one `⭐` on the leading option.

**Pipeline completion:** every `AUTHOR_GATE_PACKET:` MUST be followed by `ask_user_question` in the **same response** (`post_cursor_agent_author_gate_pipeline_audit.py`). **Bypass:** `AG_PIPELINE_AUDIT_BYPASS=1`.

## Canonical-emitter invariant

> ⛔ `AUTHOR_GATE_PACKET:` MUST be produced by `.claude/skills/author-gate-packet-builder/emit_packet.py`. Hand-crafting is FORBIDDEN — the emitter is the SSOT for AG-10 shape. Hand-crafted packets omit fields that `post_cursor_agent_author_gate_capture.py` keys on, causing ledger misses and stale-ledger CI violations (§30).

**Required pipeline**: `refactor-decision-memory` → `author-gate-packet-builder` → `author-gate-ui-renderer` → `ask_user_question` → `DECISION_CAPTURED:` marker.

**Enforcement**: `post_cursor_agent_author_gate_schema_audit.py`, `post_cursor_agent_author_gate_ui_audit.py`. **Bypass**: `AUTHOR_GATE_SCHEMA_BYPASS=1`.

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
> **Detection**: `post_cursor_agent_author_gate_miss_detector.py` Signal 5 (`prose_options_menu`, weight +3) fires when ≥2 option-menu patterns appear without `DECISION_CAPTURED` or `AUTHOR_GATE_PACKET`.

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
        {"label": "⭐ Recommended — Approve All", "description": "[RECOMMENDED ⭐ confidence=0.82] · trade-off: Unblocks work quickly but adds guardian debt to the burndown ledger"},
        {"label": "Reject All", "description": "[confidence=0.71] · trade-off: Zero new debt but blocks the current change set until reworked"},
        {"label": "Review Details", "description": "[confidence=0.68] · trade-off: Informed breakdown before deciding but slows the current wave"}
    ]
)
```

**Commit prefix**: `Author-Gate-APPROVED: <count> anti-pattern violations`

### Integration

- `ops_scripts/ci/_adg_burndown_gate.py` — Violation detection
- `.claude/hooks/after_agent_governance_dispatch.py` — Post-agent capture + AG audit chain (not `post_cursor_agent_author_gate_audit.py`, obsolete)
- `.pre-commit-config.yaml` — T3a ratchet enforcement

---

## Where detail lives

AG-10 shape: `author-gate-packet-builder` skill. Triggers: `author-gate-decision-points.md`. SVP calibration: `author-gate-svp-calibration.md`. Precedent: `refactor-decision-memory` skill. Ledger: `.claude/state/refactor_decisions/refactor_decision_ledger.sqlite`. Bypass: `AUTHOR_GATE_STALE_BYPASS=1`.

## Calibration-driven triggers

Wilson CI evidence in `docs/reports/calibration/<YYYY-Www>.md` MAY require an Author-Gate when a band has `n ≥ 20` AND CI miss > 0.05, OR ≥2 bands mis-calibrated. Action: `decision_type=architecture_choice`. Smaller deltas auto-tune silently.

## Constitutional cross-reference

§6, §30. ADR-023 separates from runtime HITL.
