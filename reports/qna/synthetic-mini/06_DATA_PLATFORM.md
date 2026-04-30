# 06 Data Platform Stack

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

### Preferred reliability-chain phrasing
When a reliability chain is useful, use these clusters instead of a long control inventory:
- **trusted data and semantic grounding**
- **validated execution and model lifecycle**
- **governed action and policy gates**
- **observability, audit, and regression evals**



## Purpose
Specialist card for architecture and DS-to-platform answers. Loads only when the question pulls in the data platform layer (warehouse, semantic catalog, governance, AI workspace).


## Stack anchors
- Lakehouse with semantic catalog
- Model registry with lineage


## When to invoke
- Architecture answer that needs to ground on the data layer.
- Governance answer that pivots into semantic grounding.
- DS-to-platform answer that needs to name the registry / lineage path.

## Talking points
- The catalog is the contract surface for agents.


## Anti-patterns to avoid
- Do not list every tool in the stack. Name only what the answer needs.
- Do not promise vendor lock-in. Name the contract surface.
- Do not turn this into a tooling debate. Stay on the control points.

## Hand-off
- If the question shifts to model lifecycle, route to **10_DS_TO_PLATFORM.md**.
- If the question shifts to client trust, route to **08_GOVERNANCE.md**.
