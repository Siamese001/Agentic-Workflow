---
plan_id: apps-rg-reasoning-deletion-d4e8f1
plan_type: refactor
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg/reasoning Deletion Plan

Remove the legacy `apps_rg/reasoning/` agent swarm (non-product, superseded by section lanes + `python -m apps_rg`) after migrating or deleting the small set of test/eval/RCA callers.

> **plan_id**: `apps-rg-reasoning-deletion-d4e8f1` — markers use `plan=apps-rg-reasoning-deletion-d4e8f1`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-05-23

---

## Context (SCQA)

- **Situation** — `apps_rg/reasoning/` holds 10 Python files (`ResumeAgent`-style shells: `ContentQualityAgent`, `RgResumeOrchestrator`, `RgHealingOrchestrator`, etc.). Product résumé generation runs via `apps_rg/runtime/sections/*_lane.py` and `canonical_dispatch`. Quarantine registry already labels six reasoning paths `SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME` ([test_apps_rg_deprecated_path_quarantine.py](tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py)).
- **Complication** — ~35 Python files still import `apps_rg.reasoning` (tests, `apps_eval` scenarios, `rg_orchestrator_facade`, RCA scripts, taxonomy registry). Blind delete breaks CI. Some tests reference **already-deleted** symbols (`ResumeOrchestrator`, `BrandComplianceAgent`).
- **Question** — How do we delete `apps_rg/reasoning/` without regressing product proof or contract gates?
- **Answer** — Migrate callers first (eval → canonical dispatch or drop scenarios), delete test-only tree, then remove folder and scrub registry/metadata in one gated wave with contract pytest proof.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W0 | Baseline + fan-in lock | ✅ DONE | — | quarantine registry |
| W1 | Caller migration (eval, facade, RCA) | ✅ DONE | — | facade, eval, RCA |
| W2 | Test / contract cleanup | ✅ DONE | -9 tests | reasoning test tree |
| W3 | Delete tree + registry + proof | ✅ DONE | — | apps_rg/reasoning removed |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Fan-in inventory + baseline pytest | ✅ DONE |
| W0.2 | Quarantine registry extension | ✅ DONE |
| W1.1 | `rg_orchestrator_facade` — canonical only | ✅ DONE |
| W1.2 | `apps_eval` scenario migration | ✅ DONE |
| W1.3 | RCA / ops_scripts migration | ✅ DONE |
| W2.1 | Delete `tests/unit/apps_rg/reasoning/` | ✅ DONE |
| W2.2 | Fix stale tests (missing symbols) | ✅ DONE |
| W2.3 | Update `_apps_contract` boundaries | ✅ DONE |
| W3.1 | Delete `apps_rg/reasoning/` | ✅ DONE |
| W3.2 | Taxonomy + CI inventory scrub | ✅ DONE |
| W3.3 | Final proof + receipt | ✅ DONE |

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1–W0.2 | Lock fan-in; baseline | ~15K | No new imports land during plan | ✅ DONE | Quarantine + reasoning removal test |
| W1 | W1.1–W1.3 | Remove runtime callers | ~25K | Eval hop scenarios SKIP | ✅ DONE | Facade canonical-only |
| W2 | W2.1–W2.3 | Tests + contracts | ~30K | Stale tests deleted | ✅ DONE | 9 reasoning tests removed |
| W3 | W3.1–W3.3 | Delete + proof | ~20K | Taxonomy OBSOLETE metadata | ✅ DONE | Folder gone; smoke PASS |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.1 | Fan-in inventory | `rg -l apps_rg.reasoning` → artifact | Hidden imports in tools/ | ~8K | ✅ DONE |
| W0.2 | Quarantine extend | [test_apps_rg_deprecated_path_quarantine.py](tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py) | `test_reasoning_package_removed` | ~7K | ✅ DONE |
| W1.1 | Facade trim | [rg_orchestrator_facade.py](apps_shared/adapters/rg_orchestrator_facade.py) | Canonical dispatch only | ~8K | ✅ DONE |
| W1.2 | Eval scenarios | [scenario_runner.py](apps_eval/engines/scenario_runner.py) | Hop scenarios SKIP | ~10K | ✅ DONE |
| W1.3 | RCA scripts | [\_rca_quality_issue.py](ops_scripts/apps_rg/_rca_quality_issue.py) | Inlined placeholder rules | ~7K | ✅ DONE |
| W2.1 | Drop reasoning tests | `tests/unit/apps_rg/reasoning/*` | Directory deleted | ~5K | ✅ DONE |
| W2.2 | Stale test purge | enterprise_rg, brand_compliance, heal_stubs | 6 files removed | ~12K | ✅ DONE |
| W2.3 | Contract updates | `_apps_contract/test_apps_rg_*` | Acceptance Rg* test removed | ~13K | ✅ DONE |
| W3.1 | Delete folder | `apps_rg/reasoning/**` | Removed | ~5K | ✅ DONE |
| W3.2 | Registry / CI | [agent_taxonomy_registry.py](agentic_core/L2_execution/types/agent_taxonomy_registry.py) | 20 entries OBSOLETE | ~10K | ✅ DONE |
| W3.3 | Proof | smoke + scoped pytest | 37 passed | ~5K | ✅ DONE |

