---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\apps-star-refactor-plan-4f6d9c.md'
original_relative_path: 'apps-star-refactor-plan-4f6d9c.md'
source_sha256: a3dbf246330686da5a130d28c54e8a18906eb79dd8dbaf13e861e4d9b7c37e93
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_* Refactoring Plan (Equivalent to execute_ssot Phases 0–16)

Unified multi-phase refactoring of `apps_rg`, `apps_lic`, and `apps_shared` mirroring the three execute_ssot tracks: structural streamlining, bug/inefficiency fixes, and Guardian-driven architecture migration.

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


## Source Reference

This plan mirrors three prior execute_ssot plans:
- **Structural:** `execute-ssot-streamlining-hardened.md` (6 items)
- **Bugs/Quality:** `execute-ssot-consolidated-refactor.md` (27 items, B1–B19, H1–H5, I1–I5)
- **Architecture:** `execute-ssot-refactor-plan-991629.md` (8 steps)

---

## Dry-Run Baseline (from `execute_ssot_apps_dry_run_report.md`)

| Folder | Files | Compliant | Issues |
|---|---|---|---|
| apps_shared | 232 | 225 | 17 MISNAMED_UTILITY, 6 DUAL-TAG |
| apps_lic | 139 | 131 | MISNAMED_UTILITY, DUAL-TAG, PASSIVE_AGENT_NAMING |
| apps_rg | 155 | 148 | 1 DUPLICATE, MISNAMED_UTILITY, MISPLACED-TEST, DUAL-TAG |

---

## TRACK A — Structural Streamlining (≡ execute_ssot Items 1–3)

### A1 · Remove `ContentStrategyAgent` shim in apps_rg *(Risk: None)*
- `apps_rg/reasoning/ContentStrategyAgent.py` is a 20-line backward-compat shim pointing to `RGStrategyExecutor`
- Pre-check: `grep -r "ContentStrategyAgent"` — if only `RGStrategyExecutor` is the live consumer, delete the shim
- Parallel: `apps_rg/engines/` has a **duplicate** `ContentStrategyAgent` — FCA dry-run flagged this; remove canonical duplicate from `reasoning/` per FCA output

### A2 · Audit and remove dead `MCPHardenedMixin` stubs in apps_lic *(Risk: Low)*
- `OutreachValidationExecutorAgent.py` and `OutreachSignalRouterAgent.py` both define local `MCPHardenedMixin` stub classes ("Legacy mixin — use LICAgentBase instead")
- Both files carry a try/except that defines the stub on ImportError — the real mixin is `agentic_core.mixins.mcp_hardened_mixin`
- Fix: consolidate to a single fallback in a shared `apps_lic/utils/` shim module; remove the two inline class definitions

### A3 · Deduplicate healing orchestrator constants *(Risk: Low)*
- `RgHealingOrchestrator`, `LicHealingOrchestrator`, `ResumeEnhancementOrchestrator`, and 10+ other files each independently define identical module-level constants:
  ```python
  MAX_RETRIES = 3; DEFAULT_SLEEP = 1.0; THRESHOLD = 0.95
  BUFFER_SIZE = 8192; BATCH_SIZE = 32; MAX_DEPTH = 6
  MAX_FILES = 1000; DEFAULT_TIMEOUT = 300
  ```
- Fix: extract to `apps_shared/config/pipeline_constants_config.py`; replace inline definitions with a single import across all consumers
- Scope: ~25 files across all three apps_* folders

### A4 · Flatten apps_rg orchestration layer overlap *(Risk: Low-Medium)*
- `apps_rg/reasoning/` contains: `ResumeOrchestrator`, `RgResumeOrchestrator`, `ResumeEnhancementOrchestrator` — three orchestrators with overlapping resume-pipeline duties
- `apps_rg/engines/` has `ResumeOrchestratorEngine` as the canonical extracted engine
- Fix: audit method overlap via AST; identify which reasoning-layer orchestrators are shims/wrappers; consolidate to one entry-point in `reasoning/` delegating to `engines/ResumeOrchestratorEngine`

### A5 · Fix MISPLACED-TEST in apps_rg *(Risk: None)*
- `apps_rg/scripts/test_run_grand_unification_tests.py` is a test file outside `tests/`
- Fix: move to `tests/apps_rg/test_run_grand_unification_tests.py` + update any CI references

