# Live section proof — readiness audit (Wave 1)

**Wave 1 status: LIVE_READY** for all seven canonical sections via `qwen_vllm` when local vLLM responds at `http://localhost:8000/v1`.

## Provider classification

| Mode | Product proof? | Notes |
|------|----------------|-------|
| `--provider mock` | **No** (MOCK_ONLY) | Plumbing / certification tests only |
| `--provider qwen_vllm` + `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB=1` | **No** (semi-live stub) | `OFFLINE_CONTRACT_STUB` — not REAL_LLM |
| `--provider qwen_vllm`, stub unset, vLLM healthy | **Yes** (LIVE_READY) | `runtime_generation_status=REAL_LLM` |

Default when `--provider` omitted: `qwen_vllm` (`DEV_DEFAULT_QWEN_VLLM`).

## SSOT inputs (verified present)

- Augmented skills graph: `apps_rg/fact_inventory/master_skills_arsenal_ledger.json`
- Candidate fact ledger: `artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json`
- Base resume: `apps_rg/resume/base/amit_ayer_base_resume_v1.json`
- Default briefing: `apps_rg/config/default_targeting_briefing.txt`
- Section prompt templates under `apps_rg/prompt_assembly/templates/`
- X2/X3 validators under `apps_rg/runtime/validators/` and `apps_rg/runtime/exit/`

## vLLM preflight

Probe at `http://localhost:8000/v1` → **healthy** (2026-05-18 session).  
`http://127.0.0.1:8000` without `/v1` returns 404 — use canonical base URL.

## Run matrix

All sections use lane SSOT defaults for target company/role/JD/briefing when CLI flags omitted. Live command template:

```text
python -m apps_rg --section <section> --provider qwen_vllm --allow-non-allow-exit-zero
```

`--allow-non-allow-exit-zero` collects artifacts when X3 is REVIEW/BLOCK; it does **not** change `x3_disposition.json`.

Artifacts land under `artifacts/apps_rg/runtime_proofs/<section>/real/<run_id>/` with `latest_real_run.json` pointer.

Machine-readable matrix: `apps_rg_live_section_proof_readiness.json`.
