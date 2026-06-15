---
plan_id: adr-open-scope-closeout-a6d4f2
plan_format: v2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# ADR Open Scope Closeout

Close the 2026-06-15 ADR inventory's deferred, partial, and not-applied records by separating terminal dispositions from real implementation work.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-06-15

---

## Context (SCQA)

- **Situation** - The ADR index reports 122 ADR-like records with zero missing statuses, but 13 records still carry deferred, partial, advisory, proposed-not-executed, or not-applied status text.
- **Complication** - The 13 records mix real implementation gaps, intentionally scoped ADRs, no-op safety decisions, and gate-readiness criteria. Treating them as one backlog would either hide real debt or force oversized implementation.
- **Question** - How do we finish the cleanup without creating dishonest "accepted" statuses or launching unnecessary subsystems?
- **Answer** - Execute three waves: terminalize scoped/no-op records, close retrieval residuals with either small implementation or explicit owning scope, and handle runtime/legacy records only where local evidence proves the action is safe.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Terminal dispositions for scoped/no-op/advisory ADRs | ~8K | No runtime code needed for intentionally scoped records | ✅ DONE | ADR index no longer lists scoped ADRs as open debt |
| W2 | W2.1, W2.2 | Retrieval residuals | ~16K | Prefer small repo-native primitives; split oversized Matryoshka/topology work | ✅ DONE | RAG ADR statuses reflect implemented primitives or explicit successor scope |
| W3 | W3.1, W3.2 | Runtime telemetry split and legacy entrypoints | ~16K | Migrate/delete only when caller evidence is safe; otherwise create explicit terminal disposition | ✅ DONE | Runtime/legacy ADRs no longer have vague unexecuted status |
| W4 | W4.1, W4.2 | Verification and inventory closeout | ~6K | Docs-only changes require diff/inventory checks; code changes require targeted tests | ✅ DONE | Parser reports zero missing statuses and only intentionally not-applied records |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Normalize terminal status text | ✅ DONE |
| W1.2 | Update ADR index categories | ✅ DONE |
| W2.1 | Retrieval implementation evidence pass | ✅ DONE |
| W2.2 | Patch retrieval ADRs and small primitives | ✅ DONE |
| W3.1 | Legacy entrypoint caller safety audit | ✅ DONE |
| W3.2 | Patch runtime/legacy ADRs or safe stubs | ✅ DONE |
| W4.1 | Run focused tests and diff checks | ✅ DONE |
| W4.2 | Final inventory summary | ✅ DONE |

---

## Out Of Scope

- Full Matryoshka multi-collection rollout unless existing code already contains the required primitives.
- Migrating thousands of `_emit_*` telemetry call sites in one pass.
- Activating AG-PURITY strict mode without a fresh stability window and owner sign-off evidence.
- Changing the semantic cache threshold ADR's `PROPOSED_NOT_APPLIED` contract without a new safe sweep and owner approval.

---

## Wave 1 - Terminal Dispositions

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: APPROVED_BY_USER_DIRECTIVE
CHECKPOINT: A

**Authorization**: APPROVED_BY_USER_DIRECTIVE - user asked to implement the cleanup waves.

**Phases**:
- **W1.1** - Normalize statuses for records that are scoped complete or intentionally advisory | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Update `docs/architecture/adr/README.md` to separate intentional no-op from live implementation debt | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Exit-eval scoped ADRs do not appear as incomplete implementation work.
- AG-PURITY remains advisory but is not treated as missing implementation.
- Semantic cache remains not-applied and explicitly intentional.

---

## Wave 2 - Retrieval Residuals

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: APPROVED_BY_USER_DIRECTIVE
CHECKPOINT: B

**Phases**:
- **W2.1** - Confirm existing retrieval primitives for ADR-057/058/061/062/063 | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** - Patch small missing retrieval primitives or terminal successor scope | ~10K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Retrieval ADRs no longer use broad "partial" status for work that is either present or explicitly split.
- Any new retrieval code has focused unit tests.

---

