---
plan_id: old-l5-agent-retirement-a94f6c
plan_format: v2
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: "artifacts/governance/core_addition_author_gate/old-l5-agent-retirement-a94f6c.json"
dod_exempt: false
supersedes: []
---

# Old L5 Agent Retirement

Retire Windsurf-era and already-replaced L5 `*Agent` shims through a gated wave plan. Runtime/test references move to canonical utilities first; physical archive/delete waits for explicit eligibility evidence.

> **plan_id discipline**: `old-l5-agent-retirement-a94f6c` is the filename stem and lifecycle markers use `plan=old-l5-agent-retirement-a94f6c`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: EXECUTED_WITH_W4_BLOCKED
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-06-15

---

## Context (SCQA)

- **Situation** - The generated Old L5 manifest found 72 retired-or-suspect `agentic_core/L5_safety/**/*Agent.py` candidates, including 21 already authorized for deletion after the cooling window and 45 unclassified old L5 agents.
- **Complication** - Active imports and governance catalogs still point at several already-authorized shims. Direct deletion on 2026-06-15 would violate the manifest gate because zero candidates are physically archive-eligible before 2026-07-23.
- **Question** - How do we make material retirement progress without destabilizing active runtime or skipping deletion controls?
- **Answer** - Execute W1-W5 as a wave-based retirement: migrate live references to canonical utilities, produce classification and blocker packets for the remaining cohort, hold physical deletion behind the cooling gate, and verify with focused tests and refreshed manifest evidence.

