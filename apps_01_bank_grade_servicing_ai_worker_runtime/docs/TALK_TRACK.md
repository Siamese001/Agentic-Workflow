# Interview Talk Track — Fee-Adjustment Agentic Worker

One page. Use the UI + eval table as the visuals.

## 30-second pitch
"I built a reference implementation of a bank-grade agentic control plane for
servicing fee adjustments — one use case, end to end. The headline is the
inversion most agent demos get wrong: **the model proposes, the deterministic
control plane disposes, and the agent is the least-trusted component.** The LLM
never has authority; it has a voice. Everything money-touching is a deterministic,
auditable, human-gated control around it."

## Architecture in one breath
"A request flows through a fixed spine: validate → frame ambiguity → deterministic
route → evidence custody → prompt/data boundary → **the one model call** → exit
disposition → (human review if needed) → write gate → archive. The model can only
emit an inert proposed diff. Exit emits exactly one disposition. The write gate is
the single path to durable state. HITL is a disposition, not something the model
chooses. UNKNOWN is never PASS."

## What's actually real (don't overclaim)
- Live local **Qwen2.5-32B** decision at L2 — recorded for deterministic replay.
- Gates derive the disposition from **evidence**, not the model's word — I have
  tests proving a wrong or failed model can't approve a conflicted or complaint case.
- The durable write is **physically gated** — one function, refuses without a
  UWG-approved commit.
- An **eval suite** with prompt-injection cases; defense-in-depth (model resisted
  AND gate caught).

## The demo (≈3 minutes)
1. **Scenario B** — show the case + C0 evidence custody (each item has ACL,
   freshness, quality, contradiction status, can-support-write).
2. **Live Worker panel** — Qwen recommends *escalate*; show provenance: real model
   id, ~2.5s, ~1k prompt tokens.
3. **Exit** — the deterministic gate escalates (X3B). Stress: *not because the model
   said so — because the evidence posture requires a human.*
4. **HITL approve → re-clearance → UWG validates → L4 row appears** in the real
   SQLite ledger. Before/after state.
5. **Eval tab** — 7/7; injection caught 2/2 by both the model and the gate.
6. **The kicker** — the test where the model is forced to say *approve* on the
   conflicted case: the gate still abstains, no write. "The model was wrong and the
   control plane caught it."

## SR 11-7 / model risk management mapping
- The LLM is **a model** under MRM; the deterministic gates are the **controls**.
- The replayable trace is **audit/dispute evidence** (reproduces byte-for-byte).
- HITL is **structural**, not optional.
- Fail-closed UNKNOWN is the **conservative default** examiners want.

## Hard questions → crisp answers
- **What model / why local?** Qwen2.5-32B AWQ, on-prem via vLLM — nothing leaves
  the bank. 24k context is ~4× what bounded prompts need.
- **How do you know it's safe?** Two independent layers (model discipline + gate),
  proven by tests, and the write is physically gated. Safety is a property of the
  control plane, not a hope about the model.
- **Latency / cost?** ~2.5s per decision, one call per case, ~1k prompt tokens.
- **What breaks at Truist scale?** Throughput + batching, a model registry under
  MRM, expanding the eval set to labeled production history, human-review staffing
  and SLAs, OTEL observability, multi-tenant policy config behind the same gates.
- **What would you harden for real prod?** System-of-record adapters behind UWG,
  golden eval set from labeled cases, canary + rollback, judge calibration cadence,
  formal SR 11-7 documentation, secrets/key management, PII handling.

## Honesty line (say it early)
"This is a working reference implementation — a prototype of the control plane I'd
stand up. Let me be precise about what's real and what I'd harden for production at
your scale." Then show, don't tell.
