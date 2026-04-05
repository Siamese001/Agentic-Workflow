# Prompt Governance Gap Analysis — Phase 1 Evidence

**Date:** 2026-02-20
**Baseline Commit:** `6f71bee8671c9f41f3b4c968f1bd4369e070d393`
**Scope:** `agentic_core/prompt_governance/**` — NO behavior change

---

## Wave 1 — Baseline Capture + Deterministic Inventory

### 1.1 Git Baseline

```
git rev-parse HEAD
6f71bee8671c9f41f3b4c968f1bd4369e070d393

git status --porcelain
(clean)

python -V
Python 3.12.10
```

### 1.2 Prompt Governance File Inventory (86 files)

```
agentic_core/prompt_governance/__init__.py
agentic_core/prompt_governance/core/__init__.py
agentic_core/prompt_governance/core/governance_hub.py
agentic_core/prompt_governance/core/prompt_assembler.py
agentic_core/prompt_governance/core/sovereign_prompt_renderer.py
agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md
agentic_core/prompt_governance/meta_prompts/__init__.py
agentic_core/prompt_governance/meta_prompts/adversarial_escalation.jinja
agentic_core/prompt_governance/meta_prompts/adversarial_self_test.jinja
agentic_core/prompt_governance/meta_prompts/agent_prioritization.jinja
agentic_core/prompt_governance/meta_prompts/autonomous_mission_resume.jinja
agentic_core/prompt_governance/meta_prompts/convergence_planning.jinja
agentic_core/prompt_governance/meta_prompts/emergent_capability_discovery.jinja
agentic_core/prompt_governance/meta_prompts/evolution_directive.jinja
agentic_core/prompt_governance/meta_prompts/immune_response.jinja
agentic_core/prompt_governance/meta_prompts/meta_agent_activation.jinja
agentic_core/prompt_governance/meta_prompts/meta_convergence_forecast.jinja
agentic_core/prompt_governance/meta_prompts/meta_coordination_directive.jinja
agentic_core/prompt_governance/meta_prompts/prompt_selection.jinja
agentic_core/prompt_governance/meta_prompts/red_team_governance.jinja
agentic_core/prompt_governance/meta_prompts/red_team_scope_validator.jinja
agentic_core/prompt_governance/meta_prompts/self_reflection.jinja
agentic_core/prompt_governance/meta_prompts/sovereign_convergence_orchestrator.jinja
agentic_core/prompt_governance/meta_prompts/sovereign_orchestrator.jinja
agentic_core/prompt_governance/optimization/__init__.py
agentic_core/prompt_governance/optimization/optimization_strategy.py
agentic_core/prompt_governance/prompt_entry_types.py
agentic_core/prompt_governance/prompt_loader.py
agentic_core/prompt_governance/registry/backups/__init__.py
agentic_core/prompt_governance/registry/prompt_registry_config.json
agentic_core/prompt_governance/registry/registry.json
agentic_core/prompt_governance/scripts/audit_registry_linkages.py
agentic_core/prompt_governance/scripts/cleanup_duplicates_util.py
agentic_core/prompt_governance/scripts/detect_template_drift.py
agentic_core/prompt_governance/scripts/dry_run_compiler.py
agentic_core/prompt_governance/scripts/file_intent.py
agentic_core/prompt_governance/scripts/harden_templates.py
agentic_core/prompt_governance/scripts/import_violation_visitor.py
agentic_core/prompt_governance/scripts/synchronize_registry_hashes.py
agentic_core/prompt_governance/scripts/template_render_visitor.py
agentic_core/prompt_governance/security/__init__.py
agentic_core/prompt_governance/security/adversarial/*.jinja (11 files)
agentic_core/prompt_governance/security/detectors/__init__.py
agentic_core/prompt_governance/security/detectors/injection_detector.py
agentic_core/prompt_governance/security/detectors/pii_scrubber.py
agentic_core/prompt_governance/security/utils/__init__.py
agentic_core/prompt_governance/security/utils/injection_scan_util.py
agentic_core/prompt_governance/security/utils/normalization_util.py
agentic_core/prompt_governance/security/validators/__init__.py
agentic_core/prompt_governance/security/validators/output_schema_validator.py
agentic_core/prompt_governance/templates/*.jinja (23 files)
agentic_core/prompt_governance/utils/__init__.py
agentic_core/prompt_governance/validate_assembly.py
agentic_core/prompt_governance/validation/validate_assembly.py
```

