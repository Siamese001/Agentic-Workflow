---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-research-spine-alignment-d4e8f2__dup270.md'
original_relative_path: 'apps-research-spine-alignment-d4e8f2__dup270.md'
source_sha256: 2ca0f82b74b7a8e5bbccfd5f14feb6e5e9b93fb5d1f3476d5c39ecf63abacd38
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-research-spine-alignment-d4e8f2
plan_type: refactor
---

# apps_research Canonical Spine Alignment

Refactor `apps_research` to align with the canonical `agentic_core` spine — pure `__main__.py` shim, core-owned route/capability resolution, governed Prompt Assembly, briefing-grade C0 retrieval, correct L2 E1-E5 lifecycle, FEC + Exit v6 + L6/UWG proof — eliminating every wiring failure pattern identified during `apps_lic` review.

---

## Context (SCQA)

- **Situation** — `apps_research` has an `__main__.py` that directly imports and calls `apps_research.scripts.run_research.main` (line 226), bypassing canonical `agentic_core` runner/capability resolution. Engines (`company_brief_engine.py`, `research_assembly_engine.py`, `query_decomposer.py`) are imported directly; synthesis prompt strings live ad hoc in engine code; there is no governed Prompt Assembly layer, no `CompiledPromptArtifact`, and the C0 retrieval path lacks the briefing-grade evidence contracts (`BriefingCoverageMatrix`, `ClaimEvidenceMap`, `ContradictionMatrix`, `FreshnessReport`, `SynthesisGuidanceForPA`) required by the canonical spine. FEC and Exit v6 are wired in cert-mode only.

- **Complication** — `apps_lic` review surfaced a repeating failure pattern: app-owned recipe resolution, handmade `l2_callable` closures, ad hoc prompt strings, placeholder PA templates, provider calls without `CompiledPromptArtifact`, blurred Exit/UWG boundaries, and legacy runner fall-throughs. `apps_research` has the same class of defects and is a primary upstream dependency for `apps_rg` and `apps_lic` research nodes. Leaving it off-spine means every downstream consumer inherits ungoverned evidence and synthesis paths.

- **Question** — How do we bring `apps_research` into full canonical spine alignment (P0 entrypoint purity, P1.5 Prompt Assembly, W1-W4 spine wiring, W5 acceptance sweep) without breaking existing cert-path tests or deferred-scope items?

