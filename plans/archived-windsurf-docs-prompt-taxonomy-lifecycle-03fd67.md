---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\prompt-taxonomy-lifecycle-03fd67.md'
original_relative_path: 'prompt-taxonomy-lifecycle-03fd67.md'
source_sha256: f017884d6d035c8b70f42ffd05af8a21605d8c8fc1c3e1744e08909a037f2305
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-12'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Prompt Taxonomy & Lifecycle — Gap Analysis & Implementation Plan

Implement the complete Prompt Taxonomy (S0/D0/I0/C0/U0 authority slots) and Lifecycle
(PromptBOM → Assembly → CompiledPromptArtifact → LLM Gateway) across all enforced territories,
closing every gap identified from the freshly generated ADG (`adg_full_20260312T093508Z.json`).

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## ADG Baseline — 2026-03-12T09:35:08Z

| Metric | Value | Source |
|---|---|---|
| Modules | 3,766 | `generate_full_adg.py` |
| Entities (nodes incl. symbols) | 49,226 | sqlite `total_nodes` |
| Edges | 161,563 | sqlite `total_edges` |
| Orphan modules | 135 | snapshot `counts.orphan_module_count` |
| Graph planes | G1_imports=25,399 · G3_implements=1,885 · G4_calls=15,979 · GT_covers=4,694 · GV_violates=224 · GG_governance=110 | snapshot |
| Generates-prompt edges | 215 | `graph_plane_counts.generates_prompt` |
| Invokes-provider edges | 501 | `graph_plane_counts.invokes_provider` |
| Routes-through edges | 49 | `graph_plane_counts.routes_through` |
| Critical repair routes | 224 | E10 repair engine |
| High-confidence entities | 43,244 (avg conf 0.887) | E9 |
| `L_PG` layer modules | 57 | snapshot `by_layer` |
| Unresolved imports | 443 | snapshot |

**ADG prerequisite fix applied this session:**
`tools/dep_graph_db.py` line 65 — added `SSOT_DIR_PATHS = [ROOT / d for d in SSOT_DIRS]`
(prior `NameError` blocked every previous rebuild).

---

## Gap Analysis (ADG-Grounded)

### GAP-1 · Entire `prompt_governance` Territory is an Island — 41 of 57 L_PG Modules are Orphans

The ADG confirms every module in `agentic_core/prompt_governance/` has **zero in-degree** (fan-in = 0) at the module level. Nothing in the running system imports or calls into this territory at runtime.

Confirmed orphans with zero in-degree:

| Module | Why it Matters |
|---|---|
| `prompt_governance/contracts/slot_contracts.py` | Defines S0/D0/I0/C0/U0 dataclasses + `SLOT_ORDER` — never used at runtime |
| `prompt_governance/contracts/context_contracts.py` | C0 context contract — orphan |
| `prompt_governance/core/prompt_assembler.py` | fi=0, fo=160 — produces output but nobody calls it |
| `prompt_governance/core/prompt_entry_types.py` | Prompt constitution SSOT — orphan |
| `prompt_governance/core/prompt_loader.py` | YAML loader — orphan |
| `prompt_governance/core/governance_hub.py` | Central hub — orphan |
| `prompt_governance/core/invariant_registry.py` | Invariant registry — orphan |
| `prompt_governance/security/assembly_injection_neutralizer.py` | Injection defense — orphan |
| `prompt_governance/security/detectors/injection_detector.py` | Detector — orphan |
| `prompt_governance/validation/validate_assembly.py` | Assembly validator — orphan |
| 31 additional L_PG modules | All orphans |

**Root cause:** There is no caller anywhere that imports `prompt_governance` into the execution path. The territory was built in isolation and never wired.

---

### GAP-2 · Assembly Stage and LLM Gateway Have Zero Importers

These three modules are the backbone of the intended Lifecycle pipeline — all have **fi=0**:

