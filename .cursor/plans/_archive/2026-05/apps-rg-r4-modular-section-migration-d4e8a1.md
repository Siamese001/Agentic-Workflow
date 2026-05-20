# apps_rg: promote offline modular section lanes into governed R4

## Status

**PASS — approved planning artifact (hardened 2026).**  
Execution must not begin until Phase 0 acceptance below is met. No SSOT flip until the **SSOT flip gate** checklist is satisfied.

**Non-negotiables:** Do not modify `agentic_core`. Do not weaken schema validation. Do not synthesize missing sections. Modular R4 must not perform a **full-resume** model call or a **final whole-resume Qwen rewrite**.

---

## Proven baseline (2026)

| Surface | Role | Body generation |
|--------|------|-----------------|
| `python -m apps_rg` | Canonical **R4 product** CLI | Monolithic: `GenerateResumeStep` → `run_apps_rg_l2_envelope` + tailor-existing CPA |
| `python -m apps_rg.runtime.internal.lane_batch` | **Offline** modular orchestrator (no `agentic_core` R4 spine) | Seven subprocess lane modules → rollup → locked copy → `final_resume_assembler` → DOCX (`runtime_proofs`-centric paths today) |
| `apps_rg/l2_recipe/r4_generation_route.py` | SSOT for R4 style / flags | Today: `monolithic_full_resume`, `R4_RECIPE_USES_FULL_RESUME_ENVELOPE_CPA=True` |

---

## ModularR4GenerationResult (contract — define before implementation)

`apps_rg`-owned result type (dataclass or `TypedDict`, TBD). Required fields:

| Field | Purpose |
|-------|---------|
| `generated_resume` | Merged `dict` matching `rg_output_schema` when successful; otherwise absent/`None` |
| `section_provider_calls_ref` | Repo-relative or absolute path under `artifact_dir` to `section_provider_calls.json` |
| `section_output_refs` | Mapping or list of paths to bounded per-lane outputs under `artifact_dir` |
| `merge_receipt_ref` | Path to deterministic merge receipt JSON |
| `schema_validation_receipt_ref` | Path to full schema validation receipt JSON |
| `final_schema_valid` | `bool` — full merged payload passed `rg_output_schema` validation |
| `decisive_status` | Enumeration e.g. `PASS` / `FAIL` / `BLOCKED` |
| `failure_reason` | Machine-safe string / code (empty when `PASS`) |
| `provider_call_count` | Total provider invocations attributed to modular lanes |
| `locked_sections_provider_calls_detected` | `bool` — must be **false** for PASS (no provider calls for locked deterministic sections) |

### `GenerateResumeStep` / context rule

`context["generated_resume"]` may be set **only when all** of:

- `decisive_status=PASS`
- `final_schema_valid=true`
- `generated_resume` is present and non-empty

Otherwise the step must fail closed (raise / structured fault) so `DocxExportStep` never receives invalid payload.

---

## Shared runner API (Phase 0 deliverable)

### Signature (normative)

```text
run_modular_resume_generation(
    input_package: <TBD apps_rg-owned input bundle>,
    artifact_dir: Path | str,
    run_id: str,
    profile: <TBD provider/profile bundle>,
) -> ModularR4GenerationResult
```

- **Ownership:** `apps_rg` only (e.g. `apps_rg.l2_recipe.modular_resume_generation` or sibling).
- **Writes:** All canonical R4 modular proof outputs MUST live under the **R4 run `artifact_dir`** (e.g. `artifact_dir/section_lanes/`, `artifact_dir/merge/`, `artifact_dir/section_provider_calls.json`).
- **Forbidden for canonical R4:** Depending on **`artifacts/apps_rg/runtime_proofs/**` as the write root for product proof. Offline CLI may keep `runtime_proofs` for backward compatibility until deprecated, but the **shared function** invoked by R4 must use **`artifact_dir`** only.
- **Behavior:** Preserve **seven-lane** order and semantics, **deterministic merge**, and **locked** sections (no LLM for locked lanes).

### Phase 0 — API readiness proof (replaces “baseline proof only”)

Phase 0 must prove whether the offline modular runner can be **reused in-process** by R4.

**Acceptance:**

