# apps_rg U0 material inputs audit — 2026-05-17

**Scope:** JD (job description), brief (targeting brief), and base resume as consumed on the modular lane path, the canonical R4 path, and U0 ingress hashing. **Read-only** (no code changes in this audit).

**STATUS:** PARTIAL — JD/briefing certified paths are strong; base resume and one envelope path have gaps (see Findings).

---

## Executive summary

| Input | Modular lane path | U0 hash / contract | Canonical R4 | Gaps |
|-------|-------------------|--------------------|--------------|------|
| **JD** | `resolve_jd_for_lanes` → file or default; digest via `canonical_jd_digest` | `jd_hash`: SHA-256 of **inline** `job_description_text` only | `build_canonical_jd_payload` + `canonical_jd_digest` aligned | Ref-only U0 vs digest when lane reads file |
| **Brief** | `resolve_briefing_for_lanes` | `brief_hash`: SHA-256 of **inline** `targeting_notes_text`; no file open in U0 tests | Parallel `_read_optional_brief` (not resolver) | No RG-Brief0; R4 ≠ modular resolver |
| **Base resume** (JSON/text) | Each dispatch `load_base_resume` + path constant | `resume_hash`: SHA-256 of **inline** `source_resume_text` only | Same pattern as modular | No single resolver; no `test_u0_resume_ref_no_io`; dispatch envelope can drop JD ref / inline resume |

**Certified elsewhere:** JD INPUT CERTIFICATION PASS; RG-JD0 gate; `test_u0_jd_no_io`, `test_canonical_jd_parity`, `test_jd_resolution`.

---

## 1. JD — material flow

### Modular (`canonical_dispatch.resolve_jd_for_lanes`)

- Resolves path from env `JD_TEXT_FILE` / `JOB_DESCRIPTION_FILE` / `CANONICAL_JD_TARGETING` or default `apps_rg/config/default_jd_targeting.txt`; reads file when present.
- **Digest:** `canonical_jd_digest(jd_text)` — same primitive as R4.
- **Tests:** `tests/unit/apps_rg/test_jd_resolution.py`, `test_canonical_jd_parity.py`, `test_u0_jd_no_io.py`, RG-JD0 in `run_contract_gates`.

### U0 (`apps_rg_ingress_payload` / manifest)

- `jd_hash` = sha256 of **`job_description_text` string** only (`compute_ingress_hashes`). No automatic load from `jd_ref` into hash.
- **Implication:** If lanes resolve JD from file/env but U0 carries only a ref + empty/minimal inline text, **`jd_hash` may not match** the digest of material actually used downstream until inline text is populated consistently.

### Canonical R4 (`build_raw_request_for_r4`)

- Uses `build_canonical_jd_payload(...)`, `canonical_jd_digest(jd_payload["body_text"])`, and `jd_digest == jd_meta["canonical_jd_digest"]` guard — **aligned** with modular digest.

### Verdict (JD)

Single canonical resolver + digest on the certified path; **U0 remains pointer-oriented** for refs — acceptable if operators always mirror inline text for hashes; document or enforce if mismatch is a concern.

---

## 2. Brief (targeting briefing) — material flow

### Modular (`canonical_dispatch.resolve_briefing_for_lanes`)

- Path from `TARGETING_BRIEF_FILE` / `BRIEFING_FILE` / `CANONICAL_TARGETING_BRIEF` or default `apps_rg/config/default_targeting_briefing.txt`.

### U0

- `brief_hash` = SHA-256 of **`targeting_notes_text`** only.
- **Tests:** `tests/unit/apps_rg/test_u0_briefing_no_io.py` (fixture material; no disk read in U0 path tested).
- **Gap:** No dedicated static gate analogous to RG-JD0 for brief material.

### Canonical R4

- **`_read_optional_brief(profile_path)`** reads brief from disk near profile — **parallel mechanism**, not `resolve_briefing_for_lanes`.

### Verdict (brief)

Contract is clear for inline `targeting_notes_text`; **dual brief resolution** (modular resolver vs R4 local read) is the main convergence risk for future refactors.

---

## 3. Base resume — material flow

### Modular dispatches

- **IBM** — `DEFAULT_SOURCE_RESUME_PATH = resume/base/amit_ayer_base_resume_v1.json`, `load_base_resume()` reads JSON.
- **Headline** — same default path + `load_json_resume()`.
- **Executive summary** — same default path + `load_base_resume()`.
- **Unified narrative** — `DEFAULT_JSON_RESUME` + `_load_profile_json()`.

