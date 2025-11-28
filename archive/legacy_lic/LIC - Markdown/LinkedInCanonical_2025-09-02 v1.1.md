================================================================================
LINKEDIN OUTREACH – CANONICAL (Zero-Loss Overwrite — Reorganized & Hardened)
Version: 2025-09-02 (ND Patch applied, RAG directives relocated)
================================================================================

# SUMMARY (TL;DR)
- This file enforces single-line minimal prompts for runner execution, strict validation, two mandatory QA artifacts (LinkedIn Canonical QA Grid + AI Filter table), storage/audit conventions, signature/resume enforcement, dash/percent policies, and per-message-type RAG/evidence requirements.
- MPv5 shells: **only** used when a prompt is generated organically from instructions. Not required for standard LinkedIn runner flows.

--------------------------------------------------------------------------------
# TABLE OF CONTENTS
1) Governance & High-level Rules
2) Pre-run Validation & Audit Fields
3) Message Types (each with RAG / Evidence rules and output templates)
   - Short (NEW)
   - Recruiter (EXISTING)
   - Contact (EXISTING — Light RAG)
   - Executive (EXISTING — Robust RAG)
4) AI Filter Artifacts & Storage
5) Minimal Prompt Templates (verbatim)
6) Block / Fallback Conditions
7) Example Error Response
--------------------------------------------------------------------------------

## 1) GOVERNANCE & HIGH-LEVEL RULES
- Runner accepts a **single minimal prompt** line and either returns the message + mandatory artifacts or a single structured error (no spec dumps).
- MPv5 usage: **Only apply Master Prompts v5 shells when a prompt is generated organically from freeform user instructions.** The LinkedIn runner itself does not require MPv5 for routine runs.
- Dash policy: hyphen (ASCII minus) only — em dash/en dash/double-hyphen banned.
- Percent policy: normalize "percent" → "%".
- Region gating default: US or EU only. India or ambiguous → validation error.

--------------------------------------------------------------------------------
## 2) PRE-RUN VALIDATION & AUDIT FIELDS
- Required audit fields on pass: `is_existing`, `message_type`, `contact_category_user`, `contact_category_inferred`, `role_detector_match`, `contact_url`, `timestamp`.
- If validation fails, return JSON with `missing_fields`, `failed_checks`, `required_template_example`.
- Runner MUST compute character counts (for Short messages) and include them in metadata.

--------------------------------------------------------------------------------
## 3) MESSAGE TYPES — OUTPUT TEMPLATES + RAG / EVIDENCE DIRECTIVES
(Each message type below contains its RAG/evidence requirements immediately after the output template.)

--- SHORT MESSAGE (NEW — Unconnected) -----------------------------------------
Purpose: secure a connection from an unconnected profile quickly.

Minimal prompt template:
NEW | Short | ContactURL | FirstName | JobTitle | Company | WhyCompany (one clause) | WhyRole (one clause) | FitLine (one sentence with metric) | BaseResume

Output body (example form — runner substitutes fields):
[LinkedIn URL]
Hi [First Name], I recently applied for the [Job Title] at [Company]. I am excited by [why Company] and see the role as a chance to [why Role]. My experience in [concrete value] aligns well. Open to connect? Regards, Amit Ayer

Rules:
- Character length: **290–310** characters (runner computes and returns actual char count).
- Block if missing WhyCompany or WhyRole.
- Dash / percent normalization applied.

RAG / Evidence Directive (SHORT):
- Evidence: NOT required beyond FitLine metric.
- Save LinkedIn Canonical QA Grid (8 checks) + AI Filter canonical table (1–13).
- Store artifacts to evidence path (see §4).

--- RECRUITER (EXISTING) -----------------------------------------------------
Purpose: follow-up with a recruiter; higher operational details; must include resume line.

Minimal prompt template:
EXISTING | Recruiter | ContactURL | FirstName | JobTitle | Company | WhyCompany (one clause) | WhyRole (one clause) | 3FitBullets (pipe-separated) | ResumeChoice | CallAsk

