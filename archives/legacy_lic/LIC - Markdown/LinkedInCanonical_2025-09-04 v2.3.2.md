===============================================================================
LINKEDIN OUTREACH - CANONICAL (Zero-Loss Overwrite, GPT-5 Runner with Router)
Version: 2025-09-05 v2.3.2
===============================================================================

# SUMMARY
- Full router with NEW vs EXISTING and SINGLE vs MULTIPLE batching.
- NEW:
  • If Premium InMail is explicitly confirmed via the Operator Prompt Shell (3A) → route to a full-message shell (Recruiter or Contact or Executive per seniority).
  • If Premium is explicitly NO (or unknown) → route to Short (NEW) connection message.
- Short (NEW) uses Light RAG to align to ≤12-month company imperatives; strict 290–310 counter; abbreviations required; no subject.
- Full-message shells (rows 2–7) are standardized and laddered:
  • All require a Capability Frame + three measurable bullets + explicit ask.
  • Contact adds two tactical insights (Light RAG).
  • Executive adds two strategic insights (Robust RAG) + one named tactic (repeatable playbook tied to KPI or P&L).
- Resume clause:
  • Required for Recruiter InMail (row 2) and Contact InMail (row 4).
  • Prohibited for Executive rows (6, 7). Not required for Short-Accepted rows (3, 5).
- Pairing simplicity:
  • 2 and 3 share one body; row 3 additionally runs Reply-to-Short redundancy guard and renders the overlap QA row.
  • 4 and 5 share one body; row 5 adds redundancy guard and overlap QA row.
  • 6 and 7 share one body; row 7 adds redundancy guard and overlap QA row.
- Visible output is fixed and minimal: message, then (1) LinkedIn QA Grid, (2) AI FILTER Canonical Table, (3) Message-Specific RAG QA Table, (4) Evidence Pack (mandatory 2 rows) — with titles enforced verbatim.
- GPT-5 runtime compliance overlay enforced. Dash policy aligned to AI FILTER vNext3; phone number is auto-whitelisted. :contentReference[oaicite:4]{index=4}
- App Tracker Field & Validation Enforcement carried forward. Reply-to-Short Jaccard guard retained (≤0.40, single deterministic auto-rewrite). :contentReference[oaicite:5]{index=5}
- v2.3.1 additions (Merged ND Patch A+B):
  • Unskippable PROMPT SHELL ENTRANCE GATE at top-of-spec (sequence-guarded).
  • Router reads explicit Premium flag from prompts (3A); mismatch blocks.
  • Short (NEW) Factual Integrity Invariant (no implied “applied” without current-run evidence).
  • CharCounter v2.1 (deterministic LinkedIn-compatible normalization + count; tolerance rule).
  • QA Title Enforcement (exact block titles required).
  • Added audit flags, new block codes, tests & evidence section.
- v2.3.2 additions (ND Patch — CharCounter v2.1 Metadata Exclusion Enforcement):
  • Boundary markers for body counting: BEGIN MESSAGE BODY … END MESSAGE BODY.
  • Operator confirmation prompt added for boundary/metadata placement (Short path).
  • CharCounter v2.1 counts only content inside markers; metadata lines (“LinkedIn URL”, “Chars: N”) are always outside and excluded.
  • New BLOCK codes for missing markers, metadata inside body, or missing confirmation.

===============================================================================
PROMPT SHELL ENTRANCE GATE — MANDATORY (top-of-spec)
===============================================================================
The system MUST execute this Operator Prompt sequence before any routing or render. Prior chat content can be consulted only AFTER successful completion; it may never substitute for operator replies.

Prompts (verbatim; exact replies required):
(1) "Is this outreach for a NEW contact or an EXISTING contact? Reply EXACTLY NEW or EXISTING."
(2) "Are you sending to a Single contact or Multiple contacts? Reply EXACTLY SINGLE or MULTIPLE."
    → If MULTIPLE + NEW:
      (2A) "Confirm this is immediate post-application outreach (requires minimum K = 4 contacts)? YES/NO."
(3) "Paste the contact's LinkedIn information (Name, Title, About section, LinkedIn URL) in one block:"
(3A) "Is Premium InMail explicitly available for this contact? Reply YES or NO." (REQUIRED for NEW)
(3B) "Show inferred Message Type (Recruiter | Contact | Executive). Answer YES or NO to confirm."
      → If NO: operator must explicitly select one of Recruiter | Contact | Executive.