### 1.3 Test Files Referencing prompt_governance (57 files)

```
tests/agentic_core/prompt_governance/core/test_governance_hub.py
tests/agentic_core/prompt_governance/core/test_prompt_assembler.py
tests/agentic_core/prompt_governance/core/test_sovereign_prompt_renderer.py
tests/agentic_core/prompt_governance/domain/test_prompt_entry_types.py
tests/agentic_core/prompt_governance/optimization/test_optimization_strategy.py
tests/agentic_core/prompt_governance/scripts/test_audit_registry_linkages.py
tests/agentic_core/prompt_governance/scripts/test_cleanup_duplicates_util.py
tests/agentic_core/prompt_governance/scripts/test_detect_template_drift.py
tests/agentic_core/prompt_governance/scripts/test_dry_run_compiler.py
tests/agentic_core/prompt_governance/scripts/test_file_intent.py
tests/agentic_core/prompt_governance/scripts/test_harden_templates.py
tests/agentic_core/prompt_governance/scripts/test_import_violation_visitor.py
tests/agentic_core/prompt_governance/scripts/test_synchronize_registry_hashes.py
tests/agentic_core/prompt_governance/scripts/test_template_render_visitor.py
tests/agentic_core/prompt_governance/security/test_injection_detector.py
tests/agentic_core/prompt_governance/security/test_pii_scrubber.py
tests/agentic_core/prompt_governance/test_prompt_entry_types.py
tests/architecture/test_prompt_governance_no_orphans.py
tests/unit/agentic_core/prompt_governance/test_prompt_loader.py
tests/unit/agentic_core/prompt_governance/security/test_output_schema_validation_gate.py
tests/unit/agentic_core/prompt_governance/security/test_injection_normalization_util.py
tests/unit/agentic_core/prompt_governance/security/test_injection_signatures_v2.py
tests/unit/agentic_core/prompt_governance/security/test_injection_wiring_non_fenced_joinpoints.py
(+ 34 additional files with indirect references)
```

---

## Wave 2 — Entry Points + Capability-to-Code Mapping

### 2.1 Entry Points (def get_/build_/render_/load_)

| File | Line | Symbol |
|------|------|--------|
| `core/prompt_assembler.py` | 542 | `get_prompt_assembler()` |
| `core/sovereign_prompt_renderer.py` | 202 | `render_tagentic()` |
| `core/sovereign_prompt_renderer.py` | 264 | `get_template_schema()` |
| `core/sovereign_prompt_renderer.py` | 280 | `get_sovereign_prompt_renderer()` |
| `prompt_entry_types.py` | 240 | `get_constitution()` |
| `prompt_entry_types.py` | 252 | `get_prompt()` |
| `prompt_entry_types.py` | 263 | `get_template()` |
| `prompt_entry_types.py` | 275 | `get_persona()` |
| `prompt_loader.py` | 50 | `load_prompt()` |
| `prompt_loader.py` | 103 | `get_template()` |
| `scripts/audit_registry_linkages.py` | 14 | `load_registry()` |
| `scripts/detect_template_drift.py` | 16 | `load_registry()` |
| `scripts/synchronize_registry_hashes.py` | 16 | `load_registry()` |
| `validation/validate_assembly.py` | 41 | `load_manifest()` |

### 2.2 Capability Search Results

#### READ-ONLY ISOLATION
| File | Line | Match |
|------|------|-------|
| `core/prompt_assembler.py` | 375 | `<!-- UNTRUSTED USER DATA - READ ONLY -->` |
| `meta_prompts/__init__.py` | 19 | `No side effects unless explicitly in L2_execution or L4_state` |
| `prompt_entry_types.py` | 6 | `All structures are immutable to enforce contract integrity.` |
| `prompt_entry_types.py` | 14 | `Immutable prompt entry contract.` |
| `prompt_entry_types.py` | 26 | `Immutable SSOT for all prompt definitions.` |
| `prompt_entry_types.py` | 38 | `Build immutable prompt registry.` |

