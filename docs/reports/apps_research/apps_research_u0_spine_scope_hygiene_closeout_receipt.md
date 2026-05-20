# apps_research U0/Spine — Scope Hygiene Closeout

STATUS: PASS

## SUMMARY

Scope-hygiene wave completed after critical review. Unrelated `apps_qna`, `apps_lic`, and `u0_runtime_package_binding` edits were reverted from the working tree. Default CLI U0/profile convergence, Phase 0–1 deletes, justified package-driven PA/L2 core fixes, and new governance tests for the no-legacy-default-path rule are preserved and re-proven.

## SCOPE_MATCH

| Bucket | Status |
|--------|--------|
| `apps_research` convergence + PA prompt assets | **In wave** |
| Justified `agentic_core` PA/L2 (3 files) | **In wave** |
| `apps_qna` / `apps_lic` tracked edits | **Reverted** — not in wave |
| `u0_runtime_package_binding.py` | **Reverted** — not on apps_research U0 path |
| `apps_rg/*` local edits | **Out of scope** — left untouched, not part of commit |

## FILES_CHANGED

- [__main__.py](apps_research/__main__.py)
- [profile_builder_adapter.py](apps_research/runtime/profile_builder_adapter.py)
- [__init__.py](apps_research/runtime/u0/__init__.py)
- [prompt_registry.yaml](apps_research/prompts/prompt_registry.yaml) *(add to commit)*
- [templates/*.jinja](apps_research/prompts/templates/)
- [check_apps_research_import.py](ops_scripts/ci/check_apps_research_import.py)
- [test_w1_hardening_active_runtime_path.py](tests/apps_research/test_w1_hardening_active_runtime_path.py)
- [test_apps_research_ag9_spine.py](tests/_apps_contract/test_apps_research_ag9_spine.py)
- [test_app_ingress_runner.py](tests/_archived_obsolete/unit/agentic_core/runtime/entry/test_app_ingress_runner.py)
- [test_apps_research_spine.py](tests/governance/test_apps_research_spine.py)
- [test_apps_research_entrypoint_purity.py](tests/governance/test_apps_research_entrypoint_purity.py)
- [apps_research_pa_binding.py](agentic_core/prompt_governance/apps_research_pa_binding.py)
- [pa_package_driven_binding.py](agentic_core/prompt_governance/pa_package_driven_binding.py)
- [l2_package_driven_executor.py](agentic_core/L2_execution/l2_package_driven_executor.py)

## FILES_DELETED

- [__main__.py.new](apps_research/__main__.py.new)
- [base_research_engine.py.quarantine](apps_research/engines/base_research_engine.py.quarantine)
- [company_brief_engine.py.quarantine](apps_research/engines/company_brief_engine.py.quarantine)
- [research_ingress_runner.py](apps_research/integrations/research_ingress_runner.py)

## OUT_OF_SCOPE_FILES_REMOVED_FROM_WAVE

**Reverted (tracked):**

- `agentic_core/runtime/entry/u0_runtime_package_binding.py`
- `apps_lic/contracts/apps_lic_ingress_field_map.v1.yaml`
- `tests/_apps_contract/test_w1_qna_spine_migration.py`
- `apps_qna/runtime/bindings/u0_binding.py`
- `apps_qna/runtime/profile_builder.py`
- `apps_qna/` engine/router deletions and related tracked paths (restored via `git checkout -- apps_qna/`)
- `tests/apps_qna/governance/test_apps_qna_entrypoint.py`

**Left on disk, not staged (untracked user work — do not include in apps_research commit):**

- `apps_qna/config/domain_contract/runtime_customization_package.card_pack_build.v1.yaml`
- `apps_qna/config/domain_contract/runtime_package_registry.yaml`
- `apps_qna/runtime/u0_package_store.py`
- `apps_lic/scripts/_wizard_input_r3r4_*.json`
- `apps_rg/*` modified files (separate workstream)

## AGENTIC_CORE_DIFF_REVIEW

### Justified (kept)

| File | Purpose |
|------|---------|
| [pa_package_driven_binding.py](agentic_core/prompt_governance/pa_package_driven_binding.py) | Repo-root loader fix, JSON schema load, FEC/SlotContent compatibility, slot key mapping — required for apps_research PA to complete |
| [apps_research_pa_binding.py](agentic_core/prompt_governance/apps_research_pa_binding.py) | Absolute prompt profile path; test alias `pa_compose_apps_research` |
| [l2_package_driven_executor.py](agentic_core/L2_execution/l2_package_driven_executor.py) | `compilation_hash` fallback when `prompt_hash` absent on `CompiledPromptArtifact` |

No authority widening, route bypass, or gate removal in these diffs.

### Reverted / isolated

| File | Reason |
|------|--------|
| [u0_runtime_package_binding.py](agentic_core/runtime/entry/u0_runtime_package_binding.py) | apps_research profile uses `u0_validate_apps_research`, not `u0_resolve_runtime_package` — no runtime dependency proved |

## DEFAULT_CLI_U0_PROOF

- Path: `main()` → `_run_product_research` → `_run_profile_spine` → `AppIngressRunner(profile=build_app_runtime_contract()).run(payload)`
- `build_app_runtime_contract().u0 is u0_validate_apps_research` — **U0_BINDING_OK**
- `--spine` strips flag only; same `_run_profile_spine` path
- Stub CLI run exit **0** (`APPS_RESEARCH_L2_FORCE_STUB=1`)

## NO_DEFAULT_LEGACY_PATH_PROOF

New governance tests in [test_apps_research_entrypoint_purity.py](tests/governance/test_apps_research_entrypoint_purity.py):

- `test_apps_research_main_default_path_no_legacy_capability_registry`
- `test_apps_research_main_default_path_uses_profile_spine_call_chain`

Updated [test_apps_research_spine.py](tests/governance/test_apps_research_spine.py): `test_apps_research_main_routes_through_profile_spine`

Modules may still exist on disk (`research_capability_registry`, `GovernedResearchRun`) — Phase 3 deferred; tests forbid `__main__` wiring only.

## TOMBSTONE_PROOF

- `import apps_research.runtime.entry.dispatch` → governed **ImportError** (exit 1 expected)
- `check_no_shadow_spine.py` NC-4 → exit **0**

## COMMANDS_RUN

| Command | Exit |
|---------|------|
| `git status --short` | 0 |
| `python -m compileall apps_research agentic_core apps_shared -q` | 0 |
| `python -m apps_research --help` | 0 |
| `APPS_RESEARCH_L2_FORCE_STUB=1 python -m apps_research --topic ...` | 0 |
| U0 binding assertion | 0 |
| Tombstone import | 1 (expected) |
| `python ops_scripts/ci/check_no_shadow_spine.py` | 0 |
| `python ops_scripts/ci/check_apps_research_import.py` | 0 |

## TESTS_GATES

| Suite | Exit | Count |
|-------|------|-------|
| governance spine + purity + hop | 0 | 26 passed |
| spine alignment | 0 | 110 passed |
| w1 hardening + ag9 spine | 0 | 25 passed |
| new legacy-path + profile-spine tests | 0 | 3 passed |

## DRIFT_FOUND

- Untracked `apps_qna` config/runtime files remain locally — excluded from wave commit
- Untracked `apps_lic` wizard JSON — excluded
- **`apps_rg/*` still modified in working tree** — not reverted (outside user revert list); must not ship with apps_research commit

## PROOF_CLASSIFICATION

- **CONTRACT_TEST_PROOF:** 164 pytest (includes new governance tests)
- **CANONICAL_RUNTIME_PROOF (stub):** default CLI U0→Exit with `APPS_RESEARCH_L2_FORCE_STUB=1`

## EXPLICIT_NON_CLAIMS

- No live provider / LLM proof
- No release eligibility
- No Phase 3 deletion (`ResearchOrchestrator`, `GovernedResearchRun`, registry modules)
- No dispatch tombstone removal
- Stub L2 is not live LLM proof
