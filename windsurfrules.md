# ARCHITECTURE GOVERNOR (Key 40) - SYSTEM DIRECTIVES

## 1. THE PHYSICS (ASCII FOLDER TREE)

You must strictly maintain and validate this hierarchy:

- agentic_core/ (L1-L5): Sovereign Brain. NO imports from apps_*.
- prompt_governance/: Sovereign Law. Markdown personas (Keys 11-30).
- schemas/: Sovereign Contracts. JSON/Pydantic (Keys 31-39).
- apps_shared/: Infrastructure. Utils shared across domains.
- apps_rg/: Domain A (Resume Generation). Specific agent logic.
- apps_lic/: Domain B (Licensing). Compliance agent logic.

## 2. THE GRAVITY RULE (IMPORT WATERFALL)

- Sovereign layers (agentic_core, prompt_governance, schemas) are UPSTREAM.
- Domains (apps_rg, apps_lic) are DOWNSTREAM.
- Rule: UPSTREAM must NEVER import from DOWNSTREAM. If a core utility is needed in a domain, move it to apps_shared.

## 3. KEY-TO-FOLDER ENFORCEMENT

- Key 0: Root files only (pyproject.toml, canon_validator_agentic_v2.py).
- Key 11: Surgeon Persona -> prompt_governance/personas/architectural/
- Key 31: Fission Blueprint -> schemas/canon/blueprints/
- Key 40: Core Logic -> agentic_core/

## 4. AGENT DISCOVERY PROTOCOL

When creating new agents:

- Domain-specific agents (e.g., NarrativeLead) go to apps_rg/agents/.
- Framework-level agents (e.g., FissionManager) go to agentic_core/L3_orchestration/.
- Every __init__.py must be "Light" (No circular imports).

## 5. VOID COMPLIANCE

- No numbered folders (e.g., 01_logic).
- No single-child folders (e.g., folder/subfolder/file.py should be folder/file.py).

## 6. NEURAL LINK & ENVIRONMENT (THE PHYSICS)

- **Mandatory .env Check**: Before executing `canon_validator_agentic_v2.py` or any script in `agentic_core`, you MUST verify that the `.env` file exists in the root directory and contains a valid `GEMINI_API_KEY`.
- **Pathing**: Always use `Path(__file__).parent / ".env"` or absolute project root paths to load variables. Never assume the current working directory.
- **Fail-Fast**: If `GEMINI_API_KEY` is missing or empty, STOP and alert the user. Do not attempt a "Dry Run" unless explicitly commanded.
