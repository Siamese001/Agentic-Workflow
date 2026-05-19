# L6 Benchmark Collection & Reviewer Workflow — W4 Report

**Report date:** 2026-05-18  
**Status:** DESIGN_ONLY  
**proof_eligible:** false  

---

## What was added

| Artifact | Path |
|----------|------|
| Collection workflow | [collection_workflow.md](artifacts/apps_rg/benchmarks/collection_workflow.md) |
| Reviewer scoring guide | [reviewer_scoring_guide.md](artifacts/apps_rg/benchmarks/reviewer_scoring_guide.md) |
| Holdout split strategy | [holdout_split_strategy.md](artifacts/apps_rg/benchmarks/holdout_split_strategy.md) |
| W4 manifest | [l6_benchmark_collection_workflow_w4_manifest.json](docs/reports/apps_rg/l6_benchmark_collection_workflow_w4_manifest.json) |

**Receipt (hyperlinked):** [l6_benchmark_collection_workflow_w4_receipt.md](docs/reports/apps_rg/l6_benchmark_collection_workflow_w4_receipt.md)

**Upstream inputs (unchanged):**

- [human_benchmark_plan.md](artifacts/apps_rg/plans/human_benchmark_plan.md)
- [human_benchmark_schema.json](artifacts/apps_rg/plans/human_benchmark_schema.json)
- [benchmarks README](artifacts/apps_rg/benchmarks/README.md) + [examples/](artifacts/apps_rg/benchmarks/examples/)
- [l6_benchmark_fixture_layout_w3_manifest.json](docs/reports/apps_rg/l6_benchmark_fixture_layout_w3_manifest.json)

---

## Why this remains design-only

- Defines **process** for collection, review, splits, and calibration report I/O — no pipeline code, no runtime hooks.
- No real samples ingested; no `human_scores` written; no public datasets downloaded.
- No Spearman rho, Cohen kappa, or promotion decisions — thresholds are documented targets only.
- No changes to `agentic_core`, `apps_rg/runtime`, X1D/X2/X3/Exit/UWG/L4/L6 code.

---

## How W5 should proceed (recommended)

1. **Collection tooling** — Script or operator runbook to extract completed-run sections into schema-valid JSON under `benchmarks/<section_group>/<split>/`.
2. **PII gate** — Checklist + optional script to set `pii_status=cleared` before split assignment.
3. **Split assigner** — Stratified 60/20/20 assigner implementing `holdout_split_strategy.md`; seal `drift_holdout_manifest.json`.
4. **Reviewer packet exporter** — Blind packets from calibration + validation rows (no judge scores).
5. **Score ingest** — Merge dual-reviewer JSON into `human_scores` with kappa pre-check.
6. **Calibration report job** — Offline job producing `calibration_report.json`, `false_pass_fail_rates.json`, `slice_metrics.json` — still **no** auto-promotion; L6 ProposalPacket → UWG only.

W5 may start with **synthetic dry-run** rows (non-PII) in `calibration` split only — still not promotion-eligible until real dual-human labels exist.

---

## Open gaps

| Gap | Notes |
|-----|-------|
| Collection pipeline not implemented | Workflow doc only |
| Reviewer UX / forms not built | Guide only |
| Split assigner not implemented | Strategy doc only |
| drift_holdout manifest not sealed | W5+ |
| Calibration report job not implemented | I/O spec in collection_workflow.md |
| `split_assignment` schema field | Optional future schema bump |
| Judge `calibration_status` promotion | Blocked until metrics + UWG |

---

## Non-claims

- No real samples collected  
- No human labels collected  
- No judges promoted  
- No Spearman rho or Cohen kappa computed  
- No runtime behavior changed  
- No calibration complete  

See [l6_benchmark_collection_workflow_w4_manifest.json](docs/reports/apps_rg/l6_benchmark_collection_workflow_w4_manifest.json) and [l6_benchmark_collection_workflow_w4_receipt.md](docs/reports/apps_rg/l6_benchmark_collection_workflow_w4_receipt.md) for command receipts.
