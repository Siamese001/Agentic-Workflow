# W0 — Baseline proof (apps_rg prompt authority program)

**SSOT:** `apps_rg_prompt_remediation_program.md`  
**Hardening language:** apps_rg owns prompt content; PA assembles, fences, hashes, and emits `CompiledPromptArtifact`; L2 executes; X2 / X1D / Exit judge outcomes.

## W0 status (two layers)

| Scope | Status | Basis |
|-------|--------|--------|
| **Overall W0** (incl. program-listed `test_apps_rg_pa_tiered_prompt` + full `tests/_apps_contract`) | **PARTIAL** | Reds below are **not** treated as scoped W0–W3 blockers; see classification. |
| **Scoped W1–W3** (inventory/classification, `section_prompt_contracts`, `section_prompt_adapter`, adapter tests, no lane migration) | **PASS** | Headline/exec-summary/competencies slices green; adapter tests green; inventory artifacts present; no `agentic_core` diff. |

**Do not** expand W0–W3 to fix the full `tests/_apps_contract` suite.

## Task 361987 — W0 baseline evidence (Cursor shell task)

Short pointer: `command_transcripts/w0_task_361987_evidence.txt`. JSON: `artifacts/apps_rg/prompt_authority/w0_test_status.json` (`cursor_shell_task_evidence`).

Captured runs include the batch that produced **exit 1** on broader pytest surfaces. Canonical numbers recorded here:

| Evidence | Result |
|----------|--------|
| `tests/_apps_contract/test_apps_rg_pa_tiered_prompt.py` | **exit 1**, **97 failed** (23 passed) — transcript `command_transcripts/w0_pytest_test_apps_rg_pa_tiered_prompt.txt` |
| Full `tests/_apps_contract` rerun | Transcript: **`docs/reports/apps_rg_prompt_authority/command_transcripts/w0_pytest_apps_contract_full_rerun.txt`** |
| Full suite summary | **exit 1** — **1605 failed** / **4890 passed** / **19 skipped** / **81 errors** (857.52s) |
| **Classification** | **Broader suite / profile-contract drift** — **not** a scoped W0–W3 blocker for prompt authority inventory + adapter seam. |

### Explicit W0 notes (triage, not in-scope fixes)

- Missing `apps_rg/config/domain_contract/resume_pa_prompt_profile.v1.json` and **`SectionPromptArtifact` drift** (vs `test_apps_rg_pa_tiered_prompt.py` expectations) are **candidate W13** full-suite triage items.
- **Do not** fix them in W0–W3 **unless** they block `section_prompt_adapter` / `test_apps_rg_section_prompt_adapter` (they do not today).

## Constraints honored (W0–W1)

- Did **not** edit `prompt_registry.yaml`.
- Did **not** edit dispatch prompt bodies.
- Did **not** migrate executive_summary, competencies, headline, IBM, or Unify lanes in this pass.
- No **`agentic_core`** edits.

## Tooling

- **pytest:** use `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` with `python -m pytest -p pytest_timeout …` so `pytest_timeout` is not registered twice.
- **Search:** `rg` may be unavailable on PATH; `python tools/apps_rg/prompt_inventory_grep.py` used for read-only inventory (see `command_transcripts/w0_prompt_inventory_grep.txt`).

## Command transcripts (repo-relative)

| Step | Transcript | Exit |
|------|------------|------|
| `git status --short` | `command_transcripts/w0_git_status.txt` | 0 |
| prompt inventory grep | `command_transcripts/w0_prompt_inventory_grep.txt` | 0 |
| headline slice | `command_transcripts/w0_pytest_headline.txt` | 0 |
| exec summary slice | `command_transcripts/w0_pytest_test_exec_summary_runtime_slice.txt` | 0 |
| competencies slice | `command_transcripts/w0_pytest_test_competencies_runtime_slice.txt` | 0 |
| PA tiered prompt | `command_transcripts/w0_pytest_test_apps_rg_pa_tiered_prompt.txt` | 1 (97 failed) |
| full `tests/_apps_contract` | `command_transcripts/w0_pytest_apps_contract_full_rerun.txt` | 1 |
| W3 adapter tests | `command_transcripts/w3_pytest_section_prompt_adapter.txt` | 0 |
| `git diff --name-only -- agentic_core` | `command_transcripts/w0_agentic_core_diff.txt` | 0 |

## Interpretation

- **Required narrative slices (headline, executive summary, competencies):** PASS (exit 0).
- **`test_apps_rg_pa_tiered_prompt.py`:** recorded above; excluded from scoped W1–W3 PASS gate.
- **Full `tests/_apps_contract`:** recorded above; excluded from scoped W1–W3 PASS gate.

## Artifacts

- `artifacts/apps_rg/prompt_authority/w0_prompt_inventory_before.json`
- `artifacts/apps_rg/prompt_authority/w0_runtime_bypass_map_before.json`
- `artifacts/apps_rg/prompt_authority/w0_test_status.json`
- `artifacts/apps_rg/prompt_authority/template_classification.json`
- `artifacts/apps_rg/prompt_authority/runtime_bypass_map.json`

## W1–W3 continuation (this tranche)

- Inventory / classification: `W1_prompt_inventory.md` + JSON under `artifacts/apps_rg/prompt_authority/`
- `section_prompt_contracts/`: schema + stubs (incl. locked non-LLM sections)
- `apps_rg/runtime/bindings/section_prompt_adapter.py` + `tests/_apps_contract/test_apps_rg_section_prompt_adapter.py`
- **No** executive_summary (or other lane) migration yet
