# apps_rg post-section aggregation hardening blueprint (2026-05-17)

**Nature:** Specification and patch plan saved to disk (**SSOT full text**). This document does **not** implement code in the same pass unless a separate authored implementation task is explicitly approved.

**Related gap analysis:** `docs/reports/apps_rg/apps_rg_post_section_aggregation_gap_20260517.md`

**Hard exclusions (never in this blueprint’s spirit):**

- Replace or rebuild `final_resume_assembler.py` or `resume_package_x3.py` as wholesale rewrites  
- Modify `agentic_core`  
- Change provider plumbing, judges, section generation prompts, or X3 spine semantics  
- New standalone resume pipelines or heavyweight proof systems  

---

## 1. Accepted current aggregation (baseline)

The read-only audit confirmed deterministic **offline** stacking:

| Layer | Role |
|--------|------|
| `generated_lane_rollup.py` | Per-lane filesystem pointers (`latest_successful_real` et al.) into `generated_lane_rollup.json` |
| `final_resume_assembler.py` | Deterministic merge into `final_resume.json` (+ locked copy + base resume hash vs manifest) |
| `final_resume_x2.py` | Structural / provenance gates (sections, order, snapshot equality, locked copy, hashes, no stray provider artifacts in assembly dir) |
| DOCX manifest / render + X2 | Fidelity gates from manifest and rendered plaintext substring order |
| `resume_package_x3.py` | Package-level `final_x3_code` rollup of downstream X2 + lane receipts; nests `section_level_x3` vs whole-resume disposition |

---

## 2. Taxonomy: `final_x3_code`

**Governance:** In `resume_package_x3`, `final_x3_code` denotes **apps_rg resume package disposition** only. Binding to constitutional **single spine Exit X3** requires an explicit downstream contract beyond this blueprint. Treat **GateVerdict (00C)** and **lane `x3_disposition`** as distinct planes; do not conflate with terminal Exit disposition without authored binding docs.

---

## 3. Target gaps (minimal hardening surfaces)

These are additive over the baseline; preference for **wrappers**, **sidecars**, and **narrow X2 families**:

1. **Rollup coherence:** Rollup can resolve **different per-lane run contexts** (independent pointers + timestamps).  
2. **Unified orchestration fingerprint:** No single immutable envelope binds `rollup_id`, `base_resume_digest`, JD/briefing digests (when known), target fields, per-lane `run_id`/artifact dirs.  
3. **Digest enforcement across sections:** Assembler already checks base resume ↔ locked manifest at assembly input; JD/briefing are **not** aggregate-enforced vs every included lane artifact.  
4. **Claim ledgers:** Carried inside `l2_output` payloads; **no aggregate** ref/digest/coverage verification.  
5. **Cross-section semantics:** Structural X2 ≠ narrative quality (overlap, repetition, length, em-dash, competency/bullet bleed). Deterministic lexical gates only (**no LLM**).  
6. **`final_x3` naming:** Documented above; optional future doc cross-link only (no semantic change).

---

## 4. Proposed additive modules (`apps_rg/runtime/aggregation/`)

| Module | Responsibility |
|--------|----------------|
| `run_fingerprint.py` | Build deterministic `OrchestrationRunEnvelope` from existing rollup + optionally orchestrator CLI context (additive only). |
| `section_sealed_index.py` | Derive `SectionSealedPointer` list + `SectionSealedIndex` from rollup `artifact_refs` + on-disk lane JSON (**sidecar**, avoid changing rollup JSON shape). |
| `cross_section_x2.py` | Run lexical/provenance gates; emit JSON gate verdict list with `PASS` / `FAIL` / `WARN` / **`UNKNOWN`** (UNKNOWN **never treated as PASS**). |

### 4.1 `OrchestrationRunEnvelope` (proposed fields)

All digests copied only from authoritative lane / manifest sources; **omit or mark UNKNOWN** with `decisive_reason` when missing.

| Field | Notes |
|--------|-------|
| `orchestration_id` | Stable id (e.g. hash of canonical sorted inputs chosen in implementation) |
| `rollup_id` | From `generated_lane_rollup.json` |
| `created_at_utc` | Iso timestamp at envelope emission |
| `base_resume_digest` | From locked manifest / base resume artifact where present |
| `jd_digest` | From lane metadata if consistent; else UNKNOWN |
| `briefing_digest` | From lane metadata if consistent; else UNKNOWN |
| `target_role` | If available on metadata |
| `target_company` | If available on metadata |
| `lane_run_ids` | `dict[lane_key, run_id]` from each lane `l2_output`/manifest |
| `lane_artifact_digests` | `dict[lane_key, sha256_digest]` over canonical serialization of keyed inputs (implementation-defined **deterministic** hashing) |

**Rules:** Never invent JD/briefing digests from JD text blobs at aggregation time without the same ingest path used by lanes — if absent across artifacts, UNKNOWN + reason.

### 4.2 `SectionSealedPointer` (proposed fields)

Derived from rollup row + pointed run dir (read-only):

