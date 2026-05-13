---
plan_id: apps-rg-structured-resume-refactor-f8c2a1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

> [!IMPORTANT]
> PORTFOLIO_STATUS: CONSOLIDATED_UNDER_MASTER
> MASTER_PLAN_REF: .windsurf/plans/apps-rg-master-governed-runtime-hardening.md
> DISPOSITION: MERGED_INTO_MASTER_WITH_CONFLICT_RESOLUTION
> SUPERSEDED_BY_PHASES: Phase 0, Phase 10, Phase 11, Phase 12
> RETAINED_SCOPE:
> - structured source resume JSON
> - tiered bullet customization
> - provider-neutral prompts
> - anti-invention guardrails
> - exact source-span extraction
> - deterministic G21/G22 checks
> - judge surface inventory
> MOVED_SCOPE:
> - runtime path inventory moves to Phase 0
> - C0 evidence trust moves to Phase 9/11
> - L6 handoff verification moves to Phase 12
> DEFERRED_SCOPE:
> - LLM judges and benchmark calibration
> CONFLICTS_RESOLVED:
> - W10 must not repair `l6_shadow_learning.py`; rewrite as canonical L6 handoff verification only

## Portfolio Consolidation Notes
This plan has been merged into the master consolidation with conflict resolution:
- Phase 0: Runtime path inventory (W0A)
- Phase 10: Structured resume schema + PA tiering + Exit G21/G22
- Phase 11: C0 fact_vectors integration with structured resume
- Phase 12: Canonical L6 handoff (NOT repair of l6_shadow_learning.py)

**CRITICAL**: W10 L6 Shadow Learning Repair is superseded by Master Phase 2 (delete/quarantine L6) and Phase 12 (canonical handoff verification). Do not implement W10 as originally written.

**Resume Shipping Critical Path:**
- W1-W6 are promoted into the Resume Shipping Critical Path (Master Plan S0-S6).
- W9 judges remain inventory only and are not required before first resume sending.
- W10 remains superseded and must not repair `l6_shadow_learning.py`.

---

# Refactor apps_rg to Structured Resume with Tiered Customization

Refactor the apps_rg resume generation pipeline to use a structured source resume JSON with separated narrative/bullets and implement tiered customization strategies per role section. Patch existing runtime paths to correctly display U0→L2 live pipeline vs L6 shadow/future-run boundaries.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Not Started
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-13

---

## Context (SCQA)

- **Situation** — Current apps_rg has multiple overlapping runtime paths (runtime/bindings, runtime/section_*, integrations/hops, engines/judges) with unclear ACTIVE vs LEGACY vs QUARANTINED status. The `pa_binding.py` exists but needs role-aware tiering. The `runtime_executive_summary.py` incorrectly implies L6 and Cache are part of live pipeline.

- **Complication** — Heavy customization roles (Unify, IBM) need bullet rewriting with JD alignment, but existing code has quarantined judges and multiple abandoned paths. Need to inventory existing surface before creating new frameworks. Core boundary must be strictly enforced: no agentic_core modifications, no G01-G29 renames, no canonical schema changes.

- **Design Decisions from 2026-05-13 Session** —
  1. **Narrative copied verbatim** — No LLM customization; U0 supplies briefing, JD, base resume
  2. **Bullets tiered by role** — Unify (current): Top 3 heavy rewrite, 4-5 moderate, 6 light. IBM: Top 2 moderate, 3-5 light. InsurTech/EY: Light reframe. Early career: Preserve verbatim.
  3. **Provider-neutral prompts** — XML-style sections, no Claude-specific wording, Qwen vLLM compatible
  4. **Anti-invention guardrails** — NO new metrics/clients/tools/domains/scope/titles/impacts without source support. INSUFFICIENT_SOURCE_SUPPORT emitted when evidence inadequate.
  5. **Exact source-span extraction** — Verbatim citation required before rewrite, JSON output with source_span, jd_alignment, rewritten_bullet, blocked_items, status
  6. **Hard core boundary** — apps_rg may consume agentic_core contracts but NEVER modify core, G01-G29, or canonical X1/X2/X3 schemas
  7. **L6 is shadow-only** — Never part of live generation pipeline; only future-run learning

- **Question** — How do we consolidate the existing fragmented apps_rg runtime surface, patch the active paths to enforce core boundaries, and implement tiered customization without creating parallel frameworks?

- **Answer** — Inventory and classify all existing paths (W0A), patch the single active dispatch→bindings→runtime path (W2/W4), inventory existing judge surface before any new creation (W9). W10 is superseded: do not repair apps_rg/runtime/l6_shadow_learning.py. Structured resume scope may only verify canonical Exit -> RuntimeExhaustBundle handoff through the master plan.

---

## Wave Overview

**Waves**: 11 total (W0A, W1–W8, W9, W10) including W6.0
**Total Estimate**: ~7,800 tokens
**Current**: W0 (pre-flight)

---

## Wave 0A — Active Runtime Path Inventory (New)

WAVE_ID: W0A
WAVE_STATUS: Not Started
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A0

**Goal**: Classify every apps_rg runtime-related file as ACTIVE, LEGACY, QUARANTINED, or OUT_OF_SCOPE. Declare exactly one active generation path.

**Initial Classification Hypothesis, to be verified by W0A**:

| Path | Classification | Rationale | Binding Evidence Required |
|------|---------------|-----------|---------------------------|
| `apps_rg/runtime/bindings/*.py` | **ACTIVE** | U0→L1→L0→C0→PA→L2→Exit spine per plan d4e8a1 | Import graph proves dispatch uses these |
| `apps_rg/runtime/dispatch/apps_rg_dispatch.py` | **ACTIVE** | Entry point for `python -m apps_rg` | Import graph + dry-run test |
| `apps_rg/runtime/section_*.py` | **LEGACY** | Per-section pipeline was aspirational; section logic moves to PA | Import graph confirms no active imports |
| `apps_rg/integrations/hops/*.py` | **QUARANTINED** | AG-RGGOV-8 runtime authority | Import graph proves no active imports |
| `apps_rg/engines/judges/*.py` | **QUARANTINED** | `executive_positioning_judge.py` has QUARANTINE notice | Import graph proves no active imports |
| `apps_rg/integrations/gates/online_judges.py` | **QUARANTINED** | RuntimeError on import | Import graph proves no active imports |
| `apps_rg/reasoning/` | **OUT_OF_SCOPE** | Unfunded complexity; no active reasoning loop | Mark archived |
| `apps_rg/tools/` | **ACTIVE** | Utility tools (word_count, context_format) used by bindings | Import graph proves bindings use these |
| `apps_rg/_quarantine/` | **QUARANTINED** | `compiler.py`, `HardenedanthropicexecutorStrategy.py`, `ResumeAssemblyAgent.py` | Already isolated |