### A6 · Rename MISNAMED_UTILITY files in apps_shared/config/ *(Risk: Low)*
- FCA flagged 17 files in `apps_shared/config/` as `MISNAMED_UTILITY` (class body has active methods, not just data)
- Examples: `config_loader_config.py` → `config_loader_util.py`, `environment_config.py` → `environment_util.py` (already exists — collision to resolve), etc.
- Fix: rename per FCA canonical suffix rules; update all import sites; re-run FCA dry-run to confirm zero violations

---

## TRACK B — Bug & Inefficiency Fixes (≡ execute_ssot B1–B19, I1–I5)

### B1 · State bleed across HOP iterations in apps_lic pipeline *(≡ B2: conversational_violations accumulation)*
- `LicHealingOrchestrator.active_incidents` is a shared dict that is never reset between pipeline runs — analogous to the `conversational_violations.extend()` bug in execute_ssot
- Fix: reset `active_incidents = {}` at the start of each `orchestrate()` / `run()` call

### B2 · `ResumeEnhancementOrchestrator` initializes components to `None` without guard *(≡ B5: fallback engine creation)*
- `persona_router`, `evidence_injector`, `recon_agent`, `infrastructure` are all set to `None` in `__init__`; calling any method before `await initialize()` raises `AttributeError`
- Fix: add `if not self._initialized: raise RuntimeError(...)` guard at each method entry, or use lazy-init properties

### B3 · `HardenedOpenAIExecutor` / `HardenedAnthropicExecutor` duplicate circuit-breaker logic *(≡ I1: save() frequency / manual safety logic)*
- Both `apps_rg/reasoning/HardenedopenaiexecutorStrategy.py` and `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py` hand-roll identical retry + circuit-breaker patterns
- `agentic_core.mixins.circuit_breaker_mixin` already implements this
- Fix: inherit from `circuit_breaker_mixin`; remove ~60 lines of duplicated retry logic per class

### B4 · `apps_rg/scripts/test_engine.py` and `test_input.py` are misplaced test runners *(≡ B10: SystemArchitectAgent wrong-path)*
- Both files live in `apps_rg/scripts/` but import `pytest` and run assertions — they are test files in the wrong layer
- Fix: move to `tests/apps_rg/`; add `__init__.py`; verify CI picks them up

### B5 · `asyncio.get_event_loop()` deprecation in apps_shared utils *(≡ I4)*
- Scan `apps_shared/utils/` for `asyncio.get_event_loop()` — present in at least `async_coordinator_util.py`
- Fix: replace all occurrences with `asyncio.new_event_loop()` or `asyncio.get_running_loop()`

### B6 · `OutreachSignalRouterAgent` double-defines `MCPHardenedMixin` class *(≡ B11: two LocationValidatorAgent instances)*
- The file defines `MCPHardenedMixin` twice (lines 34 and 57) — once in the try block and once as a plain stub after it
- Fix: keep only the try/except block; remove the unconditional second definition

### B7 · `apps_lic/tools/` has operational scripts that are not tools *(≡ B18: dead load_agents)*
- `apps_lic/tools/run_workflow.py`, `run_workflow_lic.py`, `network_ops.py`, `mcp_mocks.py`, `fix_duplicate_*.py` are scripts/utilities incorrectly placed in `tools/`
- Fix: move scripts to `apps_lic/scripts/`; move mocks to `tests/apps_lic/`; move fixers to `ops_scripts/`

### B8 · `apps_shared/config/` MISNAMED files cause DUAL-TAG resolution failures *(≡ B7: key collision)*
- `app_config_types.py`, `checkpoint_manager_types.py` carry `{CONFIG, TYPES}` dual-tag — FCA resolves by folder context but this is ambiguous
- Fix: for files in `config/` that are actually types, move to `apps_shared/types/` or rename

---

## TRACK C — Architecture Migration (≡ execute_ssot Steps 1–8)

### C1 · Define `AppGuardianSpec` registry for apps_* *(≡ Step 1: HealerRegistry)*
**`apps_shared/config/app_guardian_registry.py`**

Maps per-app check IDs to scan functions, parallel to `agentic_core.L0_routing.types.guardian_registry.GuardianSpec`:
```python
@dataclass(frozen=True)
class AppGuardianSpec:
    app: str                   # "apps_rg" | "apps_lic" | "apps_shared"
    check_id: str
    scanner_module: str        # dotted module path
    scanner_fn: str
    healer_module: str | None
    healer_fn: str | None
    requires_approval: bool
```
Initial entries from dry-run findings:
- `apps_rg.duplicate_files` → scanner: FCA duplicate check
- `apps_rg.misplaced_tests` → scanner: FCA MISPLACED-TEST check
- `apps_shared.misnamed_utility` → scanner: FCA MISNAMED_UTILITY check
- `apps_lic.passive_agent_naming` → scanner: FCA PASSIVE_AGENT_NAMING check

