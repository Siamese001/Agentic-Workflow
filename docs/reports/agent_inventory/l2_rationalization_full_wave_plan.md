# L2 rationalization — full wave plan

**Recommended waves:** 12 (W0–W11)  
**Machine-readable:** [l2_rationalization_full_wave_plan.json](l2_rationalization_full_wave_plan.json)  
**Canonical execution plan:** [.cursor/plans/l2-rationalization-waves-c8e4f1.md](../../.cursor/plans/l2-rationalization-waves-c8e4f1.md) · Notion `l2-rationalization-waves-c8e4f1`

Planning-only — no deprecation, deletion, or behavior change in this pass. **W0–W1 complete.**

---

## Wave summary

| Wave | Objective | Depends on |
|------|-----------|------------|
| **W0** | Freeze inventory SSOT + ADG provenance | — |
| **W1** | L2.2/2.3/2.4 ↔ E2/E3/E4 vocabulary alignment (docs) | W0 |
| **W2** | Spine model env guards on apps_rg generation | W1 |
| **W3** | apps_rg judge env isolation + receipt `model_source` | W2 |
| **W4** | Signal-quality SSOT wire-up or stub quarantine | W0 |
| **W5** | Same-authority healing enforcement audit | W1 |
| **W6** | Retire `apps_rg_l2_binding` shim | W2, W3 |
| **W7** | Quarantine non-product apps_rg paths | W0 |
| **W8** | Consolidate dispatch vs section lane surfaces | W7 |
| **W9** | L2 E2 validator/gateway consolidation | W1, W5 |
| **W10** | Exit/UWG/L4/L6 no-bypass contract tests | W5 |
| **W11** | Gated archive/delete | W6–W10 |

---

## W0: Freeze inventory SSOT and ADG provenance

- **Why:** Baseline evidence before quarantine labels change imports.
- **Files:** `docs/reports/agent_inventory/*`, `artifacts/adg/adg_indexed_*.sqlite`
- **Tests:** `python docs/reports/agent_inventory/_generate_l2_inventory.py`
- **Commands:** `python -m compileall agentic_core apps_rg -q`; `adg_health`
- **Acceptance:** JSON cites snapshot id; compileall exit 0
- **Rollback:** Delete new report files only
- **PASS:** Artifacts present + compileall 0 | **PARTIAL:** JSON without compileall | **FAIL:** compileall non-zero

---

## W1: Document L2 subphase vocabulary

- **Why:** Prevents engineers wiring healers to wrong phase hooks.
- **Files:** `agentic_core/L2_execution/types/l2_execution_contract.py` (comments only), `docs/architecture/` ADR or table, `l2_phase_pipeline.py` cross-link
- **Tests:** `pytest tests/unit/agentic_core/L2_execution/orchestration/ -q` (if exists)
- **Acceptance:** Single mapping table; **no enum behavior change**
- **Rollback:** Revert doc-only commit
- **Risks:** Accidental enum edit changes runtime

---

## W2: Model env ownership guards (generation)

- **Why:** Stops `OPENAI_MODEL` / `GOOGLE_AI_*` bleed into Qwen product path.
- **Files:** `apps_rg/runtime/providers/qwen_vllm_provider.py`, `apps_rg/runtime/sections/*_lane.py`, `.env.example`, new `tests/_apps_contract/test_apps_rg_generation_model_env_isolation.py`
- **Tests:** `pytest tests/_apps_contract/test_apps_rg_generation_entrypoints.py tests/unit/apps_rg/test_section_judge_policy.py -q`
- **Acceptance:** Import/static guard fails if section lane imports `GEMINI_FLASH_MODEL_ID` for generation
- **Rollback:** Revert guard test commit
- **Risks:** False positives on shared utilities

---

## W3: apps_rg judge env isolation

- **Why:** `APPS_RG_*_JUDGE_MODEL_*` must be sole proof-judge source per [X1D_PROVIDER_CONFIG.md](../../apps_rg/runtime/judges/X1D_PROVIDER_CONFIG.md).
- **Files:** `apps_rg/runtime/judges/section_judge_profile.py`, `executive_summary_x1d.py`, judge receipts
- **Tests:** `pytest tests/unit/apps_rg/test_section_judge_policy.py -q`
- **Acceptance:** When `APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD` set, resolution does not read `GOOGLE_AI_MODEL`; receipts include `resolved_model_source`
- **Rollback:** Revert profile changes
- **Risks:** Live judge BLOCKED if env incomplete

---

## W4: Signal-quality SSOT or quarantine

- **Why:** `apps_shared` stubs mimic `signal_enhancer` — not spine SSOT.
- **Files:** `agentic_core/runtime/config/signal_quality_config.py`, `apps_shared/utils/subatomic_hop_util.py`, `apps_shared/types/engine_type_types.py`
- **Tests:** `pytest tests/unit/agentic_core/runtime/config/test_signal_quality_config.py -q`
- **Options (NEEDS_DECISION):** (1) wire imports to `get_signal_enhancer`, (2) quarantine stubs + ADR, (3) delete after migration (W11)
- **Acceptance:** Decision recorded; no proof claims using stub scores
- **Rollback:** Keep stubs; document non-product only