Output body (example):
Subject: Quick follow-up on [Role Name]

Hi [First Name],

Thanks for connecting and your note regarding the [Role Name] at [Company]. I am excited by [why Company] and am interested in the [Role Name] scope to [why Role].

Given your emphasis on [JD requirement or recruiter insight], here are three immediate ways I can contribute:
- [Concrete achievement aligned to JD with metric]
- [Tangible result mapped to recruiter’s insight]
- [Outcome demonstrating collaboration or credibility]

My resume is attached for your convenience.

Would you be open to a brief call?

Regards,

Amit Ayer
amitayer1@gmail.com
+1-917-239-3830
https://www.linkedin.com/in/amitayer1/

Rules:
- The exact sentence "My resume is attached for your convenience." is required (signature/resume enforcement).
- Signature block must follow canonical order and appear inside message body.
- BLOCK on em/en/double-dash.

RAG / Evidence Directive (RECRUITER):
- RAG level: **Light** — provide 1–2 sourceable recruiter insights (if available).
- Evidence pack: attach minimal RAG pack (source lines/IDs) used to craft 3FitBullets.
- Save LinkedIn Canonical QA Grid (8 checks) + AI Filter canonical table (1–13) + RAG evidence pack to evidence path.

--- CONTACT (EXISTING — LIGHT RAG) ------------------------------------------
Purpose: outreach to an existing contact (non-executive), with light RAG evidence.

Minimal prompt template:
EXISTING | Contact-LightRAG | ContactURL | FirstName | JobTitle | Company | Insight1 | Insight2 | ResumeChoice | Ask (e.g., 15 min)

Output body (example):
Subject: Quick follow-up and brief introduction

Hi [First Name],

Thanks again for connecting. I am drawn to [why Company] and see the [Role Name] as a chance to [why Role]. Your recent [insight #1] and [insight #2] map directly to the JD focus on [JD requirement #1] and [JD requirement #2]. For [insight #1], I delivered [achievement with metric]. For [insight #2], I drove [measurable result]. Could we schedule a brief 15-minute call?

Regards,

Amit Ayer
amitayer1@gmail.com
+1-917-239-3830
https://www.linkedin.com/in/amitayer1/

Rules:
- Requires at least **2** sourceable insights. BLOCK if <2 or if deduplication fails.
- Deduplication: message must add net-new content vs prior outreach.

RAG / Evidence Directive (CONTACT — LIGHT RAG):
- RAG level: **Light RAG** — include two sourceable insights (dateable when possible).
- Evidence pack: include short citations (URL + quote line) for Insight1 and Insight2.
- Save QA Grid + AI Filter table + Light RAG evidence to evidence path.

--- EXECUTIVE (EXISTING — ROBUST RAG) ---------------------------------------
Purpose: high-seniority outreach requiring robust sourcing and tactical value.

Minimal prompt template:
EXISTING | Executive-RobustRAG | ContactURL | FirstName | Title | Company | ExecInsight1 (dated/sourceable) | ExecInsight2 (dated/sourceable) | TwoResumeMappings (brief) | EvidenceReq (yes/no) | Ask (e.g., 15 min)

Output body (example):
Subject: Accelerating [Executive’s Priority]

Hi [First Name],

I appreciated your [dated exec insight #1] and [dated exec insight #2]. I am excited by [why Company] and the [Role Name] mandate to [why Role]. On [insight #1], I led [quantified outcome]. On [insight #2], my teams delivered [explicit result]. A practical lever to consider is [non-obvious tactic from deep research]. Would you be open to a brief strategy discussion?

Regards,

Amit Ayer
amitayer1@gmail.com
+1-917-239-3830
https://www.linkedin.com/in/amitayer1/

Rules:
- Requires **≥2 dated/sourceable executive insights** (must be attributable).
- Executive flows **must not** include a resume line. BLOCK if resume sentence present.
- Dedup check required.

RAG / Evidence Directive (EXECUTIVE — ROBUST RAG):
- RAG level: **Robust RAG** — supply full evidence pack (source links, excerpt lines, dates).
- Evidence pack must include provenance metadata (source, date, snippet).
- Save QA Grid + AI Filter table + full Robust RAG evidence to evidence path.

--------------------------------------------------------------------------------
## 4) AI FILTER ARTIFACTS & STORAGE (MANDATORY)
- After the message body the runner must emit in this exact order:
  1) LinkedIn Canonical QA Grid (8 checks)
  2) AI Filter canonical table (checks 1–13)
