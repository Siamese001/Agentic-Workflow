# apps_rg Agentic Spine

> L2-owned deterministic HOP pipeline for on-demand résumé generation.
> Preloaded context (JD + master resume + company brief from disk) — **no C0 vector retrieval, no live research**.
> Output is a sealed résumé draft (JSON + narrative enrichment + DOCX export) reviewed by the candidate out-of-band.

## Canonical Spine Ownership Invariants

> Authoritative for `apps_rg`. The diagrams and HOP tables below describe the deterministic execution recipe; this section names the immutable boundary contract. If the diagrams disagree, this section wins.

| Layer | Owns | Does NOT own |
|---|---|---|
| **U0 INTAKE** | request envelope validation; `request_id` / `session` / `tenant` / `trace_id` stamping; labeling raw user content as user intent (not authority) | reasoning, routing, retrieval, assembly, execution |
| **L1 PLAN** | task_spec / query_spec / ambiguity register / route hints; `L1PlanContract` emission; planning priors | provider-ready prompts, prompt artifacts, model calls |
| **L0 ROUTE** | exactly one `RouteContract`; cache / fallback / grounded read / action / managed-workflow decision; `grounding_required`, `execution_form`, risk/HITL posture, provider/model eligibility hints, route reason codes | provider-ready prompts, `PromptBOM`, `PromptEnvelope`, `CompiledPromptArtifact`, raw provider payloads |
| **C0 CONTEXT ENGINE** *(grounded routes only)* | retrieves, shapes, and verifies evidence; `FinalEvidenceContract`; retrieved content remains data-only | answering; assembling prompts; promoting retrieved text to instruction |
| **PA PROMPT ASSEMBLY** | `PromptBOM`, `PromptEnvelope`, `CompiledPromptArtifact`; slot order; slot authority map; slot lineage map; token budget + deterministic trimming; provider-aware rendering; response schema binding; `prompt_hash` / `compiled_artifact_hash`; prompt boundary receipts; injection neutralization receipts | routing, planning, retrieval, execution |
| **RUNTIME GATES + L5 EVIDENCE** | L5 emits **certification evidence** (authority / policy / origin-trust / registry / sandbox / egress / replay-audit). Runtime Gates emit **live `GateVerdict` records**. `UNKNOWN` is never `PASS`. | the runtime "permit / block / escalate" disposition (that is Exit's job, not L5's) |
| **L2 EXECUTE** | consumes the signed compiled artifact (or approved bounded work packet); executes one bounded model/tool/script/PTC attempt; same-authority local heal; sealed artifact emission | constructing prompts before receiving a compiled artifact; widening route/tool/model/policy/capability/sandbox |
| **L3 ORCHESTRATION** *(MANAGED_WORKFLOW only — BYPASSED for apps_rg)* | bounded step contracts, checkpoints, branch/join state, retry policy | tool/model/script execution; healing execution failures; output approval; L4 writes |
| **EXIT** | normalizes sealed artifact / terminal return packet; evaluates outcome / safety / evidence / replay / observability / write-eligibility; emits **exactly one X3 disposition**; may emit `CommitRequest` (does not write L4) | mutating durable state |
| **UWG / L4** *(only when durable write cleared)* | the sole durable write path | being bypassed by direct writers |
| **L6 SHADOW EVALUATION** | observes completed-run exhaust; evaluates / calibrates / detects drift / drafts proposals | rescuing the current run; writing L4 directly |

**Spine summary:** L1 plans · L0 routes · C0 retrieves evidence · PA composes and defends prompt artifacts · Runtime Gates emit live `GateVerdict` records · L5 emits governance certification evidence · L2 executes signed compiled artifacts · L3 orchestrates managed-workflow step contracts only when L0 selects them · Exit emits exactly one X3 · UWG alone writes durable state · L6 learns only after the run.

## Two Prompt-Injection Concepts (definitive)

These are **related but not the same**. apps_rg honors both.

### Instructional prompt injection (governed composition)

The governed insertion of: goal · success criteria · task mode · scope · efficiency constraints · evidence binding · reasoning controls · safety rails · output schema · error format · minimality rules.

