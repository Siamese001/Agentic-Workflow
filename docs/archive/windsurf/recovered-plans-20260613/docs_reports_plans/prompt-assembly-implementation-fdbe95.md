# Prompt Assembly Implementation Plan — Parallel Wave Execution

Implement the complete prompt assembly system across four parallel waves: runtime core, template taxonomy, ADG instrumentation, and sovereign gateway, ensuring cross-wave dependencies are mapped and integrated.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | P1-RUNTIME | Core runtime: SlotAssemblyEngine, CompiledPromptArtifact, AuthorityValidator | 198,450 | Base classes exist in L2_execution; authority slots defined in reference docs | YELLOW | Runtime generates signed artifacts; slot assembly order (S0→I0→D0→C0→U0) enforced |
| Wave 2 | P2-TEMPLATES | Template taxonomy: 10 prompt categories, category loaders, TemplateManifest registry | 195,200 | Jinja2 or string.Template available; golden exemplars in L4 State | YELLOW | All 10 categories loadable; TemplateManifest validates required_variables |
| Wave 3 | P3-ADG | ADG instrumentation: PromptLifecycleVisitor, edge emission, lifecycle trace contracts | 201,800 | Static scanner has visitor framework; schema.py has RelationType extensibility | YELLOW | All 6 prompt edge types (generates_prompt, consumes_prompt, etc.) tracked |
| Wave 4 | P4-GATEWAY | Sovereign LLM Gateway: signature verification, provider abstraction, telemetry ledger | 189,300 | HMAC-SHA256 available; provider APIs (OpenAI/Anthropic/Gemini) accessible | YELLOW | Gateway signs/verifies artifacts; provider routing functional |

**Total: 784,750 tokens across 4 waves, all YELLOW**

---

## Gap Register

**GAP-1: No slot assembly runtime**
- Reference defines S0/I0/D0/C0/U0 slot taxonomy with authority gradients, but no runtime implementation exists to assemble slots in order, validate authority hierarchy, or produce CompiledPromptArtifact with HMAC signature.
- Impact: Prompt assembly is ad-hoc; no deterministic slot ordering or authority enforcement.

**GAP-2: Template taxonomy not codified**
- 10 prompt categories defined (User, Instructional, Injections, Exemplars, Dependency, Meta-Cognitive, Synthesis, System/State, Healing Proposal) but no Python classes, loaders, or registry exist to instantiate category-specific templates.
- Impact: Templates are unstructured; no category-specific validation or authority slot assignment.

**GAP-3: Missing ADG prompt lifecycle tracking**
- Reference documents 6 prompt edge types (generates_prompt: 215, consumes_prompt: 11, prompt_template_used_by: 45, reads_policy_state: 1,317, applies_guardrail: 68, retrieves_via: 52) but no visitor emits these edges during static analysis.
- Impact: Prompt assembly flow is invisible in ADG; no provenance for compiled prompts.

**GAP-4: No Sovereign LLM Gateway**
- Reference defines gateway responsibilities (consume signed artifact, translate to provider API, inject D0 stop-sequences, log to Telemetry Ledger) but no implementation exists.
- Impact: No single seam for LLM calls; no signature verification or replayability.

---

## Execution Plan

### Phase 1 — Core Runtime (Wave 1)
**Scope**: Implement SlotAssemblyEngine, CompiledPromptArtifact dataclass, AuthorityValidator, and HMAC signer. Enforce slot order S0→I0→D0→C0→U0. Integrate with existing L5 applies_guardrail hooks.

**New Files**:
- `agentic_core/L2_execution/prompt_assembly/slot_assembly_engine.py` — SlotAssemblyEngine class
- `agentic_core/L2_execution/prompt_assembly/compiled_artifact.py` — CompiledPromptArtifact dataclass + HMAC signer
- `agentic_core/L2_execution/prompt_assembly/authority_validator.py` — AuthorityValidator with hierarchy checks
- `agentic_core/L2_execution/prompt_assembly/__init__.py` — Package exports

