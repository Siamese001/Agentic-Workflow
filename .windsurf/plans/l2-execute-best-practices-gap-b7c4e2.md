# L2 EXECUTE — Best-Practices Gap Analysis & Rectification Plan

- **Plan ID**: `l2-execute-best-practices-gap-b7c4e2`
- **Tier**: T3 (multi-file, cross-layer, adds contracts in L2 + touches L0/L3/L5/L6 seams)
- **Status**: EXECUTING — W0 done, W1 in progress (2026-04-23)
- **Source doctrine**: `docs/reference/agentic_process_mapping_v33.md` §[4] L2 EXECUTE (lines 266–595)
- **ADG snapshot at plan time**: latest `artifacts/adg/adg_indexed_*.sqlite` (to be stamped at Wave 0 entry)
- **Last refreshed**: 2026-04-23

---

## 1. Scope

Review best practices from **Anthropic**, **OpenAI**, and **Google** on L2-equivalent execution (tool validation + sandboxed mutation), score them against v33 §4 doctrine *and* against the current `agentic_core/L2_execution/` implementation, then define waves to close every gap. No edits in this plan.

Out of scope: changes to L0 routing reasoning, L4 durable commit internals, L6 shadow learning grading rubrics. Seam points at L0/L3/L5/L6 are identified but rectification stays inside L2.

---

## 2. Web Best-Practice Corpus (primary sources)

| # | Source | URL | Key patterns extracted |
|---|--------|-----|------------------------|
| 1 | Anthropic — Claude Code Sandboxing | `anthropic.com/engineering/claude-code-sandboxing` | OS-level sandbox (Linux bubblewrap / macOS seatbelt); **filesystem + network isolation both required**; egress proxy with domain confirmation; scoped credentials never inside sandbox |
| 2 | Anthropic — Advanced Tool Use | `anthropic.com/engineering/advanced-tool-use` | Tool Search Tool (context-bloat control), **Programmatic Tool Calling** (code-based orchestration to keep intermediate tool output out of main context), **Tool Use Examples** (few-shot parameter calibration), strategic layering, idempotent + parallel-safe markers |
| 3 | OpenAI — Agents SDK Guardrails | `openai.github.io/openai-agents-python/guardrails/` | **Input / Output / Tool guardrails as first-class wrappers**; `GuardrailFunctionOutput` + `tripwire_triggered` exception pattern that halts execution immediately; optimistic execution with parallel guardrail checks |
| 4 | OpenAI — Agent Builder Safety | `platform.openai.com/docs/guides/agent-builder-safety` | Trace grading per decision / tool call / reasoning step; harden critical steps to cut prompt-injection risk |
| 5 | Google — Vertex AI Function Calling | `docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling` | Strongly-typed params with `enum`; **temperature 0** for tool-selection calls; structured output schemas; **validate-before-execute for high-consequence calls**; **thought signatures** required with function calling; parallel function calling when safe; 10–20 tool active cap |
| 6 | codebridge.tech — Production Guardrails (2026) | `codebridge.tech/articles/ai-agent-guardrails-for-production-kill-switches-escalation-paths-and-safe-recovery` | Permission boundaries (narrow identity), runtime monitoring for unusual tool sequences, escalation as **routing logic** not vague review, **state + recovery** controls that preserve what-already-happened, governance visibility with decision records |
| 7 | arXiv — Architectures for Building Agentic AI (2512.09458) | `arxiv.org/html/2512.09458v1` | Function-schema + structured-output contracts as the defense against silent failures; validator + content-filter chain |

---

## 3. Doctrine Map (what v33 §4 already says)

| v33 Phase | Phase Name | Doctrine promises |
|---|---|---|
| **E1** | Preparation / Prep Desk | Lock env + tools + permissions + budget; bind stable run identity; freeze policy snapshot for the step |
| **E2** | Work Order Check | Integrity + sig chain, cap scope + budget, schema + side-effect class, mutation type sanity |
| **E3** | Doing the Work | Bounded invocation with timeout / circuit breaker; isolated execution (sandbox for mutating ops); telemetry; result class SUCCESS / SOFT\_REPAIRABLE / FAIL\_TERMINAL |
| **E4** | Heal Loop | Same snapshot + lineage; bounded retries; LOCAL → COORDINATED → ESCALATED tiers |
| **E5** | Seal the Final Folder | Replay-oriented receipts; lineage; attempt counters; **NO durable commit** — only sealed artifacts for [5] Exit Eval |

