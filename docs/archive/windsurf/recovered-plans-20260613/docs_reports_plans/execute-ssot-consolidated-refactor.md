# execute_ssot.py — Consolidated Refactor Plan

Exhaustive bug/inefficiency audit of `agentic_core/L0_routing/scripts/execute_ssot.py` with all fixes sequenced, including healing-output enrichment.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## P1 — Correctness: Report Accuracy (7 bugs + 3 new)

### B1 · Global violations stamped onto every per-territory JSON
- **Where:** `execute_phase5_final_impl` lines 2984–2998 (hygiene) and 2945–2963 (gravity)
- **Cause:** `hygiene_violations` and `gravity_violations` are set **once globally** before the territory loop, but Phase 5 reads them into `all_violations` for **every territory's** `detailed_cert`.
- **Fix:** Exclude `hygiene_violations` and `gravity_violations` from per-territory `all_violations`. Emit them only in `save_aggregate_report()` under a new top-level `"global_violations"` key.

### B2 · `conversational_violations` accumulates across territories
- **Where:** Line 4777 — `.extend(conv_violations)` never resets between territories.
- **Fix:** Add `state_mgr.state["conversational_violations"] = []` at the top of each territory's Phase 4.5 block.

### B3 · `gravity_fixed`, `hierarchy_fixed`, `location_fixed` never written to state
- **Where:** Phase 5 certifier lines 3067–3070 reads these three keys; none are ever set.
  - `gravity_fixed`: computed at line 2696 but never stored.
  - `hierarchy_fixed`: computed at line 2648 (`healed`) but never stored.
  - `location_fixed`: computed at line 2527 (`healed_count`) but never stored.
- **Fix:** After each local compute, add `state_mgr.state["<key>"] = <value>`.

### B4 · AI Governance Log always empty — wrong decision list source
- **Where:** Line 3040 — `decisions_made = state_mgr.state.get("decisions_made", [])`
- **Cause:** `state_mgr.state["decisions_made"]` is initialized to `[]` and **never populated**. Actual decisions live in `decision_engine.decisions_made`.
- **Fix:** Use `decision_engine.decisions_made` directly. Requires passing `decision_engine` into Phase 5 (see B5).

### B5 · Phase 5 creates a fresh `AutonomousDecisionEngine` losing LLM/CDA context
- **Where:** Lines 3025–3028 — `getattr(state_mgr, "_decision_engine", None)` is always `None`; fallback creates a bare engine with `enable_llm=False`.
- **Fix:** Pass the real `decision_engine` as a parameter to `execute_phase5_final_impl`. Remove the fallback creation. This also fixes B4.

### B6 · Phase 3 post-heal validation always passes empty violations list
- **Where:** Lines 4668–4673 — `p1_drift.get("violations", [])` is always `[]` because `p1_drift` keys are `forbidden_folders`, `duplicate_folders`, `archived_files_at_root`.
- **Fix:** Pass `_phase1_violations` (built at lines 4621–4646) instead.

### B7 · `compliance_report` state key collision
- **Where:** Line 4501 sets `state_mgr.state["compliance_report"] = audit_results` (Phase 8 audit), then line 4741 overwrites with `gov` (Phase 3 governance report).
- **Fix:** Rename Phase 8 key to `state_mgr.state["compliance_report_audit"]`.

### B13 · `decision_history` dead expression (line 2859)
- **Where:** `state_mgr.state.get("decision_history", [])` — result fetched but never assigned or used.
- **Fix:** Remove the dead expression.

### B14 · Governance log shows ALL territories' decisions, not current territory
- **Where:** Once B4+B5 are fixed and `decision_engine.decisions_made` is used, this list contains decisions from **every** territory (the engine is shared across the loop).
- **Root cause:** `decision_data` (lines 1260–1272) has no `territory` field.
- **Fix:** (a) Add `"territory": territory` to `decision_data` in `should_proceed_with_healing`. (b) In Phase 5, filter: `[d for d in decision_engine.decisions_made if d.get("territory") == territory]`.

### B15 · Per-territory reset misses `_healing_enabled` — budget exhaustion bleeds
- **Where:** Lines 4602–4603 reset `_call_path` and `_healing_count` but NOT `_healing_enabled`.
- **Cause:** If territory N exhausts the budget (`_healing_enabled = False`), territories N+1..M are permanently blocked.
- **Fix:** Add `decision_engine._healing_enabled = True` at line 4603.

---

## P2 — Correctness: Healing Behavior (5 bugs)

### B8 · `GravityLeakRepairAgent` runs once per territory — should run once globally
- **Where:** `execute_phase3_validation_impl` lines 2686–2743 (called inside territory loop).
- **Fix:** Move `GravityLeakRepairAgent` outside the territory loop (same pattern as `RootHygieneAgent`). Store result in `state_mgr.state["gravity_violations"]` and `state_mgr.state["gravity_fixed"]` before the loop.

