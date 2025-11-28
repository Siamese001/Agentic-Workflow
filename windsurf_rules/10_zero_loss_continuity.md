# ==================================================================================================
# /windsurf_rules/10_zero_loss_continuity.md
# GLOBAL ZERO-LOSS PROMPT & RULE CONTINUITY GUARANTEE
# ==================================================================================================
# PURPOSE:
#   This rule ensures that Windsurf NEVER forgets, overrides, weakens, or discards ANY previously
#   established rule files, global templates, architectural constraints, or public API requirements.
#   All rules accumulate over time, enabling arbitrarily long multi-phase workflows.

# =====================================================================
# SECTION 1 — ZERO-LOSS MEMORY & RULE CONSISTENCY
# =====================================================================
Windsurf MUST preserve:
  • ALL global Windsurf rule files (00–99).
  • ALL global templates (e.g., nuclear templates, scaffolding templates).
  • ALL architectural constraints (L1–L5, DAG, import matrix, layering invariants).
  • ALL public APIs defined in ANY Phase.
  • ALL constraints from earlier Phases.
  • ALL directory and module topologies defined earlier.
  • ALL safety and governance constraints.

No rule may be forgotten or silently ignored.

# =====================================================================
# SECTION 2 — ADDITIVE RULE MODEL
# =====================================================================
All new Phase prompts MUST be interpreted as ADDITIVE:
  • New instructions ADD to existing constraints.
  • Existing constraints MUST remain in force.
  • If conflicts arise:
        Windsurf MUST apply the STRICTEST rule.
  • Nothing may “reset” the environment unless the user explicitly issues:
        RESET WINDSURF

# =====================================================================
# SECTION 3 — PROMPT CONTINUITY GUARANTEE
# =====================================================================
Windsurf MUST:
  • Merge all new constraints with previous ones.
  • NEVER weaken or remove prior rules.
  • ALWAYS maintain cumulative context for all Phases.
  • Maintain stable semantics across long multi-phase workflows
    (2 phases, 10 phases, or 50 phases).

# =====================================================================
# SECTION 4 — PROHIBITED BEHAVIOR
# =====================================================================
Windsurf MUST NOT:
  • Discard prior rules.
  • Replace global templates.
  • Override or downgrade architectural constraints.
  • Alter layering rules unless explicitly commanded.
  • Collapse public APIs or rename them without explicit instruction.

# =====================================================================
# SECTION 5 — CONTINUITY COMPLETION CRITERIA
# =====================================================================
This rule is satisfied only when:
  • All future Phase prompts inherit ALL prior rules fully.
  • No contradictions exist.
  • Windsurf applies the strictest constraint where multiple apply.
  • No rule is lost, rewritten, ignored, or superseded without explicit user direction.

# ==================================================================================================
# END FILE: 10_zero_loss_continuity.md
# ==================================================================================================
