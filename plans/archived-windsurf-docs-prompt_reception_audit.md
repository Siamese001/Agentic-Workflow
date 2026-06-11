---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\prompt_reception_audit.md'
original_relative_path: 'prompt_reception_audit.md'
source_sha256: 4c20d68bfd5841e632d42f660ae4c820295bfb8fd28aa05c710f1ac254c5cb4b
recovered_status: LOST_RECOVERED
last_commit: '47c5a6ff2e6'
last_commit_date: '2026-04-23 07:30:31 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Prompt Reception Audit — W1 Evidence Report

- **Plan**: `@c:/Git/Agentic-Workflow/.windsurf/plans/prompt-assembly-reception-hardening-9c4e2b.md`
- **Wave**: W1 (RH1.1 instrumentation + RH1.2 assembly-site crawl)
- **ADR**: `ADR-PROMPT-ASSEMBLY-001`
- **Date**: 2026-04-23
- **Method**: ADG MCP health (Redis cold, SQLite canonical) + literal grep for constructor / assembler symbols + structural read of gateway seam.

## Headline Findings

1. **The reception seam is confirmed**: two methods on `SovereignLLMGateway`
   (`generate`, `generate_with_reasoning`) hand the provider adapter a pair of
   flat strings (`final_system_string`, `final_user_string`). All slot
   structure is lost at this boundary. Source:
   `@c:/Git/Agentic-Workflow/agentic_core/L2_execution/enforcement/SovereignLLMGateway.py:653-660,558-565`.

2. **Only 2 of 7 production apps currently route through the governed
   assembler** (`AirlockAssembler.assemble_from_bom` or direct
   `CompiledPromptArtifact` construction): `apps_lic` and `apps_rg`.
   The other five apps (`apps_exec`, `apps_research`, `apps_eval`, `apps_rfp`,
   `apps_underwriting_ai`) do not appear as callers of the governed path —
   this is a reception gap independent of the slot-structure problem.

3. **Two parallel `CompiledPromptArtifact` definitions exist** with different
   field shapes:
   - `agentic_core/prompt_governance/contracts/compiled_artifact_types.py` — 6 fields (trace_id, final_system_string, final_user_string, allowed_tools_schema, token_estimate, signature).
   - `agentic_core/L2_execution/reasoning/` (via `SovereignLLMGateway.py` import and `_artifact_from_request` at line 793-808) — richer shape with `slots_used`, `tokens`, `metadata`, `timestamp`, `system_version_hash`.
   This is an SSOT drift that W2 (structured-artifact phase) must resolve.

4. **The final-composition seam is literal**: the assembler joins S0+D0+I0+C0 with `"\n\n".join(...)` at `@c:/Git/Agentic-Workflow/agentic_core/L0_routing/reasoning/assembly_stage.py:343-346`. The instrumented `_reception_audit.py` counts doubled-newlines in the outbound `final_system_string` so we can measure the blob-shape empirically at runtime.

## Instrumentation Landed (RH1.1)

New module: `@c:/Git/Agentic-Workflow/agentic_core/L2_execution/enforcement/_reception_audit.py`

- Pure observation. Zero behavior change. No exception path on failure (guardian-exempt narrow IO).
- Detects fences in the two flat strings: `<D0>`, `<U0>`, `<instructions>`, `<context>`, `<examples>`, `<example`, `<thinking>`, `<document>`, `<documents>`, `<role>`.
- Records `system_bytes`, `user_bytes`, `tools_count`, `token_estimate`, `signature_present`, `newline_joined_sections`.
- Always emits a structured `prompt_reception` log line at INFO.
- Optionally appends to `artifacts/prompt_reception/reception_evidence.jsonl` when `PROMPT_RECEPTION_AUDIT=1`.
- Optional path override via `PROMPT_RECEPTION_AUDIT_PATH`.

Gateway injection: both `generate()` and `generate_with_reasoning()` call
`_emit_reception_evidence(_build_reception_evidence(...))` immediately before
`provider_impl.generate(...)`.

## Assembly-Site Inventory (RH1.2)

### `CompiledPromptArtifact` constructor sites — production

