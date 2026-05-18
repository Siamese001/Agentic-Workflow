# apps_rg prompt authority remediation program

**Version:** 1.0 (planning artifact)  
**Execution status:** **CLOSED** — **2026-05-15**. Waves **W0–W12** satisfied; W12 runtime proof **PASS** (scoped **171** tests, empty `agentic_core` diff on `topic/apps_rg-prompt-authority`). **W13** / **W14** remain **separate** artifacts (full-suite triage plan + quality benchmark scaffold only); they do **not** block this closure.

**Canonical language:** *apps_rg owns prompt content; PA assembles, fences, hashes, and emits `CompiledPromptArtifact`; L2 executes the bounded packet; X2 / X1D / Exit judge the outcome.*

**Related:** Narrow wave (closed) — `docs/reports/apps_rg_prompt_review/apps_rg_prompt_remediation_plan.md`.

---

## Target end state

```text
apps_rg/prompt_assembly/
  templates/
  section_contracts/
  examples/
  rubrics/
  schemas/
  jd_calibration_contract.yaml
  prompt_registry.yaml
  prompt_bom.yaml
        |
        v
apps_rg PA compiler / section prompt adapter
        |
        v
CompiledPromptArtifact
        |
        v
apps_rg/runtime/dispatch/<section>_dispatch.py
        |
        v
L2 model execution
        |
        v
X2 deterministic gates
        |
        v
X1D section judge
        |
        v
Exit / X3
```

### What must be true at the end

1. No active generated section lane has freeform inline prompt authority.  
2. Every generated section prompt is **apps_rg-owned** and **PA-assembled**.  
3. Every active prompt template is registered or explicitly classified.  
4. Companion context enters through **PA slots**, not ad hoc disk reads in dispatch.  
5. Displayed resume text has **no inline source tags**.  
6. Proof lives in `claim_ledger`, `source_fact_ids`, `evidence_ids`, and gate receipts.  
7. X2 blocks unsupported, orphan, duplicate, malformed, and locked-field mutations.  
8. X1D judges quality only, not deterministic facts.  
9. Locked sections remain deterministic.  
10. Full suite status is honest: **PASS**, or **PARTIAL** with classified unrelated failures.

---

## Non-negotiable constraints

- **No** `agentic_core` edits.  
- **No** C0 core rewrite.  
- **No** L0 route rewrite.  
- **No** L5 / L6 / UWG rewrite.  
- **No** locked-section LLM rewrite.  
- **No** broad prompt-body churn where behavior is already stable.  
- **No** PASS without command output and exit codes.

---

## Wave 0 — Baseline proof and current-state freeze

**Goal:** Freeze truth before changing behavior.

**Deliverables:**

```text
docs/reports/apps_rg_prompt_authority/
  W0_baseline.md
  command_transcripts/
artifacts/apps_rg/prompt_authority/
  w0_prompt_inventory_before.json
  w0_runtime_bypass_map_before.json
  w0_test_status.json
```

**Commands (capture exit codes; use `python -m pytest -p pytest_timeout …`):**

- `git status --short`  
- `rg --version` (if unavailable, use `tools/apps_rg/prompt_inventory_grep.py` — non-mutating; optional `--out`)  
- `test_headline_runtime_slice.py`  
- `test_exec_summary_runtime_slice.py`  
- `test_competencies_runtime_slice.py`  
- `test_apps_rg_pa_tiered_prompt.py`  
- `tests/_apps_contract` (full — honest PARTIAL if red; do not fix unrelated failures)

**Acceptance:**

- **PASS:** scoped slice commands complete with exit codes.  
- **PARTIAL:** full `tests/_apps_contract` red but scoped slices complete and failures classified.  
- **FAIL:** headline, exec-summary, or competencies slice fails.  
- **BLOCKED:** `pytest_timeout` or search tooling cannot run.

**Do not:** fix unrelated full-suite failures; support bare pytest; edit prompt bodies.

---

## Wave 1 — Full prompt inventory and gap classification

**Goal:** Every prompt surface visible.

**Inventory (representative paths):**