**Acceptance**:
- **Import graph generated** via `tools/analysis/import_graph_builder.py` or static analysis
- Classification is **evidence-based**, not aspirational — every ACTIVE classification must have import proof
- **Mismatch blocks W0A completion**: If import graph shows active imports from QUARANTINED paths, W0A fails
- CI gate `check_apps_rg_runtime_path_inventory.py` verifies:
  - No imports from quarantined paths in active code
  - Exactly one active path: `apps_rg_dispatch.py` → `bindings/` → spine
  - Deprecation warnings on LEGACY paths (section_*.py)
- Tests prove: `python -m apps_rg --help` imports only from `bindings/`, `dispatch/`, `tools/`

---

## Consolidated Section Processing Design

| Section | Pipeline | Narrative | Bullets | Count | Treatment Tier | Rationale |
|---------|----------|-----------|---------|-------|----------------|-----------|
| **Headline** | U0→L1→L0→C0→PA→L2→Exit | Single X\|Y\|Z line | N/A | 1 line | **Heavy** | High JD visibility, keyword optimization critical |
| **Executive Summary** | U0→L1→L0→C0→PA→L2→Exit | 5-sentence paragraph | N/A | 5 sentences | **Heavy** | Flagship positioning, every sentence needs metric/scope/technical term |
| **Unify** | U0→L1→L0→C0→PA→L2→Exit | 1 intro sentence (verbatim) | 6 bullets | 6 | **Top 3: Heavy, 4-5: Moderate, 6: Light** | Current role, highest investment |
| **IBM** | U0→L1→L0→C0→PA→L2→Exit | 1 intro sentence (verbatim) | 5 bullets | 5 | **Top 2: Moderate, 3-5: Light** | Supporting relevance |
| **InsurTech** | U0→L1→L0→C0→PA→L2→Exit | 1 intro sentence (verbatim) | 3 bullets | 3 | **Moderate** | Background context |
| **EY** | U0→L1→L0→C0→PA→L2→Exit | 1 intro sentence (verbatim) | 3 bullets | 3 | **Light** | Older experience |
| **Early Career** | U0→L1→L0→C0→PA→L2→Exit | 1 intro sentence (verbatim) | 1 bullet | 1 | **Preserve Verbatim** | Historical record |
| **Competencies** | U0→L1→L0→C0→PA→L2→Exit | N/A | 12 entries | 12 | **Moderate** | JD-ranked, 2-4 word noun phrases |
| **Education** | **Verbatim Copy** | Exact from source | N/A | All | **None** | No LLM generation |
| **Certifications** | **Verbatim Copy** | Exact from source | N/A | All | **None** | No LLM generation |

### Treatment Tier Definitions (Role-Aware)

| Role | Bullets | Tier Assignment |
|------|---------|-----------------|
| **Unify** | 6 | 1-3: Heavy, 4-5: Moderate, 6: Light |
| **IBM** | 5 | 1-2: Moderate, 3-5: Light |
| **InsurTech** | 3 | All: Moderate |
| **EY** | 3 | All: Light |
| **Early Career** | 1 | Verbatim (no LLM) |

**Key Principle**: Narratives (intro sentences) are **copied verbatim** from structured source. Only achievement bullets go through agentic spine with tiered treatment.

---

## Allowed Change Surface

**Explicitly Allowed to Change** (app-specific paths only):

| Path | Rationale |
|------|-----------|
| `apps_rg/runtime/bindings/*` | U0→L1→L0→C0→PA→L2→Exit spine bindings |
| `apps_rg/runtime/runtime_executive_summary.py` | W4 bug patch for correct display |
| `apps_rg/runtime/l6_shadow_learning.py` | SUPERSEDED / REFERENCE ONLY — do not repair. Duplicate app-local L6 runtime must be deleted or quarantined unless live caller proof exists. Structured resume scope may only verify canonical Exit -> RuntimeExhaustBundle handoff through Master Phase 12. |
| `apps_rg/runtime/schemas/*` | App-specific schemas (SectionArtifact, etc.) |
| `apps_rg/config/domain_contract/*` | App profiles, rubrics, thresholds |
| `tests/_apps_contract/test_apps_rg_*.py` | App-specific test coverage |
| `ops_scripts/ci/check_apps_rg_*.py` | CI gates for apps_rg |
| `ops_scripts/ci/check_agentic_core_leakage.py` | W5 core boundary enforcement |
| `ops_scripts/ci/check_major_checkpoint_core_boundary.py` | W5 checkpoint validator |
| `artifacts/apps_rg/**/*` | App-specific build artifacts |

**Explicitly Forbidden to Change**:

| Path | Rationale | Violation Action |
|------|-----------|------------------|
| `agentic_core/**/*` | Core must remain app-agnostic | CI gate BLOCKS, checkpoint fails |
| Canonical G01-G29 gate definitions | Governance stability | CI gate BLOCKS, checkpoint fails |
| Canonical X1/X2/X3 schemas | Exit eval stability | CI gate BLOCKS, checkpoint fails |
| `.windsurf/rules/*` | Global governance rules | Exception: rule update plans only |
| Global plan templates (`execution-plan-template.md`) | Cross-plan consistency | Exception: template update plans only |

**Boundary Principle**: apps_rg may consume agentic_core contracts; apps_rg may NEVER modify agentic_core. All changes to the above forbidden paths require separate architectural plan with Author-Gate.

---

## Wave Manifest

- **W0A** — Active Runtime Path Inventory | ~400 tokens | STATUS: Not Started
- **W1** — Structured JSON Schema + Exit Binding Ingestion | ~800 tokens | STATUS: Not Started
- **W2** — PA Binding Tiered Prompt Patching | ~800 tokens | STATUS: Not Started
- **W3** — U0 Payload Synthesizer Structured Resume Support | ~600 tokens | STATUS: Not Started
- **W4** — Runtime Executive Summary Bug Patch | ~400 tokens | STATUS: Not Started
- **W5** — CI Gates + Core Boundary Enforcement | ~600 tokens | STATUS: Not Started
- **W6.0** — Canonical Exit Harness Wiring | ~600 tokens | STATUS: Not Started
- **W6** — Exit Gate Payload Extensions (G21/G22) | ~800 tokens | STATUS: Not Started
- **W7** — C0 Evidence Trust & Retrieval Safety | ~600 tokens | STATUS: Not Started
- **W8** — Identity, Budget, L6 Firewall + Inert Writeback | ~600 tokens | STATUS: Not Started
- **W9** — Judge Surface Consolidation (Inventory First) | ~1000 tokens | STATUS: Not Started
- **W10** — SUPERSEDED: L6 Shadow Learning (Reference Only) | ~0 tokens | STATUS: Superseded by Master Plan

---