| Module | Layer | fan-in | fan-out | Status |
|---|---|---|---|---|
| `L0_routing/engines/assembly_stage.py` | L0 | **0** | 50 | Orphan — nobody calls it |
| `prompt_governance/core/prompt_assembler.py` | L_PG | **0** | 160 | Orphan — nobody calls it |
| `L2_execution/enforcement/SovereignLLMGateway.py` | L2 | **0** | 125 | Orphan — nobody imports it |

The fact that all three have large fan-out (they import many dependencies) but zero fan-in means they were built as sinks, never connected to actual callers.

---

### GAP-3 · Missing Lifecycle Data Contracts — All Four Are Absent

The ADG confirms no module anywhere in the repository contains these names:

| Contract | Required By Spec | ADG Result |
|---|---|---|
| `PromptBOM` | L0 → Assembly handoff | **MISSING** |
| `CompiledPromptArtifact` | Assembly → Gateway handoff | **MISSING** |
| `TemplateManifest` | L4 Registry → Assembly | **MISSING** |
| `InstructionPacket` | L0 Router → PromptBOM builder | **MISSING** |
| `prompt_bom_builder` module | L0 Router output stage | **MISSING** |
| `template_registry` module | L4 SSOT for S0/I0 | **MISSING** |

---

### GAP-4 · 215 `generates_prompt` Edges All Bypass the Governed Pipeline

The ADG tracks a dedicated `generates_prompt` edge plane (215 edges). Analysis shows these come **entirely from `L0` scripts via `dynamic_exec`** (importlib/`__import__` calls), not from `prompt_assembler` or `assembly_stage`. This means:

- Prompts are generated dynamically at the routing layer using raw string construction
- None pass through slot-ordering enforcement (`validate_slot_order`)
- None produce a `CompiledPromptArtifact` with HMAC signature
- The governed assembly path is completely bypassed in production

---

### GAP-5 · 501 `invokes_provider` Edges — Many from `L_APP` Directly

501 edges in the `invokes_provider` plane, with significant contribution from `L_APP` (apps_rg, apps_lic):

- `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py` → `SovereignLLMGateway` (but via `routes_through`, not via `CompiledPromptArtifact`)
- `apps_rg/tools/ResumeGenerator.py`, `apps_rg/utils/providers_anthropic_client_util.py` — direct provider calls
- `apps_lic/tools/GeminiLLMClient.py` — direct Gemini calls

**Only 49 `routes_through` edges exist** (the governed path), vs 501 provider invocations — meaning **~90% of LLM calls bypass the gateway's governed entry point**.

---

### GAP-6 · Elevator Shaft Seam is a Stub with No Consumers

`L0_routing/seams/elevator_shaft_seam.py`:
- Body: `return {}` (stub)
- **fan-in = 0, fan-out = 0** — total orphan
- The C0 slot (dependency context) in `assembly_stage` therefore receives an empty dict
- JIT context loading is completely unimplemented

---

### GAP-7 · `prompt_version_store` is Orphaned

`L4_state/memory/prompt_version_store.py`:
- **fan-in = 0** — nothing reads from it
- Implements SHA-256 versioned S0/I0 storage (write-once semantics)
- In-memory only (no persistence layer)
- Never called by `assembly_stage` or `prompt_assembler`

---

### GAP-8 · 8 Orphaned `apps_shared` Prompt Modules — Shadow System

Eight `L_APP` modules constitute an ungoverned parallel prompt infrastructure:

| Module | fan-in |
|---|---|
| `apps_shared/types/prompt_optimizer_types.py` | 0 |
| `apps_shared/types/prompt_type_types.py` | 0 |
| `apps_shared/utils/prompt_enhancer_util.py` | 0 |
| `apps_shared/utils/prompt_loader_util.py` | 0 |
| `apps_shared/utils/prompt_registry_util.py` | 0 |
| `apps_shared/utils/reasoning_prompt_util.py` | 0 |
| `apps_shared/utils/stored_prompt_util.py` | 0 |
| `apps_shared/validators/resume_prompts_validator.py` | 0 |

