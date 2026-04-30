# 05 Agentic Architecture Core


<!-- card-meta
card_id: 05_ARCHITECTURE_CORE
card_type: skill
priority: should
paste_order: 5
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
Primary card for **Route 4 — Architecture concept**. When the question is "how would you build", this card drives the answer.


## Answer shape
1. Business workflow first.
2. Data and semantic layer.
3. Agent / orchestration layer.
4. Governance and eval layer.
5. Product and scale layer.

## Spine for an architecture answer

- Start with the **business decision** the system serves at Acme.
- Name the **trusted data contract** (semantic layer, governed catalog, lineage trace).
- Explain the **agent or orchestration layer** — what it plans, what it executes, what it does not touch.
- Name the **control point** (gate, eval, registry, approval checkpoint, audit log).
- Translate uncertainty honestly. Stop on the practical implication.

## Reliability chain (use as clusters, not full inventory)
- **trusted data and semantic grounding**
- **validated execution and model lifecycle**
- **governed action and policy gates**
- **observability, audit, and regression evals**

## Architecture content

### Business workflow
- Start with the planner's actual decision.
- Name the trusted data contract.


### Governance layer
- Separate read paths from write paths.
- Every write through a governed action plane.



## What this card does NOT do
- Does not turn into a STAR story unless asked.
- Does not collapse into governance — that is Route 5.
- Does not name vendor stack unless the question requires it.

## Cross-exam fallback
If the interviewer pushes deeper, hand off to **16_CROSS_EXAM.md** — name the artifact, gate, or metric and stop.