## Wave Structure Table

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W0A | W0A.1, W0A.2 | Runtime path inventory + classification + CI gate | ~400 | Not Started |
| W1 | W1.1, W1.2 | Structured JSON schema + exit binding ingestion | ~800 | Not Started |
| W2 | W2.1, W2.2 | Patch pa_binding.py with role-aware tiering | ~800 | Not Started |
| W3 | W3.1, W3.2 | U0 payload synthesizer structured support | ~600 | Not Started |
| W4 | W4.1 | Bug patch runtime_executive_summary.py display | ~400 | Not Started |
| W5 | W5.1, W5.2 | CI gates + core boundary enforcement tests | ~600 | Not Started |
| W6.0 | W6.0 | Canonical Exit harness wiring | ~600 | Not Started |
| W6 | W6.1, W6.2, W6.3 | Exit G21/G22 payload extensions | ~800 | Not Started |
| W7 | W7.1, W7.2 | C0 evidence trust + retrieval safety | ~600 | Not Started |
| W8 | W8.1, W8.2, W8.3 | Identity + budget + L6 firewall + inert writeback envelope | ~600 | Not Started |
| W9 | W9.1, W9.2 | Judge surface inventory + consolidation decision | ~800 | Not Started |
| W10 | — | SUPERSEDED: Canonical L6 handoff owned by Master Phase 12 | ~0 | Superseded |

---

## Phase-Level Summary Table

| Phase ID | Title | Scope (files) | Est. Tokens | Status |
|----------|-------|---------------|-------------|--------|
| W0A.1 | Inventory Runtime Paths | All `runtime/`, `integrations/`, `engines/`, `_quarantine/` | ~200 | Not Started |
| W0A.2 | CI Gate + Classification Enforcement | `check_apps_rg_runtime_path_inventory.py` | ~200 | Not Started |
| W1.1 | Define Structured Resume Schema | `source_resume_structured.json` schema doc | ~400 | Not Started |
| W1.2 | Update Exit Binding Ingestion | `exit_binding.py:_ingest_docx_to_master_resume` | ~400 | Not Started |
| W2.1 | Patch PA Binding Role-Aware Tiering | `pa_binding.py` section detection + tiering | ~400 | Not Started |
| W2.2 | PA Provider-Neutral Prompt Polish | `pa_binding.py` XML structure, anti-invention | ~400 | Not Started |
| W3.1 | U0 Structured Resume Detection | `payload_synthesizer.py`, `u0_binding.py` | ~300 | Not Started |
| W3.2 | Backward Compatibility | Flat text fallback | ~300 | Not Started |
| W4.1 | Patch Runtime Summary Display | `runtime_executive_summary.py` bug fixes | ~400 | Not Started |
| W5.1 | Core Boundary CI Gate | `check_apps_rg_core_boundary.py` | ~300 | Not Started |
| W5.2 | Core Diff Prevention Tests | Tests for no core modification | ~300 | Not Started |
| W6.0 | Canonical Exit Harness Wiring | `apps_rg/runtime/bindings/exit_binding.py` | ~600 | Not Started |
| W6.1 | Exit G21 Schema Gates | `exit_binding.py` headline/bullet count | ~300 | Not Started |
| W6.2 | Exit G22 Quality Gates | Metric preservation, hash compare | ~250 | Not Started |
| W6.3 | Exit G22 Verbatim Integrity | Hash-based proof for education, certifications, early career | ~250 | Not Started |
| W7.1 | C0 Evidence Scoping | `c0_binding.py` per-section profiles | ~300 | Not Started |
| W7.2 | Retrieved Content Trust | Injection risk detection | ~300 | Not Started |
| W8.1 | Identity & Isolation | `u0_binding.py` caller/session binding | ~200 | Not Started |
| W8.2 | Budget & L6 Firewall | Token/cost caps, learning-only mode | ~200 | Not Started |
| W8.3 | Inert Writeback Envelope | `AppsRgInertWritebackCandidate` with X3C/UWG requirements | ~200 | Not Started |
| W9.1 | Judge Surface Inventory | `engines/judges/`, `integrations/gates/`, config files | ~400 | Not Started |
| W9.2 | Judge Consolidation Decision | Migrate/wrap/replace analysis | ~400 | Not Started |
| W10.1 | SUPERSEDED | No extension of l6_shadow_learning.py RuntimeExhaustBundle — canonical handoff owned by Master Phase 12 | ~0 | Superseded |
| W10.2 | SUPERSEDED | No repair of ProposalPacket — G29 work owned by Core G29 plan | ~0 | Superseded |

---

## Wave 0A — Active Runtime Path Inventory

**Phases**:
- **W0A.1** — Inventory all runtime/bindings, runtime/section_*, integrations/hops, integrations/gates, engines/judges, reasoning/, tools/, _quarantine/
- **W0A.2** — Create CI gate to enforce classification; block new files in quarantined paths

**Acceptance**:
- Classification table in plan (ACTIVE/LEGACY/QUARANTINED/OUT_OF_SCOPE)
- Exactly one active generation path: `apps_rg_dispatch.py` → `bindings/` → spine
- CI gate passes: no imports from quarantined paths in active code
- Tests prove: `python -m apps_rg --help` imports only from `bindings/` and `dispatch/`
- Deprecation warnings on LEGACY paths (section_*.py)

---

## Wave 1 — Structured JSON Schema + Exit Binding Ingestion

**Critical Reframe**: Standardize resume input to structured JSON with normalized identifiers and clear separation of narrative vs bullets.

**Phases**:
- **W1.1** — Define Structured Resume Schema with normalized IDs
- **W1.2** — Update Exit Binding to produce structured format from DOCX

**Schema Requirements** (`source_resume_v2_structured.json`):

```python
StructuredResumeV2:
  schema_version: "2.0.0"           # Explicit version
  resume_id: str                    # Unique resume identifier
  
  sections: List[Section]
  
Section:
  # Normalized identifiers
  section_id: str                    # "headline", "executive_summary", "unify", "ibm", "insurtech", "ey", "early_career", "competencies", "education", "certifications"
  company_id: Optional[str]         # Normalized: "unify_consulting", "ibm", "ernst_young", etc.
  
  # Content classification
  content_kind: str                  # "narrative_only", "bullets_only", "narrative_and_bullets", "verbatim_copy"
  
  # Processing policy
  rewrite_policy: str                # "heavy", "moderate", "light", "verbatim"
  judge_policy: str                  # "p0_full_panel", "p1_full_panel", "p2_deterministic_only", "none"
  
  # Content
  narrative: Optional[str]           # Intro sentences (verbatim for experience sections)
  bullets: List[str]                # Achievement bullets (tiered treatment)
  verbatim_fields: Optional[Dict]   # Exact copy fields for education/certifications
  
  # Provenance
  source_location: str              # JSON path in original DOCX
  extraction_confidence: float       # 0.0-1.0
```

**Normalized ID Conventions**:

| Field | Format | Examples |
|-------|--------|----------|
| `section_id` | lowercase_snake | `"headline"`, `"executive_summary"`, `"unify"`, `"ibm"`, `"insurtech"`, `"ey"`, `"early_career"`, `"competencies"`, `"education"`, `"certifications"` |
| `company_id` | lowercase_snake | `"unify_consulting"`, `"ibm"`, `"ernst_young"`, etc. |
| `content_kind` | snake_case | `"narrative_and_bullets"`, `"bullets_only"`, `"verbatim_copy"` |
| `rewrite_policy` | lowercase | `"heavy"`, `"moderate"`, `"light"`, `"verbatim"` |
| `judge_policy` | pN_descriptor | `"p0_full_panel"`, `"p2_deterministic_only"`, `"none"` |

**Acceptance**:
- `source_resume_v2_structured.json` validates against schema with `schema_version: "2.0.0"`
- Exit binding produces structured format from DOCX with all normalized IDs
- All required fields present: `section_id`, `company_id`, `content_kind`, `rewrite_policy`, `judge_policy`
- Verbatim fields (header, education, certifications) extracted exactly with `content_kind: "verbatim_copy"`
- Tests: `test_source_resume_schema_v2.py`, `test_exit_binding_structured_output.py`

---

## Wave 2 — PA Binding Tiered Prompt Patching

**Critical Reframe**: This is NOT creating a new PA layer. It patches `apps_rg/runtime/bindings/pa_binding.py` to add role-aware tiering.

**Phases**:
- **W2.1** — Add role detection from `experience[].company` → tier assignment
- **W2.2** — Polish provider-neutral XML structure, anti-invention rules

**Acceptance**:
- `pa_binding.py` detects: Unify→heavy/moderate/light, IBM→moderate/light, InsurTech/EY→light, Early Career→verbatim
- System preamble uses provider-neutral wording (no Claude references)
- Bullet rewrite prompt includes tiered treatment instructions
- Anti-invention rules embedded: NO new metrics/clients/tools/domains without source support
- Tests: `test_pa_binding_role_tiering.py` verifies correct tier per role

---

## Wave 4 — Runtime Executive Summary Bug Patch

**Critical Reframe**: This is NOT a new feature. It patches bugs in `runtime_executive_summary.py` to correctly display the live pipeline vs shadow boundaries.

**Required Display Corrections**:

```
LIVE GENERATION PIPELINE (U0 → L2):
  U0 Validate ──► L1 Plan ──► L0 Route ──► C0 Retrieve ──► PA Compose ──► L2 Execute ──► Exit Finalize
  
POST-RUNTIME (NO PRODUCTION IMPACT):
  RuntimeExhaustBundle emitted: YES/NO
  L6 Shadow Handoff emitted: YES/NO
  G29 Learning Firewall: PASS/WARN/FAIL
  
WRITE-BACK STATUS (REQUIRES UWG RECEIPTS):
  inert_writeback_candidates: <count>
  uwg_committed_writes: <count> (only with ExitReceipt)
  
NO LIVE CACHE WRITES WITHOUT UWG
NO L6 IN LIVE PIPELINE
NO AUTONOMOUS LEARNING MUTATION
```

**Removed Claims**:
- ~~"L6 part of live pipeline"~~ → L6 is shadow-only, future-run
- ~~"Cache writes durable"~~ → Only with UWG receipts
- ~~"Semantic cache immediate"~~ → inert_writeback_candidates until UWG

**Acceptance**:
- `runtime_executive_summary.py` displays corrected ASCII table
- Tests verify no L6 in live path claims
- Tests verify "inert" prefix on writeback candidates without receipts

---

## Wave 5 — Core Boundary Enforcement + Checkpoint CI

**Hard Constraints**:
- apps_rg may consume existing `agentic_core` contracts
- apps_rg may NOT modify `agentic_core/**`
- apps_rg may NOT rename or redefine G01-G29
- apps_rg may NOT modify canonical X1/X2/X3 schemas
- Violations fail CI immediately

**Phases**:
- **W5.1** — CI gate `check_agentic_core_leakage.py` + `check_major_checkpoint_core_boundary.py`
- **W5.2** — Tests verify no apps_rg literals added to core files

**CI Scripts Created**:

| Script | Location | Purpose |
|--------|----------|---------|
| `check_agentic_core_leakage.py` | `ops_scripts/ci/` | Detect apps_* literals, imports, conditionals in agentic_core |
| `check_major_checkpoint_core_boundary.py` | `ops_scripts/ci/` | Run at every major checkpoint (pre/post wave, pre-commit, pre-merge) |

**Checkpoint Schedule**:

| Checkpoint | When | Action |
|------------|------|--------|
| `pre-wave` | Before W1, W2, W3... | Verify core clean, no staged core changes with leakage |
| `post-wave` | After each wave complete | Verify no leakage introduced during wave execution |
| `pre-commit` | Before every `git commit` | Block commit if core leakage detected in staging |
| `pre-merge` | Before merge to main | Comprehensive scan + uncommitted core change check |
| `post-core-edit` | After any agentic_core edit | Immediate verification, alert on leakage |

**Acceptance**:
- CI gate fails if `git diff agentic_core/` non-empty (with fail-closed)
- CI gate fails if `grep -r "apps_rg" agentic_core/` finds new literals
- CI gate fails if G01-G29 definitions changed
- CI gate fails if X1/X2/X3 canonical schemas modified
- Checkpoint log at `artifacts/ci/checkpoint_core_boundary_log.jsonl` tracks every run
- All waves must pass `post-wave` checkpoint before marking complete

---

## Wave 6.0 — Canonical Exit Harness Wiring

**Critical Prerequisite**: G21/G22 evidence is useless if Exit never consumes it through the canonical path. Ensure apps_rg Exit uses the canonical Exit flow BEFORE adding richer G21/G22/X1D evidence.

**Required Runtime Path**:

```
apps_rg sealed output
  -> SealedWorkflowPackage or canonical terminal package
  -> ExitReviewPacket
  -> X1CheckoutResult
  -> X2AggregationResult
  -> GateMeshResult
  -> ExitDispositionReceipt
  -> RuntimeExhaustBundle
```

**Scope**:
- `apps_rg/runtime/bindings/exit_binding.py`
- `apps_rg/exit/apps_rg_exit_evidence_builder.py`
- `apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json`
- `tests/_apps_contract/test_apps_rg_exit_integration.py`

**Hard Constraints**:
- Do not modify `agentic_core`
- Do not modify canonical X1/X2/X3 schemas
- Do not redefine G01-G29
- Do not let apps_rg emit final X3 directly if canonical ExitDispositionReceipt is required
- Do not let local stub gates replace GateMeshResult
- **UNKNOWN is never PASS**

**Acceptance**:
- apps_rg constructs/normalizes the terminal output into the expected Exit input shape
- ExitReviewPacket is created for apps_rg runs
- X1CheckoutResult is produced or populated with explicit UNKNOWN/NOT_APPLICABLE reasons
- X2AggregationResult consumes exactly one X1CheckoutResult
- GateMeshResult includes required G21/G22/G23/G24/G26/G28 verdict refs
- ExitDispositionReceipt emits exactly one X3
- RuntimeExhaustBundle is produced after Exit
- **X3D_ALLOW_FINISH is impossible when material G22/G24/G28 is UNKNOWN**
- Integration test proves apps_rg no longer relies on local G24-G27 stub logic