- `apps_rg/prompt_assembly/templates/*.yaml`  
- `apps_rg/prompt_assembly/section_contracts/*.yaml`  
- `apps_rg/prompt_assembly/rubrics/*.yaml`  
- `apps_rg/prompt_assembly/examples/*.yaml`  
- `forbidden_ai_phrases.yaml`, `jd_calibration_contract.yaml`  
- `apps_rg/runtime/dispatch/*_dispatch.py`  
- `apps_rg/runtime/validators/*_x2.py`, `judges/*_x1d.py`, `exit/*_x3.py`, `shadow/*`  
- `apps_rg/config/domain_contract/judges/*`  
- `apps_rg/spine_manifest.yaml`, `prompt_registry.yaml`, `prompt_bom.yaml`

**Classification (every template):**

| Classification | Meaning |
|----------------|---------|
| **ACTIVE** | Production runtime or PA compiler uses it. |
| **TEST_ONLY** | Tests only. |
| **DEPRECATED** | Superseded; retained intentionally. |
| **REMOVE_CANDIDATE** | No references after proof. |
| **UNKNOWN** | Needs follow-up before migration. |

**Deliverables:**

```text
docs/reports/apps_rg_prompt_authority/W1_prompt_inventory.md
artifacts/apps_rg/prompt_authority/template_classification.json
artifacts/apps_rg/prompt_authority/runtime_bypass_map.json
```

**Acceptance:** Every template classified; every dispatch lane has YAML/registry sibling status; every unused `PROMPT_TEMPLATE` constant listed; every inline `build_prompt_messages` path listed.

---

## Wave 2 — Canonical language and section prompt contract

**Goal:** Remove ambiguity: **apps_rg-owned, PA-assembled** (not “PA-owned prompts”).

**Deliverables:**

```text
apps_rg/prompt_assembly/section_prompt_contracts/
  section_prompt_contract.schema.json
  headline.contract.yaml
  executive_summary.contract.yaml
  competencies.contract.yaml
  unify_narrative.contract.yaml
  unify_bullets.contract.yaml
  ibm_narrative.contract.yaml
  ibm_bullets.contract.yaml
```

**Contract shape (informative):**

```json
{
  "section_id": "",
  "mode": "COMPOSE_NEW | REWRITE_FROM_FACT_POOL | SUMMARIZE_ROLE_SCOPE | LOCKED_DETERMINISTIC",
  "apps_rg_prompt_template_ref": "",
  "pa_template_ref": "",
  "output_schema_ref": "",
  "claim_ledger_required": true,
  "display_text_source_tags_allowed": false,
  "jd_as_proof_allowed": false,
  "companion_context_allowed": true,
  "companion_context_authority": "U_TIER_CONTEXT_ONLY",
  "x2_gate_profile_ref": "",
  "x1d_judge_profile_ref": "",
  "locked_fields": []
}
```

**Acceptance:** Every generated section has a contract; points to template, output schema, X2, X1D; no generated section allows inline source tags in displayed text; locked deterministic sections marked non-LLM. **No runtime behavior change** in W2.

---

## Wave 3 — apps_rg per-lane PA adapter (`python -m apps_rg --section <lane>`)

**Goal:** Seam for section lanes to consume PA-assembled prompts **without** `agentic_core` edits.

**Add:**

- `apps_rg/runtime/bindings/section_prompt_adapter.py`  
- `tests/_apps_contract/test_apps_rg_section_prompt_adapter.py`

**Adapter responsibilities:** resolve `section_id` → load section contract → load apps_rg template → build `PromptAssemblyInput` → fence C0 evidence / JD / companion (U-tier only) → call **apps_rg** PA compiler → return `CompiledPromptArtifact` and provider-ready messages.

**Prohibited:** model call inside adapter; retrieval; registry mutation; durable write; silent fallback to inline prompt on compile failure.

**Acceptance:** Adapter compiles at least one dummy section; artifact includes `prompt_hash` and `slot_lineage_map`; **no dispatch lane migrated yet**.

---

## Wave 4 — Executive summary migration

**Rationale:** Highest contamination risk (historically: golden narrative, hardcoded facts).

**Files (representative):** `executive_summary_dispatch.py`, `executive_summary.generate_scratch_v1.yaml`, `executive_summary_contract.yaml`, `executive_summary_x2.py`, `executive_summary_x1d.py`, slice tests + `test_exec_summary_pa_compiled_prompt.py`.

