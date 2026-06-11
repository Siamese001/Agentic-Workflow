---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\chromadb_coverage_report.md'
original_relative_path: 'chromadb_coverage_report.md'
source_sha256: 8a44eaea08cada329a78962dab51dd423d088d454b1bb518a77a530ae010ea69
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ChromaDB Coverage Report

**Generated:** 2026-04-24T01:26:10+00:00
**ADG snapshot:** `adg_indexed_04232026_2123.sqlite`
**Collection:** `repo_code_chunks` @ canonical store

## Totals

| Source | Count |
|---|---:|
| ADG Symbol nodes (non-test `.py`) | 5879 |
| ChromaDB chunks | 24839 |
| Ratio (chunks / symbols) | 422.50% |

## By Layer

| Layer | ADG Symbols | ChromaDB Chunks | Coverage |
|---|---:|---:|---:|
| `L0` | 504 | 1290 | 256.0% |
| `L1` | 167 | 2123 | 1271.3% |
| `L2` | 335 | 2233 | 666.6% |
| `L3` | 329 | 1895 | 576.0% |
| `L4` | 1949 | 6564 | 336.8% |
| `L5` | 559 | 3946 | 705.9% |
| `L6` | 316 | 1184 | 374.7% |
| `L_APPS` | 409 | 5604 | 1370.2% |
| `L_OPS` | 188 | 0 | 0.0% |
| `L_SYSTEM_LEARNING` | 420 | 0 | 0.0% |
| `L_TOOLS` | 703 | 0 | 0.0% |

## Interpretation

- `Coverage > 100%` means ChromaDB has multiple chunks per ADG symbol (expected — every function/class/method yields one chunk; additional ``*`` module-level symbols show as 1:1 in ADG but 0 chunks here).
- `Coverage == n/a` means ADG has no symbols for that layer — ChromaDB chunks labelled `L_UNKNOWN` belong here.
- `Coverage < 50%` on a populated layer indicates an ingest gap. Run `python -m tools.ingestion.pipeline --only code_<root>` for the affected root.

## Next

Per plan `.windsurf/plans/chromadb-bge-retrieval-hardening-e9aa09.md`: run full pipeline to converge chunk count with ADG symbols, then re-run this report. Target: ≥ 90% layer coverage on every populated layer.
