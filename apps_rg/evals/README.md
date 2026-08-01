# Apps RG evaluation contracts

`apps_rg/evals` evaluates sealed Apps RG artifacts. It does not launch the
resume-generation runtime, change retrieval, or authorize a release merely by
producing a score.

The versioned measurement contract is
[`contracts/evaluation_contract.v2.yaml`](contracts/evaluation_contract.v2.yaml).
It keeps six evaluation questions independent:

| Gate | Question | Current implementation state |
| --- | --- | --- |
| G1 - Retrieval | Did the graph retrieve the most relevant available evidence? | Implemented by the existing resume-graph evaluator and human labels. |
| G2 - Binding | Was evidence bound to the correct employer, role, date, metric, credential, and graph path? | Partial; the existing evaluator covers path, entailment, metric binding, and target relevance. |
| G3 - Grounding | Is every material generated claim supported by exact cited evidence? | Partial; the complete material-claim gate is a later wave. |
| G4 - Output quality | Is the resume relevant, natural, concise, credible, ATS-compatible, and personalized? | Scaffold only; the existing section schemas do not constitute a completed benchmark. |
| G5 - Robustness | Is behavior acceptable across stored runs and difficult evidence scenarios? | Not measured. |
| G6 - Eval validity | Do the graders catch known defects without rejecting clean controls? | Not measured. |

## Result semantics

Every gate emits exactly one state:

- `PASS`: all required evidence exists and the gate's governed criteria pass.
- `FAIL`: sufficient evidence exists and at least one governed criterion fails.
- `UNKNOWN`: the gate should be measurable, but required evidence is missing,
  invalid, untrusted, or insufficient.
- `NOT_MEASURED`: the gate is outside the declared measurement coverage of the
  report or has no implemented measurement lane.

Missing evidence never becomes `PASS`. `UNKNOWN` is distinct from
`NOT_MEASURED`, and neither state is release-authorizing.

## Score groups

Reports use the following named groups without calculating a blended overall
score:

- `retrieval_quality`
- `binding_accuracy`
- `factual_grounding`
- `section_quality`
- `whole_resume_quality`
- `runtime_repeatability`
- `evaluator_validity`

The report schemas require all six gates and all seven score groups to be
present. An unavailable lane is represented explicitly as `UNKNOWN` or
`NOT_MEASURED`; it is not omitted.

## Authority boundary

This contract is declarative. It does not change the existing W6 authority,
the six-pair W9 prerequisite contract, current-run release authority, or the
future-run-only threshold-promotion rule. Model judges remain advisory until
calibrated against authorized human review. The existing
`resume_graph_evaluation.py`, `c03_ci_ratchet.py`, and `c03_w9_closeout.py`
entry points retain their current behavior.

Schemas:

- [`schemas/evaluation_gate_result.v1.schema.json`](schemas/evaluation_gate_result.v1.schema.json)
  defines one named gate result.
- [`schemas/evaluation_report.v2.schema.json`](schemas/evaluation_report.v2.schema.json)
  defines a complete, non-blended report over G1-G6.
