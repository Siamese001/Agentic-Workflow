"""ADG integration ingesters — Waves 8-13.

Each ingester augments a freshly built ADG SQLite snapshot with new
edge types that originate from runtime / dynamic / external sources.

Wave-to-module mapping:
  W8  — calls_ingester.py        : adds calls edges (decorator + type-annotation resolution)
  W9  — otel_ingester.py         : adds runtime_trace edges from OTel JSONL
  W10 — branch_coverage_bridge.py: adds branch-level covers edges from coverage.json
  W11 — secret_access_ingester.py: adds reads_secret edges from runtime sidecar
  W12 — hitl_decision_ingester.py: adds hitl_decision edges from Author-Gate ledger
  W13 — profiling_bridge.py      : adds profiler-derived calls edges from .pstats

Each module exports `ingest(sqlite_path: Path, source: Path | None = None) -> int`
returning the number of edges inserted. All ingesters are idempotent (dedup by
src_id + dst_id + relation_type + line_no).
"""
