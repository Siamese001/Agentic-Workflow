# Apps RG evaluation contracts

`apps_rg/evals` evaluates sealed Apps RG artifacts. It does not launch the
resume-generation runtime, change retrieval, or authorize a release merely by
producing a score.

The versioned measurement contract is
[`contracts/evaluation_contract.v2.yaml`](contracts/evaluation_contract.v2.yaml).
It keeps six evaluation questions independent:

| Gate | Question | Current implementation state |
| --- | --- | --- |
| G1 - Retrieval | Did the graph retrieve the most relevant available evidence? | Active; legacy W6 metrics are preserved and the finite-universe API adds coverage, hard-negative, and slice results. |
| G2 - Binding | Was evidence bound to the correct employer, role, date, metric, credential, and graph path? | Active; the claim-evidence API verifies seven exact binding dimensions and graph paths. |
| G3 - Grounding | Is every material generated claim supported by exact cited evidence? | Active; the material-claim API recomputes support and fails closed on incomplete evidence. |
| G4 - Output quality | Is the resume relevant, natural, concise, credible, ATS-compatible, and personalized? | Partial; the five-lane section benchmark is active, while whole-resume and W9 scoring remain unmeasured. |
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
- [`schemas/claim_evidence_record.v1.schema.json`](schemas/claim_evidence_record.v1.schema.json)
  freezes one material claim, exact locator, path, entailment, and factual
  bindings. Additional runtime-authored support flags are rejected.
- [`schemas/retrieval_universe.v1.schema.json`](schemas/retrieval_universe.v1.schema.json)
  freezes one query and every candidate in its finite labelled universe.

## Grounding, binding, and retrieval APIs

`apps_rg.evals.resume_graph` exports the Wave 3 entry points:

- `seal_claim_evidence_record` and `evaluate_claim_evidence` operate on one
  claim-evidence record. `evaluate_binding_gate` and `evaluate_grounding_gate`
  emit independent G2 and G3 dispositions over the same complete denominator.
- `seal_retrieval_query` freezes the candidate denominator.
  `evaluate_retrieval_query` preserves Recall and nDCG at 1, 3, 5, and 10,
  adds coverage and hard-negative metrics, and never evaluates only emitted
  Top-K. `evaluate_retrieval_gate` requires distinct calibration and holdout
  sets and reports governed slices.

The deterministic rubrics live in
[`contracts/grounding_binding_rubric.v1.yaml`](contracts/grounding_binding_rubric.v1.yaml)
and
[`contracts/retrieval_coverage_rubric.v1.yaml`](contracts/retrieval_coverage_rubric.v1.yaml).
They are future-run-only measurement rules; they do not promote thresholds or
change W6 release authority.

## Section quality benchmark

[`section_quality_benchmark/`](section_quality_benchmark/) provides the active
five-lane offline G4 section evaluator. It consumes sealed artifacts and
completed absolute or blinded pairwise reviews, keeps human and model-judge
results separate, and emits no runtime or release authority. Whole-resume and
W9 scoring remain outside this benchmark and are still unmeasured.
