# RUNBOOK — apps_exec

> **When to use this:** an executive brief is wrong, slow, or unrendered. Start at top.
> **Companion docs:** `SLO.md` · `SVP_ENGINEERING_REVIEW.md` · `TECHNICAL_SPEC.md`
> **Owner:** see `CODEOWNERS`

## On-Call Decision Tree (5-minute triage)

```
A brief request is misbehaving
├── Did the brief render at all?
│   ├── NO  → §1 Render Failure
│   └── YES → continue
├── Did it exceed the 90s hard ceiling?
│   ├── YES → §2 Latency Stall
│   └── NO  → continue
├── Are gate_violations non-empty?
│   ├── YES → §3 Quality Gate Failure
│   └── NO  → continue
├── Is style validator firing repeatedly?
│   ├── YES → §4 Style Drift
│   └── NO  → §5 Generic Investigation
```

## §1 Render Failure (no output at all)

**Symptom:** `ExecBriefResult.brief_text == ""` or render exception.

**Triage:**
1. Check `gate_violations` — if `NO_CAPABILITIES_EXTRACTED`, the upstream extraction failed; that's the real bug.
2. Check `BriefSection` count — if 0, the assembly engine never produced sections.
3. Re-run with `--trace` to capture per-phase timing.

**Mitigation:**
- If capability extraction is down → return a stub brief with `gate_violations=["DEGRADED_NO_CAPABILITIES"]` so the user sees an actionable error rather than silence.
- Never silently render a brief with placeholder content.

## §2 Latency Stall (>90s)

**Symptom:** brief generation hangs >90s.

**Almost always upstream LLM.** The local code paths (style validator, render) are bounded under 1s.

**Triage:**
1. `python -c "from agentic_core.L3_orchestration.inference.qwen_vllm import AppsQwenGateway; print(AppsQwenGateway().health())"` — if Qwen is the bottleneck, this surfaces it.
2. Check `apps_qwen_telemetry` for long-running session.

**Mitigation:**
- Cancel the hung request.
- Fall through to **deterministic skeleton brief** (executive summary + capability bullets, no LLM-generated narrative).
- Surface the degradation explicitly to the user.

## §3 Quality Gate Failure (gate_violations non-empty)

**Common gate violations and responses:**

| Violation | What it means | Response |
|---|---|---|
| `EVIDENCE_TOO_OLD` | Capability evidence anchor > 90 days | Refresh evidence sources; do NOT silently relax the threshold |
| `STYLE_VIOLATIONS_EXCEED_LIMIT` | >3 style violations | Surface to user; do NOT auto-rewrite (anti-silent-rewrite) |
| `BRIEF_TOO_SHORT` | <500 words | Likely upstream LLM truncation; check `max_tokens` config |
| `EMPTY_SECTION` | A section came back blank | Rerun assembly with `--retry-empty-sections=1` |

## §4 Style Drift (validator firing repeatedly)

**Symptom:** style validator fires >3 violations on most briefs (not just one).

**Likely cause:** style profile updated without coordinated assembly engine update.

**Triage:**
1. `git log --since='7 days ago' apps_exec/validators/brief_style_validator.py apps_exec/validators/style_gate_validator.py`
2. Compare validator rules against the assembly engine's prompt template.

**Mitigation:**
- Revert the validator change.
- Open an Author-Gate decision: should style drift the validator or the assembly engine?

## §5 Generic Investigation

If none of §1-§4 apply:
1. Capture full trace: `python -m apps_exec --request=<id> --trace --replay`
2. Check determinism: re-run; if output differs, that's the bug, not the brief content.
3. Check upstream `apps_research` or `apps_eval` if the brief depends on their output.

## Rollback Procedure

apps_exec produces briefs as artifacts; **rollback affects only future briefs**, never past ones (briefs are immutable once rendered).

1. `git revert <commit>` on the offending file.
2. Confirm with a smoke test: `python -m apps_exec --demo`.
3. Notify any user whose brief was generated from the bad commit (audit log query).

## Top-3 Failure Modes

1. **LLM stall causing 90s+ hang** → §2 (most frequent)
2. **Style drift after validator update** → §4
3. **Capability extraction returning empty** → §1

## Key Files

- `engines/brief_assembly_engine.py` — main composer
- `engines/capability_extraction_engine.py` — upstream feeder
- `validators/brief_style_validator.py` + `style_gate_validator.py` — gates
- `outputs/brief_renderer.py` + `enterprise_brief_renderer.py` — final render
- `SLO.md` — latency targets

## Escalation Contacts

- **Primary on-call:** see `CODEOWNERS`
- **L3 inference owner:** see `agentic_core/L3_orchestration/inference/CODEOWNERS`

## Eval Harness (apps-eval-harness-closeout-b7c9d2 W3.P1)

The app-specific evaluation rubric and threshold profile live under
`apps_exec/config/domain_contract/` and are authoritative via the L4
`AppEvalRubricRecord` + `AppThresholdProfileRecord` registered through
UWG.

**Rubric**: `apps_exec/config/domain_contract/eval_rubrics.yaml`
**Threshold profile**: `apps_exec/config/domain_contract/threshold_profiles.yaml`
**Grader roster**: `apps_exec/config/domain_contract/grader_roster.yaml`

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
