# apps_rg input wiring audit — briefing, broad skills ledger, U0 base resume

**Audit date:** 2026-05-18  
**Scope:** Seven canonical section lanes (`headline`, `executive_summary`, `unify_bullets`, `unify_narrative`, `ibm_bullets`, `ibm_narrative`, `competencies`)  
**Mode:** Read-only code/artifact/receipt audit (no refactors, no `agentic_core` edits, no mocks added)

---

## 1. Executive summary

| Question | Finding |
|----------|---------|
| Does every section receive **briefing**? | **Yes** on the canonical `python -m apps_rg --section <lane>` path: CLI `--manual-brief` → `canonical_dispatch._read_optional_brief` → lane `briefing` arg → `runtime_payload` → PA `c0_jd_requirements` / input-authority block. Defaults apply when omitted (`resolve_briefing_for_lanes`, `section_cli_defaults.default_targeting_briefing_text`). |
| Does every section receive **broad skills ledger**? | **No** on the default path. The governed artifact is `artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json` (`load_master_candidate_fact_ledger`). It is consumed only by offline SRFS generation (`apps_rg/fact_inventory/select_role_facts.py`), not loaded directly by section lanes. Default proof pools use **canonical base résumé employment bullets** (`collect_employment_bullets` / `extract_allowed_facts`), not the broad skills ledger. |
| Does every section receive **JD / title / company** targeting? | **Yes** via `target_company`, `target_role` → `target_title` / `target_company`, and JD text from `resolve_jd_for_lanes` + `jd_text` in `runtime_payload` and PA. |
| Does every section receive **SRFS** where applicable? | **Optional** via `--selected-role-fact-set`; all seven lanes wire `selected_role_fact_set` when the path is provided. Default runs use `proof_pool_type: base_resume_fallback`. |
| Is **base résumé** a U0 runtime input? | **Full R4 path:** yes — `AppsRgIngressPayload.source_resume_ref` / `source_resume_text` → `u0_validate_apps_rg` (`resume_hash` from `source_resume_text`) with optional `enrich_ingress_resume_inline_text`. **Section-only path:** lanes **do not** call U0; they load base JSON via `load_lane_base_resume_json` / lane-local `load_base_resume()` from SSOT pointer, **ignoring** CLI `--resume` passed into `canonical_dispatch`. |
| Architecture alignment | Targeting inputs (JD, briefing, title, company) are consistently labeled **non-proof** in PA, X2, judge packets, and `section_input_usage_ledger.json`. Base résumé material is **claim evidence** but section runs ingest it **outside** U0, as structured JSON bullets—not as an ungoverned free-text U0 blob when enrichment runs. |

**Audit status:** `PARTIAL` — wiring is largely consistent for briefing/JD/SRFS-on-demand, but broad skills ledger and CLI `--resume` are not on the default section proof path; section-only runs bypass U0 entirely.

**Product claim:** `false` (audit only; no runtime certification).

---

## 2. Canonical section matrix

| section | canonical path | lane / dispatcher | PA template | primary artifact dir | notes |
|---------|----------------|-------------------|-------------|----------------------|-------|
| headline | `python -m apps_rg --section headline` | `apps_rg.runtime.sections.headline_lane.run_headline_lane_execution` | `headline_tailor_v1.yaml` → `headline_pa.compile_headline_prompt` | `artifacts/apps_rg/runtime_proofs/headline/<provider>/<run_id>/` | Legacy: `headline_dispatch` (deprecated) |
| executive_summary | `python -m apps_rg --section executive_summary` | `executive_summary_lane.run_executive_summary_execution` | `executive_summary.generate_scratch_v1.yaml` → `executive_summary_pa.compile_executive_summary_prompt` | `.../executive_summary/...` | SRFS density/judge-safe repair modules |
| unify_bullets | `python -m apps_rg --section unify_bullets` | `unify_bullets_lane` (execution in lane; helpers in `unify_bullets_dispatch`) | W7 shell + unify bullets PA | `.../unify_bullets/...` | Companion context from prior lanes |
| unify_narrative | `python -m apps_rg --section unify_narrative` | `unify_narrative_lane` | `unify_narrative_pa.compile_unify_narrative_prompt` | `.../unify_narrative/...` | Depends on finalized `unify_bullets` L2 |
| ibm_bullets | `python -m apps_rg --section ibm_bullets` | `ibm_bullets_lane` | IBM bullets PA (policy-backed) | `.../ibm_bullets/...` | |
| ibm_narrative | `python -m apps_rg --section ibm_narrative` | `ibm_narrative_lane` / `ibm_narrative_dispatch` helpers | `ibm_narrative_pa` | `.../ibm_narrative/...` | |
| competencies | `python -m apps_rg --section competencies` | `competencies_lane` → `competencies_dispatch.run_competencies_execution` | `competency_selector_v2.pa_slots.yaml` → `competencies_pa` | `.../competencies/...` | Proof from employment bullets only (not `facts.skills[]`) |

