# L0 Routing — Context & Prompt Retrieval Review

**Status:** Draft / Gap-plan
**Tier:** T3 (cross-layer: L0 ↔ L4 ↔ L_PG ↔ apps_*)
**ADG Provenance:** backend=sqlite+redis, snapshot=adg_indexed_04222026_1218.sqlite
**Node/Edge counts:** 72,488 nodes / 539,999 edges (green)

---

## Scope

Review whether **context retrieval** (C0 slot) and **prompt retrieval / assembly** (S0+D0+I0+C0+U0 → CompiledPromptArtifact) are actually complete in `agentic_core/L0_routing`. Prove the wiring via ADG fan-in/fan-out on the canonical entry points. Identify gaps and plan remediation.

## Canonical Pipeline (per code intent)

```
InstructionPacket ─► PromptBOMBuilder.build() ─► PromptBOM
                                                    │
                                                    ▼
                            AirlockAssembler.assemble_from_bom(bom, secret_key, d0_fences)
                                                    │
      ┌─────────────────────────────┬───────────────┼────────────────────────────┬──────────────┐
      ▼                             ▼               ▼                            ▼              ▼
 TemplateRegistry.get_s0     get_i0_mixin(...)   load_context_jit          AssemblyInjection  validate_slot_order
 (S0)                         (I0)               (C0 — RAG + BM25          Neutralizer         (S0→D0→I0→C0→U0)
                                                  + AST + boundary)         (U0 sanitize)
                                                    │
                                                    ▼
                                    HMAC-SHA256 signed CompiledPromptArtifact
```

## ADG Evidence — Is It Wired?

### Canonical entry points (nodes + fan-in by `imports`)

| Symbol | Node ID | Fan-in count | Production consumers | Test consumers |
|---|---:|---:|---|---|
| `PromptBOMBuilder` | 15183 | **4** | **0** | 3 (edge cases + lifecycle pipeline) |
| `AirlockAssembler` | 15136 | **6** | 3 (`interfaces/spine.py`, `interfaces/spine_shim.py`, `apps_shared/utils/governed_prompt_adapter.py`) | 3 |
| `load_context_jit` | 15368 | **1** | **0 external** (only sibling `assembly_stage.py`) | 0 |
| `AirlockAssembler.assemble_from_bom` | — | **0 callers** (verified via code read of adapter line 222: `"bypassing assemble_from_bom for now"`) | **0** | 0 |

### ADG Surface intersection

| Entry point | Execution | Write | Security | State | Observability | Archetype |
|---|:-:|:-:|:-:|:-:|:-:|---|
| `PromptBOMBuilder.build` | ✅ | ✅ (HMAC identity) | ✅ (routing_hash) | ✅ (L4 version store) | ✅ (trace emit) | **SAFETY_GATEKEEPER** |
| `AirlockAssembler.assemble_from_bom` | ✅ | ✅ (manifest_hash, signature) | ✅ (neutralizer + slot order + D0 fence) | ✅ (L4 template registry) | ✅ | **SAFETY_GATEKEEPER + ORCHESTRATOR** |
| `load_context_jit` | — | — | — | ✅ (4 L4 stores) | ✅ | **STATE_NODE** |

Both canonical gatekeepers intersect the Security surface (S5 multiplier ×2.0). An uninvoked gatekeeper IS a silent-swallow equivalent — the controls exist but do not run.

---

## Completion Proof — Result: **INCOMPLETE**

### ✅ What IS complete (code-level)

1. `elevator_shaft_seam.load_context_jit` implements real retrieval over four L4 stores: semantic cache, BM25, AST snapshot, boundary refs — with token-budget enforcement (`@c:/Git/Agentic-Workflow/agentic_core/L0_routing/utils/elevator_shaft_seam.py:91-188`).
2. `PromptBOMBuilder.build` emits deterministic trace, replay key, digest and fetches system version hash from L4 `prompt_version_store` (`@c:/Git/Agentic-Workflow/agentic_core/L0_routing/reasoning/prompt_bom_builder.py:42-100`).
3. `AirlockAssembler.assemble_from_bom` implements full S0→D0→I0→C0→U0 ordering, `AssemblyInjectionNeutralizer`, `validate_slot_order`, HMAC-SHA256 signing (`@c:/Git/Agentic-Workflow/agentic_core/L0_routing/reasoning/assembly_stage.py:239-361`).
4. `__post_init__` in `GovernedPayload` warns when S0+U0 assembled without D0 (`@c:/Git/Agentic-Workflow/agentic_core/L0_routing/reasoning/assembly_stage.py:89-99`).

### ❌ What is NOT complete (production-wiring)