All orphaned — they were never wired into the governed pipeline or into `apps_*` agents.

---

### GAP-9 · 224 Critical Repair Routes — No Prompt-Specific Violations in GV Plane

The `GV_violates` edge plane has 224 entries (all critical per E10 repair engine), but **zero involve prompt modules** directly. This means prompt governance is not actively violated — it is simply **ignored** (orphaned). The 224 violations are in other layer-boundary areas. Prompt governance failures are gaps, not violations.

---

### GAP-10 · No CI Enforcement for Prompt Taxonomy

- `ops_scripts/ci/` contains zero `check_*` scripts for prompt taxonomy
- `.pre-commit-config.yaml` does not wire `sovereign_precommit_no_raw_prompts_util`
- `sovereign_precommit_no_raw_prompts_util` (L0_routing/scripts) is itself an **orphan**
- `direct_prompt_compilation_validator` (L5_safety) fan-in=1, not wired to CI
- No GitHub Actions workflow for taxonomy enforcement exists

---

## Implementation Plan

### Phase 1 — Data Contracts (Foundation Layer)

**Objective:** Define the four missing contracts that the entire lifecycle depends on. No behavior — pure frozen dataclasses.

**Files to create:**

**`agentic_core/prompt_governance/contracts/prompt_bom_types.py`**
- `@dataclass(frozen=True) class PromptBOM`
- Fields: `trace_id: str`, `system_version_hash: str`, `mixins_required: tuple[str, ...]`, `raw_u0: str`, `raw_c0: dict`, `template_args: dict`, `path: Literal["A","B","C","D"]`
- Produced by: L0 Router. Consumed by: Assembly Stage.

**`agentic_core/prompt_governance/contracts/compiled_artifact_types.py`**
- `@dataclass(frozen=True) class CompiledPromptArtifact`
- Fields: `trace_id: str`, `final_system_string: str`, `final_user_string: str`, `allowed_tools_schema: tuple`, `token_estimate: int`, `signature: str` (HMAC-SHA256 over content)
- Produced by: Assembly Stage. Consumed by: SovereignLLMGateway.

**`agentic_core/prompt_governance/contracts/template_manifest_types.py`**
- `@dataclass(frozen=True) class TemplateManifest`
- Fields: `template_id: str`, `version: str`, `git_commit_hash: str`, `required_variables: tuple[str, ...]`, `schema_version: str`
- Owned by: L4 Registry. Referenced by: PromptBOM.

**`agentic_core/L0_routing/types/instruction_packet_types.py`**
- `@dataclass(frozen=True) class InstructionPacket`
- Fields: `trace_id: str`, `path: Literal["A","B","C","D"]`, `intent_class: str`, `required_mixins: tuple[str, ...]`, `escalation_threshold: float`
- Produced by: L0 path classifier. Consumed by: PromptBOM builder.

**Wire into `prompt_governance/contracts/__init__.py`:** export all four types.

**Tests:** `tests/unit/agentic_core/prompt_governance/contracts/test_lifecycle_contracts.py`
- Frozen-ness, field validation, HMAC signature round-trip for `CompiledPromptArtifact`.

---

### Phase 2 — L0 PromptBOM Builder (First Pipeline Wire)

**Objective:** Create the bridge from L0 routing intent to the Assembly Stage. This is the first module that actually connects L0 to `L_PG`.

**File to create:** `agentic_core/L0_routing/engines/prompt_bom_builder.py`
- `class PromptBOMBuilder`
- `build(packet: InstructionPacket) -> PromptBOM`
  - Fetches `system_version_hash` from `L4_state.memory.prompt_version_store`
  - Packages pointers only — no inline strings
  - Injects `trace_id` and `path`
- This module imports from `L_PG` contracts and `L4` store — must be registered as L0 in ADG

**Wire:** `path_router.py` → emits `InstructionPacket` → `PromptBOMBuilder.build()` → `PromptBOM`