**Dispatch spine:** `apps_rg.__main__` → `apps_rg.runtime.orchestration.canonical_dispatch.run_canonical_apps_rg_from_cli_primitives` → per-section `_run_*_lane_from_cli`.

**Validators / exit:** section `*_x2.py`, `*_x1d.py` (policy-backed judge packets where migrated), `aggregate_x3` in section exit modules.

---

## 3. Input propagation matrix

| section | JD / title / company | briefing | broad skills ledger | SRFS | base résumé raw U0 | evidence (code) |
|---------|----------------------|----------|---------------------|------|-------------------|-----------------|
| headline | PRESENT | PRESENT | MISSING (default) | OPTIONAL (`--selected-role-fact-set`) | ABSENT on section path | `canonical_dispatch._run_headline_lane_from_cli`; `headline_lane.build_runtime_payload`; `headline_pa.build_headline_assembly_input` |
| executive_summary | PRESENT | PRESENT | MISSING (default) | OPTIONAL | ABSENT on section path | `executive_summary_lane.run_executive_summary_execution`; `executive_summary_pa.build_executive_summary_assembly_input` |
| unify_bullets | PRESENT | PRESENT | MISSING (default) | OPTIONAL | ABSENT on section path | `unify_bullets_lane`; `jd_non_proof_block` via PA common |
| unify_narrative | PRESENT | PRESENT | MISSING (default) | OPTIONAL | ABSENT on section path | `unify_narrative_pa.jd_non_proof_block`; base anchor `unify_narrative_base_001` from base JSON |
| ibm_bullets | PRESENT | PRESENT | MISSING (default) | OPTIONAL | ABSENT on section path | `ibm_bullets_lane` + dispatch |
| ibm_narrative | PRESENT | PRESENT | MISSING (default) | OPTIONAL | ABSENT on section path | `ibm_narrative_pa` |
| competencies | PRESENT | PRESENT | MISSING (default) | OPTIONAL | ABSENT on section path | `competencies_dispatch.collect_employment_bullets` (no `facts.skills` ingest) |

**Legend**

- **PRESENT:** propagated into `runtime_payload` and compiled prompt slots (`c0_jd_requirements` / INPUT_AUTHORITY).
- **MISSING (default):** `load_master_candidate_fact_ledger` is not called from any section lane; only `select_role_facts.py` CLI.
- **OPTIONAL:** `__main__.py` `--selected-role-fact-set` → `canonical_dispatch` → lane `resolve_srfs_section_proof_bundle`.
- **ABSENT on section path:** section lanes load base résumé JSON directly; they do not consume `ValidatedRequest.app_payload.source_resume_text`.

---

## 4. U0 base résumé finding

| U0_FIELD | SOURCE_FILE | CURRENT_BEHAVIOR | COMPLIANT? | REASON |
|----------|-------------|------------------|------------|--------|
| `source_resume_text` | `agentic_core/runtime/contracts/apps_rg_ingress_payload.py` (`AppsRgIngressPayload`) | Optional inline résumé material on ingress envelope | PARTIAL | Accepted at U0; hashed in `u0_validate_apps_rg` (`apps_rg/runtime/bindings/u0_binding.py` L89–100, L279). Enrichment canonicalizes JSON via `enrich_ingress_resume_inline_text` (`apps_rg/runtime/dispatch/apps_rg_dispatch.py`). |
| `source_resume_ref` | same | Optional path ref; enrichment resolves file when text empty | PARTIAL | File I/O intentionally **outside** U0 (`resume_resolution.py` module docstring). |
| `briefing_artifact_ref` / `manual_brief_path` | `u0_binding._coerce_envelope_to_app_payload` | Ref only at U0; text loaded downstream | YES | U0 does not treat briefing as proof. |
| `job_description_text` / ref | same | JD hashed (`jd_hash`); targeting only downstream | YES | |
| Section-only lanes | all `*_lane.py` | `load_lane_base_resume_json` / `load_base_resume()` from SSOT pointer; **no** `ValidatedRequest` | NO (vs stated U0-only intake for runs) | Section CLI bypasses U0; `--resume` on CLI is not passed into lane args (only into `build_raw_request_for_r4`, unused by lanes). |

### Answers (U0 boundary)

1. **Is base résumé currently accepted as a U0 runtime input?**  
   **Yes** on the full integrated R4 ingress path (`source_resume_ref` / `source_resume_text`).  
   **No** on the section-only golden path (lanes read base JSON directly).

