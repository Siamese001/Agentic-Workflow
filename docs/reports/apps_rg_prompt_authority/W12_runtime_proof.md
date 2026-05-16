# W12 — Full runtime prompt-authority proof (apps_rg)

## Status

**PASS** (final closeout **2026-05-15** on branch **`topic/apps_rg-prompt-authority`**).

Prior labels **PARTIAL** (Qwen slice timeout), **PARTIAL_ENV**, and **BLOCKED** (purity gate when `agentic_core` churn was mixed into the PA working tree) are **superseded**. Resolution: branch split from shared **BASE `77b8487ecf…`** — prompt-authority on this branch; binding/Exit spine work isolated on **`topic/agentic_core-binding-exit`**. Narrow Qwen rerun and full headline/exec/competencies bundle re-verified green; **`agentic_core`** purity re-checked (**empty** `git diff` and **empty** `git status` for `agentic_core`).

### Final evidence (recorded)

| Check | Result |
|-------|--------|
| Branch | `topic/apps_rg-prompt-authority` |
| `agentic_core` purity | **PASS** — empty diff, empty status (pathspec `agentic_core`) |
| Qwen narrow rerun | **PASS** — `test_qwen_unavailable_blocks_not_mocks`, 1 passed, exit 0 |
| Headline / exec / competencies bundle | **PASS** — 70 passed, exit 0 |
| Prior W12 registry / no-inline / X2 / ledger bundle | **PASS** — 57 passed |
| Prior Unify / IBM slice bundle | **PASS** — 44 passed |
| Full scoped proof total | **PASS** — **171** passed (57 + 70 + 44) |
| Full `tests/_apps_contract` | **NOT RUN** — correctly out of scope |
| Code edits during rerun | **None** |

**Advisory (not a current failure):** An earlier run hit `subprocess.TimeoutExpired` (~120s) calling real `qwen_vllm` on `test_qwen_unavailable_blocks_not_mocks` (environment/provider timing). The narrow rerun **passed** (~72s). Treat Qwen timeout risk as **flake / env advisory** only unless it recurs.

**Repo noise:** `pr_body.md` (if present untracked) is **unrelated** to this proof and lives outside `agentic_core`.

Durable bundle: `artifacts/apps_rg/prompt_authority/full_runtime_prompt_authority_proof.json`

## Carry-forward (W13 / W14)

- **W13** — **PASS** as **triage plan only**; full `tests/_apps_contract` remains **not promoted** here.
- **W14** — **PASS** as **quality benchmark scaffold only** (see `W14_quality_benchmark.md`).
- Full `tests/_apps_contract` is a **separate** execution surface; scoped **171** does **not** replace it.
- Additional strings (Qwen advisory, `pr_body.md`, optional slice assertions): `carry_forward` in `full_runtime_prompt_authority_proof.json`.

## What was proven (generated lanes)

For **headline**, **executive_summary**, **competencies**, **unify_narrative**, **unify_bullets**, **ibm_narrative**, **ibm_bullets**:

| Claim | Evidence |
|-------|----------|
| apps_rg-owned templates / contracts | `section_prompt_contracts/*.contract.yaml` + `prompt_assembly/templates/*` refs in bundle JSON |
| Compile via PA + `section_prompt_adapter` | `test_apps_rg_no_inline_prompt_authority.py` (dispatch `build_prompt_messages` → `compile_*`, PA modules import `compile_section_prompt`) |
| `CompiledPromptArtifact` path | Same + dispatch implementations write `compiled_prompt_artifact.json` |
| `prompt_hash` present | Dispatch implementations (sha16 of serialized messages); not yet asserted in slice JSON fixtures |
| `section_id` present | Contracts + runtime payloads (slice tests cover mock dispatch / X2 plumbing) |
| No active inline prompt authority | W10 tests + registry integrity scans |
| No silent inline fallback | Adapter source scan in W10 test |
| Ledger-only display | `test_apps_rg_ledger_only_citations.py` |
| X2 vs X1D boundary | `test_apps_rg_x2_x1d_alignment.py` + `x2_x1d_alignment_matrix.json` |
| Locked deterministic sections not LLM lanes | Matrix rows for education / certifications / early_career (`llm_generation_allowed: false`) |

## Proof commands (recorded)

Run from repo root (Windows `cmd`):

```bat
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest -p pytest_timeout tests/_apps_contract/test_apps_rg_prompt_registry_integrity.py tests/_apps_contract/test_apps_rg_no_inline_prompt_authority.py tests/_apps_contract/test_apps_rg_x2_x1d_alignment.py tests/_apps_contract/test_apps_rg_ledger_only_citations.py -q --tb=short
python -m pytest -p pytest_timeout tests/_apps_contract/test_exec_summary_runtime_slice.py::test_qwen_unavailable_blocks_not_mocks -q --tb=short
python -m pytest -p pytest_timeout tests/_apps_contract/test_headline_runtime_slice.py tests/_apps_contract/test_exec_summary_runtime_slice.py tests/_apps_contract/test_competencies_runtime_slice.py -q --tb=short
python -m pytest -p pytest_timeout tests/_apps_contract/test_unify_narrative_runtime_slice.py tests/_apps_contract/test_unify_bullets_runtime_slice.py tests/_apps_contract/test_ibm_narrative_runtime_slice.py tests/_apps_contract/test_ibm_bullets_runtime_slice.py -q --tb=short
git diff --name-only -- agentic_core
git status --short -- agentic_core
```

Full `tests/_apps_contract` was **not** run (out of scope).

## Git / artifacts

- `.gitignore` allows **only** `artifacts/apps_rg/prompt_authority/*.json` to be versioned; **`artifacts/apps_rg/runtime_proofs/` remains ignored** (bulky).