**Tests:** `tests/unit/agentic_core/L0_routing/engines/test_prompt_bom_builder.py`

---

### Phase 3 — Assembly Stage Enhancement (Core Pipeline)

**Objective:** Make `assembly_stage.py` consume a `PromptBOM` and emit a `CompiledPromptArtifact`. This resolves GAP-1 (wires `L_PG` territory) and GAP-2 (gives assembly_stage a real caller).

**Modify:** `agentic_core/L0_routing/engines/assembly_stage.py`

Changes:
1. Add `assemble(bom: PromptBOM) -> CompiledPromptArtifact` as the canonical entry point
2. Load S0 from `prompt_version_store` by `bom.system_version_hash`
3. Load I0 mixin content from `template_registry` (Phase 5) by `bom.mixins_required`
4. Load C0 via `elevator_shaft_seam.load_context_jit(bom.trace_id)` (Phase 4)
5. Wrap U0 (`bom.raw_u0`) with XML delimiters
6. Call `prompt_assembler.assemble(s0, d0, i0, c0, u0)` — wires in the orphaned assembler
7. Call `validate_slot_order()` from `slot_contracts` — wires in the orphaned slot contract
8. Call `assembly_injection_neutralizer.scan(u0)` — wires in the orphaned security module
9. Call `validate_assembly.validate(assembled)` — wires in the orphaned validator
10. Compute HMAC-SHA256 signature over final strings
11. Return `CompiledPromptArtifact`

**This single change wires in at minimum 5 orphaned `L_PG` modules.**

**Tests:** `tests/unit/agentic_core/L0_routing/engines/test_assembly_stage.py` (exists — extend)

---

### Phase 4 — Elevator Shaft Implementation (C0 Slot)

**Objective:** Replace the `return {}` stub with real JIT context loading. Resolves GAP-6.

**Modify:** `agentic_core/L0_routing/seams/elevator_shaft_seam.py`

Changes:
1. `load_context_jit(trace_id: str, intent_class: str) -> dict`
2. Query `L4_state.memory.semantic_cache_manager` for relevant context chunks
3. Query `L4_state.memory.bm25_store` for keyword-matched context
4. Apply a context token budget (configurable max, default 2048 tokens)
5. Return structured dict with keys: `rag_chunks`, `ast_snapshot`, `boundary_refs`

**Constraint:** No routing logic, no decision logic — context loading only (per existing docstring).

**Tests:** `tests/unit/agentic_core/L0_routing/seams/test_elevator_shaft_seam.py`

---

### Phase 5 — L4 Template Registry (S0/I0 SSOT)

**Objective:** Implement the L4 registry that `assembly_stage` will fetch S0/I0 templates from. Resolves GAP-7 (wires `prompt_version_store`).

**File to create:** `agentic_core/L4_state/memory/template_registry.py`
- `class TemplateRegistry` (singleton, read-only)
- `get_s0(version_hash: str) -> str` — fetches S0 system prompt by hash
- `get_i0_mixin(mixin_id: str) -> str` — fetches I0 mixin by ID
- `register_template(manifest: TemplateManifest, content: str) -> str` — returns SHA-256 hash
- Backed by `prompt_version_store` for storage
- Never compiles — returns versioned string content only

**Wire:** `PromptBOMBuilder` fetches `system_version_hash` from this registry.
**Wire:** `assembly_stage` fetches S0/I0 content from this registry.

**Tests:** `tests/unit/agentic_core/L4_state/memory/test_template_registry.py`

---

### Phase 6 — LLM Gateway — Consume CompiledPromptArtifact (Execution Wire)

**Objective:** Add a governed entry point to `SovereignLLMGateway` that consumes `CompiledPromptArtifact`. Resolves GAP-2 (gives gateway a wired caller path) and begins resolving GAP-5.

**Modify:** `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`