**Authority:** PA Prompt Assembly (apps_rg local PA + agentic_core mixin corpus consumed only after PA compile). Worker-side instructional mixins are consumed only through the compiled artifact or an approved bounded work packet.

### Prompt injection defense (boundary protection)

Detection / fencing / neutralization / quarantine / rejection of untrusted content trying to override: system instructions · developer instructions · policy · route · tool selection · provider/model · schema · output format · sandbox/capability scope · write authority · HITL requirements.

**Authority:** PA airlock layer + `agentic_core/prompt_governance/security/`.

> **Required language:** *Instructional injection is a governed composition pattern. Prompt injection defense is a boundary protection pattern. They are related but not the same.*

See `apps_rg/PROMPT_BOUNDARY_CONTRACT.md` for the slot authority map, evidence airlocks, and receipt contract.

## Dual PA Topology

apps_rg has a **dual PA topology**. The governed apps_rg PA compiler owns `AppsRgCompiledPromptArtifact` generation for L2 recipe templates. The legacy `anthropic_rag_entrypoint` bridge consumes agentic_core `PromptEnvelope` for the narrative / R3 contract surface. **Both are PA-owned prompt assembly surfaces. This dual topology does not grant L0 prompt assembly authority.**

| Surface | Path | Used for |
|---|---|---|
| **NEW PA (apps_rg-local)** | `apps_rg/prompt_assembly/compiler.py:compile_prompt(AppsRgPromptRequest) → AppsRgCompiledPromptArtifact` | governed L2 recipe templates (`hop_4_generate_resume`, `fact_check_generated_resume`, `omit_unsupported_resume_claims`, `repair_bullet_diversity`, `hop_6_docx_export`) — see `spine_manifest.yaml: compiled_artifact_required_for` |
| **LEGACY PA bridge (agentic_core PromptEnvelope)** | `apps_rg/utils/anthropic_rag_entrypoint.py:build_anthropic_rag_payload(PromptEnvelope) → AnthropicRagPayload` (re-exported as `apps_rg/prompt_assembly/rg_pa_compiler.py`) | original load-bearing R3 contract surface (per `spine_manifest.yaml:51, 82-85`); narrative-pipeline ensemble + judges via `apps_rg/integrations/hops/_llm_client.py` (PA-instrumented through `apps_rg.prompt_assembly.pa_local.capture_prompt_bom`) |

**Invariants for both surfaces:**

1. PA owns slot composition, slot authority order, schema binding, and the boundary airlock — neither route, planner, retriever, nor executor may forge a provider-ready prompt.
2. PA compiles **before** L2 consumes. The current `apps_rg/l2_recipe/steps.py::_PAGuard` enforces this fail-closed (no model call without `PA_L2_HANDOFF_READY` artifact). PA invocation may live inside an L2 step adapter for ergonomic reasons; the compile-before-execute contract is preserved by the guard.
3. Worker-side instructional mixins (framing / context / reasoning-control / tooling / safety / output) are consumed only after PA compile — they cannot create new authority, bypass PA, or inject retrieved/user/tool/human/model text as instructions.
4. Output schema is bound through R0 (PA-owned) — prose schema instructions are not a substitute when structured schema binding exists.

> **Removed false mental model:** earlier doc snapshots implied "L0 owns prompt assembly" or "L0 emits CompiledPromptArtifact". That is incorrect. L0 emits a `RouteContract` only. PA assembles. L2 executes. The dual-PA topology above is a PA-internal property, not an L0 property.

