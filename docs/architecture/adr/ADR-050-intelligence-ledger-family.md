# ADR-050 — Intelligence Ledger Family

- **Status**: Accepted
- **Decision Date**: 2026-04-24
- **Deciders**: Cursor Agent + operator
- **Impact Layers**: L6 (Observability), L0 (Routing — consulters surface in prompt context)
- **Supersedes**: None
- **Related**: ADR-023 (Runtime HITL — distinct from harness-side Author-Gate), ADR-031 (Priority scoring operational signals), ADR-019 (ADG materialized views)
- **Plan**: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`

## Context

The Author-Gate decision ledger (`.windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite`)
captures developer-loop decisions as `(prediction, outcome, latency, metadata)` rows and
feeds the `refactor-decision-memory` skill. This pattern demonstrably biases future
decisions toward precedent — but it is the *only* feedback loop of its kind in the harness.

Ten other high-leverage decisions happen dozens of times per session without any
outcome capture:

1. Retrieval-tool choice (grep vs ADG vs vector)
2. Refactor-wave outcome (predicted vs actual P-count delta)
3. Prompt-tier classification (T0/T1/T2/T3)
4. MCP invocation latency / retry / hang attribution
5. Hotspot prediction vs 30-day defect density
6. Deferred-scope P-band vs days-to-done
7. Guardian-exemption lifecycle and RCA attribution
8. Progress-bar ETA vs actual duration
9. Memory-recall entity hit rate in session
10. Test-selection triage precision/recall

Without these, formula tuning (layer_multiplier, surface_boost, band thresholds) is
doctrinal rather than empirical, and the harness cannot self-correct drift.

## Decision

Introduce a **family of ten intelligence ledgers** under `artifacts/ledgers/`, each a
SQLite file conforming to the shared base schema at `.windsurf/schemas/ledger_base.schema.sql`
and registered in `tools/ledgers/schema_registry.py`. Each ledger has:

- A **per-ledger schema extension** in `.windsurf/schemas/<name>_ledger.schema.sql`
  that documents its `prediction_json`, `outcome_json`, and `score_band` taxonomy.
- A **writer hook** that appends rows (typically an existing post-hook, extended).
- A **consulting skill** at `.windsurf/skills/ledger-consulter-<name>/SKILL.md` invoked
  before making a decision of that class.
- A **weekly calibration entry** in `ops_scripts/calibration/ledger_weekly_report.py`
  emitting a unified report to `docs/reports/calibration/<YYYY-Www>.md`.
- A **CI gate** (`ops_scripts/ci/check_ledger_writer_contract.py`) validating schema,
  writer hook, and consulting-skill existence.
- A **sunset criterion** encoded in `LedgerSpec.sunset_criterion` — observable conditions
  under which the ledger retires (mirrors the `mcp-serialization.md` TTL pattern).

## Design Invariants

| Invariant | Enforcement |
|---|---|
| SQLite is canonical; no remote DB | `LedgerSpec.db_path` under `artifacts/ledgers/` only |
| Writer is fail-soft | Never raises to caller; stderr on error; empty `event_id` on bypass |
| Writer is idempotent | `event_id` = SHA-256 of `(kind, ts, repo_area, prediction_json)` |
| Writer respects bypass | `LEDGER_WRITER_BYPASS=<name>` or `=1`/`=all` disables |
| Consulter is pure-read | No ledger mutation in `LedgerConsulter.lookup` |
| Precedent budget ≤500 tokens | Top-3 matches only per consulting skill |
| Schema is additive | `apply_schema.py` only runs `ALTER TABLE ADD COLUMN` — never DROP or RENAME |
| Base tables are protected | `events`, `event_scope`, `events_fts`, `schema_version` exist in every ledger |

## Alternatives Considered

### Alternative 1 — One unified mega-ledger

Single `artifacts/ledgers/all.sqlite` with an `event_kind` discriminator. Rejected:
operators cannot reason about a single growing DB; per-ledger DB file makes size,
retention, and sunset independently manageable; also mirrors existing
`adg_indexed_<ts>.sqlite` and `refactor_decision_ledger.sqlite` discipline.

### Alternative 2 — Extend the existing decision ledger

Bolt new event kinds onto `refactor_decision_ledger.sqlite`. Rejected: schema divergence
risk, blast radius on the existing ledger's integrity checker, and conceptual coupling
of developer-loop Author-Gate with runtime/operational telemetry the operator never sees.

### Alternative 3 — OpenTelemetry metrics instead of SQLite rows

Emit metrics via `otel_mcp` and query from a TSDB. Rejected: precedent lookup
(the primary consumer) is a row query, not an aggregation query; no TSDB is currently
part of the harness; and OTEL trace context propagation is explicitly N/A for stdio MCP
transports.

## Consequences

### Positive

- Every major decision class gets an empirical feedback loop.
- Cursor Agent queries precedent via consulting skills — same proven pattern as
  `refactor-decision-memory`, now generalized.
- Unified weekly report centralizes drift signals in one ≤6KB Markdown file.
- Sunset criteria prevent ledger sprawl.

### Negative / Accepted Risks

- Ten new SQLite files increase artifact count (accepted; mitigated by unified report).
- Writer adds latency to hot hook paths (hard-capped at 20% p95 budget; bypass env var
  provides emergency kill-switch).
- Hotspot-vs-Defect ledger needs a 30-day observation window before useful output
  (mitigated with historical seed from snapshot archive).

### Neutral

- Ten new consulting skills swell the skills index. The `ledger-consulter` base skill
  holds the contract; per-ledger skills stay <80 lines each.

## Retirement

Each ledger retires independently when its sunset criterion holds. The ADR itself is
retired when ≥8/10 ledgers have sunset — at which point the family returns to status
"superseded by empirical coefficient stability."

## References

- Plan: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
- Base DDL: `.windsurf/schemas/ledger_base.schema.sql`
- Registry: `tools/ledgers/schema_registry.py`
- Writer: `tools/ledgers/writer.py`
- Consulter: `tools/ledgers/consulter.py`
- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- CI gate: `ops_scripts/ci/check_ledger_writer_contract.py`
- Weekly report: `ops_scripts/calibration/ledger_weekly_report.py`
- Precedent for this pattern: `.windsurf/schemas/decision_ledger.schema.sql`,
  `.windsurf/skills/refactor-decision-memory/SKILL.md`
