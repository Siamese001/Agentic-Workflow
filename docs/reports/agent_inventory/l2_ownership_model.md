# L2 ownership model (W1 — zero behavior change)

**Wave:** W1 documentation only  
**SSOT pipeline:** [l2_phase_pipeline.py](../../../agentic_core/L2_execution/orchestration/l2_phase_pipeline.py)  
**Related:** [apps_rg_canonical_runtime_boundary.md](apps_rg_canonical_runtime_boundary.md), [env_ownership_boundary.md](env_ownership_boundary.md)

This document maps early-learning labels (L2.2 / L2.3 / L2.4) to the current v3 E-phase pipeline. It does **not** change runtime code or enums.

---

## 1. L2_LAYER_MAPPING

| Legacy / user label | v3 phase | Receipt (sealed) | Responsibility |
|---------------------|----------|------------------|----------------|
| **L2.1 prep** (implicit in older docs) | **E1 PREP** | `PrepReceipt` | Freeze `DeterminismBundle` (blueprint_hash, policy_hash); establish execution room |
| **L2.2 validators** | **E2 VALID** | `ValidationReceipt` | Validate frozen work order **before** execution; PASS or sealed FAIL |
| **L2.3 executors** | **E3 EXEC** | `AttemptReceipt` | Execute **exactly one** bounded packet per attempt |
| **L2.4 healers / recovery** | **E4 HEAL** | `HealReceipt` | **Same-authority** local repair only; optional `TwoPhaseHealerFn` (resolve → gate → execute) |
| **L2.5 seal / handoff** (implicit) | **E5 SEAL** | `DispatchReceipt` | Terminal handoff; `has_commit_payload=False` at L2 — Exit/UWG decide durable writes |

### E1 prep / freeze (HIGH static)

- Freezes snapshot authority; downstream phases must `assert_snapshot_match`.
- L2 does **not** create authority — it receives it from upstream routing/package handoff.

### E2 validation = L2.2 validators (HIGH static)

Representative **agentic_core** modules (adapter callables into pipeline):

- `reasoning/authority_validator.py`
- `prompt_envelope_validator.py`
- `enforcement/boundary_validator.py`, `e2_agent_gate.py`, guardrail chokepoints via `write_gateway`
- `healers/healing_evidence_validator.py`
- `reasoning/validation_orchestrator.py` — **MEDIUM**: parallel orchestration surface; **NEEDS_DECISION** vs single E2 entry (W9)

**Must not:** approve execution on missing authority, ACL block, stale policy/registry, or provider substitution.

### E3 execution = L2.3 executors (HIGH static)

- `bounded_executor.py`, `l2_package_driven_executor.py`
- `reasoning/tool_intent_executor.py`, `reasoning/execute_command_executor.py`
- User-supplied `executor_fn` in `l2_phase_pipeline`
- `ExecutorResult.proposed_state_diff` is **inert** at L2 — not an L4 commit

### E4 heal = L2.4 same-authority repair (HIGH static)

- `healers/healing_router.py`, `healers/local_healer.py`, `healers/gemini_gateway_provisioner.py`
- `healers/healing_cascade_registry.py` — tier model IDs (`HEALING_GOOGLE_AI_PRO_MODEL` override)
- `TwoPhaseHealerFn`: structural INV-RC-5 — no model/tool I/O on resolution mismatch

**Must not heal (architecture law — static docs):** missing authority, ACL block, stale policy, stale registry, sandbox gap, HITL need, route mismatch, provider substitution, capability expansion. Runtime enforcement proof: **W5** (not claimed here).

### E5 seal (HIGH static)

- `DispatchReceipt` — terminal L2 handoff to Exit path
- Pipeline explicitly never writes L4/UWG

### Legacy enum caveat (MEDIUM)

`agentic_core/L2_execution/types/l2_execution_contract.py` `CanonicalAgentRole` may use older L2.x numbering. For **new wiring**, treat [l2_phase_pipeline.py](../../../agentic_core/L2_execution/orchestration/l2_phase_pipeline.py) docstrings and receipts as SSOT.

---

## 2. KEEP_IN_AGENTIC_CORE

Reusable **spine substrate** only — not apps_rg section product logic.

| Concern | Where | Confidence |
|---------|-------|------------|
| Frozen execution room / snapshot binding | E1 `PrepReceipt`, `DeterminismBundle` | HIGH |
| Validation contracts & E2 adapters | `authority_validator`, envelope/boundary validators, E2 gates | HIGH |
| Bounded execution packet handling | `bounded_executor`, `l2_package_driven_executor`, E3 `AttemptReceipt` | HIGH |
| Governed provider / model / tool gateway | `SovereignLLMGateway`, `provider_registry`, substitution prohibition | HIGH |
| Same-authority repair primitives | `healing_router`, cascade registry, `TwoPhaseHealerFn` | HIGH |
| Sealing / phase receipts | `types/l2_v3_receipts.py`, `l2_phase_pipeline` E5 | HIGH |
| Generic eval / consensus (non-apps_rg) | L1 `consensus_validator` + spine model registry | HIGH |
| vLLM health probe (shared infra) | `healers/vllm_health_probe.py` — consumed by apps_rg | HIGH |
| Temporary app shims | `*_l2_binding.py` — **RETIRE_CANDIDATE** `apps_rg_l2_binding` (W6) | HIGH |

**Not in core (leakage if added):** section prompt YAML, SRFS slice rules, apps_rg judge profiles, résumé locked copy.