```
USER (CLI: python -m apps_rg --target-company <co> --jd <path> ...)
 │
 v
U0 INTAKE
 │  raw input capture, arg parse, file existence
 │
 v
L1 PLAN
 │  JDPlan extraction (jd_planner.py)
 │  seniority_band, role_family, ats_keywords, max_pages
 │  Pure deterministic — no LLM, no network
 │
 v
L0 ROUTE DECISION
 │
 ├── R1A Exact Cache? ──hit──► [RET] sealed artifact ref → Exit X3D_ALLOW_FINISH
 │     (SHA256 of jd+resume+brief+policy+blueprint+schema+cache_schema_version)
 │
 ├── R1B Semantic Cache? ──hit──► [RET] cached chunks + lineage → Exit X3D_ALLOW_FINISH
 │     (14-field compatibility key: candidate_profile_hash, master_resume_hash,
 │      jd_text_hash, company_brief_hash, target_company, role_title_hash,
 │      seniority_band, output_schema_hash, prompt_template_hash, policy_hash,
 │      blueprint_hash, model_lane_hash, freshness_class, cache_schema_version)
 │
 ├── R5 Briefing Prerequisite ──fail──► sealed_failure_packet → Exit X3E_SAFE_ABSTAIN_CLARIFY
 │     (brief missing / stale / invalid)
 │
 └── R4_SINGLE_ACTION ──────────────────────────────────────────────┐
                                                                     │
 L2 BOUNDED EXECUTION PACKET                                        │
 │                                                                   │
 ├── E1 PREP                                                        │
 │   • Load JD, master resume, company brief from disk              │
 │   • Compute content hashes (jd, resume, brief)                   │
 │   • Freeze run directory (artifacts/apps_rg/runs/<ts>/)          │
 │   • Bind policy/blueprint/registry/model lane                    │
 │   • Create replay_key + idempotency_key                          │
 │   • Create artifact manifest shell                               │
 │   • Compile CompiledPromptArtifact via PA compiler (CANONICAL_PA)│
 │                                                                   │
 ├── E2 VALID                                                       │
 │   • Validate JD JSON schema                                      │
 │   • Validate company brief freshness + schema                    │
 │   • Validate no hidden research path (Tavily/internal disabled)  │
 │   • Validate prompt/model authority                              │
 │   • Validate output schema                                       │
 │   • Validate sandbox write location                              │
 │   • Validate cache compatibility rules                           │
 │                                                                   │
 ├── E3 EXEC (L2-owned deterministic HOP pipeline)                  │
 │   • HOP 1 Clerk Extraction                                       │
 │   │   Parse JD + master resume, normalize extracted fields        │
 │   • HOP 2 Data Enrichment                                        │
 │   │   Enrich extracted data, repo signal collection (optional)    │
 │   • HOP 3 Resume Generation (governed prompt packet)              │
 │   │   Qwen vLLM / Anthropic synthesis via prompt_bom              │
 │   │   Flow-routed: strategic_tailor / tailor_existing /            │
 │   │     generate_scratch / enhance_current                        │
 │   • HOP 4 Fact Check                                              │
 │   │   Cross-reference claims against master resume                │
 │   │   Fabrication detection gate                                  │
 │   • HOP 5 Bullet Diversity Gate                                   │
 │   │   Thematic-spread evaluation + fact-check clean gate          │
 │   • HOP 6 Content Optimizer                                      │
 │   │   Keyword / action-verb refinement, ATS compatibility pass    │
 │   • HOP 7 Generation Diagnostics                                  │
 │   │   Final scorecard + QA report, composite quality score        │
 │   • Narrative Pass (HOP-4A..4H, preloaded brief only)             │
 │   │   Company brief grounding, headline, summary, experience      │
 │   • DOCX Export                                                   │
 │   │   Render final .docx artifact                                 │
 │                                                                   │
 │   HOP failure paths:                                              │
 │   • LLM timeout / generation failed → sealed_failure_packet       │
 │   • Fabrication detected → sealed_violation_packet                │
 │   • Gate failed → sealed_degraded_packet                          │
 │   • Narrative failed → sealed_degraded_packet (JSON still usable) │
 │   • DOCX export failed → sealed_degraded_packet (JSON still usable)│
 │   (All sealed packets flow to E5, NOT directly to Exit X3)        │
 │                                                                   │
 ├── E4 HEAL (same-authority local repair only)                     │
 │   • Retry model timeout (same provider lane, within budget)      │
 │   • Retry JSON/schema/template/DOCX formatting defects           │
 │   • NOT allowed: research, human input, route change, L4 write   │
 │                                                                   │
 └── E5 SEAL                                                        │
     • Seal generated_resume.json                                    │
     • Seal narrative_resume.json (if produced)                      │
     • Seal DOCX (if produced)                                       │
     • Seal run_report.json, diagnostics, claim-to-source map        │
     • Seal compiled_prompt_artifact + prompt_bom + replay metadata   │
     • terminal_class: SUCCESS | DEGRADED_SUCCESS | FAILURE          │
     • Optional cache_commit_candidate (inert until Exit)            │
                                                                     │
 EXIT                                                                │
 │  X1 checkout checks (provenance, schema, evidence)               │
 │  X2 aggregation                                                  │
 │  Exactly one X3 disposition:                                     │
 │    X3A_DENY_REROUTE — hard failure, no usable output             │
 │    X3C_COMMIT_REQUEST_TO_UWG — if cache commit enabled + passed  │
 │    X3D_ALLOW_FINISH — success or degraded success                │
 │    X3E_SAFE_ABSTAIN_CLARIFY — brief missing, fabrication, etc.   │
 │    (X3B_ESCALATE_HITL not used — no runtime HITL)                │
 │                                                                   │
 ├── Optional CommitRequest → UWG → L4 (cache commit only)          │
 │                                                                   │
 └── L6 (after run completion only — evaluation + future-run learning)
```