Invariants across all phases: **no routing, no human interaction, no durable commit authority** — those belong to L0, [5] Exit Eval / HITL per ADR-023, and UWG → L4 respectively.

---

## 4. Repo Implementation Inventory (evidence)

| Doctrine phase | Present in repo | Evidence |
|---|---|---|
| E1 init | ✅ | `agentic_core/L2_execution/utils/l2_agent_wrappers.py` (20 `l2_init` / phase-orchestration matches); `types/l2_execution_contract.py`; `reasoning/tool_intent_executor.py` |
| Sandbox (write-blocking) | ✅ (partial) | `enforcement/preventative_sandbox.py` (96 matches) — Python-level monkey-patch blocker covering **filesystem, process, network, persistence, dynamic** write vectors; `types/sandbox_envelope_types.py` (86 matches); `enforcement/firecracker_manager.py` (VM isolation skeleton); `types/ephemeral_vm_types.py` |
| Idempotency / dedup | ✅ | `utils/replay_guard.py` (75 matches on idempotency_key / dedup) |
| Boundary + chokepoint | ✅ | `enforcement/boundary_verifier.py`; `enforcement/execution_guardrail_chokepoint.py`; `enforcement/budget_enforcer.py` |
| Capability / cap tokens | ✅ | `enforcement/SovereignLLMGateway.py`; `capability/ticket_builder.py`; `capability/call_interceptor.py`; `capability/lane_router.py` |
| Healing tiers | ✅ | `healers/healing_router.py` (LOCAL / COORDINATED / ESCALATED); `healers/confidence_scorer.py`; `healers/routing_gates.py` |
| Trace / telemetry | ✅ | `types/execution_trace_types.py` |
| Rollback | ✅ | `reasoning/rollback_refiner.py` |
| Prompt envelope validation | ✅ | `prompt_envelope_validator.py` |
| Structured tool contract | ✅ | `utils/ptc_contract.py` (Precision Tool Contract); `types/execution_tool_contract.py`; `types/ptc_tool_contracts_types.py` |

---

## 5. Gap Register — what the repo is missing vs. the web best practices

Each row is keyed by its rectification wave (§6).