#### SEMANTIC RECALL
| File | Line | Match |
|------|------|-------|
| `scripts/import_violation_visitor.py` | 13 | `Forbidden import namespaces` (false positive — not semantic recall) |

**No matches for:** embedding, vector, similarity, top_k, max_k, recall

#### VERSIONED CONFIG
| File | Line | Match |
|------|------|-------|
| `prompt_entry_types.py` | 18 | `version: str` field in `PromptEntry` |
| `prompt_entry_types.py` | 43+ | `version="v1"` (22 instances) |

**No matches for:** budget, max_k, token limit, safety filter config schema

#### CITATIONS & ANCHORS
**No matches for:** citation, anchor, source_doc, offset, timestamp, span, chunk_id

#### TELEMETRY LOGGING
| File | Line | Match |
|------|------|-------|
| `core/prompt_assembler.py` | 70 | `Logger = logging.getLogger(__name__)` |
| `security/validators/output_schema_validator.py` | 19 | `Logger = logging.getLogger(__name__)` |

**No matches for:** telemetry, metrics, hit_rate, miss, empty_result, recall_estimate

#### ITERATIVE FEEDBACK
**No matches for:** refine, retry, iterate, feedback, re_query, second pass

#### SCHEMA VALIDATION
| File | Line | Match |
|------|------|-------|
| `security/validators/output_schema_validator.py` | 31 | `validate_against_schema()` |
| `validation/validate_assembly.py` | 34 | `sha256_bytes()` |
| `validation/validate_assembly.py` | 37 | `sha256_file()` |
| `validation/validate_assembly.py` | 85 | `sha256` manifest verification |
| `prompt_loader.py` | 89 | `Validate minimal schema` (template key only) |
| `prompt_entry_types.py` | 6 | `contract integrity` |

#### ELEVATOR LOADING
| File | Line | Match |
|------|------|-------|
| `prompt_loader.py` | 23 | `PromptLoader` class |
| `prompt_loader.py` | 50 | `load_prompt()` |
| `scripts/dry_run_compiler.py` | 14 | `FileSystemLoader` (Jinja2) |
| `security/utils/__init__.py` | 5 | `Lazy imports to avoid circular dependency` |
| `validation/validate_assembly.py` | 41 | `load_manifest()` |

---

## Wave 3 — Coverage Matrix + Ranked Gap List

### 3.1 Coverage Matrix (8 Capabilities)