### C2 · Build `AppRemediationDispatcher` *(≡ Step 2: RemediationDispatcher)*
**`apps_shared/scripts/app_remediation_dispatcher.py`**

~80 lines. Consumes `combined_app_guardian_result.json`:
1. Load per-app `AppGuardianResult`
2. Filter to FAIL checks
3. Look up `AppGuardianSpec` → healer
4. If `requires_approval=True`, skip without HIL token
5. Execute healer, capture `AppHealResult`
6. Write `combined_app_heal_result.json`

CLI:
```
python -m apps_shared.scripts.app_remediation_dispatcher \
    --apps apps_rg,apps_lic,apps_shared \
    --strict
```

### C3 · Build `AppHealResult` contract *(≡ Step 3: HealResult contract)*
**`apps_shared/types/app_heal_contract_types.py`**

Parallel to `agentic_core.L2_execution.types.heal_contract_types`:
- `AppHealStatus`: `HEALED | PARTIAL | FAILED | SKIPPED`
- `AppHealResult`: `check_id`, `app`, `status`, `changes_made`, `rollback_info`

### C4 · Wire `LicHealingOrchestrator` and `RgHealingOrchestrator` to `healing_tier_router` *(≡ GAP 1: L2 Tier Router)*
Both healing orchestrators currently use hardcoded `max_cycles=5` with no tier escalation. The `agentic_core.L2_execution.healers.healing_tier_router` is unused from apps_*.

Fix:
- Import `route_healing_tier` and `dispatch_healing` in both orchestrators
- Replace bare `await self.heal()` calls with `HealingInput` construction → `route_healing_tier()` → `dispatch_healing()`
- This wires the real `QwenInvokerAdapter` / `GeminiInvokerAdapter` for escalated failures

### C5 · Wire `apps_shared` meta-learning bridge to L4 `reasoning_memory` *(≡ GAP 3: L4 cross-run memory)*
- `apps_shared/scripts/meta_learning_bridge.py` already exists (5.3KB) but is not wired to `agentic_core.L4_state.memory.reasoning_memory`
- `apps_shared/scripts/meta_learning_operator.py` (9.4KB) is not called from either healing orchestrator
- Fix: in `RgHealingOrchestrator` and `LicHealingOrchestrator`, post-heal: call `meta_learning_operator.record_outcome(agent, violation_type, success)` — feeds `L4 reasoning_memory.set_historical_success_rate()` for the next run

### C6 · CI integration *(≡ Step 7)*
- Add `app_remediation_dispatcher.py --strict` as a CI step after existing guardian scans
- Replace direct `FileClassificationAgent` invocations in CI with `AppRemediationDispatcher` dispatch

---

## Implementation Order (risk-sequenced)

| Phase | Items | Risk | Description |
|---|---|---|---|
| **0** | A5, B4 | None | Move misplaced test files |
| **1** | A1 | None | Remove ContentStrategyAgent shim + duplicate |
| **2** | A2, B6 | Low | Consolidate MCPHardenedMixin stubs |
| **3** | A3 | Low | Extract shared pipeline constants |
| **4** | B1, B2 | Low | Fix state bleed + unguarded init |
| **5** | B5 | Low | Fix asyncio deprecations |
| **6** | A6, B8 | Low | Rename MISNAMED_UTILITY / DUAL-TAG files |
| **7** | B7 | Low | Relocate misplaced tools/scripts |
| **8** | B3 | Medium | Wire circuit_breaker_mixin into hardened executors |
| **9** | A4 | Medium | Flatten apps_rg orchestration layer overlap |
| **10** | C3 | Low | Build AppHealResult contract |
| **11** | C1 | Low | Build AppGuardianSpec registry |
| **12** | C2 | Low | Build AppRemediationDispatcher |
| **13** | C4 | Medium | Wire healing_tier_router into LicHealingOrchestrator + RgHealingOrchestrator |
| **14** | C5 | Medium | Wire meta_learning_bridge to L4 reasoning_memory |
| **15** | C6 | Low | CI integration |
| **16** | All | — | Full pytest suite + FCA dry-run verify zero violations |

---

## TRACK D — ADG Refresh, Bootstrap, and Spine Enforcement

