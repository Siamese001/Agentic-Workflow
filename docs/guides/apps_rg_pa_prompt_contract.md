# apps_rg Prompt Assembly (PA) Contract

> **Status:** W1-W9 Complete | **W10 Docs/Receipts** | W11 Runtime Binding Decision (Future)
>
> **Scope:** This document describes the governed, local, replayable apps_rg PA compile path. It explicitly does NOT describe runtime wiring.

---

## 1. Canonical Prompt Locations

All declarative PA artifacts live under `apps_rg/prompt_assembly/`:

| Location | Purpose |
|----------|---------|
| `apps_rg/prompt_assembly/prompt_bom.yaml` | Bill of materials — defines 8-slot authority model |
| `apps_rg/prompt_assembly/prompt_registry.yaml` | Template registry — maps template_id to template files |
| `apps_rg/prompt_assembly/templates/` | 8 declarative YAML templates (E3/E4/E5) |
| `apps_rg/prompt_assembly/rg_prompt_profile.yaml` | Power verbs, forbidden phrases, prompt profile |
| `apps_rg/prompt_assembly/rg_style_profile.yaml` | Voice/tone and anti-patterns |
| `apps_rg/prompt_assembly/rg_evidence_profile.yaml` | C0 extraction and citation rules |
| `apps_rg/prompt_assembly/rg_output_schema.json` | R0 schema contract |
| `apps_rg/prompt_assembly/compiler.py` | Local PA compiler (no runtime wiring) |
| `apps_rg/prompt_assembly/contracts.py` | Typed contracts: `PromptAssemblyInput`, `CompiledPromptArtifact`, `EvidenceSource` |

---

## 2. 8-Slot Authority Model (ADR-023)

The PA system implements the 8-slot authority model with strict precedence:

```
S0 (SYSTEM_AUTHORITY)     >  # Immutable governance — no-fabrication oath
D0 (BINDING_AUTHORITY)    >  # Security fences — injection boundaries
I0 (GOVERNED_AUTHORITY)   >  # Domain instructions — section-specific guidance
C0 (INFORMATIONAL)        >  # Evidence data — candidate_facts, jd_requirements
E0 (EXAMPLE_AUTHORITY)    >  # Approved examples — few-shot patterns
Y0 (STYLE_AUTHORITY)      >  # Synthesis preferences — tone, format (advisory only)
U0 (ZERO_AUTHORITY)       >  # User task — intent only, never overrides S0-D0
R0 (SCHEMA_AUTHORITY)     >  # Output contract — response schema binding
```

**Key invariant:** Lower authority NEVER overrides higher authority.

---

## 3. S0: No-Fabrication Oath

Every template's S0 slot contains a sovereign no-fabrication oath:

1. **NO FABRICATION:** Never invent employers, titles, dates, metrics, achievements, tools, technologies.
2. **CANDIDATE FACTS ARE TRUTH:** Content in `<candidate_facts>` is GROUND TRUTH.
3. **JD/TARGET CONTEXT IS NOT PROOF:** JD requirements are TARGET context only, not proof of candidate experience.
4. **UNSUPPORTED CLAIMS:** OMIT entirely or flag as `[Gap: insufficient evidence]`.
5. **CITATION REQUIREMENT:** Preserve `[source: X]` citations from C0 evidence.

**Enforcement:** The compiler validates `has_no_fabrication_oath` flag in `CompiledPromptArtifact`.

---

## 4. C0: Source Separation

C0 evidence is strictly separated by source type:

| Source | Content | `source_tag` | Purpose |
|--------|---------|--------------|---------|
| `candidate_facts` | Verified candidate history | `candidate_facts_*` | Ground truth for resume claims |
| `jd_requirements` | Job description requirements | `jd_*` | Target context, NOT candidate proof |
| `company_brief` | Company research | `company_brief_*` | Cultural context |
| `alignment_map` | JD-to-candidate mapping | `alignment_*` | DIRECT/IMPLIED/GAP classifications |

**Critical rule:** JD requirements must NOT be treated as candidate achievements. The compiler enforces distinct `source_tag` values and validates C0 separation via `validate_c0_separation()`.

---

## 5. Y0: Advisory-Only Semantics

Y0 (style preferences) is explicitly advisory:

- Y0 can suggest tone, length, format preferences
- Y0 CANNOT override S0-D0-I0 constraints
- Y0 CANNOT introduce new claims or modify facts
- Y0 violations are logged but do not fail compilation (advisory)

**Example valid Y0:** `"Tone: professional but approachable"`
**Example invalid Y0:** `"Add AWS experience if not present"` (violates S0)

---

## 6. R0: Schema Binding

R0 defines the output contract:

- `rg_output_schema.json` defines the JSON schema for compiled artifacts
- `response_schema_ref` in `CompiledPromptArtifact` points to schema location
- Schema validation occurs during compilation via `validate_r0_schema()`

**Required fields:** `schema_version`, `candidate_name`, `target_role`, `target_company`, `sections`, `citations`

---

## 7. Compiler Fail-Closed Behavior

The `PromptCompiler` in `compiler.py` fails closed on validation errors:

| Violation | Error Code | Behavior |
|-----------|------------|----------|
| Missing `prompt_bom.yaml` | `MISSING_BOM` | Raise `PromptAssemblyError` |
| Missing `prompt_registry.yaml` | `MISSING_REGISTRY` | Raise `PromptAssemblyError` |
| Missing template file | `MISSING_TEMPLATE_FILE` | Raise `PromptAssemblyError` |
| Unknown `template_id` | `UNKNOWN_TEMPLATE_ID` | Raise `PromptAssemblyError` |
| Missing required slot | `MISSING_REQUIRED_SLOT` | Raise `PromptAssemblyError` |
| Invalid slot order | `INVALID_SLOT_ORDER` | Raise `PromptAssemblyError` |
| Duplicate slot ID | `DUPLICATE_SLOT_ID` | Raise `PromptAssemblyError` |
| Missing `candidate_facts` | `C0_MISSING_CANDIDATE_FACTS` | Raise `PromptAssemblyError` |
| Missing `jd_requirements` | `C0_MISSING_JD_REQUIREMENTS` | Raise `PromptAssemblyError` |
| Duplicate C0 source tags | `C0_DUPLICATE_SOURCE_TAGS` | Raise `PromptAssemblyError` |
| Missing R0 schema | `R0_MISSING_SCHEMA` | Raise `PromptAssemblyError` |
| Invalid JSON schema | `R0_INVALID_JSON_SCHEMA` | Raise `PromptAssemblyError` |
| Override attempt detected | `OVERRIDE_ATTEMPT_DETECTED` | Raise `PromptAssemblyError` |

**All errors include:** `code`, `message`, `slot_id` (if applicable), `context`, `safe_downstream_instruction`

---

## 8. Dry-Run Smoke Test Coverage

The W9 test suite (`test_w9_pa_integration_smoke.py`) provides dry-run coverage:

**Fixtures:**
- `dry_run_candidate_facts` — Employers, titles, dates, 2+ metrics, fact IDs
- `dry_run_jd_requirements` — Target role, must-have/nice-to-have skills, source_tag
- `dry_run_alignment_map` — DIRECT matches, IMPLIED matches, GAP items
- `dry_run_company_brief` — Company context
- `dry_run_user_task` — Task description with constraints

**Smoke tests:**
- All 4 E3 templates compile from fixtures
- E4/E5 templates skip gracefully if not yet supported
- No model/provider/network calls (verified via mocks)
- Compiled artifacts include all required fields
- `prompt_hash` stability verified
- Source separation survives compile
- JD context not treated as candidate proof

---

## 9. What Is Explicitly NOT Runtime-Wired

The PA compile path is **packet builder only**. The following are NOT implemented:

| Capability | Status | Why |
|------------|--------|-----|
| Runtime prompt retrieval | ❌ Not wired | PA is compile-time only |
| C0 evidence retrieval | ❌ Not wired | Fixtures provide C0 data |
| L2 execution | ❌ Not wired | PA renders packets, does not execute |
| Exit evaluation | ❌ Not wired | PA does not evaluate output |
| UWG writeback | ❌ Not wired | PA does not write L4 |
| Model/provider calls | ❌ Not wired | PA is local compilation only |
| Live C0 caching | ❌ Not wired | Evidence provided in input |
| Heal-stage integration | ❌ Not wired | E4 templates exist but not wired to runtime |

---

## 10. Why PA Fixtures Are Not the Canonical Runtime Prompt Source

**Critical distinction:**

- **PA fixtures** (`dry_run_*`) are for **compile-time validation and smoke testing**
- **Runtime prompts** are constructed by the live system using real C0 retrieval, L2 execution, Exit evaluation

**The PA compiler provides:**
- Governed template loading
- Slot validation
- Source separation enforcement
- Deterministic hashing
- Replay manifests

**The PA compiler does NOT provide:**
- Live C0 evidence
- Runtime prompt dispatch
- Model execution
- Output evaluation

**W11 (Future)** will decide if/how the runtime consumes the PA compiler. Until then, PA remains a local, testable, governed compile path separate from runtime wiring.

---

## 11. Test Summary