(3C) (REQUIRED for EXISTING) "Paste the exact prior message(s) sent to this contact, or explicitly reply NONE if no prior message exists:"
(3F) (REQUIRED if Executive) "Frame + 2 strategic insights + tactic + 3 bullets + ask present? Reply YES or NO."
(3G) (REQUIRED when Short (NEW) route is selected)
"Confirm the message body is enclosed exclusively between the markers BEGIN MESSAGE BODY and END MESSAGE BODY, and that metadata lines are explicitly outside these markers. Reply EXACTLY YES to confirm compliance."

Sequence enforcement:
- Any attempt to route or render prior to completing all required prompts → BLOCK with:
  { "status":"error","missing_fields":["operator_prompt_sequence_confirmation"],"failed_checks":["operator_prompt_sequence_violation"] }
- Decision-tree isolation: prior chat never auto-answers prompts; use only operator replies to proceed.

Audit (minimum):
- operator_prompt_sequence_confirmed (bool), prompt_sequence_timestamps {p1_ts..}, premium_inmail_confirmed_explicitly (YES/NO), decision_tree_context_isolation (bool).

--------------------------------------------------------------------------------
VISIBLE OUTPUT CONTRACT — RENDER ONLY THIS (titles enforced)
--------------------------------------------------------------------------------
For each contact, render exactly the following in order. No other text, headings, paths, hashes, or commentary.

Top line (all message types): [LinkedIn URL] (if provided)

1) Subject line (omit for Short NEW)  
2) Greeting and body (final message text; CTA see Section H)  
3) A line with exactly: Regards,  
4) Exactly one empty line  
5) Canonical signature block (Section E)  
6) QA & Evidence sequence in this strict order (Section D), with titles rendered EXACTLY:
   6.1) LinkedIn QA Grid
   6.2) AI Filter Canonical
   6.3) Message-Specific RAG QA Table
   6.4) Evidence Pack

Body normalization:
- Replace “percent” → “%”.
- No em dashes. A standard hyphen may appear inside words or numbers, not as joiners.

Short (NEW) only:
- Immediately after the body, render: Chars: <N> (LinkedIn-compatible body count via CharCounter v2.1).

-------------------------------------------------------------------------------
D) QA RENDERING ORDER — GRID • AI FILTER • RAG • EVIDENCE PACK (mandatory)
-------------------------------------------------------------------------------
Render all four blocks after the message, always in this order; titles must match the contract above. Omission or title drift yields:
{ "status":"error","failed_checks":["qa_table_titles_missing"] }

Message-Specific RAG QA Table — route checks (unchanged core; numbering enforced):
Common full-message checks (rows 2–7)
- Capability Frame present.
- Bullets count = 3, each bullet contains a metric token (% or $ or count).
- Bullet provenance = resume-sourced (Base or Versioned) with an audit flag present.
- Explicit ask present.

Contact-specific (rows 4, 5)
- Insights count = 2 (tactical, Light RAG).
- Insights numbered formatting present (“1.” and “2.”).

Executive-specific (rows 6, 7)
- Insights count = 2 (strategic, Robust RAG).
- Insights numbered formatting present (“1.” and “2.”).
- Tactic present (named playbook tied to KPI or P&L).

Resume clause checks
- Row 2 required; row 4 required; rows 6–7 prohibited; rows 3 and 5 default to no.

Reply-to-Short overlap row (only for 3, 5, 7)
- Append: | X | Non-Redundant vs Prior Short (≤0.40 Jaccard) | ✅/❌ | Token overlap: <score> |

-------------------------------------------------------------------------------
E) SIGNATURE BLOCK — CANONICAL ENFORCEMENT
-------------------------------------------------------------------------------
Signature must be exactly:

Regards,

Amit Ayer
amitayer1@gmail.com
+1-917-239-3830
https://www.linkedin.com/in/amitayer1/

Rules:
- Exactly one blank line after “Regards,” and no blank lines between the four signature lines.
- Enforce trailing slash on the LinkedIn URL.
- Any deviation is auto-corrected silently and logged in the Audit Overlay.

-------------------------------------------------------------------------------
F) AI FILTER INTEGRATION — DASH POLICY EXCEPTIONS (clarified)
-------------------------------------------------------------------------------
- Phone number dashes are auto-whitelisted; do not prompt. :contentReference[oaicite:6]{index=6}
- Hyphens used to join list items or produce patterny parallelism are disallowed; auto-rewrite and re-validate per AI FILTER.
- “No em dashes” rule remains in force for all external text.