## Spine Characteristics

| Property | Value |
|----------|-------|
| **Route Type** | `R4_SINGLE_ACTION` (see `spine_manifest.yaml`) |
| **Execution Form** | `DETERMINISTIC_PIPELINE` (multi-HOP, no async/resume) |
| **L3 DAG Path** | `BYPASSED` (no orchestration graph — HOPs run within L2 E3) |
| **C0 Grounding** | `False` (JD, master resume, company brief are preloaded from disk) |
| **Prompt Assembly** | `CANONICAL_PA` — **dual-PA topology** (see "Dual PA Topology" section above): NEW `apps_rg/prompt_assembly/compiler.py` for governed L2 templates + LEGACY `apps_rg/utils/anthropic_rag_entrypoint.py` (`PromptEnvelope`-based) for narrative/R3 contract surface. Both surfaces are PA-owned. L0 does NOT own prompt assembly. |
| **PA→L2 Timing** | PA compiles **before** L2 consumes (sequential). `_PAGuard` (`apps_rg/l2_recipe/steps.py:27-104`) enforces fail-closed: no model call without `PA_L2_HANDOFF_READY` artifact. |
| **Runtime Authority** | `FILESYSTEM_SANDBOX_WRITE` + `MODEL_EGRESS` (governed provider lane) |
| **HITL Posture** | `False` (no runtime HITL; no X3B emission; résumé review is out-of-band) |
| **Optional Cache Commit** | Via Exit → CommitRequest → UWG → L4 only (never direct L4 write) |

## Flow Routing (K.0 Thematic Analysis)

The `RGFlowRouter` classifies each request into one of four flows based on task description, master resume availability, and thematic analysis:

| Flow | Trigger | Required HOPs | Description |
|------|---------|---------------|-------------|
| **strategic_tailor_node** | >3 differentiator keywords (K.0) | HOP 1–6 | Full strategic tailoring with thematic analysis |
| **tailor_existing** | Tailor keywords + master resume | HOP 1–5 | Modify existing résumé for target role |
| **generate_scratch** | Generate keywords / no resume | HOP 1–5 | Build from scratch against JD |
| **enhance_current** | Enhance keywords | HOP 3–5 | Polish existing content only |

## Route and Cache Strategy

| Route | Key / Condition | Hit Behavior |
|-------|-----------------|--------------|
| **R1A Exact** | SHA256(jd+resume+brief+policy+blueprint+schema+cache_schema_version) | Sealed artifact ref → Exit X3D |
| **R1B Semantic** | 14-field compatibility key (see flow diagram) | Cached chunks + lineage → Exit X3D |
| **R5 Briefing Gate** | Manual-brief file existence + freshness + schema | sealed_failure_packet → Exit X3E |

## L2-Owned Deterministic HOP Pipeline (7 stages)

> These HOPs execute within L2 E3 — they are NOT L3 DAG nodes.
> The topology in `config/hop_pipeline.py` is a domain-level pipeline specification consumed by E3.

