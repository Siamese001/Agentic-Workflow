# apps_rg canonical runtime boundary (W1)

**Wave:** W1 documentation only — no runtime edits.

**Recipe SSOT:** [r4_generation_route.py](../../../apps_rg/l2_recipe/r4_generation_route.py)  
**CLI SSOT:** [__main__.py](../../../apps_rg/__main__.py)  
**Dispatch SSOT:** [canonical_dispatch.py](../../../apps_rg/runtime/orchestration/canonical_dispatch.py)

---

## Canonical product path (HIGH static)

```text
python -m apps_rg
  → dispatch_apps_rg_run (agentic_core.runtime.entry.apps_rg_dispatch)   [integrated whole-run]
  OR run_canonical_apps_rg_from_cli_primitives (canonical_dispatch)       [--section lanes]

Default body generation: APPS_RG_R4_GENERATION_MODE unset → modular_section_lanes
  → runtime/sections/<section>_lane.py
  → runtime/providers/qwen_vllm_provider.py (no silent mock fallback)

Judges: runtime/judges/* + section_judge_profile (APPS_RG_*_JUDGE_MODEL_*)
X2:     runtime/validators/*
X3:     runtime/exit/*
Proof:  artifacts/apps_rg/runtime_proofs/ (when run completes)
```

| Stage | Owner layer | Key modules |
|-------|-------------|-------------|
| Ingress / U0 handoff | apps_rg + core generic | `runtime/bindings/c0_binding.py`, domain_contract |
| L2 body execute (legacy rollback only) | apps_rg binding → core executor | `runtime/bindings/l2_binding.py` |
| Section generation (default) | apps_rg | `sections/*_lane`, `qwen_vllm_provider` |
| X1D semantic quality | apps_rg | `judges/*_x1d.py` |
| X2 hard correctness | apps_rg | `validators/*` |
| X3 disposition | Exit profile (app helpers) | `runtime/exit/*` |
| L6 learning | apps_rg shadow only | `runtime/shadow/*` (`offline_only`) |
| Durable write | UWG / L4 (core) | **not** apps_rg direct write |

---

## What is **not** canonical product proof

| Entry / flag | Classification | Confidence |
|--------------|----------------|------------|
| `python -m apps_rg.runtime.internal.lane_batch` | QUARANTINE_CANDIDATE — offline modular orchestrator | HIGH |
| `apps_rg/runtime/dry_run/*` | QUARANTINE_CANDIDATE — demos | HIGH |
| `APPS_RG_L2_PROVIDER_MODE=stub_only` / `APPS_RG_L2_FORCE_STUB=1` | QUARANTINE_CANDIDATE | HIGH |
| `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1` | QUARANTINE_CANDIDATE | HIGH |
| `--mock-judges` without `--allow-test-mock-judges` | QUARANTINE_CANDIDATE | HIGH |
| Legacy `runtime/dispatch/*_dispatch.py` calling `exit_deprecated_runtime_cli` | RETIRE_CANDIDATE | MEDIUM |
| `APPS_RG_R4_GENERATION_MODE=legacy_full_resume` | NEEDS_DECISION — rollback, not default proof path | HIGH |
| `apps_rg/reasoning/RgResumeOrchestrator` etc. | TEST_SUPPORT_ONLY — unit tests + `apps_shared` facade | HIGH |

**Do not delete** any of the above in W0/W1.

---

## Relationship to agentic_core L2

| Concern | apps_rg | agentic_core L2 |
|---------|---------|-----------------|
| Section text generation | **owns** (Qwen/vLLM) | gateway/health only |
| Frozen work order validation | app X2 validators | generic E2 substrate available |
| Healing product defects | section-level retry policies | E4 same-authority heal substrate |
| Model env for body | `VLLM_*`, `QWEN_*` | must not use `GOOGLE_AI_MODEL` for body |
| Model env for judges | `APPS_RG_*_JUDGE_*` | limited fallback documented in X1D config |

Shim: `agentic_core/L2_execution/apps_rg_l2_binding.py` re-exports `apps_rg.runtime.bindings.l2_binding` — **RETIRE_CANDIDATE** (W6), still imported by some contract tests (HIGH static).

---

## Proof receipt checklist (for future live waves)

When claiming live product proof (not done in W0/W1):

- [ ] Entry: `python -m apps_rg` or documented `--section` via `canonical_dispatch`
- [ ] `runtime_generation_status` = `REAL_LLM` (not `MOCKED` / `STUBBED`)
- [ ] `provider_request` / `provider_response` show Qwen/vLLM for section body
- [ ] Judge artifacts show `APPS_RG_*_JUDGE_MODEL_*` as `resolved_model_source` when configured
- [ ] `x3_disposition` present for integrated runs
- [ ] No smoke/demo CLI markers in command line

**Example receipt paths (runtime evidence exists in repo — not re-run here):**

- [final_resume_receipt.json](../../../artifacts/apps_rg/runtime_proofs/final_resume_assembly/final_resume_receipt.json)

---

## PROOF_BOUNDARY (apps_rg-specific)

| Tier | Examples in repo |
|------|------------------|
| Static | Module docstrings, `r4_generation_route` constants |
| Tests | `tests/_apps_contract/test_exec_summary_runtime_slice.py`, section pipeline contracts |
| Runtime receipts | `artifacts/apps_rg/runtime_proofs/**` |
| Live proof | Full CLI + live Qwen + judges — **not executed in W0/W1** |

---

## Explicit non-claims

- No claim that all deprecated dispatch modules are unreachable (grep ≠ dead).
- No live apps_rg run in W0/W1.
- Mock/smoke/demo/offline stub never counted as product proof.