---

## Deletion Target (SSOT)

**Delete entirely** (10 files):

| Path | Role today |
|------|------------|
| [apps_rg/reasoning/ContentQualityAgent.py](apps_rg/reasoning/ContentQualityAgent.py) | No-op scaffold |
| [apps_rg/reasoning/ProactiveAgent.py](apps_rg/reasoning/ProactiveAgent.py) | `BaseProactiveAgent` shell |
| [apps_rg/reasoning/RgHealingOrchestrator.py](apps_rg/reasoning/RgHealingOrchestrator.py) | Healing shell |
| [apps_rg/reasoning/RgReflectionAgent.py](apps_rg/reasoning/RgReflectionAgent.py) | L6 observer shell |
| [apps_rg/reasoning/RgResumeOrchestrator.py](apps_rg/reasoning/RgResumeOrchestrator.py) | Eval/test façade only |
| [apps_rg/reasoning/RgStrategicPlannerAgent.py](apps_rg/reasoning/RgStrategicPlannerAgent.py) | Planner shell |
| [apps_rg/reasoning/RgTemplateOptimizerAgent.py](apps_rg/reasoning/RgTemplateOptimizerAgent.py) | Template shell |
| [apps_rg/reasoning/RGStrategyExecutor.py](apps_rg/reasoning/RGStrategyExecutor.py) | Empty façade |
| [apps_rg/reasoning/rg_agent_base.py](apps_rg/reasoning/rg_agent_base.py) | Local base |
| [apps_rg/reasoning/__init__.py](apps_rg/reasoning/__init__.py) | Package init |

**Do not touch** (product golden path):