**Changes:** Remove inline `build_prompt_messages` authority; dispatch → `section_prompt_adapter`; facts only via `selected_fact_plan`; clean `resume_display_text`; proof in `claim_ledger`; X2 includes orphan ledger / inline-tag absence / JD-as-proof / hardcoded-metric gates (as listed in charter).

**Acceptance:** No freeform inline prompt construction; captured `CompiledPromptArtifact` + `prompt_hash`; sentence↔ledger mapping or `gap_notes`; exec slice green.

---

## Wave 5 — Competencies migration

**Rationale:** Companion + duplicate injection risk; enforce PA slot discipline.

**Files:** `competencies_dispatch.py`, `competency_selector_v2.yaml`, `competencies.contract.yaml`, X2/X1D, slice + `test_competencies_pa_compiled_prompt.py`.

**Changes:** Single canonical facts path; adapter-based compile; U-tier companion only; one primary `source_fact_id` per term (structured output); JD ranks/selects, does not prove.

**Acceptance:** No inline prompt authority; companion fenced; terms backed; unsupported terms fail X2; slice green.

---

## Wave 6 — Headline migration

**Rationale:** Companion-from-disk PARTIAL risk.

**Files:** `headline_dispatch.py`, `headline_tailor_v1.yaml`, `headline.contract.yaml`, `headline_x2.py`, slice + PA compile test.

**Changes:** Adapter path; no ad hoc companion read in dispatch; U-tier via PA; metrics/employer/title rules preserved in contract + X2.

**Acceptance:** `CompiledPromptArtifact`; no companion file read outside adapter; slice green.

---

## Wave 7 — Unify / IBM mechanical migration

**Rationale:** Review marks lanes mostly PASS — **mechanical** migration only.

**Changes:** Move bodies if needed; dispatch → adapter; **preserve** semantics, schema, X2/X1D behavior; before/after normalized messages match.

**Deliverable:** `tests/_apps_contract/test_unify_ibm_pa_compiled_prompt.py` (or equivalent).

**Acceptance:** Unify/IBM slices green; no semantic prompt churn; no new judge behavior.

---

## Wave 8 — Ledger-only citation standard cleanup

**Goal:** End contract/template vs runtime mismatch.

**Files:** `section_contracts/*.yaml`, rubrics, examples, templates as needed, `*_x2.py`, `test_apps_rg_ledger_only_citations.py`.

**Rule:** Displayed resume text: no inline citations; audit via ledger and IDs.

**Acceptance:** No production prompt asks for `[source: id]` in displayed text; X2 blocks inline tags; test green.

---

## Wave 9 — Registry and manifest SSOT

**Files:** `prompt_registry.yaml`, `spine_manifest.yaml`, `prompt_bom.yaml`, `test_apps_rg_prompt_registry_integrity.py`.

**Rules:** ACTIVE → registry entry; TEST_ONLY marked; DEPRECATED not runtime-loadable; REMOVE_CANDIDATE only after zero refs; UNKNOWN fails integrity gate.

**Acceptance:** No active template missing from registry; no dangling refs; integrity test green.

---

## Wave 10 — Remove remaining inline prompt authority

**Add:** `tests/_apps_contract/test_apps_rg_no_inline_prompt_authority.py`

**Assertions (charter):** no `build_prompt_messages` in active dispatch except explicit deprecated shim; no manual system/user assembly; generated sections use adapter + `CompiledPromptArtifact`; no direct companion disk reads in dispatch.

---

## Wave 11 — X2 / X1D alignment

**Per section:** map output schema, ledger shape, X2 list, X1D dimensions, unsupported-claim handling, JD-as-proof, locked fields.

**Acceptance:** X2 owns determinism; X1D owns soft quality; every gate has tests.

---

## Wave 12 — Full runtime prompt authority proof

**Status:** **CLOSED — PASS** (2026-05-15). Evidence: `docs/reports/apps_rg_prompt_authority/W12_runtime_proof.md`, `artifacts/apps_rg/prompt_authority/full_runtime_prompt_authority_proof.json`.

**Deliverables:**