-------------------------------------------------------------------------------
G) PREMIUM INMAIL — NEW FULL MESSAGE (routing & content)
-------------------------------------------------------------------------------
For NEW contacts where (3A) premium_inmail_confirmed_explicitly == YES:
- Use the full-message shell (Recruiter or Contact or Executive per R1).
- Apply salutation override (block “Thanks for connecting” and similar).
- Resume clause rule applies by audience (rows 2, 4 = required; rows 6, 7 = prohibited).

-------------------------------------------------------------------------------
H) CTA (“ASK”) CLARITY ENFORCEMENT
-------------------------------------------------------------------------------
- Require a single-sentence, explicit ask at the end of the body with a clear verb and purpose.
- Allowed patterns include:
  • Are you open to a brief conversation to discuss [goal]?
  • Would you be open to a 15-minute intro call next week?
- Amorphous asks are auto-rewritten to an allowed pattern and logged.

-------------------------------------------------------------------------------
I) AUDIT OVERLAY — KEY FLAGS (extended)
-------------------------------------------------------------------------------
Record per render:
- message_type_inferred: Recruiter | Contact | Executive
- route_selected: NEW-Short | NEW-Full | EXISTING-[Recruiter|Contact|Executive-(Direct|Reply)]
- premium_inmail_available: true | false
- premium_inmail_confirmed_explicitly: YES | NO
- capability_frame_present: true | false
- bullets_count: 0..3; bullets_metrics_ok: true | false
- bullet_provenance: resume_sourced | missing
- insights_count: 0..2; insights_level: tactical | strategic | n/a
- insights_numbered_format: true | false
- tactic_present (Executive only): true | false
- resume_clause_rule: required | prohibited | optional | n/a
- reply_to_short_guard_active: true | false
- evidence_pack: rendered=true
- qa_table_titles_present: true | false
- signature_autocorrect: true | false
- cta_pattern: explicit | ambiguous_rewritten
- ai_filter_phone_dash_exception: auto_whitelisted=true
- operator_prompt_sequence_confirmed: true | false
- prior_messages_supplied: true | false
- redundancy_overlap_score: <float> | n/a
- contact_body_auto_confirm: true | false  (true when type = Contact)
- message_type_matrix_synced: true | false
- last_matrix_sync_event: EV-ID
- matrix_validator_sha: <sha256>
- matrix_last_editor: <actor_id>
- matrix_last_edit_timestamp: <RFC3339>
- factual_integrity_invariant_passed: true | false
- character_counter_normalized_linkedin: true | false
- decision_tree_context_isolation: true | false
- message_body_boundary_confirmation: YES | NO
- message_body_markers_present: true | false
- metadata_outside_body_markers: true | false

===============================================================================
ROUTER — MESSAGE TYPE INFERENCE & SELECTION
===============================================================================
R1 — Seniority-based typing only
- Executive = titles VP and above; GM or P&L ownership; Partner or Principal or C-suite; scope described as multi-region, multi-line, or “division” leadership.
- Recruiter and Contact otherwise.
- Do not use messaging mechanics to decide seniority.

R2 — Route matrix
- NEW + Premium (3A == YES) → Full Message (select Recruiter or Contact or Executive per R1).
- NEW + Premium (3A == NO/unknown) → Short (NEW).
- EXISTING → use EXISTING shells. Reply-to-Short variant requires the prior short body (or “NONE”) and activates redundancy guard.

Classification blocker
- If seniority cannot be inferred from title or scope, BLOCK with classification alert.

Premium mismatch blocker
- If route_selected conflicts with (3A), BLOCK with:
  { "status":"error","failed_checks":["premium_routing_mismatch"],"missing_fields":["premium_inmail_confirmation"] }

