# apps_rg X2 dead gates — W4 receipt

**Plan:** [apps-rg-x2-dead-gates-burndown-c4e8f2.md](../../.cursor/plans/apps-rg-x2-dead-gates-burndown-c4e8f2.md)  
**User approval:** Option A — SRFS structural X2 retired on default graph/ledger path (2026-05-22)  
**Generated:** 2026-05-22

## W4 — SRFS skip-PASS emission removal + live proof

### Preconditions verified

- `apps_rg/config/targeting/**`: **no** `artifact_path_resolved` (SRFS envelope not in repo targeting SSOT).
- SRFS structural gates still emit when `srfs_integration.artifact_path_resolved` is set (contract tests unchanged).

### Runtime (W4.1)

- [executive_summary_x2.py](../../apps_rg/runtime/validators/executive_summary_x2.py): `x2_srfs_*` gates wrapped in `_srfs_mode_active(srfs_integration)` only.
- `x2_source_sensitive_phrases_supported`: emitted only when `selected_facts` substrate is present (no PASS `"skipped"` row).
- [section_complexity_reduction_audit.py](../../ops_scripts/apps_rg/section_complexity_reduction_audit.py): static catalog updated for W4 omission semantics.

### Proof (W4.2)

**Unit / contract**

```text
pytest -p pytest_timeout tests/_apps_contract/test_exec_summary_runtime_slice.py::test_x2_srfs_gates_omitted_when_no_selected_role_fact_set tests/_apps_contract/test_exec_summary_runtime_slice.py::test_x2_srfs_standalone_proof_id_gate_fails_when_integration_active tests/_apps_contract/test_executive_summary_x2_x1d_alignment.py -> 8 passed
```

**Live executive_summary (qwen_vllm, REAL_LLM)**

```text
python -m apps_rg --section executive_summary --provider qwen_vllm --target-company Neo4j --target-role "VP Product Management Agentic AI" --jd apps_rg/config/targeting/neo4j_vp_product_management_agentic_ai_jd.txt --manual-brief tests/_fixtures/ci-probe-briefing.txt --allow-non-allow-exit-zero
```

Bundle: [exec_summary_20260522_095758](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260522_095758/)

| Check | Result |
|-------|--------|
| `x2_srfs_*` gate IDs in `x2_gate_outputs.json` | **none** |
| `skipped_no_selected_role_fact_set` on any gate | **none** |
| `x2_source_sensitive_phrases_supported` | **present PASS** (graph path has `selected_facts`) |
| `x2_srfs_gate_status` in proof-pool receipt | `NOT_APPLICABLE` |
| `RUNTIME_GENERATION_STATUS` | `REAL_LLM` |
| CLI / product | `X3_BLOCK` on product X2 (jd alignment, evidence utilization, mechanism inventory) — **not** SRFS skip rows |

**Section authority proof (four lanes)**

```text
python ops_scripts/apps_rg/run_live_section_authority_proof.py -> exit 0
```

All sections: `evidence_authority.type` = `augmented_skills_graph`, `graph_ref`/`ledger_ref` = `present` (executive_summary ledger: [exec_summary_20260522_100933](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260522_100933/section_input_usage_ledger.json)).

### W4.1 deferral (only if you still run live SRFS in production)

If a targeting job **outside** this repo sets `artifact_path_resolved`, SRFS structural gates will still emit and enforce. No change required for that opt-in path. Say so if you want a narrow W4.1 follow-up to grep production envelopes.

### Out of scope (unchanged)

- Harness tests expecting removed CLI `--selected-role-fact-set` / offline SRFS slice gate PASS rows.
- Retired SRFS repair modules (W2) and proof-pool slice IDs (W3).
