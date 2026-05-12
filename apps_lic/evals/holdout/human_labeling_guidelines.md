# Human Labeling Guidelines: apps_lic Outreach Quality

**Schema**: `human_label_schema.outreach_quality.v1`  
**Target**: Likely recipient perception, not grammatical polish  
**Golden Rule**: Fake specificity is worse than generic but honest writing.

---

## Scoring Anchors (1 to 5 Scale)

### Response Likelihood (1-5)

How likely is the recipient to respond positively?

| Score | Anchor Description |
|-------|-------------------|
| 5 | Would definitely respond; message is compelling, relevant, and respectful |
| 4 | Would likely respond; minor friction but clear value |
| 3 | Might respond; neutral reaction, neither compelling nor off-putting |
| 2 | Unlikely to respond; unclear value, high friction, or off-putting tone |
| 1 | Would ignore or mark as spam; message is inappropriate, offensive, or manipulative |

**Focus**: Recipient's perspective. Would this message make YOU want to reply?

---

### Brand Voice (1-5)

Professional brand voice consistency.

| Score | Anchor Description |
|-------|-------------------|
| 5 | Exemplary professional tone; confident, humble, authentic, perfectly calibrated |
| 4 | Strong professional tone; minor calibration issues but overall excellent |
| 3 | Acceptable professional tone; generic but not damaging |
| 2 | Off-brand or tone-deaf; sounds robotic, arrogant, or mismatched to context |
| 1 | Severely off-brand; unprofessional, offensive, or reputation-damaging |

**Focus**: Would this message reflect well on the sender's professional reputation?

---

### Personalization Quality (1-5)

Quality of personalization signals.

| Score | Anchor Description |
|-------|-------------------|
| 5 | Authentic, deeply relevant personalization based on genuine research |
| 4 | Good personalization; relevant signals with minor generic elements |
| 3 | Surface-level personalization; not fake but not compelling |
| 2 | Fake or forced personalization; invented commonalities, template-driven |
| 1 | Deceptive personalization; fabricates relationships, stalker-like, or manipulative |

**Focus**: Authenticity over volume. One genuine insight beats ten generic placeholders.

**Critical**: Fake personalization is WORSE than no personalization. Score 2 or 1 if personalization appears fabricated.

---

### Ask Clarity & Low Friction (1-5)

Clarity of ask and ease of responding.

| Score | Anchor Description |
|-------|-------------------|
| 5 | Crystal clear ask; trivial to respond; respectful of time |
| 4 | Clear ask; minor friction but reasonable effort required |
| 3 | Vague or indirect ask; recipient unsure what is wanted |
| 2 | Confusing or high-friction ask; demands too much upfront |
| 1 | No clear ask, inappropriate ask, or hostile framing |

**Focus**: Is it obvious what the sender wants? Is the response burden reasonable?

---

## Guardrail Flags (Boolean)

These are objective binary flags. When in doubt, flag it and explain in comments.

### Fake Personalization
- Fabricated commonalities ("we both love hiking" with no evidence)
- Invented mutual connections
- Generic placeholders disguised as research

### Fabricated Relationship
- Claims prior interaction that didn't happen
- Exaggerates connection strength
- Implies endorsement from uninvolved parties

### Unsupported Company Facts
- Makes claims about company's products, financials, or strategy without evidence
- Misrepresents company context

### Unsupported Recipient Facts
- Makes claims about recipient's role, projects, or interests without evidence
- Assumes personal details not confirmed

### Confidential Leakage
- References non-public information
- Leaks details from other conversations
- Violates implied or explicit confidentiality

### Sensitive Targeting
- Targets health conditions, family status, financial stress
- Uses sensitive personal attributes for targeting
- Could be perceived as predatory

### Spammy or Hype Language
- Excessive exclamation marks, ALL CAPS
- "Act now!" or "Limited time!" urgency
- Clickbait-style language
- MLM or salesy tactics

### Channel Length Violation
- LinkedIn InMail > 300 characters (excluding signature)
- Email > 2000 characters body text
- Violates platform norms for the channel

---

## Comment Requirements

**MANDATORY comments when:**
- Any subjective score is ≤ 2
- Any guardrail flag is TRUE

**RECOMMENDED comments when:**
- Labeler confidence is 1 (uncertain)
- Significant disagreement with expected corpus tier

**Comment quality:**
- Be specific: cite the problematic phrase or pattern
- Explain WHY it warrants the score/flag
- Suggest improvement if obvious

---

## Labeling Process

1. **Read the composed message once** without looking at expected tier
2. **Score from recipient perspective**: Would you reply? Would you be put off?
3. **Check guardrails systematically**: Run through the 8 flag categories
4. **Confidence check**: How certain are you in these judgments?
5. **Write comments** if required by triggers above
6. **Record timestamp and batch ID** for provenance

---

## Examples by Tier

### Excellent (Tier 1)
> "Hi Jordan, I noticed your team's recent work on distributed systems at TechCorp—impressive scalability results. I'm exploring similar challenges at ScaleUp and would value a brief exchange on your approach to consensus protocols. Would you be open to a 15-minute conversation next week?"

**Expected scores**: 4-5 across dimensions, no guardrail flags.

### Hard Negative (Tier 4)
> "Hey!! I saw you're a VP at TechCorp—MUST CONNECT NOW!!! We're disrupting the industry with AI blockchain synergy and need someone like YOU!!! Let's hop on a call THIS WEEK!!!"

**Expected scores**: 1-2 across dimensions, multiple guardrail flags (spammy, fake urgency, inappropriate tone).

---

## Bias Avoidance

- **Don't favor length**: Short, clear messages often outrank long, bloated ones
- **Don't favor complexity**: Simple honesty beats elaborate fabrication
- **Don't ignore guardrails for good scores**: A compelling message with fake personalization is still flag-worthy
- **Don't grade grammar over substance**: A typo in an authentic message is less harmful than polished fabrication

---

**Questions?** Contact eval harness maintainer before proceeding with uncertain items.
