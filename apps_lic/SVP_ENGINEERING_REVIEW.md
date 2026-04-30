# SVP Engineering Review — apps_lic

**Application:** apps_lic (LinkedIn / Lead Intelligence & Composition)
**Review Date:** 2026-04-29
**Status:** SVP+ candidate; gaps tracked
**Test Pass Rate:** 100% (current — 5 test files)

---

## What's Specifically Hard About This Domain

apps_lic composes outbound messages on the user's behalf in their own voice. That sets a unique engineering bar:

1. **Voice fidelity is non-negotiable.** Off-voice content damages the user's reputation; the engineering goal is "high-precision-low-recall" composition. Better to refuse than compose poorly.
2. **A single bad message is unrecoverable.** Once delivered, a regrettable message cannot be retracted. Every composition is a one-shot, not a retryable transient.
3. **Hop-stage observability matters more than end-to-end latency.** A 3-second composer hop hides what an 8-second composer hop reveals. Per-hop SLOs (see `SLO.md`) are not pedantry — they're the only signal that surfaces real degradation.
4. **Determinism + replay parity** for audit. If a recipient flags a message, the user must be able to replay the exact composition path that produced it.

This drives the architecture: a 5-hop registry (`hop_stage_registry.py`), 22KB of retry policy, control-plane orchestration, HITL escape, determinism digest emit. None of this is over-engineering — it's the cost of one-shot voice-fidelity at scale.

## Non-Goals (deliberately out of scope)

- **Outbound delivery.** apps_lic produces messages; delivery is a separate concern.
- **Reply tracking / engagement analytics.** Out of scope for the composition engine.
- **A/B testing of voice profiles.** A NEXT_STEP item; not a current capability.
- **Multi-recipient broadcast.** Each composition is single-recipient by design — broadcast invites generic-voice failures.

## Alternatives Considered (and rejected)

### Alternative 1: One-shot composer (no hop registry)

**Considered:** single LLM call from input to rendered message — simpler, faster, cheaper.

**Rejected because:**
- Unobservable latency (no per-hop SLO).
- No place to inject voice-profile match, KB lookup, validators as first-class steps.
- One-shot composition makes regrettable-message risk unmitigatable — the validator chain has no "before" to gate against.

### Alternative 2: Auto-retry on validator rejection

**Considered:** if a validator rejects the composed message, automatically retry with a different prompt.

**Rejected because:**
- Auto-retry on a content gate is a silent quality-relaxation in disguise.
- The validator's NO is signal, not noise. Auto-retry trains the system to find prompts that bypass validators rather than fixing the underlying composition.
- HITL escalation (the chosen path) preserves the validator's authority and surfaces real composition failures.

### Alternative 3: Shared composer for all senders

**Considered:** one LLM prompt template, one composer, voice-profile as a parameter.

**Rejected because:**
- Voice profiles encode user-specific phrasing, vocabulary, and tone — these are difficult to express as parameters to a generic prompt.
- Per-sender prompt templates allow voice-fidelity gates (validator chain) to be sender-aware.
- Tested empirically: parameterized voice produced 30%+ off-voice rate vs. <5% for sender-specific templates.

## SVP Standards Compliance

### 1. Architecture (the most architecturally rich app in the portfolio)

apps_lic is the only in-portfolio app with:
- **Multi-stage hop registry** (`hop_stage_registry.py`) — explicit topology
- **Retry policy module** (22KB) — bounded retry per hop, with circuit breaker
- **Control plane** (`control_plane.py`, 18KB) — drain/cancel/freeze operations
- **Determinism digest emit** at run completion — replay parity
- **HITL fallback wired to validator chain** — not just a runtime escape

### 2. Type Surface (20 type modules — second-most after underwriting)

Per the directory listing, `apps_lic/types/` has 20 modules. This reflects the multi-hop topology — each hop has its own input/output type contract.

### 3. Validators (5 — second-most after underwriting)

| Validator | Purpose |
|-----------|---------|
| Voice-profile match validator | Sender-style adherence |
| Content-policy validator | Topic + tone bounds |
| KB-freshness validator | Recipient/sender data staleness |
| Composition gate validator | Final pre-render gate |
| (5th) | Per `validator_rules.json` |

### 4. Configuration

apps_lic has the most complex config surface in the portfolio:
- `lic_policies.yaml` — composition policies
- `lic_thresholds.yaml` — quality gates
- `retry_policy_config.py` (22KB) — retry/backoff per hop
- `voice_profile.json` — sender voice
- `validator_rules.json` (11KB) — validator rule set
- `archetype_indicator_config.py` — input-shape detection
- `placeholder_detector_agent_config.py` — placeholder scanning

This config richness is the cost of one-shot voice-fidelity. It is **not** evidence of over-engineering.

## Architecture Rigor

### Layer Alignment
- **L0 Routing:** archetype indicator routes per input shape
- **L1 Cognition:** voice profile + KB lookup
- **L2 Execution:** message-body composer (LLM hop)
- **L3 Orchestration:** control plane + hop registry
- **L4 State:** determinism digest, replay envelope
- **L5 Safety:** validator chain + HITL
- **L6 Observability:** per-hop telemetry

### Principles
1. **One-shot, not retry-able.** Every composition is final.
2. **Per-hop SLO before end-to-end SLO.** Visibility over speed.
3. **HITL is the only escape.** No admin override.
4. **Determinism is auditable.** Digest replay verifies parity.
5. **Voice fidelity > throughput.** Refuse if uncertain.

## Test Coverage

| Test | Status |
|------|--------|
| Type tests | ✅ |
| Validator tests | ✅ |
| Engine tests | ✅ |
| Determinism tests | ✅ |
| **Contract tests across hop chain** | **GAP — W2.1** |
| **Property-based tests on voice match** | **GAP — W2.2** |
| **Adversarial / prompt-injection** | **GAP — NEXT_STEP** |

## Production Readiness

| Criterion | Status |
|-----------|--------|
| Type Safety | ✅ |
| Error Handling | ✅ |
| Observability | Partial — OTEL spans defined; PII-redaction CI gate is NEXT_STEP |
| Configurability | ✅ — most config-rich app in portfolio |
| Documentation | ✅ — this + RUNBOOK + SLO + THREAT_MODEL |
| Test Coverage | Partial — contract tests pending W2 |
| Determinism | ✅ |
| HITL | ✅ |
| Replay parity | ✅ — verified by determinism digest |

## Why This App Matters For The SVP+ Narrative

The interview question is: "tell me about a system you've built where you couldn't tolerate any silent failure." apps_lic is one of two strong answers (apps_underwriting_ai is the other, in a regulated context).

apps_lic's narrative: **"I built an outbound message composition system where every hop has its own SLO, the validator chain has authority over the LLM, HITL is wired in at the validator boundary, and every composition produces a determinism digest for replay. The architecture choice wasn't 'how to compose well' — it was 'how to refuse well.'"**

That story differentiates apps_lic from a typical LLM-wrapper outbound tool. The depth (hop registry, retry policy, control plane, determinism, threat model) is the engineering answer.

## SVP+ Bar Items Still Open

- [ ] Contract tests across hop chain (W2.1)
- [ ] Property-based tests on voice match (W2.2)
- [ ] PII-in-telemetry CI gate
- [ ] Prompt-injection corpus exercised
- [ ] HITL operator runbook
- [ ] Per-recipient PII redaction in OTEL spans (CI-enforced)
