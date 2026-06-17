# ADR-101: Sub-Stage Telemetry in HowTrace Schema

**Status**: ACCEPTED
**Date**: 2026-05-07
**Phase**: W2 (agentic-spine-diagram-refinement-a3f7c2)
**Deciders**: Codex + user Author-Gate
**ADG Snapshot**: `artifacts/adg/adg_indexed_20260507.sqlite`

---

## Context (SCQA)

- **Situation**: The L7 HowTrace schema (v1.0) recorded stage-level
  outcomes (e.g., `C0_CONTEXT: PASS`, `L2_EXECUTE: PASS`) but had no
  mechanism to record sub-stage detail. The spine diagram showed
  sub-stages (X1A–X1J, C0.1–C0.6, L2 E1–E5) but the telemetry was flat.

- **Complication**: Without sub-stage telemetry, operators could not
  determine which specific gate or step caused a failure. A `DENY` on
  X1 could be any of 10 sub-gates with no way to disambiguate from the
  HowTrace artifact alone.

- **Question**: How should sub-stage execution detail be recorded in the
  HowTrace schema?

- **Answer**: Add a `sub_stages` array to each stage entry in the HowTrace
  schema (v1.1), with `SubStageRecord` containing `sub_stage_id`, `status`,
  `duration_ms`, and optional `meta`.

---

## Decision

Extend the HowTrace schema to v1.1 with sub-stage telemetry:

1. Add `SubStageRecord` dataclass with fields: `sub_stage_id`, `sub_stage_name`,
   `status` (PASS/FAIL/BYPASSED), `duration_ms`, `meta` (optional dict).
2. Add `sub_stages: list[SubStageRecord]` to the stage entry schema.
3. Instrument sub-stage boundaries in:
   - C0 grounding (6 steps: C0.1–C0.6) via `c0_bypass_receipt`
   - L2 execution (5 steps: E1–E5) via `terminal_ret_packet`
   - X1 exit gates (10 gates: X1A–X1J) via `exit_review_packet`

---

## Consequences

### Positive
- Operators can trace failures to specific sub-stages from the HowTrace artifact.
- Spine diagram sub-stage nodes now have corresponding telemetry.
- Schema is backward-compatible (new field, no breaking changes).

### Negative
- HowTrace artifact size increases (~2KB per run with sub-stage data).
- Instrumentation adds ~0.1ms overhead per sub-stage boundary.

### Neutral
- X1 sub-stages only populate when preflight passes (honest fail-closed).

---

## Alternatives Considered

1. **Separate sub-stage artifact**: Would fragment the audit trail across
   multiple files. Rejected — single HowTrace artifact is the SSOT.
2. **Nested stage hierarchy**: Would require schema redesign. Rejected —
   flat `sub_stages` array is simpler and sufficient.
3. **Log-based sub-stage tracking**: Would require log parsing for analysis.
   Rejected — structured JSON is queryable without log infrastructure.

---

## References

- Plan: `.claude/plans/agentic-spine-diagram-refinement-a3f7c2.md` W2
- Schema: `agentic_core/L7_auditability/contracts/how_trace.py`
- Builder: `agentic_core/L7_auditability/how_trace/how_trace_builder.py`
- Verification: W4 (HowTrace v1.1 confirmed)