===============================================================================
MESSAGE TYPE MATRIX — AUTHORITATIVE (MUST BE KEPT IN SYNC)
===============================================================================
| #  | Message Type                | Contact           | Route                 | Capability Frame | JD-Relevant Bullets | Insights Required                          | Tactic (Playbook)                                   | Resume Clause | Reply-to-Short Guard | RAG Mode | Notes                                                                                                      |
|----:|-----------------------------|-------------------|-----------------------|-----------------|---------------------|--------------------------------------------|-----------------------------------------------------|---------------|----------------------|---------:|------------------------------------------------------------------------------------------------------------|
| 1   | Short (NEW)                 | Prospect (new)    | NEW                   | No              | No                  | No                                         | No                                                  | No            | No                   | Light    | **290–310 chars (LinkedIn-compatible via v2.1); abbreviations required; proactive default if no JD/app; no subject** |
| 2   | Recruiter — InMail          | Recruiter         | NEW→Full (Premium=YES)| Yes             | Yes (3)             | No                                         | No                                                  | Yes           | No                   | —        | Frame + 3 bullets; salutation override + résumé line                                                       |
| 3   | Recruiter — Short Accepted  | Recruiter         | EXISTING              | Yes             | Yes (3)             | No                                         | No                                                  | No            | Yes                  | —        | Same as #2 + redundancy guard (Reply-to-Short)                                                             |
| 4   | Contact — InMail            | Business contact  | NEW→Full (Premium=YES)| Yes             | Yes (3)             | Yes (2 tactical, numbered “1.” & “2.”)     | No                                                  | Yes           | No                   | Light    | Frame + insights + 3 bullets; insights must be explicitly numbered; salutation override + résumé line      |
| 5   | Contact — Short Accepted    | Business contact  | EXISTING              | Yes             | Yes (3)             | Yes (2 tactical, numbered “1.” & “2.”)     | No                                                  | No            | Yes                  | Light    | Same as #4 + redundancy guard (Reply-to-Short); insights must be explicitly numbered                       |
| 6   | Executive — InMail          | Executive         | NEW→Full (Premium=YES)| Yes             | Yes (3)             | Yes (2 strategic, numbered “1.” & “2.”)    | **Yes — repeatable playbook tied to KPI/P&L**       | No            | No                   | Robust   | Frame + exec insights (numbered) + tactic + 3 bullets; salutation override                                 |
| 7   | Executive — Short Accepted  | Executive         | EXISTING              | Yes             | Yes (3)             | Yes (2 strategic, numbered “1.” & “2.”)    | **Yes — repeatable playbook tied to KPI/P&L**       | No            | Yes                  | Robust   | Same as #6 + redundancy guard (Reply-to-Short); peer/board tone; insights must be explicitly numbered      |

Note: This table is the single source of truth for message typing behavior, routing, and per-row enforcement. Any future change to Router rules or rendering must reconcile here before merge.

===============================================================================
OPERATOR PROMPTS — MINIMAL PATH (verbatim • REQUIRED • sequence gate)
===============================================================================
**Sequence gate (REQUIRED):** The following prompts must be completed in order before any render.

(1) "Is this outreach for a NEW contact or an EXISTING contact? Reply NEW or EXISTING."
(2) "Are you sending to a Single contact or Multiple contacts? Reply SINGLE or MULTIPLE."
- SINGLE → proceed.
- MULTIPLE → EXISTING allowed (K = 2–5). NEW allowed only if explicitly confirmed as post-application outreach (minimum K = 4).
  If NEW + MULTIPLE selected, ask:
  (2A) "Confirm this is immediate post-application outreach (requires minimum K = 4 contacts)? YES/NO."
    - YES → allow MULTIPLE with K ≥ 4; proceed.
    - NO or invalid → BLOCK (standard error JSON).

(3) "Paste the contact's LinkedIn information (Name, Title, About section, LinkedIn URL) in one block:"
- REQUIRED. Semantic parse into Name, Title, About, canonical URL.
- On parse failure → BLOCK (standard error JSON).

(3A) "Is Premium InMail explicitly available for this contact? Reply YES or NO." (REQUIRED for NEW)
- REQUIRED. Drives routing guard (see Router).

(3B) Show inferred Message Type (Recruiter | Contact | Executive). Answer YES or NO.
- REQUIRED.
- YES → proceed.
- NO → require explicit selection: Recruiter | Contact | Executive.

(3C) “Paste the exact prior message(s) sent to this contact, or explicitly reply NONE if no prior message exists:”
- REQUIRED for EXISTING contacts.
- If response ≠ NONE, run redundancy check (Jaccard ≤ 0.40).
- On fail, BLOCK and trigger mandatory deterministic auto-rewrite.

(3E) Contact body confirmation (applies when type = Contact):
- No operator input required. Presence of Frame, 2 tactical insights (Light RAG), 3 measurable bullets, and an explicit ask defaults to YES and is auto-logged.

(3F) Executive body confirmation (applies when type = Executive):
"Frame + 2 strategic insights + tactic + 3 bullets + ask present? Reply YES or NO."
- REQUIRED when Executive. NO or invalid → BLOCK (see Section D checks).

(3G) Short body boundary confirmation (applies when route = NEW-Short):
"Confirm the message body is enclosed exclusively between the markers BEGIN MESSAGE BODY and END MESSAGE BODY, and that metadata lines are explicitly outside these markers. Reply EXACTLY YES to confirm compliance."

