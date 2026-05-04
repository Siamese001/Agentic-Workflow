# apps_exec Agentic Spine

> On-demand executive brief generator — persona-targeted synthesis from architecture documentation.
> Grounded read over the `exec_docs` collection (C0 hybrid retrieval) — **no side-effect actions**.
> Output is a sealed executive brief artifact (Markdown + JSON) reviewed by platform consumers out-of-band.

```
USER (CLI: python -m apps_exec --audience <persona> --source-dirs <dirs> ...)
 │
 v
U0 INTAKE
 │  raw input capture, arg parse, audience persona binding
 │  validate source directories exist and contain .md/.txt files
 │  bind request envelope (audience, emphasis_areas, source_dirs, out_dir)
 │
 v
L1 PLAN
 │  parse executive brief intent from audience persona
 │  define persona tone + required sections from emphasis_areas
 │  create ExecBriefRequest spec (audience, sections, evidence_expectations)
 │  grounding_required = true (C0 retrieval required)
 │  emit L1PlanContract
 │
 v
L0 ROUTE DECISION
 │
 ├── R1A EXACT_CACHE?
 │     hit ──► [RET] sealed brief artifact → Exit X3D_ALLOW_FINISH
 │     (SHA256 of audience + source_dirs + policy + blueprint + schema)
 │
 ├── R1B SEMANTIC_CACHE?
 │     hit ──► [RET] cached brief chunks + lineage → Exit X3D_ALLOW_FINISH
 │     (compatibility key: audience, source_digest, emphasis_hash, freshness_class)
 │
 ├── R5 PRE_ROUTE_FALLBACK?
 │     selected ──► [RET] sealed degradation packet → Exit X3E_SAFE_ABSTAIN
 │     (source_dirs missing / no readable files / schema invalid)
 │
 └── R3_SIMPLE_GROUNDED_READ ───────────────────────────────────────┐
                                                                     │
 R3 Route Contract                                                   │
 │                                                                   │
 │   route_id            = R3_SIMPLE_GROUNDED_READ                   │
 │   execution_form      = SINGLE_STEP                             │
 │   l3_required         = false                                   │
 │   selected_capability = apps_exec.execution_v1                  │
 │                                                                   │
 │   Meaning:                                                        │
 │   - SIMPLE   = no L3 managed workflow (no retry/branch/join)      │
 │   - GROUNDED = C0 hybrid retrieval required over exec_docs        │
 │   - READ     = informational briefing output, no side effects   │
 │                                                                   │
 v                                                                   │
apps_exec normalization                                              │
 │  - normalize audience persona (recruiter/cto/svp_eng/board)    │
 │  - bind source_dirs → ingestion targets                           │
 │  - bind output = governed executive brief packet                  │
 │  - bind freshness and evidence expectations per persona            │
 │  - does not route (already R3)                                    │
 │  - does not retrieve final evidence (delegates to C0)            │
 │  - does not approve output (delegates to Exit)                   │
 │                                                                   │
 v                                                                   │
C0 Context Engine                                                    │
 │  - build retrieval plan over exec_docs collection                 │
 │  - hybrid retrieval: dense (embedding) + sparse (keyword)          │
 │  - metadata filtering by freshness, source type, relevance       │
 │  - preserve source refs and citation anchors                      │
 │  - score evidence support per claim                               │
 │  - detect freshness issues (stale architecture docs)               │
 │  - detect contradictions and evidence gaps                       │
 │  - emit FinalEvidenceContract                                     │
 │                                                                   │
 │  If evidence unusable:                                            │
 │     sealed degraded/failure packet → Exit X3E_SAFE_ABSTAIN      │
 │                                                                   │
 v                                                                   │
PA Prompt Assembly                                                   │
 │  - bind ExecBriefRequest + evidence + persona rubric           │
 │  - fence retrieved content as DATA                               │
 │  - include evidence refs / policy_hash / blueprint_hash          │
 │  - bind audience-specific section templates                       │
 │  - emit CompiledPromptArtifact                                    │
 │                                                                   │
 │  If PA fails:                                                     │
 │    sealed prompt failure packet → Exit X3E_SAFE_ABSTAIN          │
 │                                                                   │
 v                                                                   │
L2 Execute                                                           │
 │                                                                   │
 ├── E1 PREP ─────────────────────────────────────────────────────┤
 │   • Load source files via IngestionEngine                         │
 │   • Compute content hashes (sources, policy, blueprint)            │
 │   • Freeze run directory (artifacts/apps_exec/runs/<ts>/)      │
 │   • Bind policy/blueprint/registry/model lane                    │
 │   • Create replay_key + idempotency_key                          │
 │   • Bind persona-specific output schema                           │
 │                                                                   │
 ├── E2 VALID ──────────────────────────────────────────────────────┤
 │   • Validate source file schema (YAML frontmatter if present)    │
 │   • Validate evidence contract freshness + coverage              │
 │   • Validate prompt/model authority                               │
 │   • Validate output schema (brief sections expected)            │
 │   • Validate sandbox write location                               │
 │   • Validate style gate thresholds pre-execution                 │
 │                                                                   │
 ├── E3 EXEC ───────────────────────────────────────────────────────┤
 │   • CapabilityExtractionEngine ──► extract platform capabilities  │
 │   • BriefAssemblyEngine ──► assemble persona-targeted sections     │
 │     - platform_summary, key_capabilities, portfolio_value         │
 │     - architecture_overview, governance_model, platform_strategy  │
 │     - engineering_decisions, quality_gates                        │
 │     - strategic_value, risk_posture, competitive_differentiation │
 │     - enterprise_use_cases                                        │
 │   • StyleGateValidator ──► enforce buzzword density, absolutes   │
 │   • ArtifactEmission ──► write brief.md + run_summary.json       │
 │                                                                   │
 │   Execution failure paths:                                        │
 │   • No capabilities extracted → sealed_failure_packet            │
 │   • Style violations exceed limit → sealed_violation_packet      │
 │   • Assembly engine failure → sealed_failure_packet              │
 │   (All sealed packets flow to E5, NOT directly to Exit X3)        │
 │                                                                   │
 ├── E4 HEAL (same-authority local repair only) ──────────────────────┤
 │   • Retry deterministic template substitution                      │
 │   • Retry JSON/schema formatting fixes                            │
 │   • NOT allowed: research, human input, route change, L4 write   │
 │                                                                   │
 └── E5 SEAL ─────────────────────────────────────────────────────────┤
     • Seal exec_brief_<audience>_<trace_id>.md                     │
     • Seal run_summary_<trace_id>.json (provenance + gate results)  │
     • Seal evidence_anchor_map.json                                 │
     • terminal_class: SUCCESS | DEGRADED_SUCCESS | FAILURE         │
     • Optional cache_commit_candidate (inert until Exit)            │
                                                                     │
 EXIT                                                                │
 │  X1 checkout checks (provenance, schema, evidence anchors)       │
 │  X2 aggregation (gate_violations + terminal_class)               │
 │  Exactly one X3 disposition:                                      │
 │    X3A_DENY_REROUTE — hard failure, no usable output            │
 │    X3C_COMMIT_REQUEST_TO_UWG — cache commit only (if enabled)    │
 │    X3D_ALLOW_FINISH — success or degraded success                 │
 │    X3E_SAFE_ABSTAIN — source missing, style violations, etc.    │
 │    (X3B_ESCALATE_HITL used only when hitl_policy=require_always) │
 │                                                                   │
 ├── Optional CommitRequest → UWG → L4 (cache commit only)        │
 │                                                                   │
 └── L6 (after run completion only — evaluation + future-run learning)
```

