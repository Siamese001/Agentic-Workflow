# C0 Policy Migration Guide

> **Plan**: `c0-policy-rectification-deferred-f7b2a9` (W5)
> **Status**: Completed 2026-05-08
> **Authority**: L0 is the source of truth; L1 provides advisory signals only.

## Executive Summary

This document describes the migration from legacy C0 grounding checks to the
new **contract-driven C0 policy** architecture. The new architecture:

- Freezes C0 policy at L0 routing time in `RouteContract.c0_policy`
- Uses **typed bypass reasons** (preferred) instead of legacy strings
- Provides OTEL observability for C0 policy provenance
- Maintains backward compatibility during transition period

## Migration Timeline

| Phase | Date | Status | Description |
|-------|------|--------|-------------|
| W1 | 2026-05-08 | ✅ Complete | L3 step-level C0 policy inheritance |
| W2 | 2026-05-08 | ✅ Complete | Remove deprecated `preflight()` function |
| W3 | 2026-05-08 | ✅ Complete | Audit R4-like entrypoints for typed bypass |
| W4 | 2026-05-08 | ✅ Complete | OTEL observability for C0 policy |
| W5 | 2026-05-08 | ✅ Complete | Migration docs and deprecation timeline |

## Typed vs Legacy Bypass Reasons

### Preferred (Typed) - Use These

| Reason | Description | When to Use |
|--------|-------------|-------------|
| `BYPASS_PRELOADED_CONTEXT` | R4 routes with preloaded manifest | R4_SINGLE_ACTION routes |
| `BYPASS_CACHE_RETURN` | Semantic cache hit (R1B) | R1B_SEMANTIC_CACHE routes |
| `BYPASS_FALLBACK` | Fallback with no retrieval | R5 fallback scenarios |
| `NOT_REQUIRED` | Explicitly not required | Terminal routes, synthetic queries |

### Legacy (Deprecated) - Do Not Use

| Reason | Status | Replacement |
|--------|--------|-------------|
| `GROUNDING_NOT_REQUIRED` | ⚠️ Deprecated | `NOT_REQUIRED` or `BYPASS_PRELOADED_CONTEXT` |
| `TERMINAL_SHORTCIRCUIT_NO_RETRIEVAL` | ⚠️ Deprecated | `NOT_REQUIRED` |
| `CACHE_REUSE_PRIOR_EVIDENCE` | ⚠️ Deprecated | `BYPASS_CACHE_RETURN` |
| `FALLBACK_NO_RETRIEVAL` | ⚠️ Deprecated | `BYPASS_FALLBACK` |

## Code Changes Required

### Before (Legacy)

```python
from agentic_core.runtime.contracts.c0_bypass_receipt import build_c0_bypass_receipt

# Hardcoded legacy reason (DEPRECATED)
c0_bypass = build_c0_bypass_receipt(
    run_id=run_id,
    route_id="R4_SINGLE_ACTION",
    reason="GROUNDING_NOT_REQUIRED",  # ❌ Legacy
)
```

### After (Typed)

```python
from agentic_core.runtime.contracts.c0_bypass_receipt import build_c0_bypass_receipt

# Typed bypass reason (PREFERRED)
c0_bypass = build_c0_bypass_receipt(
    run_id=run_id,
    route_id="R4_SINGLE_ACTION",
    c0_bypass_reason="BYPASS_PRELOADED_CONTEXT",  # ✅ Typed
    preloaded_context_ref=ROUTE_ID,  # Optional: add context reference
)
```

## C0Policy Dataclass

The `C0Policy` dataclass is frozen at L0 and carried through the pipeline:

```python
@dataclass(frozen=True)
class C0Policy:
    c0_mode: C0Mode | str                    # RETRIEVE_REQUIRED, BYPASS_*, etc.
    evidence_contract_required: bool       # True = need FinalEvidenceContract
    c0_mode_reason: str | None = None      # Why this mode was chosen
    decision_source: str = "L0_ROUTE_TOPOLOGY"  # Who decided
```

### Decision Sources

- `L0_ROUTE_TOPOLOGY`: Route ID pattern (R1_, R3_, R4_, R5_)
- `L0_CONTRACT_OVERRIDE`: Explicit route contract field
- `L1_ADVISORY`: L1 cognition signal (advisory only)
- `L0_L1_DISAGREEMENT`: Conflict resolution (L0 wins)

## OTEL Observability

### C0 Preflight Span Fields

| Field | Type | Description |
|-------|------|-------------|
| `l1_grounding_required` | bool | L1 advisory signal |
| `route_c0_mode` | str | Frozen C0 mode from RouteContract |
| `evidence_contract_required` | bool | Whether evidence needed |
| `c0_policy_decision_source` | str | Who decided the C0 policy |

### PA Boundary Span Fields

| Field | Type | Description |
|-------|------|-------------|
| `c0_mode` | str | Frozen C0 mode |
| `evidence_required` | bool | Evidence requirement |
| `evidence_present` | bool | Contract/bypass receipt found |
| `c0_policy_source` | str | Decision authority |
| `boundary_status` | str | PASS/FAIL/SKIP |
| `fail_reason` | str | Failure code (if FAIL) |

## Deprecation Schedule

### 2026-05-08 (Today)
- ✅ All entrypoints updated to typed bypass reasons
- ✅ OTEL observability deployed
- ✅ Documentation published

### 2026-06-08 (30 days)
- 🗓️ Legacy bypass reasons marked as deprecated in code
- 🗓️ CI gate warns on legacy reason usage

### 2026-08-08 (90 days)
- 🗓️ Legacy bypass reasons removed from `ALLOWED_C0_BYPASS_REASONS`
- 🗓️ Type enforcement becomes strict

## Verification Checklist

- [ ] All R4-like entrypoints use `BYPASS_PRELOADED_CONTEXT`
- [ ] All R1B cache paths use `BYPASS_CACHE_RETURN`
- [ ] No hardcoded `GROUNDING_NOT_REQUIRED` in codebase
- [ ] OTEL spans show C0 policy fields in traces
- [ ] Tests pass for C0 policy inheritance (W1)
- [ ] Tests pass for preflight removal (W2)
- [ ] Tests pass for entrypoint audit (W3)
- [ ] Tests pass for OTEL tracing (W4)

## Rollback Plan

If issues are detected:

1. **Immediate**: Set `C0_POLICY_STRICT_MODE=0` to allow legacy reasons
2. **Short-term**: Revert specific entrypoint to legacy reason
3. **Long-term**: Fix root cause and redeploy

## References

- **Plan**: `.codex/plans/c0-policy-rectification-deferred-f7b2a9.md`
- **Code**: `agentic_core/L0_routing/c0_retrieval/preflight.py`
- **Code**: `agentic_core/prompt_governance/prompt_assembly/pa0_boundary.py`
- **Tests**: `tests/agentic_core/runtime/entrypoints/test_w3_entrypoint_c0_bypass_audit.py`
- **Tests**: `tests/agentic_core/runtime/entrypoints/test_w4_otel_c0_policy_tracing.py`

## Contact

For questions about C0 policy migration, contact:
- Architecture: SVP Engineering
- Implementation: Agentic Core Team
