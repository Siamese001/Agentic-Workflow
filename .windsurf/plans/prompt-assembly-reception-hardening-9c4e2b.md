# Plan: Prompt Assembly Reception Hardening

- **Slug**: `prompt-assembly-reception-hardening-9c4e2b` (supersedes `prompt-assembly-few-shot-exemplars-9c4e2b`)
- **Tier**: T3 (cross-layer: L0 assembly, L2 gateway, L4 mixins/exemplars, L5 governance, `apps_*/config`, `infrastructure/sdks_mcps`)
- **Status**: Todo — Author-Gate design decisions locked 2026-04-23
- **Parent Plan Summary**: Close the prompt-reception gap where the LLM receives an undifferentiated `\n\n`-joined blob of S0+D0+I0+C0 instead of structurally distinguishable content. Align the 9-category SSOT (`docs/reference/03_L0_Routing/Prompt Assembly/Agentic Prompt Categories.txt`) with current Anthropic (Claude Opus 4.7) and OpenAI (GPT-4.1 + o-series) prompting best practice by (a) adding missing slots E0/M0/H0, (b) routing structured slots through to provider adapters which render per-provider, and (c) gating reception quality in CI.

## Research Basis

- `@c:/Git/Agentic-Workflow/docs/reference/prompting/anthropic_best_practices_2026.md` — XML tagging, long-context at top, `<thinking>`/`<answer>`, adaptive thinking, `<example>` wrapping, role priming.
- `@c:/Git/Agentic-Workflow/docs/reference/prompting/openai_best_practices_2026.md` — instruction hierarchy (developer > system > user), GPT-4.1 recommended skeleton (Role → Instructions → Reasoning → Output Format → Examples → Context → Final), o-series diverging rules, Structured Outputs.
- `@c:/Git/Agentic-Workflow/docs/reference/prompting/current_architecture_crossmap.md` — 30-technique scorecard; 22 of 30 currently missing.

## Author-Gate Decisions (locked 2026-04-23)

| # | Decision | Outcome | Confidence |
|---|---|---|---|
| Q1 | META-COGNITIVE slot shape | Separate M0 slot between C0 and U0 | 0.88 |
| Q2 | Provider-adapter contract | Adapters receive structured slots; render per provider | 0.93 |
| Q3 | Long-context composition | Per-provider adapter with shared tail-repeat default | 0.89 |
| Q4 | Structured-output schema source | AgentSpec is the SSOT for `response_schema` | 0.90 |

## Goal

Every LLM call leaving `SovereignLLMGateway.generate` is provider-idiomatically rendered from a structured `CompiledPromptArtifact`, with:

- Anthropic providers receiving XML-tagged content (`<instructions>`, `<context>`, `<examples>`, `<thinking>`, `<documents>/<document>`) and `system=<role>` parameter set.
- OpenAI providers receiving correct role splits (developer for D0 on o-series, system for S0+I0, user for U0+C0) plus markdown section headings.
- All 9 SSOT prompt categories represented by an assembler slot.
- `response_schema` enforced from AgentSpec where declared.

## Scope

| In Scope | Out of Scope |
|---|---|
| Assembler slot-order change `S0→D0→I0→E0→C0→M0→U0→H0` | Dynamic few-shot selection via embeddings (future) |
| `CompiledPromptArtifact` schema extension | Rewriting existing YAML injection corpus content |
| Provider adapters in `infrastructure/sdks_mcps/` — Anthropic + OpenAI (GPT-4.1) + o-series | Third-party providers (Gemini, etc.) — follow in later wave |
| AgentSpec `response_schema` field + governance load-time validation | Migrating all agents to structured output simultaneously |
| CI gates: reception coverage, XML tag coverage, schema coverage, conflict linter | Meta-prompt authoring tooling |
| Migration shim preserving replay-key determinism | Manifest-hash backward compat beyond migration window |

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| **W1** | RH1.1, RH1.2 | Reception audit — instrument gateway + assembler | 4000 🟢 | Todo | Evidence report at `docs/reports/plans/prompt_reception_audit.md` quantifying per-slot bytes across all `apps_*` providers |
| **W2** | RH2.1, RH2.2, RH2.3 | Structured artifact + per-provider adapters | 14000 🟡 | Todo | `CompiledPromptArtifact` carries structured slots; Anthropic + OpenAI adapters render per vendor docs; replay-key determinism preserved |
| **W3** | RH3.1, RH3.2, RH3.3 | Missing slots: E0 (exemplars), M0 (meta-cognitive), H0 (healing re-entry) | 10000 🟡 | Todo | Slot-order validator accepts new 8-slot order; `GovernedPayload` extended; all assembly sites migrated |
| **W4** | RH4.1, RH4.2 | Exemplar bank (original narrow-plan scope preserved) | 6000 🟢 | Todo | `agentic_core/L4_state/exemplars/` module; ≥3 examples per eligible prompt; assembly gate rejects offenders |
| **W5** | RH5.1, RH5.2, RH5.3 | Reception gates + CI + AgentSpec response_schema | 8000 🟡 | Todo | 4 CI gates wired to pre-commit + `run_contract_gates.py`; golden-replay test green against Anthropic + OpenAI |

