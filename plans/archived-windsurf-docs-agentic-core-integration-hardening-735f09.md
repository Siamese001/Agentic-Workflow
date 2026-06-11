---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\agentic-core-integration-hardening-735f09.md'
original_relative_path: 'agentic-core-integration-hardening-735f09.md'
source_sha256: b978f341e2028f5fc0035a06dccc52db14f72698b080989a88551d5870f536a0
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Agentic-Core Integration Hardening for Resume Generation

Wire `apps_rg/scripts/generate_resume.py` through all agentic_core layers (L0–L7 + prompt_governance) with a non-bypassable Layer Execution Manifest, enforced safety gates, and regression tests — without requiring external backends (Pinecone/Redis/RL).

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


## Pre-Plan Evidence Summary

Evidence gathered via ripgrep + file reads (not assumed):

| Fact | Evidence |
|------|----------|
| `generate_resume.py` imports 0 from `agentic_core` | `rg "agentic_core" generate_resume.py` → 0 matches |
| `resume_orchestrator_engine.py` imports 0 from `agentic_core` | `rg "agentic_core" resume_orchestrator_engine.py` → 0 matches |
| `apps_rg/` has 35 `agentic_core` refs across 9 files, but NONE on the generate_resume call path | `rg "agentic_core" apps_rg/ *.py` → 35 matches in RGAgentBase, void_compliance_config, reasoning agents |
| `NervousSystemAgent` requires L4 storage, L5 safety layer, InterventionServer, GovernanceAgent | Direct read of `__init__` at lines 44–159 |
| `meta_prompts/` folder = `agentic_core/prompt_governance/meta_prompts/` (12+ jinja templates) | `find_by_name` confirmed |
| `L7_meta_learning/` has only `types/` (frozen schema artifacts, no runtime logic) | `list_dir` confirmed; `__init__.py` exports nothing |
| `artifacts/run_manifests/` does NOT exist | `find_by_name` → 0 results |
| `GovernanceAgent` is DECISION-ONLY (depth/atomicity laws), not content safety | Read of GovernanceAgent.py lines 1–60 |
| `HallucinationDetector` in apps_rg is a placeholder with simple heuristics | Read of hallucination_detector.py lines 1–50 |
| `SovereignPromptRenderer.render_tagentic()` composes meta-prompts from jinja templates | Read of sovereign_prompt_renderer.py |

### Naming Corrections (vs. original audit)
- **"meta_prompt" layer** → maps to `agentic_core/prompt_governance/` (folder `meta_prompts/` for templates, `core/sovereign_prompt_renderer.py` for rendering)
- **L7** → `agentic_core/L7_meta_learning/types/` — schema-only, no runtime behavior. MVP integration = record proposal artifacts.
- **GovernanceAgent** is NOT a content safety validator; it's structural governance. Content safety for resume gen must be implemented fresh or via `HallucinationDetector` hardening.

---

## REQUIRED Layer Manifest Keys

```
REQUIRED_LAYERS = {
    "L0_routing",
    "L1_cognition",
    "L2_execution",
    "L3_orchestration",
    "L4_state",
    "L5_safety",
    "L6_observability",
    "L7_meta_learning",
    "prompt_governance",
}
```

Each layer entry in manifest:
```json
{
  "name": "L0_routing",
  "entered": true,
  "exited": true,
  "inputs_sha256": "<hex>",
  "outputs_sha256": "<hex>",
  "component": "JDClassifier",
  "stub": false
}
```

---

## Phase 1 — Prove Isolation (Evidence Only)

**Wave 1.1 — Run evidence commands and TRACE_IMPORTS probe**

Actions:
1. Run `rg -n "agentic_core" apps_rg/scripts/generate_resume.py` — expect 0 matches
2. Run `rg -n "agentic_core" apps_rg/engines/resume_orchestrator_engine.py` — expect 0 matches
3. Run `rg -n "NervousSystemAgent|UnifiedWorkflowEngine|CognitiveNode|RootCustomsAgent|GovernanceAgent" apps_rg/scripts/ apps_rg/engines/` — expect 0 matches
4. Add a temp `TRACE_IMPORTS` block at the end of `generate_resume.py` that prints all `sys.modules` with prefix `agentic_core` after `main()` completes. Run the script. Capture output.
5. Remove temp block after capturing.

Accept: Raw outputs prove zero `agentic_core` on the generate_resume.py → ResumeOrchestratorEngine → HOP engines call path.

Commit: `evidence: prove apps_rg/scripts/generate_resume.py isolation from agentic_core`

---

## Phase 2 — Layer Execution Manifest (Stubs, No Behavioral Change)

**Wave 2.1 — Implement `layer_manifest.py` tracing module**

New file: `apps_shared/scripts/layer_manifest.py` (dependency-free, stdlib only)

