# ADR-098: Legacy Entrypoints Disposition (R1A, R5, MW-Real, R4, UWG-Block, UWG-Commit)

**Status**: Superseded by compatibility-retention disposition
**Date**: 2026-05-06
**Phase**: W4 of apps-l7-deferred-scope-followup-a1d9e3
**Deciders**: Codex
**ADG Snapshot**: `artifacts/adg/adg_indexed_20260506T200000.sqlite`

> **Current-state note (2026-06-15):** the six entrypoint files listed below
> still exist under `agentic_core/runtime/entrypoints/` because local evidence
> shows live certification and governance callers. The original archive-first
> retirement choice is superseded; compatibility retention is now the terminal
> disposition until those callers migrate under a dedicated runtime plan.

---

## Context (SCQA)

- **Situation** — Six legacy entrypoints in `agentic_core/runtime/entrypoints/` lack the mandatory L7_AUDITABILITY evidence plane: `integrated_exact_cache_run.py` (R1A exact cache), `integrated_fallback_run.py` (R5 fallback), `integrated_managed_workflow_real_run.py` (MW real), `integrated_single_action_run.py` (R4 single action), `integrated_uwg_block_run.py` (UWG block), `integrated_uwg_commit_run.py` (UWG commit). These entrypoints emit artifacts directly to run directories without canonical filenames or how_trace integration.

- **Complication** — The L7_AUDITABILITY plane is constitutionally mandatory (§17), yet these 6 entrypoints bypass it entirely. Wiring each with full L7 emit requires ~2k tokens × 6 = ~12k tokens plus ongoing maintenance. The entrypoints are either superseded by newer routes (R1A→R3, R4 deterministic) or have low/no recent usage per ADG activity metrics.

- **Question** — Should we invest ~12k tokens to retrofit full L7 compliance, or retire/archive these entrypoints and redirect traffic to L7-compliant successors?

- **Answer** — Retain all six entrypoints as compatibility surfaces while documenting successor routes. Archive only after the live certification scripts, coverage registry, and governance sentinels migrate under a dedicated runtime plan.

---

## Decision

Supersede the original retirement decision. The following six entrypoints remain
compatibility surfaces with documented successor routes:

1. `integrated_exact_cache_run.py` → Successor: `integrated_r3_grounded_read_run.py` (L7-compliant)
2. `integrated_fallback_run.py` → Successor: `integrated_safe_reuse_run.py` (L7-compliant)
3. `integrated_managed_workflow_real_run.py` → Successor: `integrated_managed_workflow_run.py` (L7-compliant)
4. `integrated_single_action_run.py` → Successor: `integrated_single_action_spine_run.py` (L7-compliant)
5. `integrated_uwg_block_run.py` → Successor: Use UWG validation pipeline directly (L7-compliant)
6. `integrated_uwg_commit_run.py` → Successor: Use UWG commit pipeline directly (L7-compliant)

---

## Consequences

### Positive
- Avoids breaking live certification scripts and governance sentinels
- Keeps successor routes explicit for a later, safer migration
- Prevents a documentation cleanup from becoming an unreviewed runtime API removal

### Negative
- Runtime surface remains larger than the retirement proposal intended
- L7 retrofit/retirement still needs a dedicated runtime plan if owners want consolidation

### Neutral
- Compatibility retention preserves operational continuity
- Git history remains the rollback path

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

### Live caller evidence
1. `tools/certification/regen_r1a_latest.py` imports `integrated_exact_cache_run.py`.
2. `tools/certification/regen_r5_latest.py` imports `integrated_fallback_run.py`.
3. `tools/certification/regen_mw_real_latest.py` imports `integrated_managed_workflow_real_run.py`.
4. `tools/certification/regen_r4_latest.py` and `tests/governance/test_integrated_single_action_run_identity.py` import `integrated_single_action_run.py`.
5. `tools/certification/regen_uwg_block_latest.py` imports `integrated_uwg_block_run.py`.
6. `tools/certification/regen_uwg_commit_latest.py` imports `integrated_uwg_commit_run.py`.
7. `agentic_core/L7_auditability/coverage/route_family_l7_coverage.py` still records these route families.

### Migration order if consolidation is reopened
1. Migrate certification scripts to successor routes.
2. Update L7 coverage registry expectations.
3. Replace or retire governance sentinels that assert current public identity.
4. Add fail-closed archive stubs only after the caller scan is clean.
5. Remove the compatibility entrypoints in a runtime-scoped PR.

### Rollback path
Current rollback path is no-op: keep compatibility entrypoints in place. If a
future consolidation PR removes them, rollback restores the files from git
history and re-enables the existing certification callers.

### CI gates added/changed
- None in this closeout.
- Future consolidation must update certification regeneration scripts, route-family L7 coverage, and `tests/governance/test_integrated_single_action_run_identity.py` in the same PR.

---

## References

- Related ADRs: ADR-017 (L7_AUDITABILITY mandate), ADR-081 (canonical hop pipeline), ADR-082 (apps folder taxonomy)
- Related plans: `.claude/plans/apps-l7-deferred-scope-followup-a1d9e3.md`, `.claude/plans/apps-l7-w2-w4-followup-a2e8f4.md`
- Related rules: `.claude/rules/adg-canonical-invariants.md` §17 (L7 mandatory)
