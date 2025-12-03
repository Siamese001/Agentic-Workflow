=============================================================================
AGENTIC-WORKFLOW — HARDENED GLOBAL RULESET (REBUILT FOR PHASES 1–4)
=============================================================================
This ruleset is absolute. It overrides all defaults, all tools, all templates,
all heuristics, and governs the entire SubAtomic refactor.
=============================================================================
=============================================================================
0. DOCKER-ONLY EXECUTION MODEL
=============================================================================

• All execution MUST assume a Linux container.
• Allowed paths: /project_root/... only.
• Forbidden: Windows paths, Mac paths, host paths, mounted volumes.
• Any host path appearing in output MUST be auto-corrected.
• All FS operations MUST occur inside the containerized project root.
• No absolute host paths may ever appear in patches, scripts, imports, or logs.

=============================================================================
1. ROOT FOLDER IMMUTABILITY (SUBATOMIC MODEL)
=============================================================================

The ONLY allowed root-level contents:

01_agentic_core/
02_schemas/
03_runtime/
04_prompt_governance/
05_config/
06_data/
07_observability/
08_scripts/
09_apps/
10_tests/
sub-atomic-design.md
unified_structure_subatomic.yaml


Rules:
• No new root folders allowed.
• No new root files allowed (except user-approved edits to the YAML).
• Root folder names MUST NOT change.
• Any violation MUST trigger auto-repair.

=============================================================================
2. ROOT-LEVEL WRITE FORBIDDANCE
=============================================================================

Windsurf MUST NOT write anything to the repo root.

Forbidden at root:
• logs
• temporary files
• diffs
• snapshots
• execution reports
• pytest output
• coverage
• generated code
• text files
• migration plans
• caches

ALL outputs must be placed in their designated non-root folder per phase rules.
If a root artifact appears → immediate auto-correction.

=============================================================================
3. STRUCTURAL VALIDATION (PHASE 1 GOVERNANCE)
=============================================================================

Every patch cycle must validate:

• Root contains EXACTLY the 10 canonical folders + unified YAML.
• No extra root contents.
• No missing root contents.
• No renamed root contents.

If ANY deviation occurs:
• Windsurf MUST self-patch until clean.
• Patch loop MUST continue until root is pristine.

=============================================================================
4. OUTPUT REDIRECTION (PER-PHASE LOCATION RULES)
=============================================================================

ALL generated artifacts MUST be redirected as follows:

Artifact Type	Mandatory Destination
Phase 1 structural snapshots	06_data/phase1/ (NOT root)
Phase 2 merge manifests	06_data/phase2/
Phase 3 semantic cache	06_data/semantic_cache/
Phase 3 mutation reports	07_observability/reports/
Phase 4 validation logs	07_observability/validation/
Tests	10_tests/

Rules:
• NEVER root.
• NEVER outside the container.
• No implicit folder creation outside the 10 canonical areas.

=============================================================================
5. PHASE COMPLETION — ALL KEYS MUST PASS (PHASES 1–4 LOGIC)
=============================================================================

For each phase (1, 2, 3, 4):

Windsurf MUST evaluate ALL validation keys defined for that phase.

Must output:

K<n> = PASS
K<n> = FAIL


A phase cannot complete unless EVERY key is PASS.

ANY failed key MUST trigger auto-patching and re-validation.

Missing keys = FAIL.

On success, Windsurf MUST print:

PHASE VALIDATION COMPLETE — ALL KEYS PASS


This rule overrides ALL other stopping criteria.

=============================================================================
6. ZERO-LOSS GUARANTEE (MAPPED TO PHASES 1–4)
=============================================================================

Zero-loss rules mapped to the new workflow:

Phase 1 (Structure)

• MUST NOT modify content.
• Structure only.
• Only deletion allowed is structural cleaning of empty folders.
• No mutation of any file content allowed.

Phase 2 (Historical Merge)

• All legacy code MUST be captured.
• No code or comments may be lost.
• No destructive overwrite allowed outside canonical mapping.

Phase 3 (Semantic Mutation)

• Allowed: rewriting, refactoring, restructuring code only if semantics identical.
• Forbidden: deleting functionality, reducing coverage, or altering behavior.
• Every mutation MUST remain reversible (via transcript).

Phase 4 (Validation)

• No content changes allowed except minimal fixes required to pass:
– tests
– imports
– ruff
– mypy
– safety checks

This is the strictest zero-loss model.

=============================================================================
7. ABSOLUTE OVERRIDE CLAUSE
=============================================================================

This ruleset supersedes:
• prior Windsurf rules
• default toolchain rules
• templates
• heuristics
• auto-refactors
• linting behaviors
• file placement logic

Windsurf MUST obey this ruleset end-to-end for all phases and all patches.