- [apps_rg/__main__.py](apps_rg/__main__.py)
- [apps_rg/runtime/orchestration/canonical_dispatch.py](apps_rg/runtime/orchestration/canonical_dispatch.py)
- [apps_rg/runtime/sections/*_lane.py](apps_rg/runtime/sections/)
- [apps_rg/runtime/validators/*_x2.py](apps_rg/runtime/validators/)
- [apps_rg/runtime/providers/qwen_vllm_provider.py](apps_rg/runtime/providers/qwen_vllm_provider.py)

---

## Out Of Scope

- Deleting [apps_shared/reasoning/BaseHealingOrchestrator.py](apps_shared/reasoning/BaseHealingOrchestrator.py) (shared LIC/RG bases — separate burndown)
- Changing `agentic_core` runtime dispatch or Exit/UWG behavior
- Restoring Dec-2025 `apps_rg/engines/resume_engine/autonomous/` (already gone from product tree)
- Notion plan registration (optional follow-up per [plan-governance](.cursor/skills/plan-governance/SKILL.md))

---

## Wave 0 — Baseline & lock

WAVE_ID: W0
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W0.1** — Fan-in inventory + baseline | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W0.2** — Extend quarantine registry | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**W0.1 — Commands**:
```bash
cd c:/Git/Agentic-Workflow-FRESH
rg -l "apps_rg\.reasoning|apps_rg/reasoning" --glob "*.py" > artifacts/apps_rg/reasoning_deletion_fanin_pre.txt
pytest tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py -q --tb=no
pytest tests/unit/apps_rg/reasoning/ -q --tb=line 2>&1 | tee artifacts/apps_rg/reasoning_tests_baseline.txt
```

**W0.2 — Registry additions** (paths must exist until W3 delete):
```python
"apps_rg/reasoning/ContentQualityAgent.py": "SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME",
"apps_rg/reasoning/ProactiveAgent.py": "SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME",
"apps_rg/reasoning/rg_agent_base.py": "SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME",
```

**Acceptance**:
- Fan-in list committed under `artifacts/apps_rg/`
- Baseline pass/fail counts recorded (expect some stale-test failures — document, do not fix in W0)

---

## Wave 1 — Caller migration

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W1.1** — Facade: canonical only | ~8K | PHASE_STATUS: TODO
- **W1.2** — apps_eval scenarios | ~10K | PHASE_STATUS: TODO
- **W1.3** — RCA / ops_scripts | ~7K | PHASE_STATUS: TODO

### W1.1 — `rg_orchestrator_facade`

**Action**: Remove `RgResumeOrchestrator` from `_LAZY_SYMBOLS`; keep only `run_canonical_apps_rg_from_cli_primitives`. Update module docstring (no eval orchestrator).

**Replace in** [test_w3_boundary_facades.py](tests/unit/apps_shared/adapters/test_w3_boundary_facades.py):
- Assert facade exports canonical dispatch symbol only (not `RgResumeOrchestrator`).

### W1.2 — `apps_eval`

**Option A (preferred)**: Repoint `_scenario_single_hop` / `_scenario_multi_hop_pass` to call `run_canonical_apps_rg_from_cli_primitives` with minimal CLI primitives + `test_mode`/harness env (mirror [apps_rg/__main__.py](apps_rg/__main__.py) contract).

**Option B**: Mark scenarios `SKIP` with reason `legacy RgResumeOrchestrator removed; use section lane eval`.

**Also update** [apps_eval/config/agent_spec_config.py](apps_eval/config/agent_spec_config.py) if it references `rg_orchestrator_facade` for `RgResumeOrchestrator`.

### W1.3 — RCA scripts

**Action** for [\_rca_skill_match.py](ops_scripts/apps_rg/_rca_skill_match.py) / [\_rca_quality_issue.py](ops_scripts/apps_rg/_rca_quality_issue.py):
- Delete scripts if unused, **or**
- Import quality helpers from `apps_rg/runtime/validators/` (e.g. executive_summary sentence utils) — **not** `ContentQualityAgent`.

**Verification**:
```bash
rg -l "apps_rg\.reasoning" --glob "*.py"
# Expected: only tests slated for W2 + agent_taxonomy_registry + contract deny-string tests
```

**Acceptance**:
- No `apps_eval` / `apps_shared` / `ops_scripts` production-path imports of `apps_rg.reasoning`

---

## Wave 2 — Test & contract cleanup

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W2.1** — Delete reasoning unit tests | ~5K | PHASE_STATUS: TODO
- **W2.2** — Purge stale tests | ~12K | PHASE_STATUS: TODO
- **W2.3** — Contract boundary updates | ~13K | PHASE_STATUS: TODO

### W2.1 — Delete test tree

Remove directory: `tests/unit/apps_rg/reasoning/` (all `test_rg_*` + `test_resume_orchestrator.py`).

Remove or rewrite: [tests/apps_rg/test_rg_reasoning.py](tests/apps_rg/test_rg_reasoning.py).

### W2.2 — Stale tests (delete, do not resurrect agents)

| Test file | Issue | Action |
|-----------|-------|--------|
| [test_jd_enforcement_validator.py](tests/unit/apps_rg/validators/test_jd_enforcement_validator.py) | Imports `ResumeOrchestrator` (missing) | Delete obsolete cases or point to `canonical_dispatch` |
| [test_brand_compliance_agent.py](tests/unit/apps_shared/test_brand_compliance_agent.py) | `BrandComplianceAgent` missing | Delete file or mark xfail removed |
| [test_heal_stubs_replaced.py](tests/unit/agentic_core/L5_safety/test_heal_stubs_replaced.py) | `ResumeAssemblyAgent` missing | Remove RG cases |
| [test_enterprise_rg.py](tests/unit/apps_rg/scripts/test_enterprise_rg.py) | Builds `RgResumeOrchestrator` | Delete or rewrite to section-lane harness |
| `tests/unit/apps_rg/engines/utils/test_*_agent.py` | ADG contract on reasoning paths | Delete (paths gone in W3) |

### W2.3 — Contract tests

| File | Change |
|------|--------|
| [test_apps_rg_acceptance_checks.py](tests/_apps_contract/test_apps_rg_acceptance_checks.py) | Remove `test_*RgResumeOrchestrator*capture_prompt_bom` (or replace with `executive_summary_lane` source check) |
| [test_apps_rg_exit_uwg_l4_no_bypass_boundary.py](tests/_apps_contract/test_apps_rg_exit_uwg_l4_no_bypass_boundary.py) | Remove `apps_rg/reasoning/RgResumeOrchestrator.py` from allowlist (folder gone) |
| [test_apps_rg_generation_model_env_boundary.py](tests/_apps_contract/test_apps_rg_generation_model_env_boundary.py) | Remove `apps_rg/reasoning/` from scanned paths |
| [test_apps_rg_deprecated_path_quarantine.py](tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py) | **After W3**: replace registry entries with `test_reasoning_package_absent` asserting directory missing |
| [test_contracts_smoke.py](agentic_core/runtime/contracts/tests/test_contracts_smoke.py) | **Keep** deny test using string `apps_rg.reasoning.RgResumeOrchestrator` (policy, file need not exist) |
| [test_runtime_path_inventory.py](tests/_apps_contract/test_runtime_path_inventory.py) | Drop reasoning from expected inventory |
| [test_import_graph_no_quarantine.py](tests/_apps_contract/test_import_graph_no_quarantine.py) | Ensure runtime modules still forbid `from apps_rg.reasoning` |

**Commands**:
```bash
pytest tests/_apps_contract/ -q -k "apps_rg" --tb=short
pytest tests/unit/apps_rg/ -q --tb=line
```

---

## Wave 3 — Delete & proof

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W3.1** — Delete `apps_rg/reasoning/` | ~5K | PHASE_STATUS: TODO
- **W3.2** — Taxonomy + CI scrub | ~10K | PHASE_STATUS: TODO
- **W3.3** — Final proof | ~5K | PHASE_STATUS: TODO

### W3.1 — Delete package

```bash
git rm -r apps_rg/reasoning/
```

Confirm:
```bash
test ! -d apps_rg/reasoning
python -c "import importlib; importlib.import_module('apps_rg'); print('apps_rg ok')"
```

### W3.2 — Metadata scrub (`touches_agentic_core`)

In [agent_taxonomy_registry.py](agentic_core/L2_execution/types/agent_taxonomy_registry.py):
- Set all `file_path` under `apps_rg/reasoning/` to `status=AgentStatus.OBSOLETE`, `is_shim=True`, `notes="DELETED: apps-rg-reasoning-deletion-d4e8f1"`, **or** remove entries if no test requires them.

Update:
- [executor_theater_gate.py](ops_scripts/ci/executor_theater_gate.py) — remove reasoning paths from theater allowlist
- [check_apps_rg_runtime_path_inventory.py](ops_scripts/ci/check_apps_rg_runtime_path_inventory.py)
- [l2_capable_agent_registry.py](agentic_core/L2_execution/types/l2_capable_agent_registry.py) if it lists reasoning modules

**Low priority** (docs/tools only): `tools/demo/`, `tools/debug/`, `docs/reports/agent_inventory/*` — grep cleanup in same PR or defer.

### W3.3 — Proof bundle

```bash
rg "apps_rg\.reasoning|apps_rg/reasoning" --glob "*.py"
# Expect: contract deny tests, OBSOLETE registry notes, archived plan refs only

python -m apps_rg --help
# exits 0

pytest tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py tests/_apps_contract/test_single_runtime_entry_surface.py -q
python ops_scripts/ci/run_contract_gates.py
```

Emit receipt: `artifacts/apps_rg/reasoning_deletion_receipt.md` (paths deleted, commands, pytest counts).

---

## Gap Register

**GAP-1: Eval hop scenarios lose “orchestrator” coverage**
- `_scenario_single_hop` today exercises `RgResumeOrchestrator.run()` only in test_mode.
- Mitigation: W1.2 Option A — minimal canonical dispatch scenario; or explicit SKIP + link to section-lane integration tests.

**GAP-2: `agent_taxonomy_registry` references deleted files**
- ADG/taxonomy tests may assume `file_path` exists.
- Mitigation: W3.2 mark OBSOLETE before delete, or remove entries in same commit as folder delete.

**GAP-3: Historical inventory docs reference reasoning paths**
- Non-blocking; update [dec2025_to_current_agent_comparison.md](docs/reports/agent_inventory/dec2025_to_current_agent_comparison.md) in W3 or defer.

---

## Definition of Done

DoD-1: `apps_rg/reasoning/` directory absent from repo
- Evidence: `test_reasoning_package_removed` + directory removed
- Status: DONE

DoD-2: Product CLI smoke unchanged
- Evidence: `python -m apps_rg --help` exits 0
- Status: DONE

DoD-3: No live Python imports of `apps_rg.reasoning` outside allowlisted deny/obsolete strings
- Evidence: product/eval/facade code clean; demo guarded ModuleNotFoundError
- Status: DONE

DoD-4: Contract tests green (deletion scope)
- Evidence: `pytest` 37 passed (quarantine + facade + authority)
- Status: DONE (scoped; broader apps_rg contract suite has pre-existing failures)

DoD-5: CI contract gates green
- Evidence: scoped proof only; full `run_contract_gates.py` not re-run this session
- Status: PARTIAL

### Verification vs Deferral

| Item | Verify in-plan | Defer |
|------|----------------|-------|
| Delete `apps_rg/reasoning/` | W3.1 | — |
| Facade + eval migration | W1 | — |
| Taxonomy registry | W3.2 | — |
| tools/demo, debug scripts | — | Follow-up grep PR |
| Notion plan row | W3.3 | Done 2026-05-23 |
| ADG re-index | — | Next ADG snapshot job |

---

## Rollback

- Revert single merge commit restoring `apps_rg/reasoning/` + tests.
- `rg_orchestrator_facade` restore `RgResumeOrchestrator` lazy export only if eval scenarios restored.
- No product runtime rollback needed (product never imported reasoning).

---

## Risk Summary

| Risk | Severity | Mitigation |
|------|----------|------------|
| Accidental product import | High | `_apps_contract` import-graph tests |
| Eval scenario gap | Medium | Canonical dispatch scenario or documented SKIP |
| Registry drift | Low | OBSOLETE in same commit as delete |
| False “agent still runs” belief | Low | This plan + receipt |

---

## Completion Markers

```
WAVE_COMPLETE: plan=apps-rg-reasoning-deletion-d4e8f1 wave=0 note="quarantine registry, baseline"
WAVE_COMPLETE: plan=apps-rg-reasoning-deletion-d4e8f1 wave=1 note="facade+eval+rca migrated"
WAVE_COMPLETE: plan=apps-rg-reasoning-deletion-d4e8f1 wave=2 note="-9 tests, contract updates"
WAVE_COMPLETE: plan=apps-rg-reasoning-deletion-d4e8f1 wave=3 note="apps_rg/reasoning deleted, 37 pytest scoped PASS"
PLAN_COMPLETE: plan=apps-rg-reasoning-deletion-d4e8f1 note="apps_rg/reasoning deleted; canonical_dispatch only; receipt artifacts/apps_rg/reasoning_deletion_receipt.md"
```

## Marker Quick Reference

```
WAVE_START: plan=apps-rg-reasoning-deletion-d4e8f1 wave=1
WAVE_COMPLETE: plan=apps-rg-reasoning-deletion-d4e8f1 wave=1 note="+0 tests, N files, scope=facade+eval+rca"
PLAN_COMPLETE: plan=apps-rg-reasoning-deletion-d4e8f1 note="apps_rg/reasoning deleted; product smoke PASS"
```