## Spine Characteristics

| Property | Value |
|----------|-------|
| **Route Type** | `R3_SIMPLE_GROUNDED_READ` (see `spine_manifest.yaml`) |
| **Execution Form** | `SINGLE_STEP` (no L3 orchestration required) |
| **L3 DAG Path** | `BYPASSED` — L3 runtime orchestration not required |
| **C0 Grounding** | `True` (hybrid retrieval over `exec_docs` collection) |
| **Prompt Assembly** | `CANONICAL_PA` (CompiledPromptArtifact with fenced DATA) |
| **Runtime Authority** | `FILESYSTEM_SANDBOX_WRITE` + `MODEL_EGRESS` (deterministic template synthesis) |
| **HITL Posture** | Configurable via `threshold_profiles.yaml` (`none` / `required_on_low` / `required_always`) |
| **Cache Strategy** | R1A exact + R1B semantic (optional cache commit via Exit → UWG) |

## Audience Personas

The `ExecOrchestrator` routes each request to persona-specific section templates:

| Persona | Tone | Required Sections | Emphasis Trigger |
|---------|------|-------------------|------------------|
| **recruiter** | recruiter-friendly | platform_summary, key_capabilities, portfolio_value | Default / `--audience recruiter` |
| **cto** | cto-ready | architecture_overview, governance_model, platform_strategy | `--audience cto` |
| **svp_eng** | technical | system_architecture, engineering_decisions, quality_gates | `--audience svp_eng` |
| **board** | board-ready | strategic_value, risk_posture, competitive_differentiation | `--audience board` |

