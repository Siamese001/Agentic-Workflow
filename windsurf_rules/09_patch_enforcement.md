# ==================================================================================================
# /windsurf_rules/09_patch_enforcement.md
# GLOBAL APPLY-PATCH ENFORCEMENT RULE
# ==================================================================================================
# PURPOSE:
#   This rule guarantees that Windsurf ALWAYS produces deterministic, patch-only outputs during
#   any Phase that requires changes to the repository. It prevents narrative drift, interactive
#   behavior, partial updates, and non-deterministic execution.

# =====================================================================
# SECTION 1 — PATCH-ONLY OUTPUT (MANDATORY)
# =====================================================================
Windsurf MUST treat every Phase prompt as a PATCH GENERATION REQUEST
unless the Phase is explicitly declared VALIDATION-ONLY.

When a Phase requires changes:
  • Windsurf MUST output ONLY:
        apply_patch blocks
        write_to_file blocks
  • NEVER narrative text outside patch blocks.
  • NEVER ask questions.
  • NEVER delay patch output.
  • NEVER partially apply changes.

Ambiguity rule:
  IF any part of the prompt could imply patches,
  Windsurf MUST assume:
        “PATCH REQUIRED → produce full diffs immediately.”

# =====================================================================
# SECTION 2 — APPLY_PATCH RULES
# =====================================================================
All apply_patch blocks MUST:
  • Use unified diff format.
  • Modify ONLY the files explicitly in-scope for the current Phase.
  • Contain syntactically valid changes.
  • Complete ALL intended modifications in one batch.

All write_to_file blocks MUST:
  • Create new files only.
  • Use absolute or fully-qualified paths as required by the simulation.
  • Auto-create missing directories as needed.

# =====================================================================
# SECTION 3 — PROHIBITED BEHAVIOR
# =====================================================================
Windsurf MUST NOT:
  • Output prose instead of patches.
  • Mix narrative and patch content.
  • Produce partial diffs.
  • Wait for confirmation.
  • Ask for clarification.
  • Create patches that depend on runtime state or execution.
  • Introduce placeholders (“TODO”, “STUB”, “pass”) unless explicitly required.

# =====================================================================
# SECTION 4 — DETERMINE COMPLETION BY PATCH SUCCESS
# =====================================================================
A Phase requiring patches is complete ONLY when:
  • All patch blocks have been emitted.
  • All modified files are syntactically valid.
  • No out-of-scope files were touched.
  • Patches satisfy the Phase's Completion Criteria.

# ==================================================================================================
# END FILE: 09_patch_enforcement.md
# ==================================================================================================
