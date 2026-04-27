# ADR-067 — Exit-Eval v6 hardening tractable subset (Wave 2)

**Status**: Accepted (partial — H1, H2, H3-control-plane, H4, H7, H9, H10 deferred)
**Date**: 2026-04-26
**Wave**: exit-eval-v6 deferred-scope Wave 2
**Promotes**: 23 design rows → OK (13 H5 attrs + 1 H6 math constant + 9 H8 fault codes) + 6 ADR-067 acceptance rows

---

## Context

`docs/reference/05_Exit_Evaluation_and_Control/v4_hardening_addendum.md` adds 11 hardening sections (H1-H11) on top of the canonical v4/v6 spec. The full implementation surface is genuinely large:

- **H1** Reward-hacking detection (5 signals + 3 counter-measures + disposition routing)
- **H2** Agent-as-judge controls (5 controls including non-agentic fallback judge)
- **H3** Break-glass emergency override → resolved by **ADR-065** (X3F disposition + builder + invariant enforcement)
- **H4** Jailbreak taxonomy (8 categories × 20 probe cases each = 160-case probe set)
- **H5** OTEL wire-up (per-gate span attributes + disposition links + runtime ADG ingest)
- **H6** `pass^k` threshold math (table + non-i.i.d. bucket reset + small-sample correction)
- **H7** Rubric-diff review process (PR checklist + auto-checks + 1-week shadow deploy)
- **H8** Fault-injection matrix (9 fail-modes × correct/forbidden behavior pairs)
- **H9** Operator runbook (9-step triage)
- **H10** Constitutional linkage (8 cross-refs + 3 ADR pointers)

Realistic implementation scope: **H1, H2, H4, H7, H9 are full subsystems** each requiring a dedicated multi-session effort. **H10 is documentation linkage**.

This ADR addresses the genuinely tractable layer: **constants, enums, helper functions, and required-attribute extensions** that pin the runtime contracts the future H1/H2/H4/H7 subsystems will depend on.

## Decision

Implement three fully-tractable hardenings now:

### 1. H5.1 — Per-gate span attributes

Extend `REQUIRED_ATTRIBUTES` (`agentic_core/L3_orchestration/exit_eval/v6/otel.py`) with the 13 hardening attributes named in §H5.1:

```
gate, track, trajectory_class, rubric_version, composition,
aggregate_score, aggregate_threshold, passed, abstain,
disposition_hint, bypass_audit_id, grader_class, rubric_id
```

`REQUIRED_ATTRIBUTES` grows from **26 → 39** entries.

### 2. H6 — `pass^k` threshold math primitives

Create `agentic_core/L3_orchestration/exit_eval/v6/hardening.py` with:

| Symbol | Purpose |
|---|---|
| `PASS_K_THRESHOLD_TABLE: dict[(theta, k), p]` | The 4-row worked table from §H6.1 |
| `pass_k_required_p(theta, k)` | Inverse: solve `theta = p^k` for required per-trial `p` |
| `pass_k_observed(per_trial_p, k)` | Forward: compute observed `pass^k` |
| `PASS_K_INSUFFICIENT_HISTORY_REASON = "INSUFFICIENT_HISTORY"` | §H6.4 small-sample correction reason code |

Wave 2 codifies the math; full X1G/X1I bucket-reset implementation (§H6.3 non-i.i.d.) and the X3B routing helper (§H6.4 small-sample) are deferred to the X1G/X1I implementation pass.

### 3. H8 — Fault-injection reason codes + disposition map

Same module exports:

| Symbol | Purpose |
|---|---|
| `FaultInjectionReasonCode(Enum)` | 9 codes from §H8: `JUDGE_TIMEOUT`, `JUDGE_ERROR`, `GRADER_EXCEPTION`, `RUBRIC_UNAVAILABLE`, `AUDIT_UNAVAILABLE`, `CONSISTENCY_HISTORY_UNAVAILABLE`, `COMMIT_UNAVAILABLE`, `L5_RECLEARANCE_UNAVAILABLE`, `GRADER_BYPASS_DETECTED` |
| `FAULT_INJECTION_CODES: frozenset[str]` | Set view for fast `code in CODES` checks |
| `FAULT_INJECTION_DISPOSITION_HINT: dict[Code, "X3A"\|"X3B"]` | Canonical fail-closed routing map |
| `is_fault_injection_code(code: str) -> bool` | Helper predicate |

