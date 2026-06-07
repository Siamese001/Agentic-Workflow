# Artifact Provenance Discipline — Never Present a Wrong-Run Artifact

> ⛔ Before presenting ANY JSON artifact as evidence for a specific run, Cursor Agent MUST
> verify the artifact's identity fields match the run under analysis. Substituting a
> nearest-match artifact without explicit disclosure is FORBIDDEN.

## The Failure Pattern This Rule Prevents

Cursor Agent fetches artifact `X` (from run A) and presents it as evidence for run B without
checking `run_id`, `emitted_at`, or `request_id`. The user receives fabricated analysis
that describes a different execution path entirely.

Incident: 2026-05-07 — `certification/integrated_runtime/r4_latest/agentic_core_how_trace.json`
(R1B cache-hit, emitted 2026-05-02) was presented as the HowTrace for a live R4 generation
run from `apps_rg/runs/20260507_085435/`. L2 "BYPASSED" was narrated for a run where L2
fully executed. RCA filed same session.

## Hard Rules

### 1. Verify identity fields before citing any artifact

When analyzing a specific run (identified by run dir, run_id, timestamp, or user description),
ANY artifact cited as evidence MUST have its identity fields verified:

| Artifact type | Fields to verify |
|---|---|
| `agentic_core_how_trace.json` | `run_id`, `emitted_at`, `route_contract_id` |
| `validated_request.json` | `run_id`, `request_id` |
| `runtime_identity_envelope.json` | `run_id`, `started_at_utc` |
| Any scorecard / candidate JSON | `generated_at`, `section_id` |
| Any `*_receipt.json` | `run_id` |

### 2. Absent artifact → state absence, do not substitute

If the target run dir does NOT contain the expected artifact (e.g. no `agentic_core_how_trace.json`
in `runs/20260507_085435/`):

- MUST state: **"This run did not emit [artifact]. No HowTrace exists for this run."**
- MUST NOT silently substitute an artifact from another run dir or certification fixture
- MAY note where similar artifacts exist for reference, WITH explicit disclosure that they
  are from a different run

### 3. Cross-run citation requires explicit disclosure

If citing an artifact from a different run for comparison or context:

> "Note: this artifact is from run `<run_id>` (`<emitted_at>`), NOT from the run under analysis."

This disclosure MUST appear before any content derived from the artifact.

### 4. `certification/integrated_runtime/` dirs are fixture artifacts

Paths under `artifacts/certification/integrated_runtime/` are certification harness fixtures,
NOT live run artifacts. They MUST NOT be cited as evidence for any user-initiated run without
the cross-run disclosure in Rule 3.

## Verification Procedure

Before citing any artifact:

1. Read the target run dir first — confirm what artifacts exist there
2. If the target artifact exists in the run dir → verify its `run_id` matches
3. If it does not exist → state absence explicitly (Rule 2)
4. If citing from elsewhere for reference → apply Rule 3 disclosure

## Forbidden Patterns

- ❌ Presenting `r4_latest/agentic_core_how_trace.json` as evidence for a run in `apps_rg/runs/<date>/`
- ❌ Narrating stage statuses (RAN / BYPASSED) from a different run's trace without disclosure
- ❌ Using `find_by_name` results to pick "closest matching" artifact without reading its identity fields
- ❌ Presenting `success: true/false` from a fixture artifact as the outcome of a user's live run

## References

- Constitutional §20 (fact grading: DIRECTLY OBSERVED / DERIVED / UNRESOLVED)
- RCA 2026-05-07: incorrect HowTrace attribution for apps_rg Brown & Brown run
