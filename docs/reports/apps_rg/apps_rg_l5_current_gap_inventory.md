# apps_rg L5 Governance Current Gap Inventory

Plan: `apps-rg-l5-governance-best-practice-closure`

Scope: apps_rg L5 governance certification runtime wiring, CI, and eval closure. This inventory freezes the pre-wiring gap surface and names the evidence files changed by the closure branch.

## Gap Table

| Gap | Baseline Finding | Closure Status | Evidence |
|---|---|---|---|
| G1 | Core `L5PacketProducer` existed, but apps_rg did not require a runtime `L5CertificationPacket`. | Closed | `apps_rg/runtime/l5/packet_builder.py`, `apps_rg/runtime/spine/governed_l2_exit_compose.py`, `apps_rg/runtime/bindings/exit_binding.py` |
| G2 | Core egress certifier existed, but ProviderGateway metadata did not materialize a typed `EgressCertificationReceipt`. | Closed | `apps_rg/runtime/l5/egress_receipts.py`, `apps_rg/runtime/bindings/l2_envelope_adapter.py` |
| G3 | Governance profile existed as static YAML but did not emit child receipts. | Closed | `apps_rg/runtime/l5/governance_profile.py`, `apps_rg/runtime/l5/child_receipts.py` |
| G4 | U0 could fall back to `test:valid:w6`. | Closed | `apps_rg/runtime/bindings/u0_binding.py`, `tests/unit/apps_rg/test_l5_packet_builder_runtime.py` |
| G5 | L2 attempt seed used nondeterministic UUID material. | Closed | `apps_rg/runtime/bindings/l2_envelope_adapter.py`, `tests/unit/apps_rg/test_l5_replay_audit_receipts.py` |
| G6 | Egress receipt digests lived in notes instead of typed fields. | Closed | `agentic_core/L5_safety/contracts/l5_certification_contracts.py`, `agentic_core/L5_safety/certification/egress_certifier.py` |
| G7 | Cert-ref CI gate was advisory unless an env var was set. | Closed | `ops_scripts/ci/check_apps_rg_l5_cert_refs.py`, `.github/workflows/contract-gates.yml` |
| G8 | HITL disabled path lacked reclearance fail-closed posture. | Closed | `apps_rg/runtime/l5/hitl_reclearance.py`, `apps_rg/runtime/l5/child_receipts.py` |
| G9 | Direct durable cache write guard was not explicit for legacy bypass patterns. | Closed | `ops_scripts/ci/check_apps_rg_no_direct_durable_writes.py`, `tests/governance/test_apps_rg_no_direct_cache_write_bypass.py` |
| G10 | Tests did not prove full runtime packet wiring through U0/L1/C0/PA/L2/Exit. | Closed | `tests/_apps_contract/test_apps_rg_l5_runtime_wiring.py`, `tests/evals/apps_rg/test_l5_lane_eval.py`, `tests/evals/apps_rg/test_l5_suite_eval.py` |

## Authority Boundaries

L5 certification evidence remains evidence-only. It does not emit `GateVerdict`, does not emit X3, does not route/retrieve/execute, does not write L4, and does not rescue the current run. Exit consumes L5 packet status as an additional fail-closed gate before user-visible allow or cache proposals.

App-specific runtime wiring stays under `apps_rg/runtime/l5`. `agentic_core/L5_safety` changes are limited to app-agnostic contract fields and certifier validation.

## File Evidence List

- Core contracts: `agentic_core/L5_safety/contracts/l5_certification_contracts.py`
- Core packet/egress producers: `agentic_core/L5_safety/certification/l5_packet_producer.py`, `agentic_core/L5_safety/certification/egress_certifier.py`
- apps_rg L5 runtime: `apps_rg/runtime/l5/*.py`
- Runtime spine: `apps_rg/runtime/bindings/u0_binding.py`, `apps_rg/runtime/bindings/l2_envelope_adapter.py`, `apps_rg/runtime/bindings/exit_binding.py`, `apps_rg/runtime/spine/governed_l2_exit_compose.py`
- UWG/L4 evidence chain: `apps_rg/cache/r1b_uwg_promotion.py`, `apps_rg/cache/r1b_governed_receipt_emission.py`
- CI guards: `ops_scripts/ci/check_apps_rg_l5_cert_refs.py`, `ops_scripts/ci/check_apps_rg_l5_no_authority_widening.py`, `ops_scripts/ci/check_apps_rg_l5_packet_runtime_wiring.py`, `ops_scripts/ci/check_apps_rg_no_direct_durable_writes.py`