## Route and Cache Strategy

| Route | Key / Condition | Hit Behavior |
|-------|-----------------|--------------|
| **R1A Exact** | SHA256(audience + source_dirs + policy + blueprint + schema + cache_schema_version) | Sealed brief ref → Exit X3D |
| **R1B Semantic** | Compatibility key: audience, source_digest, emphasis_hash, freshness_class | Cached brief + lineage → Exit X3D |
| **R5 Briefing Gate** | source_dirs existence + file count + schema validity | sealed_failure_packet → Exit X3E |

## Quality Gates (StyleGateValidator)

| Gate | Threshold | Severity | Response |
|------|-----------|----------|----------|
| **EVIDENCE_TOO_OLD** | Evidence anchor > 90 days | WARN | Surface to user; do NOT relax threshold |
| **UNSUPPORTED_ABSOLUTE_CLAIM** | Contains "always", "never", "guaranteed" | BLOCK | Seal violation packet → X3E |
| **BUZZWORD_DENSITY** | Density > 5% | BLOCK | Seal violation packet → X3E |
| **BRIEF_TOO_SHORT** | < 500 words | WARN | Check `max_tokens` config |
| **EMPTY_SECTION** | Any required section blank | WARN | Retry assembly with `--retry-empty-sections` |
| **STYLE_VIOLATIONS_EXCEED_LIMIT** | > 3 style violations | BLOCK | Surface to user; no auto-rewrite |

## L2 Execution Stages (SINGLE_STEP Pipeline)

| Stage | Engine | Function | Gate |
|-------|--------|----------|------|
| 1 | `IngestionEngine` | Load source files from `source_dirs` | — |
| 2 | `CapabilityExtractionEngine` | Extract platform capabilities from docs | — |
| 3 | `BriefAssemblyEngine` | Assemble persona-targeted sections | — |
| 4 | `StyleGateValidator` | Enforce buzzword density, absolutes | ✅ |
| 5 | `ArtifactEmission` | Write brief + run_summary to disk | — |

## Exit Disposition Mapping (Canonical X3)

| Failure Mode | Stage | Sealed Packet | X3 Disposition | terminal_class | User Action |
|--------------|-------|---------------|----------------|----------------|-------------|
| Source dirs missing | R5 (pre-L2) | `sealed_failure_packet` | `X3E_SAFE_ABSTAIN` | FAILURE | Provide valid `--source-dirs` |
| No files readable | R5 (pre-L2) | `sealed_failure_packet` | `X3E_SAFE_ABSTAIN` | FAILURE | Check file permissions / paths |
| No capabilities extracted | E3 | `sealed_failure_packet` | `X3E_SAFE_ABSTAIN` | FAILURE | Check source content quality |
| Style violations exceed limit | E4 | `sealed_violation_packet` | `X3E_SAFE_ABSTAIN` | FAILURE | Fix style profile / templates |
| Buzzword density > 5% | E4 | `sealed_violation_packet` | `X3E_SAFE_ABSTAIN` | FAILURE | Edit source / reduce marketing language |
| Unsupported absolutes detected | E4 | `sealed_violation_packet` | `X3E_SAFE_ABSTAIN` | FAILURE | Remove "always/never/guaranteed" claims |
| Evidence too old (advisory) | Exit | (no sealed packet) | `X3D_ALLOW_FINISH` (warn) | SUCCESS | Refresh architecture docs |
| Empty section (advisory) | E3 | (no sealed packet) | `X3D_ALLOW_FINISH` (warn) | DEGRADED_SUCCESS | Retry with `--retry-empty-sections` |
| Full success | E5 | `sealed_success_packet` | `X3D_ALLOW_FINISH` | SUCCESS | — |
| Full success + cache eligible | E5 | `sealed_success_packet` + `cache_commit_candidate` | `X3C_COMMIT_REQUEST_TO_UWG` then `X3D` | SUCCESS | — |

