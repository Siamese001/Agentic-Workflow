# Critical-grader validity (G6)

This package runs repository-owned sealed fixtures through the actual G1, G2,
and G3 evaluation functions. Clean controls must pass. Controlled critical
defects must fail or, for invalid provenance, be rejected fail-closed as
`UNKNOWN` with the expected stable reason.

Run:

```text
python -m apps_rg.evals.meta_eval --out g6-receipt.json
```

The machine-critical receipt measures mutation recall, clean-control false
positives, deterministic score stability, critical slice coverage, unexpected
required `UNKNOWN`, and leakage/mutation failures. Human and model-judge
agreement dimensions remain explicitly unmeasured until authorized labels
exist. A machine `PASS` does not create human labels, freeze agreement
thresholds, or authorize release.
