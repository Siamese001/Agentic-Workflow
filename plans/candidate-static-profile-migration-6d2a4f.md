---
plan_id: candidate-static-profile-migration-6d2a4f
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# Candidate Static Profile Migration

Replace runtime base-resume identity reads with a static profile spine so the full base resume is never treated as claim or skills proof.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: NONE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-12

---

## Context (SCQA)

- **Situation** - `apps_rg` still has runtime and export paths named around `base_resume`, even though product evidence law already forbids base resume claim authority.
- **Complication** - The name and file shape invite callers to hydrate bullets, skills, summaries, or metrics from a legacy resume artifact instead of graph bundles and skill nodes.
- **Question** - How do we preserve static render anchors while removing the base-resume proof affordance from runtime readers?
- **Answer** - Add `candidate_static_profile.json`, point identity/contact/certification readers to it, and keep claims/skills in graph-backed sources.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Evidence and profile schema | ~8K | Existing base JSON has all static identity fields needed | DONE | Static profile contains only identity, contact, certs, and employment identity |
| W2 | W2.1, W2.2 | Runtime/export migration | ~14K | Existing callers can keep backward-compatible function names where tests need them | DONE | Final assembler/export enrichment read static profile for static anchors and no skills from base resume |
| W3 | W3.1, W3.2 | Tests and cleanup | ~10K | Existing dirty worktree changes are user-owned | DONE | Targeted tests pass and remaining `base_resume` references are authority guards, legacy CLI args, or explicit anti-hydration checks |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | ADG and call-site evidence | DONE |
| W1.2 | Static profile artifact | DONE |
| W2.1 | Identity/profile loader migration | DONE |
| W2.2 | Export enrichment migration | DONE |
| W3.1 | Unit tests and fixtures | DONE |
| W3.2 | Diff review and remaining-reference audit | DONE |

---

## Out Of Scope

- Deleting the legacy full base-resume JSON in this first migration step.
- Rewriting graph skill nodes or employer role-episode bundles except where tests need static-profile wiring.
- Removing legacy CLI option names before callers have migrated.

---

## Wave 1 - Evidence And Profile Schema

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: A

**Authorization**: USER_REQUESTED_IMPLEMENT - User explicitly requested implementation and tests.

**Phases**:
- **W1.1** - ADG and call-site evidence | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Static profile artifact | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- ADG fallback provenance is recorded.
- New profile file excludes bullets, skills, summaries, accomplishments, metrics, and role claims.

---

## Wave 2 - Runtime And Export Migration

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: B

**Phases**:
- **W2.1** - Identity/profile loader migration | ~8K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** - Export enrichment migration | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Final assembly identity/profile data resolves from `candidate_static_profile.json`.
- Export enrichment copies contact and certifications from the static profile.
- Export enrichment no longer hydrates skills categories from base resume data.

---

## Wave 3 - Tests And Cleanup

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: C

**Phases**:
- **W3.1** - Unit tests and fixtures | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** - Diff review and remaining-reference audit | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Targeted `apps_rg` tests pass with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.
- Audit confirms static profile contains only non-claim/static fields.

---

## Execution Details

### W1.1 - ADG And Call-Site Evidence
**Scope**: Use ADG before text search, then inspect exact runtime/export call sites.

**Commands**:
```bash
python -c "from pathlib import Path; print(sorted(Path('artifacts/adg').glob('adg_indexed_*.sqlite'))[-1])"
rg -n "base_resume|candidate_static_profile|static_profile" apps_rg tests
```

ADG Provenance: backend=sqlite-direct-degraded-fallback, snapshot=adg_indexed_06122026_1101.sqlite
DEGRADED_FALLBACK: reason=adg_sqlite MCP tools unavailable in this Codex session after tool discovery.

### W1.2 - Static Profile Artifact
**Scope**: Create `apps_rg/resume/base/candidate_static_profile.json` from non-claim fields only.

**Commands**:
```bash
python -m json.tool apps_rg/resume/base/candidate_static_profile.json
```

### W2.1 - Identity/Profile Loader Migration
**Scope**: Add or update runtime loader helpers so identity/static context resolves from the new profile path.

**Commands**:
```bash
python -m pytest tests/unit/apps_rg -q
```

### W2.2 - Export Enrichment Migration
**Scope**: Move contact/cert enrichment to static profile input and remove base-resume skills hydration.

**Commands**:
```bash
python -m pytest tests/unit/apps_rg -q
```

### W3.1 - Unit Tests And Fixtures
**Scope**: Add targeted assertions for static-only profile contents and export behavior.

**Commands**:
```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest <targeted-tests> -q
```

### W3.2 - Diff Review And Remaining-Reference Audit
**Scope**: Review changed files and classify remaining `base_resume` references.

**Commands**:
```bash
git diff -- <changed-files>
rg -n "base_resume|candidate_static_profile|static_profile" apps_rg tests
```

---

## Gap Register

**GAP-1: Legacy CLI naming remains**
- Some public CLI/test helper fields still use `base_resume` names.
- Impact: Full deletion of `base_resume.json` remains a second-step migration after callers move.

---

## Definition of Done

DoD-1: Static profile exists and is claim-free.
- Evidence: JSON audit for forbidden keys and content categories.
- Status: DONE

DoD-2: Runtime static anchors use the profile.
- Evidence: final assembler/export enrichment tests cover identity/contact/cert paths.
- Status: DONE

DoD-3: Skills are not hydrated from the static profile or base resume.
- Evidence: export enrichment test keeps missing skills missing unless graph/render payload supplies them.
- Status: DONE

DoD-4: Targeted tests pass.
- Evidence: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest <targeted-tests> -q`.
- Status: DONE

DoD-5: Remaining base-resume references are classified.
- Evidence: `rg` audit summarized in final response.
- Status: DONE

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=candidate-static-profile-migration-6d2a4f wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=candidate-static-profile-migration-6d2a4f decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=candidate-static-profile-migration-6d2a4f reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| _None - net-new plan._ | |

_None - net-new plan._

---

## Marker Quick Reference

Wave lifecycle markers:
```text
WAVE_START: plan=candidate-static-profile-migration-6d2a4f wave=<N>
WAVE_COMPLETE: plan=candidate-static-profile-migration-6d2a4f wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=candidate-static-profile-migration-6d2a4f phase=<W1.1>
PLAN_COMPLETE: plan=candidate-static-profile-migration-6d2a4f note="<final outcome>"
```
