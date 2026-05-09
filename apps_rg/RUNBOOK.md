# RUNBOOK — apps_rg

> **When to use this:** a generated résumé is wrong, low-quality, fails ATS coverage, or contains fabricated claims.
> **Companion docs:** `SLO.md` · `SVP_ENGINEERING_REVIEW.md` · `README.md`
> **Owner:** see `CODEOWNERS`

## On-Call Decision Tree

```
A résumé generation run is misbehaving
├── Did the gate flag fabrication (claim with no profile evidence)?
│   ├── YES → §1 Fabrication Violation (CRITICAL)
│   └── NO  → continue
├── Did ATS coverage fall below the 80% floor?
│   ├── YES → §2 ATS Coverage Failure
│   └── NO  → continue
├── Did the anti-overfitting check flag low evidence density?
│   ├── YES → §3 Anti-Overfitting Flag
│   └── NO  → continue
├── Is generation stalled > 5min for a single résumé?
│   ├── YES → §4 Generation Stall
│   └── NO  → §5 Generic
```

## §1 Fabrication Violation (CRITICAL)

**Symptom:** `gate_violations=["FABRICATION:<claim>"]` — the rendered résumé contains a claim that does not trace to any entry in the candidate profile.

**This is the most critical failure type.** A fabricated claim represents the candidate falsely.

**Triage:**
1. **DO NOT submit the résumé.** The gate already blocked render but verify nothing leaked downstream.
2. Inspect the offending claim: `python -m apps_rg --inspect --run-id=<id> --filter=fabrication`.
3. Identify whether the LLM hallucinated (engine bug) or the profile is missing the supporting entry (profile-completeness bug).

**Mitigation:**
- If engine bug → freeze the assembly engine; root-cause the prompt; add evidence-binding to the failing template.
- If profile bug → return to candidate to complete the profile entry; do not synthesize.
- **Never relax the no-fabrication gate.**

## §2 ATS Coverage Failure (<80%)

**Symptom:** `gate_violations=["ATS_COVERAGE_LOW:<pct>"]`.

**Triage:**
1. Run `python -m apps_rg --inspect --run-id=<id> --filter=ats` to surface missing keywords.
2. Determine whether the candidate profile genuinely lacks experience for the target role (real gap) or the engine failed to surface relevant experience (engine bug).

**Mitigation:**
- If genuine gap → flag the role-fit mismatch to the user; lower target-role tier or expand profile.
- If engine bug → re-run with `--rerender-section experience` and bisect the assembly engine.

## §3 Anti-Overfitting Flag (low evidence density)

**Symptom:** `gate_violations=["EVIDENCE_DENSITY_LOW"]` — claims-per-position exceeds evidence support.

**Triage:** the engine compressed multiple positions into one inflated entry. Spot-check the evidence-density score per position.

**Mitigation:**
- Re-run with stricter evidence binding.
- If repeated, freeze the achievement-prioritizer engine and root-cause.

## §4 Generation Stall (>5min)

**Symptom:** résumé run exceeds the 5-min hard ceiling.

**Triage:**
1. Check Anthropic / Qwen provider health.
2. Check engine count — résumés invoking >12 specialist engines may legitimately need more time; review hard ceiling for that scope class.
3. Check retrieval cold-start latency on the candidate-profile index.

**Mitigation:**
- Cancel the run.
- For deadline-sensitive work, render a partial résumé with explicit `[INCOMPLETE]` markers.

## §5 Generic Investigation

1. `python -m apps_rg --trace --replay --run-id=<id>`.
2. Bisect against last 24h commits to `apps_rg/engines/`.
3. Check `apps_rg/integrations/anti_overfitting.py` and `ats_coverage.py` for threshold drift.

## Rollback Procedure

apps_rg produces résumés as artifacts. Rollback affects only future generations. Past rendered résumés are **immutable** and retained for audit.

1. `git revert <commit>`.
2. `python -m apps_rg --demo` smoke test.
3. Re-arm fabrication + ATS-coverage gates.

## Top-3 Failure Modes

1. **Fabrication violation** → §1 (CRITICAL — candidate-trust)
2. **ATS coverage below floor** → §2 (job-application impact)
3. **Generation stall near deadline** → §4 (operational reality)

## Key Files

- `__main__.py` — transport shim; delegates to `agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run`
- `l2_recipe/steps.py` — L2 step adapters with `_PAGuard` (no model call without `PA_L2_HANDOFF_READY` artifact)
- `prompt_assembly/compiler.py` — apps_rg local PA compiler (governed L2 templates)
- `utils/anthropic_rag_entrypoint.py` — legacy PA bridge consuming `PromptEnvelope` (narrative / R3 surface)
- `integrations/llm_client.py` — sanctioned `infrastructure.sdks_mcps` shim (active provider surface)
- `engines/achievement_prioritizer_engine.py` — claim-ranking
- `engines/ats_coverage_engine.py` — keyword coverage check
- `integrations/anti_overfitting.py` — evidence-density gate
- `integrations/ats_coverage.py` — coverage gate
- `bootstrap_runtime.py` — ADG bootstrap

> **Dormant scaffold (not the active provider surface):** `enforcement/HardenedanthropicexecutorStrategy.py`, `reasoning/HardenedopenaiexecutorStrategy.py`, `validators/enforcement/HardenedanthropicexecutorStrategy.py`, `engines/hardened_gemini_executor.py` have **zero module fan-in** per W1 ADG audit (`docs/reports/apps_rg/spine_boundary_findings_20260509_055000.md` §4B). Do not investigate provider issues here — investigate in `integrations/llm_client.py` and the canonical L2 step adapters above. Cleanup tracked separately as `NEXT_STEP:` in plan `apps-rg-spine-hardening-7e3b9c`.

## Escalation Contacts

- **Primary on-call:** see `CODEOWNERS`
- **Provider hardening owner:** see `apps_rg/enforcement/CODEOWNERS`
- **L0 routing owner:** see `agentic_core/L0_routing/CODEOWNERS`

## Eval Harness (apps-eval-harness-closeout-b7c9d2 W3.P1)

The app-specific evaluation rubric and threshold profile live under
`apps_rg/config/domain_contract/` and are authoritative via the L4
`AppEvalRubricRecord` + `AppThresholdProfileRecord` registered through
UWG.

**Rubric**: `apps_rg/config/domain_contract/eval_rubrics.yaml`
**Threshold profile**: `apps_rg/config/domain_contract/threshold_profiles.yaml`
**Grader roster**: `apps_rg/config/domain_contract/grader_roster.yaml`

**HITL policy**: see `threshold_profiles.yaml` `hitl_policy` field
(`none` | `required_on_low` | `required_always`). Soft below-threshold
failures escalate when `required_on_low`; hard guardrail failures always
DENY regardless of policy.

**Run the advisory CI gate**:

`ash
python ops_scripts/ci/check_app_domain_harness_parity.py
`

Exit 0 with JSON report at `artifacts/ci/app_domain_harness_parity.json`.
Fail-closed mode via `APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED=1`.

**Ledger**: per-run outcomes land in
`artifacts/ledgers/eval_harness_outcome.sqlite` (fail-soft — Exit pipeline
is never blocked by ledger errors). Weekly rollup:

`ash
python ops_scripts/calibration/eval_harness_weekly_report.py
`

Emits JSON + Markdown under `docs/reports/eval_harness/<YYYY-Www>.md`.
