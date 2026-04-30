# RUNBOOK — apps_eval

> **When to use this:** something is wrong with apps_eval in production or staging. Start at the top, work down.
> **Companion docs:** `SLO.md` (target) · `SVP_ENGINEERING_REVIEW.md` (architecture) · `TECHNICAL_SPEC.md` (contracts)
> **Owner:** see `CODEOWNERS`

## On-Call Decision Tree (5-minute triage)

```
A scenario / suite is failing or hung
├── Is the LLM judge (Qwen) reachable?
│   ├── NO  → §1 Judge Unavailable
│   └── YES → continue
├── Are scenarios deterministic but failing?
│   ├── YES → §2 Regression Detector Storm
│   └── NO  → continue
├── Is the suite returning empty / 0 scenarios?
│   ├── YES → §3 Suite Discovery / Loader
│   └── NO  → §4 Generic latency / cost spike
```

## §1 Judge Unavailable (Qwen down or degraded)

**Symptom:** `BaseEvalEngine.evaluate_with_qwen` returns `success=False` with `error="Qwen gateway not available"` or repeated `TimeoutError`.

**Triage:**
1. Check `agentic_core/L3_orchestration/inference/qwen_vllm.py` heartbeat: `python -c "from agentic_core.L3_orchestration.inference.qwen_vllm import AppsQwenGateway; print(AppsQwenGateway().health())"`.
2. Check vLLM container: `docker ps | grep vllm`.
3. Check OTEL spans for `apps_qwen_telemetry.record_request_error` over the last 15 min.

**Mitigation:**
- Mark current run `verdict=DEGRADED`. Skip LLM-judged dimensions.
- Run **only deterministic scenarios** until judge is back.
- Do NOT silently substitute another judge — that violates determinism guarantees.

**Escalation:** if Qwen is down >30min, page L3 inference owner. Block any promotion gate that depends on judge confidence.

## §2 Regression Detector Storm (>10 verdict=REGRESSION in one suite)

**Symptom:** `regression_detector.py` emits >10 `verdict=REGRESSION` records in a single suite run.

**This is almost always a baseline issue, not a real regression.** Three likely causes:
1. Baseline was rebuilt against a buggy snapshot (last 7 days).
2. New scenarios were added without baseline alignment.
3. Judge model swapped (different scoring distribution).

**Triage:**
1. `python -m apps_eval --suite=<id> --baseline-info` → check baseline timestamp + judge model.
2. Compare current judge model ID vs. baseline judge model ID. **If different → halt promotion immediately.**
3. Spot-check 3 of the regressed dimensions manually; if they look correct, the storm is a baseline artifact.

**Mitigation:**
- Halt the promotion gate (`agentic_core/L6_observability/promotion_gates.py`).
- Restore prior baseline.
- Author-Gate review before re-running.

**Escalation:** any storm involving a forbidden-feature or compliance dimension auto-pages compliance.

## §3 Suite Discovery / Loader Failure (empty suite)

**Symptom:** `SuiteResult.scenarios = []` or `gate_violations=["NO_SCENARIOS_FOUND"]`.

**Triage:**
1. Verify `apps_eval/data/evaluation_prompts.json` is present and parseable.
2. Run `python -m apps_eval.engines.scenario_runner --dry-run --suite=<id>` to surface loader errors.
3. Check `apps_eval/config/eval_policies.yaml` for an active suite filter that's excluding everything.

**Mitigation:**
- Restore last-known-good `evaluation_prompts.json` from git.
- Bypass policy filter (`--no-policy-filter`) only for triage, never for production.

## §4 Generic Latency / Cost Spike

**Symptom:** p95 latency or daily cost exceeds SLO.

**Triage steps in order:**
1. **Check token count per call** — a model that "wakes up" with full context window is the #1 cause.
2. **Check semantic cache hit rate** — a deployed config flip can disable caching silently.
3. **Check scorecard render time** — outliers >2s indicate deserialization stall (artifact-cache miss).

**Mitigation:**
- If cost spike > 2× budget → engage cost cap (kill switch in `apps_eval/config/eval_policies.yaml::cost_cap_usd`).
- If latency spike → bisect against last 24h of commits; the eval suite usually isn't the regression source — its caller is.

## Rollback Procedure

apps_eval rollback is **always safe** because evaluations are read-only. The only durable side-effect is writing to `data/judge_calibration/` and emitting promotion-gate signals.

To roll back a bad eval config:
1. `git revert <commit>` on the eval-policies or thresholds yaml.
2. Re-run a known-good suite to confirm green verdict.
3. Re-arm promotion gate if it was disabled.

## Top-3 Failure Modes (must-know for on-call)

1. **Judge model unavailable** → §1
2. **Regression false-positive storm** → §2
3. **Cost spike from unbounded token consumption** → §4

## Key Files (read these first if you're new on-call)

- `engines/scenario_runner.py` — main execution loop
- `engines/regression_detector.py` — baseline comparison logic
- `validators/quality_gate_validator.py` — SLO enforcement
- `config/eval_policies.yaml` — kill switches and thresholds
- `SLO.md` — what "good" looks like

## Escalation Contacts (TODO — fill before this is real)

- **Primary on-call:** see `CODEOWNERS`
- **L3 inference owner (Qwen):** see `agentic_core/L3_orchestration/inference/CODEOWNERS`
- **Compliance gate:** TBD
