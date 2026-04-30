# RUNBOOK — apps_lic

> **When to use this:** a hop chain stalled, retry storm, determinism mismatch, HITL backlog.
> **Companion docs:** `SLO.md` · (SVP review at W1.5)
> **Owner:** see `CODEOWNERS`

## On-Call Decision Tree (5-minute triage)

```
apps_lic is misbehaving
├── Did a hop chain stall mid-run?
│   ├── YES → §1 Hop Chain Stall
│   └── NO  → continue
├── Is the retry counter spiking?
│   ├── YES → §2 Retry Storm
│   └── NO  → continue
├── Is determinism digest mismatching on replay?
│   ├── YES → §3 Determinism Failure (CRITICAL)
│   └── NO  → continue
├── Is HITL escalation rate >8%?
│   ├── YES → §4 HITL Backlog
│   └── NO  → §5 Generic
```

## §1 Hop Chain Stall

**Symptom:** a hop chain begins but never completes within the per-hop ceiling.

**Hop ceilings (from SLO.md):**

| Hop | Ceiling |
|---|---:|
| Archetype indicator | 2s |
| KB lookup | 3s |
| Voice-profile match | 1s |
| Message-body composer (LLM) | 30s |
| Validator pass | 2s |

The composer is the most common stall location.

**Triage:**
1. Check which hop is stuck: `python -m apps_lic --inspect --run-id=<id>` shows current hop + elapsed.
2. If the composer is stuck, check Qwen health (see apps_eval RUNBOOK §1).
3. If a deterministic hop is stuck >2× ceiling, that's a code bug — capture state and bisect.

**Mitigation:**
- Cancel the run via the control plane: `python -m apps_lic.engines.control_plane --cancel --run-id=<id>`.
- The retry policy in `retry_policy_config.py` will pick up; if it doesn't, the circuit breaker tripped (see §2).

## §2 Retry Storm

**Symptom:** retry counter for a given hop ID climbs >5 in <1min, or circuit breaker trips.

**Triage:**
1. Inspect `apps_lic/config/retry_policy_config.py` — the policy is detailed (22KB) and may have a misconfigured backoff.
2. Check whether the underlying hop is failing for a transient reason (rate limit, timeout) or a real reason (validator hit).
3. If the validator chain is rejecting the message body repeatedly, **the message is the problem, not the retry** — escalate to HITL.

**Mitigation:**
- Manually trip the circuit breaker if not already: prevents further retries on the same input.
- Reset only after the upstream cause is identified.

## §3 Determinism Failure (CRITICAL)

**Symptom:** `emit_determinism_digest` produces different outputs on replay.

**This is a CRITICAL data-integrity issue.** apps_lic depends on determinism digests for replay parity and audit trails.

**Triage:**
1. Freeze the run: `python -m apps_lic.engines.control_plane --freeze --run-id=<id>`.
2. Capture full input + intermediate state: `python -m apps_lic --capture-state --run-id=<id>`.
3. **Do NOT auto-recover.** Determinism failures must be diagnosed before resumption.

**Common causes (in order of probability):**
1. **Non-deterministic timestamp** snuck into a hop (e.g., `datetime.now()` inside a deterministic stage).
2. **LLM response with non-zero temperature** in a hop expected to be deterministic.
3. **Floating-point ordering** (rare; usually deterministic on identical hardware).
4. **External data refresh** between original run and replay (KB or voice profile changed).

**Mitigation:**
- Identify the non-deterministic source.
- Either (a) make it deterministic, or (b) declare the hop non-deterministic and adjust the digest contract via ADR.
- Never relax the digest assertion silently.

## §4 HITL Backlog (escalation rate >8%)

**Symptom:** `apps_lic.outputs.hitl_router` queue depth growing or escalation rate exceeds 8% SLO.

**Triage:**
1. Check which validator is firing most often: `python -m apps_lic --hitl-stats --since='24h ago'`.
2. If one validator dominates, the validator is too aggressive OR the upstream input quality dropped.
3. Spot-check 5 escalated cases manually.

**Mitigation:**
- If validator is too strict → Author-Gate review of the validator threshold; do NOT silently relax.
- If input quality dropped → trace upstream to the source (likely a knowledge-base refresh issue).

## §5 Generic Investigation

1. Inspect control plane state: `python -m apps_lic.engines.control_plane --status`.
2. Re-run with full trace: `python -m apps_lic --trace --replay --run-id=<id>`.
3. Bisect against last 24h commits.

## Rollback Procedure

apps_lic has two rollback layers:

**Configuration rollback** (safe):
1. `git revert <commit>` on `apps_lic/config/*.yaml` or `*_config.py`.
2. Re-run smoke test: `python -m apps_lic --demo`.

**Engine rollback** (riskier — affects in-flight runs):
1. Drain in-flight: `python -m apps_lic.engines.control_plane --drain --grace=60s`.
2. `git revert <commit>` on engines / outputs.
3. Restart workers.
4. Replay any drained runs (determinism digest verifies parity).

## Top-3 Failure Modes

1. **Composer stall (LLM)** → §1
2. **Determinism digest mismatch** → §3 (CRITICAL — data integrity)
3. **Retry storm** → §2

## Key Files

- `engines/control_plane.py` — top-level orchestrator (18KB)
- `engines/hop_stage_registry.py` — hop topology
- `config/retry_policy_config.py` — retry / backoff (22KB)
- `validators/*.py` — per-stage validators
- `tools/run_workflow_lic.py` — CLI entry; the highest-emit-edge file (85 ADG edges) — **THIS is your operational entry point**

## Escalation Contacts

- **Primary on-call:** see `CODEOWNERS`
- **L3 inference owner (composer LLM):** see `agentic_core/L3_orchestration/inference/CODEOWNERS`
- **Compliance / HITL:** TBD