| ID | Gap | Best-practice source | v33 phase touched | Current repo state | Severity | Wave |
|---|---|---|---|---|---|---|
| **G1** | **Unified tripwire guardrail pipeline** (input / output / tool wrappers with `tripwire_triggered` → halt) | OpenAI Agents SDK | E2 + E3 + E5 | Fragmented across `boundary_verifier`, `execution_guardrail_chokepoint`, `budget_enforcer` — no single abstraction, no named tripwire exception shape. Archived code (`archives/adg_dead_code/.../input_guardrail_util.py`) shows the team had a prior attempt. | High | W1 |
| **G2** | **Sandboxed network egress allowlist + proxy** (not just a write-blocker that denies network calls outright) | Anthropic Claude Code Sandboxing | E1 + E3 | `preventative_sandbox.py` blocks `socket`, `urllib`, `requests` as write-class actions, but has **no egress proxy**, no per-step domain allowlist, no runtime confirmation flow for new domains. `firecracker_manager.py` exists but unused at runtime. | High | W2 |
| **G3** | **Scoped per-run credentials** (credentials live outside the sandbox; proxy injects at egress) | Anthropic Claude Code on the Web | E1 | `SovereignLLMGateway.authorize_and_execute()` issues cap tokens but there is no "credentials never inside sandbox" contract. No egress-injection mint path. | High | W2 |
| **G4** | **Thought-signature propagation** across E3 → E4 → E5 (required for reliable multi-turn function calling per Gemini 3) | Google Vertex AI | E3, E4 replay | Grep shows only 3 hits repo-wide (`L0_routing/config/model_registry.py`, `L2_execution/healers/routing_gates.py`, `embeddings/embedding_factory.py`) — no L2 contract carries thought signatures, no heal-replay binds them. | Medium | W3 |
| **G5** | **Tool Use Examples** (few-shot parameter calibration attached to each tool contract) | Anthropic Advanced Tool Use | E2 | `ptc_contract.py` and `execution_tool_contract.py` define structural schemas but have no `examples: list[ToolUseExample]` slot for behavioral clarity. Result: the model relies on schema alone for parameter choice. | Medium | W3 |
| **G6** | **Tool Search Tool** (dynamic retrieval of tool definitions so the active set stays ≤ 10–20) | Anthropic Advanced Tool Use + Google cap | E1 tool binding | `SubAtomicRegistryAgent` has a registry but no embedding-search / description-keyed retrieval. All tools are bound statically at `l2_init`. | Medium | W4 |
| **G7** | **Programmatic Tool Calling** (code-based sub-orchestration that keeps large intermediate tool outputs out of the main context) | Anthropic Advanced Tool Use | E3 | `utils/tool_chain_executor.py` exists (1 match) but no sub-context / code-interpreter-style boundary. Large tool outputs pollute the parent trace. | Medium | W4 |
| **G8** | **Validate-before-execute for high-consequence calls** at E2, not only post-E5 | Google + OpenAI | E2 | v33 says mutation type is checked at E2, but the pre-execute HITL short-circuit is currently only wired at [5] Exit Eval (ADR-023). Irreversible high-blast-radius intents should be able to trip an E2 `CONFIRM_BEFORE_EXECUTE` gate without reaching E3 at all. | High | W1 |
| **G9** | **Side-effect-class + reversibility taxonomy in the work order contract** | Google "validate before significant consequences" + codebridge | E2 | `types/ml_write_intent_types.py` and `types/blast_radius_controls_types.py` exist but there is no canonical `SideEffectClass` enum (`READ / WRITE / ACTION / IRREVERSIBLE`) attached to every tool contract. E2's "mutation type sanity" check is ad-hoc. | High | W1 |
| **G10** | **Parallel-safe / serial-required markers** on tool contracts | Google parallel function calling + Anthropic idempotent/retry markers | E3 | No `parallel_safe: bool` / `idempotent: bool` in `ptc_contract.py`. Heal loop cannot confidently retry without first reasoning ad hoc about reversibility. | Medium | W3 |
| **G11** | **Temperature-0 enforcement for tool-selection calls** | Google Vertex AI | E2/E3 LLM calls | No audit in `SovereignLLMGateway.py` that enforces `temperature ≤ 0.2` for calls whose `tool_choice != "none"`. | Low | W5 |
| **G12** | **Explicit workflow-wide kill switch** separate from E4 ESCALATED | codebridge | E3 + E4 | `healing_router.py` has an ESCALATED tier but no documented workflow-level emergency-stop that preserves state and prevents further E3 re-entry for the same step lineage. | Medium | W4 |
| **G13** | **Runtime-behavior monitoring** (tool-sequence anomaly, retry storm, cost drift) | codebridge | Cross-cutting | Telemetry is emitted but no L2 detector fires on "unusual tool sequence" or "retry storm"; L6 does it post-run. | Medium | W5 |
| **G14** | **E5 seal schema validation** (JSON-schema round-trip before handoff to [5]) | Google structured output + arXiv | E5 | `execution_trace_types.py` defines types; no gate asserts schema conformance as the last step of E5 (would catch silent type drift before [5] Exit Eval). | Low | W5 |
| **G15** | **Trace grading annotations** flowing to L6 shadow eval with per-decision / per-tool / per-reasoning scoring | OpenAI trace grading | E5 → L6 6B | Execution traces include outcomes but not per-step grading hooks. L6 6B (v33 lines 456–470) reads graded signals — grading is currently re-derived there. | Low | W5 |
| **G16** | **Narrow-identity permission boundaries per step** | codebridge + Anthropic | E1 | Cap tokens exist but there is no per-step identity narrowing contract ("this step may only touch `cap:X` and `egress:Y`"). Identity is agent-scoped, not step-scoped. | Medium | W2 |

---