**Evidence Baseline**:
- Manifest: `docs/reports/agent_deprecation/old_l5_agent_retirement_manifest_20260615.json`.
- ADG fallback: `DEGRADED_FALLBACK: reason=adg_sqlite MCP unavailable in Codex session; used existing SQLite snapshot read-only.`
- ADG provenance from manifest generator: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_06152026_1043.sqlite`.
- Manifest summary: 72 candidates, 21 deletion-authorized, 0 physically archive-eligible as of 2026-06-15.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1, W0.2, W0.3 | Manifest, plan, receipt | ~5K | Existing ADG snapshot is valid baseline evidence | DONE | Manifest, plan, and core receipt exist |
| W1 | W1.1, W1.2, W1.3 | Move live refs off authorized shims | ~14K | Canonical utilities are already present | DONE | Focused tests import canonical utilities, not old shim modules |
| W2 | W2.1, W2.2 | Classify remaining Old L5 cohort | ~8K | Unknown agents require explicit disposition before deletion | DONE | Authorization packet records class, owner, and next action |
| W3 | W3.1, W3.2 | Large facade retirement prep | ~8K | Large facades are technical debt but still need caller proof | DONE | Blockers and safe replacement surfaces are recorded |
| W4 | W4.1, W4.2 | Physical archive/delete gate | ~4K | Cooling window remains authoritative | BLOCKED | No deletion before eligibility or explicit override |
| W5 | W5.1, W5.2, W5.3 | Verification and closeout | ~8K | Full ADG/BCG generation is out of scope unless requested | DONE | Targeted pytest and refreshed manifest evidence complete |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Generate Old L5 retirement manifest | DONE |
| W0.2 | Create disk plan and core author-gate receipt | DONE |
| W0.3 | Isolate work in `codex/old-l5-agent-retirement` worktree | DONE |
| W1.1 | Update tests from authorized shim modules to canonical utilities | DONE |
| W1.2 | Update active seam/governance references from authorized shim modules to canonical utilities | DONE |
| W1.3 | Preserve generated/historical baselines until W4/W5 | DONE |
| W2.1 | Produce remaining-cohort disposition packet | DONE |
| W2.2 | Separate deletion-authorized, large-facade, duplicate-shim, and unknown groups | DONE |
| W3.1 | Produce large-facade blocker packet, including `FileClassificationAgent` as technical debt | DONE |
| W3.2 | Split actual caller migration/deletion when replacement surfaces are not yet proven | DONE |
| W4.1 | Evaluate deletion eligibility date and zero-consumer proof | BLOCKED |
| W4.2 | Defer physical archive/delete when cooling gate is closed | BLOCKED |
| W5.1 | Run focused pytest selectors | DONE |
| W5.2 | Refresh manifest evidence without rerunning full ADG/BCG | DONE |
| W5.3 | Record final wave outcomes and residual blockers | DONE |

---

## Out Of Scope

- Re-running the full ADG/BCG generation pipeline unless explicitly requested.
- Modernizing `FileClassificationAgent`; it is Windsurf-era technical debt and should be retired through caller migration, not improved in place.
- Physical archive/delete before the manifest cooling date unless the user explicitly overrides the gate.
- Purging historical plans, archives, or generated baselines solely to remove old literals.
- Fixing unrelated dirty worktree changes outside `codex/old-l5-agent-retirement`.

---

## Wave 0 - Manifest and Authorization Control Plane

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: SATISFIED
CHECKPOINT: A

**Acceptance**:
- Manifest exists and identifies current candidate buckets.
- Plan exists under `plans/`.
- Author-gate receipt covers the small `agentic_core/**` edits needed to move active references off already-authorized shims.

---

## Wave 1 - Live Reference Migration

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: SATISFIED
CHECKPOINT: B

**Scope**:
- Migrate live tests and active seam/governance references for already-authorized shims to canonical utilities.
- Do not delete shim files in W1.
- Leave historical/generated baselines for W4/W5 cleanup after physical eligibility.

**Expected canonical replacements**:
- `CodeDetectorAgent.py` -> `agentic_core.L5_safety.utils.code_detector_util`.
- `CodeEnforcerAgent.py` -> `agentic_core.L5_safety.utils.code_enforcer_util`.
- `CodeJanitorAgent.py` -> `agentic_core.L5_safety.utils.code_janitor_util`.
- `CodeValidatorAgent.py` -> `agentic_core.L5_safety.utils.code_validator_util`.
- `LocationHealerAgent.py` -> `agentic_core.L5_safety.utils.location_healer_util`.

---

## Wave 2 - Remaining Cohort Classification

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: DEPRECATION_AUTHORIZED_DELETION_DEFERRED
CHECKPOINT: C

**Scope**:
- Create a disposition packet for the 45 unclassified old L5 agents and all large-facade candidates.
- Record whether each candidate is deletion-ready, requires caller migration, needs a canonical utility replacement, or should split to a separate plan.

---

## Wave 3 - Large Facade Retirement Prep

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: DEPRECATION_AUTHORIZED_DELETION_DEFERRED
CHECKPOINT: D

**Scope**:
- Treat `FileClassificationAgent` and peer large facades as retirement targets.
- Do not modernize or deepen these facades.
- Produce blockers and replacement requirements for actual deletion waves.

---

## Wave 4 - Physical Archive/Delete Gate

WAVE_ID: W4
WAVE_STATUS: BLOCKED
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: TIME_GATED
CHECKPOINT: E

**Scope**:
- Evaluate `eligible_for_physical_archive_as_of_2026_06_15`.
- If the value remains `0`, perform no physical archive/delete and record the date gate.

**Blocked Gate**:
- Earliest manifest archive date for already-authorized shims is 2026-07-23.

---

## Wave 5 - Verification and Closeout

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety/reasoning/test_CodeDetectorAgent.py tests/unit/agentic_core/L5_safety/reasoning/test_CodeEnforcerAgent.py tests/unit/agentic_core/L5_safety/reasoning/test_CodeJanitorAgent.py tests/unit/agentic_core/L5_safety/reasoning/test_CodeValidatorAgent.py tests/integration/agentic_core/test_depth_violation_no_archive_invariant.py -q
python tools/governance/generate_old_l5_agent_retirement_manifest.py
rg -n "agentic_core\.L5_safety\.reasoning\.(CodeDetectorAgent|CodeEnforcerAgent|CodeJanitorAgent|CodeValidatorAgent|LocationHealerAgent)" agentic_core tests ops_scripts -g "!agentic_core/L5_safety/reasoning/*Agent.py" -g "!docs/archive/**"
```

**Acceptance**:
- Focused pytest selectors pass or failures are attributed with evidence.
- Refreshed manifest still reports zero premature physical archive/delete.
- Active references to migrated authorized shims are absent outside historical/generated baselines and self-deprecation shims.

---

## Definition of Done

DoD-1: W1 live references for already-authorized shim modules are migrated to canonical utilities.
- Evidence: focused literal scan over active source/test surfaces.
- Status: DONE

DoD-2: W2 classification packet exists for remaining old L5 candidates.
- Evidence: `docs/reports/agent_deprecation/old_l5_agent_wave2_authorization_20260615.*`.
- Status: DONE

DoD-3: W3 large-facade retirement blocker packet exists and does not modernize `FileClassificationAgent`.
- Evidence: `docs/reports/agent_deprecation/old_l5_agent_wave3_facade_blockers_20260615.md`.
- Status: DONE

DoD-4: W4 deletion gate is enforced.
- Evidence: no `git rm`/archive move of candidate files before eligibility unless explicitly overridden.
- Status: BLOCKED

DoD-5: W5 focused tests and manifest refresh complete.
- Evidence: command output in final closeout.
- Status: DONE

DoD-6: Unrelated worktree branches and dirty main worktree changes remain untouched.
- Evidence: edits occur only in `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-old-l5-agent-retirement`.
- Status: DONE

---

## W5 Verification Results

- `python -m pytest tests/unit/agentic_core/L5_safety/reasoning/test_CodeDetectorAgent.py tests/unit/agentic_core/L5_safety/reasoning/test_CodeEnforcerAgent.py tests/unit/agentic_core/L5_safety/reasoning/test_CodeJanitorAgent.py tests/unit/agentic_core/L5_safety/reasoning/test_CodeValidatorAgent.py tests/unit/agentic_core/L5_safety/validators/test_CodeJanitorAgent.py tests/integration/agentic_core/test_depth_violation_no_archive_invariant.py -q`: 18 passed, 20 skipped.
- `python -m pytest tests/unit/agentic_core/seams/test_seams_hardening.py -q`: 35 passed.
- `python tools/governance/generate_old_l5_agent_retirement_manifest.py`: refreshed manifest; 72 candidates, 21 authorized, 0 eligible for physical archive on 2026-06-15.
- `python -m json.tool` passed for the manifest, author-gate receipt, and lazy seam allowlist.
- `git diff --check`: no whitespace errors; line-ending normalization warnings only.

Residual W3 blocker:

- `ops_scripts/dev_tools/l0_scripts/rename_unified_agents_util.py` still contains an old generated `new_init` string for deprecated shim imports. It is intentionally deferred because it also references legacy factory helpers that do not yet exist on the utility surface.

---

## Gap Register

**GAP-1: Physical deletion is time-gated**
- Impact: W4 cannot complete on 2026-06-15 without explicit override.

**GAP-2: ADG MCP unavailable in Codex**
- Impact: Manifest generation uses the existing SQLite snapshot fallback instead of live MCP tools.

**GAP-3: Unknown old L5 cohort**
- Impact: W2 can classify and prepare authorization, but actual deletion of unknown agents must wait for replacement and zero-consumer proof.

**GAP-4: Large facades may still have callers**
- Impact: W3 produces blockers and replacement paths rather than deleting large facades opportunistically.

---

## Marker Quick Reference

```text
PLAN_CREATED: slug=old-l5-agent-retirement-a94f6c path=plans/old-l5-agent-retirement-a94f6c.md status=In Progress
WAVE_COMPLETE: plan=old-l5-agent-retirement-a94f6c wave=W0 note="manifest, plan, receipt"
WAVE_BLOCKED: plan=old-l5-agent-retirement-a94f6c wave=W4 reason="cooling window closes no earlier than 2026-07-23"
PLAN_COMPLETE: plan=old-l5-agent-retirement-a94f6c note="W1-W3/W5 complete; W4 deferred by gate"
```
