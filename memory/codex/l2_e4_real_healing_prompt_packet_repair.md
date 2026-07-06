# ProceduralPattern:L2E4RepairAuthorityModes

- L2 E4 repair proof is mode-specific: generic package-driven L2 proves repair by consuming a changed prompt packet; `apps_rg` v4 envelope proves repair by consuming the same prompt text with a sealed repair receipt and retry audit ref.
- Package-driven L2 repair may return a modified `CompiledPromptArtifact` with H0 bounded repair context, changed prompt hash, and `HealReceipt.before_prompt_hash` / `after_prompt_hash` / `repaired_packet_ref`.
- `apps_rg` v4 envelope E4 must not mutate `user_instruction`, `prompt_blocks`, or `compilation_hash`; safe-local repairs carry `repair_patch.h0_context` plus `bounded_context`, append `l2_e4_repair:<id>` to retry CPA audit refs, and keep `HealReceipt.before_hash == after_hash`.
- Verify apps_rg v4 envelope with `python -m pytest tests/_apps_contract/test_apps_rg_l2_envelope.py::TestE4AllowedRepairs tests/_apps_contract/test_apps_rg_l2_envelope.py::TestW7FailClosed tests/_apps_contract/test_apps_rg_governed_l2_exit_w6.py -q`.
- Do not apply the package-driven prompt-mutation law to `run_apps_rg_l2_envelope()`; do not accept an apps_rg repair unless the retry consumes the audit-linked CPA and E5 seals the heal ref.
- discovered: 2026-07-01, updated: 2026-07-05, validated: 2026-07-05