Provides:
- `RunManifest` class with `start_run(run_id)`, `layer_enter(name, inputs_obj)`, `layer_exit(name, outputs_obj)`, `finalize()`
- SHA256 computed on `json.dumps(obj, sort_keys=True, default=str).encode()`
- Writes to `artifacts/run_manifests/<run_id>.json`
- `validate_manifest(manifest_path)` → raises if any REQUIRED layer missing or any layer missing `entered`/`exited`

**Wave 2.2 — Wrap `generate_resume.py` with stub spans**

Modify `generate_resume.py`:
- Import `RunManifest` from `apps_shared.scripts.layer_manifest`
- Before existing logic: `manifest.start_run(run_id)`
- Wrap existing call chain with 9 REQUIRED layer spans (stubs for now):
  - `L0_routing`: stub — passes JD through, records sha256
  - `prompt_governance`: stub — records meta_prompt digest placeholder
  - `L1_cognition`: stub — passes through
  - `L2_execution`: stub — passes through
  - `L3_orchestration`: wraps the existing `orchestrator.execute()` call
  - `L4_state`: stub — records checkpoint placeholder
  - `L5_safety`: stub — PASS verdict (will be hardened in Phase 4)
  - `L6_observability`: stub — records timing metrics
  - `L7_meta_learning`: stub — records empty proposal artifact
- After execution: `manifest.finalize()` → writes JSON
- **Hard fail**: if `manifest.finalize()` raises (missing layers / write failure) → `sys.exit(1)`

Accept: `python apps_rg/scripts/generate_resume.py` produces `artifacts/run_manifests/<run_id>.json` with all 9 REQUIRED layers, each with `entered: true`, `exited: true`, and stable SHA256 hashes.

Commit: `feat: add Layer Execution Manifest with REQUIRED layer enforcement`

---

## Phase 3 — Wire True agentic_core Entrypoints (Thin Adapter)

**Wave 3.1 — Identify instantiable agentic_core components**

Evidence probes (read-only):
1. Can `CognitiveNode()` be instantiated without backends? → Read constructor: `MetaLearningAgent` and `SemanticMemory` are try/except ImportError guarded → YES, safe with fallbacks
2. Can `MetaLearningAgent()` be instantiated? → Extends `SovereignBaseAgent` → needs mixin chain verification
3. Can `PerceptionNode()` be instantiated? → No dependencies, simple class → YES
4. Can `SovereignPromptRenderer()` render without Jinja2? → Requires jinja2 package → verify in pyproject.toml
5. `NervousSystemAgent` → NOT instantiable without backends (confirmed). **Do NOT use directly.**

**Wave 3.2 — Implement `AgenticResumeMissionAdapter`**

New file: `apps_rg/engines/agentic_resume_adapter.py`

This adapter replaces stubs with real agentic_core calls where instantiable:

| Layer | Stub → Real | Component |
|-------|------------|-----------|
| `L0_routing` | JD classification using keyword extraction (lightweight, no RootCustomsAgent which is file-routing) | New `classify_jd()` function using L0 layer_entry patterns |
| `L1_cognition` | `PerceptionNode.process()` for JD parsing + `CognitiveNode.process_async()` if instantiable, else `PerceptionNode` + `PlanningCoordinator` standalone | `agentic_core.L1_cognition.engines.perception_engine.PerceptionNode` |
| `L2_execution` | Wrap HOP dispatch in coordinator pattern (local, no UnifiedWorkflowEngine if too heavy) | Lightweight coordinator dispatch |
| `L3_orchestration` | The existing `ResumeOrchestratorEngine.execute()` IS the L3 orchestration — keep it, wrap with manifest span | `apps_rg.engines.resume_orchestrator_engine` |
| `L4_state` | Local file-based checkpoint after each HOP (no Redis/Pinecone) | `json.dump` to `artifacts/run_manifests/<run_id>/checkpoints/` |
| `L5_safety` | Hardened content validator (Phase 4 detail) | New in `apps_rg/engines/` |
| `L6_observability` | Timing + trace metrics (local, no dashboard) | Span timing in manifest |
| `L7_meta_learning` | Record `MetaLearningProposalArtifact` schema (frozen, no runtime mutation) | `agentic_core.L7_meta_learning.types.meta_learning_types` |
| `prompt_governance` | `SovereignPromptRenderer.render()` if jinja2 available, else sha256 of static prompt text | `agentic_core.prompt_governance.core.sovereign_prompt_renderer` |

Modify `generate_resume.py`:
- Import and call `AgenticResumeMissionAdapter` instead of direct `ResumeOrchestratorEngine`
- Adapter internally calls `ResumeOrchestratorEngine` (preserving HOP pipeline)
- Manifest stubs replaced with real `entered`/`exited` around actual agentic_core calls

