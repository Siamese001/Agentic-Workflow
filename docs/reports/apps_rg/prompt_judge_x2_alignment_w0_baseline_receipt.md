# W0 Baseline Receipt — prompt-judge-x2-alignment-closeout-c8e4a2

**Wave:** W0 (baseline + manifest + red-before-green tests)  
**Date:** 2026-05-26  
**Proof class:** static + smoke (not canonical runtime)

## Prior plan revalidation

[section-product-shape-alignment-b4e7a1](../../.cursor/plans/section-product-shape-alignment-b4e7a1.md) is **claimed complete — revalidated here**. Drift audit path handling remains unsafe for absolute/traversal refs until W1.4.

## W0.1 — Baseline commands

### Drift audit (`audit_all_generated_lanes`)

```text
Command: PYTHONPATH=. python -c "from apps_rg.runtime.sections.section_prompt_drift_audit import audit_all_generated_lanes; v=audit_all_generated_lanes(); print(len(v)); [print(x) for x in v[:20]]"
Result: 0 violations (Windows host — forward-slash refs resolve via backslash substitution)
```

### Lockstep audit (`audit_all_generated_sections_prompt_judge`)

```text
Command: PYTHONPATH=. python -c "from apps_rg.runtime.sections.section_prompt_judge_alignment import audit_all_generated_sections_prompt_judge; v=audit_all_generated_sections_prompt_judge(); print(len(v)); [print(x) for x in v[:20]]"
Result: 0 violations
```

**Note:** Zero drift violations on Windows does not prove POSIX-safe path resolution. W1.4 must wire [`resolve_repo_template_path`](../../apps_rg/runtime/sections/section_prompt_authority_ssot.py) into drift audit; closeout drift assert required on all platforms.

### Unsafe path probe (current `_repo_path`)

| ref | resolves | in_repo (strict) |
|-----|----------|------------------|
| `apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml` | OK | yes |
| `/etc/passwd` | `C:\etc\passwd` | **no — not rejected** |
| `apps_rg/../../../outside.txt` | escapes | **not rejected** |

## W0.2 — Deliverables

| Artifact | Path |
|----------|------|
| Executable prompt authority SSOT | [section_prompt_authority_ssot.py](../../apps_rg/runtime/sections/section_prompt_authority_ssot.py) |
| P0 lanes | executive_summary, competencies, unify_bullets, ibm_bullets, unify_narrative, ibm_narrative |

## W0.3 — Red-before-green tests

Command: `python -m pytest tests/unit/apps_rg/test_prompt_judge_x2_alignment_w0.py -q -o addopts=`

| Test | Result (2026-05-26) | W1 owner |
|------|---------------------|----------|
| `test_exec_summary_x1d_rubric_lists_all_ssot_dimensions` | **FAIL** — missing `evidence_utilization`, `deterministic_alignment` | W1.1 |
| `test_exec_summary_pa_claim_ledger_guidance_consistent` | **FAIL** — graph guard still says one row per sentence | W1.2 |
| `test_competencies_u0_schema_matches_x2` | **FAIL** — U0 lacks `categories` key in output contract | W1.3 |
| `test_drift_audit_repo_path_rejects_absolute_and_traversal` | **FAIL** — `_repo_path` accepts `/etc/passwd` | W1.4 |
| `test_resolve_repo_template_path_safe` | **PASS** | — |
| `test_prompt_authority_executable_corpus_non_empty` | **PASS** | — |

**Summary:** 4 failed, 2 passed (intended red-before-green state).

**W1 resolution (2026-05-26):** All six W0 tests green after W1.1–W1.4 patches.

**Checkpoint discipline:** W0+W1 may merge together on default branch (6/6 green).

## Explicit non-claims

- No live provider certification
- No full canonical Brown/Forge runtime run
- No release eligibility beyond unit/contract/smoke for this wave