| Layer | File | Notes |
|---|---|---|
| L0 | `agentic_core/L0_routing/reasoning/assembly_stage.py` | `AirlockAssembler.assemble_from_bom` — canonical governed path |
| L2 | `agentic_core/L2_execution/reasoning/slot_assembly_engine.py` | Direct slot-assembly engine |
| L2 | `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | `_artifact_from_request` (route_generation fallback path) |
| Learning | `system_learning/engines/prompt_provenance_builder.py` | Provenance reconstruction |

### `AirlockAssembler.assemble_from_bom` callers — production

| App / Module | File | Coverage |
|---|---|---|
| apps_lic | `apps_lic/engines/lic_spine_adapter.py` | ✅ Governed |
| apps_rg | `apps_rg/engines/rg_spine_adapter.py` | ✅ Governed |
| apps_shared | `apps_shared/utils/governed_prompt_adapter.py` | ✅ Shared adapter |
| L_SHARED | `agentic_core/interfaces/spine.py`, `spine_shim.py` | Wrapper |
| L5 | `agentic_core/L5_safety/validators/direct_prompt_compilation_validator.py` | Enforcement |
| L0 | `agentic_core/L0_routing/reasoning/assembly_stage.py` | Self-reference |

### Apps NOT observed in governed path

| App | Status | Follow-up |
|---|---|---|
| apps_exec | ❌ No governed-path caller observed | W5.1 should add AgentSpec-driven assembly |
| apps_research | ❌ No governed-path caller observed | W5.1 |
| apps_eval | ❌ No governed-path caller observed | W5.1 |
| apps_rfp | ❌ No governed-path caller observed | W5.1 |
| apps_underwriting_ai | ❌ No governed-path caller observed | W5.1 |

**Implication**: the reception-hardening plan must account for the possibility
that 5 apps don't even reach the seam we are hardening. W5 (reception gates
+ AgentSpec response_schema) must extend to include a "does this app's LLM
path flow through the governed assembler?" check. Candidate: new gate
`check_assembler_coverage.py` asserting each `apps_*/engines/*` with an LLM
call has a traceable `assemble_from_bom` call in its import closure.

## ADG Graph-Layer Evidence

ADG Provenance: backend=sqlite (snapshot adg_indexed_04222026_2106.sqlite), Redis cold at audit time. Live MV queries deferred to a later audit pass (MCP serialization budget). Grep-based inventory above is classified DERIVED per constitutional fact-grading; structural fan-in counts remain UNRESOLVED pending a live ADG query session.

Target MVs to query in follow-up:
- `mv_hotspot_centrality` on `SovereignLLMGateway.generate` — expect top-5 closeness centrality.
- `mv_graph_chokepoint_bridges` on `CompiledPromptArtifact` (both definitions) — expect bridge status.
- `mv_dependency_cone_risk` on `AirlockAssembler.assemble_from_bom`.
- `mv_graph_critical_path_blast_radius` for the seam lines 558-565 + 653-660.

Target semantic edges:
- `calls(*, SovereignLLMGateway.generate)` — full fan-in of gateway callers.
- `flows_to(PromptBOM, CompiledPromptArtifact)` — trace the pre-seam pipeline.
- `writes_to(*, CompiledPromptArtifact)` — all constructor paths.

Target P-views:
- `v_p2_duplicated_adapters` — cross-check against the two parallel `CompiledPromptArtifact` definitions.

## Verification

- `python -m py_compile agentic_core/L2_execution/enforcement/_reception_audit.py` → exit 0.
- `python -m py_compile agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` → exit 0.
- Mypy warnings pre-existing on `SovereignLLMGateway.py`; no new issues introduced by the injection.
- Log-only contract preserved: no new exception paths, no new branches in either `generate` method.

## Success Criteria (per plan)

| Criterion | Status |
|---|---|
| Evidence report at docs/reports/plans/prompt_reception_audit.md | ✅ This file |
| Instrumentation in SovereignLLMGateway.generate | ✅ Both `generate` methods |
| ADG live queries populated | ⚠️ Grep-derived inventory only; live MV queries deferred to a follow-up when Redis is warm |

## Exit Recommendation for W1

W1 is **complete enough to unblock W2**. The three critical facts needed to size W2:

1. ✅ Reception seam location and exact handoff contract.
2. ✅ Number of production apps currently in the governed path (2 of 7) — materially changes W5 scope.
3. ✅ Two-parallel-artifact SSOT drift — materially changes W2 scope (W2.1 must resolve before adapter rewrites).

Recommend proceed to W2. A follow-up audit pass with Redis warm + live MV
queries can run in parallel with W2 work.
