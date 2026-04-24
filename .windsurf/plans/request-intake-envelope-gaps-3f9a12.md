# Request Intake + Envelope Check — Best-Practice Gap Rectification Plan

**Plan ID**: `request-intake-envelope-gaps-3f9a12`
**Scope reference**: `@c:/Git/Agentic-Workflow/docs/reference/agentic_process_mapping_v33.md` §[1]
**Contract doc**: `@c:/Git/Agentic-Workflow/docs/reference/01_Request_Intake/01_request_intake.md`
**Implementation under review**: `@c:/Git/Agentic-Workflow/agentic_core/L5_safety/enforcement/ingress_envelope_check.py`
**Tier**: T3 (cross-layer, multi-file, architectural)
**Status**: DRAFT — no code changes yet
**ADG snapshot**: see `artifacts/adg/adg_indexed_<latest>.sqlite` at execution time

---

## 1. Best-Practice Reference Set (Anthropic / OpenAI / Google)

| # | Principle | Source |
|---|-----------|--------|
| BP-1 | Design toolsets deterministically so the model cannot take rogue actions; "expose only the actions we want taken and nothing else" | Anthropic — *Building Effective Agents* |
| BP-2 | Prefer predictable workflows over open-ended agents; pick lowest viable agency | Anthropic — *Building Effective Agents* |
| BP-3 | Ambiguous instructions are a top risk category; reject/clarify at the earliest possible gate | Anthropic Managed Agents, Google ADK Safety |
| BP-4 | Input guardrails run **before** the expensive/side-effecting phase; support both blocking and parallel modes; emit a `tripwire_triggered` signal that aborts the run fail-closed | OpenAI Agents SDK — *Guardrails* |
| BP-5 | Use a dedicated cheap/fast agent or rule set for input validation; do not pay full model cost until the envelope clears | OpenAI Agents SDK — *Guardrails and human review* |
| BP-6 | "Untrusted data must never directly drive agent behavior"; extract only specific structured fields (enums or validated JSON) from external inputs to limit prompt-injection propagation | OpenAI — *Safety in building agents* |
| BP-7 | Identity & Authorization: explicitly choose `Agent-Auth` vs `User-Auth` per tool; attribution logging must survive the agent boundary | Google ADK — *Safety and Security* |
| BP-8 | In-tool guardrails: tools receive **arguments (model-controlled)** and **Tool Context (developer-controlled)**; deterministic ToolContext must enforce the policy, not the model | Google ADK — *Safety and Security* |
| BP-9 | Pre-flight risk assessment per deployment context: adversarial prompt-injection, indirect prompt-injection via tools, PII leakage, data exfiltration | Google ADK — *Safety and Security* |
| BP-10 | Validate inputs **early** to prevent cascading errors — verbose, specific error messages | Google ADK — *Input Validation* best practice |
| BP-11 | Human-in-the-loop pause must be first-class state, not an exception branch | OpenAI — *Guardrails and human review* |

---

## 2. Current Repo State — Observed Facts

| Fact | Evidence |
|------|----------|
| Envelope gate class exists | `@c:/Git/Agentic-Workflow/agentic_core/L5_safety/enforcement/ingress_envelope_check.py:140` |
| E1–E6 checks implemented (transport, schema, identity-presence, quota, dedup) | same file, `_e1_transport`..`_e6_dedup` |
| `StampedRequest` output contract defined | same file, line 109 |
| `RejectionSlip` + `IngressRejected` fail-closed primitives exist | same file, lines 62–106 |
| **Zero production callers** of `IngressEnvelopeCheck` outside the module itself | grep of repo — only design docs reference it |
| **Zero tests** covering the gate | `find tests/ -name "*ingress*"` returns empty |
| E3 identity is **presence-only** — no token/JWT/OAuth verification, no tenant binding beyond a SHA hash of identity+version | `_e3_identity()` body |
| E5 "normalize / clean payload" step from the contract doc is **not implemented** — `StampedRequest.request_payload` passes through raw | `check()` returns `env.get("request_payload")` unmodified |
| **No PII / prompt-injection / jailbreak screen** at ingress | no module in `L5_safety/enforcement/` does this |
| **No structured-field extraction** from untrusted payloads (BP-6) | `request_payload: Any` |
| **No ambiguity / clarify-vs-accept early signal** (BP-3) | E1–E6 doesn't route to `CLARIFY` |
| **No adapters for U1–U4 source classes** (chat, API, batch, callback/webhook) | no `U1..U4` entry modules found |
| `_rate_limiter` is an injected `Any` — **no default implementation**, so E4 is a no-op when omitted | `_e4_quota()` early-returns on `None` |
| Replay-dedup uses in-memory `set[str]` — **not durable across processes**, no TTL | `self._seen_request_ids` |
| `seen_request_ids` can grow unbounded | no eviction policy |
| Trace-emit calls are fired at module-import time (side effects) | lines 47–54 emit `_emit_*` at import |
| No linkage to L6 observability structured telemetry for rejection counts | no OTEL counters, no dashboard |
| Output contract fields present: `request_id`, `session_id`, `trace_root`, `caller_scope_baseline`, `schema_version`, `request_payload`, `caller_identity`, `stamped_at` | `StampedRequest` — matches v33 map except `normalized_payload` missing (raw pass-through) |

