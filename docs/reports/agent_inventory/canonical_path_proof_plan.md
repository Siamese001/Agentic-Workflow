# Canonical apps_rg path proof plan

Planning-only — defines what counts as product proof vs plumbing.

---

## Product / proof-eligible (HIGH static + runtime receipts)

| Entry | Role | Confidence |
|-------|------|------------|
| `python -m apps_rg` | Integrated R4 CLI — [__main__.py](../../apps_rg/__main__.py) | HIGH |
| `dispatch_apps_rg_run` | Governed spine entry — `agentic_core.runtime.entry.apps_rg_dispatch` | HIGH |
| [canonical_dispatch.py](../../apps_rg/runtime/orchestration/canonical_dispatch.py) | CLI primitives; section-only runs | HIGH |
| [r4_generation_route.py](../../apps_rg/l2_recipe/r4_generation_route.py) | Default `modular_section_lanes` | HIGH |
| [sections/*_lane.py](../../apps_rg/runtime/sections/) | Qwen/vLLM generation per section | HIGH |
| [qwen_vllm_provider.py](../../apps_rg/runtime/providers/qwen_vllm_provider.py) | No silent mock fallback | HIGH |
| [judges/*](../../apps_rg/runtime/judges/) | X1D semantic judges | HIGH |
| [validators/*](../../apps_rg/runtime/validators/) | X2 deterministic gates | HIGH |
| [runtime/exit/*](../../apps_rg/runtime/exit/) | X3 disposition helpers | HIGH |

**Integrated flow (static):** `__main__` → `dispatch_apps_rg_run` OR `canonical_dispatch.run_canonical_apps_rg_from_cli_primitives` for `--section` lanes.

**Runtime proof (HIGH where receipts exist):** `artifacts/apps_rg/runtime_proofs/` — fields: `provider_request`, `provider_response`, `compiled_prompt`, `run_manifest`, `x3_disposition`, judge `resolved_model_source`.

---

## Non-product (do not use for PASS)

| Path | Reason |
|------|--------|
| [orchestrate_full_resume.py](../../apps_rg/runtime/internal/lane_batch.py) | Offline modular orchestrator — distinct from integrated dispatch |
| [runtime/dry_run/](../../apps_rg/runtime/dry_run/) | Demo; hardcoded OpenAI in demo |
| [reasoning/Rg*.py](../../apps_rg/reasoning/) | Early-learning agents |
| `APPS_RG_L2_PROVIDER_MODE=stub_only` | Deterministic stub |
| `--mock-judges` (without test waiver) | Plumbing only per `mock_runtime_proof_policy` |
| Deprecated dispatch CLIs | `exit_deprecated_runtime_cli` |
| [validate_exec_summary_graph_only_generation.py](../../apps_rg/runtime/validators/validate_exec_summary_graph_only_generation.py) | Live-proof validator — not generation entry |

---

## Proof commands (acceptance for implementation waves)

```bash
python -m compileall agentic_core apps_rg -q

python -m apps_rg --target-company "<co>" --target-role "<role>" --jd "<path>"
# Expect artifacts under artifacts/apps_rg/runtime_proofs/

pytest tests/_apps_contract/test_exec_summary_runtime_slice.py -q
pytest tests/_apps_contract/test_apps_rg_generation_entrypoints.py -q
```

Section-only example (contract tests use canonical_dispatch):

```bash
python -m apps_rg --section executive_summary --target-company "<co>" --target-role "<role>" --jd "<path>"
```

---

## Boundary proof (W10)

No-bypass tests must verify:

- L2 / apps_rg runtime does not durable-write L4 except via UWG
- Exit owns X3; L6 shadow does not mutate current run ([unify_bullets_l6.py](../../apps_rg/runtime/shadow/unify_bullets_l6.py) `offline_only: True`)
- Cache admission: [r1b_post_exit_eligibility.py](../../apps_rg/cache/r1b_post_exit_eligibility.py) rejects mock runtime

---

## Receipt fields checklist

- [ ] `provider_request` / `provider_response` show Qwen/vLLM (not Gemini/OpenAI) for section body
- [ ] `runtime_generation_status` = `REAL_LLM` for live proof (not `MOCKED` / `STUBBED`)
- [ ] X1D judge artifacts show `APPS_RG_*_JUDGE_MODEL_*` as source when configured
- [ ] `x3_disposition` present for integrated runs
- [ ] No `smoke_dispatch` / `executive_summary_demo` markers in command line (see graph-only validator)

---

## Explicit non-claims

- Operator live keys availability not verified in this plan.
- All seven modular lanes not individually re-run in this planning pass.
