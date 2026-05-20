# L2 rationalization — repo assessment

Generated: 2026-05-19T10:27:35Z (W0 refresh) · W1 ownership docs added (zero behavior change)

**ADG:** [adg_indexed_05172026_0651.sqlite](../../artifacts/adg/adg_indexed_05172026_0651.sqlite) — snapshot `05172026_0651`

**Machine-readable:** [l2_rationalization_repo_assessment.json](l2_rationalization_repo_assessment.json)

**W1 ownership docs (new):**

- [l2_ownership_model.md](l2_ownership_model.md) — L2.2/2.3/2.4 ↔ E1–E5 mapping + KEEP lists
- [apps_rg_canonical_runtime_boundary.md](apps_rg_canonical_runtime_boundary.md) — product vs non-product paths
- [env_ownership_boundary.md](env_ownership_boundary.md) — model + signal env boundaries

**Wave status:** W0 PASS · W1 PASS · no runtime or agentic_core/apps_rg code edits

**Canonical plan (disk):** [.cursor/plans/l2-rationalization-waves-c8e4f1.md](../../.cursor/plans/l2-rationalization-waves-c8e4f1.md)  
**Notion Plans row:** `l2-rationalization-waves-c8e4f1` · page `36527693-f55c-81d1-928c-c387dfcdafc5` · Status **In Progress**

---

## 1. What does L2 contain today?

`agentic_core/L2_execution/` (~273 Python modules). Subtrees:

| Subtree | Role |
|---------|------|
| `enforcement/` | SovereignLLMGateway, E2 validate-before-execute, provider substitution prohibition, read/write gateways |
| `healers/` | healing_router, healing_cascade_registry, Gemini/Qwen gateways, local_healer, confidence_aware_executor |
| `reasoning/` | StructuredEngineAgent, validation_orchestrator, ToolsmithAgent, tool/execute executors |
| `orchestration/` | **l2_phase_pipeline** — E1→E5 receipts |
| `providers/`, `types/`, `utils/` | Provider surfaces, vLLM contracts, tool chains, l2_agent_wrappers |
| `*_l2_binding.py` | Temporary app shims (apps_rg → apps-owned binding) |

### L2.2 / L2.3 / L2.4 vs v3 E-phases

User-facing **L2.2 validate / L2.3 execute / L2.4 heal** maps to **E2 / E3 / E4** in [l2_phase_pipeline.py](../../agentic_core/L2_execution/orchestration/l2_phase_pipeline.py):

| User label | Pipeline phase | Receipt type |
|------------|----------------|--------------|
| L2.2 validate | E2 VALID | `ValidationReceipt` |
| L2.3 execute | E3 EXEC | `AttemptReceipt` |
| L2.4 heal | E4 HEAL | `HealReceipt` |

**Caveat (MEDIUM confidence):** [l2_execution_contract.py](../../agentic_core/L2_execution/types/l2_execution_contract.py) `CanonicalAgentRole` enum labels may still use older L2.x numbering where EXECUTE was called L2.2 — treat pipeline docstrings as runtime SSOT for new wiring.

**Architecture invariants (HIGH static):**

- Pipeline never writes L4/UWG ([l2_phase_pipeline.py](../../agentic_core/L2_execution/orchestration/l2_phase_pipeline.py) docstring).
- `TwoPhaseHealerFn`: `resolve()` pure, `execute()` only after resolution-consistency gate (INV-RC-5).

---

## 2. Useful agentic_core L2 components (KEEP_CORE)

| Component | Path | Confidence |
|-----------|------|------------|
| Phase orchestrator | `orchestration/l2_phase_pipeline.py` | HIGH |
| Healing router | `healers/healing_router.py` | HIGH |
| Cascade + heal model tiers | `healers/healing_cascade_registry.py` | HIGH |
| LLM gateway | `enforcement/SovereignLLMGateway.py` | HIGH |
| Bounded executor | `bounded_executor.py`, `l2_package_driven_executor.py` | HIGH |
| Authority validation | `reasoning/authority_validator.py` | HIGH |
| Gemini heal provision | `healers/gemini_gateway_provisioner.py` | HIGH |
| vLLM health (apps_rg consumer) | `healers/vllm_health_probe.py` | HIGH |
| Model registry SSOT | `L0_routing/config/model_registry.py` | HIGH |
| Google env names | `config/google_ai_env.py` | HIGH |

**L2.2 validators (E2 chokepoints):** `authority_validator`, `prompt_envelope_validator`, `enforcement/boundary_validator`, `healers/healing_evidence_validator`, `capability/registry_validator`, `enforcement/e2_agent_gate`, `enforcement/guardrail_gate` (via write_gateway), `reasoning/validation_orchestrator` (orchestration overlap — **NEEDS_DECISION**).

**L2.3 executors (E3):** `bounded_executor`, `l2_package_driven_executor`, `reasoning/tool_intent_executor`, `reasoning/execute_command_executor`, `healers/confidence_aware_executor`, user-supplied `executor_fn` in pipeline.

**L2.4 healers (E4):** `healing_router`, `local_healer`, `gemini_gateway_provisioner`, `qwen_strict_diagnostic`, `qwen_judge_gateway` (judge-shaped; audit overlap with apps_rg judges — **NEEDS_DECISION**).

---

## 3. Obsolete, duplicated, unsafe, or superseded (core)