**Tests**:
- `test_apps_rg_exit_review_packet_created.py`
- `test_apps_rg_x1_checkout_result_produced.py`
- `test_apps_rg_x2_aggregation_consumes_x1.py`
- `test_apps_rg_gate_mesh_result_includes_g21_g28.py`
- `test_apps_rg_exit_disposition_receipt_emits_x3.py`
- `test_apps_rg_runtime_exhaust_bundle_produced.py`
- `test_apps_rg_no_local_stub_gates.py`

---

## Wave 6 — Exit Gate Payload Extensions (G21/G22)

**Critical Gap Closure**: G21 (Schema/Completeness) and G22 (Quality/Safety) currently DORMANT or PARTIAL. **apps_rg emits app-owned evidence payloads** for existing canonical G21/G22 — NO canonical gate modifications.

**Core Principle**: Canonical G21/G22 gates remain unchanged. apps_rg produces **app-specific evidence receipts** that the generic Exit evaluation consumes alongside canonical signals.

**Phases**:
- **W6.1** — AppsRgSectionValidationReceipt: Per-section schema validation (headline XYZ, bullet counts, structure)
- **W6.2** — AppsRgMetricPreservationEnvelope: Metric extraction from source vs generated, preservation proof
- **W6.3** — AppsRgVerbatimIntegrityReceipt: Hash-based proof for education, certifications, early career

**New Evidence Types** (app-owned, not canonical):

```python
AppsRgSectionValidationReceipt:
  receipt_id: str                    # Unique receipt identifier
  run_id: str                        # Parent run
  section_id: str                    # "headline", "executive_summary", "unify", etc.
  g21_schema_check: G21CheckResult   # Headline XYZ format, bullet count, structure
  g22_quality_check: G22CheckResult  # Metric presence, anti-invention flags
  timestamp: datetime
  evidence_digest: str               # Hash of validation inputs

AppsRgHeadlineValidationReceipt:
  receipt_id: str
  headline_text: str
  xyz_format_valid: bool             # X|Y|Z structure
  xyz_parsed: {x: str, y: str, z: str}
  jd_keyword_density: float          # Keywords from JD present
  seniority_signal_detected: bool    # SVP/C-suite language

AppsRgMetricPreservationEnvelope:
  envelope_id: str
  section_id: str
  source_metrics: List[Metric]        # Extracted from source resume
  generated_metrics: List[Metric]   # Extracted from generated output
  preservation_ratio: float         # % of source metrics preserved
  invented_metrics: List[Metric]     # Any metrics not in source (BLOCKED)
  blocked_inventions: List[str]      # Attempted inventions caught by anti-invention

AppsRgVerbatimIntegrityReceipt:
  receipt_id: str
  section_id: str                    # "education", "certifications", "early_career"
  source_hash: str                    # SHA256 of source content
  generated_hash: str                 # SHA256 of generated content
  hash_match: bool                   # Must be True for verbatim sections
  verbatim_preservation_verdict: "PASS" | "FAIL" | "NOT_APPLICABLE"

AppsRgClaimSupportMap:
  map_id: str
  section_id: str
  claims: List[Claim]                 # Claims made in generated output
  claim_support_status: Dict[str, "SUPPORTED" | "INSUFFICIENT_EVIDENCE" | "BLOCKED"]
  source_spans: Dict[str, List[str]]  # Verbatim source supporting each claim
```

**Acceptance**:
- G21 gates ACTIVE via apps-owned receipts: Headline parses as X|Y|Z, 12 competency bullets present, all P0 sections have content
- G22 gates ACTIVE via apps-owned receipts: Metrics preserved from source, early career copied verbatim (hash match)
- **NO canonical G21/G22 changes**: All evidence is app-specific, consumed by generic Exit eval
- Exit gate emits enriched payload with per-section gate results
- Tests: `test_apps_rg_section_validation_receipt.py`, `test_apps_rg_metric_preservation.py`, `test_apps_rg_verbatim_integrity.py`
- Checkpoint: `post-wave W6` proves no modifications to `agentic_core/**/g21_*.py` or `**/g22_*.py`

---

## Wave 7 — C0 Evidence Trust & Retrieval Safety

**Critical Gap Closure**: G08 (Evidence Trust) and G13 (Retrieval Safety) currently UNFUNDED. **C0 remains evidence-only** — NO answer generation, NO prompt assembly, NO direct L4 writes.

**Core Principle**: C0 supplies evidence to PA/L2. C0 does not generate answers, compile prompts, or write to L4. Apps-specific evidence tracing captures provenance.

**Phases**:
- **W7.1** — AppsRgEvidenceTraceMap: Per-section evidence provenance with full traceability
- **W7.2** — Retrieved Content Trust: Injection risk detection, source span verification, blocked claims tracking

**New Evidence Type** (app-owned trace map):

```python
AppsRgEvidenceTraceMap:
  map_id: str
  run_id: str
  request_id: str
  section_id: str                    # Section this evidence supports
  
  # Provenance hashes
  source_resume_hash: str           # Hash of full source resume
  jd_hash: str                      # Hash of job description
  briefing_hash: str                # Hash of research briefing
  
  # Retrieval trace
  retrieval_query_hash: str         # Hash of query sent to retriever
  retrieved_chunk_refs: List[str]   # References to retrieved chunks
  retrieved_chunk_hashes: List[str] # Verification hashes
  
  # Source-to-claim mapping
  source_span_refs: List[SourceSpan] # Exact source spans available
  claim_refs: List[ClaimRef]        # Claims that will be made
  blocked_claims: List[BlockedClaim] # Claims blocked due to insufficient evidence
  
  # Status
  support_status: "SUFFICIENT" | "PARTIAL" | "INSUFFICIENT"
  injection_risk_score: float       # 0.0-1.0, threshold at 0.15
  content_safety_verdict: "PASS" | "REVIEW" | "BLOCK"
  
  # Contract reference
  final_evidence_contract_ref: str   # Reference to C0 FinalEvidenceContract

SourceSpan:
  span_id: str
  source_location: str               # JSON path in source resume
  verbatim_text: str                # Exact text
  hash: str                         # Verification hash

ClaimRef:
  claim_id: str
  claim_text: str                   # The claim to be made
  supporting_span_ids: List[str]     # SourceSpan IDs that support this
  support_status: "VERIFIED" | "UNVERIFIED" | "BLOCKED"

BlockedClaim:
  claim_text: str                   # Claim that was blocked
  reason: "NO_SOURCE_SUPPORT" | "CONTRADICTS_SOURCE" | "INJECTION_RISK" | "SAFETY"
  required_source_type: str          # What evidence would be needed
```

