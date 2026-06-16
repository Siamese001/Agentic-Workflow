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
2. If the composer is stuck, check Anthropic and OpenAI provider health. **Generation is Claude Opus primary and fail-closed**: without a valid Anthropic generation path the composer emits a blocked provider-unavailable draft rather than an ungrounded message. Bring the configured provider up (the model SSOT is `apps_lic/config/domain_contract/model_profiles.yaml`; generator = Claude Opus 4.8, X1D judge = GPT-5.5) before retrying. A "blocked" disposition here reflects a real provider-down verdict, not a stale default.
3. If a deterministic hop is stuck >2× ceiling, that's a code bug — capture state and bisect.

> **Send prerequisites (W6):** a send requires (a) Claude Opus generation and GPT X1D judge provider readiness where applicable (fail-closed, above); (b) C0 evidence readiness — apps_lic C0 is governed-ingestion/payload-only **by design** (no ChromaDB/dense retrieval), with explicit readiness states `READY` / ingestion-required / `STALE` / `CONFLICTED` / `BLOCKED` (`apps_lic/runtime/bindings/c0_binding.py`); (c) the C0.3 sender-proof packet ready, grounded against the shared apps_rg proof SSOT (`apps_lic/integrations/apps_rg_proof_bridge.py` — same `augmented_skills_graph` version apps_rg uses, so resume and outreach proof cannot drift). Dispositions on the Exit bundle reflect real X2/X1D verdicts; a `BLOCKED` is always backed by a reason code, never a stale default.

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
- `python -m apps_lic` — **product CLI entry** (`run_canonical_apps_lic_spine` only; see `apps_lic/__main__.py`)

## Escalation Contacts

- **Primary on-call:** see `CODEOWNERS`
- **L3 inference owner (composer LLM):** see `agentic_core/L3_orchestration/inference/CODEOWNERS`
- **Compliance / HITL:** TBD

## Heal-Method NotImpl Convention

**Established 2026-05-02.** apps_lic agents that derive from `LICAgentBase` (or are stateless renderers) inherit a `heal(violation, **kwargs)` and `heal_repository(*args, **kwargs)` ABC contract. Three categories exist:

| Category | Pattern | Example agents |
|---|---|---|
| **Real heal** | Implements violation-specific repair logic | `OutreachLearningAgent`, `OutreachSignalRouterAgent`, `MessageDiversityValidator` |
| **Delegating heal** | Calls `super().heal(violation, **kwargs)` | `LicTemplateOptimizerAgent`, `PIISanitizerSpecialistAgent`, most QA agents |
| **No-op heal** ← THIS DOC | Returns structured `{"status": "noop", "agent": <name>, "reason": <why>}` | `ExecutiveStrategyAgent`, `GovernanceShieldAgent`, `ValidatorAgent`, `OutreachMessageAgent` |

### When to use no-op heal