**Modified Files**:
- `agentic_core/L5_safety/enforcement/guardrail_router.py` — Integrate authority validation pre-guardrail
- `agentic_core/runtime/lifecycle_trace_contract.py` — Add prompt assembly emitters

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L2_execution/prompt_assembly/ -v --collect-only
python -m pytest tests/unit/agentic_core/L2_execution/prompt_assembly/test_slot_order.py -v
python -m pytest tests/unit/agentic_core/L2_execution/prompt_assembly/test_artifact_signing.py -v
```

**Acceptance**:
- SlotAssemblyEngine.assemble() returns CompiledPromptArtifact with HMAC-SHA256 signature
- AuthorityValidator rejects slots out of order (e.g., U0 before S0)
- All 5 slot types can be added, validated, and serialized

---

### Phase 2 — Template Taxonomy (Wave 2)
**Scope**: Implement 10 prompt category classes with loader, TemplateManifest registry, and category-specific authority slot defaults. Store templates in versioned directory structure.

**New Files**:
- `agentic_core/L4_state/prompt_taxonomy/categories.py` — PromptCategory enum + 10 category classes
- `agentic_core/L4_state/prompt_taxonomy/template_manifest.py` — TemplateManifest dataclass + registry
- `agentic_core/L4_state/prompt_taxonomy/loader.py` — TemplateLoader with category detection
- `agentic_core/L4_state/prompt_taxonomy/__init__.py` — Package exports
- `agentic_core/L4_state/prompt_taxonomy/templates/S0_*.j2` — System/State templates (Absolute)
- `agentic_core/L4_state/prompt_taxonomy/templates/I0_*.j2` — Instructional templates (Governed)
- `agentic_core/L4_state/prompt_taxonomy/templates/D0_*.j2` — Injection templates (Binding)
- `agentic_core/L4_state/prompt_taxonomy/templates/C0_*.j2` — Dependency/Exemplar templates (Info)
- `agentic_core/L4_state/prompt_taxonomy/templates/U0_*.j2` — User prompt templates (Zero)

**Modified Files**:
- `agentic_core/L4_state/__init__.py` — Export taxonomy classes

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L4_state/prompt_taxonomy/ -v --collect-only
python -c "from agentic_core.L4_state.prompt_taxonomy import PromptCategory; print([c.value for c in PromptCategory])"
python -m pytest tests/unit/agentic_core/L4_state/prompt_taxonomy/test_category_loader.py -v
```

**Acceptance**:
- All 10 categories importable and instantiable
- TemplateManifest.validate() checks required_variables against template
- Category loader detects category from template filename prefix

---

### Phase 3 — ADG Instrumentation (Wave 3)
**Scope**: Add PromptLifecycleVisitor to static scanner, emit 6 prompt edge types, extend schema.py with prompt RelationTypes, add lifecycle trace contract emitters.

**Modified Files**:
- `agentic_core/adg/schema.py` — Add PROMPT_RELATION_TYPES frozenset with 6 edge types
- `agentic_core/adg/extraction/static_scanner.py` — Add _PromptLifecycleVisitor (G34) with symbol→edge mapping
- `agentic_core/runtime/lifecycle_trace_contract.py` — Add 6 prompt lifecycle emitters
- `agentic_core/adg/extraction/builder.py` — Wire prompt edges to multi_writer

**New Files**:
- `agentic_core/adg/extraction/visitors/prompt_lifecycle_visitor.py` — Standalone visitor (optional decomposition)

**Commands**:
```bash
python tools/adg/generate_full_adg.py --incremental --focus prompt_edges
python tools/adg/adg_redis_ingest.py --force
python -m pytest tests/unit/agentic_core/adg/extraction/test_prompt_lifecycle_visitor.py -v
```

**Acceptance**:
- _PromptLifecycleVisitor detects generates_prompt from L1 intent functions
- consumes_prompt detected in L2 execution functions
- prompt_template_used_by detected in template loading code
- All 6 edge types appear in ADG SQLite with semantic_type="prompt_lifecycle"

---

### Phase 4 — Sovereign Gateway (Wave 4)
**Scope**: Implement SovereignLLMGateway as single outbound seam with signature verification, provider abstraction (OpenAI/Anthropic/Gemini), stop-sequence injection from D0 slots, and telemetry ledger logging.

**New Files**:
- `agentic_core/L0_routing/gateway/sovereign_llm_gateway.py` — SovereignLLMGateway class
- `agentic_core/L0_routing/gateway/provider_adapters.py` — OpenAIAdapter, AnthropicAdapter, GeminiAdapter
- `agentic_core/L0_routing/gateway/signature_verifier.py` — HMAC-SHA256 sign/verify
- `agentic_core/L0_routing/gateway/telemetry_ledger.py` — TelemetryLedger for determinism/replay
- `agentic_core/L0_routing/gateway/__init__.py` — Package exports