--------------------------------------------------------------------------------
OPERATOR PROMPTS ENFORCEMENT — MANDATORY SEQUENCE
--------------------------------------------------------------------------------
- Sequence violations → BLOCK. Any render attempt prior to completing (1), (2), (2A if applicable), (3), (3A), (3B), (3C for EXISTING), and (3F for Executive) is blocked.
- When route = NEW-Short, (3G) is REQUIRED and must be EXACTLY "YES". Otherwise BLOCK with:
  { "status":"error","missing_fields":["message_body_boundary_confirmation"],"failed_checks":["message_body_boundary_confirmation_missing"] }
- Invalid responses on any required prompt → BLOCK.
- Reply-to-Short path requires the prior short body (or “NONE”) and activates redundancy guard.
- On sequence violation, emit error JSON (see Block & Fallback) and log a detailed prompt-sequence violation report.

===============================================================================
SHORT — NEW — PROMPT SHELL (Light RAG aligned; CharCounter v2.1)
===============================================================================
1) Role
Composer for a ≤310 character connection message to a new, unconnected contact.

2) Task
Draft a 290–310 character DM that includes Why Company, Why Role, and a single Fit line with a metric. Abbreviations required to meet length.

3) Context
- ContactURL, FirstName, JobTitle, Company, WhyCompany, WhyRole, FitLine, BaseResume.

4) Retrieval Plan — Light RAG
- Identify one or two current company imperatives (≤12 months). Use them to phrase WhyCompany, WhyRole, FitLine. Keep citations internal.

5) Reasoning — length and style rules
- Normalize “percent” to “%”. Dash ban for body text.
- Verb-tense: present or future for proposals; past only for brief proof.
- LinkedIn-compatible character counting in body only (CharCounter v2.1). Target 290–310 inclusive.
- Boundary markers are mandatory for counting: the system shall enclose the message body with the exact markers:
  BEGIN MESSAGE BODY
  [message body]
  END MESSAGE BODY
  CharCounter v2.1 strictly counts only the characters inside these markers. The metadata lines “LinkedIn URL” and “Chars: N” must be outside the markers and are excluded from the count.
- Factual Integrity Invariant: If no explicit JD URL or application evidence is provided in the current execution, the body must NOT imply prior application (e.g., “I recently applied…”). Violation → BLOCK with:
  { "status":"error","failed_checks":["factual_integrity_invariant_failed"] }
- If out of range after final pass → BLOCK with:
  { "status":"error","failed_checks":["char_count_mismatch_linkedin"],"count":<internal_count>,"required_range":[290,310],"suggestions":[...] }
- If markers are missing or metadata lines are detected inside the markers → BLOCK with:
  { "status":"error","failed_checks":["message_body_boundary_markers_missing"|"metadata_lines_within_message_body"] }

6) Output (strict)
- Render:

[LinkedIn URL]
Hi [FirstName], I recently applied for the [JobTitle] at [Company]. I am excited by [why Company] and see the role as a chance to [why Role]. My experience in [concrete value] aligns well. Open to connect? Regards, Amit Ayer

Chars: <N>

- Then render QA Grid, AI Filter Canonical, Short RAG QA Table, Evidence Pack (2 rows).

===============================================================================
FULL-MESSAGE BODY STANDARD (applies to rows 2–7)
===============================================================================
The body must contain, in this order:
1) Capability Frame (one or two lines).
2) Insights:
   • Recruiter: none.
   • Contact: two tactical insights explicitly numbered 1. and 2. (Light RAG).
   • Executive: two strategic insights explicitly numbered 1. and 2. (Robust RAG).
3) Tactic (Executive only): one named playbook tied directly to a KPI or P&L.
4) Three measurable bullets (one sentence each), capability-backed and resume-sourced (Base or Versioned).
5) Explicit one-sentence ask.
6) Resume clause line where required (rows 2, 4 only).

===============================================================================
RECRUITER — EXISTING — PROMPT SHELL (rows 2, 3)
===============================================================================
- Structure: Frame → three bullets → ask.
- Row 2 (InMail): add salutation override and resume clause line.
- Row 3 (Short-Accepted): add Reply-to-Short redundancy guard and the QA overlap row.
- Abbreviations prohibited.

===============================================================================
CONTACT — EXISTING — LIGHT RAG — PROMPT SHELL (rows 4, 5)
===============================================================================
- Structure: Frame → two tactical insights numbered 1., 2. → three bullets → ask.
- Row 4 (InMail): add salutation override and resume clause line.
- Row 5 (Short-Accepted): add Reply-to-Short redundancy guard and the QA overlap row.
- Abbreviations prohibited.

