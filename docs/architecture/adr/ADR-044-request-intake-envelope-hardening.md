# ADR-044 — Request Intake + Envelope Check Hardening

**Status**: Accepted
**Date**: 2026-04-23
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: L5 (primary), runtime entry (new), L6 (via telemetry sink)
**Plan**: `.windsurf/plans/request-intake-envelope-gaps-3f9a12.md`

---

## Context

`docs/reference/agentic_process_mapping_v33.md` §[1] and
`docs/reference/01_Request_Intake/01_request_intake.md` specify the "front desk"
stage of the agentic loop: every inbound request MUST pass an envelope check
before L1 reasoning sees it. The prior implementation at
`agentic_core/L5_safety/enforcement/ingress_envelope_check.py` defined an
`IngressEnvelopeCheck` class with E1–E6 primitives but:

* was **not wired** into any production entry path (zero callers),
* had **zero tests**,
* performed identity verification as a presence check only,
* passed the raw payload through to L1 (no E5 normalization),
* had no prompt-injection / PII / jailbreak screen,
* emitted lifecycle-trace calls at module import time,
* had no rejection-response contract back to the caller.

External agent-safety guidance from Anthropic (*Building Effective Agents*),
OpenAI (*Guardrails*, *Guardrails and human review*, *Safety in building
agents*), and Google ADK (*Safety and Security*) converges on a common
pattern:

1. **Input guardrails run before any expensive / side-effecting stage**
   (OpenAI blocking guardrails; Google "validate inputs early").
2. **Untrusted data never directly drives agent behaviour** — extract only
   specific validated fields (OpenAI).
3. **In-tool guardrails with deterministic policy context** — policy decided by
   the developer, not the model (Google ADK).
4. **Prefer predictable workflows**; reserve open agency for the cases that
   truly need it (Anthropic).
5. **Fast cheap validator agent / rule set** avoids paying full model cost on
   rejected inputs (OpenAI blocking tripwires).

## Decision

Promote the ingress gate to a fully wired, testable, pluggable E1–E7 pipeline
and route every U0 source (U1 chat, U2 HTTP/API, U3 batch, U4 webhook) through
it. Specifically:

| E-stage | Behavior | Module |
|:-------:|----------|--------|
| E1 | Transport validity — non-empty dict | `ingress_envelope_check.py` |
| E2 | Schema + oversize + nesting guard | same + `payload_normalizer.estimate_*` |
| E3 | Identity verification via pluggable `IdentityVerifier` | `identity_verifier.py` |
| E4 | Quota via pluggable `RateLimiter` (default: in-process token bucket) | `rate_limit.py` |
| E5 | Payload normalization (NFC, control chars, whitespace, depth, size cap) | `payload_normalizer.py` |
| E6 | Input safety screen (prompt-injection, jailbreak, PII tripwires) | `input_safety_screen.py` |
| E7 | Replay dedup via bounded LRU cache with optional TTL | `replay_cache.py` |

Additionally:

* The gate returns **three** outcomes: `StampedRequest`, `ClarificationRequired`,
  or raises `IngressRejected`. Clarification is a first-class result, not an
  exception branch.
* `RejectionResponse` + per-source renderers (`render_http`, `render_webhook`,
  `render_chat`, `render_batch`, `render_clarification_http`) keep the
  rejection contract transport-agnostic.
* Four source adapters under `agentic_core/runtime/entry/` are the only
  authorised entry points for U1–U4.
* Lifecycle-trace emits are gated behind `register()` instead of firing at
  import time (G-12).
* `IngressMetrics` exposes four canonical counters / histograms
  (`ingress_requests_total`, `ingress_rejections_total`,
  `ingress_clarifications_total`, `ingress_latency_ms`) — L6 may swap in its
  own sink without touching the gate.

## Rejected Alternatives

* **Wire the gate only at a single L3 orchestration chokepoint instead of
  four adapters.** Rejected: v33 §[1] and the contract doc require four
  distinct U0 shapes to be normalised *before* they can be treated as the same
  canonical envelope. A single chokepoint hides the transport-level rejection
  contract from each source.
* **Hand-roll a JWT verifier in this wave.** Rejected: identity verification
  is deployment-specific; shipping `IdentityVerifier` as a protocol with an
  HMAC default is portable and back-compatible. A JWT verifier is an opt-in
  drop-in later.
* **Use a cheap-model classifier for E6.** Rejected *for this wave*: regex
  patterns are deterministic, fast, and sufficient as a first cut. Classifier
  augmentation stays as a future hardening wave behind the same
  `InputSafetyScreen` protocol.
* **Keep E7 dedup as an unbounded `set[str]`.** Rejected: unbounded growth
  and no TTL — `LRUReplayCache` replaces it.

## Consequences

Positive:

* The gate is now on the critical path for every U0 source; bypassing it
  requires a PR that removes or edits an adapter.
* 60/60 unit tests cover every rejection path, the clarification outcome, the
  happy path, and the supporting primitives.
* Best-practice parity with Anthropic / OpenAI / Google agent-safety guidance.
* Rejections, clarifications, and latency are observable via `IngressMetrics`.

Negative / follow-ups:

* Existing runtime entry modules in `apps_*` are **not yet refactored** to
  route through the new adapters. Separate follow-up wave.
* JWT / OAuth verifier is a protocol-level seam only; production deployments
  supplying OAuth-issued tokens need their own verifier.
* `IngressMetrics` defaults to an in-memory sink; a real OTEL counter adapter
  is deferred.
* Cheap-model augmentation to the safety screen is deferred.

## References

* `.windsurf/plans/request-intake-envelope-gaps-3f9a12.md` — gap register and
  wave plan this ADR closes.
* `docs/reference/agentic_process_mapping_v33.md` §[1]
* `docs/reference/01_Request_Intake/01_request_intake.md`
* Anthropic — *Building Effective Agents*
  (https://www.anthropic.com/research/building-effective-agents)
* OpenAI — Agents SDK Guardrails
  (https://openai.github.io/openai-agents-python/guardrails/)
* OpenAI — Guardrails and human review
  (https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
* Google — Agent Development Kit Safety and Security
  (https://adk.dev/safety/)

## Test Evidence

```
tests/unit/agentic_core/L5_safety/enforcement/test_ingress_envelope_check.py
60 passed, 1 warning in 0.25s
```