## Local Evidence Contract (FEC)

> apps_exec C0-grounded FEC produced by `apps_exec/cert/fec_producer.py` → `resolve_fec()`

```yaml
# Produced by apps_exec/cert/fec_producer.py
producer: apps_exec.cert.fec_producer
schema_version: "1.0"
grounded: true                              # True when C0 retrieval sources non-empty
retrieval_sources:                          # From C0 exec_docs collection
  - source_type: architecture_doc
    source_id: docs/architecture/adr/*.md
    freshness_days: 14
    citation_count: 12
route_id: apps_exec.execution_v1
template_ids:
  - apps_exec.brief.recruiter.v1
  - apps_exec.brief.cto.v1
  - apps_exec.brief.svp_eng.v1
  - apps_exec.brief.board.v1
evidence_sufficiency: grounded              # empty | template_only | partial | grounded
source_ladder:
  exec_docs_sources: []                     # Retrieved from C0 hybrid search
  policy_sources: []                        # From L0 policy binding
  blueprint_sources: []                       # From apps_exec config manifests
# Additional fields:
#   citation_coverage: float                # % of claims with ≥1 citation
#   freshness_score: float                    # Weighted avg source freshness
#   contradiction_flags: []                    # Detected contradictions in evidence
#   gap_list: []                             # Claims without source backing
```

## File Outputs (Sealed Artifacts)

```
artifacts/apps_exec/runs/<timestamp>/
├── exec_brief_<audience>_<trace_id[:8]>.md     # Formatted executive brief
├── run_summary_<trace_id[:8]>.json              # Provenance + gate results
├── evidence_anchor_map.json                     # Claim → source citation map
├── style_validation.json                        # Style gate detailed results
└── compiled_prompt_artifact.json               # PA output for audit replay
```

## Cross-App Integration Points

| Source App | Artifact Consumed | Usage | Boundary |
|------------|-------------------|-------|----------|
| `apps_research` | Company brief (disk) | Cross-referenced for CTO/board strategic_value sections | Reads prebuilt artifact from disk |
| `apps_eval` | Evaluation rubrics | Style gate thresholds sourced from eval harness | Config-only dependency |

> **apps_exec does NOT invoke apps_research at runtime.**
> If company brief is needed, user must run `apps_research` upstream.
> The integration is artifact-on-disk, not API call.

## Non-Goals (This Spine Does NOT)

- ❌ Side-effect actions (no external API writes, no ATS submission)
- ❌ CommitRequest for durable writes (brief is read-only artifact)
- ❌ L3 orchestration DAG (bypassed — SINGLE_STEP execution)
- ❌ Real-time web research (C0 retrieval from pre-indexed exec_docs only)
- ❌ Runtime HITL chat (review is out-of-band; HITL policy gates X3B only)
- ❌ Direct L4 writes (optional cache commit via Exit → CommitRequest → UWG only)
- ❌ Hidden cross-app execution (apps_research runs upstream, not inside apps_exec)

## See Also

- `spine_manifest.yaml` — Canonical route-type declaration (R3_SIMPLE_GROUNDED_READ)
- `config/route_registry.yaml` — L0 route contracts (SINGLE_STEP, l3_required=false)
- `engines/brief_assembly_engine.py` — Main brief composer
- `engines/capability_extraction_engine.py` — Platform capability extraction
- `validators/style_gate_validator.py` — Quality gates enforcement
- `cert/fec_producer.py` — C0-grounded FEC producer
- `__main__.py` — Canonical entrypoint with live cert mode
- `README.md` — Quick start and persona table
- `RUNBOOK.md` — On-call triage and failure modes
