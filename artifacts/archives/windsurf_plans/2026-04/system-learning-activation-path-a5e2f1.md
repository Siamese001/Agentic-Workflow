# Plan: `system_learning/` Activation Path Investigation + Wiring

**Slug**: `system-learning-activation-path-a5e2f1`
**Status**: Active (investigation phase)
**Tier**: T2
**Created**: 2026-04-23
**Parent gap**: Gap #4 from 2026-04-23 gap review

## The Finding

`system_learning/runtime_hitl_consumer.py` defines a complete, production-ready
`RuntimeHitlConsumer` class with `consume()` and `consume_and_submit()` public
API and 477 lines of well-typed logic that produces `DraftProposal`s from HITL
ledger evidence and routes them via `DraftSink` to UWG for review.

**But nothing calls it at runtime.** Importers (per `git grep -l`):

| Caller | Role |
|---|---|
| `tests/unit/system_learning/test_runtime_hitl_consumer.py` | Unit tests |
| `docs/architecture/adr/ADR-023-runtime-hitl-exit-control.md` | Design doc |
| `docs/architecture/runtime_hitl_soc2_mapping.md` | Compliance doc |
| `docs/contracts/L5_exit_control_hitl.md` | Contract |
| `.windsurf/plans/*.md` (3 plan files) | Historical plans |
| `docs/reports/plans/*.md` (2 reports) | Historical reports |

There is **no import from `agentic_core/`, `apps_*/`, `ops_scripts/`, or
`tools/`** — i.e., no runtime entrypoint invokes the consumer.

Symptom: `system_learning/` persistent state is empty despite a full source
tree. The architecture is scaffolded but inert.

## Scope

1. **Audit**: for each of the 10+ classes in `system_learning/`, determine
   whether anything in a runtime path (`agentic_core/`, `apps_*/`,
   `ops_scripts/`, `tools/`) instantiates or calls it.
2. **Classify** each class as:
   - `LIVE` — wired and firing
   - `DORMANT` — wired but not triggered by current workload
   - `INERT` — no activation path (like `RuntimeHitlConsumer`)
3. **Design an activation path** for `RuntimeHitlConsumer`:
   - When in the lifecycle should `consume()` fire? (Candidates: step [6]
     SHADOW EVAL per v33, end-of-run trigger, scheduled cron, CLI command,
     ADG snapshot hook.)
   - What provides the `HitlQualityReport` input? (Candidates: a new
     `compute_hitl_quality()` function over the existing ledger.)
   - What entity holds the `RuntimeHitlConsumer` instance? (Candidates: a
     new daemon, an existing orchestrator hook, a post-ingest step in
     `otel_services_ingest.py`.)
4. **Wire a minimal activation** — one entrypoint that can be verified end-to-end.
5. **Write an integration test** that exercises the full path: seed ledger
   entries \u2192 trigger activation \u2192 draft files appear in
   `artifacts/runtime/hitl_drafts/`.

## Out of Scope

- Rewriting the consumer logic (it works correctly; only the trigger is missing).
- UWG review workflow implementation (Draft \u2192 review \u2192 commit is a
  separate pipeline outside this plan).
- Activating OTHER `system_learning/` classes (they each need their own
  investigation and may or may not share a trigger).

## Success Criteria

1. Written inventory of which `system_learning/` classes are LIVE / DORMANT / INERT.
2. Concrete activation design for `RuntimeHitlConsumer` (ADR or decision memo).
3. One runtime entrypoint wired (minimum: a CLI invocation via
   `python -m system_learning.runtime_hitl_consumer` or equivalent).
4. Integration test passes: ledger \u2192 consumer \u2192 draft on disk.
5. `artifacts/runtime/hitl_drafts/` is non-empty after the test run.

## Probing Strategy (pre-implementation)

Before wiring, run these probes (each under 5 minutes):

```bash
# 1. Which agentic_core / apps_* files mention system_learning?
git grep -l "system_learning" agentic_core/ apps_exec/ apps_rg/ apps_lic/ apps_research/ apps_rfp/ ops_scripts/

# 2. What do L5 exit-control / L6 learning paths actually invoke?
git grep -l "RuntimeHitlConsumer\|DraftProposal\|DraftSink" agentic_core/ apps_*/

# 3. Inspect system_learning/adapters/ for any inbound/outbound ports.
ls -la system_learning/adapters/ system_learning/ports/ 2>/dev/null

# 4. Is there an existing post-ingest hook in otel_services_ingest?
grep -n "post_ingest\|after_ingest\|consumer" tools/otel/otel_services_ingest.py
```

Expected outcome: probe #1 returns empty (confirming INERT status);
probes #2-4 reveal whether the scaffold has pre-wired seams awaiting activation.

## Deferred-Scope Marker

DEFERRED_SCOPE: plan=NEW:system-learning-activation-path wave=SL phase=SL.P1 layer=L6 fan_in=5 surface=Observability coverage_gap_pct=75.0 est_tokens=8000 reason=Wire RuntimeHitlConsumer activation path; system_learning is architecturally complete but inert at runtime
