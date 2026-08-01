# Whole-resume and W9 quality evaluation

This package consumes six sealed blinded W9 pairs, their exact structured
whole-resume artifacts, two completed qualified human reviews per pair, and one
adjudication per pair. It never generates a resume, invokes a judge, or mutates
the runtime.

The evaluator calculates material-claim grounding, cross-section and employment
consistency, achievement reuse, summary/experience repetition, target-concept
and achievement coverage, section balance, length/density, ATS structure,
parroting and keyword-insertion risks, unsupported leadership/scope inflation,
and the existing W9 human dimensions. Candidate/baseline identities stay hidden
from reviewers; only the sealed evaluator resolves them.

For each pair it calculates grounding, naturalness, and relevance no-worse
decisions from adjudicated scores. It also reports candidate preference,
reviewer agreement, narrative coherence, and material defects. A PASS requires
exactly six pairs, twelve independent qualified reviews, six adjudications,
official W6 PASS, authorized variant generation, official completed human-review
evidence, every candidate material claim grounded, zero critical consistency or
inflation defects, and all three human no-worse rates at 1.0.

Run:

```text
python -m apps_rg.evals.whole_resume \
  --input sealed-whole-resume-input.json \
  --output whole-resume-evaluation-receipt.json
```

Exit codes are `0` for PASS, `1` for FAIL, `2` for UNKNOWN, and `3` for file or
JSON errors. The receipt is conditionally authoritative input to
`c03_w9_closeout.py`, but it is not current-run release authority by itself and
cannot promote thresholds outside the existing future-run W9 process.

The old `whole_resume_release_pass` closeout argument remains a marked legacy
compatibility path. New W9 closeouts should supply
`whole_resume_evaluation_receipt`; receipt use is explicit in the closeout
output as `whole_resume_gate_source=SEALED_EVALUATION_RECEIPT`.
