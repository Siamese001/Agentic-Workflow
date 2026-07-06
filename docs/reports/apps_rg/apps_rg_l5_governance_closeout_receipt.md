# apps_rg L5 Governance Closeout Receipt

Plan: `apps-rg-l5-governance-best-practice-closure`

Branch: `codex/apps-rg-l5-governance-closure`

Date: 2026-07-06

## Runtime Flow

`apps_rg` now materializes L5 governance evidence as:

`profile -> child receipts -> egress receipts -> L5 packet -> Exit consumption -> UWG/L4 sidecar evidence`

The L5 packet is evidence-only. Exit consumes `l5_certification_packet_ref`, `l5_certification_packet_digest`, and `l5_certification_status` as a fail-closed input. A non-certified, missing, malformed, or placeholder-backed packet blocks `outcome_authorized` and emits no `SectionCacheWriteProposal`.

## Explicit Non-Authorities

- L5 does not emit `GateVerdict`.
- L5 does not emit X3.
- L5 does not write L4.
- L5 does not commit durable cache or vector state.
- L5 does not rescue the current run.
- Eval results do not waive runtime gates.
- Exit and L2 do not commit durable state.

## Gaps Closed

| Gap | Disposition |
|---|---|
| G1 | Closed by `apps_rg/runtime/l5/packet_builder.py` and governed L2/Exit attachment. |
| G2 | Closed by typed metadata-only egress receipts from ProviderGateway exchange metadata. |
| G3 | Closed by profile loader and child receipt materializer. |
| G4 | Closed by deterministic production U0 cert refs and test-only placeholder flag. |
| G5 | Closed by deterministic L2 attempt seed from replay key, prompt hash, attempt number, and lane id. |
| G6 | Closed by typed egress receipt fields and packet context digest fields. |
| G7 | Closed by fail-closed CI cert-ref enforcement and bypass rejection. |
| G8 | Closed by HITL disabled `NOT_APPLICABLE` triple and reclearance validation. |
| G9 | Closed by direct durable-write static scanner and UWG/L4 sidecar digest propagation. |
| G10 | Closed by unit, governance, contract, and eval coverage. |

Deferred: none.

## Validation Targets

Static:

- `APPS_RG_L5_CERT_REFS_FAIL_CLOSED=1 python ops_scripts/ci/check_apps_rg_l5_cert_refs.py`
- `python ops_scripts/ci/check_apps_rg_l5_no_authority_widening.py`
- `python ops_scripts/ci/check_apps_rg_l5_packet_runtime_wiring.py`
- `python ops_scripts/ci/check_apps_rg_no_direct_durable_writes.py`

Unit and contract:

- `pytest tests/unit/agentic_core/L5_safety/test_l5_packet_producer.py -q`
- `pytest tests/unit/agentic_core/L5_safety/test_egress_certifier.py -q`
- `pytest tests/unit/apps_rg/test_l5_governance_profile.py -q`
- `pytest tests/unit/apps_rg/test_l5_child_receipts.py -q`
- `pytest tests/unit/apps_rg/test_l5_packet_builder_runtime.py -q`
- `pytest tests/unit/apps_rg/test_l5_egress_receipts.py -q`
- `pytest tests/unit/apps_rg/test_l5_replay_audit_receipts.py -q`
- `pytest tests/unit/apps_rg/test_l5_hitl_reclearance.py -q`
- `pytest tests/unit/apps_rg/test_c0_semantic_cache_payload_uwg_l4.py -q`
- `pytest tests/governance/test_l5_cross_child_certification.py -q`
- `pytest tests/governance/test_apps_rg_l5_authority_boundaries.py -q`
- `pytest tests/governance/test_apps_rg_no_direct_cache_write_bypass.py -q`
- `pytest tests/_apps_contract/test_apps_rg_l5_runtime_wiring.py -q`
- `pytest tests/_apps_contract/test_apps_rg_l2_envelope.py -q`

Eval:

- `pytest tests/evals/apps_rg/test_l5_lane_eval.py -q`
- `pytest tests/evals/apps_rg/test_l5_suite_eval.py -q`

## Final Command Transcript

Static gates:

- `APPS_RG_L5_CERT_REFS_FAIL_CLOSED=1 python ops_scripts/ci/check_apps_rg_l5_cert_refs.py`: scanned 59 files, 8 refs, 0 issues, GREEN.
- `python ops_scripts/ci/check_apps_rg_l5_no_authority_widening.py`: scanned 6 core certification files and 488 apps_rg files, 0 issues, GREEN.
- `python ops_scripts/ci/check_apps_rg_l5_packet_runtime_wiring.py`: checked 3 runtime files, 0 issues, GREEN.
- `python ops_scripts/ci/check_apps_rg_no_direct_durable_writes.py`: scanned 488 files, 0 issues, GREEN.

Unit:

- `pytest tests/unit/agentic_core/L5_safety/test_l5_packet_producer.py -q`: 102 passed.
- `pytest tests/unit/agentic_core/L5_safety/test_egress_certifier.py -q`: 93 passed.
- `pytest tests/unit/apps_rg/test_l5_governance_profile.py -q`: 4 passed.
- `pytest tests/unit/apps_rg/test_l5_child_receipts.py -q`: 4 passed.
- `pytest tests/unit/apps_rg/test_l5_packet_builder_runtime.py -q`: 5 passed.
- `pytest tests/unit/apps_rg/test_l5_egress_receipts.py -q`: 5 passed.
- `pytest tests/unit/apps_rg/test_l5_replay_audit_receipts.py -q`: 3 passed.
- `pytest tests/unit/apps_rg/test_l5_hitl_reclearance.py -q`: 4 passed.
- `pytest tests/unit/apps_rg/test_c0_semantic_cache_payload_uwg_l4.py -q`: 11 passed.

Governance/contract:

- `pytest tests/governance/test_l5_cross_child_certification.py -q`: 6 passed.
- `pytest tests/governance/test_apps_rg_l5_authority_boundaries.py -q`: 3 passed.
- `pytest tests/governance/test_apps_rg_no_direct_cache_write_bypass.py -q`: 2 passed.
- `pytest tests/_apps_contract/test_apps_rg_l5_runtime_wiring.py -q`: 4 passed.
- `pytest tests/_apps_contract/test_apps_rg_l2_envelope.py -q`: 150 passed.

Eval:

- `pytest tests/evals/apps_rg/test_l5_lane_eval.py -q`: 1 passed.
- `pytest tests/evals/apps_rg/test_l5_suite_eval.py -q`: 6 passed.

Additional hygiene:

- `ruff check --select F401,F821 ...`: all checks passed.
- `python -m compileall -q ...`: passed.

Non-failing warnings observed: existing `apps_test_model` marker is not registered with pytest in several new governance/eval tests; C0/UWG tests emit existing SWIG deprecation warnings.