## Wave 3 - Runtime Telemetry And Legacy Entrypoints

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: APPROVED_BY_USER_DIRECTIVE
CHECKPOINT: C

**Phases**:
- **W3.1** - Audit callers/tests for ADR-098 legacy entrypoints and ADR-075 telemetry decorator rollout | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** - Execute safe legacy/runtime cleanup or terminalize to successor plan | ~10K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- No production caller is broken by legacy entrypoint handling.
- ADR-075 does not imply the 2,482-call migration is complete unless it actually is.
- ADR-098 status matches on-disk state.

---

## Wave 4 - Verification

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** - Run focused tests and documentation checks | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.2** - Update inventory and final summary | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `git diff --check` passes for touched docs/code.
- ADR inventory parser reports zero missing statuses.
- Targeted tests pass for any code touched.

---

## Execution Details

### W1.1 - Normalize terminal records
**Scope**: ADR-067, ADR-068, ADR-069, AG-PURITY, ADR-024, and semantic-cache status language.

**Commands**:
```powershell
git diff --check -- docs/architecture/adr docs/adr plans/adr-open-scope-closeout-a6d4f2.md
```

### W2.1 - Retrieval evidence pass
**Scope**: ADR-057, ADR-058, ADR-061, ADR-062, ADR-063 and nearby retrieval modules/tests.

**Commands**:
```powershell
rg -n "matryoshka|query_transform|retrieval_ragas|retrieval_drift|chunker_catalog" agentic_core tools tests config data docs
```

### W3.1 - Runtime and legacy audit
**Scope**: ADR-075 runtime telemetry decorators and ADR-098 legacy entrypoints.

**Commands**:
```powershell
rg -n "integrated_exact_cache_run|integrated_fallback_run|integrated_managed_workflow_real_run|integrated_single_action_run|integrated_uwg_block_run|integrated_uwg_commit_run" .
```

---

## Gap Register

**GAP-1: ADG MCP unavailable in Codex**
- Exact structural MCP queries are unavailable in this session.
- Fallback is targeted local file/search evidence and repo scripts where available.

**GAP-2: Semantic cache threshold intentionally not applied**
- Tests assert `PROPOSED_NOT_APPLIED` and `PENDING_APPROVAL`.
- Cleanup must not change that status without a new safe threshold sweep.

**GAP-3: AG-PURITY strict activation requires external readiness evidence**
- Strict activation needs stability window, owner sign-off, and low false positive evidence.
- This plan may clarify status, but must not flip strict mode without those artifacts.

---

## Definition of Done

DoD-1: ADR statuses are terminal or explicitly owned
- Evidence: ADR inventory parser output lists no vague stale statuses.
- Status: DONE

DoD-2: Retrieval residuals are not hidden
- Evidence: each retrieval ADR has either focused implementation evidence, tests, or explicit successor scope.
- Status: DONE

DoD-3: Legacy/runtime cleanup is safe
- Evidence: caller audit plus targeted tests or explicit no-code terminal disposition.
- Status: DONE

DoD-4: Formatting and inventory checks pass
- Evidence: `git diff --check` and ADR inventory parser pass.
- Status: DONE

DoD-5: Final summary names remaining intentional non-action
- Evidence: final response lists not-applied/advisory items and why they remain non-action.
- Status: DONE

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=adr-open-scope-closeout-a6d4f2 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=adr-open-scope-closeout-a6d4f2 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=adr-open-scope-closeout-a6d4f2 reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

---

## Supersedes

_None - net-new plan._

---

## Marker Quick Reference

```
WAVE_START: plan=adr-open-scope-closeout-a6d4f2 wave=W1
WAVE_COMPLETE: plan=adr-open-scope-closeout-a6d4f2 wave=W1 note="<summary>"
PHASE_COMPLETE: plan=adr-open-scope-closeout-a6d4f2 phase=W1.1
PLAN_COMPLETE: plan=adr-open-scope-closeout-a6d4f2 note="ADR inventory reduced from 13 explicit open/partial/not-applied records to one intentional semantic-cache safety hold"
```
