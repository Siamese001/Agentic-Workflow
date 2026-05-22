# apps_rg legacy SRFS JSON purge — D2 receipt

**Plan:** [apps-rg-legacy-srfs-json-purge-a8f3c1.md](../../.cursor/plans/apps-rg-legacy-srfs-json-purge-a8f3c1.md)  
**Generated:** 2026-05-22

## D2 — Remove SRFS envelope from product runtime path

### Runtime (graph-only authority)

- [executive_summary_x2.py](../../apps_rg/runtime/validators/executive_summary_x2.py) — removed SRFS-only X2 checks; `run_x2_gates` uses `proof_pool_metadata.graph_skills_proof_pool` only; `srfs_integration` arg ignored on painting shape check
- [executive_summary_judge_packet.py](../../apps_rg/runtime/judges/executive_summary_judge_packet.py) — always `GRAPH_ONLY` rubric; no SRFS rows in `build_deterministic_gate_summary`; dropped `srfs_integration` kwarg
- [executive_summary_composition.py](../../apps_rg/runtime/sections/executive_summary_composition.py) — painting gates via `_graph_painting_active` / graph metadata
- [executive_summary_lane.py](../../apps_rg/runtime/sections/executive_summary_lane.py) — stripped `srfs_integration` from payload, X2, judge packet, remediation; no `selected_role_fact_set_ref.json` write
- [executive_summary_judge_remediation.py](../../apps_rg/runtime/sections/executive_summary_judge_remediation.py) — remediation X2 paths no longer thread SRFS envelope
- [selected_role_fact_set.py](../../apps_rg/runtime/sections/selected_role_fact_set.py) — `load_selected_role_fact_set`, `build_srfs_integration_envelope`, `resolve_srfs_section_proof_bundle` raise `RuntimeError` on product path

### Tests updated

- [test_selected_role_fact_set_runtime.py](../../tests/unit/apps_rg/test_selected_role_fact_set_runtime.py)
- [test_exec_summary_runtime_slice.py](../../tests/_apps_contract/test_exec_summary_runtime_slice.py) (SRFS gate omission + painting shape)
- [test_executive_summary_judge_packet_srfs_rubric.py](../../tests/_apps_contract/test_executive_summary_judge_packet_srfs_rubric.py) — expects graph rubric always
- [test_executive_summary_x2_x1d_alignment.py](../../tests/_apps_contract/test_executive_summary_x2_x1d_alignment.py)
- [test_executive_summary_composition_x2.py](../../tests/unit/apps_rg/test_executive_summary_composition_x2.py)
- [test_exec_summary_pa_compiled_prompt.py](../../tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py) (judge packet shape)

### Proof

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout \
  tests/unit/apps_rg/test_selected_role_fact_set_runtime.py \
  tests/_apps_contract/test_exec_summary_runtime_slice.py::test_x2_srfs_gates_omitted_when_no_selected_role_fact_set \
  tests/_apps_contract/test_exec_summary_runtime_slice.py::test_srfs_sentence_responsibility_shape_passes_compliant_five_sentences \
  tests/_apps_contract/test_exec_summary_runtime_slice.py::test_compile_exec_summary_srfs_includes_style_oneshot_block \
  tests/_apps_contract/test_executive_summary_judge_packet_srfs_rubric.py \
  tests/_apps_contract/test_executive_summary_x2_x1d_alignment.py \
  tests/unit/apps_rg/test_executive_summary_composition_x2.py \
  tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py::test_executive_summary_judge_packet_grade_only_shape \
  -> 38 passed
```

### Live proof (optional — not run this session)

BLOCKED in workspace: `APPS_RG_L2_PROVIDER_MODE=stub_only` rejects `--provider qwen_vllm`. When live provider is available:

```text
python -m apps_rg --section executive_summary --provider qwen_vllm --allow-non-allow-exit-zero
python ops_scripts/apps_rg/run_live_section_authority_proof.py
```

### Deferred to D3–D5 (still reference SRFS vocabulary / JSON)

- [executive_summary_pa.py](../../apps_rg/runtime/sections/executive_summary_pa.py) — `format_srfs_role_adaptive_appendix`, reads `runtime_payload["srfs_integration"]`
- [executive_summary_evidence_capsule.py](../../apps_rg/runtime/sections/executive_summary_evidence_capsule.py) — capsule still accepts `srfs_integration` dict (JSON file load fail-closed from D1)
- [exec_summary_graph_projection_w4b.py](../../apps_rg/fact_inventory/exec_summary_graph_projection_w4b.py) — inventory envelope builder (D4)
- ~~srfs_receipt_aggregator~~ (removed D3 — see [d3_receipt](apps_rg_legacy_srfs_json_purge_d3_receipt.md))