Changes:
1. Add `execute_artifact(artifact: CompiledPromptArtifact, agent_id: str) -> LLMResponse`
2. Verify HMAC-SHA256 signature — reject with `ArtifactTamperError` if invalid
3. Translate `final_system_string` / `final_user_string` to provider-specific format
4. Inject D0 stop-sequences
5. Log `trace_id` + artifact hash to audit ledger before every call
6. Existing raw-string `execute()` path remains for backward compat — deprecated flag added

**Tests:** `tests/unit/agentic_core/L2_execution/enforcement/test_sovereign_llm_gateway_artifact.py`

---

### Phase 7 — Wire `apps_*` Callers Through Governed Path (GAP-4 / GAP-5)

**Objective:** Migrate the highest-volume direct callers to route through the governed pipeline.

**Priority callers (from ADG `routes_through` + `invokes_provider` planes):**

| File | Current | Target |
|---|---|---|
| `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py` | `routes_through SovereignLLMGateway` (symbol ref) | `execute_artifact(CompiledPromptArtifact)` |
| `apps_rg/engines/hardened_gemini_executor.py` | direct provider | `execute_artifact()` |
| `apps_rg/tools/ResumeGenerator.py` | direct provider | `execute_artifact()` |
| `apps_lic/tools/GeminiLLMClient.py` | direct provider | `execute_artifact()` |
| `apps_rg/utils/agent_executor_util.py` | direct provider | `execute_artifact()` |

**Method per caller:**
1. ADG blast-radius check (what does changing this break?)
2. Introduce `PromptBOM` construction at the call site
3. Route through `PromptBOMBuilder` → `assembly_stage.assemble()` → `execute_artifact()`
4. Remove direct provider string construction

**This is the highest-impact phase for closing GAP-4 (215 `generates_prompt` edges).**

---

### Phase 8 — Consolidate `apps_shared` Shadow System (GAP-8)

**Objective:** Eliminate the 8 orphaned parallel prompt modules in `apps_shared`.

**Process per module:**
1. Read module — determine if it duplicates `prompt_governance` capability
2. If duplicate: delete module, route any future consumers to governed equivalent
3. If unique capability: promote to `prompt_governance` as a new governed sub-module
4. Add shim at original path if any consumers discovered at runtime

**Expected outcome:** All 8 orphans deleted or absorbed. `apps_shared` prompt count → 0.

---

### Phase 9 — Activate Orphaned Enforcement Modules (GAP-1 residual)

**Objective:** Wire the remaining `L_PG` orphans that Phase 3 did not reach.

| Orphan | Wire-in Action |
|---|---|
| `governance_hub.py` | Import from `assembly_stage` as the coordination point |
| `evaluation_loader.py` | Import from `governance_hub` for evaluation prompt loading |
| `optimization/optimization_strategy.py` | Import from `assembly_stage` for token budget optimization |
| `scripts/detect_template_drift.py` | Register as CI check (Phase 10) |
| `scripts/synchronize_registry_hashes.py` | Register as CI check (Phase 10) |
| `scripts/audit_registry_linkages.py` | Register as CI check (Phase 10) |
| `scripts/dry_run_compiler.py` | Register as CI check (Phase 10) |
| `security/detectors/pii_scrubber.py` | Import from `assembly_injection_neutralizer` |
| `security/utils/injection_scan_util.py` | Import from `injection_detector` |
| `security/utils/normalization_util.py` | Import from `injection_detector` |

---

### Phase 10 — CI + Pre-Commit Enforcement (GAP-10)

**Objective:** Make taxonomy compliance mandatory on every commit and PR.

**File to create:** `ops_scripts/ci/check_prompt_taxonomy.py`
- AST scan: detect raw string prompt construction outside `L_PG` territory
- Detect `execute()` calls to `SovereignLLMGateway` (deprecated path) outside tests
- Detect `generates_prompt`-pattern code (string templates sent directly to provider) outside L_PG
- Exit 1 on violations — CI-blocking

**Modify:** `.pre-commit-config.yaml`
- Register `sovereign_precommit_no_raw_prompts_util` as a hook (resolves its orphan status)
- Register `check_prompt_taxonomy.py` as a local hook