===============================================================================
EXECUTIVE — EXISTING — ROBUST RAG — PROMPT SHELL (rows 6, 7)
===============================================================================
- Structure: Frame → two strategic insights numbered 1., 2. → tactic (named playbook) → three bullets → ask.
- Resume clause prohibited for both rows 6 and 7.
- Row 7 (Short-Accepted): add Reply-to-Short redundancy guard and the QA overlap row.
- Abbreviations prohibited. Tone: peer-level, boardroom concise.

===============================================================================
RUN-TIME COMPLIANCE OVERLAY — GPT-5 (binding & pointers)
===============================================================================
Must PASS to emit any App Tracker payload:
- Non-Redundant vs Prior Short (when applicable).
- AI FILTER vNext3. :contentReference[oaicite:7]{index=7}
- Signature exact match.
- Capability Frame present.
- Bullets count = 3 and metrics present.
- Bullet provenance = resume-sourced.
- Insights count and level correct (Contact tactical two; Executive strategic two).
- Insights numbered formatting present.
- Executive tactic present (rows 6, 7).
- Resume clause rules respected (row 2 required; row 4 required; rows 6, 7 prohibited).
- CTA explicit.

===============================================================================
BLOCK & FALLBACK CONDITIONS (expanded)
===============================================================================
- capability_frame_missing
- bullets_invalid (count ≠ 3 or metrics missing)
- bullet_provenance_missing (not resume-sourced)
- contact_insights_count_error (not exactly two tactical insights)
- executive_insights_count_error (not exactly two strategic insights)
- insights_formatting_violation (insights not numbered “1.” and “2.”)
- executive_tactic_missing
- resume_clause_required_missing (rows 2 or 4)
- resume_clause_prohibited (rows 6 or 7)
- reply_guard_missing (rows 3, 5, 7)
- qa_table_titles_missing
- operator_prompt_sequence_violation
- prior_message_prompt_skipped
- premium_routing_mismatch
- factual_integrity_invariant_failed
- char_count_mismatch_linkedin
- message_body_boundary_confirmation_missing
- message_body_boundary_markers_missing
- metadata_lines_within_message_body
- plus all existing enforcement and renderer bans

On block, return only:
{ "status":"error","missing_fields":["..."],"failed_checks":["..."] }

For operator_prompt_sequence_violation:
{
  "status":"error",
  "missing_fields":["operator_prompt_sequence_confirmation"],
  "failed_checks":["operator_prompt_sequence_violation"]
}

For prior_message_prompt_skipped and insights_formatting_violation:
{
  "status":"error",
  "missing_fields":["prior_message(s)_confirmation","numbered_insights_formatting"],
  "failed_checks":["prior_message_prompt_skipped","insights_formatting_violation"]
}

===============================================================================
RENDERER HARD BAN & SCRUB (must not appear in visible output)
===============================================================================
Hard-banned section headers: Audit Metadata, Artifact Storage Paths, SHA256 Fingerprints
Hard-banned prefixes: is_existing:, message_type:, contact_category_user:, contact_category_inferred:, role_detector_match:, contact_url:, timestamp:, deduplication_verdict:, msc/evidence/, message_body_sha256:, ai_filter_table_sha256:, linkedin_canonical_qa_grid.json, ai_filter_table.json, run_audit.json, message_body.txt
Hard-banned regex (multiline):
- (?m)^(msc\/evidence\/.*)$
- (?mi)^\s*(sha256|message_body_sha256|ai_filter_table_sha256)\s*:
- (?m)^(Audit Metadata|Artifact Storage Paths|SHA256 Fingerprints)\b
- (?m)^(is_existing|message_type|contact_category_user|contact_category_inferred|role_detector_match|contact_url|timestamp|deduplication_verdict)\s*:

Dash policy for external content: absolute ban on dash-like characters. Signature phone number is auto-whitelisted. Conditional ban for “Thanks for connecting” lines in NEW Full messages.

===============================================================================
EXCEPTION REGISTRY — DASHES (internal note)
===============================================================================
Purpose: allow minimal, auditable use where unavoidable.
- Auto-whitelist: +1-917-239-3830 (signature phone).
- Other classes: code minus; proper nouns that legally include a dash.
Any exception beyond the signature phone requires a registry entry; otherwise → BLOCK.

