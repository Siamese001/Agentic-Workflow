# 19 Source Register


<!-- card-meta
card_id: 19_SOURCE_REGISTER
card_type: rule
priority: must
paste_order: 19
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
- Every claim about Searce that came from research must carry a `[S#]` tag resolved in card 19 (Source Register).
- Personal experience (STAR, RCA) needs no citation.
- If you cannot cite a research claim, downgrade the framing to "my read is" or drop it.

### Preferred reliability-chain phrasing
When a reliability chain is useful, use these clusters instead of a long control inventory:
- **trusted data and semantic grounding**
- **validated execution and model lifecycle**
- **governed action and policy gates**
- **observability, audit, and regression evals**



## Purpose
This card is the **citation backbone** for everything in the pack. Every research-derived claim has a `[S#]` citation that resolves here.

## Inline citation grammar
- `[S1]`, `[S2]`, ... reference entries in the table below.
- A claim with no `[S#]` is either personal experience (STAR / RCA) or a generic principle.
- Direct evidence beats interpretation; interpretation beats inference; inference beats assumption.
- Never invent a `[S#]` that is not registered here.

## Source register


| ID | Type | Claim | Source |
|----|------|-------|--------|
| `SRC-001` | direct_evidence | Searce was founded in 2004 by Hardik Parekh, headquartered in Pune India with executive presence in Houston TX; ~2,200 employees, ~$126M revenue (2025), entirely bootstrapped | company_history |
| `SRC-002` | direct_evidence | Searce is a Google Cloud Premier Partner and Everest Group 2025 PEAK Matrix Major Contender for GCP Services Specialists | market_positioning |
| `SRC-003` | direct_evidence | Searce led a $1.8M Series A in ConveGenius (Feb 2024), its first vertical-AI IP equity move | strategic_investments |
| `SRC-004` | direct_evidence | Vrinda Khurjekar serves as VP Solutions Consulting NA; Siddharth Shah as AVP — they own the commercial pre-sales motion in North America | regional_leadership |
| `SRC-005` | direct_evidence | Vrinda Khurjekar is VP Americas at Searce (Sept 2024-present per LinkedIn), 17-year tenure, started 2008 as Business Process Improvement Manager (Houston). The role being interviewed for reports into her. | interviewer_profile |
| `SRC-006` | direct_evidence | Vrinda's Sept 2025 LinkedIn post enumerates her 5 priorities for Searce's next phase: deepen customer partnerships, scale AI-native offerings, expand Americas footprint, strengthen partner ecosystem, build high-performance teams | interviewer_priorities |
| `SRC-009` | direct_evidence | Vrinda has published bylines on regulated-industries AI in Emerj podcast (with Paul Pallath), MedCity News (precision medicine), Authority Magazine (manufacturing), and Street Fight (retail supply chain) — establishing her POV territory | interviewer_thought_leadership |
| `SRC-007` | direct_evidence | Searce's HAPPIER values (Humble, Adaptable, Positive, Passionate, Innovative, Excellence, Responsible) are strictly enforced in technical interview behavioral screening; technical brilliance without HAPPIER alignment results in disqualification | cultural_fit |
| `SRC-008` | analyst_inference | Searce employee sentiment data shows significant friction in middle management, compensation structures, offshore delivery — relevant context for first-90-day planning by senior hires | operational_friction |



## Claim-type ladder
Each row is labeled with one of:

- **`direct_evidence`** — verbatim from a primary source (annual report, press release, SEC filing, signed exec quote).
- **`interpretation`** — an analyst summary that combines two or more direct sources.
- **`analyst_inference`** — a third-party analyst's downstream inference about a direction or strategy.
- **`assumption`** — explicit working hypothesis with no source backing; flag in any answer that uses it.

## Anti-pattern
Do **not** quote an `analyst_inference` row as if it were `direct_evidence`. If Searce pushes back, downgrade the citation honestly.

## Example usage in a live answer
Without source register:

> "I think Acme is investing in measurement intelligence."

With source register:

> "Acme's most recent investor day called out measurement intelligence as a 2026 priority `[S2]`. My read is that this lines up with their decisioning practice expansion."

The first sentence is a direct citation. The second is labeled "my read" so the listener knows it is interpretation.