**Acceptance**:
- C0 retrieves only evidence relevant to section being generated (per-section scoping)
- **NO C0 answer generation**: C0 supplies evidence, PA/L2 generate answers
- **NO C0 prompt assembly**: PA composes prompts
- **NO C0 direct L4 writes**: All writes via Exit/X3 or inert until UWG
- Retrieved content hash-verified against source (retrieved_chunk_hashes)
- No evidence cross-contamination between sections (per-section trace maps)
- Injection risk score computed per evidence item (threshold 0.15)
- Blocked claims tracked with reasons (NO_SOURCE_SUPPORT, CONTRADICTS_SOURCE, etc.)
- Tests: `test_apps_rg_evidence_trace_map.py`, `test_c0_no_answer_generation.py`, `test_c0_no_direct_l4_write.py`
- Checkpoint: `post-wave W7` proves no C0 code changes that add answer generation or L4 write paths

---

## Wave 8 — Identity, Budget, L6 Firewall + Inert Writeback

**Phases**:
- **W8.1** — Identity & Isolation: U0 caller binding, session isolation
- **W8.2** — Budget & L6 Firewall: Token/cost caps, L6 learning-only mode enforcement
- **W8.3** — Inert Writeback Candidate Envelope: Distinguish candidates from committed writes

**New Evidence Type** (W8.3 — inert writeback envelope):

```python
AppsRgInertWritebackCandidate:
  candidate_id: str
  run_id: str
  section_id: str
  
  # Content
  proposed_content: str             # Content that could be written back
  content_hash: str                 # Verification hash
  
  # Admission requirements
  requires_x3c: bool = True         # Requires X3C exit certification
  requires_uwg_admission: bool = True  # Requires UWG approval
  
  # Status (initially inert)
  durable_commit_occurred: bool = False  # FALSE until UWG admits
  inert_until_uwg: bool = True      # TRUE until admitted
  
  # Timeline
  created_at: datetime
  x3c_certification_ref: Optional[str]  # Populated after X3C
  uwg_admission_ref: Optional[str]    # Populated after UWG approval
  committed_at: Optional[datetime]    # Populated after durable commit

RuntimeExhaustBundle (extended):
  # ... existing fields ...
  inert_writeback_candidates: List[AppsRgInertWritebackCandidate]
  uwg_committed_writes: List[AppsRgInertWritebackCandidate]  # Subset with durable_commit_occurred=True
```

**Runtime Summary Display** (must distinguish):

```
POST-RUNTIME STATUS:
  X3C Certification: PASS/WARN/FAIL
  
WRITE-BACK STATUS:
  inert_writeback_candidates: <count> (requires X3C + UWG)
  uwg_committed_writes: <count> (durable commits with receipts)
  
L6 SHADOW (FUTURE-RUN ONLY):
  L6 Shadow Handoff: YES/NO
  G29 Learning Firewall: PASS/WARN/FAIL
  inert_proposals: <count> (gauntlet→UWG→L4 path only)
```

**Acceptance**:
- U0 validates caller identity, binds to session
- Budget caps enforced (token limit, cost limit)
- L6 operates in learning-only mode (no production impact)
- G29 firewall receipt required for any L6 output activation
- **W8.3**: Runtime summary distinguishes `inert_writeback_candidates` from `uwg_committed_writes`
- **W8.3**: `durable_commit_occurred=False` for all candidates until UWG receipt present
- Tests: `test_apps_rg_inert_writeback_candidate.py`, `test_runtime_summary_inert_vs_committed.py`

---

## Wave 9 — Judge Surface Consolidation (Inventory First)

**Critical Reframe**: Do NOT create new judge framework until existing surface is inventoried.

**Existing Files to Inventory**:

| File | Status | Content | Decision |
|------|--------|---------|----------|
| `engines/judges/executive_positioning_judge.py` | QUARANTINED | RuntimeError on import | Keep quarantined; reference for prompts only |
| `engines/judges/__init__.py` | QUARANTINED | Empty | Keep quarantined |
| `config/domain_contract/judge_profile.resume_generation.v1.json` | ACTIVE | Dimension definitions, thresholds | **WRAP** — Use as config source for X1D |
| `config/domain_contract/judge_prompts.yaml` | ACTIVE | LLM-as-judge prompts | **WRAP** — Use as prompt templates for X1D |
| `config/domain_contract/grader_roster.yaml` | ACTIVE | Grader references | **WRAP** — Use as roster spec for X1D |
| `integrations/gates/online_judges.py` | QUARANTINED | RuntimeError on import | Keep quarantined; do not use |
| `integrations/hops/*` | QUARANTINED | Runtime authority | Keep quarantined; no judge calls from here |

**Judge Role Boundary** (strict enforcement):

```
JUDGE PRODUCES X1D EVIDENCE ONLY

Judges MAY:
  ✓ Produce X1D evidence packets (JudgeResult, scores, rationale)
  ✓ Emit quality assessments with confidence scores
  ✓ Flag insufficient evidence or blocked claims
  ✓ Recommend retry or HITL (advisory only)

Judges MAY NOT:
  ✗ Emit GateVerdict (PASS/FAIL/BLOCK) — X3 owns this
  ✗ Emit X3 disposition — Exit/X3 owns final say
  ✗ Trigger retry or regeneration — L3/L4 orchestration owns this
  ✗ Mutate current-run state — shadow-only
  ✗ Write directly to L4 — must route through gauntlet/UWG
  ✗ Autonomously PASS P0 sections when uncalibrated — advisory only

Copy-verbatim sections (education, certifications, early career):
  → Use deterministic checks only (hash compare, schema validation)
  → NO subjective LLM judges
  → Judges produce no evidence for these sections

Calibration requirements:
  UNCALIBRATED judges → advisory_only=True, no autonomous PASS
  CALIBRATED judges (Spearman ≥ 0.80) → may contribute to PASS with deterministic checks
```

**Inventory Decision Matrix**:

| Option | Action | When |
|--------|--------|------|
| **Migrate** | Move working code to new location | If existing code is sound but misplaced |
| **Wrap** | Adapter layer around existing config | If existing config is valid but needs runtime |
| **Replace** | New implementation | If existing code is fundamentally broken |

**Phases**:
- **W9.1** — Complete inventory of all judge-related files with classification + Judge Role Boundary documentation
- **W9.2** — Decision: Migrate/Wrap/Replace per file; do not create parallel framework

**Acceptance**:
- Inventory table complete with all 7+ files classified
- **Judge Role Boundary** documented and enforced: Judges produce X1D evidence only, no GateVerdict, no X3, no retry, no L4 write, no autonomous PASS when uncalibrated
- Decision recorded for each: Migrate/Wrap/Replace
- No new `apps_rg/runtime/judges/` created until inventory complete
- If "Wrap" chosen: Adapter uses existing config files as SSOT
- If "Replace" chosen: Explicit rationale why existing config cannot be used
- Tests: `test_judge_produces_x1d_only.py`, `test_judge_no_gate_verdict.py`, `test_uncalibrated_advisory_only.py`, `test_copy_verbatim_no_judges.py`