**Gap:** No shared `resume_resolution` module; duplicated path constants and loaders.

### U0

- `resume_hash` = SHA-256 of **`source_resume_text`** only.
- **Gap:** No `test_u0_resume_ref_no_io` mirroring JD/brief tests; ref-only resume without populated inline text can skew hash vs file-backed resume used in lanes.

### Canonical R4

- Same local JSON load pattern as modular (path constants per section).

### Envelope / `apps_rg_dispatch` (`apps_rg/runtime/dispatch/apps_rg_dispatch.py`)

- `_build_u0_ingress_from_envelope`: may pass only **`job_description_text`** (drops `jd_ref` / structured JD payload) and only **`source_resume_ref`** for `resume_path` when building raw request — **inline resume text can be omitted**. Risk: downstream sees path while U0 hash reflected empty/mismatched inline text.

### Verdict (base resume)

Functional for default paths; **weakest** of the three inputs on SSOT, envelope parity, and U0 ref/no-I/O testing.

---

## 4. Auxiliary: U0 file access outside the three inputs

`u0_profile_manifest.py` reads **`rg_planning_profile.yaml`** from disk to compute the L1 planning digest. That is **not** JD/brief/resume content but shows U0-adjacent file I/O if interpreting “U0 never opens files” literally.

---

## 5. Proof commands (audit run)

All **exit 0** when this audit was executed:

- `pytest -q tests/unit/apps_rg/test_jd_resolution.py tests/unit/apps_rg/test_canonical_jd_parity.py tests/unit/apps_rg/test_u0_jd_no_io.py tests/unit/apps_rg/test_u0_briefing_no_io.py tests/unit/apps_rg/test_modular_lane_adapter.py tests/unit/apps_rg/test_modular_headline_dispatch.py tests/unit/apps_rg/test_modular_execsum_dispatch.py tests/unit/apps_rg/test_modular_unify_dispatch.py tests/unit/apps_rg/test_modular_ibm_dispatch.py tests/_apps_contract/test_apps_rg_generation_entrypoints.py`
- `python scripts/contracts/run_contract_gates.py --only RG-JD0`
- `pytest -q tests/unit/apps_rg/test_ds_r7_jd_interactive.py` (context: JD / `__main__` raw request)

---

## 6. Recommendations (for follow-up work, not part of this read-only audit)

1. **P0:** Unify base resume resolution (single module + shared default + digest helper); add **`test_u0_resume_ref_no_io`** and fix **`apps_rg_dispatch`** envelope mapping so JD ref + inline resume are not dropped relative to lane consumption.
2. **P1:** Optional **RG-Brief0** or brief parity test; consider converging R4 `_read_optional_brief` with `resolve_briefing_for_lanes`.
3. **Docs:** State explicitly whether `jd_hash` / `resume_hash` must match file-resolved material or only inline payload.

---

## Artifact

- **Disk (this file):** `docs/reports/plans/apps_rg_u0_material_inputs_audit_2026-05-17.md`
- **Notion:** [apps_rg U0 material inputs audit — 2026-05-17](https://www.notion.so/36327693f55c81e9917bf3e46ede9be5) (child of *Agentic-Workflow Engineering Hub*).

---

## Status addendum — material-input SSOT (accepted)

Historical body above is the original audit snapshot. **Below is the operator-accepted status for material-input / ingress SSOT only** (no broadened product or certification claims).

- **Base resume:** PASS. `apps_rg/runtime/resume_resolution.py` is the shared SSOT; U0 remains no-I/O for resume files; modular lanes and `build_raw_request_for_r4` use canonical resume digest; RG-RESUME0 is wired.
- **JD:** PASS. JD resolver, parity tests, canonical digest, and RG-JD0 remain the authority.
- **Briefing:** Functional PASS with **P1 open**. Modular lanes use `resolve_briefing_for_lanes`; U0 remains pointer-only; `canonical_dispatch._read_optional_brief` remains a separate R4 path and should be converged with the resolver; add RG-Brief0.
- **Boundary:** This certifies material-input / ingress SSOT hygiene only. It does **not** certify full `apps_rg` runtime, Fort Knox, RTC-REQ, or final release signoff.