1. **Inventory subprocess / path assumptions** in `apps_rg.runtime.internal.lane_batch`:
   - Subprocess `cwd=repo`, fixed `RUNTIME_PROOFS` / `PLANNED_DOCX_REL` strings
   - Modules that assume paths under `artifacts/apps_rg/runtime_proofs/`
   - Pointer mutation (`active_base_resume_pointer.json`) — R4 may need a no-pointer or scoped variant when using `artifact_dir`
2. **Deliver** `run_modular_resume_generation(...)` (or thin wrapper that delegates to it) that:
   - Accepts `artifact_dir` + `run_id` + structured input + profile
   - Returns `ModularR4GenerationResult`
   - Writes modular artifacts **only** under `artifact_dir` for the R4 invocation
   - Does **not** require `runtime_proofs` for **canonical** R4 output
3. **Preserve** seven-lane behavior and deterministic merge **semantics** (same gates/order as offline; implementation may refactor from subprocess to in-process).
4. **Exit:** Documented PASS/PARTIAL with tests proving the shared entrypoint is callable without relying on `runtime_proofs` for writes when `artifact_dir` is passed.

---

## 1. Inventory — offline modular runner

### 1.1 Entry

- **Module:** `apps_rg.runtime.internal.lane_batch`
- **API:** `run_orchestration(...)` / CLI `main()` — **legacy orchestration shell**; should call `run_modular_resume_generation` once extracted.
- **Lane loop:** `LANE_MODULES` — subprocess `python -m <lane>` for each:

  1. `apps_rg.runtime.dispatch.headline_dispatch`
  2. `apps_rg.runtime.sections.executive_summary_lane_api`
  3. `apps_rg.runtime.sections.unify_bullets_lane_api`
  4. `apps_rg.runtime.sections.unify_narrative_lane_api`
  5. `apps_rg.runtime.sections.ibm_bullets_lane_api`
  6. `apps_rg.runtime.sections.ibm_narrative_lane_api`
  7. `apps_rg.runtime.sections.competencies_lane_api`

### 1.2 Post-lane pipeline (subprocess, in order)

- `apps_rg.runtime.internal.generated_lane_rollup`
- `apps_rg.runtime.internal.locked_copy_builder`
- `apps_rg.runtime.internal.final_resume_assembler`
- In-process: `_run_docx_emit` → `docx_manifest_builder` + `docx_renderer`
- `apps_rg.runtime.internal.resume_package_disposition.emit_resume_package_artifacts`

### 1.3 Section output schemas

- Per-lane contracts under `apps_rg/prompt_assembly/section_prompt_contracts/*.contract.yaml`
- Section PA builders under `apps_rg/runtime/dispatch/*_pa.py` (compile via `section_prompt_adapter`)
- Dispatch modules wrap Qwen via `apps_rg.runtime.providers.section_qwen_slice` (lane-tagged transport + `reasoning_execution_receipt` on slice)

### 1.4 Legacy artifacts (offline — `artifacts/apps_rg/runtime_proofs/`)

*Not R4 canonical output root after migration; listed for parity with current offline CLI.*

- `generated_lane_rollup/generated_lane_rollup.json`
- `locked_copy/locked_copy_manifest.json`
- `final_resume_assembly/final_resume.json`, `final_resume_x2_gate_outputs.json`
- `docx_manifest/`, `docx/` manifests + planned DOCX path
- Package X3 / disposition paths from `resume_package_x3`

### 1.5 Locked copy

- `locked_copy_builder` after rollup; base resume validated by `validate_base_resume_for_orchestration`; pointer merge for `active_base_resume_pointer.json`

---

## 2. Gap analysis — offline vs governed R4

| Concern | R4 today (`l2_envelope_adapter`) | Offline modular |
|--------|----------------------------------|-----------------|
| **Artifact root** | Per-run `artifact_dir` (e.g. `artifacts/apps_rg/runs/cli_*`) | Fixed `runtime_proofs` tree under repo |
| **L2 sealed artifact / receipt** | `run_apps_rg_l2_envelope` → sealed L2 with `proposed_state_diff` | Lane-local manifests; package X3 — **not** same object as core `CompiledPromptArtifact` envelope seal |
| **Provider diagnostics** | `provider_run_diagnostics`, prompt budget, redacted gateway meta | Per-lane dispatch artifacts (needs consolidation under `artifact_dir`) |
| **`section_provider_calls.json`** | Not emitted | **Missing** — must be added for R4 modular path |
| **`reasoning_execution_receipt`** | Via envelope / provider path | Via `section_qwen_slice`; must aggregate into R4 accounting |
| **X1D / Exit** | Integrated R4 exit_eval / disposition | Package-level section X3; **mapping** required so `outcome_authorized` / X3 codes stay honest |
| **`generated_resume.json` / `resume.docx` / `apps_rg_output_manifest.json`** | `DocxExportStep` + `ResumeArtifactGateStep` under `artifact_dir/outputs/` | Different paths today — R4 modular must **emit R4 layout** under `artifact_dir` |
| **`r4_run_manifest.json`** | Written by integrated pipeline | Must be **augmented** with modular generation fields |