2. **Where exactly?**  
   - Contract: `agentic_core/runtime/contracts/apps_rg_ingress_payload.py`  
   - Validation: `apps_rg/runtime/bindings/u0_binding.py` → `u0_validate_apps_rg`  
   - Enrichment: `apps_rg/runtime/dispatch/apps_rg_dispatch.py` → `enrich_ingress_resume_inline_text`  
   - CLI default: `apps_rg/__main__.py` `--resume` → `canonical_dispatch.build_raw_request_for_r4` (full run only)

3. **Raw text, parsed facts, ledger, or SRFS?**  
   At U0: canonical JSON serialized into `source_resume_text` when enriched (`u0_inline_text_from_payload`).  
   At lanes (default): employment **bullet rows** extracted from base résumé JSON (`fact_id` / `bul_*`), not master skills ledger rows (`candidate_fact_id`).  
   With `--selected-role-fact-set`: **SelectedRoleFactSet** JSON (may cite ledger-sourced facts if built via `select_role_facts.py`).

4. **Consistent with desired architecture?**  
   **Partially.** Non-proof vs proof separation for JD/briefing is strong. Broad skills ledger is **not** the default governed proof pool for sections. Section-only base résumé load **sidesteps** U0, which conflicts with “U0 emits ValidatedRequest only” for those runs.

5. **Tests asserting behavior**  
   - `tests/_apps_contract/test_apps_rg_u0_structured_resume_support.py` — U0 structured résumé classification  
   - `tests/_apps_contract/test_apps_rg_section_input_usage_ledgers.py` — all 7 sections: briefing/JD authority in ledger + compiled prompt  
   - `tests/_apps_contract/test_apps_rg_e2e_resume_orchestrator.py` — `--base-resume` on full orchestrator (not per-section `--resume`)

---

## 5. Prompt assembly findings

All audited sections use **8-slot PA** (`PromptAssemblyInput`) via `section_prompt_adapter.compile_section_prompt`:

| Slot role | Typical content |
|-----------|-----------------|
| S0 / D0 / I0 / E0 / Y0 | System, fences, task instructions, examples, style |
| **c0_candidate_facts** | Proof: employment bullets, selected facts, ALLOWED_SOURCE_FACT_IDS |
| **c0_jd_requirements** | TARGET_TITLE, TARGET_COMPANY, JD_TEXT, BRIEFING — explicitly **NOT PROOF** |
| u0_user_task | Section JSON contract |
| r0_response_schema | Structured output schema |

`augment_section_compiled_with_input_authority` adds **INPUT_AUTHORITY** / **BASE_RESUME_SELECTED_FACTS** blocks (`input_authority_prompt_block.py`).

**Flags**

| Check | Result |
|-------|--------|
| Briefing used as proof | **Mitigated** — prompts + X2 + `FORBIDDEN_JD_PROOF_ID_TOKENS` in `section_input_usage_ledger.py` |
| JD used as proof | **Mitigated** — same |
| Broad skills ledger in prompt | **Absent** unless SRFS artifact embeds ledger-selected facts |
| Relies only on base résumé | **Default yes** — employment bullets (+ section anchors); competencies **does not** ingest `facts.skills[]` |
| Raw base résumé text without fact IDs | **No** — C0 uses `fact_id` / `bul_*` rows; claim_ledger requires `source_fact_ids` |
| SRFS naming | **Consistent `SRFS` / `SelectedRoleFactSet`** in code; no `SFRS` typo located in `apps_rg/` |

---

## 6. Artifact / receipt proof findings

| section | artifact | proves briefing? | proves broad skills? | proves SRFS? | proves base not raw U0? | gaps |
|---------|----------|------------------|----------------------|--------------|-------------------------|------|
| all 7 | `section_input_usage_ledger.json` | hashes + `CONTEXT_INPUT` authority | **No** — no ledger ref | SRFS fields when active | records `base_resume_ref` / hash from lane load | no `master_candidate_fact_ledger` ref |
| all 7 | `compiled_prompt.txt` / `compiled_prompt_artifact.json` | prompt text + `pa_prompt_hash` | no | SRFS appendix when SRFS mode | INPUT_AUTHORITY block | |
| all 7 | `canonical_claim_ledger_v2.json`, `claim_ledger.json` | no (proof IDs only) | no | source_fact_ids | yes | |
| all 7 | `section_metric_receipt.json` | indirect (`prompt_hash`) | no | `selected_role_fact_set_used`, `proof_pool_type` | `proof_pool_type: base_resume_fallback` default | |
| executive_summary | `selected_role_fact_set_ref.json` | no | no | yes when flag set | yes | |
| SRFS audit | `apps_rg/audit/srfs_receipt_aggregator.py` | no | no | cross-section structural | N/A | `SECTION_SRFS_STRUCTURAL_AUDIT_ONLY` |

