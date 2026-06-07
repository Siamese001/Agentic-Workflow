
<!-- Converted from `.claude/rules/intelligence-ledger-family.md`. Original Cursor trigger: `model_decision`. -->

# Intelligence Ledger Family — Writer and Consulter Invariants

> ⛔ **Scope**: the ten ledgers registered in `tools/ledgers/schema_registry.py`.
> Non-negotiable rules for every hook, calibration job, or skill that touches
> `artifacts/ledgers/<name>.sqlite`. See ADR-050 for rationale.

## 1. Writer Discipline

All writes go through `tools.ledgers.hook_helpers.emit_ledger_event` or
`tools.ledgers.writer.LedgerWriter`. **Never** open a ledger DB with raw
`sqlite3.connect()` from a hook. Raw writes bypass fail-soft, idempotency, and
thread-safety contracts.

```python
from tools.ledgers.hook_helpers import emit_ledger_event
event_id = emit_ledger_event(
    ledger="<name>",
    event_kind="<ledger-specific-kind>",
    prediction={...},         # JSON-serializable
    outcome={...},            # optional — bind later via bind_ledger_outcome
    score_band="<band>",      # optional
    repo_area="<file/module>",
)
```

### Fail-Soft Contract (non-negotiable)

- Every writer call **MUST** be wrapped in `try/except Exception` with a
  `# guardian: allow-broad-except -- hook fail-soft contract` comment.
- The `except` block **MUST** be `pass` or a stderr log — never re-raise,
  never mutate hook state, never abort downstream processing.
- Hooks that violate this discipline break the fail-open property of the
  entire post-cursor_agent chain.

### Idempotency

`event_id` is `SHA-256(event_kind, ts_utc, repo_area, prediction_json)[:32]`.
Multiple calls with identical inputs **MUST** collapse to one row. Callers
that need a new row on retry **MUST** vary `ts_utc` or `prediction`.

### Bypass Discipline

The `LEDGER_WRITER_BYPASS` environment variable disables writes:

- `=1` or `=all` → all ledgers bypassed
- `=<name>,<name>` → specific ledgers bypassed

Bypass is for scripted batch runs or acknowledged exploratory sessions only.
Every bypass is silent (no stderr log) to avoid polluting hook output.

## 2. Consulter Discipline

Reading ledger precedent happens **before** acting, not after:

```python
from tools.ledgers import LedgerConsulter
verdict = LedgerConsulter("<name>").lookup(
    query_text="<current intent>",
    filters={"event_kind": "<class>"},
    limit=5,
)
if verdict.strength == "strong":
    # bias current decision toward precedent
```

### Verdict → Action (non-negotiable)

| `verdict.strength` | Required behavior |
|---|---|
| `strong`      | Bias current decision; note alignment in Author-Gate packet or plan body |
| `suggestive`  | Surface precedent without auto-biasing |
| `none`        | State explicitly: `Precedent: ledger had no match (novel case).` |

### Precedent Budget

Consulting-skill output **MUST NOT** exceed 500 tokens of precedent text
added to the prompt context. Top-3 matches only. Larger dumps crowd the
context window and defeat the W0 design goal of a lean recall layer.

## 3. Schema Discipline

- All DDL changes go through `.cursor/schemas/ledger_base.schema.sql` or
  `.cursor/schemas/<name>_ledger.schema.sql`.
- `tools/ledgers/apply_schema.py` is the **only** schema applier. Never
  run DDL ad-hoc.
- Schema changes are **additive only**: `ALTER TABLE ADD COLUMN` is the
  sole migration primitive. No `DROP`, no `RENAME`, no destructive change.
- The four base tables (`events`, `event_scope`, `events_fts`,
  `schema_version`) **MUST** exist in every ledger — enforced by
  `ops_scripts/ci/check_ledger_writer_contract.py`.

## 4. Sunset Criteria

Every `LedgerSpec` in `tools/ledgers/schema_registry.py` declares an
observable `sunset_criterion`. When that condition holds for the stated
duration, the ledger retires via the same lifecycle as the
ledger TTL config pattern:

1. Operator writes `.cursor/config/ledger_ttl_<name>.json` with
   `{retired_after: "<UTC-date>", evidence: "...", verified_by: "..."}`.
2. The writer's `_bypass_active()` check reads that file and no-ops the
   ledger after `retired_after`.
3. The entry is removed from `LEDGER_REGISTRY` after one full review cycle.

## 5. Calibration Evidence → Threshold Tuning (W5, plan c8f4a2)

Each weekly report at `docs/reports/calibration/<YYYY-Www>.md` includes a
**Per-Band Calibration Curve** per ledger. When that curve produces actionable
signal (Wilson 95% CI does not overlap the band's nominal range), follow this
deterministic ritual:

| Evidence pattern | Action | Author-Gate? |
|---|---|:---:|
| Band has `n < 20` | Wait — sample too small to act on | No |
| Band has `n ≥ 20` AND CI overlaps nominal range | Confirm calibration; no change | No |
| Band has `n ≥ 20` AND CI miss is `< 0.05` | Auto-tune scorer threshold up to 0.05 | No |
| Band has `n ≥ 20` AND CI miss is `≥ 0.05` | **STOP — Author-Gate required** | **Yes** |
| ≥2 bands mis-calibrated in same ledger | **STOP — Author-Gate required** | **Yes** |

**Why this split?** Small adjustments (≤0.05) within a single band fall inside
normal stochastic drift; auto-tuning preserves momentum. Large miscalibrations
or systemic miscalibrations (multiple bands in one ledger) reveal the scoring
formula itself is wrong — that's an architectural decision, not a parameter
tweak, and must be surfaced via Author-Gate per `author-gate-enforcement.md`.

**Decision-type for the Author-Gate**: `architecture_choice` (re-scoring
formula) — not `parameter_tune`. Surface the affected band, the empirical
success rate with CI, and the candidate fixes (re-weight features, change
band boundaries, retire the metric). Capture under
`DECISION_CAPTURED: type=architecture_choice, repo_area=tools/calibration/<ledger>, …`.

## 6. Enforcement Layers

| Layer | Mechanism |
|---|---|
| Advisory (this file) | `model_decision` rule, loaded on demand |
| Deterministic | `ops_scripts/ci/check_ledger_writer_contract.py` (CI + pre-commit) |
| Schema drift | `python -m tools.ledgers.apply_schema --check` |
| Weekly visibility | `ops_scripts/calibration/ledger_weekly_report.py` → `docs/reports/calibration/<YYYY-Www>.md` |
| Calibration freshness | `ops_scripts/ci/check_weekly_calibration_freshness.py` (8-day window, W4.3) |
| Notion writeback | `tools/calibration/post_weekly_summary.py` → `artifacts/calibration/weekly_summary_<week>.json` (Cursor Agent-dispatched, W4.2) |
| Calibration math | `tools/calibration/loop_metrics.py` (Wilson CI, banding, W2 SSOT) |
| Coverage audit | `ops_scripts/ci/check_ledger_coverage.py` (future) |

## 7. References

- **Plan**: `.cursor/plans/intelligence-ledgers-ten-a7c3e2.md`
- **ADR**: `docs/architecture/adr/ADR-050-intelligence-ledger-family.md`
- **Base schema**: `.cursor/schemas/ledger_base.schema.sql`
- **Registry**: `tools/ledgers/schema_registry.py`
- **Writer / Consulter / Helpers**: `tools/ledgers/{writer,consulter,hook_helpers}.py`
- **Base consulting skill**: `.claude/skills/ledger-consulter/SKILL.md`
