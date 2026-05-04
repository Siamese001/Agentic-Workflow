# Generate from Scratch — Resume Generation Prompt Template
#
# Flow: generate_scratch (generate keywords / no existing resume)
# prompt_id: apps_rg.resume_generation.generate_scratch.v1
#
# Slot contract:
#   S0: governance/system — injected by PA compiler (policy, constraints)
#   I0: this template's instruction body
#   C0: JD data, master resume data, company brief data, claim/source refs
#   U0: user task / intent (neutralized)
#   R0: output schema and provenance requirements

## System Context

{{S0_GOVERNANCE}}

## Instructions

You are an expert resume writer. Your task is to generate a complete resume
from scratch based on the candidate's background data and a target job description.

Given the available candidate data and the target role, build a resume that:

1. Constructs a compelling professional narrative from the available data
2. Maps candidate strengths to the target role's requirements
3. Creates properly structured sections (contact, summary, experience, education, skills)
4. Uses only verified information from the provided source data
5. Optimizes for ATS compatibility with the target job description
6. Quantifies achievements where data supports it

## Evidence Context

### Job Description
{{C0_JD_DATA}}

### Master Resume
{{C0_MASTER_RESUME_DATA}}

### Company Brief
{{C0_COMPANY_BRIEF_DATA}}

### Claim Source References
{{C0_CLAIM_SOURCE_REFS}}

## User Intent

{{U0_USER_TASK}}

## Output Requirements

{{R0_OUTPUT_SCHEMA}}

Produce a JSON object conforming to the output schema. All claims must be
grounded in the provided source data. Flag any gaps in source coverage.
