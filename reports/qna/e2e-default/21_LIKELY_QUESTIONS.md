# 21 Likely Questions


<!-- card-meta
card_id: 21_LIKELY_QUESTIONS
card_type: rule
priority: may
paste_order: 21
load_strategy: always_on
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
A predicted-questions list, grouped by route, derived from the JD, role, and research. Use this as a rehearsal warmup, not as a script.


## Default likely-question seeds
Use these patterns until a real predicted-questions set is supplied via `extra_context.likely_questions`.

### Executive fit
- Why this company at this point in your career?
- What is your read on our agentic strategy?
- What would make the first 90 days obviously fail?

### Architecture
- How would you build a governed agentic system for Acme from scratch?
- Where do you draw the line between agent autonomy and human approval?
- What is the failure mode you design for first?

### Governance
- How do you prevent hallucination in production?
- How do you separate advisory output from state-changing actions?
- What is your evidence floor for promoting a model?

### STAR proof
- Tell me about a time you shipped a governed agentic system end-to-end.
- Give me an example of a measurement model you productized.
- Describe a time you pushed back on a stakeholder about safety.

### RCA
- Tell me about a production failure you owned.
- What was the operating-model change that came out of it?

### Cross-exam
- Be more specific. What exact tools did you use?
- That sounds high-level. Walk me one layer deeper.


## Rehearsal posture
- Run each predicted question against the routing manifest in card 01.
- If the same primary card answers ≥ 4 of these, that card is the **highest-leverage** prep target.
- If a question does not map cleanly to any route, treat it as a **routing gap** and add to card 22 (Learnings).
