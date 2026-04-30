# 22 Learnings and Delta Sheet


<!-- card-meta
card_id: 22_LEARNINGS
card_type: rule
priority: may
paste_order: 22
load_strategy: post_rehearsal
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
The post-rehearsal learnings card. After every mock or live interview, Amit writes here what worked, what drifted, and what to fix in the next build.

## How to use
1. After a rehearsal or interview, type the actual question into the Project chat.
2. Capture the actual answer pattern that came out (paraphrase if needed).
3. Score it against the pathology taxonomy below.
4. Edit the relevant card before the next build, then re-run `python -m apps_qna build`.

## Pathology taxonomy

| Code | Pathology | Symptom | Fix |
|------|-----------|---------|-----|
| `P-DRIFT` | Route drift | Answer started architecture but ended STAR | Tighten card 01 routing or add tie-breaker |
| `P-CITE-MISS` | Citation miss | Made a claim about Acme with no `[S#]` | Add the source to card 19; rebuild |
| `P-OVERPOLISH` | Over-polish | Answer sounded scripted; lost first-person credibility | Soften phrasing in `_always_on_header.md.j2`; remove forced summaries |
| `P-LATENCY` | Latency | Took >10s to start the answer | Memorize the answer-shape skeleton in the relevant primary card |
| `P-DEPTH-MISS` | Depth miss | Cross-exam pushed deeper than the prep card supported | Add specifics to card 16 cross-exam depth anchors |
| `P-PROOF-MISS` | Proof miss | STAR story did not match the question | Add or reweight a story in card 14 STAR bank |
| `P-RCA-MISS` | RCA miss | Failure question landed on the wrong story | Add to card 15 RCA bank |
| `P-OFFENSIVE` | Offensive framing | Answer triggered an avoid-phrase from card 04 | Reinforce avoid list and rebuild |
| `P-ETHICS` | Ethics drift | Hinted at fabrication or undisclosed assistance | Re-read card 18 before the next mock |

## Delta sheet
After the rehearsal, capture:

- **Question that drifted**: <write here>
- **Pathology code**: `<P-...>`
- **Card to edit**: `<filename>`
- **Specific change**: <what to add or remove>

Repeat for every drift. Carry the deltas forward into the next build.

## Self-eval workflow
Run `python -m apps_qna self-eval --pack <output_dir> --previous <prior_pack>` to get an automatic delta report between two builds. The CLI surfaces:

- Cards that changed
- New routes covered
- New STAR or RCA stories
- Source-register diffs

Use the report alongside this learnings card to decide which pathologies have been addressed and which are still open.