| Test File | Tests | Purpose |
|-----------|-------|---------|
| `test_w6_pa_compiler.py` | 32 | Compiler/contracts validation |
| `test_w7_pa_compiler_negative_controls.py` | 24 | Fail-closed negative controls |
| `test_w8_pa_templates_e4_e5.py` | 48 | E4/E5 template content validation |
| `test_w9_pa_integration_smoke.py` | 32 | Dry-run integration smoke tests |
| `test_w10_pa_guardrails.py` | TBD | Governance guardrails |
| **Total W6-W10** | **136+** | **Governance-grade PA compile path** |

**Known caveat:** `test_apps_rg_pa_governance.py` — 34 failed, 47 passed (pre-existing legacy type references; separate cleanup wave)

---

## 12. Machine-Readable Receipt

**Receipt location:** `artifacts/apps_rg/pa_prompt_contract_receipt.json`

The receipt contains:
- Plan ID and generation timestamp
- Completed waves (W1-W9)
- Template IDs (all 8)
- Canonical paths
- Exact test result lines
- Sample `prompt_hash` from W9
- `no_agentic_core_imports` proof
- `no_runtime_wiring` assertion
- Remaining gaps (W11, legacy governance)

---

## 13. Remaining Gaps

| Gap | Status | Notes |
|-----|--------|-------|
| **W11: Runtime binding decision** | 🟡 Future | Decide if/how runtime consumes PA compiler |
| **Legacy governance-test reconciliation** | 🔴 Open | `test_apps_rg_pa_governance.py` type references need cleanup |
| **Live C0 integration** | 🟡 Future | Connect to real evidence retrieval |
| **Heal-stage wiring** | 🟡 Future | Connect E4 templates to runtime heal path |

---

## 14. W10.5 Rev 3 — PA Signal Hardening

> **Status:** Completed | **Plan:** `apps-rg-pa-w10-5-section-signal-hardening-d9b3e7.md`
> **Boundary:** PA-layer only. No agentic_core changes. No runtime wiring. No model/provider calls.

### New Shared YAML Artifacts

| File | Purpose |
|------|---------|
| `apps_rg/prompt_assembly/forbidden_ai_phrases.yaml` | Declarative naturalness guidance — HARD_BLOCK and SOFT_WARN phrase labels |
| `apps_rg/prompt_assembly/jd_calibration_contract.yaml` | Declarative JD overfitting calibration guidance |

### New Section Contracts

| File | Section |
|------|---------|
| `section_contracts/executive_summary_contract.yaml` | Executive summary prompt constraints |
| `section_contracts/unify_contract.yaml` | Unify pass consistency/de-duplication contract |
| `section_contracts/competencies_contract.yaml` | Competencies section evidence/ordering contract |

### New Examples

| File | Coverage |
|------|---------|
| `examples/executive_summary_examples.yaml` | Positive/negative/repair multishot examples |
| `examples/unify_examples.yaml` | Unify pass multishot examples |
| `examples/competencies_examples.yaml` | Competencies multishot examples |

### New Rubric

| File | Dimensions |
|------|-----------|
| `rubrics/section_quality_rubrics.yaml` | 7 dimensions: evidence_support, target_relevance, specificity, non_generic_language, section_consistency, citation_preservation, voice_naturalness |

### Template Updates

All 4 E3 templates (`strategic_tailor_v1`, `tailor_existing_v1`, `generate_scratch_v1`, `enhance_current_v1`) updated with:
- `<instruction_hierarchy>` + `<system_authority>` + `<governing_contract>` XML wrapper in S0
- `<instructions>` XML wrapper with `<evidence_tier_selection>`, `<section_instructions>`, `<naturalness_guidance>`, `<jd_calibration_guidance>`, and `<pre_output_checklist>` blocks in I0

All 3 E4 templates (`bullet_diversity_repair_v1`, `resume_fact_check_v1`, `unsupported_claim_omission_v1`) updated with:
- `<naturalness_guidance>` block in I0

### New Template: unify_v1

New E4_HEAL template `apps_rg/prompt_assembly/templates/unify_v1.yaml` for consistency and de-duplication pass. Registered in `prompt_registry.yaml` and `prompt_bom.yaml`.

### Governance Invariants

- `HARD_BLOCK` and `SOFT_WARN` are **declarative prompt instruction severity labels only** — not compile-time or runtime gates.
- `<pre_output_checklist>` is **private model self-review guidance only** — not chain-of-thought output.
- All new files are under `apps_rg/prompt_assembly/` only.
- Zero `agentic_core` modifications.
- Zero new model/provider calls.

---

*Document version: W10-complete + W10.5-Rev3*
*Updated: 2026-05-14*
*Plan: apps-rg-pa-w10-5-section-signal-hardening-d9b3e7.md*
