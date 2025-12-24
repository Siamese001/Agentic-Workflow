# WINDSURF RULES — HUMAN-READABLE CONSTITUTION

This document defines the **spirit, rationale, and human guidance** of the architecture.

All **machine-enforceable structural facts** (folder hierarchy, depths, key mappings, forbidden folders) are defined exclusively in:

```
agentic_core/config/P1_core/structure_blueprint.py
```

Do NOT duplicate enforceable details here — they will drift.

Update this file only for new guidance, rationale, or architectural decisions.

## CANON KEY CONSOLIDATION — December 24, 2025

- The 50-key system has been officially consolidated to **19 active keys (0–18)**.
- All validation, reporting, and healing now operate exclusively on this range.
- Legacy key numbers (e.g., old Key 50) are internally remapped.

## 1. THE PHYSICS (ASCII FOLDER TREE)

You must strictly maintain and validate this hierarchy:

 

- agentic_core/ (L1-L5): Sovereign Brain. NO imports from apps_*.
- prompt_governance/: Sovereign Law. Markdown personas (Keys 1–6).
- schemas/: Sovereign Contracts. JSON/Pydantic (Keys 7–10).
- apps_shared/: Infrastructure. Utils shared across domains (Key 14, 16).
- apps_rg/: Domain A (Resume Generation). Specific agent logic (Key 15).
- apps_lic/: Domain B (Licensing). Compliance agent logic (Key 15).
- scripts/: Sovereign Operations. Root-level utility scripts (Key 18).

 

> **Note**: This is a high-level human overview. The absolute source of truth for folder structure,
> depths, and allowed subfolders is *structure_blueprint.py* (SSOT). Run *canon_validator_agentic_v2.py*
> to verify current physical compliance.

## 2. THE GRAVITY RULE (IMPORT WATERFALL)

- Sovereign layers (agentic_core, prompt_governance, schemas, scripts) are UPSTREAM.
- Domains (apps_rg, apps_lic) are DOWNSTREAM.
- Rule: UPSTREAM must NEVER import from DOWNSTREAM. If a core utility is needed in a domain, move it to apps_shared.

> **Rationale**: Prevents contamination of the sovereign core and ensures reusability.

## 3. CANON KEY ENFORCEMENT (Active Keys 0–18)

- Key 0:  Root sovereign files
- Key 1:  Architectural Personas
- Key 2:  Operational Personas
- Key 3–4: Prompt directives (instructional/negative)
- Key 5–6: Security guardrails
- Key 7–10: Schema contracts (blueprints, reports, APIs)
- Key 11: Core cognition & strategy
- Key 12: Orchestration & routing
- Key 13: Persistent state
- Key 14–16: Shared & domain infrastructure
- Key 17: Testing
- Key 18: Operational tools

## 4. AGENT DISCOVERY PROTOCOL

When creating new agents:

- Domain-specific agents (e.g., NarrativeLead) go to apps_rg/agents/.
- Framework-level agents (e.g., FissionManager) go to agentic_core/L3_orchestration/.
- Every __init__.py must be *Light* (No circular imports).

> **Heuristic**: If the agent uses domain-specific knowledge (e.g., resume scoring, license rules) → domain folder.
> If it manages framework concerns (fission, healing, validation) → agentic_core.

## 5. VOID COMPLIANCE

- No numbered folders (e.g., 01_logic).
- No single-child folders (e.g., folder/subfolder/file.py should be folder/file.py).
- File names must use high-signal keywords (agent, engine, manager, validator, healer, etc.).
- Forbidden: generic names like utils.py, helper.py, main.py, temp.py, script.py.

## 6. NEURAL LINK & ENVIRONMENT (THE PHYSICS)

- **Mandatory .env Check**: Before executing `canon_validator_agentic_v2.py` or any script in `agentic_core`, you MUST verify that the `.env` file exists in the root directory and contains a valid `GEMINI_API_KEY`.
- **GEMINI-ONLY Policy**: Presence of OPENAI_API_KEY or ANTHROPIC_API_KEY in .env triggers immediate halt with warning (enforced by validator).
- **Pathing**: Always use `Path(__file__).parent / ".env"` or absolute project root paths to load variables. Never assume the current working directory.
- **Fail-Fast**: If *GEMINI_API_KEY* is missing or empty, STOP and alert the user. Do not attempt a "Dry Run" unless explicitly commanded.

## 7. MAINTENANCE DIRECTIVE

- Propose structural changes → update `structure_blueprint.py` first.
- Then run `canon_validator_agentic_v2.py` to validate.
- Update this file only when adding new human guidance or recording decisions.