- AI Filter template (1–13):
  1. Clarity: PASS/FAIL
  2. Specificity: PASS/FAIL
  3. Quantification: PASS/FAIL
  4. Relevance to Role/JD: PASS/FAIL
  5. Action-Oriented Ask: PASS/FAIL
  6. Conciseness: PASS/FAIL
  7. Keyword Integration: PASS/FAIL
  8. Structure & Formatting: PASS/FAIL
  9. Region & Role Gating: PASS/FAIL
 10. Dash/Character Policy Check: PASS/FAIL
 11. Deduplication Check: PASS/FAIL
 12. RAG / Evidence Present: PASS/FAIL
 13. Signature & Compliance: PASS/FAIL

Storage instructions:
- Save artifacts to `msc/evidence/<company>_<appid_or_versioned_resume>/<contact_slug>/<ISO8601_timestamp>/`
- Include SHA256 for each artifact and set `ai_filter_table_path`, `ai_filter_summary_path`, `ai_filter_table_sha256`, `ai_filter_summary_sha256` in message audit metadata.

--------------------------------------------------------------------------------
## 5) MINIMAL PROMPT TEMPLATES (VERBATIM — DO NOT ALTER)
1) NEW | Short (Unconnected)  
`NEW | Short | ContactURL | FirstName | JobTitle | Company | WhyCompany (one clause) | WhyRole (one clause) | FitLine (one sentence with metric) | BaseResume`

2) EXISTING | Contact-LightRAG  
`EXISTING | Contact-LightRAG | ContactURL | FirstName | JobTitle | Company | Insight1 (sourceable one-line) | Insight2 (sourceable one-line) | ResumeChoice | Ask (e.g., 15 min)`

3) EXISTING | Recruiter  
`EXISTING | Recruiter | ContactURL | FirstName | JobTitle | Company | WhyCompany (one clause) | WhyRole (one clause) | 3FitBullets (pipe-separated, each 1 short sentence with metric) | ResumeChoice | CallAsk`

4) EXISTING | Executive-RobustRAG  
`EXISTING | Executive-RobustRAG | ContactURL | FirstName | Title | Company | ExecInsight1 (dated/sourceable) | ExecInsight2 (dated/sourceable) | TwoResumeMappings (brief) | EvidenceReq (yes/no) | Ask (e.g., 15 min)`

--------------------------------------------------------------------------------
## 6) BLOCK / FALLBACK CONDITIONS (summary)
Block if any of:
- Region invalid/ambiguous (India included)
- Missing or non-canonical LinkedIn URL
- Short Message length outside 290–310 chars
- Missing "WhyCompany" or "WhyRole"
- Insufficient attributable insights for EXISTING flows
- Deduplication failure
- Dash policy violations
- Resume line present in Executive message
Fallback: return structured JSON error; optionally suggest corrected minimal prompt.

--------------------------------------------------------------------------------
## 7) EXAMPLE MINIMAL ERROR RESPONSE
```json
{
  "status": "error",
  "missing_fields": ["WhyCompany","WhyRole"],
  "failed_checks": ["Region gating"],
  "required_template_example": "NEW | Short | https://www.linkedin.com/in/jdoe | Jane | Sr. Program Manager, Insurance | Uber | I admire Uber's data-driven scale | to modernize actuarial & claims | Led 12 initiatives cutting claims cycle 30% | Prof Services AI Resume.pdf"
}