## 6. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W0** | P0.1–P0.3 | ADG-first evidence + hotspot rank, contract inventory freeze | 8k 🟢 | ADG MCP green; redis warm | Todo | `ADG_HOTSPOT_REPORT` + `ADG_GRAPH_LAYER_EVIDENCE` sections populated in this file; every L2 file touched by the plan has a fan-in and a layer multiplier |
| **W1** | P1.1–P1.3 | **E2 contract hardening**: unified tripwire pipeline (G1), side-effect-class + reversibility enum (G9), validate-before-execute short-circuit (G8) | 24k 🟡 | No changes to UWG or L5 runtime HITL; E2 short-circuit feeds [5] HITL via existing ADR-023 seam | Todo | All three gaps closed; added ADR-L2-Guardrails; existing L2 tests still pass; new contract tests for tripwire + side-effect class |
| **W2** | P2.1–P2.3 | **Sandbox hardening**: egress-proxy allowlist (G2), scoped per-run credentials (G3), step-scoped narrow identity (G16) | 28k 🟡 | `firecracker_manager.py` and `ephemeral_vm_types.py` become the enforcement path; `preventative_sandbox.py` retained as in-process backstop | Todo | Tool execution that tries an un-allowlisted domain fails closed; credentials never appear inside sandbox process tree (verified with audit); step identity in trace ≠ agent identity |
| **W3** | P3.1–P3.3 | **Tool-contract enrichment**: thought-signature propagation (G4), Tool Use Examples (G5), parallel-safe / idempotent markers (G10) | 18k 🟢 | Purely additive contract fields with default-safe values | Todo | Every L2 tool has `examples`, `idempotent`, `parallel_safe`, `thought_signature_required` fields; heal replay carries the original signature |
| **W4** | P4.1–P4.3 | **Context + orchestration controls**: Tool Search Tool (G6), Programmatic Tool Calling sub-context (G7), workflow kill switch (G12) | 22k 🟡 | Keep the static binding path as fallback; kill switch is a new opcode in `healing_router.py`, not a new agent | Todo | Active tool set ≤ 20 under Tool Search; large tool output never pollutes parent trace; kill-switch trip preserves state and blocks re-entry for the step lineage |
| **W5** | P5.1–P5.4 | **Observability + schema + seal**: temperature-0 audit (G11), runtime-behavior monitoring (G13), E5 seal schema validation (G14), trace grading hooks (G15) | 14k 🟢 | L6 grading is not refactored; L2 only adds the hooks | Todo | Seal schema validated on every exit; grading annotations visible in L6 6B ingest; audit log for any LLM call with tool_choice + temperature > 0.2 |
| **W6** | P6.1 | Integration test + doctrine sync: update v33 §4 with the new E2 short-circuit and E5 schema-gate arrows; close plan | 6k 🟢 | All W1–W5 complete | Todo | v33 reflects the hardened pipeline; no failing CI gates; memory + Notion writeback posted |

**Total estimate**: ~120k tokens across 6 waves. No wave exceeds 30k (yellow ceiling).

---

## 7. Phase-Level Summary

