# ADR-098: Legacy Entrypoints Disposition (R1A, R5, MW-Real, R4, UWG-Block, UWG-Commit)

**Status**: PROPOSED
**Date**: 2026-05-06
**Phase**: W4 of apps-l7-deferred-scope-followup-a1d9e3
**Deciders**: Cascade
**ADG Snapshot**: `artifacts/adg/adg_indexed_20260506T200000.sqlite`

---

## Context (SCQA)

- **Situation** — Six legacy entrypoints in `agentic_core/runtime/entrypoints/` lack the mandatory L7_AUDITABILITY evidence plane: `integrated_exact_cache_run.py` (R1A exact cache), `integrated_fallback_run.py` (R5 fallback), `integrated_managed_workflow_real_run.py` (MW real), `integrated_single_action_run.py` (R4 single action), `integrated_uwg_block_run.py` (UWG block), `integrated_uwg_commit_run.py` (UWG commit). These entrypoints emit artifacts directly to run directories without canonical filenames or how_trace integration.

- **Complication** — The L7_AUDITABILITY plane is constitutionally mandatory (§17), yet these 6 entrypoints bypass it entirely. Wiring each with full L7 emit requires ~2k tokens × 6 = ~12k tokens plus ongoing maintenance. The entrypoints are either superseded by newer routes (R1A→R3, R4 deterministic) or have low/no recent usage per ADG activity metrics.

- **Question** — Should we invest ~12k tokens to retrofit full L7 compliance, or retire/archive these entrypoints and redirect traffic to L7-compliant successors?

- **Answer** — Retire all six legacy entrypoints with a 90-day deprecation window; redirect callers to L7-compliant successors; archive entrypoints to `archives/entrypoints/` with preservation stubs.

---

## Decision

Retire the following six legacy entrypoints effective 90 days from ADR acceptance:

1. `integrated_exact_cache_run.py` → Successor: `integrated_r3_grounded_read_run.py` (L7-compliant)
2. `integrated_fallback_run.py` → Successor: `integrated_safe_reuse_run.py` (L7-compliant)
3. `integrated_managed_workflow_real_run.py` → Successor: `integrated_managed_workflow_run.py` (L7-compliant)
4. `integrated_single_action_run.py` → Successor: `integrated_r4_deterministic_pipeline_run.py` (L7-compliant)
5. `integrated_uwg_block_run.py` → Successor: Use UWG validation pipeline directly (L7-compliant)
6. `integrated_uwg_commit_run.py` → Successor: Use UWG commit pipeline directly (L7-compliant)

---

## Consequences

### Positive
- Eliminates ~12k token technical debt without implementation
- Consolidates runtime surface to 8 L7-compliant entrypoints (down from 14)
- Reduces CI matrix complexity (6 fewer test suites)
- Aligns with constitutional L7_AUDITABILITY mandate without retrofit cost
- Archives preserve git history for audit/rollback needs

### Negative
- Callers of legacy entrypoints must migrate (90-day notice required)
- Historical references in documentation need updates
- CI gates that test legacy routes must be removed

### Neutral
- 90-day deprecation preserves operational continuity
- Archive stubs maintain import paths (fail-closed with DeprecationWarning)

---

## Alternatives Considered

| Option | Pros | Cons | Why rejected |
|---|---|---|---|
| **A. Retrofit full L7 wiring** | Full compliance, no migration needed | ~12k tokens, ongoing maintenance burden, low ROI for superseded routes | Rejected: ROI insufficient for superseded routes |
| **B. Minimal stub wiring** | Quick ~2k token compliance | Incomplete L7 (no how_trace), violates §17 "full plane" | Rejected: Violates constitutional mandate |
| **C. Status quo** | Zero work | Constitutional violation, audit gap grows | Rejected: §17 non-negotiable |
| **D. Retire with redirect** (Selected) | ~4k tokens, full §17 compliance, consolidates surface | Requires caller migration | Accepted: Best cost/benefit for superseded routes |

---

## Implementation Notes

### Files/modules touched
1. `agentic_core/runtime/entrypoints/integrated_exact_cache_run.py` → archive
2. `agentic_core/runtime/entrypoints/integrated_fallback_run.py` → archive  
3. `agentic_core/runtime/entrypoints/integrated_managed_workflow_real_run.py` → archive
4. `agentic_core/runtime/entrypoints/integrated_single_action_run.py` → archive
5. `agentic_core/runtime/entrypoints/integrated_uwg_block_run.py` → archive
6. `agentic_core/runtime/entrypoints/integrated_uwg_commit_run.py` → archive
7. `archives/entrypoints/` (new) — preservation stubs
8. `.github/workflows/` — remove legacy test jobs
9. `docs/architecture/adr/` — this ADR

### Migration order
1. Create archive stubs with `DeprecationWarning` (fail-closed on invocation)
2. Update CI to remove legacy test jobs
3. Notify known callers (search ADG for imports)
4. 90-day countdown
5. Remove from main, preserve in archives/

### Rollback path
Git history preserved; archive stubs can be restored if business need emerges. Restore requires re-opening this ADR with new justification.

### CI gates added/changed
- Remove: `test_exact_cache_l7`, `test_fallback_l7`, `test_mw_real_l7`, `test_single_action_l7`, `test_uwg_block_l7`, `test_uwg_commit_l7`
- Add: Archive validation gate (ensures stubs fail-closed)

---

## References

- Related ADRs: ADR-017 (L7_AUDITABILITY mandate), ADR-081 (canonical hop pipeline), ADR-082 (apps folder taxonomy)
- Related plans: `.windsurf/plans/apps-l7-deferred-scope-followup-a1d9e3.md`, `.windsurf/plans/apps-l7-w2-w4-followup-a2e8f4.md`
- Related rules: `.windsurf/rules/adg-canonical-invariants.md` §17 (L7 mandatory)
