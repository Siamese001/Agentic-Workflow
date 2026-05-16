# W12 — Full runtime prompt-authority proof (apps_rg)

## Status

**BLOCKED (purity gate)** on 2026-05-16 closeout: scoped `apps_rg` proof **passed** (57 + 70 + 44 = **171** tests on re-run), but **`agentic_core`** still carries **substantive binding/exit edits** (tracked diff + untracked `runtime/bindings/` and exit pipeline modules). Classified as **required shared-core / parallel initiative**, not prompt-authority — per W12 rules **no silent revert** here; move work to its own branch or explicitly request revert to achieve **PASS**.

Prior label **PARTIAL** (proof good, tree dirty) is superseded for closeout by **BLOCKED** until the tree is clean.

Durable bundle: `artifacts/apps_rg/prompt_authority/full_runtime_prompt_authority_proof.json`

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
python -m pytest -p pytest_timeout tests/_apps_contract/test_headline_runtime_slice.py tests/_apps_contract/test_exec_summary_runtime_slice.py tests/_apps_contract/test_competencies_runtime_slice.py -q --tb=short
python -m pytest -p pytest_timeout tests/_apps_contract/test_unify_narrative_runtime_slice.py tests/_apps_contract/test_unify_bullets_runtime_slice.py tests/_apps_contract/test_ibm_narrative_runtime_slice.py tests/_apps_contract/test_ibm_bullets_runtime_slice.py -q --tb=short
git diff --name-only -- agentic_core
```

Full `tests/_apps_contract` was **not** run (out of scope).

## Git / artifacts

- `.gitignore` now allows **only** `artifacts/apps_rg/prompt_authority/*.json` to be versioned; **`artifacts/apps_rg/runtime_proofs/` remains ignored** (bulky).
- Promote **PASS** after: `git diff --name-only -- agentic_core` is empty **and** no unintended untracked `agentic_core` paths remain.

## Carry-forward

See `carry_forward` in `full_runtime_prompt_authority_proof.json`.