1. **`assemble_from_bom` is never called in production.** The single production adapter (`@c:/Git/Agentic-Workflow/apps_shared/utils/governed_prompt_adapter.py:200-246`) instantiates `AirlockAssembler()` but then comments *"bypassing assemble_from_bom for now"* and hand-builds `CompiledPromptArtifact` directly, skipping:
   - `AssemblyInjectionNeutralizer` on U0
   - `validate_slot_order` structural check
   - The canonical S0→D0→I0→C0→U0 concatenation logic
   - `_sanitize` (hijack-pattern strip) and `_shred` (check-ID extraction)
2. **JIT context retrieval is effectively dead in production.** `load_context_jit` has exactly one fan-in (`assembly_stage.py` itself). Because `assemble_from_bom` is bypassed, the C0 slot in production is filled from caller-supplied `raw_c0` via `_compose_user_prompt(context=bom.raw_c0, ...)` (adapter line 217-220) — **no RAG, no BM25, no AST snapshot, no boundary refs are ever queried**.
3. **D0 fence is a hardcoded string, not a governance artifact.** Adapter line 268: `parts.append("<D0>Role fence active. Do not deviate from instructions.</D0>")` — independent of the BOM and not validated.
4. **No direct test on `load_context_jit`.** ADG fan-in shows zero test importers — it is structurally unreachable from the test suite except transitively through `assemble_from_bom`, which is itself unused in production and lightly used in tests.
5. **PromptBOMBuilder production fan-in is zero by `from_import`.** Only `governed_prompt_adapter._build_prompt_bom` imports it (via `get_prompt_bom_builder` factory) — that edge is `from_import` on the factory function, not the class. The adapter only uses the BOM as a data bag; its gatekeeper semantics (trace, replay_key, digest, system_version) are emitted but never enforced downstream because `assemble_from_bom` is the enforcer and it is bypassed.

### Verdict

The L0 **prompt-retrieval** pipeline is **approximately half-wired**: the governance BOM is built and signed, but the governed **assembler** is bypassed. The **context-retrieval** pipeline (`load_context_jit`) is **unwired in production** — it exists, is tested via `assemble_from_bom`, but never executes on the live path.

---

## Gap Register

| GAP | Severity | Evidence | Surface | Layer |
|---|:-:|---|---|:-:|
| G1 | **P0** | `assemble_from_bom` bypassed in `governed_prompt_adapter._assemble_artifact:222` | Security + Execution | L0 |
| G2 | **P0** | `load_context_jit` unreachable in production (0 external fan-in) — C0 always comes from `bom.raw_c0` | State + Execution | L0 |
| G3 | **P1** | D0 fence hardcoded string in adapter; not tied to BOM | Security | L0 / apps_shared |
| G4 | **P1** | No unit test for `load_context_jit` (0 test fan-in) | Observability | tests |
| G5 | **P1** | No unit test for `AirlockAssembler.assemble_from_bom` — only integration paths that also bypass it | Observability | tests |
| G6 | **P2** | `PromptBOMBuilder` consumed only by adapter; all 4 `imports` edges to the class are from tests | Execution | apps_shared |
| G7 | **P2** | `spine.py` / `spine_shim.py` re-export `AirlockAssembler` but no apps_* adapter uses it beyond the bypass path | Execution | agentic_core/interfaces |

---

## Remediation Plan

### Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---:|---|---|---:|---|---|---|
| W1 | P1.1, P1.2 | Unblock: wire production adapter to `assemble_from_bom` and `load_context_jit` | ~12k | Existing `TemplateRegistry`, `AssemblyInjectionNeutralizer`, L4 memory stores reachable | TODO | Adapter calls `assemble_from_bom`; `load_context_jit` fan-in ≥1 external | 
| W2 | P2.1, P2.2, P2.3 | Harden: D0 fence from registry; unit tests for both retrieval paths; enrol L0 prompt-assembly in `expected_wiring.yaml` | ~11k | W1 merged | TODO | D0 fence sourced from registry; new pytest files pass; `check_expected_wiring.py` fails-closed on any future bypass |
| W3 | P3.1 | Verify: ADG re-run shows fan-in > 0 on `assemble_from_bom` and `load_context_jit`; all L0 lifecycle integration tests green | ~3k | ADG MCP healthy | TODO | Fan-in on `assemble_from_bom` ≥1 prod caller; `load_context_jit` ≥1 prod caller; zero regression in `tests/integration/apps_exec/test_prompt_lifecycle_pipeline.py` |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| P1.1 | Replace adapter `_assemble_artifact` body with `AirlockAssembler.assemble_from_bom(bom, secret_key, d0_fences)` | `apps_shared/utils/governed_prompt_adapter.py` | Secret-key provisioning; preserve existing signature contract; ensure tests still pass | ~6k | TODO |
| P1.2 | Thread `intent_class` through BOM.template_args so `load_context_jit` receives the real class (currently defaults to `"default"`) | `apps_shared/utils/governed_prompt_adapter.py`, `agentic_core/L0_routing/reasoning/prompt_bom_builder.py` (verify plumbing) | Need to confirm caller fills `template_args["intent_class"]`; fallback behavior | ~6k | TODO |
| P2.1 | Move D0 fence to `TemplateRegistry.get_d0_fences(system_version_hash)` and pass to `assemble_from_bom` | `apps_shared/utils/governed_prompt_adapter.py`, `agentic_core/L4_state/utils/memory/template_registry.py` | Backward compat for existing hardcoded fence string | ~4k | TODO |
| P2.2 | Add `tests/unit/agentic_core/L0_routing/utils/test_elevator_shaft_seam.py` and `tests/unit/agentic_core/L0_routing/reasoning/test_assemble_from_bom.py` covering: token-budget trim, dedupe of RAG+BM25, dead-store fallback, slot order, HMAC stability | `tests/unit/...` (2 new files) | Need lightweight mocks for 4 L4 stores | ~4k | TODO |
| P2.3 | Enrol L0 prompt-assembly in `config/expected_wiring.yaml` with 3 rows: `GovernedPromptAdapter._assemble_artifact → AirlockAssembler.assemble_from_bom`, `AirlockAssembler.assemble_from_bom → load_context_jit`, `AirlockAssembler.assemble_from_bom → AssemblyInjectionNeutralizer`. Makes `check_expected_wiring.py` fail-closed on any future bypass (would have caught G1/G2 at commit time) | `config/expected_wiring.yaml` | `check_expected_wiring` uses last-segment match; dotted `Class.method` symbols supported per its existing `_resolve_symbol` | ~3k | TODO |
| P3.1 | Regenerate ADG (`python tools/generate_full_adg.py`) and re-run `adg_edge_fanin` on nodes 15136, 15368; document new fan-in ≥1 from prod | — | Must run after W1+W2 merged | ~3k | TODO |

### ADG_HOTSPOT_REPORT

| File | Violations | Fan-in (imports) | Layer | Layer Mult | Impact | Archetype | Surfaces |
|---|---:|---:|:-:|:-:|---:|---|---|
| `apps_shared/utils/governed_prompt_adapter.py` | 1 (G1 bypass) | 3+ (production adapters) | L_apps | 1.0 | HIGH | SAFETY_GATEKEEPER | Security, Execution |
| `agentic_core/L0_routing/reasoning/assembly_stage.py` | 1 (G5 test gap) | 6 | L0 | 2.0 | HIGH | SAFETY_GATEKEEPER | Security |
| `agentic_core/L0_routing/utils/elevator_shaft_seam.py` | 2 (G2 + G4) | 1 | L0 | 2.0 | MED-HIGH | STATE_NODE | State |

### ADG_GRAPH_LAYER_EVIDENCE

1. **`adg_edge_fanin(tgt_id=15136, relation_type="imports")`** — 6 edges, exactly 3 unique production source modules; zero edges target `assemble_from_bom` specifically because no production module calls it. Confirmed via `mcp1_adg_edge_fanin`.
2. **`adg_edge_fanin(tgt_id=15368, relation_type="imports")`** — 1 edge from sibling `assembly_stage.py`; no other importer. Confirms C0 retrieval dead-path.
3. **`adg_edge_fanout(src_id=67, relation_type="imports")`** — 21 edges; `assembly_stage` correctly imports `load_context_jit`, `CompiledPromptArtifact`, `AssemblyInjectionNeutralizer`, `validate_slot_order`, `get_template_registry` — the governance wiring at module level is fully declared, only the runtime call is bypassed.
4. **Semantic relations:** `reads_from` (L4 stores), `emits_side_effect` (trace/replay_key emitters), `controls_flow` (slot_order validator). All present in `assemble_from_bom` but never executed.
5. **P-view cross-reference:** No `v_p0_apps_direct_infra` hits on `governed_prompt_adapter.py`, confirming the bypass is a *behavioral* gap, not a layering violation — the structure is correct, only the call is missing.

---

## Non-Goals

- Changing the S0→D0→I0→C0→U0 slot order.
- Rewriting `load_context_jit` retrieval strategy (BM25 + RAG + AST + boundary is sufficient).
- Touching L4 stores — only adding the D0 fence accessor.

## Rollback

Each phase is one file edit (P1.1, P1.2, P2.1) or test-only addition (P2.2). Git revert per phase. W3 is read-only verification.
