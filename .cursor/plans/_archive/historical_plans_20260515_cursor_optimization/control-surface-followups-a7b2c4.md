# Control-Surface Separation — Follow-Ups

**Plan ID:** `control-surface-followups-a7b2c4`
**Status:** Open
**Origin:** Operator directives 2026-05-01 14:15 + 14:45 UTC-04:00
**Parent work:** Completed in same session — separation gate, healing registry, evidence validator, CI wiring (139 tests pass).

This plan consolidates the residual follow-up items captured during the
control-surface separation hardening pass. None block the v3 panel
attestation gate or the healing-evidence validator. Each entry is a
voluntary improvement — author-declared P-band, not scorer-assigned.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W-NEXT | NEXT-1 .. NEXT-5 | Control-surface follow-ups | ~38000 | No upstream regressions; existing 139 tests stay green | Todo | Each phase merges cleanly with no rule re-litigation |

## Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---|---|
| NEXT-1 | Decouple `veto_orchestrator.py` from `llm_judge_veto.py` | `tools/certification/safety/veto_orchestrator.py` lines 93–96 | Conditional import blocks (2) below | ~6000 | Todo |
| NEXT-2 | Relocate `llm_judge_veto.py` to legacy path | `tools/certification/safety/llm_judge_veto.py` → `tools/_legacy/certification_safety/`; update 9 callers | Depends on NEXT-1 | ~10000 | Todo |
| NEXT-3 | Move `CONSENSUS_JURORS` from `model_registry.py` to L1 registry | `agentic_core/L0_routing/config/model_registry.py`; create new L1 registry module | Used by `consensus_validator.py` only — scope is bounded | ~4000 | Todo |
| NEXT-4 | Fix ADG-hotspot scaffold test path config | `tests/agentic_core/L2_execution/healers/conftest.py` (or root conftest); 4 `test_module_imports`-style tests fail with `ModuleNotFoundError` despite modules existing | Pre-existing infrastructure issue, not a code bug | ~5000 | Todo |
| NEXT-5 | Wire first durable healing emitter to `build_healing_evidence_stamp()` | One concrete healer site (TBD) — emit `artifacts/healing/<run_id>/<action>.json` and validate via `validate_healing_evidence` | No emitter exists today; current healers are non-emitting | ~13000 | Todo |

## Phase Detail

### NEXT-1 — Decouple `veto_orchestrator.py` from `llm_judge_veto.py`

**Why now:** Required to unblock NEXT-2.
**Scope:** `tools/certification/safety/veto_orchestrator.py` conditional `try`/`except ImportError` block at lines 93–96 currently imports `LLMJudgeVeto`. Replace with a feature-flagged dispatch (or remove if the legacy single-provider judge path is no longer reachable through the orchestrator).
**Risk:** 6 production callers of `veto_orchestrator.py` — must remain identity-preserving.
**Tests:** Existing `tests/runtime/test_veto_fail_closed.py`, `tests/runtime/test_integrated_runtime_safe_reuse_veto.py` must stay green.

### NEXT-2 — Relocate `llm_judge_veto.py` to legacy path

**Why now:** Operator decision #3 (2026-05-01 14:15) — relocate when active imports are gone.
**Scope:** `tools/certification/safety/llm_judge_veto.py` → `tools/_legacy/certification_safety/llm_judge_veto.py`. Update 9 import sites: 1 production (`veto_orchestrator.py`, post-NEXT-1), 3 test files. Add deprecation shim if any external consumer references the old path.
**Depends on:** NEXT-1.
**Tests:** Update 3 affected test files; full pre-existing 139-test sweep must pass.

### NEXT-3 — Move `CONSENSUS_JURORS` to L1 registry

**Why now:** Decision #5 (2026-05-01 14:15) deferred this in the panel pass to avoid scope creep. Now safe to revisit.
**Scope:** Create `agentic_core/L1_cognition/config/consensus_validator_registry.py`. Move `CONSENSUS_JURORS` tuple from `agentic_core/L0_routing/config/model_registry.py`. Update `agentic_core/L1_cognition/enforcement/consensus_validator.py` import.
**Risk:** Single consumer — bounded blast radius.
**Tests:** Existing `consensus_validator` tests must stay green.

### NEXT-4 — Fix ADG-hotspot scaffold test path config

**Why now:** Pre-existing failure that surfaced during the hardening pass (4 tests fail with `ModuleNotFoundError` despite the modules existing). Not a regression, not blocking, but produces noise in healer test sweeps.
**Scope:** Investigate why `tests/agentic_core/L2_execution/healers/test_*.py` (auto-generated ADG scaffolds) cannot find `agentic_core.L2_execution.healers.confidence_scorer` etc. via `importlib.import_module` even though the modules import fine outside pytest. Likely a `conftest.py` `sys.path` config issue OR pytest collection policy interaction.
**Tests:** Affected tests start passing.

### NEXT-5 — Wire first durable healing emitter to `build_healing_evidence_stamp()`

**Why now:** The validator + scorer + registry helpers are in place but no healer currently emits durable evidence. First emitter exercises the full healing surface end-to-end.
**Scope:** Pick one concrete healer site (likely `healing_router.py` or `confidence_aware_executor.py` at the post-decision boundary). Wire it to:
1. Call `build_healing_evidence_stamp(healing_tier=..., healing_action=..., healing_evidence_ref=...)`
2. Write a JSON record to `artifacts/healing/<run_id>/<action>.json`
3. Optionally validate via `validate_healing_evidence` before write (defensive)

**Tests:** Add a runtime test that exercises the path and asserts the on-disk artifact passes `validate_healing_evidence` and is REJECTED by `validate_panel_attestation`.

## Acceptance (overall)

- All 5 phases independently mergeable.
- No phase requires re-touching `rtc_req_056_panel.py`, `rtc_req_056_gate.py`, `_panel_attestation.py`, or `healing_evidence_validator.py`.
- `python scripts/verify_control_surface_separation.py` continues to PASS after each phase.
- Existing 139-test sweep (RTC-REQ-056 gate + control-surface separation + panel writer + consensus veto + juror clients + healing validator) stays green.

## Out of Scope

- Re-litigating any of the 7 operator decisions made in the parent pass.
- Changes to `consensus_validator.py` itself (decision #5).
- Schema-version bump beyond v3.
- Healer behavior changes (the migration was import-source-only).
- New CI frameworks.