---

## 3. Gap Register — Best Practice → Repo Delta

| Gap ID | BP ref | Gap | Current state | Target state | Severity |
|--------|--------|-----|---------------|--------------|:--------:|
| G-01 | BP-4, BP-10 | Gate is **not wired** into any real entry path | `IngressEnvelopeCheck` is orphaned | U1/U2/U3/U4 adapters all call `gate.check(envelope)` before any L1/L0 work | **P0** |
| G-02 | BP-10 | **Zero test coverage** on the gate | 0 tests | ≥95% line coverage + property tests for each rejection path | **P0** |
| G-03 | BP-4 | Gate does not distinguish **blocking** vs **parallel** execution | single `check()` entry | expose `check_blocking()` (default) and document that side-effecting downstream stages never start before clearance | **P1** |
| G-04 | BP-7 | E3 identity = presence-only | string non-empty check | verify bearer token / JWT / OAuth via injected `IdentityVerifier` protocol; produce `caller_scope_baseline` from verified claims, not raw hash | **P0** |
| G-05 | BP-6, BP-9 | **No prompt-injection / jailbreak / PII screen** at ingress | absent | pluggable `InputSafetyScreen` (regex + optional cheap-model classifier) with `IP_DETECTED`, `PII_DETECTED`, `JAILBREAK_DETECTED` rejection codes running between E4 and E5 | **P1** |
| G-06 | BP-6 | Raw `Any` payload passed downstream | `request_payload: Any` | `normalized_payload` field populated by E5 normalizer; strict schema-per-work-class extraction when declared | **P1** |
| G-07 | BP-3, BP-11 | No early **CLARIFY** branch — only accept or reject | binary outcome | third outcome `ClarificationRequired` when envelope valid but intent field obviously empty/ambiguous; routes back to caller, not L1 | **P2** |
| G-08 | BP-8 | E4 rate-limiter is optional → silent no-op when unconfigured | `if self._rate_limiter is None: return` | default in-process token-bucket limiter required; explicit opt-out flag for tests only; log a WARNING on opt-out | **P1** |
| G-09 | BP-10 | Replay-dedup is in-memory, unbounded, non-durable | `set[str]` | swap to LRU-bounded cache or Redis-backed store with TTL aligned to `request_id` freshness window | **P1** |
| G-10 | BP-2 | No structured source adapters for U1–U4 | none | 4 thin adapters that normalize transport → canonical `raw_envelope` dict, then delegate to the gate | **P1** |
| G-11 | BP-10 | No L6 telemetry for rejections / latencies / per-gate-stage counters | absent | emit structured events via existing L6 `observability_recorder`; expose `ingress_rejections_total{reason_code}` counter | **P2** |
| G-12 | BP-4 | Trace-emit side effects at import time | lines 47–54 | move emits inside `check()` or a `register()` call; keep import side-effect-free | **P2** |
| G-13 | BP-10 | No `ingress_time`, no `tenancy_stamp` in `StampedRequest` (contract doc specifies both) | fields missing | add `ingress_time_utc` (already have `stamped_at` — rename/alias) and explicit `tenant_id` | **P2** |
| G-14 | BP-9 | No oversize / abuse guard (body-size, nesting depth, token estimate) | absent | E2 adds `max_payload_bytes`, `max_nesting_depth`, configurable per schema_version | **P1** |
| G-15 | BP-11 | No explicit contract for "rejected" response shape delivered back to the U0 source | `IngressRejected` raised; transport adapters must translate | define `RejectionResponse` dataclass and per-source renderers (HTTP 4xx, webhook 202+deadletter, chat error bubble) | **P2** |
| G-16 | BP-3 | No documentation or ADR cross-linking v33 §[1] ↔ implementation ↔ tests | docs drift from code | ADR + RTM row linking map → contract → class → tests | **P2** |