### B9 · `FileClassificationAgent` Phase 1 early detection scans entire repo unscoped
- **Where:** Line ~2562 — `file_classifier.run()` with no `target_territory` argument.
- **Fix:** Pass `target_territory=territory` to the Phase 1 scan call.

### B10 · `SystemArchitectAgent` constructs wrong path for non-`agentic_core` territories
- **Where:** Line 2747 — `sys_arch.validate_core_architecture(f"agentic_core/{territory}")`.
- **Cause:** For `apps_rg`, `tests`, `docs`, etc. this produces `agentic_core/apps_rg` which doesn't exist.
- **Fix:** Only invoke for L-layer territories. Skip and record as skipped for non-AC territories.

### B11 · Two `LocationValidatorAgent` instances created per territory
- **Where:** Lines 2421 and 2438 — one for confidence calc/heal, one for scanning.
- **Fix:** Remove the first instance. Use `_lva` for both scanning and healing. Set `_hitl_approval_fn` on it before `run()`.

### B12 · `_NON_AC_TERRITORIES` computed but never enforced
- **Where:** Lines 4538–4544 — defined but never checked in territory loop.
- **Fix:** At the start of each territory iteration: `if territory in _NON_AC_TERRITORIES: effective_ctx = _dc_replace(effective_ctx, heal=False)`.

---

## P3 — Code Quality / Inefficiency (5 existing + 4 new)

### I1 · `state_mgr.save()` called on every agent update/complete/event
- **Impact:** ~500+ atomic disk writes per run.
- **Fix:** Remove `self.save()` from `update_agent`, `complete_agent`, `skip_agent`, `add_event`. Keep only in `start_mission`, `finish_mission`, and at territory boundaries.

### I2 · Dead dict literal constructed and immediately discarded
- **Where:** Lines 2914–2920.
- **Fix:** Remove.

### I3 · Per-territory full JSON + Markdown printed to stdout
- **Where:** Lines ~3206–3215.
- **Fix:** Guard with `--verbose` flag. Always log a one-line summary instead.

### I4 · `asyncio.get_event_loop()` deprecated in Python 3.10+
- **Where:** Line ~2452.
- **Fix:** Replace with `asyncio.new_event_loop()`.

### I5 · Phase log labels are misleading (Phase 2.5 runs after Phase 3)
- **Fix:** Renumber log labels to reflect actual execution order.

### B16 · `discover_agents_from_registry` has ~50 lines of duplicated path-resolution logic
- **Where:** Lines 2197–2229 (cache path) and 2244–2276 (live scan path) are nearly identical.
- **Fix:** Extract into a `_resolve_agent_module_path(agent, project_root)` helper.

### B17 · `GracefulExitHandler` class defined but never instantiated
- **Where:** Lines 4985–5004.
- **Fix:** Either instantiate in `_legacy_main` after `state_mgr` creation, or remove if not needed.

### B18 · `load_agents` function is dead code
- **Where:** Lines 4882–4979 — never called in the pipeline.
- **Fix:** Mark as `@deprecated` or remove entirely.

### B19 · `validate_territory_input` has redundant security checks
- **Where:** Lines 1950–1954 — regex `^[A-Za-z0-9_]+$` at line 1946 already blocks all special characters.
- **Fix:** Remove the redundant checks (lines 1950–1954).

---

## H — Healing Output Enrichment (5 items)

### H1 · Fix governance log source (=B4+B5 prerequisite)
- Pass real `decision_engine` to Phase 5. Use `decision_engine.decisions_made` filtered by territory (=B14).

### H2 · Add `_record_healing_action()` helper
- Module-level helper that appends a structured healing action to `state_mgr.state["healing_actions"]`.
- Fields: `agent`, `territory`, `routing_score`, `routing_tier`, `model`, `routing_gate`, `confidence`, `fix_summary`, `outcome`.

### H3 · Call `_record_healing_action` at every heal site

| Phase | Location | Agent | Fix summary source |
|---|---|---|---|
| Pre-loop (RootHygiene) | ~line 4578 | `RootHygieneAgent` | `f"Cleaned {hygiene_fixed} items"` |
| Phase 1 (Location) | ~line 2527 | `LocationAgent` | `f"Healed {healed_count} location violations"` |
| Phase 2 (Reconciliation) | ~line 1899 per agent batch | per `agent_key` | `f"Applied N reconciliation fixes"` |
| Phase 2.5 (FileClassification) | ~line 4723 | `FileClassificationAgent` | `f"Classified {healed} files"` |
| Phase 4 (ArchGovernor) | ~line 2836 | `ArchitectureGovernorAgent` | `f"Fixed {fixed} violations"` |