---

## Wave 10 — SUPERSEDED / REFERENCE ONLY: Canonical L6 Handoff Verification Only

**SUPERSEDED ORIGINAL INTENT — DO NOT IMPLEMENT**

The original W10 intent was to repair `apps_rg/runtime/l6_shadow_learning.py` by extending duplicate local classes such as RuntimeExhaustBundle, SectionCompletedEvalRecord, AggregateCompletedEvalRecord, and ProposalPacket.

**Resolution:**
- Do not repair `apps_rg/runtime/l6_shadow_learning.py`.
- Do not extend duplicate app-local RuntimeExhaustBundle or ProposalPacket classes.
- Do not create or preserve an app-local L6 runtime engine.
- Delete or quarantine the duplicate app-local L6 runtime unless live caller proof exists.
- Structured resume may only verify canonical Exit -> RuntimeExhaustBundle handoff.
- G29 and promotion proof fields remain owned by the separate Core G29 plan.

**Reference-only historical requirements, superseded:**
- RuntimeExhaustBundle ref completion
- SectionCompletedEvalRecord enrichment
- AggregateCompletedEvalRecord enrichment
- ProposalPacket promotion path fields
- l6_shadow_learning.py acceptance tests

**Active acceptance for structured resume scope:**
- No change to `apps_rg/runtime/l6_shadow_learning.py`.
- No active W10 implementation task remains in this plan.
- Any canonical L6 handoff verification is owned by Master Phase 12.
- Any G29/promotion proof work is owned by `core-l6-g29-promotion-proof-hardening-d9e3b2.md`.

---

## Core Boundary Contract

```
APPS_RG BOUNDARY — NON-NEGOTIABLE

apps_rg MAY:
  ✓ Import and use agentic_core contracts (ValidatedRequest, L1PlanContract, etc.)
  ✓ Implement app-specific logic in apps_rg/** only
  ✓ Consume canonical G01-G29 gates via Exit binding
  ✓ Produce X1D evidence for X2 aggregation → X3 disposition
  ✓ Shadow learning in L6 (strictly future-run)

apps_rg MAY NOT:
  ✗ Modify any file in agentic_core/**
  ✗ Rename or redefine G01-G29
  ✗ Modify canonical X1/X2/X3 schemas
  ✗ Import from quarantined paths (integrations/hops, engines/judges)
  ✗ Emit autonomous PASS from uncalibrated judges
  ✗ Run subjective judges for copy-verbatim sections
  ✗ Claim L6 in live pipeline
  ✗ Claim durable writes without UWG receipts

VIOLATION = CI FAIL (run_contract_gates.py)
```

---

## Definition of Done

| DoD | Criterion | Verification | Priority |
|-----|-----------|--------------|----------|
| DoD-1 | W0A: Runtime paths classified | Inventory table committed, CI gate passes | P0 |
| DoD-2 | W1: Structured JSON schema | `source_resume_v2_structured.json` validates | P0 |
| DoD-3 | W2: PA role-aware tiering | Tests verify Unify→heavy/moderate/light, IBM→moderate/light | P0 |
| DoD-4 | W3: U0 structured support | `payload_synthesizer.py` detects structured vs flat | P0 |
| DoD-5 | W4: Runtime summary bug patch | Display shows U0→L2 only, L6 shadow separate, no cache claims | P0 |
| DoD-6 | W5: Core boundary enforced | CI gate blocks core diffs, G01-G29 changes, X1/X2/X3 schema changes; checkpoint CI passes | P0 |
| DoD-7 | W6.0: Canonical Exit harness wired | ExitReviewPacket → X1 → X2 → GateMesh → ExitDisposition → ExhaustBundle proven | P0 |
| DoD-8 | W6: Exit G21/G22 active | Headline XYZ format, bullet count, metric preservation enforced | P0 |
| DoD-9 | W7: C0 evidence trace map | Per-section evidence provenance with injection risk scoring | P0 |
| DoD-10 | W8: Identity/budget/L6 + inert writeback | UWG receipts required for durable commits; L6 shadow-only | P0 |
| DoD-11 | W9: Judge inventory complete | All 7+ files classified; Migrate/Wrap/Replace decision recorded | P0 |
| DoD-12 | W9: No parallel framework | No new `apps_rg/runtime/judges/` until inventory complete | P0 |
| DoD-13 | W10: SUPERSEDED / REFERENCE ONLY | No repair of l6_shadow_learning.py; canonical L6 handoff owned by Master Phase 12 | P0 |

---

## CI Checkpoint Commands (Run at Every Major Boundary)

```bash
# Pre-wave checkpoint (run before starting any wave)
python ops_scripts/ci/check_major_checkpoint_core_boundary.py --checkpoint pre-wave --wave W1

# Post-wave checkpoint (run after completing any wave)
python ops_scripts/ci/check_major_checkpoint_core_boundary.py --checkpoint post-wave --wave W1

# Pre-commit checkpoint (run before git commit)
python ops_scripts/ci/check_major_checkpoint_core_boundary.py --checkpoint pre-commit

# Pre-merge checkpoint (run before merging to main)
python ops_scripts/ci/check_major_checkpoint_core_boundary.py --checkpoint pre-merge

# Post-core-edit checkpoint (run after any agentic_core modification)
python ops_scripts/ci/check_major_checkpoint_core_boundary.py --checkpoint post-core-edit

# Full suite (comprehensive check)
python ops_scripts/ci/check_major_checkpoint_core_boundary.py --checkpoint full-suite
```

## Verification Command Checklist