---

## 7. Test coverage findings

| test file | assertion covered | sections | missing / gap |
|-----------|-------------------|----------|----------------|
| `test_apps_rg_section_input_usage_ledgers.py` | briefing/JD/title/company authority; compiled prompt INPUT_AUTHORITY; all sections emit ledger | **all 7** | does not assert broad skills ledger |
| `test_apps_rg_srfs_w3_lane_adoption.py` | SRFS CLI threading | subset / parametrized | not “every section must have SRFS by default” |
| `test_apps_rg_srfs_w5_prompt_hierarchy.py` | JD + briefing mentioned in prompts | SRFS-focused runs | default pool only |
| `test_apps_rg_u0_structured_resume_support.py` | U0 structured résumé support | N/A (ingress) | section-only bypass |
| `test_*_section_pipeline.py` | X2 claim_ledger, jd_alignment flags | per-section | mostly mock/offline stub |
| (none found) | `load_master_candidate_fact_ledger` wired into lanes | — | **gap** |
| (none found) | CLI `--resume` overrides lane SSOT | — | **gap** |

**Targeted proof run (this audit):**  
`pytest tests/_apps_contract/test_apps_rg_section_input_usage_ledgers.py::test_section_cli_emits_input_usage_ledger_and_prompt_authority[headline]` → **passed** (exit 0).

---

## 8. Gap list

### BLOCKER

1. **Broad skills ledger not on default section proof path** — `master_candidate_skills_fact_ledger_20260518T1100Z.json` is not loaded by any canonical section lane; default C0 uses base résumé employment bullets only. If product intent requires every section to consume the broad skills ledger, current wiring cannot satisfy that without SRFS pre-generation.

### MAJOR

1. **Section-only runs bypass U0** — base résumé enters lanes via `load_lane_base_resume_json`, not `ValidatedRequest`, so U0 boundary proof does not apply to the primary golden-path CLI.
2. **CLI `--resume` not forwarded to lanes** — `canonical_dispatch` accepts `resume_path` for `build_raw_request_for_r4` but `_run_*_lane_from_cli` does not pass it into `build_*_lane_args`; lanes always use SSOT pointer (`active_base_resume_pointer.json`).
3. **Competencies ignores base `facts.skills[]`** — only `employment[].bullets` feed C0 (`competencies_dispatch.collect_employment_bullets`); broad skills categories on base JSON are unused for proof.
4. **SRFS optional on all sections** — correct for staged rollout, but no test requires SRFS for every section in production mode.

### MINOR

1. **Naming:** “broad skills ledger” is not a first-class code symbol; SSOT filename is `master_candidate_skills_fact_ledger_*`.
2. **Executive summary** uses a lane-local `load_base_resume()` duplicate of pointer resolution (parallel to `resume_resolution.load_lane_base_resume_json`).
3. **Legacy dispatch modules** still exist with deprecation banners; canonical path is `__main__` + `canonical_dispatch` + `*_lane`.

---

## 9. Recommended minimal remediation plan (one wave)

1. **Define SSOT proof-pool policy** in `apps_rg` (no `agentic_core`): default = `{base employment bullets}` vs `{SRFS slice from broad skills ledger}` vs merge rules.
2. **Thread governed proof pool into lanes** — single helper used by all seven lanes: either load SRFS slice or `load_master_candidate_fact_ledger` + section selector, with base résumé bullets as fallback only when documented.
3. **Align section CLI with ingress** — pass resolved `resume_ref` / digest from `resolve_resume_for_lanes(cli --resume)` into `runtime_payload` and `section_input_usage_ledger` (optional: call `u0_validate_apps_rg` on a minimal envelope for receipt parity).
4. **Extend contract tests** — one parametrized test asserting `section_input_usage_ledger` references `broad_skills_ledger` hash when policy demands it; one test that `--resume` changes `base_resume_hash` in artifacts.

---

## 10. Explicit non-claims

- This audit does **not** certify runtime ALLOW, X3 product release, or live Qwen/judge quality.
- Findings are from **static code/receipt paths** and one mock CLI contract test; not full-suite or live-provider runs.
- Presence of briefing/JD text in a compiled prompt does **not** prove correct model usage—only that inputs were assembled into PA slots.
- SRFS structural audit (`srfs_receipt_aggregator`) proves receipt shape only, not end-to-end R4 wiring.
- Existence of `master_candidate_skills_fact_ledger_*.json` on disk does **not** prove section lanes consume it.