| Phase ID | Title | Scope (files / modules) | Pain Points | Est. Tokens | Status |
|----------|-------|-------------------------|-------------|------------:|--------|
| P0.1 | ADG hotspot rank for L2 gap targets | `adg_edge_fanin`, `adg_p0_wave_plan` over `agentic_core/L2_execution/**` | ADG must be green; correct snapshot | 3k | Todo |
| P0.2 | Graph-layer evidence (MVs + P-views) | `mv_hotspot_centrality`, `mv_dependency_cone_risk`, `v_p0_*`, semantic edges `flows_to`/`writes_to`/`emits_side_effect` | Populate `ADG_GRAPH_LAYER_EVIDENCE` section (constitutional §22) | 3k | Todo |
| P0.3 | Contract inventory freeze | `ptc_contract.py`, `execution_tool_contract.py`, `l2_execution_contract.py`, `tool_intent_types.py` | Lock baseline before any W1 edit | 2k | Todo |
| P1.1 | Tripwire pipeline primitives | new `agentic_core/L2_execution/enforcement/tool_guardrail_pipeline.py`; wires `boundary_verifier`, `execution_guardrail_chokepoint`, `budget_enforcer` | Avoid import cycles with L5; must reuse guardian exemption pattern | 9k | Todo |
| P1.2 | `SideEffectClass` + `Reversibility` enums on contract | `ptc_contract.py`, `execution_tool_contract.py`, `ml_write_intent_types.py`, `blast_radius_controls_types.py` | Default all existing tools to safest class + reversibility to keep behavior unchanged | 8k | Todo |
| P1.3 | E2 validate-before-execute short-circuit to HITL | `l2_agent_wrappers.py` run_l2_phases(), `capability/call_interceptor.py` | Must not duplicate [5] Exit Eval HITL; cleanly reuses ADR-023 channel | 7k | Todo |
| P2.1 | Egress proxy + domain allowlist | `firecracker_manager.py`, `preventative_sandbox.py`, new `enforcement/egress_proxy.py` | OS-level isolation is out of scope; start with a Python-level proxy with fail-closed default | 11k | Todo |
| P2.2 | Scoped per-run credential mint + inject | `SovereignLLMGateway.py`, `capability/ticket_builder.py`, new `capability/scoped_credential_mint.py` | Secrets must never be logged; rely on `security-hardening.md` rule | 9k | Todo |
| P2.3 | Step-scoped narrow identity | `capability/ticket_builder.py`, `types/execution_trace_types.py` | Backward-compat: existing consumers read agent identity, need adapter | 8k | Todo |
| P3.1 | Thought-signature propagation | `types/l2_execution_contract.py`, `healers/healing_router.py`, `reasoning/tool_intent_executor.py` | Heal replay must carry signature or reject retry | 6k | Todo |
| P3.2 | Tool Use Examples slot | `ptc_contract.py`, `execution_tool_contract.py` + examples data files under `agentic_core/L2_execution/config/tool_examples/` | Optional field; populated per tool incrementally | 6k | Todo |
| P3.3 | `parallel_safe` + `idempotent` markers | `ptc_contract.py`, `utils/tool_chain_executor.py`, `utils/replay_guard.py` | Default to `False` for both (safest) | 6k | Todo |
| P4.1 | Tool Search Tool | `reasoning/SubAtomicRegistryAgent.py` + new `reasoning/tool_search.py` | Embedding-search on tool descriptions; cap active set at 20 | 9k | Todo |
| P4.2 | Programmatic Tool Calling sub-context | `utils/tool_chain_executor.py` + new `reasoning/programmatic_tool_runner.py` | Parent trace sees summary, not raw intermediates | 8k | Todo |
| P4.3 | Workflow kill switch | `healers/healing_router.py`, new `enforcement/kill_switch.py` | Kill switch preserves state + blocks re-entry by step lineage | 5k | Todo |
| P5.1 | Temperature-0 audit for tool-selection LLM calls | `SovereignLLMGateway.py`, `enforcement/execution_guardrail_chokepoint.py` | Warn, don't block, in W5; upgrade to block later | 3k | Todo |
| P5.2 | Runtime behavior monitor (L2-local) | new `enforcement/runtime_behavior_monitor.py`, hooks into `healers/healing_router.py` | Flags tool-sequence anomaly + retry storm + cost drift — emits to L6 async exhaust | 5k | Todo |
| P5.3 | E5 seal schema validator | `types/execution_trace_types.py` + new `enforcement/seal_schema_validator.py` | Validates before handoff to [5] Exit Eval | 3k | Todo |
| P5.4 | Trace grading hooks | `types/execution_trace_types.py`, emits per-step grading slots | L6 6B will consume in next cycle | 3k | Todo |
| P6.1 | Doctrine sync + integration tests + writeback | `docs/reference/agentic_process_mapping_v33.md`, `tests/agentic_core/L2_execution/`, memory + Notion writeback | Final invariant: no durable commit inside L2 | 6k | Todo |

---

## 8. Dependencies + Ordering

- W0 blocks W1..W5 (hotspot rank and contract freeze are prerequisites).
- W1 blocks W3, W5 (contract enums and tripwire pipeline are shape for later).
- W2 is independent of W1 after W0 and can run in parallel with W1.
- W3 blocks W4 (Tool Use Examples + markers feed Tool Search + Programmatic Tool Calling).
- W5 depends on W1 + W3 (needs side-effect class and markers to audit meaningfully).
- W6 depends on W1..W5.

---

## 9. Risk Register

| Risk | Mitigation |
|------|------------|
| Python-level `preventative_sandbox` monkey-patching won't stop native-code network calls | W2 adds egress proxy as process-level control; Firecracker path remains a follow-on (flagged in Deferred Scope below) |
| Unified tripwire pipeline may collide with existing chokepoint / boundary verifier | W0 contract freeze + explicit adapter layer in P1.1; no deletions in W1 |
| Scoped credential mint could break existing cap-token consumers | Backward-compatible shim in P2.2; audit test covers both paths |
| Tool Use Examples file sprawl | One YAML per tool, co-located with contract; CI gate checks presence but not required initially |
| v33 doctrine drift while plan is in flight | W6 explicitly owns the doctrine sync |

---

## 10. ADG_HOTSPOT_REPORT (W0 populated)

Snapshot: `artifacts/adg/adg_indexed_04232026_2225.sqlite`. Metric read: outgoing-import fan-out as proxy for orchestration surface; outgoing fan-in by `dst_id` was 0 for all L2 targets in this snapshot (re-verify against `mv_hotspot_centrality` in W1). Layer multiplier for L2 = ×1.0.

