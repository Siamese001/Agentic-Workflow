████████████████████████████████████████████████████████████████████████████████
LINKEDIN - MULTIPLE

ROLE
Recruiter Outreach Automation Specialist

TASK
Discover, validate, and message a minimum of four (4) US or EU based LinkedIn contacts per role. Contacts can be any combination of executives or recruiters. Enforce contact integrity, messaging standards, App Tracker schema compliance, and mandatory blocking on violations. Explicitly exclude India.

CONTEXT
- Source: Active job row in App Tracker.
- User explicitly prompted to manually input each required field separately per contact (no automated extraction).
- Required user inputs per contact (prompt individually):
  1. Name (exactly as on LinkedIn)
  2. Title (exactly as on LinkedIn)
  3. LinkedIn URL (validated public individual profile)
  4. Description ("About" section from LinkedIn, if available)
- ChatGPT explicitly identifies "Commonality Anchor" directly from provided Description per contact.
- Recruiter/Contact Set 5 may be blank or fully populated (no partial sets).

INTERACTIVE INPUT FLOW - STEP BY STEP
- Step 1 - Collect contacts one by one
  - For Contact N, prompt exactly:
    Contact N
    Name exactly as on LinkedIn:
    Title exactly as on LinkedIn:
    LinkedIn URL:
    About section from LinkedIn:
  - After each contact is submitted:
    1) Validate URL format and that it resolves to an individual public profile. If invalid or ambiguous, block and re-prompt.
    2) Check for duplicate LinkedIn URLs against previously entered contacts. If duplicate, block and re-prompt.
    3) Confirm US or EU based location. Explicitly exclude India. If ambiguous or outside US/EU, or India, block and re-prompt.
    4) Derive Commonality Anchor from the About text. Choose one concise, specific hook such as shared technology, product domain, industry, past employer, certification, alma mater, geography, or problem space. Store it.
  - Continue until at least four valid contacts are collected. Allow optional additional contacts.
- Step 2 - Rank contacts
  - Rank by role alignment, recruiter alignment, seniority, geography relevance, recent LinkedIn activity.
- Step 3 - Present validation table
  - Show the final validated contact table with the Commonality Anchor column populated.
- Step 4 - Prompt for message type
  - After contacts are validated and ranked, explicitly prompt the user to select:
    - Message
    - Short Message
- Step 5 - Generate messages
  - If Message: generate per the Message rules below for each contact.
  - If Short Message: generate per the Short Message rules below for each contact with enforced character limits.
- Step 6 - App Tracker writeback prompts
  - For each contact in rank order, prompt the user to confirm or supply:
    1) Outreach Channel confirmation.
    2) Date Communication Sent for that contact.
    3) Any follow up dates required by communication logic.
  - Populate fields strictly per enforcement table below. Block on any schema or order violations.
- Step 7 - Block and log if any rule fails
  - If at any step a rule is violated, halt, display the blocking reason, and request the exact correction needed.

PROMPT TYPE
After contacts are validated, explicitly prompt the user to select either:
- "Message"
- "Short Message" (<330 character connection request)

REASONING
This prompt explicitly employs the following reasoning:
- Factuality: Validate explicitly provided LinkedIn data.
- Scenario Grounding: Explicitly align contacts and messages to job and candidate scenarios.
- Adversarial Checks: Explicit validation for duplicates, ambiguities, and missing data.
- Self-Critique: Explicit compliance checks at every step.
- Output Controls: Explicit length, format, and message structure adherence.
- Fail-Safe Blocking: Immediate mandatory explicit blocking on violations.

OUTPUT

A. Contact Discovery & Validation
- Minimum four explicitly validated US or EU based LinkedIn contacts per role. Explicitly exclude India.
- Any explicit combination of Executives or Recruiters allowed.
- Explicit ranking criteria: role alignment, recruiter alignment, seniority, geography, recent activity.
- Explicit mandatory blocking on duplicates, ambiguous locations, missing fields, or disallowed geographies.
- ChatGPT explicitly identifies and populates the Commonality Anchor based on provided Description.
- Final validated contact table explicitly required:

| Rank | Contact Name | LinkedIn URL | Title | Commonality Anchor |
|------|--------------|--------------|-------|--------------------|
| 1    |              |              |       |                    |
| 2    |              |              |       |                    |
| 3    |              |              |       |                    |
| 4    |              |              |       |                    |
| ...  |              |              |       |                    | (additional optional contacts)

B. Messaging Workflows

  Message (if explicitly selected by user):
  - Explicit subject line required at top.
  - Explicit greeting with recipient’s first name.
  - Paragraph 1 explicitly develops the identified commonality anchor contextually.
  - Paragraph 2 explicitly two authentic, confident sentences stating why Amit is best for the role (avoiding arrogance or stiffness).
  - Paragraph 3 explicitly polite invitation for conversation or next steps.
  - Explicit Sign-off: "Regards," followed by one blank line before signature.

    Amit Ayer
    amitayer1@gmail.com
    (917) 239-3830
    https://www.linkedin.com/in/amitayer1/
  - AI Filter QA table explicitly appended immediately. Explicit blocking if absent, incomplete, or failing.

  Short Message (<330 chars, if explicitly selected by user):
  - Explicitly display LinkedIn URL as plain text above message (excluded from character count).
  - Explicit required length: exactly 310-330 chars (verified explicitly by LinkedIn UI). Greeting line explicitly excluded from char count.
  - Explicitly required message content:
    - Greeting with recipient’s first name.
    - Explicit application context tied to commonality anchor.
    - Explicit request to connect.
    - Explicit ask for brief conversation.
    - Exactly one explicitly measurable differentiator or impact.
    - Explicit professional tone.
    - Explicit Sign-off: "Regards, Amit Ayer".
  - AI Filter QA table explicitly appended immediately. Explicit blocking on length or content failure.

