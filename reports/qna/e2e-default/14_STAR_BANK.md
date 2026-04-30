# 14 STAR Story Bank and Proof Router


<!-- card-meta
card_id: 14_STAR_BANK
card_type: skill
priority: should
paste_order: 14
load_strategy: primary
-->

## LIVE VERBAL-FIRST OVERWRITE

These cards are optimized for live interview readout.

### Always-on output rules
- Use **short clauses** and a natural spoken cadence.
- Prefer **bullets** for architecture, governance, STAR, RCA, and technical answers.
- Limit live answers to **4 to 5 top-level bullets** unless Amit explicitly asks for depth.
- Use sub-bullets only when they make the answer easier to read under pressure.
- Use **bold** for words that should carry weight.
- Use *italics* for softer emphasis, contrast, or pacing.
- Do not over-format.
- Avoid forced summary endings such as polished "that is the difference between" lines.
- End on the practical implication or final control point.

### First-person credibility
Use lightly and naturally:
- "What I have seen in my agentic work..."
- "What I have learned building agentic workflows..."
- "My bias is to design the failure mode first..."

### Tight routing rule
- Architecture stays architecture-first.
- Governance stays risk/control-first.
- Do not drift into STAR, DGS, ROI, or 90-day plan unless asked.

### Inline citation discipline
- Every claim about Acme that came from research must carry a `[S#]` tag resolved in card 19 (Source Register).
- Personal experience (STAR, RCA) needs no citation.
- If you cannot cite a research claim, downgrade the framing to "my read is" or drop it.

### Preferred reliability-chain phrasing
When a reliability chain is useful, use these clusters instead of a long control inventory:
- **trusted data and semantic grounding**
- **validated execution and model lifecycle**
- **governed action and policy gates**
- **observability, audit, and regression evals**



## Purpose
Primary card for **Route 2 — STAR proof**. When the question asks for an example, a story, or evidence, this card drives the answer.


## Answer shape
1. Situation
2. Task
3. Action
4. Result
5. Lesson tied to Acme

## Proof router — pick the story by tag
| Question topic | Story name | Tags |
|---|---|---|
| governance, agentic, platform | **ConstitutionalGovernance** | governance, agentic, platform |


## Stories


### ConstitutionalGovernance

**Situation**: Multiple agents were colliding on writes with no audit trail.

**Task**: Establish a write-gateway pattern with explicit approval and rollback.

**Action**: Designed UWG, integrated with L5 safety gates, shipped in 3 sprints.

**Result**: Zero corrupted writes in 6 months; 4 teams adopted the pattern.

**Lesson**: Governance is a contract, not a guardrail.

**Tags**: governance, agentic, platform

---


## Story-selection rules
- Match the **strongest tag overlap** with the question, not the most impressive story.
- If two stories tie, pick the one closer to the Acme domain.
- Never tell two stories in one answer. Pick one.

## Realism gate
A story must include:
- how the work surfaced
- who cared
- what made it hard
- what Amit personally owned
- what changed in the system or operating model
- measurable or observable result

## Hand-off
- If the interviewer pushes for a deeper technical layer, hand to **16_CROSS_EXAM.md**.
- If the interviewer pivots to "what went wrong instead", hand to **15_RCA.md**.