**Modified Files**:
- `agentic_core/L0_routing/__init__.py` — Export gateway classes
- `agentic_core/L5_safety/enforcement/guardrail_router.py` — Route approved prompts to gateway

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L0_routing/gateway/ -v --collect-only
python -m pytest tests/unit/agentic_core/L0_routing/gateway/test_signature_verification.py -v
python -m pytest tests/unit/agentic_core/L0_routing/gateway/test_provider_routing.py -v
```

**Acceptance**:
- Gateway.sign_artifact() produces verifiable HMAC-SHA256 signature
- Gateway.send() routes to correct provider based on artifact metadata
- TelemetryLedger.log() stores final payload with replay key
- D0 stop-sequences injected before provider API call

---

## Cross-Wave Integration Points

| Integration | Source Wave | Target Wave | Contract |
|-------------|-------------|-------------|----------|
| Template → Slot Assembly | Wave 2 (Templates) | Wave 1 (Runtime) | TemplateManifest provides required_variables; SlotAssemblyEngine validates slots |
| Runtime → Gateway | Wave 1 (Runtime) | Wave 4 (Gateway) | CompiledPromptArtifact with HMAC signature passed to SovereignLLMGateway.send() |
| Runtime → ADG | Wave 1 (Runtime) | Wave 3 (ADG) | SlotAssemblyEngine emits lifecycle events captured by _PromptLifecycleVisitor |
| Gateway → Telemetry | Wave 4 (Gateway) | Wave 3 (ADG) | TelemetryLedger writes edges read by L6 observability |

---

## Rules

1. **Wave isolation**: Each wave can develop independently, but integration tests require all 4 waves complete.
2. **Authority hierarchy is absolute**: S0 > I0 > D0 > C0 > U0; no runtime bypass allowed.
3. **ADG edges are mandatory**: Any prompt assembly flow must emit corresponding ADG edges.
4. **Gateway is sole seam**: All LLM calls must route through SovereignLLMGateway; direct provider calls prohibited.
5. **Signatures required**: Every CompiledPromptArtifact must carry HMAC-SHA256 before gateway submission.
6. **Template versioning**: TemplateManifest includes git_commit_hash; template loading validates version compatibility.

---

## Success Criteria

- [ ] SlotAssemblyEngine produces ordered, validated, signed CompiledPromptArtifact
- [ ] All 10 prompt categories loadable with category-specific authority defaults
- [ ] ADG tracks 6 prompt lifecycle edge types with semantic_type="prompt_lifecycle"
- [ ] SovereignLLMGateway signs, verifies, routes, and logs all LLM calls
- [ ] Integration test: full flow from U0 input → signed artifact → provider API → telemetry ledger
- [ ] All 4 waves pass CI with YELLOW token status

---

## Implementation Commands

```bash
# Wave 1: Runtime
python -m pytest tests/unit/agentic_core/L2_execution/prompt_assembly/ -v

# Wave 2: Templates
python -m pytest tests/unit/agentic_core/L4_state/prompt_taxonomy/ -v

# Wave 3: ADG
python tools/adg/generate_full_adg.py --incremental
python tools/adg/adg_redis_ingest.py --force

# Wave 4: Gateway
python -m pytest tests/unit/agentic_core/L0_routing/gateway/ -v

# Integration (all waves complete)
python -m pytest tests/integration/prompt_assembly/full_lifecycle_test.py -v

# Full suite
python -m pytest tests/unit/agentic_core/L2_execution/prompt_assembly tests/unit/agentic_core/L4_state/prompt_taxonomy tests/unit/agentic_core/L0_routing/gateway tests/unit/agentic_core/adg/extraction/test_prompt_lifecycle_visitor.py -v
```

---

## Rollback Strategy

1. **Per-wave checkpoint**: Each wave commits independently; rollback with `git restore --source=HEAD~1 --worktree --staged <wave-files>`
2. **Integration failure**: If cross-wave integration fails, revert to last known good wave checkpoint and re-run integration tests.
3. **ADG corruption**: If ADG regeneration fails during Wave 3, restore from `artifacts/adg/adg_indexed_<timestamp>.sqlite.backup` and re-run visitor.
4. **Gateway leak**: If direct provider calls detected outside gateway, run `grep -r "openai\|anthropic\|gemini" agentic_core/ --include="*.py" | grep -v gateway` to find violations.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---:|---|
| Slot assembly order compliance | 100% | `pytest tests/unit/agentic_core/L2_execution/prompt_assembly/test_slot_order.py` |
| Template category coverage | 10/10 | `python -c "from agentic_core.L4_state.prompt_taxonomy import PromptCategory; assert len(PromptCategory) == 10"` |
| Prompt edge types in ADG | 6/6 | `python tools/adg/query_edges.py --relation-type generates_prompt,consumes_prompt,prompt_template_used_by,reads_policy_state,applies_guardrail,retrieves_via` |
| Gateway signature verification | 100% | `pytest tests/unit/agentic_core/L0_routing/gateway/test_signature_verification.py` |
| Wave token budgets | All YELLOW | `python agentic_core/planning/token_estimator.py --validate docs/reports/plans/prompt-assembly-implementation-fdbe95.md` |
| ADG freshness | HOT | `python tools/adg/adg_redis_ingest.py --status` |

---

## Evidence Notes

- Token estimates computed using ContextWindowEstimator with Kimi K2.5 budget thresholds (WARNING=197K, SAFE=223K, HARD_MAX=262K).
- Wave 1 runtime estimate based on slot assembly complexity (~5 slot types, HMAC operations).
- Wave 2 template estimate based on 10 category classes + Jinja2 template loading.
- Wave 3 ADG estimate based on visitor pattern overhead + 6 edge type emissions.
- Wave 4 gateway estimate based on 3 provider adapters + signature verification + telemetry.
- Reference documentation: `docs/reference/Prompt Assembly/Prompt Lifecycle & Taxonomy.md`, `docs/reference/Prompt Assembly/Agentic Prompt Categories.txt`, `docs/reference/agentic_process_mapping_v25.md`.
