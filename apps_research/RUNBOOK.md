# RUNBOOK — apps_research

> **When to use this:** research output is uncited, contradictory, or stalled.
> **Companion docs:** `SLO.md` · `SVP_ENGINEERING_REVIEW.md` · `TECHNICAL_SPEC.md`
> **Owner:** see `CODEOWNERS`

## On-Call Decision Tree

```
A research run is misbehaving
├── Did citation rate drop below 95%?
│   ├── YES → §1 Citation Drop
│   └── NO  → continue
├── Are sources contradicting and synthesis abstaining?
│   ├── YES → §2 Contradiction Resolution
│   └── NO  → continue
├── Is a section stuck >90s?
│   ├── YES → §3 Section Assembly Stall
│   └── NO  → §4 Generic
```

## §1 Citation Drop (rate < 95%)

**Symptom:** rendered research has many uncited claims, or `gate_violations=["LOW_CITATION_RATE"]`.

**Triage:**
1. Check `research_source_validator.py` — is it rejecting too many sources as low-confidence?
2. Check upstream retrieval (SearXNG / vector_db) — is it returning fewer sources than usual?
3. Spot-check the rendered claims: are they hallucinations (no source exists) or grounding bugs (source exists but wasn't linked)?

**Mitigation:**
- If retrieval is degraded → halt promotion of any research-grounded artifact, route to HITL review.
- If grounding is buggy → bisect against `research_assembly_engine.py` (32KB) commits.
- **Never lower the 95% threshold to make the gate pass.** Better to fail explicitly.

## §2 Contradiction Resolution Abstaining

**Symptom:** sources disagree, and synthesis output explicitly says "sources contradict, abstaining."

**This is not a bug — it's the correct behavior.** apps_research is designed to surface contradictions, not silently pick a side.

**Triage:**
1. Confirm the contradiction is real (not a citation parsing bug).
2. Render the output WITH the contradiction visible to the user.
3. The user, not the system, decides which side to trust.

**When this IS a bug:**
- If two sources agree but the system reports them as contradicting → the contradiction-detection logic is over-firing.
- Fix in `engines/research_assembly_engine.py`'s contradiction-detection block.

## §3 Section Assembly Stall

**Symptom:** a single section's assembly call hangs >90s.

**Triage:**
1. Check Qwen health (apps_eval RUNBOOK §1).
2. Check section length — sections >5K target tokens may overflow context.
3. Check for retrieval timeout upstream.

**Mitigation:**
- Kill the stalled section: `python -m apps_research --kill-section <section_id>`.
- Render with explicit gap: section becomes `[Section unavailable due to timeout]`.
- The render proceeds with remaining sections.

## §4 Generic Investigation

If none of §1-§3 apply:
1. Re-run with `--trace --capture-sources` to dump the full source registry.
2. Compare current source count vs. baseline.
3. Check `apps_research/data/judge_calibration/` for recent calibration drift.

## Rollback Procedure

apps_research outputs are **stateless** — no durable side-effects beyond the rendered artifact.

1. `git revert <commit>`.
2. `python -m apps_research --demo` to confirm green.
3. Resume.

## Top-3 Failure Modes

1. **Citation rate drop** → §1 (highest user-visible impact)
2. **Section assembly stall** → §3 (most frequent operationally)
3. **Contradiction over-detection** → §2 (false-positive contradictions degrade output quality)

## Key Files

- `engines/research_assembly_engine.py` — main composer (32KB)
- `engines/research_retrieval_engine.py` — source retrieval (13KB)
- `validators/research_source_validator.py` — source confidence gate (18KB)
- `validators/research_gate_validator.py` — output gate
- `outputs/enterprise_research_renderer.py` — final render

## Escalation Contacts

- **Primary on-call:** see `CODEOWNERS`
- **L3 inference owner:** see `agentic_core/L3_orchestration/inference/CODEOWNERS`
- **SearXNG / retrieval owner:** see `infrastructure/sdks_mcps/CODEOWNERS`

## Eval Harness (apps-eval-harness-closeout-b7c9d2 W3.P1)

The app-specific evaluation rubric and threshold profile live under
`apps_research/config/domain_contract/` and are authoritative via the L4
`AppEvalRubricRecord` + `AppThresholdProfileRecord` registered through
UWG.

**Rubric**: `apps_research/config/domain_contract/eval_rubrics.yaml`
**Threshold profile**: `apps_research/config/domain_contract/threshold_profiles.yaml`
**Grader roster**: `apps_research/config/domain_contract/grader_roster.yaml`

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
