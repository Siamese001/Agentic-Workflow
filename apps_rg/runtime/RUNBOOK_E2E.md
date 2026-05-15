# apps_rg end-to-end resume orchestrator — runbook

Single command stitches section dispatches, rollup, locked copy, final assembly, DOCX manifest, DOCX render, and resume package X3.

**Maintainer boundaries:** Generated lane behavior, X1D, X2, X3, L6 policy, DOCX renderer internals, registry, `v1` prompts, and `agentic_core` are out of scope for this orchestrator wiring. This runbook describes how to invoke the existing seams only.

---

## 1. Required services

| Dependency | Purpose |
|-----------|---------|
| **vLLM Qwen server** | Primary L2 generator when using `--provider qwen_vllm` (lanes call the apps_rg Qwen provider; server must match project env/configuration). |
| **X1D judge backends** | Per-lane Gemini, OpenAI, and Anthropic API keys/configuration where judges are configured (canonical judge list flags below). Keys may be unavailable in some environments; disposition may route to REVIEW when providers are blocked or soft-failed. |

Run from repository root (or any working directory resolved to the workspace root containing `apps_rg/resume/base`).

---

## 2. Exact command (normal usage)

Canonical base resume **`apps_rg/resume/base/amit_ayer_base_resume_v1.json`** is applied automatically (pointer merge) when **`--base-resume` is omitted**. Omitting it is the default and recommended path for apps_rg.

```bash
python -m apps_rg.runtime.orchestrate_full_resume \
  --provider qwen_vllm \
  --x1d-judges gemini_pro,openai_chatgpt,anthropic_claude \
  --allow-non-allow-exit-zero \
  --job-description artifacts/apps_rg/runtime_inputs/brown_brown_svp_it_job_description.txt \
  --briefing artifacts/apps_rg/runtime_inputs/brown_brown_svp_it_briefing.txt
```

Minimal invocation without JD/briefing files (lanes use dispatch defaults):

```bash
python -m apps_rg.runtime.orchestrate_full_resume \
  --provider qwen_vllm \
  --x1d-judges gemini_pro,openai_chatgpt,anthropic_claude \
  --allow-non-allow-exit-zero
```

Optional overrides:

```bash
python -m apps_rg.runtime.orchestrate_full_resume \
  --provider qwen_vllm \
  --x1d-judges gemini_pro,openai_chatgpt,anthropic_claude \
  --allow-non-allow-exit-zero \
  --job-description path/to/jd.txt \
  --briefing path/to/briefing.txt \
  --base-resume apps_rg/resume/base/custom_base_resume.json \
  --output-docx artifacts/apps_rg/runtime_proofs/docx/amit_ayer_resume_v1.docx
```

### 2.1 Input helper (JD + briefing only)

Validate JD and briefing paths and print a suggested CLI. **Does not read or write base resume** or pointer JSON.

```bash
python -m apps_rg.runtime.prepare_orchestrator_inputs \
  --job-description artifacts/apps_rg/runtime_inputs/brown_brown_svp_it_job_description.txt \
  --briefing artifacts/apps_rg/runtime_inputs/brown_brown_svp_it_briefing.txt
```

Add `--emit-json` for JSON-only output.

Notes:

- **`--base-resume`** (when provided) temporarily merges `active_resume_path` into `apps_rg/resume/base/active_base_resume_pointer.json` and restores afterward. When omitted, the orchestrator merges the **canonical** `amit_ayer_base_resume_v1.json` after verifying it exists (**fail-fast before Qwen, judges, or DOCX**).
- If the canonical default file is missing, correct the tree or pass `--base-resume` to a valid file under the repo.
- **`--output-docx`** must keep basename `amit_ayer_resume_v1.docx` (DOCX proof contract).

---

## 3. Inputs

| Input | Mechanism |
|-------|-----------|
| **Base resume** | **Default:** `apps_rg/resume/base/amit_ayer_base_resume_v1.json` (merged into `active_base_resume_pointer.json` for the run). **Override:** `--base-resume <path under repo>`. |
| **Job description** | Optional `--job-description path` → forwarded to lanes as JD text (`--jd-text` internally). |
| **Briefing** | Optional `--briefing path` → forwarded to lanes as briefing text. |

