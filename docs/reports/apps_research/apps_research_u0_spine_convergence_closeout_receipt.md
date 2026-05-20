# apps_research U0 / Spine Convergence — Closeout Receipt

STATUS: PASS

## SUMMARY

Default `python -m apps_research --topic ...` now enters through `AppIngressRunner(profile=build_app_runtime_contract())` with core U0 binding `u0_validate_apps_research`, sequencing U0→L1→L0→C0→PA→L2→Exit. Phase 0–1 shadow files were deleted; stale dispatch references were repointed; runtime proof completed with `APPS_RESEARCH_L2_FORCE_STUB=1` (stub L2, not live provider).

## FILES_CHANGED

- [__main__.py](apps_research/__main__.py)
- [profile_builder_adapter.py](apps_research/runtime/profile_builder_adapter.py)
- [__init__.py](apps_research/runtime/u0/__init__.py)
- [prompt_registry.yaml](apps_research/prompts/prompt_registry.yaml)
- [safety_fences_v1.jinja](apps_research/prompts/templates/safety_fences_v1.jinja)
- [task_instructions_v1.jinja](apps_research/prompts/templates/task_instructions_v1.jinja)
- [few_shot_examples_v1.jinja](apps_research/prompts/templates/few_shot_examples_v1.jinja)
- [provider_controls_v1.jinja](apps_research/prompts/templates/provider_controls_v1.jinja)
- [repair_hints_v1.jinja](apps_research/prompts/templates/repair_hints_v1.jinja)
- [check_apps_research_import.py](ops_scripts/ci/check_apps_research_import.py)
- [test_w1_hardening_active_runtime_path.py](tests/apps_research/test_w1_hardening_active_runtime_path.py)
- [test_apps_research_ag9_spine.py](tests/_apps_contract/test_apps_research_ag9_spine.py)
- [test_app_ingress_runner.py](tests/_archived_obsolete/apps_research/test_app_ingress_runner.py)
- [apps_research_pa_binding.py](agentic_core/prompt_governance/apps_research_pa_binding.py)
- [pa_package_driven_binding.py](agentic_core/prompt_governance/pa_package_driven_binding.py)
- [l2_package_driven_executor.py](agentic_core/L2_execution/l2_package_driven_executor.py)

## FILES_DELETED

- [__main__.py.new](apps_research/__main__.py.new)
- [base_research_engine.py.quarantine](apps_research/engines/base_research_engine.py.quarantine)
- [company_brief_engine.py.quarantine](apps_research/engines/company_brief_engine.py.quarantine)
- [research_ingress_runner.py](apps_research/integrations/research_ingress_runner.py)

## DEFAULT_CLI_CONVERGENCE

**Old path observed:** `__main__` → `_run_canonical` → `research_capability_registry` → `GovernedResearchRun` / `GovernedAppRunner` (L1 entry, U0 bypass).

**New path proven:** `__main__` → `_run_product_research` → `_run_profile_spine` → `AppIngressRunner(profile=build_app_runtime_contract()).run(payload)` → U0→L1→L0→C0→PA→L2→Exit.

**U0 binding proof:** `build_app_runtime_contract().u0 is u0_validate_apps_research` (assertion script printed `U0_BINDING_OK`).

**`--spine`:** Remains equivalent — same `_run_profile_spine` / profile path (alias preserved in CLI).

## COMMANDS_RUN

| Command | Exit code |
|---------|-----------|
| `python -m compileall apps_research agentic_core apps_shared -q` | 0 |
| `python -m apps_research --help` | 0 |
| `APPS_RESEARCH_L2_FORCE_STUB=1 python -m apps_research --topic "test governed research topic" --mode quick --depth shallow` | 0 |
| U0 binding assertion (`build_app_runtime_contract().u0 is u0_validate_apps_research`) | 0 |
| `python -c "import apps_research.runtime.entry.dispatch"` (tombstone ImportError) | 1 (expected) |
| `python ops_scripts/ci/check_no_shadow_spine.py` | 0 |
| `python ops_scripts/ci/check_apps_research_import.py` | 0 |

## TESTS_GATES

| Command | Exit code |
|---------|-----------|
| `pytest -p pytest_timeout tests/governance/test_apps_research_spine.py tests/governance/test_apps_research_entrypoint_purity.py tests/governance/test_apps_research_hop_discipline.py -q` | 0 (24 passed) |
| `pytest -p pytest_timeout tests/_apps_contract/test_apps_research_spine_alignment.py -q` | 0 (110 passed) |
| `pytest -p pytest_timeout tests/apps_research/test_w1_hardening_active_runtime_path.py tests/_apps_contract/test_apps_research_ag9_spine.py -q` | 0 (25 passed) |

## RUNTIME_ARTIFACTS

- CLI run (stub L2): `exit_status=success`, `outcome_authorized=True`
- Example artifact: [company_brief.json](artifacts/apps_research/runs/20260520_203623864535_0000_research-run-86cd6a8a37d5/company_brief.json)

## SHADOWS_REMOVED

- `apps_research/__main__.py.new`
- `apps_research/engines/base_research_engine.py.quarantine`
- `apps_research/engines/company_brief_engine.py.quarantine`
- `apps_research/integrations/research_ingress_runner.py`

## SHADOWS_LEFT_IN_PLACE

- `ResearchOrchestrator.py`, enterprise orchestrator, dry-run tool, agents, renderer, hollow services — Phase 3, not on default product path.
- [dispatch.py](apps_research/runtime/entry/dispatch.py) tombstone — NC-4 in `check_no_shadow_spine.py` still expects governed ImportError.
- W9 judge stubs, L6 placeholder, sanctioned infra shims — explicitly retained per wave scope.

## STALE_REFERENCES_FIXED

- [check_apps_research_import.py](ops_scripts/ci/check_apps_research_import.py) — profile builder instead of deleted `apps_research_dispatch`
- [test_w1_hardening_active_runtime_path.py](tests/apps_research/test_w1_hardening_active_runtime_path.py) — profile spine assertions
- [test_apps_research_ag9_spine.py](tests/_apps_contract/test_apps_research_ag9_spine.py) — package-driven PA/L2 contract shape
- [test_app_ingress_runner.py](tests/_archived_obsolete/apps_research/test_app_ingress_runner.py) — removed `research_ingress_runner` parametrization

## FORBIDDEN_FILES_TOUCHED

**agentic_core: yes** — minimal package-driven PA/L2 compatibility fixes required for end-to-end profile spine (repo root path resolution, JSON schema load, `SlotContent` fields, `compilation_hash`/`prompt_hash` bridge, FEC field tolerance). Pre-existing unstaged diffs also present in `evidence_shaper.py` and `hybrid_search_engine.py` (not introduced by this wave's convergence edits).

## PROOF_CLASSIFICATION

- **CONTRACT_TEST_PROOF:** governance + spine alignment + AG9/W1 suites (159 tests).
- **CANONICAL_RUNTIME_PROOF:** default CLI completed U0→Exit with stub L2 (`APPS_RESEARCH_L2_FORCE_STUB=1`); not live LLM/provider proof.

## EXPLICIT_NON_CLAIMS

- No release eligibility claim.
- No Phase 3 `ResearchOrchestrator` deletion claim.
- No dispatch tombstone deletion claim.
- No mock-only proof represented as live provider/runtime ALLOW.

## NEXT_BLOCKER

None for this wave scope. Live-provider L2 proof (without `APPS_RESEARCH_L2_FORCE_STUB`) is a separate follow-up if product signoff requires it.
