# Pathology Taxonomy — apps_qna

Codes for diagnosing rehearsal and live-interview drift. Used in card 22
(Learnings and Delta Sheet) and the `apps_qna self-eval` CLI report.

## Codes

| Code | Pathology | Symptom | Fix locus |
|------|-----------|---------|-----------|
| `P-DRIFT` | Route drift | Answer started architecture but ended STAR | `01_routing_manifest`, tie-breaker rules |
| `P-CITE-MISS` | Citation miss | Made a claim about the company with no `[S#]` | `19_source_register`, `04_company_overlay` |
| `P-OVERPOLISH` | Over-polish | Answer sounded scripted; lost first-person credibility | `_always_on_header` |
| `P-LATENCY` | Latency | Took >10s to start the answer | Memorize answer-shape skeleton in primary card |
| `P-DEPTH-MISS` | Depth miss | Cross-exam pushed deeper than the prep card supported | `16_cross_exam` depth anchors |
| `P-PROOF-MISS` | Proof miss | STAR story did not match the question | `14_star_bank` |
| `P-RCA-MISS` | RCA miss | Failure question landed on the wrong story | `15_rca` |
| `P-OFFENSIVE` | Offensive framing | Answer triggered an avoid-phrase | `04_company_overlay` |
| `P-ETHICS` | Ethics drift | Hinted at fabrication or undisclosed assistance | `18_ethics_and_disclosure` |

## How to use

1. After each rehearsal, walk through the questions that drifted.
2. Tag each with one or more pathology codes.
3. Edit the indicated card.
4. Rebuild the pack.
5. Run `python -m apps_qna self-eval --pack <new> --previous <old>` to confirm
   the change landed in the delta report.

## Severity

These codes do not have a fixed severity ladder; they are diagnostic, not
deterministic. A `P-CITE-MISS` is a high-priority fix in a research-heavy
panel; a `P-OVERPOLISH` is high-priority in a culture-fit conversation.
Severity is a function of audience and route.

## Related

- Card 22 — `apps_qna/templates/22_learnings.md.j2`
- CLI — `python -m apps_qna self-eval`
- Disclosure boundary — `apps_qna/templates/18_ethics_and_disclosure.md.j2`