### H4 · Add `healing_log` to `detailed_cert` JSON
- In `execute_phase5_final_impl`, filter `state_mgr.state["healing_actions"]` by territory.
- Global agents (RootHygiene, Gravity) use `territory="__global__"`.

### H5 · Upgrade Markdown Governance table
- Replace anemic 4-column table with 8-column:
  `| Agent | Score | Tier | Model | Gate | Confidence | Outcome | Fix Applied |`
- Tier display: `DETERMINISTIC` / `vLLM-QWEN` / `GEMINI-2.5-PRO` / `FAIL-CLOSED`
- Skipped/blocked decisions appear with `outcome=SKIP`.

---

## Implementation Order

| # | ID | Description | Risk | Depends |
|---|---|---|---|---|
| 1 | B13 | Remove dead `decision_history` expression | Trivial | — |
| 2 | I2 | Remove dead dict literal (2914–2920) | Trivial | — |
| 3 | B19 | Remove redundant `validate_territory_input` checks | Trivial | — |
| 4 | B7 | Rename Phase 8 `compliance_report` key | Low | — |
| 5 | B2 | Reset `conversational_violations` per territory | Low | — |
| 6 | B3 | Store `gravity_fixed`, `hierarchy_fixed`, `location_fixed` in state | Low | — |
| 7 | B14 | Add `territory` field to `decision_data` | Low | — |
| 8 | B4+B5 | Pass real `decision_engine` to Phase 5; remove fallback | Medium | B14 |
| 9 | B15 | Reset `_healing_enabled` per territory | Low | — |
| 10 | B1 | Remove global violations from per-territory; add to aggregate | Low | — |
| 11 | B6 | Pass `_phase1_violations` to Phase 3 validation | Low | — |
| 12 | B12 | Enforce `_NON_AC_TERRITORIES` in territory loop | Low | — |
| 13 | B11 | Consolidate to single `LocationValidatorAgent` instance | Medium | — |
| 14 | B10 | Guard `SystemArchitectAgent` for AC-only territories | Low | — |
| 15 | B9 | Scope `FileClassificationAgent` Phase 1 to territory | Low | — |
| 16 | B8 | Move `GravityLeakRepairAgent` outside territory loop | Medium | B1, B3 |
| 17 | H2 | Add `_record_healing_action` helper | Low | — |
| 18 | H3 | Call helper at all 5 heal sites | Low | H2 |
| 19 | H4 | Add `healing_log` to `detailed_cert` JSON | Low | H2, H3 |
| 20 | H5 | Upgrade Markdown governance table to 8 columns | Low | H4, B4+B5 |
| 21 | I1 | Reduce `state_mgr.save()` frequency | Medium | — |
| 22 | I3 | Guard stdout dump with `--verbose` | Low | — |
| 23 | I4 | Fix `asyncio.get_event_loop()` deprecation | Trivial | — |
| 24 | I5 | Renumber phase log labels | Trivial | — |
| 25 | B16 | Extract duplicated path-resolution helper | Low | — |
| 26 | B17 | Wire or remove `GracefulExitHandler` | Low | — |
| 27 | B18 | Deprecate/remove dead `load_agents` function | Trivial | — |

**Estimated scope:** 1 primary file, ~35 targeted edits.

---

## Acceptance Criteria

### Correctness
- `python -m pytest -q --color=no` exits 0
- Per-territory JSONs contain **no** `GRAVITY`/`HYGIENE` entries (only in AGGREGATE)
- `compliance_report_AGGREGATE.json` contains `"global_violations"` key
- `violations_fixed` in per-territory metrics reflects real values (not always 0)
- Phase 3 validation log shows non-zero violations when they exist
- Territory N+1 is not blocked by territory N budget exhaustion

### Governance & Healing Output
- AI Governance Log table in per-territory markdown is non-empty when decisions are made
- Per-territory JSON `detailed_cert` contains `"healing_log": [...]` with entries for every heal
- Each entry has: `agent`, `routing_score`, `routing_tier`, `model`, `routing_gate`, `confidence`, `fix_summary`, `outcome`
- Markdown governance table shows all 8 columns
- `routing_tier` correctly shows `DETERMINISTIC` / `vLLM-QWEN` / `GEMINI-2.5-PRO` / `FAIL-CLOSED`
- Decisions where healing was skipped/blocked appear with `outcome=SKIP`
- Governance log only shows current territory's decisions (not all territories)

### Code Quality
- No dead expressions or unreachable code in modified sections
- `state_mgr.save()` call count reduced to <50 per run (from 500+)
- Per-territory stdout output suppressed unless `--verbose`

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

