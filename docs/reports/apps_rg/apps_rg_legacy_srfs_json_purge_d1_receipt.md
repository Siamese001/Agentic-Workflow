# apps_rg legacy SRFS JSON purge — D1 receipt

**Plan:** [apps-rg-legacy-srfs-json-purge-a8f3c1.md](../../.cursor/plans/apps-rg-legacy-srfs-json-purge-a8f3c1.md)  
**Generated:** 2026-05-22

## D1 — Delete orphaned SRFS JSON runtime modules

### Deleted

- [executive_summary_srfs_binding.py](../../apps_rg/runtime/sections/executive_summary_srfs_binding.py) — `selected_role_fact_set_active.json` materialization (no callers)
- [exec_summary_srfs_integration.py](../../apps_rg/runtime/sections/exec_summary_srfs_integration.py) — JSON path bundle loader
- [exec_summary_srfs_judge_safe.py](../../apps_rg/runtime/sections/exec_summary_srfs_judge_safe.py) — SRFS repair stack (~55K LOC)
- [test_exec_summary_srfs_judge_safe.py](../../tests/unit/apps_rg/test_exec_summary_srfs_judge_safe.py)
- [test_exec_summary_srfs_judge_safe_repair_monotonic.py](../../tests/unit/apps_rg/test_exec_summary_srfs_judge_safe_repair_monotonic.py)

### Disabled

- `try_judge_safe_prefilter` → no-op ([executive_summary_judge_remediation.py](../../apps_rg/runtime/sections/executive_summary_judge_remediation.py))
- `load_srfs_and_build_capsule_from_path` → fail-closed `srfs_json_file_authority_removed` ([executive_summary_evidence_capsule.py](../../apps_rg/runtime/sections/executive_summary_evidence_capsule.py))

### Proof

```text
pytest tests/unit/apps_rg/test_selected_role_fact_set_runtime.py tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py::test_parsed_to_raw_model_output_json_omits_selected_fact_plan tests/_apps_contract/test_exec_summary_runtime_slice.py::test_x2_srfs_gates_omitted_when_no_selected_role_fact_set -> 19 passed
```

### Still to delete (D3–D5)

- PA/capsule `srfs_integration` reads (fail-closed loaders removed in D1; lane threading removed in D2)
- `srfs_receipt_aggregator`, inventory JSON writers, `exec_summary_srfs_arsenal` (after graph migration)
- `APPS_RG_BROAD_SKILLS_LEDGER_PATH` / metadata fields (authority already blocked)