- `lane`  
- `run_id`  
- `artifact_dir` (posix rel)  
- `l2_output_ref`  
- `l2_output_digest` (deterministic canonical hash over file bytes or sorted JSON canonicalization — pick one SSOT rule)  
- `x2_gate_outputs_ref`, `x3_disposition_ref`  
- `x3_code` (from rollup or fresh read of artifact for mismatch detection)  
- `prompt_hash` if present on lane runtime payload  
- `claim_ledger_ref` if file exists beside lane proofs  
- `source_fact_id_count` if derivable cheaply  
- `jd_digest` / `briefing_digest` / `base_resume_digest` if present consistently in lane payloads else UNKNOWN sentinel  

### 4.3 `SectionSealedIndex`

Container: `{ pointers: list[SectionSealedPointer], index_by_lane: dict, envelope_ref: OrchestrationRunEnvelope | None }` plus optional **`sidecar_manifest_path`** repo-relative (`artifacts/apps_rg/runtime_proofs/aggregation/…` suggestion only).

---

## 5. Aggregate cross-section X2 gates (`cross_section_x2.py`)

**Input:** `final_resume.json` assembled blob **or** plain assembled text surrogate; `SectionSealedIndex`; `OrchestrationRunEnvelope`; optional locked copy manifest path.

**Output:** Ordered list of gate records: `gate_id`, `verdict ∈ {PASS, FAIL, WARN, UNKNOWN}`, `decisive_reason`, `threshold`, `observed`, `evidence_refs` (posix paths).

| `gate_id` | Verdict rules (conservative defaults) |
|-----------|----------------------------------------|
| `x2_aggregate_same_run_identity_or_explicit_unknown` | PASS if coherent single orchestration fingerprint; FAIL on proven mismatch; UNKNOWN if envelopes partial |
| `x2_aggregate_digest_coherence` | FAIL on conflicting known non-empty JD/briefing/base hashes across lanes; UNKNOWN if materially missing |
| `x2_aggregate_no_blocked_section_included` | FAIL if any included lane disposition code matches BLOCK/BLOCKED/DENY family (normalize casing) |
| `x2_aggregate_claim_ledger_refs_present_when_lane_emits_ledger` | For lanes flagged as emitting ledger shapes: FAIL missing ref/digest pair; UNKNOWN if lane capability ambiguous |
| `x2_aggregate_no_em_dash` | FAIL if Unicode EM DASH `\u2014` (literal) detected in corpus under test |
| `x2_aggregate_resume_length_budget` | WARN if corpus length exceeds budget default (explicit constant, e.g. character cap) pending product owner SSOT budget |
| `x2_aggregate_repetition_density` | WARN same normalized 4-word phrase ≥ 3× outside exempt locked blobs |
| `x2_aggregate_headline_summary_overlap` | WARN headline normalized substring appears verbatim in first executive summary sentence |
| `x2_aggregate_summary_bullet_redundancy` | WARN same 6-token stem appears executive summary vs any unified/IBM bullets |
| `x2_aggregate_competency_bullet_overlap` | WARN if >35% competency terms verbatim in bullets (normalized token containment) |
| `x2_aggregate_locked_copy_unchanged_ref_present` | PASS if assembler already proved + cross-check locked manifest refs still present in envelope index |

Gate law: **`UNKNOWN ≠ PASS`** for rollup pass/fail policy; callers must treat WARN as advisory unless product policy escalates WARN to BLOCK later.

---

## 6. Wiring strategy (minimal blast radius)

|**Option A — optional hook**| After `assemble_final_resume` / `final_resume_x2` all-pass stub, optionally invoke cross-section evaluator writing `cross_section_x2_gate_outputs.json` beside assembly dir; `resume_package_x3` may optionally merge failure refs **without changing** semantic meaning of legacy `final_x3_code`.|

|**Option B — callable-only + docs**| Publish pure functions + unit tests **only** until package merge is narrowly safe; markdown records **CURRENT_WIRING: PARTIAL**.|

**Recommendation:** Ship **Option B** first snapshot; wire Option A gate **only when** deterministic failure paths are proven harmless to existing PASS semantics (additive receipt only).

---

## 7. Tests (contract stubs when implemented)

Suggested locations under **`tests/_apps_contract/`**:

- `test_apps_rg_aggregation_run_fingerprint.py` — coherence / UNKNOWN paths  
- `test_apps_rg_cross_section_x2.py` — em dash FAIL, repetition WARN, competency overlap WARN  

Regression anchor (when implemented):

- `pytest tests/_apps_contract/test_apps_rg_final_resume_x2.py …` unchanged green  
- No `agentic_core` diff vs HEAD  

**(This blueprint pass does not add those test modules until implementation phase.)**

---

## 8. Phase 1 inventory commands (operators)

PowerShell-safe:

```powershell
Set-Location C:\Git\Agentic-Workflow-FRESH
$env:PYTHONPATH = (Get-Location).Path
git status --short
# rg inventory if installed on PATH ...
```

Semantic inventory may substitute IDE search if `rg` absent.

---

## 9. Implementation receipt (explicitly empty for blueprint-only saves)

|| Command | Intended use when implementing |
|---------|--------------------------------|
| `python -m compileall apps_rg` | Import sanity |
| `pytest …test_apps_rg_aggregation_run_fingerprint…` etc. | New gate tests |
| `pytest …test_apps_rg_final_resume_x2… resume_package_x3…` | Regression |

---

## 10. CERTIFICATION DISCLAIMER

This artifact is **not** Fort Knox spine certification or full Exit semantics compliance. Scope: **apps_rg aggregation additive hardening** design only.