---

## 3. KEEP_IN_APPS_RG

Section-specific **product runtime** — customizes through U0 package + profiles; uses core gateways where wired.

| Concern | Where | Confidence |
|---------|-------|------------|
| Canonical CLI | `apps_rg/__main__.py` | HIGH |
| Integrated / section dispatch | `runtime/orchestration/canonical_dispatch.py` | HIGH |
| Default generation mode | `l2_recipe/r4_generation_route.py` → `modular_section_lanes` | HIGH |
| Section lanes (generation) | `runtime/sections/*_lane.py` | HIGH |
| Qwen/vLLM generation | `runtime/providers/qwen_vllm_provider.py` | HIGH |
| Prompt assembly / contracts | `prompt_assembly/`, `runtime/bindings/section_prompt_adapter.py` | HIGH |
| SRFS / proof-pool enforcement | `runtime/validators/proof_pool_*.py`, fact inventory | HIGH |
| X2 section gates | `runtime/validators/*_x2.py` | HIGH |
| X1D judges | `runtime/judges/*`, `section_judge_profile.py` | HIGH |
| X3 disposition artifacts | `runtime/exit/*` | HIGH |
| Section receipts / proof layout | `runtime/runtime_proof_layout.py`, `artifacts/apps_rg/runtime_proofs/` | HIGH (runtime receipts when live run exists) |
| L6 shadow (offline) | `runtime/shadow/*` — `offline_only` | HIGH static |
| Canonical L2 execute binding | `runtime/bindings/l2_binding.py` | HIGH |

---

## 4. NON_PRODUCT_OR_NEEDS_DECISION

**No deletion in W0/W1.** Classifications are planning labels only.

| Path / pattern | Classification | Confidence | Notes |
|----------------|----------------|------------|-------|
| `agentic_core/L2_execution/_agentic_core_smoke.py` | QUARANTINE_CANDIDATE | MEDIUM | Smoke only |
| `agentic_core/L2_execution/apps_rg_l2_binding.py` | RETIRE_CANDIDATE | HIGH | Shim; canonical `apps_rg/runtime/bindings/l2_binding.py` |
| `agentic_core/L2_execution/reasoning/examples/code_quality_*` | QUARANTINE_CANDIDATE | HIGH | Exemplars |
| `apps_rg/runtime/dry_run/` | QUARANTINE_CANDIDATE | HIGH | Demo / non-product proof |
| `apps_rg/runtime/internal/lane_batch.py` | QUARANTINE_CANDIDATE | HIGH | Offline orchestrator; distinct entry |
| `apps_rg/reasoning/Rg*.py` | TEST_SUPPORT_ONLY / NEEDS_DECISION | HIGH static | Superseded for product; **tests + facade remain** |
| `apps_rg/runtime/dispatch/*` → `exit_deprecated_runtime_cli` | RETIRE_CANDIDATE | MEDIUM | Legacy per-section CLIs |
| `APPS_RG_L2_PROVIDER_MODE=stub_only` | QUARANTINE_CANDIDATE | HIGH | CI determinism |
| `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB` | QUARANTINE_CANDIDATE | HIGH | Offline stub |
| `--mock-judges` (no waiver) | QUARANTINE_CANDIDATE | HIGH | Plumbing only |
| `APPS_RG_R4_GENERATION_MODE=legacy_full_resume` | NEEDS_DECISION | HIGH | Explicit rollback path |
| `validation_orchestrator` vs pipeline E2 | NEEDS_DECISION | MEDIUM | Duplication |
| `apps_shared` signal stubs | NEEDS_DECISION | HIGH | See env_ownership_boundary |

---

## 5. MODEL_ENV_BOUNDARY

See [env_ownership_boundary.md](env_ownership_boundary.md).

- `OPENAI_MODEL`, `GOOGLE_AI_MODEL`, `GOOGLE_AI_PRO_MODEL` → spine / shared-agent / healing / consensus — **not** apps_rg section body generation.
- Qwen/vLLM env vars → apps_rg generation.
- `APPS_RG_*_JUDGE_MODEL_*` → apps_rg proof judges.
- `HEALING_GOOGLE_AI_PRO_MODEL` → L2 healing cascade only (not judges).
- `SIGNAL_*` → signal-quality labeling only (not generation, judges, heal-tier routing).

---

## 6. PROOF_BOUNDARY

| Evidence type | What it proves | W0/W1 use |
|---------------|---------------|-----------|
| **Static grep** | Symbol/env string presence | Inventory counts only — **not** reachability |
| **Import / call graph (ADG)** | Structural fan-in/out | Hotspot hints — **not** runtime path |
| **Unit / contract tests** | Wired behavior in test harness | Orchestration tests run; not full product proof |
| **Runtime receipts** | Live/stubbed run artifacts under `artifacts/apps_rg/runtime_proofs/` | Cited as **examples** only; **no live run in W0/W1** |
| **Live product proof** | `python -m apps_rg` + real Qwen + real judges | **Out of scope** for W0/W1 |

**Rule:** Mock / smoke / demo / offline stub paths are **never** product proof (see [apps_rg_canonical_runtime_boundary.md](apps_rg_canonical_runtime_boundary.md)).

---

## Explicit non-claims (W1)

- No code behavior changed; no files deleted; no deprecation markers added.
- Same-authority healing not runtime-proven in this wave.
- `RgResumeOrchestrator` not declared dead.