```bash
# W0A: Runtime path classification
python -m pytest tests/_apps_contract/test_runtime_path_inventory.py -v
python -m pytest tests/_apps_contract/test_import_graph_no_quarantine.py -v
python ops_scripts/ci/check_apps_rg_runtime_path_inventory.py

# W1: Structured JSON schema + normalized IDs
python -m pytest tests/_apps_contract/test_source_resume_schema_v2.py -v
python -m pytest tests/_apps_contract/test_exit_binding_structured_output.py -v
python -m pytest tests/_apps_contract/test_normalized_ids_present.py -v

# W2: PA role-aware tiering
python -m pytest tests/_apps_contract/test_pa_binding_role_tiering.py -v

# W3: U0 structured support
python -m pytest tests/_apps_contract/test_u0_structured_resume_detection.py -v

# W4: Runtime summary display
python -m pytest tests/_apps_contract/test_runtime_summary_display.py -v
python -m pytest tests/_apps_contract/test_no_l6_in_live_path.py -v
python -m pytest tests/_apps_contract/test_inert_prefix_on_candidates.py -v

# W5: Core boundary + checkpoint CI
python ops_scripts/ci/check_agentic_core_leakage.py
python ops_scripts/ci/check_major_checkpoint_core_boundary.py --checkpoint full-suite
python -m pytest tests/_apps_contract/test_core_boundary.py -v
python -m pytest tests/_apps_contract/test_no_core_modifications.py -v

# W6.0: Canonical Exit harness wiring
python -m pytest tests/_apps_contract/test_apps_rg_exit_integration.py -v
python -m pytest tests/_apps_contract/test_apps_rg_exit_review_packet_created.py -v
python -m pytest tests/_apps_contract/test_apps_rg_x1_checkout_result_produced.py -v
python -m pytest tests/_apps_contract/test_apps_rg_x2_aggregation_consumes_x1.py -v
python -m pytest tests/_apps_contract/test_apps_rg_gate_mesh_result_includes_g21_g28.py -v
python -m pytest tests/_apps_contract/test_apps_rg_exit_disposition_receipt_emits_x3.py -v
python -m pytest tests/_apps_contract/test_apps_rg_runtime_exhaust_bundle_produced.py -v
python -m pytest tests/_apps_contract/test_apps_rg_no_local_stub_gates.py -v
python -m pytest tests/_apps_contract/test_apps_rg_unknown_never_pass.py -v
python -m pytest tests/_apps_contract/test_apps_rg_x3d_no_allow_on_unknown_material.py -v

# W6: Exit G21/G22 + apps-owned evidence receipts
python -m pytest tests/_apps_contract/test_apps_rg_section_validation_receipt.py -v
python -m pytest tests/_apps_contract/test_apps_rg_headline_validation_receipt.py -v
python -m pytest tests/_apps_contract/test_apps_rg_metric_preservation.py -v
python -m pytest tests/_apps_contract/test_apps_rg_verbatim_integrity.py -v
python -m pytest tests/_apps_contract/test_apps_rg_claim_support_map.py -v
python -m pytest tests/_apps_contract/test_no_canonical_g21_g22_changes.py -v

# W7: C0 evidence trust + AppsRgEvidenceTraceMap
python -m pytest tests/_apps_contract/test_apps_rg_evidence_trace_map.py -v
python -m pytest tests/_apps_contract/test_c0_no_answer_generation.py -v
python -m pytest tests/_apps_contract/test_c0_no_prompt_assembly.py -v
python -m pytest tests/_apps_contract/test_c0_no_direct_l4_write.py -v
python -m pytest tests/_apps_contract/test_injection_risk_score.py -v
python -m pytest tests/_apps_contract/test_blocked_claims_tracking.py -v

# W8: Identity, budget, L6 firewall + inert writeback
python -m pytest tests/_apps_contract/test_u0_identity_binding.py -v
python -m pytest tests/_apps_contract/test_budget_caps.py -v
python -m pytest tests/_apps_contract/test_l6_learning_only_mode.py -v
python -m pytest tests/_apps_contract/test_apps_rg_inert_writeback_candidate.py -v
python -m pytest tests/_apps_contract/test_runtime_summary_inert_vs_committed.py -v
python -m pytest tests/_apps_contract/test_durable_commit_requires_uwg.py -v

# W9: Judge inventory + role boundary
python -m pytest tests/_apps_contract/test_judge_surface_inventory.py -v
python -m pytest tests/_apps_contract/test_judge_produces_x1d_only.py -v
python -m pytest tests/_apps_contract/test_judge_no_gate_verdict.py -v
python -m pytest tests/_apps_contract/test_uncalibrated_advisory_only.py -v
python -m pytest tests/_apps_contract/test_copy_verbatim_no_judges.py -v

# W10: SUPERSEDED — no active tests (canonical L6 handoff owned by Master Phase 12)
# Historical reference only — do not repair l6_shadow_learning.py

# Full suite
python -m pytest tests/_apps_contract/ -v --tb=short

---

## Closeout Receipt (To Be Filled on Completion)

| Section | Changed | Lines Added | Lines Removed |
|---------|---------|-------------|---------------|
| W0A Active Runtime Path Inventory | ☐ | | |
| W1 Structured JSON Schema | ☐ | | |
| W2 PA Tiered Patching | ☐ | | |
| W3 U0 Structured Support | ☐ | | |
| W4 Runtime Summary Bug Patch | ☐ | | |
| W5 Core Boundary Enforcement + Checkpoint CI | ☐ | ~500 | ~0 |
| W6.0 Canonical Exit Harness Wiring | ☐ | ~600 | ~0 |
| W6 Apps-Owned G21/G22 Receipts | ☐ | ~800 | ~0 |
| W7 C0 Evidence Trace Map | ☐ | ~600 | ~0 |
| W8 Identity/Budget/L6 + Inert Writeback | ☐ | ~600 | ~0 |
| W9 Judge Surface Consolidation | ☐ | | |
| W10 SUPERSEDED / REFERENCE ONLY — Canonical L6 handoff verification only | N/A | — | — |
| **New CI Scripts** | | | |
| `check_agentic_core_leakage.py` | ☐ | ~280 | ~0 |
| `check_major_checkpoint_core_boundary.py` | ☐ | ~350 | ~0 |

**Files Changed List**:
- (To be filled on completion)

**Tests Added**: 
- (To be filled on completion)

**Verification Results**:
- (To be filled on completion)

---

## References

### Active Runtime Files
- Active runtime bindings: `apps_rg/runtime/bindings/*.py`
- Active dispatch: `apps_rg/runtime/dispatch/apps_rg_dispatch.py`
- PA binding (to patch): `apps_rg/runtime/bindings/pa_binding.py`
- Runtime summary (to patch): `apps_rg/runtime/runtime_executive_summary.py`
- L6 shadow (SUPERSEDED / REFERENCE ONLY — do not repair): `apps_rg/runtime/l6_shadow_learning.py`

### CI Checkpoint Scripts (New)
- Core leakage detection: `ops_scripts/ci/check_agentic_core_leakage.py`
- Major checkpoint validator: `ops_scripts/ci/check_major_checkpoint_core_boundary.py`
- Checkpoint audit log: `artifacts/ci/checkpoint_core_boundary_log.jsonl`

### Judge Inventory Files
- Existing judge config: `apps_rg/config/domain_contract/judge_profile.resume_generation.v1.json`
- Existing judge prompts: `apps_rg/config/domain_contract/judge_prompts.yaml`
- Existing grader roster: `apps_rg/config/domain_contract/grader_roster.yaml`
- Quarantined engines: `apps_rg/engines/judges/*.py`
- Quarantined gates: `apps_rg/integrations/gates/online_judges.py`

### Related Plans
- Plan d4e8a1 (runtime wiring): `.windsurf/plans/apps-rg-runtime-wiring-completion-d4e8a1.md`
- Plan c8b3e1 (governance): `.windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md`

---

## Out Of Scope

- Creating new `apps_rg/runtime/judges/` framework (W9 decides Migrate/Wrap/Replace first)
- L4 writeback execution (future plan)
- UWG promotion decisions (Exit/UWG scope)
- Real LLM-judge calibration with Spearman ≥ 0.80 (requires human-labeled corpus)
- Production-log mining with PII redaction (future plan)
