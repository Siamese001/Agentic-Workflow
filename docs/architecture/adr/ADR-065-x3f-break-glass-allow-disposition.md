# ADR-065 — X3F BREAK_GLASS_ALLOW disposition resolves H3 X3E naming divergence

**Status**: Accepted
**Date**: 2026-04-26
**Wave**: exit-eval-v6 deferred-scope Wave 1
**Closes**: GAP `H3.GAP.X3E_meaning_diverges` from `docs/reports/plans/exit_eval_v6_MASTER_otel_matrix.md`

---

## Context

The Exit-Eval v6 spec corpus contains a real naming divergence:

| Source | Defines `X3E` as |
|---|---|
| `docs/reference/05_Exit_Evaluation_and_Control/05.5_Exit_Aggregation_and_X3_Disposition.md` | `SAFE_ABSTAIN_CLARIFY` (canonical) |
| `docs/reference/05_Exit_Evaluation_and_Control/v4_hardening_addendum.md` §H3.2.3 | `BREAK_GLASS_ALLOW` (operator emergency override) |

The v6 runtime implementation (`agentic_core/L3_orchestration/exit_eval/v6/types.py`) tracks **05.5** — `V6Disposition.SAFE_ABSTAIN = "X3E"`. The hardening addendum's break-glass proposal collides with this naming.

Both concepts are valid and need a runtime representation:

- **Safe abstain** (X3E) is a normal-path disposition: the agent cannot answer safely and emits a clarification or bounded refusal. Already implemented and tested.
- **Break-glass allow** (proposed X3E by addendum) is an *operator-invoked* emergency override that fast-paths past selected gates with capability-gated authorization, audit trail, and 24h post-mortem requirement.

A single letter cannot mean both.

## Decision

Allocate `X3F` for break-glass and preserve `X3E` for safe-abstain.

**`V6Disposition.BREAK_GLASS_ALLOW = "X3F"`** is the canonical disposition for the v4_hardening §H3 break-glass control. The addendum's §H3.2.3 wording (`X3E BREAK_GLASS_ALLOW`) is **superseded** by this ADR.

Rationale:

1. **Canonical 05.5 is older and ships in v6 runtime today** — renaming `X3E` would break backwards compatibility, the existing 394 v6 tests, the Notion ledger entries, and the matrix evidence trail.
2. **Break-glass needs distinct runtime semantics** — it cannot route through `aggregate_decision` like X3A-X3E because it is operator-invoked, not gate-driven. A separate enum value makes the dispatch refusal explicit (see `build_x3_packet` rejecting `BREAK_GLASS_ALLOW` with a clear error).
3. **Distinct packet shape** — `X3BreakGlassAllowPacket` carries fields that have no analog in `X3SafeAbstainPacket` (operator_id, capability_token_ref, written_justification, expiry_ms, audit_id, post_mortem_due_at_ms, customer_facing_l4_commit_allowed). Sharing one enum value would force a union packet with optional-everywhere fields and lose the H3 invariant guarantees at type level.

The addendum reference docs MAY be updated in a separate doc-only commit to reflect the X3F naming. This ADR is the SSOT for the runtime contract.

## Implementation

### Type system (`agentic_core/L3_orchestration/exit_eval/v6/types.py`)

```python
class V6Disposition(str, Enum):
    DENY = "X3A"
    ESCALATE = "X3B"
    COMMIT_REQUEST = "X3C"
    ALLOW = "X3D"
    SAFE_ABSTAIN = "X3E"           # canonical 05.5 (unchanged)
    BREAK_GLASS_ALLOW = "X3F"      # NEW — v4_hardening §H3 (this ADR)


@dataclass(slots=True)
class X3BreakGlassAllowPacket:
    disposition: V6Disposition = V6Disposition.BREAK_GLASS_ALLOW
    operator_id: str = ""
    capability_token_ref: str = ""
    written_justification: str = ""
    granted_at_ms: int = 0
    expiry_ms: int = 0
    bypassed_gates: list[str] = field(default_factory=list)
    audit_id: str = ""
    pages_emitted: list[str] = field(default_factory=list)
    customer_facing_l4_commit_allowed: bool = False
    post_mortem_due_at_ms: int = 0
    final_response: str = ""
    trace_root: str = ""
```

### Builder + invariants (`agentic_core/L3_orchestration/exit_eval/v6/x3_dispositions.py`)

`build_x3f_break_glass_allow(packet, decision, *, operator_id, capability_token_ref, written_justification, bypassed_gates, audit_id, ...)` enforces all H3 invariants synchronously and raises `BreakGlassValidationError` on any violation:

| Invariant | Source | Enforcement |
|---|---|---|
| Cannot bypass X1A (policy match) | §H3.1 | `_X3F_FORBIDDEN_BYPASS_GATES = {"X1A", "X1C"}` intersection check |
| Cannot bypass X1C (sandbox/mutation) | §H3.1 | same |
| Cannot bypass UWG verification (U1/U2/U3) | §H3.1 | gates starting with `U` rejected |
| Capability token MUST declare `break_glass=True` | §H3.2.1 | direct check |
| Operator id MUST match token's operator id | §H3.2.1 | equality check |
| Token MUST NOT be expired | §H3.2.1 | direct check |
| Written justification MUST be non-empty | §H3.2.2 | strip-and-check |
| Expiry ≤ 60 minutes from grant | §H3.2.2 | `_X3F_MAX_DURATION_MS = 3_600_000` |
| Expiry > granted_at_ms | §H3.2.2 | range check |
| Audit id MUST be non-empty | §H3.2.4 | direct check |
| Post-mortem due 24h after grant | §H3.3 | `_X3F_POST_MORTEM_OFFSET_MS = 86_400_000` |
| Customer-facing L4 commit OFF by default | §H3.2.5 | default `False` |

### Dispatch (`build_x3_packet`)

```python
if decision.disposition is V6Disposition.BREAK_GLASS_ALLOW:
    raise ValueError(
        "X3F BREAK_GLASS_ALLOW must be invoked via build_x3f_break_glass_allow with "
        "explicit operator_id/capability_token_ref/written_justification; "
        "not via aggregate-decision dispatch (H3.2.1 invariant)"
    )
```

X3F is **not** dispatched via `aggregate_decision`. Operator code must call `build_x3f_break_glass_allow` directly with explicit credentials.

### OTEL (`agentic_core/L3_orchestration/exit_eval/v6/otel.py`)

```python
SPAN_X3F_BREAK_GLASS_EMIT: Final[str] = "exit.x3f.break_glass_allow_emit"
```

Added to `EXIT_V6_SPAN_CATALOG` (now 40 spans, was 39). Operator code recording the X3F emission MUST use this span name. Test `test_every_catalog_span_reachable_via_union_of_runtime_paths` exercises this span via the helper-record path because X3F is operator-invoked.

### Tests (`tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_x3f_break_glass.py`)

25 unit tests covering:

- enum value (`X3F`) and distinctness from `X3E`
- happy path
- H3.1 forbidden gate bypass (X1A, X1C, UWG)
- H3.2.1 capability token (missing flag, empty operator id, mismatch, expired)
- H3.2.2 justification (blank, whitespace) and expiry (>60min, ≤grant, exact-60min boundary, default)
- H3.2.4 audit id required
- H3.3 post-mortem 24h
- H3.2.5 customer-facing commit guard (default off, explicit on)
- Dispatcher rejection of X3F via aggregate dispatch
- X3E continues to dispatch normally (regression)
- OTEL span in catalog
- Type distinctness from X3E packet
- Default grant time uses wall clock

All 394 v6 tests pass after this change.

## Consequences

**Positive**:

- Closes GAP `H3.GAP.X3E_meaning_diverges` in the matrix (real divergence → resolved disposition).
- Span catalog grows from 39 → 40; matrix `5.8.CAT.span_count` validator updated correspondingly in next probe run.
- Operator break-glass control is now a typed contract enforced at build time, not policy prose.

**Negative**:

- The `v4_hardening_addendum.md` §H3.2.3 prose still says "X3E BREAK_GLASS_ALLOW". A doc cleanup pass should rename to `X3F` for consistency, but is not blocking since this ADR is the runtime SSOT.
- `H3.GAP.X3E_meaning_diverges` registry entry needs updating from `gap` → `ok_static` after the doc cleanup (or sooner if we treat ADR-065 as the resolution).

**Neutral**:

- The matrix's documented `span_count: 39` becomes `40` on next probe run; this is a counted-value change, not a structural change.

## Follow-up

- [ ] Doc cleanup: amend `v4_hardening_addendum.md` §H3.2.3 to reference X3F.
- [ ] Update `tools/analysis/exit_v6_requirements_registry.yaml` row `H3.GAP.X3E_meaning_diverges` to `check: "ok_static"` referencing this ADR.
- [ ] Re-run `tools/analysis/exit_v6_master_otel_probe.py` and `exit_v6_matrix_generator.py` to refresh evidence files (`OK=357 / DESIGN=214 / GAP=0` expected).
- [ ] (Future, separate plan) Implement the H3 control plane around the builder: capability-token issuance, audit-row writer, on-call paging, post-mortem scheduler, ratification workflow.

## Linked

- Matrix: `docs/reports/plans/exit_eval_v6_MASTER_otel_matrix.md`
- Spec: `docs/reference/05_Exit_Evaluation_and_Control/v4_hardening_addendum.md` §H3
- Spec: `docs/reference/05_Exit_Evaluation_and_Control/05.5_Exit_Aggregation_and_X3_Disposition.md` §X3 enum
- Code: `agentic_core/L3_orchestration/exit_eval/v6/types.py`
- Code: `agentic_core/L3_orchestration/exit_eval/v6/x3_dispositions.py`
- Code: `agentic_core/L3_orchestration/exit_eval/v6/otel.py`
- Tests: `tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_x3f_break_glass.py`