| File | Archetype | Fan-out (imports) | Viol (any) | Surface | Impact (raw × L2 mult) |
|---|---|---:|---:|---|---:|
| `enforcement/execution_guardrail_chokepoint.py` | SAFETY_GATEKEEPER | 107 | 0 | Security+Execution | 107 |
| `reasoning/tool_intent_executor.py` | CENTRAL_DEPENDENCY | 91 | 1 (LOW) | Execution | 91 |
| `enforcement/firecracker_manager.py` | SAFETY_GATEKEEPER | 91 | 1 (LOW) | Security+Write | 91 |
| `utils/replay_guard.py` | STATE_NODE | 89 | 0 | State | 89 |
| `enforcement/preventative_sandbox.py` | SAFETY_GATEKEEPER | 87 | 0 | Security+Write | 87 |
| `types/sandbox_envelope_types.py` | STATE_NODE | 86 | 0 | Security+State | 86 |
| `types/ml_write_intent_types.py` | STATE_NODE | 86 | 2 (LOW) | Write+State | 86 |
| `enforcement/budget_enforcer.py` | SAFETY_GATEKEEPER | 86 | 0 | Execution | 86 |
| `utils/tool_chain_executor.py` | ORCHESTRATOR | 84 | 2 (LOW) | Execution | 84 |
| `utils/ptc_contract.py` | CENTRAL_DEPENDENCY | 82 | 0 | Execution | 82 |
| `enforcement/boundary_verifier.py` | SAFETY_GATEKEEPER | 81 | 0 | Security | 81 |
| `types/blast_radius_controls_types.py` | STATE_NODE | 81 | 0 | Write+State | 81 |
| `types/execution_tool_contract.py` | CENTRAL_DEPENDENCY | 69 | 0 | Execution | 69 |
| `healers/healing_router.py` | ORCHESTRATOR | 19 | 6 (LOW) | Execution+Observability | 19 |
| `enforcement/SovereignLLMGateway.py` | SAFETY_GATEKEEPER | 24 | 3 (LOW) | Security | 24 |

Note: `L2_execution/determinism/replay_guard.py` (fan-out 9) is a second replay guard distinct from `utils/replay_guard.py` (fan-out 89); the utils variant is canonical.

**Prioritization implications**: W1 should start with the CENTRAL_DEPENDENCY contract files (`ptc_contract.py`, `execution_tool_contract.py`) since any field added there propagates immediately to dependent modules (fan-out 69–82). Sandbox hardening (W2) naturally targets `firecracker_manager` + `preventative_sandbox` + `sandbox_envelope_types`.

---

## 11. ADG_GRAPH_LAYER_EVIDENCE (W0 populated)

Snapshot: `artifacts/adg/adg_indexed_04232026_2225.sqlite` (55 MVs + 15 P-views confirmed present).

**Materialized views cited** (≥3 required per constitutional §22):

1. `mv_hotspot_centrality` — primary rank source for §10 table; re-query during W1 to confirm fan-in direction.
2. `mv_dependency_cone_risk` — cone-risk for `enforcement/*` and `reasoning/tool_intent_executor.py`.
3. `mv_l2_phase_coverage` — directly scoped to L2 phase coverage; every new contract field added in W1 must keep coverage ≥ baseline.
4. `mv_capability_and_egress_gaps` — primary view for W2 egress-proxy + scoped-credential work.
5. `mv_heal_retry_exit_gaps` — evidence source for W4 kill-switch placement inside `healing_router.py`.
6. `mv_replay_surface_gaps` — evidence for W3 thought-signature propagation through replay_guard.

**Semantic edges to monitor** during W1–W5: `flows_to`, `writes_to`, `emits_side_effect`, `resolves_callsite`, `controls_flow`. W2 in particular will target new `emits_side_effect` edges leaving `preventative_sandbox.py` and `firecracker_manager.py`.

**P-view cross-references**:
- `v_p0_write_bypass_uwg` — MUST stay empty for L2_execution (invariant: L2 never commits durably).
- `v_p0_provider_bypass` — ensure new W2 egress proxy does not open a provider bypass path.
- `v_p1_raw_http_outside_seam` — W2 egress allowlist must not regress this view.
- `v_p2_duplicated_adapters` — W1 tripwire pipeline must not duplicate `boundary_verifier` + `execution_guardrail_chokepoint`; additive adapter only.

