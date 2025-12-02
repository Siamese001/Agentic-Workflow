# =============================================================================
# AGENTIC-WORKFLOW — HARDENED GLOBAL RULESET (FULL ZERO-LOSS OVERWRITE)
# =============================================================================
# This ruleset is ABSOLUTE. It overrides ALL system defaults, templates,
# reasoning heuristics, and tool behavior in Windsurf.
#
# It merges:
#   • Root Folder Immutability
#   • Docker-Only Execution Model
#   • Output Redirection
#   • Phase Completion: ALL KEYS MUST PASS
#   • Zero-Loss Guarantee
#   • Protection Against Accidental FS Mutation
# =============================================================================



# =============================================================================
# 0. DOCKER-ONLY EXECUTION (MANDATORY, ABSOLUTE)
# =============================================================================
Windsurf MUST assume **all Agentic-Workflow runs occur INSIDE a Docker container**.

Forbidden:
  • Windows paths (C:\..., D:\..., \Users\...)  
  • Mac paths (/Users/...)  
  • Host paths (/mnt/host, /Volumes, etc.)  
  • Any reference to the host filesystem  
  • Any command, script, or code generation that assumes host execution

Required:
  • ALL paths MUST be Linux-style (`/`)
  • ALL FS operations MUST target the container’s project root
  • NO absolute host paths may appear in any output
  • ANY such path MUST trigger immediate auto-correction

This rule overrides ANY other directive.



# =============================================================================
# 1. ROOT FOLDER IMMUTABILITY (ABSOLUTE OVERRIDE)
# =============================================================================
The ONLY allowed root contents of Agentic-Workflow are:

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

  unified_structure_subatomic.yaml

NOTHING else may exist at root.



# =============================================================================
# 2. ROOT-LEVEL WRITE FORBIDDANCE
# =============================================================================
Windsurf MUST NOT:

  • write ANY file to repo root  
  • create ANY directory at root  
  • output test results / pytest cache / coverage data to root  
  • write logs, reports, dumps, snapshots, diffs to root  
  • write temporary files or temp directories to root  
  • write build artifacts or freeze reports to root  
  • write JSON/YAML/MD/TXT/PY to root  
  • auto-generate code in root  
  • rename or delete the 10 canonical root folders  
  • modify unified_structure_subatomic.yaml unless user explicitly requests  
  • create ANY additional root-level paths

If Windsurf generates ANY root-level artifact → **it MUST auto-correct.**



# =============================================================================
# 3. ROOT CLEANLINESS VALIDATION (MANDATORY)
# =============================================================================
Before and after ANY patch:

  • Windsurf MUST scan the root directory  
  • MUST confirm the root contains EXACTLY the 10 folders + unified_structure_subatomic.yaml  
  • If ANY additional file or folder exists →  
        → Windsurf MUST patch until the root is pristine again  
  • Root-level contamination is a hard STOP condition (autofix required)



# =============================================================================
# 4. OUTPUT REDIRECTION (GLOBAL)
# =============================================================================
All generated artifacts MUST be placed ONLY inside the correct folder:

  • Phase 1A outputs → inside the target root  
  • Phase 1B migration plan → 02_schemas/  
  • Phase 1C execution reports → NOT root; inside designated folder only  
  • Phase 1D freeze reports → inside the specific target root only  
  • Semantic cache → 06_data/semantic_cache/  
  • Tests → 10_tests/

NEVER root.  
NEVER outside container context.  
NO EXCEPTIONS.



# =============================================================================
# 5. PHASE COMPLETION RULE — EVERY KEY MUST PASS
# =============================================================================
For ANY phase (0.5, 1A, 1B, 1C, 1D):

1. Windsurf MUST evaluate EVERY validation key K1…Kn  
2. MUST print a validation document:

       K<n> = PASS
       K<n> = FAIL

3. A phase CANNOT complete unless **EVERY** key prints EXACTLY:

       K<n> = PASS

4. If ANY key fails:
   • Windsurf MUST auto-patch  
   • MUST re-run validation  
   • MUST re-print the PASS/FAIL table  
   • MUST NOT ask questions  
   • MUST NOT stop early  
   • MUST NOT summarize prematurely  
   • MUST NOT claim completion  

5. Missing keys = FAIL and MUST trigger autofix.

6. Once ALL keys PASS, Windsurf MUST print:

       "PHASE VALIDATION COMPLETE — ALL KEYS PASS"

This rule OVERRIDES ALL other stopping criteria.



# =============================================================================
# 6. ZERO-LOSS GUARANTEE (MANDATORY)
# =============================================================================
Windsurf MUST NOT:

  • lose code  
  • lose comments  
  • delete files unless allowed strictly by the phase  
  • rename/move files outside 1C atomic execution  
  • modify any file content in 1A, 1B, or 1D  
  • perform destructive operations outside phase 1C

All changes MUST be deterministic, reversible (if required), and container-safe.



# =============================================================================
# 7. ABSOLUTE OVERRIDE
# =============================================================================
This ruleset supersedes ALL:
  • default Windsurf rules  
  • system behaviors  
  • templates  
  • tools  
  • code-generation heuristics  
  • test behaviors  
  • linting defaults

Windsurf MUST obey 100% of this ruleset at ALL times.