Accept:
1. `sys.modules` filter shows `agentic_core.L1_cognition`, `agentic_core.prompt_governance`, `agentic_core.L7_meta_learning` loaded at runtime
2. Manifest spans have `stub: false` for layers with real calls
3. Generated resume output is identical to Phase 2 (behavioral equivalence)

Commit: `feat: wire agentic_core L0-L7 + prompt_governance via AgenticResumeMissionAdapter`

---

## Phase 4 — Enforce Safety (L5) and Prompt Governance

**Wave 4.1 — Implement deterministic content safety**

New file: `apps_rg/engines/resume_safety_validator.py`

Deterministic checks (no LLM required):
1. **No fabricated companies**: extract all company/org names from output; verify each exists in `master_resume` input
2. **No fabricated platforms**: extract platform/product names (SecDB, Athena, Quartz, etc.) from output; verify each exists in inputs (JD or resume)
3. **Quantified metrics guard**: any number followed by `%` or `$` or `x` must exist in input resume, or be marked `[UNVERIFIED]` and blocked by default
4. **ATS structural checks**: required sections present (summary, experience, education, skills), bullets are strings not nested objects

Returns `L5Verdict`:
```python
@dataclass
class L5Verdict:
    passed: bool
    violations: list[str]
    checked_rules: list[str]
```

If `verdict.passed == False` → `generate_resume.py` exits non-zero.

**Wave 4.2 — Implement prompt governance proof**

- Compute `sha256` of the canonical prompt text used (even if it's the system prompt / instructions embedded in the HOP engines)
- Record in manifest: `prompt_governance.digest`, `prompt_governance.applied = true`
- If `SovereignPromptRenderer` is available (jinja2 installed), render a resume-generation meta-prompt and record its digest
- If not available, compute digest of the static prompt text constants used by HOP engines
- Manifest metadata (not visible in resume content) includes `meta_prompt_id`

Accept:
1. Negative test: inject "FakeCorpTM" company name not in inputs → L5 FAIL → exit 1
2. Negative test: inject "achieved 9999% growth" metric not in inputs → L5 FAIL → exit 1
3. Positive test: normal generation → L5 PASS → exit 0
4. Manifest shows `prompt_governance.digest` and `prompt_governance.applied = true`

Commit: `feat: enforce L5 safety verdict + prompt_governance digest in manifest`

---

## Phase 5 — Regression Tests (Bypass-Proof)

**Wave 5.1 — Add test suite**

New file: `tests/integration/test_resume_manifest.py`

Tests:
1. **`test_manifest_required_layers_present`** — Run generation, load manifest, assert all 9 REQUIRED layers present with `entered: true`, `exited: true`
2. **`test_manifest_hashes_deterministic`** — Run generation twice with same inputs, assert `inputs_sha256` and `outputs_sha256` match across runs
3. **`test_bypass_legacy_path_fails`** — Attempt to call `ResumeOrchestratorEngine.execute()` directly (without adapter); assert manifest is missing/incomplete → would fail validation
4. **`test_safety_blocks_fabricated_platforms`** — Inject fabricated platform name into generated content; assert L5 verdict = FAIL
5. **`test_safety_blocks_fabricated_metrics`** — Inject fabricated quantified metric; assert L5 verdict = FAIL
6. **`test_prompt_governance_digest_present`** — Assert manifest contains `prompt_governance.digest` (non-empty hex string) and `applied = true`
7. **`test_manifest_fails_on_missing_layer`** — Programmatically remove one layer from manifest; assert `validate_manifest()` raises

Accept: `pytest tests/integration/test_resume_manifest.py -xvs` → all 7 pass. Removing manifest enforcement causes test failures.

Commit: `test: add bypass-proof regression tests for layer manifest`

---

## Files Created/Modified Summary

| File | Action | Phase |
|------|--------|-------|
| `apps_shared/scripts/layer_manifest.py` | CREATE | 2 |
| `artifacts/run_manifests/` | CREATE (dir) | 2 |
| `apps_rg/scripts/generate_resume.py` | MODIFY | 2, 3 |
| `apps_rg/engines/agentic_resume_adapter.py` | CREATE | 3 |
| `apps_rg/engines/resume_safety_validator.py` | CREATE | 4 |
| `tests/integration/test_resume_manifest.py` | CREATE | 5 |

No external dependencies introduced. No Pinecone/Redis/RL required.

---

## Acceptance Criteria (Stop When Met)

1. ✅ `python apps_rg/scripts/generate_resume.py` writes manifest with all 9 REQUIRED layers and deterministic hashes
2. ✅ `sys.modules` evidence shows `agentic_core` components loaded at runtime (L1, L7, prompt_governance at minimum)
3. ✅ L5 safety verdict enforced (FAIL → non-zero exit)
4. ✅ `prompt_governance` digest provable in manifest
5. ✅ `pytest tests/integration/test_resume_manifest.py -xvs` passes; tests fail on bypass/regression

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