| Path | Issue | Classification | Confidence |
|------|-------|----------------|------------|
| `apps_rg_l2_binding.py` | Re-export shim; canonical in apps_rg | **RETIRE** | HIGH |
| `_agentic_core_smoke.py` | Smoke only | **QUARANTINE_UNTIL_REVIEW** | MEDIUM |
| `reasoning/examples/code_quality_*` | Exemplars, not production | **QUARANTINE_UNTIL_REVIEW** | HIGH |
| `validation_orchestrator` vs `l2_phase_pipeline` E2 | Duplicate validation surfaces | **NEEDS_DECISION** | MEDIUM |
| `confidence_aware_executor` vs `healing_router` | Overlapping heal tier selection | **UPDATE** (consolidate docs first) | MEDIUM |

**Unsafe if misused (keep but gate):** healing paths that could run on authority/ACL failures — requires W5 negative tests (not yet runtime-proven).

---

## 4. Canonical apps_rg paths (KEEP_APPS_RG)

| Path | Role | Confidence |
|------|------|------------|
| `python -m apps_rg` | Integrated R4 CLI | HIGH |
| `runtime/orchestration/canonical_dispatch.py` | Section + CLI primitives | HIGH |
| `l2_recipe/r4_generation_route.py` | Default `modular_section_lanes` | HIGH |
| `runtime/bindings/l2_binding.py` | `l2_execute_apps_rg` | HIGH |
| `runtime/sections/*_lane.py` | Qwen/vLLM per section | HIGH |
| `runtime/providers/qwen_vllm_provider.py` | Product generation | HIGH |
| `runtime/judges/*` + `section_judge_profile.py` | X1D judges | HIGH |
| `runtime/validators/*` | X2 gates | HIGH |
| `runtime/exit/*` | X3 helpers | HIGH |

**Runtime proof (HIGH):** Receipts under `artifacts/apps_rg/runtime_proofs/` (e.g. final_resume_assembly) show provider_request/response and x3 disposition when live paths used.

---

## 5. Non-product apps_rg paths

| Path | Reason | Classification |
|------|--------|----------------|
| `runtime/dry_run/` | Demo/mock judges; hardcoded models | **QUARANTINE_UNTIL_REVIEW** |
| `reasoning/Rg*.py` | Early-learning agents; section runtime supersedes product path | **SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME** |
| `runtime/orchestrate_full_resume.py` | Offline modular orchestrator (distinct entry) | **QUARANTINE_UNTIL_REVIEW** |
| `runtime/dispatch/*` calling `exit_deprecated_runtime_cli` | Legacy per-section CLIs | **RETIRE** (after W8) |
| `APPS_RG_L2_PROVIDER_MODE=stub_only` | CI determinism only | Non-product proof |
| `--mock-judges` without waiver | Plumbing only | Non-product proof |

**Note:** `RgResumeOrchestrator` still has unit tests and `apps_shared/adapters/rg_orchestrator_facade.py` — **not proven dead** (LOW for deletion).

---

## 6–9. Model and signal ownership (summary)

Full tables: [model_env_ownership_plan.md](model_env_ownership_plan.md), [signal_quality_ownership_plan.md](signal_quality_ownership_plan.md).

| Var family | Owner | Must NOT use for |
|------------|-------|------------------|
| `GOOGLE_AI_MODEL`, `GOOGLE_AI_PRO_MODEL`, `OPENAI_MODEL`, `HEALING_GOOGLE_AI_PRO_MODEL` | agentic_core spine / healing / consensus | apps_rg section body generation |
| `APPS_RG_*_JUDGE_MODEL_*` | apps_rg proof judges | — |
| `QWEN_*`, `VLLM_*` | apps_rg generation (+ registry for local tier) | — |
| `SIGNAL_*` | agentic_core signal_quality_config | apps_rg generation, judges, heal routing |

**Stubs mimicking SSOT (HIGH):** [subatomic_hop_util.py](../../apps_shared/utils/subatomic_hop_util.py), [engine_type_types.py](../../apps_shared/types/engine_type_types.py).

---

## 10–11. Waves and combine rules

See [l2_rationalization_full_wave_plan.md](l2_rationalization_full_wave_plan.md) — **12 waves (W0–W11)**.

- **Safe to combine:** W0 alone; W2+W3; W7+W8
- **Must stay separate:** W4 vs W2; W5/W6/W10 before W11

---

## ADG hotspots (L2_execution centrality)

| Module | fan_in | betweenness_approx |
|--------|--------|-------------------|
| `types/l2_v3_receipts.py` | 143 | 0.09 |
| `utils/write_gateway.py` | 90 | 0.82 |
| `types/l2_v4_contracts.py` | 88 | 0.11 |
| `reasoning/compiled_artifact.py` | 79 | 0.13 |

---

## W0 / W1 execution log

| Step | Result |
|------|--------|
| `python docs/reports/agent_inventory/_generate_l2_inventory.py` | exit 0 — JSON refreshed |
| `python -m compileall agentic_core apps_rg -q` | exit 0 |
| `pytest tests/unit/agentic_core/L2_execution/orchestration/ -q` | 8 passed (1 file: `test_l2_sequencer_adapter.py`) |
| Live `python -m apps_rg` proof | **not run** (out of scope) |

**Inventory counts (git grep):** 633 agent/healer/judge patterns · 1946 model/signal env patterns (includes tests/docs).

---

## Explicit non-claims

- No runtime proof that all healing respects same-authority (planned W5).
- No deprecation, deletion, or code behavior change in W0/W1.
- Grep/git-grep counts include tests, docs, and plans — not every hit is production.
- Static inventory was not treated as runtime reachability proof.
- Mock/smoke/demo/offline stub paths were not treated as product proof.
