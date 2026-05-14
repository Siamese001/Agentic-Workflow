# apps_rg Agentic Spine

> **CANONICAL_PA**: This document defines the canonical Prompt Assembly (PA) governance model for the apps_rg (Resume Generation) application domain.

## Overview

The apps_rg application uses a governed 8-slot Prompt Assembly model to ensure safe, verifiable, and deterministic resume generation. All prompts are compiled at build-time, not runtime.

## 8-Slot Authority Model

| Slot | Authority | Description | Source |
|------|-----------|-------------|--------|
| S0 | SYSTEM | Governance preamble, NO FABRICATION oath | Template |
| D0 | BINDING | Security fences, origin boundaries | Template |
| I0 | GOVERNED | Domain instructions for tailoring | Template |
| C0 | INFORMATIONAL | Evidence data (source-separated) | Candidate Facts + JD |
| E0 | EXAMPLE | Approved resume examples | User Provided |
| Y0 | STYLE | Synthesis preferences (advisory) | User Provided |
| U0 | ZERO | User intent only | User Task |
| R0 | SCHEMA | Output contract schema | Template |

## Canonical PA Registry

The source of truth for all PA templates is at:
```
apps_rg/prompt_assembly/prompt_registry.yaml
```

This registry defines:
- Valid template IDs and versions
- Slot ordering per template
- Required vs optional slots
- Compilation constraints
- Forbidden behaviors
- Validation rules

## Compilation Constraints

- **Max tokens**: 4000-6000 depending on template
- **Output format**: JSON only
- **Slot order**: Enforced (S0 > D0 > I0 > C0 > E0 > Y0 > U0 > R0)
- **Hash determinism**: Required for replay/verification

## Governance Invariants

1. **NO FABRICATION Oath**: S0 must contain explicit "NO FABRICATION" statement
2. **Source Separation**: C0 evidence must be tagged with source (candidate_facts, jd_requirements, company_brief, alignment_map)
3. **Schema Compliance**: Output must validate against R0 schema reference
4. **Deterministic Compilation**: Same input must produce identical hash

## Fail-Closed Behavior

The PA compiler fails closed on:
- Missing required slots (MISSING_REQUIRED_SLOT)
- Unknown template ID (UNKNOWN_TEMPLATE_ID)
- Missing NO FABRICATION oath (MISSING_NO_FABRICATION_OATH)
- Missing source tags on C0 evidence (C0_MISSING_SOURCE_TAG)
- Lower-authority override attempts (OVERRIDE_ATTEMPT_DETECTED)

## W11 Runtime Wiring (Future Scope)

Integration with L0/L1/L2 runtime is explicitly **NOT** in W10 scope. The PA layer remains:
- Compile-time only
- Pure functions
- Zero side effects
- No provider calls

Runtime dispatch to LLM providers is a W11 concern and will be handled via the UWG/L4 layer per ADR-023.

## Version

- **W10**: 2026-05-14
- **Canonical PA Version**: W10-2026-05-14
- **Template Versions**: 1.0.0 (all templates)
