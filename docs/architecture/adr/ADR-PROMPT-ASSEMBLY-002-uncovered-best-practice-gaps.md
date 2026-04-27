# ADR-PROMPT-ASSEMBLY-002 — Uncovered best-practice gaps

- **Status**: **Accepted** 2026-04-23
- **Decision Date**: 2026-04-23 (approved by user same-day)
- **Deciders**: Cascade + user (implementation mode execution of plan `prompt-assembly-best-practices-gap-b4e1c2`). Author-Gate resolution: `DECISION_CAPTURED: type=architecture_choice, selected=adopt-ADR-PA-002-and-launch-EQ1, confidence=0.90, outcome=executed`.
- **Impact Layers**: L0, L2, L4, L5, L_PG, L_KR, L_SHARED, L_TOOLS
- **Plan**: `.windsurf/plans/prompt-assembly-best-practices-gap-b4e1c2.md`
- **Supersedes / complements**: `ADR-PROMPT-ASSEMBLY-001` (provider-aware
  structured prompt rendering). ADR-001 resolved Q1/Q2/Q3/Q4 (slot order, provider
  adapter contract, long-context composition, structured-output schema source).
  This ADR closes the remaining gaps G5, G6, G7, G10–G16, G19, G22, G23.

## 1. Context

Gap analysis against Anthropic Claude 4, OpenAI GPT-4.1 / o-series, and Google
Gemini 3 prompting best practices identified 23 gaps in the current prompt
assembly pipeline. ADR-001 covers 8 (G1 doc-alignment implicitly, G2, G3, G4,
G8, G9, G17, G18, G20 partially). This ADR consolidates the remaining 14 into
a single execution plane with shared invariants, so implementation waves
(W3–W8 of the gap plan) have one authoritative source.

## 2. Decision summary

Adopt the following twelve coupled changes. All preserve replay determinism
(manifest hash over canonical slot payload, not rendered string) and cache
stability (S0+D0+I0 prefix remains identity-stable).

| § | Change | Closes gap | Layer of impact |
|---|--------|-----------|-----------------|
| 3 | Grounding-in-quotes directive as default I0 mixin for RAG-heavy intents | G5 | L_PG |
| 4 | Agentic standing-reminder mixin `I0_AGENTIC_STANDING_V1` | G6 | L_PG, L_TOOLS |
| 5 | Model-self-knowledge mixin `I0_MODEL_IDENTITY_V1` | G15 | L_PG, L0 |
| 6 | Provider-aware token counter with deterministic fallback | G7 | L_KR, L0 |
| 7 | Conversation-history compressor (deterministic rule-based) | G11 | L_KR, L_PG |
| 8 | Deterministic token-budget eviction policy | G12 | L_KR, L_PG |
| 9 | Idempotency nonce on `CompiledPromptArtifact` | G10 | L0, L5 |
| 10 | Prompt-cache prefix discipline + boundary documentation | G14 | L_PG, L2 |
| 11 | Thinking-depth knob on routing meta (not prompt body) | G16 | L0, L2 |
| 12 | Context-reliance directive parameterization | G19 | L_PG |
| 13 | Parallel-tool-call caveat switch on AgentSpec | G22 | L2, L_SHARED |
| 14 | Apply-patch diff convention for code-editing agents | G23 | L_SHARED, `apps_rg` |

## 3. G5 — Grounding-in-quotes default directive

Anthropic recommends, for long-document tasks, that the model **quote relevant
spans first** before answering. Add a new I0 mixin:

- **ID**: `I0_GROUND_IN_QUOTES_V1`
- **Text** (canonical):
  > For each answer that relies on the provided documents, first quote the
  > exact spans from `<document_content>` blocks that support your answer under
  > a `<quotes>` section, then produce your final answer under `<answer>`. Do
  > not answer from memory when documents are present.
- **Activation rule**: auto-injected when `PromptEnvelope.must_use_chunks` is
  non-empty **and** `sum(len(c.content) for c in must_use) > 4 000 chars`.
  Suppressed for o-series reasoning models (reasoning is internal).
- **Conflict rule**: suppressed when `AgentSpec.response_schema` requires a
  strict JSON object without a `quotes` field (a follow-on wave may emit a
  companion schema variant).

## 4. G6 — Agentic standing-reminder mixin

OpenAI GPT-4.1 guide: including three standing reminders (persistence, tool
use, planning) improved SWE-bench pass rate ~20%. Adopt as a single mixin:

- **ID**: `I0_AGENTIC_STANDING_V1`
- **Text** (canonical, three stanzas):
  1. **Persistence** — "You are an agent. Keep going until the user's request
     is fully resolved. Only end your turn when you are sure the task is done."
  2. **Tool-first** — "If you are uncertain about file contents, codebase
     structure, or external state, use your tools to gather the information.
     Do not guess or fabricate answers."
  3. **Plan-then-act** — "Before each tool call, plan the action briefly. After
     each tool call, reflect on the outcome before planning the next. Do not
     resolve the task purely by chaining tool calls with no planning."
- **Activation rule**: auto-injected when `AgentSpec.is_agentic == True`
  (capability flag). Suppressed for pure single-turn Q&A (`is_agentic=False`).
- **Claude 4.6+ compatibility**: the persistence stanza duplicates Claude's
  training defaults; retain anyway for cross-provider uniformity.
- **o-series compatibility**: the plan-then-act stanza is inert (reasoning is
  internal) but harmless; retain for uniformity.

## 5. G15 — Model self-knowledge mixin

Anthropic recommends telling Claude its identity and exact model string when
the application needs the model to identify itself correctly.

- **ID**: `I0_MODEL_IDENTITY_V1`
- **Text template** (rendered from routing meta, not hard-coded):
  > `The assistant is {provider_display_name}, served by {vendor}. The active
  > model identifier is {model_id}. When asked which model you are, respond
  > with exactly this identifier.`
- **Activation rule**: opt-in per `AgentSpec.expose_model_identity: bool`
  (default `False`). When `True`, assembler pulls `{provider_display_name,
  vendor, model_id}` from routing metadata.

## 6. G7 — Provider-aware token counter

Current estimators (`len//4`, `words/0.75`) drift ~15–25% from true model
tokens, making budget-trim decisions unreliable.

- **Interface** — `agentic_core/prompt_governance/core/token_counter.py`:
  ```
  class TokenCounter(Protocol):
      def count(self, text: str, *, vendor: str, model: str) -> int: ...
  ```
- **Adapters**:
  - `TikTokenCounter` — wraps `tiktoken`; used for OpenAI models.
  - `AnthropicTokenCounter` — wraps `anthropic.messages.count_tokens`
    (lightweight endpoint).
  - `GeminiTokenCounter` — wraps `google.genai.Client.models.count_tokens`.
  - `FallbackHeuristicCounter` — `(text_chars + 3) // 4`; used only when the
    vendor adapter import fails. Logs **once** per process at WARNING.
- **Dependency discipline**: all three vendor libs are lazy-imported to avoid
  inflating cold-start cost for call sites that only need the heuristic.
- **Determinism**: counters MUST return the same token count for the same
  `(text, vendor, model)` within a pinned provider SDK version. Vendor-SDK
  upgrades are recorded in a snapshot test (§15).

## 7. G11 — Conversation-history compressor

The PA.1 legacy doc promised "compress multi-turn history contexts"; no
implementation exists. Introduce a deterministic rule-based compressor (no
LLM dependency — preserves replay).

- **Module**: `agentic_core/prompt_governance/core/history_compressor.py`
- **Contract**:
  ```
  @dataclass(frozen=True)
  class ConversationTurn:
      role: Literal["user", "assistant", "tool"]
      content: str
      tokens: int
      turn_index: int
      salience: float   # assigned upstream; higher = keep

  class HistoryCompressor(Protocol):
      def compress(
          self,
          turns: tuple[ConversationTurn, ...],
          budget_tokens: int,
          *,
          vendor: str,
          model: str,
      ) -> tuple[ConversationTurn, ...]: ...
  ```
- **Default rule-based policy**:
  1. Always keep the last `k_recent` turns (default 4).
  2. Always keep turns with `salience >= 0.8` (flagged upstream as must-keep).
  3. Evict remaining turns oldest-first until `sum(tokens) <= budget_tokens`.
  4. If still over budget, evict assistant turns before user turns among
     remaining candidates, still oldest-first.
  5. Never evict a `tool` turn separately from its paired `assistant` turn.
- **Optional later**: LLM-summarizer with hash-stable prompt (non-default;
  requires DEFERRED_SCOPE wave). Not in this ADR.
- **Envelope integration**: `PromptEnvelope` gains a `convo_history: tuple[
  ConversationTurn, ...]` field (default empty tuple). PA.4 pipeline calls
  `HistoryCompressor.compress` **before** fallback eviction on chunks.

