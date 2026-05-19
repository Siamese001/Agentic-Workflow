# L6 Public Bootstrap Sourcing — W9a Report

**Report date:** 2026-05-18  
**Status:** PASS  
**proof_eligible:** false

---

## Summary

Registered the **public_bootstrap** weak-label lane for apps_rg L6 benchmarks: source registry (5 candidates), weak-label contract, import eligibility rules, and schema notes. **No datasets downloaded or ingested** in this wave.

## Artifacts

| Artifact | Path |
|----------|------|
| Lane README | [README.md](../../artifacts/apps_rg/benchmarks/public_bootstrap/README.md) |
| Source registry | [source_registry.json](../../artifacts/apps_rg/benchmarks/public_bootstrap/source_registry.json) |
| Weak-label contract | [weak_label_contract.md](../../artifacts/apps_rg/benchmarks/public_bootstrap/weak_label_contract.md) |
| Schema notes | [public_bootstrap_sample_schema_notes.md](../../artifacts/apps_rg/benchmarks/public_bootstrap/public_bootstrap_sample_schema_notes.md) |

## Registered sources (5)

1. **netsol/resume-score-details** — LLM-scored resume–JD match; dry-run / shape only  
2. **CareerCorpus** — category annotations; taxonomy/schema tests  
3. **Kaggle resume examples** — negative controls / PII gates when license permits  
4. **O*NET** — JD taxonomy / rubric stress  
5. **Academic small-n relevance** — ranking dry-run only; not section-judge calibration  

All entries: `calibration_eligible: false`, `license_status` pending or unknown (no approved imports yet).

## Upstream

- [l6_reviewer_score_ingest_w8b_manifest.json](l6_reviewer_score_ingest_w8b_manifest.json) — human score template; public data must not populate `human_scores`

## Non-claims

- public_bootstrap is **not** calibration proof  
- No Spearman/Cohen computed  
- No runtime or agentic_core changes  

## Receipt

[l6_public_bootstrap_sourcing_w9a_manifest.json](l6_public_bootstrap_sourcing_w9a_manifest.json)