- **Answer** — Implement in five ordered phases: P0 creates 20 hard governance tests and the capability/registry scaffold; P1.5 creates governed PA templates and the `research_pa_compiler`; W1-W4 wire the full spine; W5 runs the acceptance sweep, quarantines the legacy runner, and produces the final YES/NO spine-alignment verdict.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_research/__main__.py` L226 `from apps_research.scripts.run_research import main as run_main` | Root impurity: main imports legacy runner | confirmed |
| `apps_research/engines/company_brief_engine.py` (36 KB) | Contains synthesis logic, likely ad hoc prompt strings | inspect W3 |
| `apps_research/engines/query_decomposer.py` | Coverage family catalog, depth profiles; no PA layer | reviewed prior session |
| `apps_research/integrations/governed_research_run.py` | GovernedResearchRun orchestrator — no CompiledPromptArtifact | inspect P1.5 |
| `apps_research/integrations/execution_adapter.py` | L2 adapter path — check for ad hoc provider calls | inspect W3 |
| `apps_lic` plan `apps-lic-entrypoint-purity-recipe-registry-d4f1a8` | Failure-pattern source and pattern to prevent | confirmed |
| `apps_rg` plan `apps-rg-l2-recipe-adapter-final-core-bound-d9f4a2` | Pattern for core-owned recipe resolution | confirmed |
| `apps_research/config/route_registry.yaml` | Existing route config; verify R3_SIMPLE_GROUNDED_READ present | inspect P0 |

---

## Wave Structure

| Wave | Phase IDs | Focus | Checkpoint | Est. Tokens |
|------|-----------|-------|------------|-------------|
| P0 | P0.1, P0.2, P0.3 | 20 governance tests (RED) + capability/registry scaffold + route config | P0 gate: 20 tests collected, >=18 fail red | ~22K |
| P1.5 | P1.5.1, P1.5.2, P1.5.3 | PromptBOM + prompt_registry + 5 real template bodies + research_pa_compiler | P1.5 gate: 25 PA tests pass green | ~35K |
| W1-W2 | W1.1, W1.2, W2.1, W2.2 | Pure shim + core runner wiring; C0 briefing-grade evidence contracts + depth profiles | W1-W2 gate: shim tests green, C0 gate tests green | ~30K |
| W3-W4 | W3.1, W3.2, W4.1, W4.2 | PA -> L2 E1-E5 synthesis path; ad hoc prompt removal; FEC + Exit v6 + L6/UWG proof | W3-W4 gate: sealed artifact tests green, FEC/Exit tests green | ~28K |
| W5 | W5.1, W5.2 | Acceptance sweep (40 spine + 35 negative controls); legacy quarantine + YES/NO verdict | W5 gate: full verdict emitted | ~18K |

**Total: ~133K tokens across 5 phases, all gated**

---

## Out Of Scope

- `apps_rg` internals beyond its research dependency call
- `apps_lic` internals beyond its research dependency call
- DS-C Spearman calibration (blocked on human annotation, tracked separately)
- `apps_underwriting_ai`, `apps_rfp`, `apps_qna`, `apps_exec` spine wiring
- Production log mining or PII redaction
- Real LLM provider calls in tests (all tests use mocked/fixture providers)
- Removing or renaming existing passing contract tests in `tests/_apps_contract/`
- Any changes to `agentic_core` L4/L6 canonical APIs (`apps_research` adapts; core does not change)
- `hop_*` engine file deletion beyond quarantine/archival in W5 (scope to W5.2 only)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0.1 | 20 hard governance tests (RED) | `tests/governance/test_apps_research_entrypoint_purity.py`, `test_apps_research_recipe_resolution.py`, `test_apps_research_no_legacy_runner.py`, `test_apps_research_provider_boundary.py`, `test_apps_research_l4_write_boundary.py` | Tests must fail initially (RED-GREEN discipline) | ~8K | ✅ DONE |
| P0.2 | Capability/registry scaffold (stubs) | `apps_research/integrations/research_capability_registry.py`, `research_l2_step_adapters.py`, `research_c0_adapter.py`, `research_exit_fec_producer.py` | Stubs only — raise NotImplementedError on all callable bodies | ~8K | ✅ DONE |
| P0.3 | Route/capability config verification | `apps_research/config/route_registry.yaml` add `l3_required: false`, `execution_form: SINGLE_STEP`, `selected_capability: apps_research.company_brief_v1` | Config-only; no behavior change | ~6K | ✅ DONE |
| P1.5.1 | PromptBOM + prompt_registry YAML | `apps_research/prompt_assembly/prompt_bom.yaml`, `apps_research/config/prompt_registry.yaml` | Exact schema from spec; hash_fields required | ~8K | ✅ DONE |
| P1.5.2 | 5 governed template bodies | `apps_research/prompt_assembly/templates/company_brief_synthesis_v1.yaml`, `briefing_evidence_to_prompt_context_v1.yaml`, `unsupported_claim_omission_v1.yaml`, `caveat_and_confidence_repair_v1.yaml`, `briefing_length_and_structure_repair_v1.yaml` | All must contain real content; zero placeholders; zero TODOs | ~15K | ✅ DONE |
| P1.5.3 | research_pa_compiler.py | `apps_research/prompt_assembly/research_pa_compiler.py` | Must emit CompiledPromptArtifact; must NOT retrieve/route/call providers | ~12K | ✅ DONE |
| W1.1 | __main__.py pure shim | `apps_research/__main__.py` remove `run_research` import; wire to `agentic_core` runner; fail-closed on missing capability | L226 legacy runner import is the direct target; cert-path preserved | ~8K | ✅ DONE |
| W1.2 | Core runner + capability resolution binding | `apps_research/integrations/research_capability_registry.py` full impl; `agentic_core` runner registration for `apps_research.company_brief_v1` | Must match agentic_core runner registration API | ~10K | ✅ DONE |
| W2.1 | C0 briefing-grade evidence contracts | `apps_research/integrations/research_c0_adapter.py` full impl; `apps_research/types/briefing_evidence_contracts.py` (8 contract dataclasses); C0-to-PA gate (PASS / WEAK_WITH_CAVEATS / FAIL_DEGRADE) | New dataclasses/schemas; no provider calls | ~12K | ✅ DONE |
| W2.2 | C0 depth profile enforcement + adaptive coverage | `apps_research/engines/query_decomposer.py` updated depth profiles (LIGHT/STANDARD/DEEP/DOSSIER from spec); adaptive coverage section selector; 10-family canonical catalog | Existing 8-family DOSSIER test assertions need updating | ~8K | ✅ DONE |
| W3.1 | PA -> L2 synthesis path (E1-E5) | `apps_research/integrations/research_l2_step_adapters.py` full impl; L2.E1-E5 receipts; CompiledPromptArtifact consumed by E3; E4 heal uses repair templates | Must not build ad hoc prompt strings | ~12K | ✅ DONE |
| W3.2 | Ad hoc prompt string audit and removal | `apps_research/engines/company_brief_engine.py`, `research_assembly_engine.py`, `execution_adapter.py` remove inline prompt strings; redirect synthesis through PA compiler | Unknown scope of prompt string sprawl — biggest risk | ~8K | ✅ DONE |
| W4.1 | FEC producer + Exit v6 full wiring (all paths) | `apps_research/integrations/research_exit_fec_producer.py` full impl; FEC carries all 8 briefing-grade evidence refs + JD fields; `__main__.py` Exit hook on non-cert path | Currently cert-mode only; must work on all invocation paths | ~10K | ✅ DONE |
| W4.2 | L6/UWG boundary proof | Verify no direct L4 writes outside UWG; verify L6 does not mutate current run; `research_brief_uwg_writer.py` compliance check; tests for UWG-only write path | research_brief_uwg_writer.py already exists -- verify compliance | ~8K | ✅ DONE |
| W5.1 | Acceptance sweep: 40 spine + 35 negative controls | `tests/governance/` full 75-test sweep; all negative controls must fail-closed | Some tests need fixture/mock updates after W1-W4 | ~12K | ✅ DONE |
| W5.2 | Legacy quarantine + YES/NO final verdict | Archive `apps_research/scripts/run_research.py`; remove any remaining fallback from `__main__.py`; emit final acceptance report | Quarantine must not break cert-path | ~6K | ✅ DONE |

**Status legend**: TODO / IN PROGRESS / DONE / BLOCKED

---

## Gap Register

**GAP-1: `__main__.py` legacy runner import at line 226**
- `from apps_research.scripts.run_research import main as run_main` is called unconditionally on the non-cert path.
- Impact: entire canonical spine (capability resolution, C0, PA, L2 E1-E5, FEC, Exit) is bypassed on every normal invocation.

**GAP-2: No governed Prompt Assembly layer**
- `company_brief_engine.py` and `research_assembly_engine.py` contain synthesis logic with inline or ad hoc prompt construction — no `PromptBOM`, no `prompt_registry`, no `CompiledPromptArtifact`.
- Impact: synthesis is ungoverned; provider calls cannot be audited; no replay key; no manifest hash.

**GAP-3: C0 evidence contracts are partial**
- `query_decomposer.py` has depth profiles and family catalogs but no `BriefingCoverageMatrix`, `ClaimEvidenceMap`, `ContradictionMatrix`, `FreshnessReport`, `SynthesisGuidanceForPA`, or `SourcePortfolioSummary` output contracts.
- Impact: PA cannot receive canonical evidence input; FEC cannot carry briefing-grade evidence; Exit cannot verify groundedness.

**GAP-4: No core-owned capability/recipe resolution**
- `apps_research` resolves its own execution path via `run_research.main`. No `agentic_core` runner registration, no `R3_SIMPLE_GROUNDED_READ` capability binding, no fail-closed on missing capability.
- Impact: route enforcement, cache checks (R1A, R1B), and R5 pre-route fallback are all skipped.

**GAP-5: FEC + Exit v6 wired in cert-mode only**
- `_run_live_cert` emits FEC and invokes Exit; the normal `main()` path at L226 does not.
- Impact: production invocations emit no Exit disposition, no X3, no FEC evidence trail.

**GAP-6: L6/UWG boundary not verified on all paths**
- `research_brief_uwg_writer.py` exists but its invocation from `governed_research_run.py` is conditional/pending. No tests verify L4 writes occur only through UWG.
- Impact: direct L4 write risk on degraded or fallback paths.

**GAP-7: `hop_*` engine files use canonical DAG terminology**
- `hop_company_brief_engine.py`, `hop_research_assembly_engine.py`, `hop_research_retrieval_engine.py` — "hop" is canonical app DAG terminology; direct `apps_research` must not use it.
- Impact: naming and import confusion; risk of hop-style orchestration being imported on normal path.

---

## Execution Plan

### Phase P0 — Governance Tests + Scaffold + Config

**P0.1 scope**: Create five governance test files under `tests/governance/`. Tests use AST-parse or import-inspect of `apps_research/__main__.py` and related modules. No live execution needed. Tests MUST initially fail red.

**Test file index** (20 tests total):

`tests/governance/test_apps_research_entrypoint_purity.py` (9 tests):
1. `test_apps_research_main_is_pure_shim`
2. `test_apps_research_main_does_not_import_research_engines`
3. `test_apps_research_main_does_not_import_c0_adapters`
4. `test_apps_research_main_does_not_import_pa_compiler`
5. `test_apps_research_main_does_not_import_l2_adapters`
6. `test_apps_research_main_does_not_import_provider_sdks`
7. `test_apps_research_main_does_not_import_l4_write_surfaces`
8. `test_apps_research_main_contains_no_l2_callable_construction`
9. `test_apps_research_main_contains_no_inline_research_closure`

`tests/governance/test_apps_research_recipe_resolution.py` (7 tests):
10. `test_apps_research_core_runner_resolves_company_brief_capability`
11. `test_apps_research_route_registry_selects_r3_simple_grounded_read`
12. `test_apps_research_r3_requires_c0`
13. `test_apps_research_direct_path_uses_no_l3`
14. `test_apps_research_recipe_resolution_failure_fails_closed_through_exit`
15. `test_apps_research_no_generic_brief_when_recipe_missing`

`tests/governance/test_apps_research_no_legacy_runner.py` (2 tests):
16. `test_apps_research_no_legacy_runner_feature_flag`
17. `test_apps_research_legacy_scripts_not_reachable_from_main`

`tests/governance/test_apps_research_provider_boundary.py` (2 tests):
18. `test_apps_research_provider_calls_only_through_governed_gateway`
19. `test_apps_research_exit_emits_x3_but_does_not_write_l4`

`tests/governance/test_apps_research_l4_write_boundary.py` (1 test):
20. `test_apps_research_no_direct_l4_writes`

**P0.2 scope**: Four stub integration files — symbols exported, `raise NotImplementedError` on all callable bodies. No circular imports.

**P0.3 scope**: Inspect and patch `apps_research/config/route_registry.yaml` to include `l3_required: false`, `execution_form: SINGLE_STEP`, `selected_capability: apps_research.company_brief_v1` under the R3_SIMPLE_GROUNDED_READ route entry.

**Acceptance**:
```
pytest tests/governance/ -v  # 20 tests collected, >=18 fail red, 0 import errors
```

---

### Phase P1.5 — Prompt Assembly + Real Template Bodies

**P1.5.1 scope**: Create `apps_research/prompt_assembly/` package. Write `prompt_bom.yaml` and `apps_research/config/prompt_registry.yaml` using exact schemas from specification.

**P1.5.2 scope**: Write all 5 template YAML files with real slot bodies. `company_brief_synthesis_v1.yaml` uses verbatim slot_bodies from spec (S0-R0). The four repair/context templates must each contain real purpose, forbidden_behaviors, slot content requirements, input_contract, validation_rules, and hash_fields. Zero occurrences of "TODO", "placeholder", or "insert here" in any template.

**P1.5.3 scope**: Implement `research_pa_compiler.py`:
- load BOM and registry from YAML
- resolve template by template_id
- validate required slots, input contract, C0 evidence refs, JD fencing
- render structured slots, canonicalize bytes
- compute five hashes: `prompt_bom_hash`, `prompt_registry_hash`, `template_hash`, `manifest_hash`, `artifact_hash`
- emit `CompiledPromptArtifact` dataclass/TypedDict
- Forbidden imports: retrieval, routing, provider SDK, L4 write

**25 PA governance tests** (added to `tests/governance/test_apps_research_prompt_assembly.py`):
1-10. Core PA contract tests (see specification section "Prompt Assembly tests" items 1-10)
11-25. Template integrity tests (items 11-25)

**Acceptance**:
```
pytest tests/governance/test_apps_research_prompt_assembly.py -v  # 25 pass green
```

---

### Phase W1-W2 — Entrypoint Shim + C0 Evidence Contracts

**W1.1 scope**: Edit `apps_research/__main__.py`:
- Remove `from apps_research.scripts.run_research import main as run_main` (line 226)
- Replace `return int(run_main())` with call to `agentic_core` canonical runner passing `app_name="apps_research"`
- On runner/capability unavailable: emit R5 terminal packet via Exit v6 (`reason_code = CAPABILITY_UNAVAILABLE`); exit non-zero
- Preserve `_run_live_cert`, `_load_cert_route_entry`, `_build_exit_receipts`, `_maybe_run_exit_hook` unchanged

**W1.2 scope**: Full implementation of `research_capability_registry.py`:
- `register_company_brief_capability()` — registers with `agentic_core` runner: `route_id=R3_SIMPLE_GROUNDED_READ`, `execution_form=SINGLE_STEP`, `l3_required=False`, `selected_capability=apps_research.company_brief_v1`
- `resolve_company_brief_capability(app_name, route_id)` — delegates to `agentic_core` runner resolution API; raises `CapabilityUnavailableError` on failure

**W2.1 scope**: Implement all 8 C0 briefing-grade evidence contracts. Add C0-to-PA gate function:
```python
def evaluate_c0_gate(
    coverage_matrix: BriefingCoverageMatrix,
    source_portfolio: SourcePortfolioSummary,
    depth_profile: str,
) -> Literal["PASS", "WEAK_WITH_CAVEATS", "FAIL_DEGRADE"]
```
Gate thresholds from spec (PASS/WEAK/FAIL criteria for COMPANY_BRIEF_DEEP).

**W2.2 scope**: Update `query_decomposer.py` depth profiles to spec values. Replace 8-family catalog with 10-family canonical catalog. Implement adaptive section selector. Update affected spine alignment tests.

**Acceptance**:
```
pytest tests/governance/ -v             # P0 + P1.5 + W1-W2 governance tests green
pytest tests/_apps_contract/ -q --tb=no  # 0 regressions
```

---

### Phase W3-W4 — PA-L2 Synthesis Path + FEC/Exit/L6/UWG

**W3.1 scope**: Full implementation of `research_l2_step_adapters.py`:
- L2.E1 prep: verify all required fields from spec present (route_id, CompiledPromptArtifact, FinalEvidenceContract, BriefingCoverageMatrix, etc.)
- L2.E2 validate: evidence status usable, source refs exist, section coverage satisfies gate, freshness OK
- L2.E3 execute: consume `CompiledPromptArtifact` from PA compiler; call governed provider gateway; return candidate brief
- L2.E4 heal: use repair templates from PA compiler; forbidden actions enforced
- L2.E5 seal: emit `sealed_research_artifact` with all required refs from spec

**W3.2 scope**: Audit and remove all ad hoc prompt strings from `company_brief_engine.py`, `research_assembly_engine.py`, `execution_adapter.py`. Redirect synthesis calls through `research_pa_compiler`. Verify `test_apps_research_no_ad_hoc_prompt_strings_in_engines` passes green.

**W4.1 scope**: Full implementation of `research_exit_fec_producer.py`:
- `build_research_fec()` — builds FEC with all 8 briefing-grade evidence artifact refs, JD fields (ref, content_hash, parse receipt, theme coverage, JD-to-company evidence map, unsupported claim report, contradiction report) when JD present
- Wire Exit hook on non-cert path in `__main__.py` — not just in `_run_live_cert`

**W4.2 scope**: Compliance audit of `research_brief_uwg_writer.py`. Add tests:
- `test_apps_research_no_direct_l4_writes` (existing governance test) must now pass green
- `test_apps_research_durable_state_only_through_uwg`
- `test_apps_research_l6_does_not_mutate_current_run`

**Acceptance**:
```
pytest tests/governance/ -v             # all governance tests green
pytest tests/_apps_contract/ -q --tb=no  # 0 regressions
```

---

### Phase W5 — Acceptance Sweep + Legacy Quarantine

**W5.1 scope**: Full 75-test sweep:
- 40 spine tests (items 26-40 from spec "C0 and spine tests" + remaining from P0/P1.5)
- 35 negative control tests — every negative control from spec must fail-closed (assert error raised or degraded packet emitted, not silent pass)

Negative control categories:
- Missing RouteContract / FinalEvidenceContract
- COMPANY_BRIEF_DEEP with insufficient sources/anchors/coverage — must NOT proceed to PA as PASS
- JD violations (missing content_hash, treated as authority, JD company conflict, JD prompt injection)
- L2 forbidden actions (retrieve new evidence, write L4, switch provider silently)
- L6 current-run mutation attempt
- PA forbidden actions (retrieve, call provider, emit Exit)
- Exit errors (missing support score, missing evidence refs)

**W5.2 scope**:
- Move `apps_research/scripts/run_research.py` to `archives/apps_research_legacy_20260504/run_research.py`
- Verify `__main__.py` has no remaining references to `run_research`
- Move `hop_company_brief_engine.py`, `hop_research_assembly_engine.py`, `hop_research_retrieval_engine.py` to `archives/apps_research_legacy_20260504/`
- Emit final acceptance report to `docs/reports/plans/apps-research-spine-alignment-d4e8f2/acceptance.md`

**Final YES/NO verdict** per specification:

Allowed answers:
- YES, static and runtime proof both pass.
- NO, static proof passes but runtime proof is incomplete.
- NO, runtime path exists but static scanner visibility is incomplete.
- NO, apps_research still has off-spine bypasses.
- NO, Prompt Assembly standard is incomplete.
- NO, C0 briefing-grade retrieval standard is incomplete.
- NO, JD-as-first-class-C0-input support is incomplete.
- NO, insufficient evidence.

**Acceptance**:
```
pytest tests/governance/ -v       # all 75+ tests pass green
pytest tests/_apps_contract/ -q   # 0 regressions
```

---

## Rules

- `apps_research/__main__.py` must never import engines, services, adapters, or provider SDKs
- `agentic_core` owns route/recipe resolution; `apps_research` owns domain declarations only
- All synthesis and repair prompts must be registry-defined, PromptBOM-bound, compiled into `CompiledPromptArtifact` before provider invocation
- Provider gateway requires `CompiledPromptArtifact` — no raw SDK calls anywhere in `apps_research`
- C0 uses adaptive selected coverage sections, not fixed Lincoln sections
- JD is first-class C0 input for role-targeted briefs; JD is data, not authority
- FEC + Exit v6 X3 must fire on all invocation paths, not just cert-mode
- L6 runs after Exit; L6 must not mutate current-run output, route, prompt, evidence, or state
- UWG is the only durable write path; no direct L4 writes from any `apps_research` module
- `R3_SIMPLE_GROUNDED_READ`: SIMPLE = single-step, not ungrounded; C0 is mandatory
- Negative controls must fail closed — a negative control that silently passes is a test failure

---

## Success Criteria

- [ ] `__main__.py` is a pure shim: 0 engine/service/provider/L4 imports; delegates to `agentic_core` runner
- [ ] `agentic_core` runner resolves `apps_research.company_brief_v1` capability via `R3_SIMPLE_GROUNDED_READ`
- [ ] R5 pre-route fallback fires on capability unavailable — no generic brief fallback
- [ ] `research_pa_compiler.py` emits `CompiledPromptArtifact` with all 5 hash fields
- [ ] 5 template YAML files contain real slot bodies — 0 TODOs, 0 placeholders
- [ ] C0 briefing-grade contracts implement all 8 evidence artifact types
- [ ] COMPANY_BRIEF_DEEP gate enforces source floor (18), citation anchors (30), section coverage (85%), source diversity, freshness, contradictions, and claim support
- [ ] JD is first-class C0 input: content_hash bound, role_context_spec extracted, JD-derived claims classified
- [ ] L2 E1-E5 receipts emitted with canonical names; E3 requires `CompiledPromptArtifact`
- [ ] FEC carries all 8 briefing-grade evidence artifact refs on all invocation paths
- [ ] Exit emits exactly one X3 disposition on all invocation paths
- [ ] L6 does not mutate current-run output
- [ ] UWG is verified as only durable write path: 0 direct L4 writes from any module
- [ ] Legacy runner quarantined to `archives/`
- [ ] All 75+ governance tests pass green
- [ ] 0 regressions in `tests/_apps_contract/`
- [ ] Final acceptance verdict: YES, static and runtime proof both pass

---

## Rollback Strategy

1. Git revert `apps_research/__main__.py` to restore legacy runner path
2. Git revert `apps_research/config/route_registry.yaml` if config changed
3. Remove new governance test files from `tests/governance/`
4. Remove `apps_research/prompt_assembly/` directory
5. Restore archived legacy files from `archives/apps_research_legacy_*/` if W5 quarantine ran
6. Run `pytest tests/_apps_contract/ -q` to verify cert-path is clean

---

## Acceptance Criteria Table

| Metric | Target | Verification |
|---|---|---|
| Governance tests pass | >=75 green, 0 red after W5 | `pytest tests/governance/ -v` |
| Contract regressions | 0 | `pytest tests/_apps_contract/ -q --tb=no` |
| `__main__.py` engine imports | 0 | `test_apps_research_main_does_not_import_research_engines` |
| Ad hoc prompt strings in engines | 0 | `test_apps_research_no_ad_hoc_prompt_strings_in_engines` |
| Template files with placeholders | 0 | `test_apps_research_template_files_include_concrete_instruction_text` |
| Direct L4 writes | 0 | `test_apps_research_no_direct_l4_writes` |
| Negative controls that silently pass | 0 | `pytest tests/governance/ -k negative` |
| Final spine verdict | YES | `docs/reports/plans/apps-research-spine-alignment-d4e8f2/acceptance.md` |

---

## Cascade Alignment Checks

- Read `apps_research/__main__.py`, `company_brief_engine.py`, `execution_adapter.py`, and `route_registry.yaml` before writing any phase code.
- Check `agentic_core` runner registration API before implementing W1.2.
- Do not widen scope to `apps_rg` or `apps_lic` internals during execution.
- NEXT_STEP marker for any discovered issue outside the active phase scope.
- Each phase completes before the next begins — no parallel phase execution.