**ADG Provenance**: `backend=sqlite_direct, snapshot=adg_indexed_04232026_2225.sqlite` (direct SQLite read; MCP `adg_sqlite` was transport-closed at session start — §26 serialization discipline applied).

---

## 12. Out-of-scope / Deferred Scope

Captured inline so no follow-ups are lost. These items are **not** part of W1–W6.

- **Native OS-level sandbox** (Linux bubblewrap / macOS seatbelt) parity with Anthropic Sandbox Runtime — Python + proxy path is sufficient for 80/20 coverage; OS primitives are a follow-on wave.
- **Firecracker microVM full lifecycle** — `firecracker_manager.py` exists but full enablement is its own plan.
- **L6 trace-grading rubric refactor** — out of scope; W5 only emits hooks.

`DEFERRED_SCOPE: plan=l2-execute-best-practices-gap-b7c4e2 wave=W_followup phase=P_followup layer=L2 fan_in=0 surface=Security coverage_gap_pct=20.0 est_tokens=30000 reason=Native OS sandbox parity and Firecracker microVM enablement deferred`

---

## 13. Exit Criteria for the Whole Plan

1. Every row in §5 Gap Register has status `CLOSED` with a linked phase completion entry.
2. v33 §4 reflects the hardened E2 + E5 arrows (W6).
3. New L2 contract fields land with default-safe values; no existing consumer breaks.
4. `ops_scripts/ci/run_contract_gates.py` green; L2 test collection count unchanged or higher.
5. Memory writeback: `ProceduralPattern:L2ExecutionHardening2026Q2` created.
6. Notion writeback: ADR Registry row for `ADR-L2-Guardrails` posted; Wave/Phase Convergence rows for W1..W6 posted with status=Done.

---

## 14. Execution Log

### W0 — DONE (2026-04-23)

- ADG snapshot stamped: `artifacts/adg/adg_indexed_04232026_2225.sqlite` (direct SQLite read; `adg_sqlite` MCP was transport-closed).
- `ADG_HOTSPOT_REPORT` (§10) and `ADG_GRAPH_LAYER_EVIDENCE` (§11) sections populated.
- Contract freeze: `ToolCapabilityDescriptor` already had `idempotent` + `requires_sandbox` + `max_retries` + `timeout_ms` — W3 will only add `parallel_safe`, `thought_signature_required`, and `examples` via an adjacent registry; no edit to the frozen dataclass.
- Probe artifact (read-only): `tools/debug/_l2_gap_w0_probe.py`.

### W1 — DONE (2026-04-23) — partial coverage of G1, G8, G9

Three additive modules + one test file landed. No existing module was edited.

| Deliverable | Path | Purpose | Gap |
|---|---|---|---|
| `SafetyProfile` + axis enums (`SideEffectClass`, `Reversibility`, `ConsequenceLevel`) + registry | `agentic_core/L2_execution/types/l2_safety_contracts.py` | Adjacent classification registry keyed by `tool_name`; default-safe lookup keeps rollout permissive. | G9, partial G10 |
| `ToolGuardrailPipeline` + `TripwireTriggered` | `agentic_core/L2_execution/enforcement/tool_guardrail_pipeline.py` | Unified pre/post guardrail wrapper with named halt exception (OpenAI SDK pattern). Additive; does not replace `boundary_verifier` or `execution_guardrail_chokepoint`. | G1 |
| `evaluate_work_order` + `ConfirmBeforeExecute` + `E2RejectedBeforeExecute` | `agentic_core/L2_execution/enforcement/e2_validate_before_execute.py` | E2 short-circuit: raises `ConfirmBeforeExecute` for high/critical or irreversible-non-read tools; re-entry via `metadata["e2_hitl_approval_ticket"]`. | G8 |
| Tests (17, all passing) | `tests/unit/agentic_core/L2_execution/test_l2_safety_w1.py` | Truth table, tripwire pre/post, HITL re-entry, policy hard-rejection. | verification |

Verification: `python -m pytest tests/unit/agentic_core/L2_execution/test_l2_safety_w1.py -q` → **17 passed**, 25 unrelated `DeprecationWarning`s.