| # | TYPE | DEFINITION | SOURCE (SSOT) | LAYER | AUTHORITY | COVERAGE | PRIMARY FILES | PRIMARY SYMBOLS | WHY | TEST COVERAGE |
|---|------|------------|---------------|-------|-----------|----------|---------------|-----------------|-----|---------------|
| 1 | READ-ONLY ISOLATION | Prevent state mutation during retrieval; thinking agent cannot poison index | Prompt v5.4 §3.8 | L1/L3 | Advisory | **PARTIAL** | `prompt_assembler.py`, `prompt_entry_types.py` | `_format_context_data()`, `@dataclass(frozen=True)` | Comment-only `<!-- READ ONLY -->` in assembler; frozen dataclasses exist but no validator-enforced invariant or negative test | `test_prompt_assembler.py` (no isolation test) |
| 2 | SEMANTIC RECALL | Vector retrieval fidelity + namespaces | Prompt v5.4 §3.8 | L4 | Runtime | **GAP** | None | None | Zero matches for embedding/vector/namespace/top_k/max_k/recall. Capability not represented in prompt_governance. | None |
| 3 | VERSIONED CONFIG | Version-controlled retrieval parameters (budgets, max_k, safety filters) | Prompt v5.4 §4.2 | L1 | Config | **PARTIAL** | `prompt_entry_types.py` | `PromptEntry.version` | `version` field exists but is string-only; no budget/max_k/safety filter schema; no config validation | `test_prompt_entry_types.py` |
| 4 | CITATIONS & ANCHORS | source_doc_id + offsets + timestamps mapping | Prompt v5.4 §3.8 | L4 | Runtime | **GAP** | None | None | Zero matches for citation/anchor/source_doc/offset/timestamp/span/chunk_id. Capability not represented. | None |
| 5 | TELEMETRY LOGGING | Hit rates, recall estimates, empty results signals | Prompt v5.4 §5.4 | L6 | Observability | **GAP** | None | None | Only standard `logging.getLogger()` exists. No telemetry/metrics/hit_rate/recall_estimate contract fields. | None |
| 6 | ITERATIVE FEEDBACK | Within-run query refinement loop (private reasoning; no authority) | Prompt v5.4 §3.8 | L1 | Advisory | **GAP** | None | None | Zero matches for refine/retry/iterate/feedback/re_query. No prompt-internal loop instruction. | None |
| 7 | SCHEMA VALIDATION | Contract/type-hash validation before prompt injection | Prompt v5.4 §4.2 | L2.1 | Validator | **PARTIAL** | `output_schema_validator.py`, `prompt_loader.py`, `validate_assembly.py` | `validate_against_schema()`, `sha256_file()` | Output schema validator exists and is wired to assembler. `PromptLoader` only validates `template` key. No type-hash on `PromptEntry`. SHA256 used for assembly manifest only. | `test_output_schema_validation_gate.py` |
| 8 | ELEVATOR LOADING | Runtime injection via loader seam; keep L0 foundation lightweight | Prompt v5.4 §3.8 | L0 | Seam | **PARTIAL** | `prompt_loader.py`, `__init__.py` | `PromptLoader`, `load_prompt()` | Loader is injectable and cached. Lazy import comment in `security/utils/__init__.py`. No explicit importlib seam or upward-import guard test. | `test_prompt_loader.py` |

### 3.2 Ranked Gap List (Priority Order)

#### GAP 1: SEMANTIC RECALL — **GAP (Critical)**
- **Status:** GAP — zero coverage
- **Files implicated:** None exist
- **Symbols implicated:** None
- **Minimal fix hypothesis:** Add `contracts/context_contracts.py` with `RetrievalContextContract` dataclass defining `namespace: str`, `max_k: int`, `version: str`. This is a shape-only contract — no retrieval logic. Validator can enforce presence when retrieval metadata is present in payload.
- **Proposed tests:**
  - `test_retrieval_context_contract_fields_required()` — missing `namespace`/`max_k`/`version` fails validation
  - `test_retrieval_context_contract_valid_passes()` — valid payload passes

#### GAP 2: CITATIONS & ANCHORS — **GAP (Critical)**
- **Status:** GAP — zero coverage
- **Files implicated:** None exist
- **Symbols implicated:** None
- **Minimal fix hypothesis:** Add `CitationAnchorContract` dataclass to `contracts/context_contracts.py` with `source_doc_id: str`, `offset_start: int`, `offset_end: int`, `timestamp: str`. Validator enforces presence when `citations` key exists in payload.
- **Proposed tests:**
  - `test_citation_anchor_contract_missing_source_doc_id_fails()` — missing `source_doc_id` fails
  - `test_citation_anchor_contract_valid_passes()` — full valid payload passes

#### GAP 3: TELEMETRY LOGGING — **GAP (High)**
- **Status:** GAP — zero coverage
- **Files implicated:** None exist
- **Symbols implicated:** None
- **Minimal fix hypothesis:** Add `TelemetryEnvelopeContract` dataclass with `hit_rate: float`, `recall_estimate: float`, `empty_result_signal: bool`. This is shape-only — no persistence logic. Contract defines expected fields for downstream telemetry consumers.
- **Proposed tests:**
  - `test_telemetry_envelope_contract_fields_exist()` — contract has required fields
  - `test_telemetry_envelope_contract_types_enforced()` — wrong types fail