Severity legend: **P0** = blocks production correctness, **P1** = blocks best-practice parity, **P2** = hardening / observability.

---

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|:------:|------------------|
| W1 | W1.1 – W1.3 | **Wiring + Coverage** — close P0 gaps G-01, G-02 | ~9k | `IngressEnvelopeCheck` class signature is stable; v33 map §[1] is canonical | 🟢 | gate is unavoidable on every U0 entry + ≥95% line coverage |
| W2 | W2.1 – W2.4 | **Identity + Safety Hardening** — close P0/P1 gaps G-04, G-05, G-14 | ~14k | a cheap-model or regex classifier is acceptable for first-cut injection/PII detection; token verifier is injectable | 🟡 | unverified token → `E3_IDENTITY_UNTRUSTED`; injected jailbreak string → `IP_DETECTED`; 1 MB+ payload → `E2_OVERSIZED` |
| W3 | W3.1 – W3.3 | **Payload Normalization + Clarify Branch** — close P1 gaps G-06, G-07, G-08, G-09 | ~11k | default token-bucket limiter + LRU dedup cache acceptable; clarify is a third outcome, not an exception | 🟡 | `normalized_payload` is populated; obviously-ambiguous intent → `ClarificationRequired`; replay cache bounded |
| W4 | W4.1 – W4.4 | **Source Adapters U1–U4** — close P1 gap G-10 | ~12k | HTTP via FastAPI; batch via file drop; webhook via signed HMAC; chat via existing UI hook | 🟡 | all four adapters route through the gate; integration test per adapter |
| W5 | W5.1 – W5.3 | **Observability + Response Contract** — close P2 gaps G-11, G-13, G-15, G-12 | ~8k | L6 `observability_recorder` is the emission SSOT; OTEL counters land in the existing dashboard | 🟢 | `ingress_rejections_total` counter visible; per-source rejection response contracts rendered |
| W6 | W6.1 – W6.2 | **Documentation + ADR + Cleanup** — close P2 gap G-16; retire dead trace-emits at import | ~5k | ADR process is the documented mechanism | 🟢 | ADR posted; RTM row exists; `grep` finds ≤0 import-time side effects |

Total estimate: ~59k tokens. All waves on critical path except W5/W6 (hardening).