## 8. G12 — Deterministic token-budget eviction

Current code flags overflow but does not trim. Specify a deterministic eviction
policy that is hash-stable under replay:

1. **Fixed slot order** — evict in this order only, stopping when
   `total_tokens <= budget - output_reserve`:
   1. Conversation-history turns (delegated to `HistoryCompressor`).
   2. Lowest-`salience` optional `C0` chunks (must-use chunks are immovable).
   3. Lowest-`salience` `E0` exemplars.
   4. Synthesis `Y0` content (lowest-priority analytic signal).
   5. **Never** evict `S0`, `D0`, `I0`, `U0`, `H0`, `R0`.
2. **Tie-break** — within the same salience band, evict by stable field
   `(turn_index | chunk_id | exemplar_id)` ascending (oldest/smallest first).
3. **Overflow hard-fail** — if budget cannot be met after step (1–4),
   `PromptAssemblyStatus.status = OVERFLOW` and assembly aborts; routed to
   HITL/refine. No silent dispatch with truncated must-use chunks.
4. **Replay determinism** — eviction decisions are logged as a
   `PruneManifest` (ordered list of evicted IDs); manifest hash includes the
   pruned slot payload only.

## 9. G10 — Idempotency nonce

The legacy doc promised an idempotency nonce; current code only signs the
deterministic manifest hash. Add:

- **Field** — `CompiledPromptArtifact.idempotency_nonce: str` (UUID4 hex).
- **Hash exclusion** — nonce is **not** included in `manifest_hash` inputs.
  It IS included in the HMAC signature inputs (so forgery still requires the
  secret). Verifier rejects artifacts where
  `HMAC(secret, slot_bytes || nonce) != signature`.
- **Use** — gateway uses `(manifest_hash, idempotency_nonce)` as a duplicate-
  dispatch guard: same hash + same nonce within replay window = dedup hit;
  same hash + different nonce = legitimate re-dispatch (e.g., retry after
  network failure).
- **Back-compat** — shim accepts unsigned-nonce artifacts for 90 days; after
  the cutover date, nonce is required.

## 10. G14 — Prompt-cache prefix discipline

Anthropic (`cache_control` markers) and OpenAI (automatic prefix cache) both
benefit from identity-stable prefixes. Lock the discipline:

1. **Prefix boundary** — `S0 + D0 + I0` forms the cached prefix. No dynamic
   content is permitted in these slots once assembled.
2. **Cache-control markers** — Anthropic adapter emits `cache_control:
   {"type": "ephemeral"}` on the last content block of each S0, D0, I0 group.
   OpenAI adapter relies on automatic prefix caching; no explicit marker.
3. **Assembly guarantees** — assembler enforces that `I0` mixin order is
   derived from `sorted(bom.mixins_required)` (already true) and that
   per-mixin text is registry-sourced (already true) so identical BOMs
   produce identical prefixes byte-for-byte.
4. **Violation detection** — CI gate `check_cache_prefix_stability.py` (new)
   diffs S0/D0/I0 byte strings across two renders of the same BOM; any drift
   is a failure.

## 11. G16 — Thinking-depth knob on routing meta