**File to create:** `.github/workflows/prompt-taxonomy-validation.yml`
- Runs `check_prompt_taxonomy.py` on every PR
- Runs `detect_template_drift.py` to catch L4 registry drift
- Runs `synchronize_registry_hashes.py` --check mode

---

## Dependency Graph (Phase Sequencing)

```
Phase 1 (Data Contracts)
  └─ Phase 2 (PromptBOM Builder)        ← needs InstructionPacket, PromptBOM
       └─ Phase 3 (Assembly Stage)      ← needs PromptBOM, all L_PG contracts
            ├─ Phase 4 (Elevator Shaft) ← called by assembly_stage C0 load
            ├─ Phase 5 (L4 Registry)    ← called by assembly_stage S0/I0 load
            └─ Phase 6 (LLM Gateway)    ← consumes CompiledPromptArtifact
                 ├─ Phase 7 (apps_* migration) ← needs gateway artifact entry point
                 └─ Phase 9 (Activate orphans) ← needs assembly_stage wired
Phase 8 (apps_shared consolidation)   ← independent, can run parallel to Phase 7
Phase 10 (CI enforcement)             ← needs Phase 7 complete (all callers migrated)
```

---

## Success Metrics (ADG-Verifiable — Re-run `generate_full_adg.py`)

| Metric | Baseline | Target |
|---|---|---|
| `L_PG` orphan modules | 41 | 0 |
| `assembly_stage` fan-in | 0 | ≥ 3 |
| `prompt_assembler` fan-in | 0 | ≥ 1 |
| `SovereignLLMGateway` fan-in | 0 | ≥ 5 |
| `elevator_shaft_seam` fan-in | 0 | ≥ 1 |
| `prompt_version_store` fan-in | 0 | ≥ 1 |
| Lifecycle contracts missing | 4 | 0 |
| `generates_prompt` edges via `dynamic_exec` | 215 | ≤ 10 (tests only) |
| `routes_through` governed edges | 49 | ≥ 150 |
| `apps_shared` prompt orphans | 8 | 0 |
| CI taxonomy check | absent | present, blocking |

---

## Files to Create (Net-New)

| File | Phase |
|---|---|
| `agentic_core/prompt_governance/contracts/prompt_bom_types.py` | 1 |
| `agentic_core/prompt_governance/contracts/compiled_artifact_types.py` | 1 |
| `agentic_core/prompt_governance/contracts/template_manifest_types.py` | 1 |
| `agentic_core/L0_routing/types/instruction_packet_types.py` | 1 |
| `agentic_core/L0_routing/engines/prompt_bom_builder.py` | 2 |
| `agentic_core/L4_state/memory/template_registry.py` | 5 |
| `ops_scripts/ci/check_prompt_taxonomy.py` | 10 |
| `.github/workflows/prompt-taxonomy-validation.yml` | 10 |
| Tests for each new module | 1–6 |

## Files to Modify (Existing)

| File | Phase | Change Summary |
|---|---|---|
| `tools/dep_graph_db.py` | ✅ Done | Added `SSOT_DIR_PATHS` |
| `agentic_core/L0_routing/engines/assembly_stage.py` | 3 | Add `assemble(bom)` entry point, wire L_PG modules |
| `agentic_core/L0_routing/seams/elevator_shaft_seam.py` | 4 | Implement `load_context_jit` stub |
| `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | 6 | Add `execute_artifact()` entry point |
| `agentic_core/L0_routing/engines/path_router.py` | 2 | Emit `InstructionPacket` |
| `agentic_core/prompt_governance/contracts/__init__.py` | 1 | Export new contracts |
| `.pre-commit-config.yaml` | 10 | Register pre-commit hooks |
| 5 `apps_*` executor files | 7 | Migrate to `execute_artifact()` |
| 8 `apps_shared` prompt modules | 8 | Delete or absorb |

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

