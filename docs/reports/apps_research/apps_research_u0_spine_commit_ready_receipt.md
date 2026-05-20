# apps_research U0/Spine — Commit-Ready Verification Receipt

STATUS: PASS

## COMMIT_SCOPE

Staged index contains **only** apps_research convergence, PA prompt assets, three justified `agentic_core` package-driven PA/L2 fixes, related ops/CI, governance/contract tests, Phase 0–1 deletes, and scope-hygiene closeout doc.

**Excluded from stage (verified absent from `git diff --cached`):**

- `apps_qna/*`
- `apps_lic/*`
- `apps_rg/*`
- `config/profiles/apps_rg/*`
- `agentic_core/runtime/entry/u0_runtime_package_binding.py`

## STAGED_FILES

```
M  agentic_core/L2_execution/l2_package_driven_executor.py
M  agentic_core/prompt_governance/apps_research_pa_binding.py
M  agentic_core/prompt_governance/pa_package_driven_binding.py
M  apps_research/__main__.py
D  apps_research/__main__.py.new
D  apps_research/engines/base_research_engine.py.quarantine
D  apps_research/engines/company_brief_engine.py.quarantine
D  apps_research/integrations/research_ingress_runner.py
A  apps_research/prompts/prompt_registry.yaml
A  apps_research/prompts/templates/few_shot_examples_v1.jinja
A  apps_research/prompts/templates/provider_controls_v1.jinja
A  apps_research/prompts/templates/repair_hints_v1.jinja
A  apps_research/prompts/templates/safety_fences_v1.jinja
A  apps_research/prompts/templates/task_instructions_v1.jinja
M  apps_research/runtime/profile_builder_adapter.py
M  apps_research/runtime/u0/__init__.py
A  docs/reports/apps_research/apps_research_u0_spine_scope_hygiene_closeout_receipt.md
M  ops_scripts/ci/check_apps_research_import.py
M  tests/_apps_contract/test_apps_research_ag9_spine.py
M  tests/_archived_obsolete/unit/agentic_core/runtime/entry/test_app_ingress_runner.py
M  tests/apps_research/test_w1_hardening_active_runtime_path.py
M  tests/governance/test_apps_research_entrypoint_purity.py
M  tests/governance/test_apps_research_spine.py
```

**Count:** 23 paths staged (4 deletes, 6 adds, 13 modifies).

## UNSTAGED_OUT_OF_SCOPE_FILES

| Path pattern | Status |
|--------------|--------|
| `apps_qna/__main__.py`, `apps_qna/runtime/bindings/l2_binding.py`, `apps_qna/u0_intake.py` | Modified, **not staged** |
| `apps_qna/config/*`, `apps_qna/runtime/u0_package_store.py` | Untracked, **not staged** |
| `apps_rg/*`, `config/profiles/apps_rg/pipeline_defaults.yaml` | Modified, **not staged** |
| `tests/apps_qna/*`, `tests/unit/apps_rg/*` | Modified, **not staged** |
| `apps_lic/scripts/_wizard_input_r3r4_*.json` | Untracked, **not staged** |
| `u0_runtime_package_binding.py` | Clean (no diff) |

## DEFAULT_CLI_U0_PROOF

- Call chain: `main()` → `_run_product_research` → `_run_profile_spine` → `AppIngressRunner(profile=build_app_runtime_contract()).run(payload)`
- `build_app_runtime_contract().u0 is u0_validate_apps_research` → **U0_BINDING_OK**
- `APPS_RESEARCH_L2_FORCE_STUB=1 python -m apps_research --topic "test governed research topic" --mode quick --depth shallow` → exit **0**, `exit_status=success`

## NO_DEFAULT_LEGACY_PATH_PROOF

`apps_research/__main__.py` grep: no `research_capability_registry`, `resolve_company_brief_capability`, `GovernedResearchRun(`, `_run_canonical`.

Governance tests (in staged set):

- `test_apps_research_main_default_path_no_legacy_capability_registry`
- `test_apps_research_main_default_path_uses_profile_spine_call_chain`
- `test_apps_research_main_routes_through_profile_spine`

## TOMBSTONE_PROOF

- `python -c "import apps_research.runtime.entry.dispatch"` → exit **1**, governed `ImportError` (RETIRED message)
- `check_no_shadow_spine.py` NC-4 → exit **0**

## COMMANDS_RUN

| Command | Exit |
|---------|------|
| `git status --short` | 0 |
| `git diff --cached --name-status` | 0 (23 wave paths) |
| `git diff --name-status` (unstaged) | 0 (includes out-of-scope; not staged) |
| `python -m compileall apps_research agentic_core apps_shared -q` | 0 |
| `python -m apps_research --help` | 0 |
| Stub default CLI `--topic ...` | 0 |
| U0 binding assertion | 0 |
| Tombstone import | 1 (expected) |
| `python ops_scripts/ci/check_no_shadow_spine.py` | 0 |
| `python ops_scripts/ci/check_apps_research_import.py` | 0 |

## TESTS_GATES

| Suite | Exit | Result |
|-------|------|--------|
| governance spine + purity + hop | 0 | 26 passed |
| `test_apps_research_spine_alignment` | 0 | 110 passed |
| w1 hardening + ag9 spine | 0 | 25 passed |

*(Pytest run with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and `-p pytest_timeout` due to `pytest.ini` `--timeout=180` addopts.)*

## PROOF_CLASSIFICATION

- **CONTRACT_TEST_PROOF:** 161 pytest (wave-related suites)
- **CANONICAL_RUNTIME_PROOF (stub):** default CLI U0→Exit with `APPS_RESEARCH_L2_FORCE_STUB=1`
- **COMMIT_SCOPE_PROOF:** staged index matches wave file list; forbidden paths absent from cache

## EXPLICIT_NON_CLAIMS

- No live provider / LLM runtime proof
- No release eligibility
- No Phase 3 module deletions
- No dispatch tombstone removal
- Stub L2 is not live LLM proof
- Staging performed for verification; user must run `git commit` when ready