===============================================================================
STORAGE & AUDIT — INTERNAL ONLY (do not render)
===============================================================================
- Save artifacts to internal evidence store; do not render paths or hashes.
- Pre-run audit fields (mandatory): is_existing, message_type, contact_category_user, contact_category_inferred, role_detector_match (bool), contact_url, timestamp.
- Operator Prompts audit (mandatory):
  contact_mode; single_or_multiple_response; post_application_outreach_flag;
  bulk_paste_raw_input; parsing_results {name_ok, title_ok, about_ok, url_ok};
  inferred_category; message_type_selected; category_confirmation_or_override;
  prior_messages_supplied; redundancy_overlap_score;
  contact_body_confirm = "auto_yes" when type = Contact; executive_body_confirm when type = Executive;
  batch_size_K (for MULTIPLE); batch_eval_timestamp; per-prompt response_timestamp.
- Short (NEW) audit: final_linkedin_char_count; abbreviation_mappings; length_violation_attempts; regeneration_attempts; final_validation_timestamp; character_counter_normalized_linkedin; message_body_boundary_confirmation; message_body_markers_present; metadata_outside_body_markers.
- NEW Full audit: new_full_message_flag; premium_confirmed (explicit from 3A); salutation_override_applied; resume_clause_rule_applied; enforcement_timestamp.
- Reply-to-Short audit block:
  "reply_to_short_audit": {
    "prior_short_body": "<exact pasted short or NONE>",
    "new_body_pre_rewrite": "<string>",
    "overlap_score": <float>,
    "overlap_tokens": ["..."],
    "auto_rewrite_attempts": <int>,
    "replaced_by_autorewrite": true|false,
    "new_body_post_rewrite": "<string|null>",
    "ai_filter_post_rewrite_pass": true|false,
    "audit_timestamp": "<ISO8601>"
  }
- Pointer resolution logging: pointer_source ∈ {msc_textdoc_id | project_file}, resolved_identifier, run_sha, actor_id, audit_timestamp. :contentReference[oaicite:8]{index=8}
- App Tracker compatibility guard: any attempt to write non-conforming fields or violate outreach gating → BLOCK with actionable error. :contentReference[oaicite:9]{index=9}
- Prompt-sequence violation logging: on any operator_prompt_sequence_violation, log the prompts completed vs. missing, timestamps, and actor_id.
- Matrix sync audit (append): message_type_matrix_synced (bool); last_matrix_sync_event (EV-ID); matrix_validator_sha; matrix_last_editor; matrix_last_edit_timestamp.
- Factual integrity audit (append): factual_integrity_invariant_passed (bool) + rationale.
- Decision-tree audit (append): decision_tree_context_isolation (bool).

-------------------------------------------------------------------------------
IMPLEMENTATION APPENDIX — REPLY-TO-SHORT (ENGINEER NOTES)
-------------------------------------------------------------------------------
- Overlap metric: deterministic stemmed-token Jaccard (threshold 0.40).
- Optional: semantic cosine overlap as advisory only (non-gating).
- Auto-rewrite must preserve numeric metrics, proper nouns, required fit metrics; validate preservation before reuse.
- Ensure Executive and Contact outputs still meet the item counts after rewrite.
- If prior_short_body == NONE, skip the guard entirely.

-------------------------------------------------------------------------------
IMPLEMENTATION APPENDIX — LINKEDIN CHARACTER COUNTER v2.1 (UPDATED)
-------------------------------------------------------------------------------
Purpose: deterministic LinkedIn-compatible normalization + Unicode code-point counting with explicit body boundaries.

Scope & boundary markers:
- CharCounter v2.1 shall strictly count only content explicitly enclosed between the operator-verified markers:
  BEGIN MESSAGE BODY
  [message body]
  END MESSAGE BODY
- Metadata such as LinkedIn URLs and character count indicators ("Chars: N") must never be included inside these markers and are excluded from counting.

Normalization (apply in exact order):
  1) Unicode NFC normalize.
  2) Remove zero-width characters: U+200B..U+200D, U+FEFF.
  3) Convert typographic quotes/apostrophes to ASCII (’→', “/”→").
  4) Replace token per spec: `percent` → `%` (word-boundary, case-insensitive).
  5) Collapse whitespace sequences (spaces, NBSP U+00A0, tabs, newlines) → single ASCII space.
  6) Replace en/em dashes U+2013..U+2014 → hyphen `-` (filter’s external dash ban still applies for emitted content).
  7) Remove control characters; trim leading/trailing spaces.

Counting:
  - len(normalized_string) measured as Unicode codepoints on the substring strictly inside the boundary markers.

Tolerance rule (optional operator-provided observed count):
  - If |observed - internal| == 1 AND sentence-boundary collapse is detected, accept observed and log char_count_tolerance_applied=true; else block.

