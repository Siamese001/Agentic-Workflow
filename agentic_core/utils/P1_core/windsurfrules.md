# WINDSURF RULES — HUMAN-READABLE CONSTITUTION

This document defines the **spirit, rationale, and human guidance** of the architecture.

## 1. THE PHYSICS (SSOT LAW)

**THE ONLY SOURCE OF TRUTH (SSOT) FOR HIERARCHY, DEPTHS, AND KEY MAPPINGS IS:**
The sovereign configuration blueprint (`structure_blueprint.py`).

- **Constraint**: Do not reference, repeat, or visualize the directory structure in this Markdown file.
- **MANDATORY**: Always execute the sovereign orchestration entry point (`sovereign_mission_control.py`) to maintain the "Eternal Circuit."

## 2. CANON KEY CONSOLIDATION

- The canon key system has been consolidated and is dynamically maintained via the blueprint.
- All validation, reporting, and healing operate on the current set of active keys.
- Legacy key numbers are internally remapped to current active ranges.
- **Mandatory**: Always query `ACTIVE_CANON_KEYS` from the blueprint to determine the current key range.

## 3. THE GRAVITY RULE (IMPORT WATERFALL)

- Sovereign layers (agentic_core, prompt_governance, schemas, scripts) are UPSTREAM.
- Domains (apps_rg, apps_lic) are DOWNSTREAM.
- Rule: UPSTREAM must NEVER import from DOWNSTREAM. If a core utility is needed in a domain, move it to apps_shared.

> **Rationale**: Prevents contamination of the sovereign core and ensures reusability.

## 4. CANON KEY ENFORCEMENT (SSOT ONLY)

- **Source of Truth**: The definition and mapping of active canon keys are located EXCLUSIVELY in the sovereign configuration blueprint.
- **Constraint**: NEVER hardcode key definitions, counts, or ranges in this Markdown file or any project asset.
- **Action**: Dynamically import and read `ACTIVE_CANON_KEYS` and `CANON_AGENT_REGISTRY` from the blueprint before any agent execution to determine the active laws.

## 5. AGENT DISCOVERY PROTOCOL

When creating new agents:

- Domain-specific agents (e.g., NarrativeLead) go to apps_rg/agents/.
- Framework-level agents (e.g., FissionManager) go to agentic_core/L3_orchestration/.
- Every __init__.py must be *Light* (No circular imports).

> **Heuristic**: If the agent uses domain-specific knowledge (e.g., resume scoring, license rules) -> domain folder.
> If it manages framework concerns (fission, healing, validation) -> agentic_core.

## 6. VOID COMPLIANCE

- No numbered folders (e.g., 01_logic).
- No single-child folders (e.g., folder/subfolder/file.py should be folder/file.py).
- File names must use high-signal keywords (agent, engine, manager, validator, healer, etc.).
- Forbidden: generic names like utils.py, helper.py, main.py, temp.py, script.py.

## 7. NEURAL LINK & ENVIRONMENT (THE PHYSICS)

- **Mandatory .env Check**: Before executing the sovereign orchestration entry point (`sovereign_mission_control.py`) or any agentic script, you MUST verify that the project root `.env` file exists and contains a valid `GEMINI_API_KEY` (or `GOOGLE_API_KEY`).
- **GEMINI-ONLY Policy**: Presence of OPENAI_API_KEY or ANTHROPIC_API_KEY in .env triggers immediate halt with warning (enforced by validator).
- **Pathing**: Always use `Path(__file__).parent / ".env"` or absolute project root paths to load variables. Never assume the current working directory.
- **Fail-Fast**: If *GEMINI_API_KEY* is missing or empty, STOP and alert the user. Do not attempt a "Dry Run" unless explicitly commanded.

## 8. MAINTENANCE DIRECTIVE

- Propose structural changes → update `structure_blueprint.py` first.
- **ETERNAL CIRCUIT**: Execute `sovereign_mission_control.py` to perform the full Audit -> Heal -> Verify cycle.
- **Zero-Tolerance**: A mission is only "Sealed" when the Sovereign Auditor returns a score of 100.0%.
- Update this file only when adding new human guidance or recording decisions.
