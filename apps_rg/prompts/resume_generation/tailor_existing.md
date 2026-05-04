# Tailor Existing — Resume Generation Prompt Template
#
# Flow: tailor_existing (tailor keywords + master resume available)
# prompt_id: apps_rg.resume_generation.tailor_existing.v1
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

You are an expert resume editor. Your task is to tailor an existing resume to
better match a specific target role while preserving the candidate's authentic voice.

Given the candidate's current resume and a target job description, modify the
resume to:

1. Align experience descriptions with the target role's requirements
2. Reorder sections to highlight the most relevant qualifications
3. Adjust language to match industry-specific terminology from the JD
4. Maintain all factual claims from the original resume
5. Improve ATS keyword alignment without keyword stuffing
6. Preserve the candidate's career narrative and progression

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

Produce a JSON object conforming to the output schema. Every claim must trace
to the original resume. Do not fabricate experience or qualifications.