**Total**: ~42000 tokens. 🟢 < 5k, 🟡 5k-15k, 🔴 > 15k.

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| RH1.1 | Gateway instrumentation | `SovereignLLMGateway.py` (lines 558-565, 653-660) | Must not change behavior; log-only | 2000 | Todo |
| RH1.2 | Assembly-site crawl + report | All `apps_*/engines/*assembly*.py`, `agentic_core/L0_routing/**` | Counting sites accurately | 2000 | Todo |
| RH2.1 | `CompiledPromptArtifact` structured form | `compiled_artifact_types.py`, `slot_assembly_engine.py` | Replay-key / HMAC determinism | 4000 | Todo |
| RH2.2 | Anthropic adapter with XML rendering | `infrastructure/sdks_mcps/` (new adapter file) | `<thinking>` + adaptive thinking passthrough | 5000 | Todo |
| RH2.3 | OpenAI adapter with role-split rendering | `infrastructure/sdks_mcps/` (new adapter file) | developer-vs-system routing for o-series; `Formatting re-enabled` header | 5000 | Todo |
| RH3.1 | Add E0 slot + exemplar XML wrapping | `assembly_stage.py`, `validate_assembly.py` | Slot-order validator update | 3000 | Todo |
| RH3.2 | Add M0 slot + CoT scaffolds | `assembly_stage.py`, new `meta_cognitive_templates.yaml` | Default CoT per AgentSpec | 4000 | Todo |
| RH3.3 | Add H0 slot + healing re-entry channel | `assembly_stage.py`, L2.3 healer integration | Re-entry manifest-hash continuity | 3000 | Todo |
| RH4.1 | Exemplar bank schema + retrieval API | `agentic_core/L4_state/exemplars/` (new module) | Schema design, task-similarity heuristic | 3000 | Todo |
| RH4.2 | Assembly gate: ≥3 exemplars for eligible prompts | `validate_assembly.py`, new `check_exemplar_coverage.py` | False positives on non-eligible categories | 3000 | Todo |
| RH5.1 | `AgentSpec.response_schema` field + governance load | All `apps_*/config/agent_spec_config.py`, `L5_safety` validator | Discriminated-union schemas for dynamic agents | 3000 | Todo |
| RH5.2 | 4 CI gates | `ops_scripts/ci/check_prompt_reception.py`, `check_xml_tag_coverage.py`, `check_response_schema_coverage.py`, `check_prompt_conflicts.py` | Gate baselines without blocking current code | 3000 | Todo |
| RH5.3 | Golden-replay test vs Anthropic + OpenAI | `tests/integration/prompt_assembly/` | Non-determinism of live providers — use frozen fixtures | 2000 | Todo |

## ADG_HOTSPOT_REPORT

Computed from the file touch-set defined above. Ranked by `impact = violation_count × (1 + log10(1 + fan_in)) × layer_multiplier` per `adg-canonical-invariants.md` §6. To be re-verified against live ADG snapshot during W1 (see `ADG_GRAPH_LAYER_EVIDENCE` query list below).

| Rank | File / Symbol | Layer | Archetype | ADG Surface | Expected fan_in | Layer × | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `SovereignLLMGateway.generate` | L2 | CENTRAL_DEPENDENCY | Execution | High (~40+) | 1.0 | Single chokepoint for all LLM traffic; the reception seam |
| 2 | `AirlockAssembler.assemble_from_bom` | L0 | ORCHESTRATOR | Execution | High (~20+) | 2.0 | All prompt assembly flows through here |
| 3 | `CompiledPromptArtifact` | L_PG | STATE_NODE | Write | High (~30+) | 1.75 | HMAC-signed artifact; schema change = replay-key change |
| 4 | `validate_slot_order` | L_PG | SAFETY_GATEKEEPER | Security | Medium (~10+) | 2.0 | Must allow new 8-slot sequence before any W3 work |
| 5 | `AgentSpec` (per `apps_*`) | L_APP | STATE_NODE | Write | Medium-High | 1.0 | ~8 apps_* × config/agent_spec_config.py |

## ADG_GRAPH_LAYER_EVIDENCE

To be populated in **RH1.2** with live queries. Required primitives (per constitutional §22):