**Not yet wired into runtime call sites.** W1's modules are load-bearing primitives only. Phase P1.3 wiring into `l2_agent_wrappers.run_l2_phases()` and `capability/call_interceptor.py` is deferred to the next execution pass to keep the blast radius bounded and tests narrowly scoped.

### W1-P1.3 — DONE (2026-04-23) — wiring

Both call sites wired; default path unchanged when no ToolContract is attached.

| Deliverable | Path | Wiring |
|---|---|---|
| `L2ExecutionAgent._maybe_gate_e2` | `agentic_core/L2_execution/types/l2_execution_contract.py` | Inserted between L2.1 INIT and L2.2 EXECUTE in `run_l2_phases()`. Local imports + fail-open on ImportError. Non-ToolContract inputs ignored. |
| `InterceptResult.needs_hitl_confirmation` + `e2_verdict` | `agentic_core/L2_execution/capability/call_interceptor.py` | New optional fields on the dataclass. `CallInterceptor._maybe_run_e2_gate` runs after risk-tier check; surfaces `rejection_reason="e2_hitl_required"` or `"e2_policy_rejected"`. |
| Tests (7, all passing) | `tests/unit/agentic_core/L2_execution/test_l2_safety_w1_p3_wiring.py` | Default-path preservation, short-circuit on high consequence, HITL-ticket re-entry, non-ToolContract ignore, CallInterceptor symmetry. |

Verification: `python -m pytest tests/unit/agentic_core/L2_execution/test_l2_safety_w1.py tests/unit/agentic_core/L2_execution/test_l2_safety_w1_p3_wiring.py -q` → **24 passed**.

Pre-existing lint warnings in `l2_execution_contract.py` (ellipsis in Protocol abstract methods) and `call_interceptor.py` (unused `target`/`context` in private helpers) were not introduced by these edits and are out of scope.

Pre-existing ADG-scaffolding test failures (220 in `tests/unit/agentic_core/L2_execution/**/test_*_adg.py`) all surface as `AttributeError: module 'agentic_core' has no attribute '...'` and are independent of this work — none touch `l2_execution_contract.py` or `call_interceptor.py`.

### W2–W6 — DEFERRED to subsequent execution passes

To respect bounded-scope discipline, the remaining waves are captured as deferred scope so the Notion backlog auto-captures them (post-hook). Each line below is a separate capture:

`DEFERRED_SCOPE: plan=l2-execute-best-practices-gap-b7c4e2 wave=W1-P1.3 phase=P1.3 layer=L2 fan_in=14 surface=Execution coverage_gap_pct=100.0 est_tokens=7000 reason=Wire evaluate_work_order into l2_agent_wrappers run_l2_phases and call_interceptor`

`DEFERRED_SCOPE: plan=l2-execute-best-practices-gap-b7c4e2 wave=W2 phase=P2.1-P2.3 layer=L2 fan_in=91 surface=Security coverage_gap_pct=80.0 est_tokens=28000 reason=Sandbox hardening egress proxy scoped credentials narrow identity`

`DEFERRED_SCOPE: plan=l2-execute-best-practices-gap-b7c4e2 wave=W3 phase=P3.1-P3.3 layer=L2 fan_in=82 surface=State coverage_gap_pct=70.0 est_tokens=18000 reason=Thought signature tool use examples parallel safe idempotent markers`

`DEFERRED_SCOPE: plan=l2-execute-best-practices-gap-b7c4e2 wave=W4 phase=P4.1-P4.3 layer=L2 fan_in=115 surface=Execution coverage_gap_pct=70.0 est_tokens=22000 reason=Tool search programmatic tool calling workflow kill switch`

`DEFERRED_SCOPE: plan=l2-execute-best-practices-gap-b7c4e2 wave=W5 phase=P5.1-P5.4 layer=L2 fan_in=24 surface=Observability coverage_gap_pct=60.0 est_tokens=14000 reason=Temperature zero audit runtime behavior monitor seal schema validator trace grading hooks`

`DEFERRED_SCOPE: plan=l2-execute-best-practices-gap-b7c4e2 wave=W6 phase=P6.1 layer=L2 fan_in=1 surface=None coverage_gap_pct=10.0 est_tokens=6000 reason=Doctrine sync v33 integration tests writeback`

### Next action

1. Re-enter this plan at W1-P1.3 (wiring), then proceed W2 sandbox hardening.
2. ADG regeneration is NOT required yet — W1 added three modules with no new edges into existing hot code; the next regen will be triggered at the end of W1-P1.3 wiring.
