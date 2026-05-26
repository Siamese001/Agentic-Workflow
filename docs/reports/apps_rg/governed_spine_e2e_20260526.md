# Governed spine E2E proof — 2026-05-26

Brown & Brown SVP targeting · live Qwen/vLLM · WSL runtime.

## Summary

| Run | Entry | Spine verifier | Product outcome |
|-----|--------|----------------|-----------------|
| **Section** `headline` | `python -m apps_rg --section headline` | **PASS** | **X3_ALLOW**, REAL_LLM, exit 0 |
| **Whole** `apps_rg` | `python -m apps_rg` (integrated R4) | **PARTIAL** (1/7 lanes) | exit 1, `L2_EXECUTION_FAILED` |

## Section lane — headline (PASS)

**Artifact dir:** [headline_20260526_194440](artifacts/apps_rg/runtime_proofs/headline/real/headline_20260526_194440)

**Verifier:** `python ops_scripts/apps_rg/verify_governed_spine_e2e.py --section-dir …`

| Check | Result |
|-------|--------|
| U0 `validated_request.json` + runtime package ingested | PASS |
| L1 / L0 contracts on disk | PASS |
| `grounding_required=true` | PASS |
| No `fixture_dev_only_bypass` | PASS |
| No `raw_proof_pool_direct_to_pa` | PASS |
| C0 evidence room + `section_spine_c0_retrieve_receipt` (dense) | PASS |
| Exit spine chain: U0→L1→L0→`c0_retrieve_apps_rg`→PA→L2→Exit | PASS |
| L6 shadow offline only (`l6_shadow_eval_package.json`) | PASS (not runtime ALLOW) |
| `is_second_spine=false` on front spine receipt | PASS |

**Output:** 11-word headline, all X2/X1D pass, `PROOF_ELIGIBLE`.

## Whole apps_rg — integrated R4 (PARTIAL)

**Run dir:** [full_resume_1bffb730f966](artifacts/apps_rg/runtime_proofs/full_resume_1bffb730f966)

**CLI:** `ops_scripts/apps_rg/run_integrated_e2e_wsl.sh` (~6 min)

### What entered the governed spine

- Producer: `agentic_core.runtime.entrypoints.integrated_single_action_spine_run`
- Cache preflight completed; generation spine invocation allowed
- Artifacts: `agentic_core_spine_proof.json`, `agentic_core_how_trace.json`, `r4_run_manifest.json`, `runtime_exhaust_bundle.json`

### Envelope accounting (known gap — not lane shadow pipeline)

At **integrated envelope** only:

- [c0_bypass_receipt.json](artifacts/apps_rg/runtime_proofs/full_resume_1bffb730f966/c0_bypass_receipt.json) — `BYPASS_PRELOADED_CONTEXT`
- [l3_bypass_receipt.json](artifacts/apps_rg/runtime_proofs/full_resume_1bffb730f966/l3_bypass_receipt.json)

Per-lane work still runs U0→L1→L0→C0 retrieve→PA→L2→Exit under `lanes/<section>/` (see executive_summary below).

### Lane completion

| Section | Status |
|---------|--------|
| executive_summary | X3_ALLOW, REAL_LLM |
| headline, unify_*, ibm_*, competencies | **NOT_RUN** (`PHASE1_NO_RUN_DIR`) |

**Root cause (run):** `r4_run_manifest.json` → `l2_fault` / modular R4 phase-1 lane dirs missing for 6 lanes.

### executive_summary lane inside integrated run (PASS)

**Dir:** [lanes/executive_summary](artifacts/apps_rg/runtime_proofs/full_resume_1bffb730f966/lanes/executive_summary)

Section governed-spine verifier: **PASS** (same binding chain as standalone section CLI).

`apps_research_call_required=false` on this lane (briefing supplied at U0).

## Static single-spine scan (pre-existing findings)

`python ops_scripts/ci/check_apps_rg_single_spine.py` → **2 ERROR** (legacy `_run_*_lane_from_cli` / remediation bridge). Not introduced by this E2E run.

## Commands

```bash
# Section
ops_scripts/apps_rg/run_headline_wsl.sh
python ops_scripts/apps_rg/verify_governed_spine_e2e.py \
  --section-dir artifacts/apps_rg/runtime_proofs/headline/real/<run_id>

# Whole (WSL, live provider)
ops_scripts/apps_rg/run_integrated_e2e_wsl.sh
python ops_scripts/apps_rg/verify_governed_spine_e2e.py \
  --section-dir artifacts/apps_rg/runtime_proofs/full_resume_<id>/lanes/executive_summary
```

## Follow-ups

1. Fix modular R4 `PHASE1_NO_RUN_DIR` so all seven lanes run under integrated `python -m apps_rg`.
2. Rectify integrated envelope `C0`/`L3` bypass receipts vs lane-level real C0 (c0-policy rectification plan).
3. Extend `briefing_u0_signals` — L1 now reads `user_constraints.briefing_text` (standalone headline run predates fix).