Each enum value's docstring records the affected gate(s) and the FORBIDDEN behavior, per §H8 verbatim. The disposition map asserts every fault routes to either X3A or X3B — never X3C or X3D — at type level.

## Why the other hardenings stay DESIGN

| Hardening | Why deferred |
|---|---|
| H1 Reward hacking | Detection signals require runtime score-history tracking, BUS-P emission, and rubric rotation infrastructure. Each signal is its own detector. |
| H2 Agent-as-judge | Requires non-agentic fallback judge implementations + judge-trajectory recording infrastructure + judge-tool version pinning subsystem. |
| H3 control plane | Capability-token issuance, audit-row writer, on-call paging, post-mortem scheduler — addressed in a follow-up. ADR-065 already pinned the X3F disposition + builder + invariants. |
| H4 jailbreak probes | 160 SME-curated probe cases (8 categories × 20). Content authoring effort, not code. |
| H7 PR review process | Process change + auto-check tooling. Non-runtime concern. |
| H9 operator runbook | Documentation. Will land in `docs/operations/` rather than runtime code. |
| H10 constitutional linkage | Documentation cross-references. Already partially captured in this ADR's references. |

These remain DESIGN rows in the matrix and constitute the deferred scope for future Waves (separate plans, not part of this ADR).

## Implementation summary

| File | Change |
|---|---|
| `agentic_core/L3_orchestration/exit_eval/v6/otel.py` | `REQUIRED_ATTRIBUTES`: 26 → 39 entries (+13 H5 attrs) |
| `agentic_core/L3_orchestration/exit_eval/v6/hardening.py` | NEW module — H6 + H8 primitives |
| `agentic_core/L3_orchestration/exit_eval/v6/__init__.py` | Export 8 new public symbols |
| `tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_hardening.py` | NEW — 57 tests (parametrized H5 attrs + H6 math + H8 codes + integration) |
| `tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_otel_emission.py` | Updated `test_required_attributes_match_spec` to match new 26+13 contract |
| `tools/analysis/exit_v6_requirements_registry.yaml` | 23 row promotions + 6 new ADR-067 acceptance rows |

## Test posture

- 451 v6 tests pass (was 394 after Wave 1; +57 new hardening tests)
- 0 v6 regressions
- All H6 math invariants verified (round-trip identity, monotonicity, boundary conditions, error handling)
- All H8 codes have a disposition assigned, restricted to X3A or X3B (fail-closed by type)

## Consequences

**Positive**:

- Future H1/H2/H4/H7 work has a typed contract to bind to (FaultInjectionReasonCode, REQUIRED_ATTRIBUTES, PASS_K_*)
- Catalog correctness verifiable: a typo'd reason code in gate code becomes a static-analysis error, not a silent runtime miss
- 23 design rows + 6 acceptance rows promoted in the matrix (~5% of 574 reqs)

**Negative**:

- The runtime ADG / OTEL emitter wiring still needs to populate the new H5 attributes; until callers do, attribute values default to empty string per the existing contract. Not regression — same shape as base 26 attrs that have always defaulted.

## Linked

- Spec: `docs/reference/05_Exit_Evaluation_and_Control/v4_hardening_addendum.md` §H5, §H6, §H8
- Wave 1 ADR: `docs/architecture/adr/ADR-065-x3f-break-glass-allow-disposition.md`
- Wave 5 ADR: `docs/architecture/adr/ADR-066-exit-eval-v6-historical-gap-closure.md`
- Code: `agentic_core/L3_orchestration/exit_eval/v6/hardening.py`
- Tests: `tests/unit/agentic_core/L3_orchestration/exit_eval/v6/test_hardening.py`
- Matrix: `docs/reports/plans/exit_eval_v6_MASTER_otel_matrix.md`