**Conclusion:** Prefer **in-process** `run_modular_resume_generation` (**Phase 0**) mirroring orchestrator steps with **`artifact_dir`** as the only canonical write root for R4.

---

## 3. Implementation phases

### Phase 0 — API readiness proof

See **Phase 0 — API readiness proof** and **Shared runner API** above.

### Phase 1 — Implement `run_modular_resume_generation`

- Implement full pipeline behind shared API; refactor `orchestrate_full_resume` to delegate to it where possible (offline may pass a distinct `artifact_dir` or legacy mode for `runtime_proofs` **only** for non-R4 CLI).
- **No `agentic_core` edits.**

### Phase 2 — `GenerateResumeStep` wiring **without silent fallback**

- **Generation mode** is explicit:
  - **Modular R4 (default target after burn-in):** mode value TBD e.g. `modular_section_lanes` (exact env name in implementation spec).
  - **Legacy monolithic:** **`APPS_RG_R4_GENERATION_MODE=legacy_full_resume`** (or equivalent single env — normative string). No other hidden path to `run_apps_rg_l2_envelope`.
- **Fail closed:** If modular generation fails, **do not** call `run_apps_rg_l2_envelope`. Surface fault and stop.
- **PA guard:** Satisfy existing tests without weakening guards (minimal modular CPA or `governed_context` as designed in Phase 0).

### Phase 3 — Deterministic merge + full `rg_output_schema` validation

- Merge validated section outputs + locked sections (**no synthesis**).
- **Full** schema validation only for product PASS.
- Populate `ModularR4GenerationResult` fields; enforce **context rule** for `generated_resume`.

### Phase 4 — `DocxExportStep` unchanged contract

- Input: `context["generated_resume"]` only when result contract allows.
- Paths: `artifact_dir/outputs/` + `apps_rg_output_manifest.json`.

### Phase 5 — SSOT flip (`r4_generation_route.py`)

- **Only** after **SSOT flip gate** (below) is satisfied in a recorded proof run.

### Phase 6 — Legacy monolithic

- **Only** when `APPS_RG_R4_GENERATION_MODE=legacy_full_resume` (or explicitly documented equivalent).
- Label: **legacy full-resume envelope** — not eligible as modular proof.

---

## 4. Required tests (add/extend)

| Test intent | Notes |
|-------------|--------|
| Explicit legacy mode | Monolithic only when `APPS_RG_R4_GENERATION_MODE=legacy_full_resume` (or spec’d equivalent) |
| Modular fail closed | On modular failure, **no** `run_apps_rg_l2_envelope` (mock/spy must not see call) |
| Modular path emits lanes | `section_provider_calls.json`; seven generative lanes; **no** `section_lane=full_resume` |
| Locked lanes | `locked_sections_provider_calls_detected=false` on PASS |
| Final JSON | Full `rg_output_schema` before any DOCX |
| `section_provider_calls.json` | Required fields per product spec |
| SC semantics | Independent provider invocations, not one multi-candidate prompt |
| Reasoning ordering | headline/exec summary temp (and SC) ≥ competencies per policy |
| SSOT / implementation | Cannot claim modular in SSOT until gate met |

### 4.1 No-bypass tests (must fail CI if violated in modular R4 mode)

When running under **modular** generation mode (not legacy):

1. **No** call to `run_apps_rg_l2_envelope` (spy/AST/source guard as appropriate).
2. **No** accounting record with `section_lane=full_resume` (or equivalent “whole resume” lane key).
3. **No** “final whole-resume Qwen rewrite” step (assert no second full-document generation pass after merge; exact hook TBD).
4. **No** DOCX / manifest that implies success **before** full merged schema validation passes (filesystem + step-order assertions under `artifact_dir`).
5. **No** canonical modular outputs written **outside** the run’s R4 `artifact_dir` (path prefix assertions).