Thinking controls are vendor-native and MUST live on routing metadata, never
in the prompt body (per invariant #9).

- **Field** — `RoutingMeta.thinking_level: Literal["none", "low", "medium",
  "high"]` (default `"medium"`).
- **Adapter mapping**:
  - Anthropic: maps to `thinking: {type: "enabled", budget_tokens: N}` where
    `N ∈ {0, 4096, 16384, 65536}` per level.
  - OpenAI (o-series): maps to `reasoning.effort ∈ {none, low, medium, high}`.
  - OpenAI (GPT-4.1): no-op (standard model).
  - Gemini 3: maps to `thinking_level` API field directly.
- **Authority** — routing layer sets the level; AgentSpec can cap the max but
  cannot raise it above the route default.

## 12. G19 — Context-reliance directive

OpenAI guide recommends explicit control over internal-vs-external knowledge
mix. Parameterize `D0` via two canonical fences:

- `D0_CONTEXT_ONLY` — "Only use the documents in the provided context to
  answer. If you cannot answer from this context, respond 'I do not have the
  information needed to answer that.'"
- `D0_CONTEXT_PLUS_INTERNAL` — "Prefer the provided context. You may use your
  own knowledge only to connect concepts or fill minor gaps, and you must
  flag any such addition with a `[model-knowledge]` tag."
- **Default** — `D0_CONTEXT_ONLY` for all retrieval-backed intents
  (`intent_class ∈ {rag, research, rfp, evaluation, underwriting}`);
  `D0_CONTEXT_PLUS_INTERNAL` otherwise.

## 13. G22 — Parallel-tool-call caveat switch

OpenAI observes rare parallel-tool anomalies; expose the knob per AgentSpec.

- **Field** — `AgentSpec.parallel_tool_calls: bool` (default `True`).
- **Adapter** — provider adapter sets the API `parallel_tool_calls` flag
  (OpenAI) or equivalent (Anthropic/Gemini) from this field.
- **Violation detection** — trajectory grader flags anomalies; auto-suggests
  flipping to `False` for the next replay.

## 14. G23 — Apply-patch diff convention (code-editing agents)

For `apps_rg` and any future code-editing app, adopt OpenAI's apply-patch
format for emitted edits:

- **Output contract** — code edits MUST be emitted as a single fenced diff
  block following the apply-patch schema (`*** Begin Patch / *** End Patch`
  envelope with file headers and hunks).
- **Schema** — new `R0` variant `apply_patch_v1.json` with a tight regex
  check on the envelope.
- **Validator** — `agentic_core/prompt_governance/security/validators/
  apply_patch_validator.py` (new) verifies syntactic integrity before the
  artifact leaves L2.
- **Rejected alternatives** — free-form prose diffs (regex-fragile), pure
  JSON file-by-file replacement (token-expensive for small edits).

## 15. Consequences

### Positive
- Gap closure — all 14 remaining gaps from the parent plan specified in a
  single authoritative ADR.
- Deterministic budget decisions (provider-aware counter + hash-stable
  eviction + rule-based history compression).
- Cache hit rate improves measurably on Anthropic adapter (explicit markers
  on stable prefix boundaries).
- Artifact replay discipline strengthens (nonce separates retry from forgery).
- Thinking controls stop polluting prompt body, freeing tokens and removing
  model-specific prompt branches.
- `apps_rg` gains a regression-resistant code-edit output contract.

### Negative / Risks
- Three new vendor SDK dependencies (`tiktoken`, `anthropic`, `google-genai`)
  enter the critical path. Mitigation: lazy imports + deterministic fallback
  counter with single WARNING.
- `PromptEnvelope` schema extension (`convo_history` field) is a mild
  signature change; 90-day shim for old-envelope consumers.
- `CompiledPromptArtifact` signature-inputs change (nonce added to HMAC
  inputs). Same 90-day shim.
- Two new CI gates (`check_cache_prefix_stability.py`,
  `check_apply_patch_schema.py`) add ~1 s per full gate run.
- Matrix tests (Anthropic × OpenAI × Gemini) triple the golden-render count
  for touched paths.

### Neutral
- `OUTPUT RESERVE` token reserve value becomes a documented routing-meta
  parameter instead of an implicit constant.
- Parallel-tool-calls default remains `True` — no behavior change unless
  specifically disabled.

## 16. Execution plan

Executed under parent plan `.windsurf/plans/prompt-assembly-best-practices-gap-b4e1c2.md`:

| Wave | ADR § | Phases |
|------|-------|--------|
| W3 (standing reminders) | §3, §4, §5 | 3.1, 3.2, 3.3 |
| W4 (budget + compression) | §6, §7, §8 | 4.1, 4.2 |
| W6 (integrity + cache + directives) | §9, §10, §12 | 6.1, 6.2 |
| W7 (regression tests) | §11, §13, §14 | 7.1, 7.2 |

## 17. References

- Parent plan: `.windsurf/plans/prompt-assembly-best-practices-gap-b4e1c2.md`
- Sibling ADR: `docs/architecture/adr/ADR-PROMPT-ASSEMBLY-001-provider-aware-structured-prompt-rendering.md`
- Sibling plan: `.windsurf/plans/prompt-assembly-reception-hardening-9c4e2b.md`
- Vendor best-practices: `docs/reference/_primers/prompting/{anthropic,openai,gemini}_best_practices_2026.md`
- Cross-map: `docs/reference/_primers/prompting/current_architecture_crossmap.md`
- Refreshed prompt-assembly doc: `docs/reference/03_L0_Routing/Prompt Assembly/Prompt Assembly.md`