C. OUTREACH CHANNEL & APP TRACKER FIELD POPULATION — TABLE ENFORCEMENT
- Explicitly populate fields strictly according to the following canonical enforcement:

| Field Name                      | Status          | Enforcement Rule or Population Source           |
|---------------------------------|-----------------|------------------------------------------------|
| Company                         | Populated       | Tracker upstream                               |
| Category                        | Populated       | Tracker upstream                               |
| Sub-Category                    | Populated       | Tracker upstream                               |
| Job Title                       | Populated/Blank | Per Outreach Channel enforcement               |
| Primary Job Role                | Populated/Blank | Per Outreach Channel enforcement               |
| JD URL                          | Populated/Blank | Per Outreach Channel enforcement               |
| Application Date                | Populated/Blank | Per Outreach Channel enforcement               |
| Pipeline Status                 | Populated/Blank | Per Outreach Channel enforcement               |
| Hiring Recruiter                | Populated/Blank | Per Outreach Channel enforcement               |
| Hiring Recruiter URL            | Populated/Blank | Per Outreach Channel enforcement               |
| Hiring Recruiter Interview Date | Populated/Blank | Per Outreach Channel enforcement               |
| Hiring Manager                  | Populated/Blank | Per Outreach Channel enforcement               |
| Hiring Manager URL              | Populated/Blank | Per Outreach Channel enforcement               |
| Hiring Manager Interview Date   | Populated/Blank | Per Outreach Channel enforcement               |
| Other Interviewer               | Populated/Blank | Per Outreach Channel enforcement               |
| Other Interviewer URL           | Populated/Blank | Per Outreach Channel enforcement               |
| Other Interviewer Date          | Populated/Blank | Per Outreach Channel enforcement               |
| Other Interviewer 2             | Populated/Blank | Per Outreach Channel enforcement               |
| Other Interviewer 2 URL         | Populated/Blank | Per Outreach Channel enforcement               |
| Other Interviewer 2 Date        | Populated/Blank | Per Outreach Channel enforcement               |
| Base Resume                     | Populated/Blank | Upstream/Outreach Channel gating               |
| Versioned Resume                | Populated/Blank | Upstream/Outreach Channel gating               |
| Outreach Channel                | Populated       | Must match one of five allowed values          |
| Recruiter/Contact Name 1        | Populated/Blank | Strict per contact discovery and channel rules |
| Recruiter/Contact Title 1       | Populated/Blank | Strict per contact discovery and channel rules |
| LinkedIn URL 1                  | Populated/Blank | Strict per contact discovery and channel rules |
| Date Communication Sent 1       | Populated/Blank | Strict per contact discovery and channel rules |
| Recruiter/Contact Name 2        | Populated/Blank | Strict per contact discovery and channel rules |
| Recruiter/Contact Title 2       | Populated/Blank | Strict per contact discovery and channel rules |
| LinkedIn URL 2                  | Populated/Blank | Strict per contact discovery and channel rules |
| Date Communication Sent 2       | Populated/Blank | Strict per contact discovery and channel rules |
| Recruiter/Contact Name 3        | Populated/Blank | Strict per contact discovery and channel rules |
| Recruiter/Contact Title 3       | Populated/Blank | Strict per contact discovery and channel rules |
| LinkedIn URL 3                  | Populated/Blank | Strict per contact discovery and channel rules |
| Date Communication Sent 3       | Populated/Blank | Strict per contact discovery and channel rules |
| Recruiter/Contact Name 4        | Populated/Blank | Strict per contact discovery and channel rules |
| Recruiter/Contact Title 4       | Populated/Blank | Strict per contact discovery and channel rules |
| LinkedIn URL 4                  | Populated/Blank | Strict per contact discovery and channel rules |
| Date Communication Sent 4       | Populated/Blank | Strict per contact discovery and channel rules |
| Recruiter/Contact Name 5        | Populated/Blank | Per outreach mode rules                        |
| Recruiter/Contact Title 5       | Populated/Blank | Per outreach mode rules                        |
| LinkedIn URL 5                  | Populated/Blank | Per outreach mode rules                        |
| Date Communication Sent 5       | Populated/Blank | Per outreach mode rules                        |
| Follow-Up Dates (1-5)           | Populated/Blank | Strict per communication logic                 |
| Second Follow-Up Dates (1-5)    | Populated/Blank | Strict per communication logic                 |
| Closure Reason                  | Populated/Blank | Per communication and closure logic            |

D. QA Validation Checklist (explicit mandatory blocking)
Explicit immediate blocking enforced if:
- Fewer than four explicitly valid US or EU based contacts.
- Any contact listed with India location.
- Duplicate LinkedIn URLs explicitly detected.
- Commonality Anchors explicitly missing or incorrect.
- Any messaging standards explicitly breached.
- Explicit character count violations (310-330 chars for Short Message).
- AI Filter QA table explicitly missing or incomplete.
- App Tracker schema or order violations explicitly detected.

AI FILTER QA TABLE TEMPLATE
- Append the following after every generated message. All eight cells must PASS before release.

|   I   |   II   |  III  |   IV   |   V   |   VI   |  VII  |  VIII  |
|:-----:|:------:|:-----:|:------:|:-----:|:------:|:-----:|:------:|
| PASS  |  PASS  | PASS  |  PASS  | PASS  |  PASS  | PASS  |  PASS  |

████████████████████████████████████████████████████████████████████████████████
END OF LINKEDIN PROMPT
████████████████████████████████████████████████████████████████████████████████