**Materialized views** (≥3 required):
- `mv_hotspot_centrality` — rank the 5 hotspots above by closeness centrality
- `mv_graph_chokepoint_bridges` — confirm `SovereignLLMGateway.generate` is a bridge chokepoint
- `mv_graph_critical_path_blast_radius` — blast radius of `CompiledPromptArtifact` schema change
- `mv_dependency_cone_risk` — risk cone for `AirlockAssembler.assemble_from_bom`

**Semantic edges to query**:
- `calls` — who calls `SovereignLLMGateway.generate`, `AirlockAssembler.assemble_from_bom`
- `flows_to` — from `PromptBOM` → `CompiledPromptArtifact` → `final_system_string`
- `reads_from` — AgentSpec readers (to size RH5.1 migration)
- `writes_to` — all assembly-site writers of `GovernedPayload`

**P-views to cross-reference**:
- `v_p0_apps_direct_infra` — confirm no apps_* directly bypass assembler to infrastructure
- `v_p1_mis_layered_infra` — ensure new provider adapters land in `infrastructure/sdks_mcps/` with correct layer
- `v_p2_duplicated_adapters` — avoid creating a fifth adapter-style code path

## Gap Register

| ID | Gap | Wave | Mitigation |
|---|---|---|---|
| G1 | Unknown whether YAML injection corpus uses positive ("do X") vs negative ("don't Y") phrasing (Anthropic A12) | RH5.2 | New lint gate `check_prompt_conflicts.py` scans YAML for negative-phrasing patterns |
| G2 | Replay-key determinism across the Q2 contract change | RH2.1 | Manifest hash inputs must include the structured slots, not the rendered string. Adapter renders are downstream and non-signed. |
| G3 | Prefill deprecation on Claude 4.6+ | RH2.2 | We do not use prefill today; anti-regression: CI forbids adding it |
| G4 | o-series models require `Formatting re-enabled` to emit markdown | RH2.3 | OpenAI adapter injects header when AgentSpec declares `markdown_output=True` |
| G5 | Long-context reorder may confuse existing eval fixtures | RH5.3 | Golden-replay test uses fixtures keyed by provider adapter version |
| G6 | `SynthesisMixin` (SSOT row 7) bypasses assembler today | Deferred | DEFERRED_SCOPE marker (below) |

## Assumptions

1. Current `infrastructure/sdks_mcps/` holds the LLM provider SDK wrappers. Verify during RH1.2.
2. Replay-key format is opaque outside `SovereignLLMGateway`; changing its inputs is allowed as long as determinism per `(trace_id, canonical bom)` is preserved.
3. The 8-slot order `S0→D0→I0→E0→C0→M0→U0→H0` is canonical; downstream consumers read from named slots, not positional indices.

## Out of Scope (Deferred)

DEFERRED_SCOPE: plan=prompt-assembly-reception-hardening-9c4e2b wave=W6 phase=RH6.1 layer=L4 fan_in=8 surface=State coverage_gap_pct=100.0 est_tokens=6000 reason=SynthesisMixin bypass integration with assembler (SSOT row 7)

DEFERRED_SCOPE: plan=prompt-assembly-reception-hardening-9c4e2b wave=W7 phase=RH7.1 layer=L0 fan_in=4 surface=Execution coverage_gap_pct=100.0 est_tokens=8000 reason=Dynamic task-similarity exemplar selection via embedding retrieval

DEFERRED_SCOPE: plan=prompt-assembly-reception-hardening-9c4e2b wave=W8 phase=RH8.1 layer=L2 fan_in=3 surface=Execution coverage_gap_pct=100.0 est_tokens=5000 reason=Gemini and other non-Anthropic-non-OpenAI provider adapters

## Verification / Exit Criteria

- ✅ All 4 CI gates green on main.
- ✅ Golden-replay test asserts: Anthropic call contains `<instructions>`, `<examples>` (when eligible), `<context>`, `<thinking>` tags; OpenAI call sends separate developer/system/user/context messages.
- ✅ `check_prompt_reception.py` reports 0 agent classes failing to receive their AgentSpec-declared slot set.
- ✅ Manifest hash stable for identical `(PromptBOM, secret_key)` pre- and post-adapter-render (adapter output is not part of hash).
- ✅ Zero regressions in existing prompt-assembly unit tests; new tests added per `tests/unit/prompt_assembly/`.

## Writebacks Required on Execution

- **Notion ADR Registry**: new ADR "Provider-aware structured prompt rendering" capturing Q1-Q4 decisions.
- **Notion MCP Registry**: note the new provider-adapter contract so future MCP-triggered prompt debugging can resolve.
- **Memory MCP**: `ProceduralPattern:PromptAssemblyReceptionHardening` entity with the 4 locked decisions and the cross-map doc reference.
- **Notion HITL Decision Ledger**: 4 rows, one per Q1-Q4 Author-Gate resolution.
