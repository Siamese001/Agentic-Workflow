# ProceduralPattern:L2E4RealHealingPromptPacketRepair

- L2 E4 healing is only real when the repaired prompt packet is consumed by the retry, not when E4 only emits a `HealReceipt`.
- Package-driven L2 repair must return a modified `CompiledPromptArtifact` with H0 bounded repair context, changed prompt hash, and `HealReceipt.before_prompt_hash` / `after_prompt_hash` / `repaired_packet_ref`.
- `apps_rg` E4 safe-local repairs must carry a `repair_patch`; `run_apps_rg_l2_envelope()` applies that patch to the active CPA before `RETURN_TO_E3` retries and seals E5 with the repaired packet.
- Verify with `python -m pytest tests/unit/agentic_core/L2_execution/test_l2_package_driven_repair.py tests/_apps_contract/test_w6_l2_package_driven_execution.py tests/_apps_contract/test_apps_rg_l2_envelope.py::TestE4AllowedRepairs tests/unit/agentic_core/L2_execution/test_l2_v3_pipeline.py::TestHealLoop tests/unit/agentic_core/L2_execution/test_l2_two_phase_healer.py -q`.
- Do not treat raw-text unwrap inside E3 or a standalone app E4 module as proof that active L2 E4 healing happened; prove the retry consumed a changed prompt packet.
- discovered: 2026-07-01, validated: 2026-07-01