The orchestrator JSON output includes `base_resume_path`, `base_resume_default_used`, `base_resume_exists`, and `base_resume_hash` (SHA-256 of UTF-8 file contents, same convention as locked-copy manifest hashing).

Lane-specific defaults still apply where optional files are omitted (see individual dispatch modules).

---

## 4. Outputs (canonical paths under repo root)

| Artifact | Typical path |
|----------|----------------|
| **DOCX** | `artifacts/apps_rg/runtime_proofs/docx/amit_ayer_resume_v1.docx` |
| **`final_resume.json`** | `artifacts/apps_rg/runtime_proofs/final_resume_assembly/final_resume.json` |
| **`generated_lane_rollup.json`** | `artifacts/apps_rg/runtime_proofs/generated_lane_rollup/generated_lane_rollup.json` |
| **`locked_copy_manifest.json`** | `artifacts/apps_rg/runtime_proofs/locked_copy/locked_copy_manifest.json` |
| **`docx_render_manifest.json`** | `artifacts/apps_rg/runtime_proofs/docx/docx_render_manifest.json` |
| **`resume_package_x3_disposition.json`** | `artifacts/apps_rg/runtime_proofs/resume_package/resume_package_x3_disposition.json` |

Related proof files (often needed for audits):  
`artifacts/apps_rg/runtime_proofs/docx_manifest/docx_manifest.json`,  
`artifacts/apps_rg/runtime_proofs/resume_package/resume_package_manifest.json`,  
lane run directories under `artifacts/apps_rg/runtime_proofs/<lane>/real/`.

The orchestrator prints a JSON summary including path keys aligned with these locations.

---

## 5. Expected current status

| Field | Expected value |
|-------|----------------|
| **`orchestrator_status`** | `PARTIAL` |
| **Package disposition** | `X3_REVIEW_SECTION_JUDGE_STATUS` (**REVIEW**, not ALLOW) |

---

## 6. Meaning of PARTIAL / REVIEW (accepted)

When the command exits **0** with **`--allow-non-allow-exit-zero`**:

- Deterministic rollup, locked copy X2, final resume assembly X2, DOCX manifest X2, and DOCX render X2 expected to **pass**.
- DOCX artifact is **written or refreshed**.
- Package X3 stays **review-gated** because section-level judge/provider outcomes are not ALLOW (e.g. provider blocked / soft-fail patterns roll up to `X3_REVIEW_SECTION_JUDGE_STATUS`).
- This is an **accepted product state**, not a failure of the orchestrator wiring.

---

## 7. Exact tests to run

After substantive orchestrator module changes only (documentation-only edits do not require rerunning generation):

```bash
python -m pytest tests/_apps_contract/test_apps_rg_e2e_resume_orchestrator.py -v
```

Regression bundles:

```bash
python -m pytest tests/_apps_contract/test_l6_shadow_packet_contract.py tests/_apps_contract/test_resume_package_x3.py tests/_apps_contract/test_docx_render.py tests/_apps_contract/test_docx_manifest.py tests/_apps_contract/test_final_resume_assembly.py tests/_apps_contract/test_generated_lane_rollup.py tests/_apps_contract/test_locked_copy_lanes.py -v
```

```bash
python -m pytest tests/_apps_contract/test_headline_runtime_slice.py tests/_apps_contract/test_competencies_runtime_slice.py tests/_apps_contract/test_ibm_narrative_runtime_slice.py tests/_apps_contract/test_ibm_bullets_runtime_slice.py tests/_apps_contract/test_unify_narrative_runtime_slice.py tests/_apps_contract/test_unify_bullets_runtime_slice.py tests/_apps_contract/test_exec_summary_runtime_slice.py tests/_apps_contract/test_exec_summary_dry_run.py -v
```

If `pytest` reports unknown arguments (e.g. `--timeout`), ensure `pytest-timeout` is loaded—see `pytest.ini` / IDE env (`PYTEST_DISABLE_PLUGIN_AUTOLOAD` may need to be unset for interactive runs).

---

## 8. No registry / v1 / agentic_core changes

The E2E orchestrator adds **apps_rg runtime wiring and documentation only**. It must not imply edits to registry, `v1` prompts, `agentic_core`, or centralized policy gates—those boundaries stay unchanged when using this command.