**Locations:** `tests/_apps_contract/` for R4 + modular; `tests/unit/apps_rg/` for pure merge/validation helpers.

---

## 5. SSOT flip gate (`r4_generation_route.py`)

The following may **not** be edited to claim `modular_section_l2` / `R4_RECIPE_USES_FULL_RESUME_ENVELOPE_CPA=False` until a **single recorded proof run** demonstrates all of:

| # | Gate |
|---|------|
| 1 | `section_provider_calls.json` present under `artifact_dir` |
| 2 | All **expected generated lanes** present (or documented lane policy + explicit waiver in receipt — default: **all seven**) |
| 3 | Locked sections: **no** provider calls (`locked_sections_provider_calls_detected=false` in result/receipt) |
| 4 | Deterministic **merge receipt** present |
| 5 | **Full** `rg_output_schema` **validation receipt** present |
| 6 | `outputs/generated_resume.json` present |
| 7 | `outputs/resume.docx` present |
| 8 | `apps_rg_output_manifest.json` present |
| 9 | `r4_run_manifest.json` present |
| 10 | **`outcome_authorized=true`** for that run |

Until then, SSOT remains monolithic defaults per today’s `r4_generation_route.py`.

---

## 6. Required proof artifacts (R4 `artifact_dir`)

- `section_provider_calls.json`
- Per-section outputs (paths referenced from `ModularR4GenerationResult.section_output_refs`)
- Merge receipt (`merge_receipt_ref`)
- Full schema validation receipt (`schema_validation_receipt_ref`)
- `outputs/generated_resume.json`
- `outputs/resume.docx`
- `apps_rg_output_manifest.json`
- `r4_run_manifest.json`
- X3 disposition / `outcome_authorized` consistent with manifest gate

---

## 7. Risks

| Risk | Mitigation |
|------|------------|
| Subprocess vs in-process drift | Single `run_modular_resume_generation` implementation |
| Silent fallback to envelope | **Forbidden** — tests in §4.1 |
| PA guard mismatch | Phase 0 design doc for minimal CPA / `governed_context` |
| Exit/X3 semantics | Map lane/package signals without synthetic ALLOW |
| Path leak to `runtime_proofs` | Phase 0 + no-bypass test §4.1 item 5 |
| Core creep | **Zero** `agentic_core` changes for this migration |

---

## ENTRYPOINT_DECISION

- **`python -m apps_rg` remains canonical:** **Yes**.
- **Offline modular becomes implementation source:** **Yes**, via **`run_modular_resume_generation`** — not subprocess layout assumptions for R4.
- **Monolithic retained as explicit legacy:** **Yes** — **`APPS_RG_R4_GENERATION_MODE=legacy_full_resume`** only.

---

## NO_GO CRITERIA

- Full-resume **single** model call on modular R4 path.
- **Final whole-resume Qwen rewrite** on modular R4 path.
- **Silent** invoke of `run_apps_rg_l2_envelope` after modular failure.
- Schema validation **weakened** for product authorization.
- DOCX / success manifest **before** full merged JSON validates.
- **`agentic_core`** changes.
- **SSOT flip** before §5 gate checklist + `outcome_authorized=true`.
- **Synthesized** section content missing from validated lane outputs + locked inputs.

---

## Files likely to change (execution phase — not all in one PR)

- `apps_rg/l2_recipe/steps.py` — explicit mode; modular vs legacy; no silent fallback
- `apps_rg/l2_recipe/r4_generation_route.py` — SSOT flip **only** after gate
- New: `run_modular_resume_generation`, `ModularR4GenerationResult`, modular pipeline modules
- Refactor: `apps_rg/runtime/internal/lane_batch.py` — delegate to shared runner
- `apps_rg/runtime/dispatch/*` — in-process hooks as needed
- `tests/_apps_contract/` — no-bypass + gate tests

---

## Proof command (future)

```bash
# Modular R4 (example — exact mode env TBD; must NOT be legacy_full_resume)
set APPS_RG_R4_GENERATION_MODE=modular_section_lanes
python -m apps_rg --target-company "..." --target-role "..."

# Legacy monolithic ONLY when explicitly selected
set APPS_RG_R4_GENERATION_MODE=legacy_full_resume
python -m apps_rg --target-company "..." --target-role "..."
```