| HOP | Stage | Engine | Required | Gate |
|-----|-------|--------|----------|------|
| 1 | `clerk_extraction` | `ClerkExtractionEngine` | ✅ | — |
| 2 | `data_enrichment` | `DataEnrichmentEngine` | ✅ | — |
| 3 | `resume_generation` | `ResumeGenerationTask` | ✅ | — |
| 4 | `fact_check` | `FactCheckEngine` | ✅ | — |
| 5 | `bullet_diversity_gate` | `BulletDiversityGate` | ✅ | ✅ |
| 6 | `content_optimizer` | `ContentOptimizerEngine` | ✅ | — |
| 7 | `generation_diagnostics` | `GenerationDiagnosticsEngine` | ✅ | — |

## Exit Disposition Mapping (Canonical X3)

> HOPs emit sealed packets to E5. Exit consumes sealed packets and emits exactly one X3 disposition.
> HOPs NEVER emit X3 directly.

| Failure Mode | Stage | Sealed Packet | X3 Disposition | terminal_class | User Action |
|--------------|-------|---------------|----------------|----------------|-------------|
| Brief missing / stale | R5 (pre-L2) | `sealed_failure_packet` | `X3E_SAFE_ABSTAIN_CLARIFY` | FAILURE | Provide or refresh company brief |
| Brief needs research | R5 (pre-L2) | `sealed_failure_packet` | `X3E_SAFE_ABSTAIN_CLARIFY` | FAILURE | Run `apps_research` upstream first |
| LLM generation timeout | E3 HOP 3 | `sealed_failure_packet` | `X3E_SAFE_ABSTAIN_CLARIFY` | FAILURE | Check provider health |
| Fabrication detected | E3 HOP 4 | `sealed_violation_packet` | `X3E_SAFE_ABSTAIN_CLARIFY` (severity=critical) | FAILURE | Fix engine prompt / profile |
| Fact-check gate fail | E3 HOP 5 | `sealed_degraded_packet` | `X3A_DENY_REROUTE` (reentry=L2_REPAIR) if retryable, else `X3E` | FAILURE | Retry generation |
| Narrative pass failed (JSON usable) | E3 narrative | `sealed_degraded_packet` | `X3D_ALLOW_FINISH` (degraded=true) | DEGRADED_SUCCESS | Check brief / narrative templates |
| Provenance failure | E5 seal | `sealed_violation_packet` | `X3E_SAFE_ABSTAIN_CLARIFY` (severity=critical) | FAILURE | Fix provenance / source data |
| DOCX export failed (JSON/narrative usable) | E3 DOCX | `sealed_degraded_packet` | `X3D_ALLOW_FINISH` (degraded=true, missing=["docx"]) | DEGRADED_SUCCESS | Check DOCX templates |
| ATS coverage < 80% | E3 HOP 6/7 | (no sealed packet — advisory) | `X3D_ALLOW_FINISH` (warn) | SUCCESS | Review keyword coverage |
| Full success | E5 seal | `sealed_success_packet` | `X3D_ALLOW_FINISH` | SUCCESS | — |
| Full success + cache eligible | E5 seal | `sealed_success_packet` + `cache_commit_candidate` | `X3C_COMMIT_REQUEST_TO_UWG` then `X3D_ALLOW_FINISH` | SUCCESS | — |

## Local Evidence Contract (FEC)

> This is an app-local evidence contract — not a C0-grounded FEC.
> apps_rg does not perform C0 retrieval; evidence sources are preloaded disk artifacts.

```yaml
# Produced by apps_rg/cert/fec_producer.py → resolve_fec()
producer: apps_rg.cert.fec_producer
grounded: false                          # Always false — no C0 retrieval. True only when
                                         # JD + (role OR repo) evidence sources are non-empty.
retrieval_sources: []                    # Aggregated from 3 source ladders (all preloaded)
route_id: apps_rg.resume_generation_v1
template_ids:
  - apps_rg.resume_generation.strategic_tailor.v1
  - apps_rg.resume_generation.tailor_existing.v1
  - apps_rg.resume_generation.generate_scratch.v1
  - apps_rg.resume_generation.enhance_current.v1
evidence_sufficiency: empty              # empty | template_only | partial | grounded
schema_version: "1.0"
source_ladder:
  jd_evidence_sources: []                # From job description (preloaded)
  role_evidence_sources: []              # From prior role evidence (preloaded)
  repo_signal_sources: []                # From repository signals (preloaded)
# Additional fields (planned):
#   claim_to_source_map: {}              # Per-claim source references
#   unsupported_claims: []               # Claims without source backing
#   fabricated_claims: []                # Claims flagged by fact-check
#   brief_freshness_status: null         # Company brief freshness assessment
#   artifact_hashes: {}                  # SHA256 of sealed artifacts
#   run_id: null                         # Unique run identifier
#   replay_key: null                     # Deterministic replay key
```