---

## W5: Same-authority healing audit

- **Why:** L2.4 must not heal missing authority, ACL block, stale policy/registry, sandbox gap, HITL, route mismatch, provider substitution, capability expansion.
- **Files:** `healers/healing_router.py`, `healers/routing_gates.py`, `enforcement/provider_substitution_prohibition.py`
- **Tests:** `pytest tests/unit/agentic_core/L2_execution/healers/ tests/runtime/test_healing_evidence_validator.py -q`
- **Acceptance:** Negative tests route non-healable signals to Exit/HITL, not Gemini cascade
- **Rollback:** Revert test additions only
- **Risks:** Over-restricting legitimate flash-tier heals

**Same-authority replacement strategy:** Prefer `TwoPhaseHealerFn` migration — `resolve()` binds `L2ResolutionContext` before any model call; extend routing_gates deny-list for non-same-authority reason codes.

---

## W6: Retire apps_rg_l2_binding shim

- **Why:** Canonical `l2_execute_apps_rg` in [apps_rg/runtime/bindings/l2_binding.py](../../apps_rg/runtime/bindings/l2_binding.py).
- **Files:** `agentic_core/L2_execution/apps_rg_l2_binding.py`, consumers (e.g. `tests/_apps_contract/test_ag6_apps_rg_golden_path.py`)
- **Tests:** ADG `adg_edge_fanin` = 0; apps_rg contract suite
- **Acceptance:** Zero importers except timed re-export period
- **Rollback:** Restore shim file

---

## W7: Quarantine non-product apps_rg paths

- **Why:** Reduce mistaken proof from smoke/demo/legacy agents.
- **Files:** `apps_rg/runtime/dry_run/`, `apps_rg/reasoning/Rg*.py`, `deprecated_runtime_cli.py` consumers
- **Tests:** New CI manifest `proof_eligible_entrypoints.yaml` or contract test listing allowed entrypoints
- **Acceptance:** Only `apps_rg.__main__`, `canonical_dispatch`, section lanes, `dispatch_apps_rg_run` marked proof-eligible
- **Rollback:** Remove quarantine markers

---

## W8: Consolidate dispatch vs section lanes

- **Why:** Parallel `runtime/dispatch/*` and `runtime/sections/*` drift (ADG fan-out).
- **Files:** `apps_rg/runtime/sections/`, `apps_rg/runtime/dispatch/`
- **Tests:** `tests/_apps_contract/test_exec_summary_runtime_slice.py`, section pipeline contracts
- **Acceptance:** One SSOT runner per section; dispatch thin wrappers or RETIRE
- **Rollback:** Keep wrappers

---

## W9: L2 E2 validator/gateway consolidation

- **Why:** Overlap among guardrail_gate, e2_agent_gate, validation_orchestrator, authority_validator.
- **Files:** `agentic_core/L2_execution/enforcement/`, `orchestration/l2_phase_pipeline.py`
- **Tests:** `pytest tests/unit/agentic_core/L2_execution/enforcement/ -q`
- **Acceptance:** Documented single E2 entry; no duplicate provider-substitution checks
- **Rollback:** Revert consolidation

---

## W10: Exit/UWG/L4/L6 no-bypass tests

- **Why:** L2 cannot commit; L6 cannot mutate current run.
- **Files:** `tests/_apps_contract/`, `agentic_core/UWG/`, `apps_rg/runtime/bindings/exit_binding.py`
- **Tests:** Static import scanners + runtime tests for direct L4 write from L2
- **Acceptance:** CI fails on bypass patterns documented in AGENTS.md
- **Rollback:** Revert tests

---

## W11: Gated archive/delete

- **Why:** No deletion until fan-in zero and proof manifest excludes path.
- **Files:** `archives/l2_rationalization_<date>/`, [deprecation_quarantine_plan.md](deprecation_quarantine_plan.md)
- **Prerequisites:** W6 fan-in=0; W7 manifest; W10 green; migration receipt in `artifacts/governance/migration_receipts/`
- **Acceptance:** 30d quarantine elapsed + full apps_rg proof run without quarantined paths
- **Rollback:** Restore from archive manifest

**Final gated archive/delete strategy:**

1. QUARANTINE label + `proof_eligible: false` in manifest (W7)
2. ADG fan-in zero (W6/W8)
3. Migration receipt + Author-Gate if RETIRE
4. Move to `archives/` with JSON manifest (not hard delete)
5. Hard delete only after one release cycle with zero imports

---

## Combine vs separate

| Safe to combine | Must stay separate |
|---------------|-------------------|
| W0 (inventory only) | W4 signal vs W2/W3 model env |
| W2 + W3 (model ownership) | W5 healing policy before W11 delete |
| W7 + W8 (apps_rg path hygiene) | W6 shim retirement before W11 delete |
| | W10 boundary tests before W11 delete |

---

## Explicit non-claims

- Wave order does not imply schedule dates or resource allocation.
- PASS criteria per wave require command output in implementation passes — not met by this planning doc alone.
- No claim that all 366 NEEDS_DECISION items are enumerated in JSON (curated subset only).