---

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|:------:|
| W1.1 | Gate injection point in UWG / L0 front-door | `agentic_core/L3_orchestration/**` entry points + new `agentic_core/L5_safety/enforcement/ingress/__init__.py` | gate is orphaned; need one canonical invocation site | 3k | todo |
| W1.2 | Unit-test matrix for E1–E6 | `tests/unit/agentic_core/L5_safety/enforcement/test_ingress_envelope_check.py` (NEW) | zero current coverage; must include each rejection path + happy path + determinism of trace_root | 4k | todo |
| W1.3 | Property test for replay dedup + idempotency of trace_root given fixed seeds | same test file | behaviour is timing-dependent today (`time.time()` in hash) | 2k | todo |
| W2.1 | `IdentityVerifier` protocol + default no-op + JWT default | `agentic_core/L5_safety/enforcement/identity_verifier.py` (NEW), reference in ingress | no token verification today | 4k | todo |
| W2.2 | `InputSafetyScreen` — regex prompt-injection / PII / jailbreak patterns | `agentic_core/L5_safety/enforcement/input_safety_screen.py` (NEW) | no safety screen at all | 5k | todo |
| W2.3 | Oversize / nesting / token-estimate guard extension to E2 | `ingress_envelope_check.py` + `config/ingress_limits.yaml` (NEW) | abuse vector open | 3k | todo |
| W2.4 | New rejection reason codes + tests | enum + tests | — | 2k | todo |
| W3.1 | E5 normalizer — whitespace / encoding / delimiter normalization; populate `normalized_payload` | `agentic_core/L5_safety/enforcement/payload_normalizer.py` (NEW) | raw pass-through violates BP-6 | 3k | todo |
| W3.2 | `ClarificationRequired` third outcome + wiring | ingress_envelope_check + types | binary outcome today | 3k | todo |
| W3.3 | Default token-bucket limiter + LRU-bounded dedup cache | `agentic_core/L5_safety/enforcement/rate_limit.py` (NEW), `replay_cache.py` (NEW) | silent no-op + unbounded memory | 5k | todo |
| W4.1 | U1 chat adapter | `agentic_core/runtime/entry/chat_adapter.py` (NEW) | — | 3k | todo |
| W4.2 | U2 HTTP/API adapter | `agentic_core/runtime/entry/http_adapter.py` (NEW) | — | 3k | todo |
| W4.3 | U3 batch / scheduled adapter | `agentic_core/runtime/entry/batch_adapter.py` (NEW) | — | 3k | todo |
| W4.4 | U4 webhook / callback adapter with HMAC verification | `agentic_core/runtime/entry/webhook_adapter.py` (NEW) | — | 3k | todo |
| W5.1 | L6 counters + latency histograms | `agentic_core/L6_observability/execution/observability_recorder.py` (edit) | no visibility | 3k | todo |
| W5.2 | `RejectionResponse` contract + 4 renderers | new module | no response shape | 3k | todo |
| W5.3 | Lift import-time trace emits into `register()` | `ingress_envelope_check.py` (edit) | import side effects | 2k | todo |
| W6.1 | ADR `ADR-NNN-request-intake-envelope-hardening.md` + RTM row | `docs/architecture/adr/` + `docs/reports/design/requirements_traceability_matrix.md` | docs/code drift | 3k | todo |
| W6.2 | AGENTS.md / v33 cross-links; Memory + Notion writeback per writeback-discipline rule | AGENTS.md edit, Notion MCP row | missing writeback | 2k | todo |

---

## 6. Assumptions (fact-graded)

- **DIRECTLY_OBSERVED**: `IngressEnvelopeCheck` class exists with E1/E2/E3/E4/E6; E5 body is the hash-based scope derivation, not the payload-normalization step the contract doc describes.
- **DIRECTLY_OBSERVED**: No callers in production code; confirmed by `grep` for `IngressEnvelopeCheck`.
- **DIRECTLY_OBSERVED**: No tests under `tests/` match `*ingress*`.
- **DERIVED**: Because the gate is orphaned, current U0 entries (chat / apps_* runners) perform their own ad-hoc validation at best — so any rejection path defined in the gate today is dead code from the system's perspective.
- **DERIVED**: Wiring the gate at a single chokepoint (e.g., an L3 orchestration entry wrapper) is lower blast-radius than 4 adapters each calling it, but we still need the 4 adapters for the U1–U4 source contract.
- **UNRESOLVED**: Whether an existing `rate_limiter` implementation already lives elsewhere in the repo and should be reused, or whether W3.3 must introduce a new one. → resolve in W3.3 intake.
- **UNRESOLVED**: Whether OAuth/JWT verification is expected now or deferred to a later hardening wave. → resolve in W2.1 intake.

---

## 7. Execution Rules (reminders, not new policy)

- No code changes are authorized by this plan draft. Each wave opens with an intake packet that must pass the constitutional Author-Gate where ambiguity exists (e.g., W2.1 identity strategy, W3.3 limiter choice).
- Every edit must include scoped tests in the same commit; no `pytest.mark.skip`.
- ADG must be healthy before W1 starts; regenerate after W1, W2, W3 per `/adg-redis-refresh`.
- Writeback: upon completion of each wave, emit `DEFERRED_SCOPE:` markers for any residual hardening that spills into W6; update Memory `Project:request-intake-envelope-gaps-3f9a12` observation with wave status.

---

## 8. Definition of Done

- All 16 gaps closed or explicitly deferred with a `DEFERRED_SCOPE:` marker and Notion Wave/Phase row.
- `IngressEnvelopeCheck` invoked on every U1–U4 path; integration tests prove a raw U0 event cannot reach L1 without passing the gate.
- ≥95% line coverage on `ingress_envelope_check.py` and every new module under `agentic_core/L5_safety/enforcement/`.
- ADR filed; RTM row added; AGENTS.md + Notion ADR Registry updated.
- `grep -n "import.*ingress_envelope_check" agentic_core/ apps_*/ tools/` shows the gate is imported only from entry adapters and tests, never from internal L1/L2/L3 paths.