#### GAP 4: ITERATIVE FEEDBACK — **GAP (Medium)**
- **Status:** GAP — zero coverage
- **Files implicated:** None exist
- **Symbols implicated:** None
- **Minimal fix hypothesis:** Add prompt-internal loop instruction block as a constant in `core/invariant_registry.py` (e.g., `ITERATIVE_FEEDBACK_INSTRUCTION`). This is advisory text for prompt composition — no execution logic. Assembler can inject this block when iterative mode is requested.
- **Proposed tests:**
  - `test_iterative_feedback_instruction_exists()` — constant is defined
  - `test_iterative_feedback_instruction_non_mutating()` — text contains no mutation verbs

#### GAP 5: READ-ONLY ISOLATION — **PARTIAL (High)**
- **Status:** PARTIAL — comment-only enforcement
- **Files implicated:** `core/prompt_assembler.py:375`
- **Symbols implicated:** `_format_context_data()`
- **Minimal fix hypothesis:** Add `invariant_registry.py` with `READ_ONLY_ISOLATION = {"forbidden_verbs": ["write", "modify", "update", "delete"]}`. Extend `validate_context_contract()` to reject forbidden verbs as keys in `retrieval_metadata`. Assembler delegates to validator — no duplicate logic.
- **Proposed tests:**
  - `test_read_only_isolation_rejects_mutation_verb()` — `{"retrieval_metadata": {"write": "x"}}` fails
  - `test_read_only_isolation_invariant_registry_valid()` — registry schema self-validates

#### GAP 6: VERSIONED CONFIG — **PARTIAL (Medium)**
- **Status:** PARTIAL — `version` field exists but no constraint enforcement
- **Files implicated:** `prompt_entry_types.py:18`
- **Symbols implicated:** `PromptEntry.version`
- **Minimal fix hypothesis:** Extend `validate_context_contract()` to enforce `version` is non-empty string, `max_k` is int > 0, `namespace` is non-empty string when `retrieval_metadata` is present.
- **Proposed tests:**
  - `test_versioned_config_empty_version_fails()` — `version=""` fails
  - `test_versioned_config_max_k_zero_fails()` — `max_k=0` fails

#### GAP 7: SCHEMA VALIDATION — **PARTIAL (Medium)**
- **Status:** PARTIAL — output validator exists, loader only checks `template` key
- **Files implicated:** `prompt_loader.py:89`, `output_schema_validator.py:31`
- **Symbols implicated:** `validate_against_schema()`, `load_prompt()`
- **Minimal fix hypothesis:** Add `validate_context_contract()` function to `output_schema_validator.py` that enforces citation/retrieval contract fields. Wire assembler to call this validator — single enforcement path.
- **Proposed tests:**
  - `test_validate_context_contract_returns_empty_on_failure()` — third element is `{}` on failure
  - `test_validate_context_contract_single_enforcement_path()` — assembler cannot bypass validator

#### GAP 8: ELEVATOR LOADING — **PARTIAL (Low)**
- **Status:** PARTIAL — loader is injectable, no upward-import guard
- **Files implicated:** `prompt_loader.py`, `__init__.py`
- **Symbols implicated:** `PromptLoader`
- **Minimal fix hypothesis:** Add test that AST-parses `prompt_governance/**/*.py` and asserts no imports from L4+ runtime systems. Existing lazy import comment in `security/utils/__init__.py` is good practice but not enforced.
- **Proposed tests:**
  - `test_no_upward_imports_in_prompt_governance()` — AST scan for forbidden imports
  - `test_no_pydantic_import_in_contracts()` — contracts use dataclasses only

---

## Summary

| Coverage | Count | Capabilities |
|----------|-------|--------------|
| **GAP** | 4 | SEMANTIC RECALL, CITATIONS & ANCHORS, TELEMETRY LOGGING, ITERATIVE FEEDBACK |
| **PARTIAL** | 4 | READ-ONLY ISOLATION, VERSIONED CONFIG, SCHEMA VALIDATION, ELEVATOR LOADING |
| **COVERED** | 0 | — |

**Phase 1 complete.** No code changes. Evidence file only.