Blocking conditions for boundaries/metadata:
  - Missing or misplaced markers:
    { "status":"error","failed_checks":["message_body_boundary_markers_missing"] }
  - Detection of metadata lines inside the markers:
    { "status":"error","failed_checks":["metadata_lines_within_message_body"] }

Suggestion generator (non-destructive; operator-confirm only):
  - Provide 1–3 safe, short suggestions (e.g., add “to explore potential synergies”; add credibility token like “with P&L experience”; or add “I’d value a quick 15-min intro to discuss ideas.”)

Pseudocode:
def normalize_for_linkedin(s):
    s = unicodedata.normalize('NFC', s)
    s = re.sub(r'[\u200B-\u200D\uFEFF]', '', s)
    s = s.replace('\u2019', "'").replace('\u201C', '"').replace('\u201D', '"')
    s = re.sub(r'\bpercent\b', '%', flags=re.IGNORECASE)
    s = re.sub(r'[\s\u00A0]+', ' ', s)
    s = s.replace('\u2014', '-').replace('\u2013', '-')
    s = ''.join(ch for ch in s if ord(ch) >= 32)
    return s.strip()

def count_linkedin_chars(s):
    # s is the full draft; extract the substring strictly between markers, then count
    body = extract_between_markers(s, "BEGIN MESSAGE BODY", "END MESSAGE BODY")
    s_norm = normalize_for_linkedin(body)
    return len(s_norm)

def suggest_lengthening(s, needed_chars):
    suggestions = []
    if needed_chars <= 10:
        suggestions.append("append 'to explore potential synergies' to CTA")
        suggestions.append("add credibility token like 'with P&L experience'")
    else:
        suggestions.append("add a short sentence: 'I’d value a quick 15-min intro to discuss ideas.'")
    return suggestions

-------------------------------------------------------------------------------
IMPLEMENTATION APPENDIX — PROMPT ENFORCEMENT HOOK
-------------------------------------------------------------------------------
- Provide PromptShell.enforce_sequence() that:
  a) emits prompts in order to operator UI,
  b) validates exact-format replies (YES/NO, NEW/EXISTING, SINGLE/MULTIPLE),
  c) records timestamps and operator replies into audit,
  d) sets operator_prompt_sequence_confirmed=true only after valid completion,
  e) returns route_allowed set for downstream Router.

-------------------------------------------------------------------------------
EXECUTIVE VARIANTS INDEX (for operator reference)
-------------------------------------------------------------------------------
| # | Message Type                                              | RAG Mode | Prompt for Prior Message |
|---:|-----------------------------------------------------------|:--------:|:-------------------------|
| 6  | Executive (EXISTING — Robust RAG, Direct via Premium)     | Robust   | N                        |
| 7  | Executive (EXISTING — Robust RAG, Reply to Short)         | Robust   | Y (Prompt 3D & guard)    |

===============================================================================
MESSAGE TYPE MATRIX — GOVERNANCE & SYNC RULES (automated)
===============================================================================
(unchanged from v2.3; remains mandatory for every canonical change with TST-060 runs and audit flags)

-------------------------------------------------------------------------------
TESTS & EVIDENCE (updated)
-------------------------------------------------------------------------------
PromptShell tests:
  TST-100: invoke runner without operator prompts → MUST BLOCK (operator_prompt_sequence_violation)
  TST-101: complete prompts correctly → route selection allowed
  TST-102: attempt bypass via prior chat replies → BLOCK

CharCounter tests:
  TST-110: vector set A (canonical short samples) → count_linkedin_chars() equals expected
  TST-111: under-290 sample → verify block + suggestions
  TST-112: 1-char off observed sample → tolerance applies if heuristic matches
  TST-113: normalization: ZWSP removal + whitespace collapse → expected count
  TST-114: boundary markers present and metadata excluded → pass; missing/misplaced → BLOCK

Integration tests:
  TST-120: full Short (NEW) render end-to-end: prompts → boundary confirmation → char counter → QA titles -> success or explicit block JSON
  TST-121: routing test: NEW + (3A == NO) -> Short; NEW + (3A == YES) -> Full

Never-recur lines:
  • "PromptShell gate enforces mandatory operator prompts before routing, preventing prior-chat bypass."
  • "CharCounter v2.1 uses explicit body boundaries and excludes metadata; mismatch blocks and suggests safe edits."

===============================================================================
END OF LINKEDIN OUTREACH - CANONICAL v2.3.2
===============================================================================
