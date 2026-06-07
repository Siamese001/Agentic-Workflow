# apps-rg-cross-section-mock-judge-policy

**Slug:** `apps-rg-cross-section-mock-judge-policy`  
**Goal:** Executive-summary-grade mock-judge blocking + proof-bundle semantics across all seven generated lanes.

## Audit snapshot (pre-patch classifications)

| File / hit surface | Classification | Action |
|---|---|---|
| `apps_rg/runtime/sections/executive_summary_lane_api.py` — `--mock-judges`, exit 14, proof bundle | SECTION_RUNTIME_CLI | Reference preserved; delegate bundle to shared helper |
| `apps_rg/runtime/dispatch/*_dispatch.py` (non-exec) — `--mock-judges`, `judge_mode` mocked without hatch guard | SECTION_RUNTIME_CLI | **MUST_PATCH:** gate before run + hatch CLI + shared bundle |
| `apps_rg/runtime/dispatch/mock_runtime_proof_policy.py` | JUDGE_PROVIDER / policy SSOT | **MUST_PATCH:** `compute_lane_proof_bundle`, stderr helper reuse |
| `apps_rg/runtime/internal/lane_batch.py` — forward mock judges | ORCHESTRATOR_FORWARDING | **MUST_PATCH:** require `--allow-test-mock-judges`; forward hatch |
| `apps_rg/l2_recipe/modular_lane_adapter.py` — mock argv | MODULAR_LANE_FORWARDING | **MUST_PATCH:** append hatch |
| `apps_rg/l2_recipe/modular_resume_generation.py` — exec-only hatch | MODULAR_LANE_FORWARDING | **MUST_PATCH:** remove special case (adapter fixed) |
| `apps_rg/runtime/runtime_proof_layout.py` — `latest_successful_real_run`, `proof_eligible` | SAFE_TO_LEAVE | Already skips pointer when `proof_eligible=False` |
| `apps_rg/runtime/judges/*_x1d.py` — MOCKED plumbing rows | JUDGE_PROVIDER | SAFE_TO_LEAVE (invoked only via hatch / blocked_if_unavailable) |
| `apps_rg/runtime/dry_run/executive_summary_demo.py`, artifacts | DOCS_ONLY / HISTORICAL_ARTIFACT | Out of scope |
| Contract tests under `tests/_apps_contract/` | CONTRACT_TEST | **MUST_PATCH:** cross-lane mock judge matrix |

## Implementation notes

- Shared proof eligibility: `compute_lane_proof_bundle` in `mock_runtime_proof_policy.py` (matches executive summary rules).
- Exit **14** + stderr pattern unified via `emit_mock_judges_blocked_stderr` / `MOCK_JUDGES_REJECT_EXIT_CODE`.
- `blocked_if_unavailable` judge modes retain **no silent mock fallback** when hatch is off.

## Verification

- `python -m pytest tests/_apps_contract/test_apps_rg_section_mock_provider_policy.py -q -o addopts=""`
- `python -m pytest tests/_apps_contract/test_exec_summary_runtime_slice.py -q -o addopts=""`
- `python -m pytest tests/_apps_contract/test_apps_rg_e2e_resume_orchestrator.py -q -o addopts=""`
- `git diff HEAD -- agentic_core` (expect empty)