### ADG State: Confirmed Covered, But Not Enforced at Entrypoints

**Current state:**
- `ADGStaticScanner._SCAN_ROOTS` already includes `APPS_RG_DIR`, `APPS_LIC_DIR`, `APPS_SHARED_DIR` — all three are scanned
- `adg_latest.json` has `layer: L_APP` entities for all apps_* modules
- **However:** neither `run_workflow_lic.py` nor `generate_resume.py` nor any apps_* entrypoint calls `build_pre_run_report()` or touches the ADG before executing
- `execute_ssot_integration.py` (`build_pre_run_report`) exists and is the canonical pattern — but it is only wired into `execute_ssot.py`, not apps_*
- `windsurfrules §0` mandates ADG-first for ANY code investigation or modification — apps_* entrypoints currently violate this

---

### D1 · Mandatory ADG refresh before each apps_* refactoring phase *(Risk: None)*

**Prerequisite gate for every implementation phase in this plan.**

Before executing any phase (A1–C6), run:
```python
python tools/generate_full_adg.py
```
or, for incremental:
```python
python ops_scripts/ci/dump_adg_to_file.py --rebuild
```
Verify `adg_latest.json` digest changes. If digest is unchanged from prior run, proceed without re-run.

**Enforcement:** Each phase evidence file MUST include a `## DEPENDENCY_GRAPH` section with:
- ADG digest (SHA256 prefix)
- apps_* entity count (from `adg_latest.json`)
- Blast radius of files in scope for that phase

### D2 · ADG bootstrap gate in `apps_lic` entrypoint *(Risk: Low)*

**Current:** `apps_lic/tools/run_workflow_lic.py` has a `main()` that directly instantiates `WorkflowOrchestrator` with zero ADG pre-flight.

**Problem:** Per §0, any execution that touches agents/modules must have ADG-backed impact analysis first.

**Fix:**
- Add a pre-flight ADG call at the top of `main()` in `run_workflow_lic.py`:
  ```python
  from agentic_core.adg.applications.execute_ssot_integration import build_pre_run_report
  adg_report = build_pre_run_report(changed_files=[], force_fresh=False)
  if adg_report.route_mode == "HUMAN_REVIEW":
      logger.warning("ADG: HUMAN_REVIEW — %s", adg_report.summary)
  ```
- This is graceful-degrade: `build_pre_run_report` never raises, returns `adg_available=False` on error
- Log `adg_report.summary` to stdout at startup
- **Canonical entrypoint:** `python -m apps_lic.tools.run_workflow_lic` (add `__main__.py` to `apps_lic/tools/` or confirm `-m` path)

### D3 · ADG bootstrap gate in `apps_rg` entrypoint *(Risk: Low)*

**Current:** `apps_rg/scripts/generate_resume.py` calls `ResumeOrchestratorEngine` directly with no ADG pre-flight.

**Fix:** Same pattern as D2 — add `build_pre_run_report` call at top of `main()`. Emit `adg_report.summary` to logger.

**Canonical entrypoint:** `python -m apps_rg.scripts.generate_resume` (add `__main__.py` to `apps_rg/scripts/` if missing).

### D4 · Define canonical `__main__.py` entrypoints for apps_lic and apps_rg *(Risk: Low)*

**Problem:** There is no single declared `__main__.py` for either app. Multiple `if __name__ == "__main__"` files compete:
- `apps_lic/tools/run_workflow_lic.py` — LIC workflow runner
- `apps_lic/tools/run_workflow.py` — second runner (to be removed per B7)
- `apps_rg/scripts/generate_resume.py` — RG resume generator
- `apps_rg/scripts/rg_live_fire.py` — second RG runner

**Fix:**
- Create `apps_lic/__main__.py` → delegates to `apps_lic.tools.run_workflow_lic:main`
- Create `apps_rg/__main__.py` → delegates to `apps_rg.scripts.generate_resume:main`
- Each `__main__.py` MUST call ADG bootstrap (D2/D3 pattern) before delegating
- After this: canonical invocation is `python -m apps_lic` and `python -m apps_rg`
- `run_workflow.py` (legacy) is deprecated per B7; `rg_live_fire.py` stays as a dev tool (non-canonical)

### D5 · Register apps_* entrypoints in ADG `execute_ssot_integration` *(Risk: Low)*

**Current:** `agentic_core/adg/applications/execute_ssot_integration.py` only serves `execute_ssot.py`.