```text
artifacts/apps_rg/prompt_authority/full_runtime_prompt_authority_proof.json
docs/reports/apps_rg_prompt_authority/W12_runtime_proof.md
```

**Proof payload (shape):** all generated sections use compiled artifact; no inline authority; ledger-only display; X2 green; X1D invoked or mocked with label; locked preserved; no `agentic_core` diff on the prompt-authority branch; scoped proof **PASS** (**171** tests: 57 + 70 + 44); full `tests/_apps_contract` **not** required for W12 closure (out of scope / separate surface).

**Commands:** adapter test, no-inline test, registry integrity, ledger citations, all section slices, full `tests/_apps_contract`.

---

## Wave 13 — Full `_apps_contract` triage (child plan)

**Deliverable:** `docs/reports/apps_rg_prompt_authority/W13_apps_contract_triage_plan.md`

**Buckets:** prompt-authority regression; route/profile drift; judge harness; collection/setup; pytest/plugin; fixture drift; unrelated app failure.

**Acceptance:** Each bucket has owner/next action; canonical pytest documented; bare-pytest stance explicit.

---

## Wave 14 — Quality benchmark and L6 calibration

**Add:** `apps_rg/evals/section_quality_benchmark/*.jsonl`, `W14_quality_benchmark.md`.

**Dimensions:** factual support, JD fit, executive presence, conciseness, specificity, seniority, unsupported-claim risk, usefulness.

**Acceptance:** Human benchmark; before/after comparison; judge calibration report; **no** X1D as release authority; **no** L6 current-run mutation.

---

## Program dependency map

```text
W0 baseline
  → W1 inventory
  → W2 section prompt contracts
  → W3 section PA adapter
       → W4 executive_summary
       → W5 competencies
       → W6 headline
       → W7 unify / IBM mechanical
  → W8 ledger-only citations
  → W9 registry SSOT
  → W10 no inline authority
  → W11 X2/X1D alignment
  → W12 runtime proof
       → W13 full-suite triage
  → W14 quality / L6 calibration
```

---

## Recommended execution chunks

| Chunk | Waves | Purpose |
|-------|--------|---------|
| **A** — Architecture proof | W0–W3 | Adapter + contracts; no risky migration |
| **B** — Weakest lanes | W4–W6 | Exec summary, competencies, headline |
| **C** — Stable lanes | W7 | IBM/Unify mechanical |
| **D** — SSOT closure | W8–W12 | Registry, ledger, gates, proof — **CLOSED** (2026-05-15) |
| **E** — Quality / suite | W13–W14 | Triage + benchmark — **separate** follow-on (plan/scaffold only; not blocking program closure) |

---

## Cursor handoff: W0–W3 only (copy-paste)

Implement **W0–W3** of this program only.

- **Scope:** `apps_rg` only. No `agentic_core`, L0 route, C0 core, L5/L6/UWG, locked-section LLM, IBM/Unify body churn. Do not chase unrelated full `tests/_apps_contract` failures.

**W0:** Baseline transcripts + exit codes; `-p pytest_timeout`; full directory honest status; `prompt_inventory_grep.py` if `rg` missing.

**W1:** Inventory + classification JSON + runtime bypass map.

**W2:** `section_prompt_contracts/` schema + per-section YAML stubs; **no** runtime behavior change.

**W3:** `section_prompt_adapter.py` + contract tests; no model/retrieve/registry write/fallback inline prompt.

**Stop after W3.** Do not migrate `executive_summary` yet.

**Proof:** `gitDiff` stats/names-only, transcripts, exit codes, no `agentic_core` diff, scoped PASS/PARTIAL/FAIL/BLOCKED.

---

## Artifact layout (reference)

| Path | Role |
|------|------|
| `docs/reports/apps_rg_prompt_authority/` | Wave reports (W0, W1, W12, W13, W14) + this program |
| `artifacts/apps_rg/prompt_authority/` | JSON inventories, proof payloads |

---

## Document history

| Date | Change |
|------|--------|
| 2026-05-15 | Program execution **CLOSED** through W12 (runtime proof PASS, scoped 171). W13/W14 remain ancillary docs only. |
| 2026-05-15 | Initial program document from staged charter (W0–W14, chunks A–E). |
