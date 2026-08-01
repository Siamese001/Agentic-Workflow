# Stored-run repeatability (G5)

This evaluator reads a sealed `apps_rg.repeatability_run_set.v1` JSON artifact.
It does not run Apps RG or infer that copied artifacts are independent.

Each governed scenario needs at least three distinct execution identities,
three distinct execution-receipt digests, and an explicit independence
attestation. The evaluator compares retrieved candidates, selected evidence,
graph paths, material claim identities, exact bindings, normalized section
decisions, grounding dispositions, final generate/escalate/abstain behavior,
and output-quality scores. Raw text differences are counted separately and do
not require exact prose equality.

Run:

```text
python -m apps_rg.evals.repeatability --run-set sealed-runs.json --out g5-receipt.json
```

`PASS` exits 0; `FAIL` or `UNKNOWN` exits 1. Every receipt is future-run-only
measurement evidence and has `release_authorizing: false`.