**Fix:** Add a parallel `build_apps_pre_run_report(app: str, changed_files: list[str])` function that:
- Accepts `app` ∈ `{"apps_rg", "apps_lic", "apps_shared"}`
- Scopes blast radius to modules prefixed by that app
- Returns `PreRunADGReport` (same type — no new contract needed)
- Location: same file, new exported function

### D6 · ADG layer violation gate for apps_* *(Risk: Low)*

**Current:** ADG schema has `ALLOWED_LAYER_EDGES` including `("L_APP", "L0")` through `("L_APP", "L6")`. Layer violations are computed but never surfaced at apps_* entrypoints.

**Fix:**
- In `__main__.py` for both apps (D4), after `build_pre_run_report`, check `adg_report.layer_violation_count > 0`
- If violations exist, log a WARN with count and `adg_report.scope_widening_events`
- Hard-block (`sys.exit(1)`) only if `adg_report.route_mode == "HUMAN_REVIEW"` (risk_score threshold already set in `execute_ssot_integration.py`)

### D7 · CI ADG invariant scan for apps_* *(Risk: None)*

**Current:** `.github/workflows/adg-invariant-scan.yml` exists. Verify it covers `L_APP` layer.

**Fix:** Confirm `adg-invariant-scan.yml` runs `ADGStaticScanner` with `apps_rg`, `apps_lic`, `apps_shared` in scan roots (they already are per `_SCAN_ROOTS`). Add explicit CI assertion: apps_* entity count must be ≥ current baseline (prevent silent removal).

---

## Updated Implementation Order (Phases 0–19)

| Phase | Items | Risk | Description |
|---|---|---|---|
| **0** | **D1** | None | ADG refresh — run `generate_full_adg.py`, freeze digest baseline |
| **1** | A5, B4 | None | Move misplaced test files |
| **2** | A1 | None | Remove ContentStrategyAgent shim + duplicate |
| **3** | A2, B6 | Low | Consolidate MCPHardenedMixin stubs |
| **4** | A3 | Low | Extract shared pipeline constants |
| **5** | B1, B2 | Low | Fix state bleed + unguarded init |
| **6** | B5 | Low | Fix asyncio deprecations |
| **7** | A6, B8 | Low | Rename MISNAMED_UTILITY / DUAL-TAG files |
| **8** | B7 | Low | Relocate misplaced tools/scripts |
| **9** | B3 | Medium | Wire circuit_breaker_mixin into hardened executors |
| **10** | A4 | Medium | Flatten apps_rg orchestration layer overlap |
| **11** | **D4** | Low | Create canonical `apps_lic/__main__.py` and `apps_rg/__main__.py` |
| **12** | **D2, D3** | Low | Wire ADG bootstrap into both `__main__.py` entrypoints |
| **13** | **D5** | Low | Add `build_apps_pre_run_report()` to `execute_ssot_integration.py` |
| **14** | **D6** | Low | Layer violation gate in both `__main__.py` |
| **15** | C3 | Low | Build AppHealResult contract |
| **16** | C1, C2 | Low | Build AppGuardianSpec registry + AppRemediationDispatcher |
| **17** | C4 | Medium | Wire healing_tier_router into LicHealingOrchestrator + RgHealingOrchestrator |
| **18** | C5 | Medium | Wire meta_learning_bridge to L4 reasoning_memory |
| **19** | **D7**, C6 | Low | CI: ADG invariant scan + AppRemediationDispatcher CI step |
| **Final** | All | — | `python -m pytest -q`, FCA dry-run, ADG digest check |

---

## Acceptance Criteria

- `python -m pytest -q --color=no` exits 0, no deselection
- FCA dry-run on all three apps_* folders: 0 MISNAMED_UTILITY, 0 MISPLACED-TEST, 0 DUPLICATE
- `python -m apps_lic` and `python -m apps_rg` execute without error and log ADG summary at startup
- `grep -r "ContentStrategyAgent" apps_rg/reasoning` returns zero hits (shim gone)
- `grep -r "MAX_RETRIES = 3" apps_rg apps_lic apps_shared` returns only the SSOT constant file
- `AppGuardianSpec` registry has ≥4 entries (one per dry-run finding category)
- `combined_app_heal_result.json` is emitted by dispatcher with `AppHealStatus` entries
- `adg_latest.json` digest changes after each phase's ADG refresh
- apps_* entity count in ADG ≥ current baseline (no silent removal)
- Both `__main__.py` files call `build_pre_run_report` before any agent dispatch
- No new files created outside the designated layer folders

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