## File Outputs (Sealed Artifacts)

```
artifacts/apps_rg/runs/<timestamp>/
├── generated_resume.json           # Core résumé JSON
├── grounding_report.json           # Optional: HOP-2 grounding
├── format_validation.json          # Optional: format gate
├── narrative_metadata.json         # Optional: narrative pass metadata
├── narrative_resume.json           # Narrative-enriched résumé
├── run_report.json                 # Orchestrator status + provenance
├── prompt_bom.json                 # Prompt bill-of-materials (all model invocations)
└── <FirstName>_<LastName>_Resume_<Company>.docx   # Final DOCX export
```

## Cross-App Integration Points

| Source App | Artifact Consumed | Usage | Boundary |
|------------|-------------------|-------|----------|
| `apps_research` | Company brief (JSON, **prebuilt on disk**) | Narrative pass grounding (HOP-4A..4H) | apps_rg reads from disk only; apps_research runs upstream, not inside apps_rg |
| `apps_qna` | Consumes apps_rg output | Resume + STAR proofs → StoryBank cards | Downstream consumer only |
| `apps_exec` | Executive brief | Cross-referenced for senior roles | Prebuilt artifact on disk |

> **apps_rg does NOT invoke apps_research, Tavily, or any live research at runtime.**
> If the company brief is missing/stale, apps_rg fails closed via R5 → X3E.
> The user must run `apps_research` upstream before invoking apps_rg.

## Non-Goals (This Spine Does NOT)

- ❌ C0 vector retrieval / RAG (preloaded disk inputs only)
- ❌ L3 orchestration DAG (bypassed — HOPs run within L2 E3)
- ❌ Runtime HITL escalation (no X3B emission; review is out-of-band by candidate)
- ❌ ATS submission (ATS score is an output metric, not a write)
- ❌ LinkedIn API calls (read-side authenticity patterns only)
- ❌ Direct L4 writes (optional cache commit via Exit → CommitRequest → UWG only)
- ❌ Live web research / Tavily / apps_research invocation inside runtime
- ❌ Hidden cross-app execution (apps_research runs upstream, not inside apps_rg)

## See Also

- `spine_manifest.yaml` — Canonical route-type declaration (R4_SINGLE_ACTION)
- `prompts/prompt_bom.yaml` — Prompt Bill of Materials (BOM) for PA compilation
- `prompt_assembly/compiler.py` — PA compiler: BOM → CompiledPromptArtifact
- `prompt_assembly/contracts.py` — PA contract types
- `prompt_assembly/slot_mapper.py` — Slot mapping (S0/I0/C0/U0/R0)
- `prompt_assembly/provider_request.py` — Artifact → provider request adapter
- `config/hop_pipeline.py` — L2 E3 HOP topology declaration (7 stages)
- `engines/hop_pipeline_adapters.py` — Substrate-compatible HOP adapters
- `reasoning/RgResumeOrchestrator.py` — Primary runtime orchestrator
- `types/rg_flow_router_types.py` — K.0 thematic analysis + flow routing
- `L1_cognition/jd_planner.py` — JD semantic extraction (L1 planning)
- `cert/fec_producer.py` — Local evidence contract producer
- `cache/r1b_adapter.py` — R1A exact cache + R1B semantic cache adapter
- `scripts/narrative_pass.py` — Post-pipeline narrative enrichment (preloaded brief only)
- `outputs/docx_exporter.py` — DOCX export
- `__main__.py` — Canonical entrypoint