Use the no-op pattern when an agent owns **no mutable state and no repository surface** (typically: prompt-only renderers, stateless audit agents, ABC-required surface that doesn't apply). The pattern is:

```python
def heal_repository(self, *args, **kwargs) -> dict:
    """No-op repository heal for <AgentName>.

    <AgentName> <one-line role>; it owns no <state-or-repo-surface>.
    Convention: see apps_lic/RUNBOOK.md "Heal-Method NotImpl Convention".
    """
    return {
        "status": "noop",
        "agent": "<AgentName>",
        "reason": "<specific justification>",
    }
```

### Why no-op instead of `raise NotImplementedError`

Prior pattern: `raise NotImplementedError("heal_repository() not implemented for <Agent>")` with `# guardian: allow-type-erasure` comment.

Problem: callers in the healing chain had to wrap every `heal_repository()` invocation in a try/except, OR the chain crashed on agents with no healable surface. The structured no-op:

1. Eliminates exception-handling boilerplate at every call site
2. Makes the "no-op" outcome **observable** — callers can branch on `result["status"] == "noop"`
3. Removes the `# guardian: allow-type-erasure` exemption requirement (per constitutional §8, generic guardian comments are forbidden — `allow-type-erasure` was borderline)

### Conversion completed (2026-05-02)

Plan `apps-completeness-followups-287d2a` W5 converted the following sites from `raise NotImplementedError` to structured no-op:

- `reasoning/ExecutiveStrategyAgent.py::heal` and `::heal_repository` (predecessor plan `907fac` W1.1)
- `reasoning/GovernanceShieldAgent.py::heal_repository` (predecessor plan `907fac` W1.2)
- `reasoning/ValidatorAgent.py::heal_repository`
- `reasoning/OutreachMessageAgent.py::heal` and `::heal_repository`

### What remains (and why)

`utils/lic_engine_validation_capability_util.py::_validate`, `utils/lic_agent_base_util.py::_process`, `utils/hop_stage_capability_util.py::_process` retain `raise NotImplementedError` — these are **legitimate ABC template-method patterns** ("subclass must override"), not heal-chain stubs. Their NotImpl is structurally correct: invoking them on an unsubclassed instance is a programming error, not a runtime healing-chain branch. **Do not convert these to no-ops.**

## Eval Harness (apps-eval-harness-closeout-b7c9d2 W3.P1)

The app-specific evaluation rubric and threshold profile live under
`apps_lic/config/domain_contract/` and are authoritative via the L4
`AppEvalRubricRecord` + `AppThresholdProfileRecord` registered through
UWG.

**Rubric**: `apps_lic/config/domain_contract/eval_rubrics.yaml`
**Threshold profile**: `apps_lic/config/domain_contract/threshold_profiles.yaml`
**Grader roster**: `apps_lic/config/domain_contract/grader_roster.yaml`

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

---

## Spine Acceptance — W4 Final (2026-05-05)

**Status**: ✅ ACCEPTED — All waves complete

### Acceptance Proof

```bash
python -m pytest tests/governance/test_apps_lic_entrypoint_purity.py \
       tests/governance/test_apps_lic_prompt_assembly.py \
       tests/governance/test_apps_lic_static_recipe.py \
       tests/governance/test_apps_lic_r3r4_managed_workflow.py \
       -q --tb=short
```

**Result**: `81 passed, 0 failed, 0 skipped`

### Wave Summary

| Wave | Focus | Status | Test Count |
|------|-------|--------|------------|
| P0 | Entrypoint purity | ✅ Accepted | 25 |
| P1.5 | Prompt Assembly, PromptBOM, registry | ✅ Accepted | 25 |
| W2 | R4 static recipe (E1-E5) | ✅ Accepted | 14 |
| W3 | R3R4 managed workflow | ✅ Accepted | 17 |
| **W4** | **Final acceptance, legacy quarantine** | **✅ Accepted** | **81 total** |

### Architecture

**R4 managed draft** (briefing present at L0):
`U0 → L1 → L0 (R4) → C0 → PA → L3 HOP → L2 → Exit`

**R3R4 managed research then draft** (briefing missing, research authorized):
`U0 → L1 → L0 (R3R4) → managed_workflow_dispatcher / apps_research_bridge → re-plan → L0 (R4) → C0 → PA → L3 HOP → L2 → Exit`

Live R3R4 research CLI: `WIZARD_FILE_MODE=1 python -m apps_lic` with wizard briefing `mode=auto` and **no** `APPS_LIC_MOCK_RESEARCH`. Mock bridge is **EVAL_ONLY** and does not satisfy release eligibility.

**Deleted shadow runners (P3–P5 hard-delete)**:
- `run_workflow_lic.py`, `governed_lic_run.py`, `spine_handoff.py`, YAML L2 DAGs — removed; not importable from product CLI

### Invariants Preserved

- ✅ No callable passing from apps_lic
- ✅ No direct apps_research import from __main__.py or L0
- ✅ Bridge executes only as registered L3/L2 managed workflow step
- ✅ No ad hoc prompt strings
- ✅ No provider SDK calls outside governed gateway
- ✅ No legacy fallback
- ✅ No generic draft on research failure

### Files

| Purpose | Path |
|---------|------|
| Product dispatch | `apps_lic/runtime/dispatch/canonical_dispatch.py` |
| L2 HOP SSOT | `apps_lic/config/hop_pipeline.py` (`REGISTRY`) |
| L2 execution | `apps_lic/runtime/bindings/l2_binding.py` |
| Research bridge | `apps_lic/integrations/apps_research_bridge.py` |
| Workflow dispatcher | `apps_lic/integrations/managed_workflow_dispatcher.py` |
| Eval harness (non-product) | `apps_lic/eval/` — **EVAL_ONLY**; not reachable from `python -m apps_lic` |
| Governance tests | `tests/governance/test_apps_lic_*.py` |
