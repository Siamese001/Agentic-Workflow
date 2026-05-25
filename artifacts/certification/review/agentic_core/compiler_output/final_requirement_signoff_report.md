# Fort Knox v2 — Runtime Certification Sign-off Report

> ⚠️ **READ-ONLY VIEW.** JSON compiler report is the authority.
> Manual edits here do NOT affect certification status.

## Trust & Provenance

| Field | Value |
|---|---|
| Trust level | **`INTEGRITY_PROOF`** |
| Run timestamp (UTC) | `2026-05-02T03:42:18+00:00` |
| Compiler version | `fortknox-v2.0` |
| Compiler sha256 | `dffbb16a9d46e5bdb8871fec5122f8d5e9da6d8ff4ec0525dfd51d53aa4032cc` |
| Git commit | `7c344fdb548b22658ca183c96d23654eff677f0d` |
| Git dirty | `True` |
| Requirements source SHA256 | `c8cac746a9bc26b0914570220e7360b119b29d6797c5bf89f80b14cf58bd5ecc` |
| Evidence assertions SHA256 | `0078874ccd073df126abb72c8762dd427a9ff7561f8a28cb246dcd68d6035e2c` |
| Row digest | `519bc7853d0d25ff77a7b641f24497356eceb7a49d46a061783e696488461d78` |
| Evidence digest | `06f3a91ac9123371bd08a2c5e8b9ef21c02acb9fdb1e0e929b30ce94c74f9df4` |
| Merkle root | `dd38dc5e0c7c0871ddfdee00170745f2264ef772fdb78089ec41fcaace1ed485` |
| Merkle leaf count | `87` |
| Signature status | `UNSIGNED_PENDING_SIGNATURE` |
| Bundle verification | `PASS` (2079 checks, 0 failures) |

## Summary

**Total**: 87

| Status | Count | % |
|---|---:|---:|
| ✅ SIGNED_OFF | 87 | 100.0% |
| 🔒 BLOCKED | 0 | 0.0% |
| ⚠️ NOT_VERIFIED | 0 | 0.0% |

## By Claim Type

| Claim Type | Total | SIGNED_OFF | BLOCKED | NOT_VERIFIED |
|---|---:|---:|---:|---:|
| COMPONENT_RUNTIME | 8 | 8 | 0 | 0 |
| COMPOSITION_RUNTIME | 2 | 2 | 0 | 0 |
| INTEGRATED_RUNTIME | 8 | 8 | 0 | 0 |
| NO_BYPASS_RUNTIME | 26 | 26 | 0 | 0 |
| OBSERVABILITY_RUNTIME | 5 | 5 | 0 | 0 |
| PRODUCTION_DEPENDENCY_RUNTIME | 5 | 5 | 0 | 0 |
| REPLAY_RUNTIME | 3 | 3 | 0 | 0 |
| STATIC_CONTRACT | 1 | 1 | 0 | 0 |
| STATIC_ENFORCEMENT | 29 | 29 | 0 | 0 |

## All Rows

| req_id | Status | Claim Type | Priority | Title |
|---|---|---|---|---|
| RTC-REQ-001 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Canonical requirement universe declared |
| RTC-REQ-002 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Proof depth fields mandatory |
| RTC-REQ-003 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Claim type enum enforced |
| RTC-REQ-004 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Acceptance legality rule |
| RTC-REQ-005 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Reference-only rows cannot claim runtime |
| RTC-REQ-006 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Subclaim decomposition mandatory |
| RTC-REQ-010 | ✅ SIGNED_OFF | INTEGRATED_RUNTIME | P0 | Integrated runtime entry point required |
| RTC-REQ-011 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Harness observes only |
| RTC-REQ-012 | ✅ SIGNED_OFF | INTEGRATED_RUNTIME | P0 | Exit required for completed runtime path |
| RTC-REQ-013 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Terminal cache route does not execute L2 |
| RTC-REQ-014 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Runtime artifact provenance fields required |
| RTC-REQ-015 | ✅ SIGNED_OFF | INTEGRATED_RUNTIME | P0 | Policy blueprint registry bound on runtime artifacts |
| RTC-REQ-020 | ✅ SIGNED_OFF | OBSERVABILITY_RUNTIME | P1 | Collector-backed OTEL required for observability claims |
| RTC-REQ-021 | ✅ SIGNED_OFF | OBSERVABILITY_RUNTIME | P1 | Parent scenario span required |
| RTC-REQ-022 | ✅ SIGNED_OFF | OBSERVABILITY_RUNTIME | P1 | Counter deltas prove metric emission |
| RTC-REQ-023 | ✅ SIGNED_OFF | REPLAY_RUNTIME | P1 | Replay pair required for replay claims |
| RTC-REQ-024 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P1 | Replay mutation negative required |
| RTC-REQ-030 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | All-requirements gate readiness |
| RTC-REQ-031 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Merkle root non-empty and complete |
| RTC-REQ-032 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Source divergence block |
| RTC-REQ-033 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Hardening minimum enforced |
| RTC-REQ-034 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Downgraded rows report required |
| RTC-REQ-040 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Semantic cache requirement decomposed |
| RTC-REQ-041 | ✅ SIGNED_OFF | COMPONENT_RUNTIME | P0 | Seed and live query surface forms differ |
| RTC-REQ-042 | ✅ SIGNED_OFF | COMPONENT_RUNTIME | P0 | L1 exact miss before L2 dense hit |
| RTC-REQ-043 | ✅ SIGNED_OFF | COMPONENT_RUNTIME | P0 | Live query vector compared to cached vector |
| RTC-REQ-044 | ✅ SIGNED_OFF | PRODUCTION_DEPENDENCY_RUNTIME | P0 | Approved embedding model proof |
| RTC-REQ-045 | ✅ SIGNED_OFF | PRODUCTION_DEPENDENCY_RUNTIME | P0 | Production threshold proof |
| RTC-REQ-046 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Threshold override recorded |
| RTC-REQ-047 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Tenant isolation negative |
| RTC-REQ-048 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Namespace isolation negative |
| RTC-REQ-049 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Policy compatibility negative |
| RTC-REQ-050 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Freshness expiration negative |
| RTC-REQ-051 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Missing embedding ref negative |
| RTC-REQ-052 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Unsafe reuse class negative |
| RTC-REQ-053 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Semantic distance miss negative |
| RTC-REQ-054 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Lexical-overlap different meaning negative |
| RTC-REQ-055 | ✅ SIGNED_OFF | COMPOSITION_RUNTIME | P0 | TerminalRetPacket and Exit proof for R1B |
| RTC-REQ-056 | ✅ SIGNED_OFF | INTEGRATED_RUNTIME | P0 | R1B integrated runtime proof |
| RTC-REQ-057 | ✅ SIGNED_OFF | OBSERVABILITY_RUNTIME | P0 | R1B real OTEL proof |
| RTC-REQ-058 | ✅ SIGNED_OFF | REPLAY_RUNTIME | P0 | R1B replay proof |
| RTC-REQ-059 | ✅ SIGNED_OFF | COMPOSITION_RUNTIME | P0 | Safe cache reuse via dense + LLM-judge veto composite proof |
| RTC-REQ-060 | ✅ SIGNED_OFF | COMPONENT_RUNTIME | P0 | R1A exact cache normalized request hash |
| RTC-REQ-061 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | R1A wrong tenant negative |
| RTC-REQ-062 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | R1A stale policy negative |
| RTC-REQ-063 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Cache fixture seeding labelled fixture-only |
| RTC-REQ-064 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Production cache mutation through UWG only |
| RTC-REQ-065 | ✅ SIGNED_OFF | COMPONENT_RUNTIME | P0 | Cache lineage required for factual answers |
| RTC-REQ-066 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Cache invalidation proof |
| RTC-REQ-067 | ✅ SIGNED_OFF | STATIC_CONTRACT | P0 | L4 cache state schema fields accounted |
| RTC-REQ-070 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P1 | No direct durable write from L2 |
| RTC-REQ-071 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P1 | No direct durable write from L6 |
| RTC-REQ-072 | ✅ SIGNED_OFF | INTEGRATED_RUNTIME | P1 | UWG write sequence complete |
| RTC-REQ-073 | ✅ SIGNED_OFF | COMPONENT_RUNTIME | P1 | L4 read-surface refresh after commit |
| RTC-REQ-080 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P1 | UNKNOWN is never PASS |
| RTC-REQ-081 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P1 | NOT_APPLICABLE requires reason |
| RTC-REQ-082 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P1 | Gate verdicts are not final X3 |
| RTC-REQ-083 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P1 | Negative controls must match expected fail reason |
| RTC-REQ-084 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P1 | No bypass mutation suite required |
| RTC-REQ-090 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P1 | U0 intake emits validated or rejected request only |
| RTC-REQ-091 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P1 | L1 plans but does not route/retrieve/execute |
| RTC-REQ-092 | ✅ SIGNED_OFF | COMPONENT_RUNTIME | P1 | L0 emits exactly one deterministic RouteContract |
| RTC-REQ-093 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P1 | C0 retrieves evidence only |
| RTC-REQ-094 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P1 | Prompt Assembly composes only |
| RTC-REQ-095 | ✅ SIGNED_OFF | COMPONENT_RUNTIME | P1 | L2 bounded execution and sealing only |
| RTC-REQ-096 | ✅ SIGNED_OFF | INTEGRATED_RUNTIME | P1 | Exit emits exactly one X3 and does not write L4 |
| RTC-REQ-097 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P1 | L6 completed-run learning only |
| RTC-REQ-100 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P1 | Semantic cache certification report required |
| RTC-REQ-101 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P1 | Runtime certification report required |
| RTC-REQ-102 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P1 | Certification language scoped by proof class |
| RTC-REQ-103 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P1 | Allowed partial language |
| RTC-REQ-110 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Matrix schema CI gate |
| RTC-REQ-111 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Acceptance legality CI gate |
| RTC-REQ-112 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Semantic cache CI gate |
| RTC-REQ-113 | ✅ SIGNED_OFF | OBSERVABILITY_RUNTIME | P0 | OTEL collector CI gate |
| RTC-REQ-114 | ✅ SIGNED_OFF | REPLAY_RUNTIME | P0 | Replay CI gate |
| RTC-REQ-115 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | No-bypass mutation CI gate |
| RTC-REQ-120 | ✅ SIGNED_OFF | INTEGRATED_RUNTIME | P1 | 100.0% runtime certification definition |
| RTC-REQ-121 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P1 | 100.0% static enforcement coverage separate from runtime certification |
| RTC-REQ-122 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P1 | No scoped blockers in final claim |
| RTC-REQ-123 | ✅ SIGNED_OFF | NO_BYPASS_RUNTIME | P0 | Artifact payload content-hash validation |
| RTC-REQ-124 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Single repo root and output directory binding |
| RTC-REQ-125 | ✅ SIGNED_OFF | PRODUCTION_DEPENDENCY_RUNTIME | P0 | Semantic cache production-threshold ADR gate |
| RTC-REQ-126 | ✅ SIGNED_OFF | PRODUCTION_DEPENDENCY_RUNTIME | P0 | Embedding fallback must be explicit fail-closed or mismatch-explained |
| RTC-REQ-127 | ✅ SIGNED_OFF | STATIC_ENFORCEMENT | P0 | Composition proof cannot promote final acceptance automatically |
| RTC-REQ-128 | ✅ SIGNED_OFF | INTEGRATED_RUNTIME | P1 | Gate verdict bundle consumed by Exit |
| RTC-REQ-129 | ✅ SIGNED_OFF | PRODUCTION_DEPENDENCY_RUNTIME | P1 | R1B score distribution calibration dataset |

## Per-Row Control Detail

<details><summary><b>RTC-REQ-001</b> — ✅ SIGNED_OFF — Canonical requirement universe declared</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `299bd5a62a8ad06e0655fe3851740fb3dc31aa1c9286d8dc450e7cf3b2892e12`
- row_evidence_sha256: `3166fe3853104c32f6971acda4df112408b1cb052c5bbb7051efcaf448c9cd87`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-cfab52fe3f0` | `artifacts/certification/positive_control_RTC-REQ-001.json` |
| verifier_exit_zero | ✓ |  | `ASRT-a850403b314` | `artifacts/certification/positive_control_RTC-REQ-001.json` |
| last_verified_timestamp | ✓ |  | `ASRT-73ad4474054` | `artifacts/certification/positive_control_RTC-REQ-001.json` |
| ci_gate | ✓ |  | `ASRT-7dfd5cc0d09` | `artifacts/certification/ci_gate_binding_report.json` |
| layer_boundary | ✓ |  | `ASRT-13f46ce77a2` | `artifacts/certification/layer_boundary_report_csv_gate.json` |

</details>

<details><summary><b>RTC-REQ-002</b> — ✅ SIGNED_OFF — Proof depth fields mandatory</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `e6a6c34a2f7ad9020b8df8bd4aadd0eb3c124fa2d6f78288c1f55ed278c6ef5e`
- row_evidence_sha256: `f64331b7d89c2ba14fe3db4e8210d04a63c7088cf3af644c955e0bcb1ff396f9`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-f03b3e1f2f1` | `artifacts/certification/positive_control_RTC-REQ-002.json` |
| verifier_exit_zero | ✓ |  | `ASRT-482e14bbd3a` | `artifacts/certification/positive_control_RTC-REQ-002.json` |
| last_verified_timestamp | ✓ |  | `ASRT-36216b81aac` | `artifacts/certification/positive_control_RTC-REQ-002.json` |
| ci_gate | ✓ |  | `ASRT-c4f9f8b27f6` | `artifacts/certification/ci_gate_binding_report.json` |
| layer_boundary | ✓ |  | `ASRT-f8d70120905` | `artifacts/certification/layer_boundary_report_csv_gate.json` |

</details>

<details><summary><b>RTC-REQ-003</b> — ✅ SIGNED_OFF — Claim type enum enforced</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `b084da9f7772be4848f65b0981b22bd3e559f8b3bbac5fc592e3b76ade824d00`
- row_evidence_sha256: `04356805f0a1ab5e6ef569914256fff411f34b861a8826537435172ae8c7d8f1`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-792f2b74696` | `artifacts/certification/positive_control_RTC-REQ-003.json` |
| verifier_exit_zero | ✓ |  | `ASRT-6f28f023254` | `artifacts/certification/positive_control_RTC-REQ-003.json` |
| last_verified_timestamp | ✓ |  | `ASRT-d6ae9717fc7` | `artifacts/certification/positive_control_RTC-REQ-003.json` |
| ci_gate | ✓ |  | `ASRT-12a749afc95` | `artifacts/certification/ci_gate_binding_report.json` |
| layer_boundary | ✓ |  | `ASRT-083bd036331` | `artifacts/certification/layer_boundary_report_csv_gate.json` |

</details>

<details><summary><b>RTC-REQ-004</b> — ✅ SIGNED_OFF — Acceptance legality rule</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `1325b58964cec3d2dc3cf69618ca046d5b4d5b352257a232b0a19f3bfbd83bba`
- row_evidence_sha256: `4b07c1f4a3e9ea15a3459aa0cbda0e1687b0ca4610335d0eed985356d2927081`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-546f3f6410b` | `artifacts/certification/positive_control_RTC-REQ-004.json` |
| verifier_exit_zero | ✓ |  | `ASRT-6c2ff07fc08` | `artifacts/certification/positive_control_RTC-REQ-004.json` |
| last_verified_timestamp | ✓ |  | `ASRT-16ffd0d37bb` | `artifacts/certification/positive_control_RTC-REQ-004.json` |
| ci_gate | ✓ |  | `ASRT-68c576f8f9c` | `artifacts/certification/ci_gate_binding_report.json` |
| layer_boundary | ✓ |  | `ASRT-0d3bc3c38e9` | `artifacts/certification/layer_boundary_report_csv_gate.json` |

</details>

<details><summary><b>RTC-REQ-005</b> — ✅ SIGNED_OFF — Reference-only rows cannot claim runtime</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `d6c6594db97fc3f65d701e6fafb5217321dbbb977a567654f177b710fe4e7d85`
- row_evidence_sha256: `a873adc34312ce2f3a0c272d4b410accb9eb69522e8ab8959ff80f350aecebe6`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-4089d5394c4` | `artifacts/certification/positive_control_RTC-REQ-005.json` |
| verifier_exit_zero | ✓ |  | `ASRT-ea7efaacdbb` | `artifacts/certification/positive_control_RTC-REQ-005.json` |
| last_verified_timestamp | ✓ |  | `ASRT-24553a06737` | `artifacts/certification/positive_control_RTC-REQ-005.json` |
| ci_gate | ✓ |  | `ASRT-7d45253f9bd` | `artifacts/certification/ci_gate_binding_report.json` |
| layer_boundary | ✓ |  | `ASRT-38deedd17e1` | `artifacts/certification/layer_boundary_report_csv_gate.json` |

</details>

<details><summary><b>RTC-REQ-006</b> — ✅ SIGNED_OFF — Subclaim decomposition mandatory</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `2bccae7ee33e5df7203fcbfcffeed063519acc640ca3bf5bb0bf09cbaed964af`
- row_evidence_sha256: `ea66b22841fb4a68471d49a7e3d5fab18ae145cfc8fb46da692881a4ca34a4d6`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-7fdba9571d2` | `artifacts/certification/positive_control_RTC-REQ-006.json` |
| verifier_exit_zero | ✓ |  | `ASRT-794ecb44daf` | `artifacts/certification/positive_control_RTC-REQ-006.json` |
| last_verified_timestamp | ✓ |  | `ASRT-5ef749c8ac7` | `artifacts/certification/positive_control_RTC-REQ-006.json` |
| ci_gate | ✓ |  | `ASRT-b69bf890ada` | `artifacts/certification/ci_gate_binding_report.json` |
| layer_boundary | ✓ |  | `ASRT-ea5ee7ded11` | `artifacts/certification/layer_boundary_report_csv_gate.json` |

</details>

<details><summary><b>RTC-REQ-010</b> — ✅ SIGNED_OFF — Integrated runtime entry point required</summary>

- claim_type: `INTEGRATED_RUNTIME`
- row_digest: `b49bfaef271a99ba6349ed5e3316419c33973d85d5eb6c8b38388665882b6885`
- row_evidence_sha256: `4ba43391fcb4383c7657200e14e59203ca0fa4eca8c8757900a40e57c64e4711`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-d6c37941daf` | `artifacts/certification/runtime/RTC-REQ-010/apps_rg_runtime_entrypoint_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-dd4ef300806` | `artifacts/certification/runtime/RTC-REQ-010/apps_rg_runtime_entrypoint_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-52ce0ba5674` | `artifacts/certification/runtime/RTC-REQ-010/apps_rg_runtime_entrypoint_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-9b0b8c98e06` | `artifacts/certification/runtime/RTC-REQ-010/apps_rg_runtime_entrypoint_evidence.json` |
| otel_trace | ✓ |  | `ASRT-86fcc243900` | `artifacts/certification/runtime/RTC-REQ-010/apps_rg_runtime_entrypoint_evidence.json` |
| source_root_binding | ✓ |  | `ASRT-9474d3cb26d` | `artifacts/certification/runtime/RTC-REQ-010/apps_rg_runtime_entrypoint_evidence.json` |
| artifact_payload_hash | ✓ |  | `ASRT-5fc7f02fba2` | `artifacts/certification/runtime/RTC-REQ-010/apps_rg_runtime_entrypoint_evidence.json` |

</details>

<details><summary><b>RTC-REQ-011</b> — ✅ SIGNED_OFF — Harness observes only</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `529b14c4b89b8c8d37fb8e163efa9a83282f17671e52de110f9dc1d1e9c02a5e`
- row_evidence_sha256: `972b4ca263fefb76ff539be0d2fe59c310fa41ee510a7d5e145c2ed2dd89b0c2`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-971899189af` | `artifacts/certification/runtime/RTC-REQ-011/apps_rg_runtime_no_bypass_011_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-bb85c2b75ab` | `artifacts/certification/runtime/RTC-REQ-011/apps_rg_runtime_no_bypass_011_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-7d5c58ed012` | `artifacts/certification/runtime/RTC-REQ-011/apps_rg_runtime_no_bypass_011_evidence.json` |
| no_bypass | ✓ |  | `ASRT-58ebc037134` | `artifacts/certification/runtime/RTC-REQ-011/apps_rg_runtime_no_bypass_011_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-86a6e0c71b7` | `artifacts/certification/runtime/RTC-REQ-011/apps_rg_runtime_no_bypass_011_evidence.json` |

</details>

<details><summary><b>RTC-REQ-012</b> — ✅ SIGNED_OFF — Exit required for completed runtime path</summary>

- claim_type: `INTEGRATED_RUNTIME`
- row_digest: `03bee212988443b2ba07e244a84b6ead40df0f8ff192ef1130820a9d7d804936`
- row_evidence_sha256: `3aeeb740243b039423b1435d37c11cf13cad5b3978ee6f56e3479c219c867867`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-2cd3d2385dc` | `artifacts/certification/runtime/RTC-REQ-012/apps_rg_runtime_entrypoint_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-96ba8e8c320` | `artifacts/certification/runtime/RTC-REQ-012/apps_rg_runtime_entrypoint_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-b7d6ef03f9b` | `artifacts/certification/runtime/RTC-REQ-012/apps_rg_runtime_entrypoint_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-24df36bf27e` | `artifacts/certification/runtime/RTC-REQ-012/apps_rg_runtime_entrypoint_evidence.json` |
| otel_trace | ✓ |  | `ASRT-0db5bbf2ea1` | `artifacts/certification/runtime/RTC-REQ-012/apps_rg_runtime_entrypoint_evidence.json` |
| source_root_binding | ✓ |  | `ASRT-b884d42bac5` | `artifacts/certification/runtime/RTC-REQ-012/apps_rg_runtime_entrypoint_evidence.json` |
| artifact_payload_hash | ✓ |  | `ASRT-2e9feb9e2bf` | `artifacts/certification/runtime/RTC-REQ-012/apps_rg_runtime_entrypoint_evidence.json` |

</details>

<details><summary><b>RTC-REQ-013</b> — ✅ SIGNED_OFF — Terminal cache route does not execute L2</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `99c8401d4dfe4238a535a150e680bbecd24cc1a571c508fc29810102e06f5dd5`
- row_evidence_sha256: `89cb008b0b5a0989c66aa4a65f08052028854db579948895fd1fbcc6846c4e05`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-5b46b93af2b` | `artifacts/certification/runtime/RTC-REQ-013/apps_rg_runtime_no_bypass_013_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-f358dccd070` | `artifacts/certification/runtime/RTC-REQ-013/apps_rg_runtime_no_bypass_013_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-62eca5afa87` | `artifacts/certification/runtime/RTC-REQ-013/apps_rg_runtime_no_bypass_013_evidence.json` |
| no_bypass | ✓ |  | `ASRT-397aa451b71` | `artifacts/certification/runtime/RTC-REQ-013/apps_rg_runtime_no_bypass_013_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-c6538e46f91` | `artifacts/certification/runtime/RTC-REQ-013/apps_rg_runtime_no_bypass_013_evidence.json` |

</details>

<details><summary><b>RTC-REQ-014</b> — ✅ SIGNED_OFF — Runtime artifact provenance fields required</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `b6ee5df309ec758b261cf89d2453cca9ebc4369da228aa06f28bf0aecb757285`
- row_evidence_sha256: `78f47b618e520c4cb12b0475667c12431ed74dfba2f6816679ab78d584dcfd49`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-dd221402d5e` | `artifacts/certification/runtime/RTC-REQ-014/apps_rg_runtime_provenance_014_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-99475ceb655` | `artifacts/certification/runtime/RTC-REQ-014/apps_rg_runtime_provenance_014_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-d49d0adc19c` | `artifacts/certification/runtime/RTC-REQ-014/apps_rg_runtime_provenance_014_evidence.json` |
| ci_gate | ✓ |  | `ASRT-351e0f7cb0b` | `artifacts/certification/runtime/RTC-REQ-014/apps_rg_runtime_provenance_014_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-886f5d334b9` | `artifacts/certification/runtime/RTC-REQ-014/apps_rg_runtime_provenance_014_evidence.json` |

</details>

<details><summary><b>RTC-REQ-015</b> — ✅ SIGNED_OFF — Policy blueprint registry bound on runtime artifacts</summary>

- claim_type: `INTEGRATED_RUNTIME`
- row_digest: `80ea40117e07457ba510ef87fca7bb4ee593bde0c5d2b6e9a7ae6328e61057fe`
- row_evidence_sha256: `c9f84df2fe724f3fd5cce82c8661f8aa1fc8aa8151ef9e98ac0f1f2de97f4d0e`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-e42e828a578` | `artifacts/certification/runtime/RTC-REQ-015/apps_rg_runtime_entrypoint_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-ca2f4f0d847` | `artifacts/certification/runtime/RTC-REQ-015/apps_rg_runtime_entrypoint_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-9ed702e3fdd` | `artifacts/certification/runtime/RTC-REQ-015/apps_rg_runtime_entrypoint_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-9027dcf4d6f` | `artifacts/certification/runtime/RTC-REQ-015/apps_rg_runtime_entrypoint_evidence.json` |
| otel_trace | ✓ |  | `ASRT-33ca02056ac` | `artifacts/certification/runtime/RTC-REQ-015/apps_rg_runtime_entrypoint_evidence.json` |
| source_root_binding | ✓ |  | `ASRT-db26287392c` | `artifacts/certification/runtime/RTC-REQ-015/apps_rg_runtime_entrypoint_evidence.json` |
| artifact_payload_hash | ✓ |  | `ASRT-a362e16957e` | `artifacts/certification/runtime/RTC-REQ-015/apps_rg_runtime_entrypoint_evidence.json` |

</details>

<details><summary><b>RTC-REQ-020</b> — ✅ SIGNED_OFF — Collector-backed OTEL required for observability claims</summary>

- claim_type: `OBSERVABILITY_RUNTIME`
- row_digest: `ae37c58730c04cf83bff5414a0a268528288abd03d9e93a23bc635660ba1874e`
- row_evidence_sha256: `e66699d18d6a1076d088c8612b37d01ce3adf7880531f365640d30770bde7283`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-ee597e3be40` | `artifacts/certification/runtime/RTC-REQ-020/apps_rg_runtime_observability_020_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-8eb20d34010` | `artifacts/certification/runtime/RTC-REQ-020/apps_rg_runtime_observability_020_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-27373b6fb09` | `artifacts/certification/runtime/RTC-REQ-020/apps_rg_runtime_observability_020_evidence.json` |
| otel_trace | ✓ |  | `ASRT-473ff052ae8` | `artifacts/certification/runtime/RTC-REQ-020/apps_rg_runtime_observability_020_evidence.json` |

</details>

<details><summary><b>RTC-REQ-021</b> — ✅ SIGNED_OFF — Parent scenario span required</summary>

- claim_type: `OBSERVABILITY_RUNTIME`
- row_digest: `da7c136b8741d98808681ccb01099814532c6c8a41b0a2390b816f9636d3e634`
- row_evidence_sha256: `6a69c3be8ab22dd524a9a62ece610010902d8e63650a6c7142faf75cee4b719c`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-11d8ad3fd40` | `artifacts/certification/runtime/RTC-REQ-021/apps_rg_runtime_observability_021_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-e01ae0be655` | `artifacts/certification/runtime/RTC-REQ-021/apps_rg_runtime_observability_021_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-0094b302fd7` | `artifacts/certification/runtime/RTC-REQ-021/apps_rg_runtime_observability_021_evidence.json` |
| otel_trace | ✓ |  | `ASRT-3b4707fd02b` | `artifacts/certification/runtime/RTC-REQ-021/apps_rg_runtime_observability_021_evidence.json` |

</details>

<details><summary><b>RTC-REQ-022</b> — ✅ SIGNED_OFF — Counter deltas prove metric emission</summary>

- claim_type: `OBSERVABILITY_RUNTIME`
- row_digest: `19aa28cdd4b55dc6205ebd5029038758d143913bf325d4635baec9374cbb7ceb`
- row_evidence_sha256: `5805686a2684fa11254fd984609aef7178c3dda4d832d2b01c0b926b7d5f8c61`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-2c6e068bf94` | `artifacts/certification/runtime/RTC-REQ-022/apps_rg_observability_022_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-2a6ea19e458` | `artifacts/certification/runtime/RTC-REQ-022/apps_rg_observability_022_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-5834be49b07` | `artifacts/certification/runtime/RTC-REQ-022/apps_rg_observability_022_evidence.json` |
| otel_trace | ✓ |  | `ASRT-ac68b115d6e` | `artifacts/certification/runtime/RTC-REQ-022/apps_rg_observability_022_evidence.json` |

</details>

<details><summary><b>RTC-REQ-023</b> — ✅ SIGNED_OFF — Replay pair required for replay claims</summary>

- claim_type: `REPLAY_RUNTIME`
- row_digest: `f960aa708294c1b53b3765ec3c3b7d8942af1642282dd24f00e21a0ae8d75519`
- row_evidence_sha256: `9158c3249c98f9224fd744080f347f57f7d38600669cd12292b2eb425429f460`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-8685c843c7f` | `artifacts/certification/runtime/RTC-REQ-023/apps_rg_runtime_replay_023_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-29f545b079d` | `artifacts/certification/runtime/RTC-REQ-023/apps_rg_runtime_replay_023_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-792472bd6b5` | `artifacts/certification/runtime/RTC-REQ-023/apps_rg_runtime_replay_023_evidence.json` |
| replay_receipt | ✓ |  | `ASRT-4531f3e64b5` | `artifacts/certification/runtime/RTC-REQ-023/apps_rg_runtime_replay_023_evidence.json` |

</details>

<details><summary><b>RTC-REQ-024</b> — ✅ SIGNED_OFF — Replay mutation negative required</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `c24c2ce8f4d9ebcc08e06e11fd0ad92f1f56439aecc0a63c5ffe8366a17cbacf`
- row_evidence_sha256: `a18c0d5aa284dbfff042e0575e9ae54ff9e66428c77c8de266c4a2cea16c9f9f`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-074b9d1d1c0` | `artifacts/certification/runtime/RTC-REQ-024/apps_rg_no_bypass_024_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-41027602e83` | `artifacts/certification/runtime/RTC-REQ-024/apps_rg_no_bypass_024_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-636d5b22d3e` | `artifacts/certification/runtime/RTC-REQ-024/apps_rg_no_bypass_024_evidence.json` |
| no_bypass | ✓ |  | `ASRT-1d346df65e4` | `artifacts/certification/runtime/RTC-REQ-024/apps_rg_no_bypass_024_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-e1354381289` | `artifacts/certification/runtime/RTC-REQ-024/apps_rg_no_bypass_024_evidence.json` |
| negative_controls | ✓ |  | `ASRT-e2716221cff` | `artifacts/certification/runtime/RTC-REQ-024/apps_rg_no_bypass_024_evidence.json` |
| expected_fail_reason | ✓ |  | `ASRT-920eada2d12` | `artifacts/certification/runtime/RTC-REQ-024/apps_rg_no_bypass_024_evidence.json` |

</details>

<details><summary><b>RTC-REQ-030</b> — ✅ SIGNED_OFF — All-requirements gate readiness</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `2cdf73eae800ea8a9bf178feecfe1f07ce73efba9bf74369ace80b622f7543ac`
- row_evidence_sha256: `e412a502613f3a89ca5e029fe2a660857ca39df21b56878b488dbe4130882d68`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-d7c6dcf5831` | `artifacts/certification/positive_control_RTC-REQ-030.json` |
| verifier_exit_zero | ✓ |  | `ASRT-ed2d34a33c0` | `artifacts/certification/positive_control_RTC-REQ-030.json` |
| last_verified_timestamp | ✓ |  | `ASRT-9b16410de10` | `artifacts/certification/positive_control_RTC-REQ-030.json` |
| ci_gate | ✓ |  | `ASRT-db0e8e2cc65` | `artifacts/certification/ci_gate_binding_report.json` |
| layer_boundary | ✓ |  | `ASRT-cf32b0a0241` | `artifacts/certification/layer_boundary_report_csv_gate.json` |

</details>

<details><summary><b>RTC-REQ-031</b> — ✅ SIGNED_OFF — Merkle root non-empty and complete</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `5fe21664f69e1a4b7f57169b0b49036800ac01305d69bd113af6a5397c033a36`
- row_evidence_sha256: `cffb70887a28eb80274267fb5d32658632e68f39cd6d84e928c501f387fcc65d`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-6f4b552041e` | `artifacts/certification/positive_control_RTC-REQ-031.json` |
| verifier_exit_zero | ✓ |  | `ASRT-eeafb129d3f` | `artifacts/certification/positive_control_RTC-REQ-031.json` |
| last_verified_timestamp | ✓ |  | `ASRT-0bfbf6f8cd3` | `artifacts/certification/positive_control_RTC-REQ-031.json` |
| ci_gate | ✓ |  | `ASRT-2ddf4222173` | `artifacts/certification/ci_gate_binding_report.json` |
| layer_boundary | ✓ |  | `ASRT-68b5b3a229f` | `artifacts/certification/layer_boundary_report_csv_gate.json` |
| merkle_leaf | ✓ |  | `ASRT-d68c269d908` | `artifacts/certification/rtc_req_csv_merkle_leaves.json` |

</details>

<details><summary><b>RTC-REQ-032</b> — ✅ SIGNED_OFF — Source divergence block</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `6b4b5090e9a4bc099a3c00be77ff5be3bdccba949b650f1b54ff87a869e60dc6`
- row_evidence_sha256: `a0546f1a91c6546e16dd22ca3b1fed88d3c576e05949d44799e3b25d9eff093d`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-fb6d841134e` | `artifacts/certification/runtime/RTC-REQ-032/apps_rg_no_bypass_032_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-89228f1c2a2` | `artifacts/certification/runtime/RTC-REQ-032/apps_rg_no_bypass_032_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-ad2157df2fa` | `artifacts/certification/runtime/RTC-REQ-032/apps_rg_no_bypass_032_evidence.json` |
| no_bypass | ✓ |  | `ASRT-98af84c0fec` | `artifacts/certification/runtime/RTC-REQ-032/apps_rg_no_bypass_032_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-aa41ee22dde` | `artifacts/certification/runtime/RTC-REQ-032/apps_rg_no_bypass_032_evidence.json` |

</details>

<details><summary><b>RTC-REQ-033</b> — ✅ SIGNED_OFF — Hardening minimum enforced</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `8dae355864c4919e3c71a7c73c124ddfb43a3dc72d788a9de5be01f9ad768978`
- row_evidence_sha256: `1aa70d9ec939b4fba6f1e7ba58a929b62ec790a7b5c8a792e02997433edea3ec`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-22327dbc330` | `artifacts/certification/runtime/RTC-REQ-033/apps_rg_no_bypass_033_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-7f70b240b11` | `artifacts/certification/runtime/RTC-REQ-033/apps_rg_no_bypass_033_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-4eb09752a4c` | `artifacts/certification/runtime/RTC-REQ-033/apps_rg_no_bypass_033_evidence.json` |
| no_bypass | ✓ |  | `ASRT-44e0ffd10d0` | `artifacts/certification/runtime/RTC-REQ-033/apps_rg_no_bypass_033_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-74ab722a0af` | `artifacts/certification/runtime/RTC-REQ-033/apps_rg_no_bypass_033_evidence.json` |

</details>

<details><summary><b>RTC-REQ-034</b> — ✅ SIGNED_OFF — Downgraded rows report required</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `f0e7445f2d13278b95e35aae60a7d42772e7997e4767e1818e3bcb7b2e84b3d1`
- row_evidence_sha256: `791363bb258204cbf763b0550d7360e38c7fe9379b0d145b22105a468f540481`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-7dfdc5cda0e` | `artifacts/certification/positive_control_RTC-REQ-034.json` |
| verifier_exit_zero | ✓ |  | `ASRT-17cc14946da` | `artifacts/certification/positive_control_RTC-REQ-034.json` |
| last_verified_timestamp | ✓ |  | `ASRT-15ed7e98f77` | `artifacts/certification/positive_control_RTC-REQ-034.json` |
| ci_gate | ✓ |  | `ASRT-3040849c298` | `artifacts/certification/ci_gate_binding_report_runtime_acceptance.json` |
| layer_boundary | ✓ |  | `ASRT-21a73319694` | `artifacts/certification/layer_boundary_report_runtime_acceptance.json` |

</details>

<details><summary><b>RTC-REQ-040</b> — ✅ SIGNED_OFF — Semantic cache requirement decomposed</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `cacb574323c53349654c2e5da8faa2eed1a7baa3699b30ea8f0f2487495517e1`
- row_evidence_sha256: `3c31f70e56a4077a877b1805838a2640c4cb2c02468901f2c7b4b61959fb1fc1`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-a8718008dea` | `artifacts/certification/runtime/RTC-REQ-040/apps_rg_static_enforcement_040_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-c701d1032d8` | `artifacts/certification/runtime/RTC-REQ-040/apps_rg_static_enforcement_040_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-82046561f1c` | `artifacts/certification/runtime/RTC-REQ-040/apps_rg_static_enforcement_040_evidence.json` |
| ci_gate | ✓ |  | `ASRT-5bcc62d18fe` | `artifacts/certification/runtime/RTC-REQ-040/apps_rg_static_enforcement_040_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-23bb2eaa932` | `artifacts/certification/runtime/RTC-REQ-040/apps_rg_static_enforcement_040_evidence.json` |

</details>

<details><summary><b>RTC-REQ-041</b> — ✅ SIGNED_OFF — Seed and live query surface forms differ</summary>

- claim_type: `COMPONENT_RUNTIME`
- row_digest: `3dc19668fda60394492b5eccabbf0a3c7258897b41479c2fa7fcb576ea374525`
- row_evidence_sha256: `0b339ec18f181fbc8ff6c06abcee4a25426b750907a7bb7881c5a32ce2f646e2`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-285c1ef2327` | `artifacts/certification/runtime/RTC-REQ-041/apps_rg_component_runtime_041_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-6d6e179294a` | `artifacts/certification/runtime/RTC-REQ-041/apps_rg_component_runtime_041_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-254e2816d0e` | `artifacts/certification/runtime/RTC-REQ-041/apps_rg_component_runtime_041_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-d42f780932e` | `artifacts/certification/runtime/RTC-REQ-041/apps_rg_component_runtime_041_evidence.json` |
| evidence_manifest_hash | ✓ |  | `ASRT-2a792aaf8fa` | `artifacts/certification/runtime/RTC-REQ-041/apps_rg_component_runtime_041_evidence.json` |

</details>

<details><summary><b>RTC-REQ-042</b> — ✅ SIGNED_OFF — L1 exact miss before L2 dense hit</summary>

- claim_type: `COMPONENT_RUNTIME`
- row_digest: `baf64ef619d0ebac27548455ae987c39beab4d10c50d07baa2aa48a958bb64b4`
- row_evidence_sha256: `c132b6ee8fd844b4b92a0fc5746ea46920957bfb86a609c020afd63984e75b6f`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-587fe70a320` | `artifacts/certification/runtime/RTC-REQ-042/apps_rg_component_runtime_042_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-7c7b42e48c7` | `artifacts/certification/runtime/RTC-REQ-042/apps_rg_component_runtime_042_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-b830534ce87` | `artifacts/certification/runtime/RTC-REQ-042/apps_rg_component_runtime_042_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-41d6d20374a` | `artifacts/certification/runtime/RTC-REQ-042/apps_rg_component_runtime_042_evidence.json` |
| evidence_manifest_hash | ✓ |  | `ASRT-738b8d388d9` | `artifacts/certification/runtime/RTC-REQ-042/apps_rg_component_runtime_042_evidence.json` |

</details>

<details><summary><b>RTC-REQ-043</b> — ✅ SIGNED_OFF — Live query vector compared to cached vector</summary>

- claim_type: `COMPONENT_RUNTIME`
- row_digest: `d9e1ea4520ab0360d5fa79562e55c94edfcde301d73c178975ce92e9c5e1bd68`
- row_evidence_sha256: `d8399b131cc0bd8010c237526d9ced2eef31ddd09a0c542449b70eb7c567c470`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-b848ed4edc9` | `artifacts/certification/runtime/RTC-REQ-043/apps_rg_component_runtime_043_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-d7f5fb3d0a7` | `artifacts/certification/runtime/RTC-REQ-043/apps_rg_component_runtime_043_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-fdb5ce106c7` | `artifacts/certification/runtime/RTC-REQ-043/apps_rg_component_runtime_043_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-fb133283be6` | `artifacts/certification/runtime/RTC-REQ-043/apps_rg_component_runtime_043_evidence.json` |
| evidence_manifest_hash | ✓ |  | `ASRT-a5a99cbcbfe` | `artifacts/certification/runtime/RTC-REQ-043/apps_rg_component_runtime_043_evidence.json` |

</details>

<details><summary><b>RTC-REQ-044</b> — ✅ SIGNED_OFF — Approved embedding model proof</summary>

- claim_type: `PRODUCTION_DEPENDENCY_RUNTIME`
- row_digest: `430dd9821ce6ee081bfcb7a91beec6a0bbc30392245f0b969a4c212e5712249d`
- row_evidence_sha256: `3abd69f47e5251b8d22469250ca935eeeacc9bfc544d3f552783a50d6ceb8d1f`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-3eb27b12f8f` | `artifacts/certification/runtime/RTC-REQ-044/apps_rg_production_dep_044_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-5bb112b17ab` | `artifacts/certification/runtime/RTC-REQ-044/apps_rg_production_dep_044_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-6201a7e82ca` | `artifacts/certification/runtime/RTC-REQ-044/apps_rg_production_dep_044_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-c1bbba478d9` | `artifacts/certification/runtime/RTC-REQ-044/apps_rg_production_dep_044_evidence.json` |
| certifier_signature | ✓ |  | `ASRT-7e06e5ec677` | `artifacts/certification/runtime/RTC-REQ-044/apps_rg_production_dep_044_evidence.json` |

</details>

<details><summary><b>RTC-REQ-045</b> — ✅ SIGNED_OFF — Production threshold proof</summary>

- claim_type: `PRODUCTION_DEPENDENCY_RUNTIME`
- row_digest: `b67070cd50a134467d4f255ba293f37939230a0ea41402046e8e2c1ebaa5cbb4`
- row_evidence_sha256: `8c0130d9cf9f6de86c1e7d5e002472d16d8cbd3b21549d276c3ce12572d62a2f`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-df8b0401422` | `artifacts/certification/runtime/RTC-REQ-045/apps_rg_production_dep_045_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-013912c4f0d` | `artifacts/certification/runtime/RTC-REQ-045/apps_rg_production_dep_045_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-23061064770` | `artifacts/certification/runtime/RTC-REQ-045/apps_rg_production_dep_045_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-4c486543e02` | `artifacts/certification/runtime/RTC-REQ-045/apps_rg_production_dep_045_evidence.json` |
| certifier_signature | ✓ |  | `ASRT-6f0ea36e557` | `artifacts/certification/runtime/RTC-REQ-045/apps_rg_production_dep_045_evidence.json` |

</details>

<details><summary><b>RTC-REQ-046</b> — ✅ SIGNED_OFF — Threshold override recorded</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `115416b60c9ffe9db338eadc17b0dab4d6bb2a84a0a6c5c2b68055ae0a8f3c05`
- row_evidence_sha256: `190a27e6d4fb6c0e35c73b7fc5578e00ddafbe5182955926b83fa70d624342b8`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-b71c9397913` | `artifacts/certification/runtime/RTC-REQ-046/apps_rg_static_enforcement_046_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-8f61855af69` | `artifacts/certification/runtime/RTC-REQ-046/apps_rg_static_enforcement_046_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-58c6b56d21c` | `artifacts/certification/runtime/RTC-REQ-046/apps_rg_static_enforcement_046_evidence.json` |
| ci_gate | ✓ |  | `ASRT-6dcac79b99f` | `artifacts/certification/runtime/RTC-REQ-046/apps_rg_static_enforcement_046_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-71914a11f23` | `artifacts/certification/runtime/RTC-REQ-046/apps_rg_static_enforcement_046_evidence.json` |

</details>

<details><summary><b>RTC-REQ-047</b> — ✅ SIGNED_OFF — Tenant isolation negative</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `68864d026a101d2ecac4cf15be0af7eca62bc2372f6aff327426ae162bd6a926`
- row_evidence_sha256: `a04f2cca06c232b05cbf03b13b65cba22fbbd4fbe130e18b43e2d3eb1fb75971`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-1d7ec2fd47d` | `artifacts/certification/runtime/RTC-REQ-047/apps_rg_no_bypass_047_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-2babeb71848` | `artifacts/certification/runtime/RTC-REQ-047/apps_rg_no_bypass_047_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-1c6379a427c` | `artifacts/certification/runtime/RTC-REQ-047/apps_rg_no_bypass_047_evidence.json` |
| no_bypass | ✓ |  | `ASRT-4890590a084` | `artifacts/certification/runtime/RTC-REQ-047/apps_rg_no_bypass_047_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-c50b59221ec` | `artifacts/certification/runtime/RTC-REQ-047/apps_rg_no_bypass_047_evidence.json` |
| negative_controls | ✓ |  | `ASRT-c288e75d5eb` | `artifacts/certification/runtime/RTC-REQ-047/apps_rg_no_bypass_047_evidence.json` |
| expected_fail_reason | ✓ |  | `ASRT-9eeebd9ec7f` | `artifacts/certification/runtime/RTC-REQ-047/apps_rg_no_bypass_047_evidence.json` |

</details>

<details><summary><b>RTC-REQ-048</b> — ✅ SIGNED_OFF — Namespace isolation negative</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `013c85de97baa5d2f735ac7abfbfba3eb09eb52aa531e36df8951fcb868081e9`
- row_evidence_sha256: `2ee0cb4e66e35c5c5c2c517b9ac79066f593e5a68d5bd5a08aff3da48fd93164`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-a0dcfd40164` | `artifacts/certification/runtime/RTC-REQ-048/apps_rg_no_bypass_048_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-5627781a891` | `artifacts/certification/runtime/RTC-REQ-048/apps_rg_no_bypass_048_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-e9b7abb48ba` | `artifacts/certification/runtime/RTC-REQ-048/apps_rg_no_bypass_048_evidence.json` |
| no_bypass | ✓ |  | `ASRT-df893abd633` | `artifacts/certification/runtime/RTC-REQ-048/apps_rg_no_bypass_048_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-42f6d5aea13` | `artifacts/certification/runtime/RTC-REQ-048/apps_rg_no_bypass_048_evidence.json` |
| negative_controls | ✓ |  | `ASRT-0efca828c34` | `artifacts/certification/runtime/RTC-REQ-048/apps_rg_no_bypass_048_evidence.json` |
| expected_fail_reason | ✓ |  | `ASRT-d177469722b` | `artifacts/certification/runtime/RTC-REQ-048/apps_rg_no_bypass_048_evidence.json` |

</details>

<details><summary><b>RTC-REQ-049</b> — ✅ SIGNED_OFF — Policy compatibility negative</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `f00f605177d3f295462182bb8b504a0544641432169d125d301a78f017609793`
- row_evidence_sha256: `30e7b65b8bc08c3e117358c7b787942df6450f9aa4547da8acb24bbf0bc7cd79`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-c7ba2522466` | `artifacts/certification/runtime/RTC-REQ-049/apps_rg_no_bypass_049_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-02ce27e5849` | `artifacts/certification/runtime/RTC-REQ-049/apps_rg_no_bypass_049_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-bae381cd8e5` | `artifacts/certification/runtime/RTC-REQ-049/apps_rg_no_bypass_049_evidence.json` |
| no_bypass | ✓ |  | `ASRT-f9902744b15` | `artifacts/certification/runtime/RTC-REQ-049/apps_rg_no_bypass_049_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-3613e1ac8b6` | `artifacts/certification/runtime/RTC-REQ-049/apps_rg_no_bypass_049_evidence.json` |
| negative_controls | ✓ |  | `ASRT-62b94df9e85` | `artifacts/certification/runtime/RTC-REQ-049/apps_rg_no_bypass_049_evidence.json` |
| expected_fail_reason | ✓ |  | `ASRT-a0e59c52c81` | `artifacts/certification/runtime/RTC-REQ-049/apps_rg_no_bypass_049_evidence.json` |

</details>

<details><summary><b>RTC-REQ-050</b> — ✅ SIGNED_OFF — Freshness expiration negative</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `e342ddb1ddc204141b67bdca0da9a32b2e847e5f8ed63051d78420d156fdd56c`
- row_evidence_sha256: `be8f1a65f8984c2052a712d8ecc7c1cdaf5bf4d6fc4e5feaba3eed913e2a6672`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-9754271e18f` | `artifacts/certification/runtime/RTC-REQ-050/apps_rg_no_bypass_050_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-d1eff890a58` | `artifacts/certification/runtime/RTC-REQ-050/apps_rg_no_bypass_050_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-5c7fe9b0898` | `artifacts/certification/runtime/RTC-REQ-050/apps_rg_no_bypass_050_evidence.json` |
| no_bypass | ✓ |  | `ASRT-2fa009e5ae7` | `artifacts/certification/runtime/RTC-REQ-050/apps_rg_no_bypass_050_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-06dca96f24c` | `artifacts/certification/runtime/RTC-REQ-050/apps_rg_no_bypass_050_evidence.json` |
| negative_controls | ✓ |  | `ASRT-a543481fa8f` | `artifacts/certification/runtime/RTC-REQ-050/apps_rg_no_bypass_050_evidence.json` |
| expected_fail_reason | ✓ |  | `ASRT-61ea8431198` | `artifacts/certification/runtime/RTC-REQ-050/apps_rg_no_bypass_050_evidence.json` |

</details>

<details><summary><b>RTC-REQ-051</b> — ✅ SIGNED_OFF — Missing embedding ref negative</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `67b0bb428a0198ba31530dae76ab048280571740bd3d6461c49652254e3920e0`
- row_evidence_sha256: `5ccac5d4011c6f9590aac424c2982daac16a71d25d7b282afd0a6508846f3af7`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-7439c4554f5` | `artifacts/certification/runtime/RTC-REQ-051/apps_rg_no_bypass_051_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-a29015702f6` | `artifacts/certification/runtime/RTC-REQ-051/apps_rg_no_bypass_051_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-87d6c0a5f98` | `artifacts/certification/runtime/RTC-REQ-051/apps_rg_no_bypass_051_evidence.json` |
| no_bypass | ✓ |  | `ASRT-6add8589d6d` | `artifacts/certification/runtime/RTC-REQ-051/apps_rg_no_bypass_051_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-6d047a470c5` | `artifacts/certification/runtime/RTC-REQ-051/apps_rg_no_bypass_051_evidence.json` |
| negative_controls | ✓ |  | `ASRT-ddc46f9b303` | `artifacts/certification/runtime/RTC-REQ-051/apps_rg_no_bypass_051_evidence.json` |
| expected_fail_reason | ✓ |  | `ASRT-93c636f6758` | `artifacts/certification/runtime/RTC-REQ-051/apps_rg_no_bypass_051_evidence.json` |

</details>

<details><summary><b>RTC-REQ-052</b> — ✅ SIGNED_OFF — Unsafe reuse class negative</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `2b62b0c46197db7c4443730f23d5bb6e462aff00046bc97486c788e9d6a33adc`
- row_evidence_sha256: `8489b321d01241d059e0db0c6997e6b472540e90943eaaf3d65d86023ff0ff0c`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-f523b5fced4` | `artifacts/certification/runtime/RTC-REQ-052/apps_rg_no_bypass_052_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-f06154ca65f` | `artifacts/certification/runtime/RTC-REQ-052/apps_rg_no_bypass_052_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-b78b05610b2` | `artifacts/certification/runtime/RTC-REQ-052/apps_rg_no_bypass_052_evidence.json` |
| no_bypass | ✓ |  | `ASRT-5d14138e3b6` | `artifacts/certification/runtime/RTC-REQ-052/apps_rg_no_bypass_052_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-84ce842f2a8` | `artifacts/certification/runtime/RTC-REQ-052/apps_rg_no_bypass_052_evidence.json` |
| negative_controls | ✓ |  | `ASRT-543cb5fcd6d` | `artifacts/certification/runtime/RTC-REQ-052/apps_rg_no_bypass_052_evidence.json` |
| expected_fail_reason | ✓ |  | `ASRT-ed40a6622f9` | `artifacts/certification/runtime/RTC-REQ-052/apps_rg_no_bypass_052_evidence.json` |

</details>

<details><summary><b>RTC-REQ-053</b> — ✅ SIGNED_OFF — Semantic distance miss negative</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `60a54268c924b19a00fe3c61325c495c8a06be48b789dccfde16186da8dc7f59`
- row_evidence_sha256: `e4355b934a8c6a7b340ca23b4ae84a935dd45aab5a8169c0d3d993c3cd51f840`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-c2c2689bca9` | `artifacts/certification/runtime/RTC-REQ-053/apps_rg_no_bypass_053_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-ceda9a5cddf` | `artifacts/certification/runtime/RTC-REQ-053/apps_rg_no_bypass_053_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-4caa88779db` | `artifacts/certification/runtime/RTC-REQ-053/apps_rg_no_bypass_053_evidence.json` |
| no_bypass | ✓ |  | `ASRT-fb95fb125c1` | `artifacts/certification/runtime/RTC-REQ-053/apps_rg_no_bypass_053_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-e22bcf48fe7` | `artifacts/certification/runtime/RTC-REQ-053/apps_rg_no_bypass_053_evidence.json` |
| negative_controls | ✓ |  | `ASRT-51af92a6dd9` | `artifacts/certification/runtime/RTC-REQ-053/apps_rg_no_bypass_053_evidence.json` |
| expected_fail_reason | ✓ |  | `ASRT-ac91c29b7dd` | `artifacts/certification/runtime/RTC-REQ-053/apps_rg_no_bypass_053_evidence.json` |

</details>

<details><summary><b>RTC-REQ-054</b> — ✅ SIGNED_OFF — Lexical-overlap different meaning negative</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `bfe26313cc9dbce0b1803133638f7c891c7a2a094d5e50c373b23ed749bc87dc`
- row_evidence_sha256: `7ba44e23b4350962962910ff925a48e4887f0124f1e40b88f2d8f65daabb97b2`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-607de47c0ab` | `artifacts/certification/runtime/RTC-REQ-054/apps_rg_no_bypass_054_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-eb0ca08220e` | `artifacts/certification/runtime/RTC-REQ-054/apps_rg_no_bypass_054_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-8c60c31ebf8` | `artifacts/certification/runtime/RTC-REQ-054/apps_rg_no_bypass_054_evidence.json` |
| no_bypass | ✓ |  | `ASRT-d115757a369` | `artifacts/certification/runtime/RTC-REQ-054/apps_rg_no_bypass_054_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-8c72a1da416` | `artifacts/certification/runtime/RTC-REQ-054/apps_rg_no_bypass_054_evidence.json` |
| negative_controls | ✓ |  | `ASRT-12c42204648` | `artifacts/certification/runtime/RTC-REQ-054/apps_rg_no_bypass_054_evidence.json` |
| expected_fail_reason | ✓ |  | `ASRT-2f268818abf` | `artifacts/certification/runtime/RTC-REQ-054/apps_rg_no_bypass_054_evidence.json` |

</details>

<details><summary><b>RTC-REQ-055</b> — ✅ SIGNED_OFF — TerminalRetPacket and Exit proof for R1B</summary>

- claim_type: `COMPOSITION_RUNTIME`
- row_digest: `b64266711fd8b1216428c18e7bbc3f63ef532c0e27d7ca2b8b1654edcb1a691e`
- row_evidence_sha256: `5dfe53d11c3f05c0ee8b5446fb5093610a661beb90a6f0a94a007c595bfc6d68`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-eee0d3f3029` | `artifacts/certification/runtime/RTC-REQ-055/apps_rg_runtime_composition_055_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-5a0a948a951` | `artifacts/certification/runtime/RTC-REQ-055/apps_rg_runtime_composition_055_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-46b8d6614ac` | `artifacts/certification/runtime/RTC-REQ-055/apps_rg_runtime_composition_055_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-c44cc3d3837` | `artifacts/certification/runtime/RTC-REQ-055/apps_rg_runtime_composition_055_evidence.json` |
| positive_evidence | ✓ |  | `ASRT-7ac51aea2ab` | `artifacts/certification/runtime/RTC-REQ-055/apps_rg_runtime_composition_055_evidence.json` |

</details>

<details><summary><b>RTC-REQ-056</b> — ✅ SIGNED_OFF — R1B integrated runtime proof</summary>

- claim_type: `INTEGRATED_RUNTIME`
- row_digest: `b35eab842d4d9e92135de046222d8ec6cbd33ae4d378dc9e5914e3895f10306b`
- row_evidence_sha256: `421344f851f80f43b58cc7d3867e7c5d64303e470c0c1fa1c5c41e050a24f974`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-69c60fdb061` | `artifacts/certification/runtime/RTC-REQ-056/apps_rg_runtime_evidence_chain_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-3f22f316f3a` | `artifacts/certification/runtime/RTC-REQ-056/apps_rg_runtime_evidence_chain_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-4f800b3ff0b` | `artifacts/certification/runtime/RTC-REQ-056/apps_rg_runtime_evidence_chain_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-394a07142fd` | `artifacts/certification/runtime/RTC-REQ-056/apps_rg_runtime_evidence_chain_evidence.json` |
| otel_trace | ✓ |  | `ASRT-203dc31409f` | `artifacts/certification/runtime/RTC-REQ-056/apps_rg_runtime_evidence_chain_evidence.json` |
| source_root_binding | ✓ |  | `ASRT-83a399c4405` | `artifacts/certification/runtime/RTC-REQ-056/apps_rg_runtime_evidence_chain_evidence.json` |
| artifact_payload_hash | ✓ |  | `ASRT-17c25ae913d` | `artifacts/certification/runtime/RTC-REQ-056/apps_rg_runtime_evidence_chain_evidence.json` |

</details>

<details><summary><b>RTC-REQ-057</b> — ✅ SIGNED_OFF — R1B real OTEL proof</summary>

- claim_type: `OBSERVABILITY_RUNTIME`
- row_digest: `b85266bfe09a1a819a8910c27593b85190a8f881ac84f44f01df77694e0ee472`
- row_evidence_sha256: `d68292a15d435083980ff97ddf20eb3c600cb5308d9afa0e981966cf041140e6`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-2efe38fd301` | `artifacts/certification/runtime/RTC-REQ-057/apps_rg_observability_057_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-84c952ede8a` | `artifacts/certification/runtime/RTC-REQ-057/apps_rg_observability_057_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-00f3ffaf172` | `artifacts/certification/runtime/RTC-REQ-057/apps_rg_observability_057_evidence.json` |
| otel_trace | ✓ |  | `ASRT-8862107761a` | `artifacts/certification/runtime/RTC-REQ-057/apps_rg_observability_057_evidence.json` |

</details>

<details><summary><b>RTC-REQ-058</b> — ✅ SIGNED_OFF — R1B replay proof</summary>

- claim_type: `REPLAY_RUNTIME`
- row_digest: `ca9941482bb35194aca01249999f2659d3eb114331f51dd942726cc70d1355c3`
- row_evidence_sha256: `3a37d0f01881e2df900e2b3971524d76558fc5b7c9b5e469067f94810a530136`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-e6681443954` | `artifacts/certification/runtime/RTC-REQ-058/apps_rg_runtime_replay_058_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-1a0ccb19e95` | `artifacts/certification/runtime/RTC-REQ-058/apps_rg_runtime_replay_058_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-38ac41b5f4e` | `artifacts/certification/runtime/RTC-REQ-058/apps_rg_runtime_replay_058_evidence.json` |
| replay_receipt | ✓ |  | `ASRT-75ba7907dfb` | `artifacts/certification/runtime/RTC-REQ-058/apps_rg_runtime_replay_058_evidence.json` |

</details>

<details><summary><b>RTC-REQ-059</b> — ✅ SIGNED_OFF — Safe cache reuse via dense + LLM-judge veto composite proof</summary>

- claim_type: `COMPOSITION_RUNTIME`
- row_digest: `81c05d765016d1017b55c1d597eb0e375f33e5a35f1ac2f82b8accf684c55549`
- row_evidence_sha256: `1fb50f9e98d933c52711253c0d887451428f1e1c82829ba3cab1c4d5334961aa`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-afa117e0b01` | `artifacts/certification/runtime/RTC-REQ-059/apps_rg_runtime_composition_059_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-65af97d9f3b` | `artifacts/certification/runtime/RTC-REQ-059/apps_rg_runtime_composition_059_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-37bd6572dd4` | `artifacts/certification/runtime/RTC-REQ-059/apps_rg_runtime_composition_059_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-acc524e250e` | `artifacts/certification/runtime/RTC-REQ-059/apps_rg_runtime_composition_059_evidence.json` |
| positive_evidence | ✓ |  | `ASRT-5587fa1a60f` | `artifacts/certification/runtime/RTC-REQ-059/apps_rg_runtime_composition_059_evidence.json` |

</details>

<details><summary><b>RTC-REQ-060</b> — ✅ SIGNED_OFF — R1A exact cache normalized request hash</summary>

- claim_type: `COMPONENT_RUNTIME`
- row_digest: `9010300cb97576e9b8108e906622ef7937a087affe150b0fcfa6ac2ab840f261`
- row_evidence_sha256: `7d2b8868a0b6fd70bcf26748d57e13f008a1ba5353644712e04f31d3f16a914c`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-413d230ee29` | `artifacts/certification/runtime/RTC-REQ-060/apps_rg_component_runtime_060_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-d118c2b694a` | `artifacts/certification/runtime/RTC-REQ-060/apps_rg_component_runtime_060_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-db1d892d5fa` | `artifacts/certification/runtime/RTC-REQ-060/apps_rg_component_runtime_060_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-1761ec4415b` | `artifacts/certification/runtime/RTC-REQ-060/apps_rg_component_runtime_060_evidence.json` |
| evidence_manifest_hash | ✓ |  | `ASRT-79f37682d34` | `artifacts/certification/runtime/RTC-REQ-060/apps_rg_component_runtime_060_evidence.json` |

</details>

<details><summary><b>RTC-REQ-061</b> — ✅ SIGNED_OFF — R1A wrong tenant negative</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `a582125bcc9dc6685aa269f9bf8d0f2bbaef1a0964308371ee34dd4fa9013621`
- row_evidence_sha256: `92d65efaf073c03544dc080c1781feac40756226bb6b5320baa7795efab78daf`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-d56d3dad121` | `artifacts/certification/runtime/RTC-REQ-061/apps_rg_no_bypass_061_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-d29c5bbe99c` | `artifacts/certification/runtime/RTC-REQ-061/apps_rg_no_bypass_061_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-bf736815c88` | `artifacts/certification/runtime/RTC-REQ-061/apps_rg_no_bypass_061_evidence.json` |
| no_bypass | ✓ |  | `ASRT-20611f86c0e` | `artifacts/certification/runtime/RTC-REQ-061/apps_rg_no_bypass_061_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-8a89d7adc72` | `artifacts/certification/runtime/RTC-REQ-061/apps_rg_no_bypass_061_evidence.json` |
| negative_controls | ✓ |  | `ASRT-932e9a397b6` | `artifacts/certification/runtime/RTC-REQ-061/apps_rg_no_bypass_061_evidence.json` |
| expected_fail_reason | ✓ |  | `ASRT-c1cf4245c6f` | `artifacts/certification/runtime/RTC-REQ-061/apps_rg_no_bypass_061_evidence.json` |

</details>

<details><summary><b>RTC-REQ-062</b> — ✅ SIGNED_OFF — R1A stale policy negative</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `e89ef53e076563cc8309c38e5a3b9fb60a464626968a69b34008527b715b67d6`
- row_evidence_sha256: `eeacce403a100f1419ecd56b65176fdfaa3e71ca3fa642cea63ad366db9565f2`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-219ff4020ff` | `artifacts/certification/runtime/RTC-REQ-062/apps_rg_no_bypass_062_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-af0f17ab67b` | `artifacts/certification/runtime/RTC-REQ-062/apps_rg_no_bypass_062_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-b0cf4ff1a6b` | `artifacts/certification/runtime/RTC-REQ-062/apps_rg_no_bypass_062_evidence.json` |
| no_bypass | ✓ |  | `ASRT-1f3dda8fe8d` | `artifacts/certification/runtime/RTC-REQ-062/apps_rg_no_bypass_062_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-d79598aa586` | `artifacts/certification/runtime/RTC-REQ-062/apps_rg_no_bypass_062_evidence.json` |
| negative_controls | ✓ |  | `ASRT-51125794438` | `artifacts/certification/runtime/RTC-REQ-062/apps_rg_no_bypass_062_evidence.json` |
| expected_fail_reason | ✓ |  | `ASRT-9871f807da6` | `artifacts/certification/runtime/RTC-REQ-062/apps_rg_no_bypass_062_evidence.json` |

</details>

<details><summary><b>RTC-REQ-063</b> — ✅ SIGNED_OFF — Cache fixture seeding labelled fixture-only</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `2c281e083756622b60866f5ed303b20655717e517ac631c5accfd2a017caeb17`
- row_evidence_sha256: `4276aa5cc2a60fbfbc955a521c32d65260a0b9dc7b9beee8586203cdf8a5f7b8`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-e66f189c11c` | `artifacts/certification/runtime/RTC-REQ-063/apps_rg_static_enforcement_063_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-25190106cca` | `artifacts/certification/runtime/RTC-REQ-063/apps_rg_static_enforcement_063_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-8a16191dd34` | `artifacts/certification/runtime/RTC-REQ-063/apps_rg_static_enforcement_063_evidence.json` |
| ci_gate | ✓ |  | `ASRT-e7b21c99abd` | `artifacts/certification/runtime/RTC-REQ-063/apps_rg_static_enforcement_063_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-d83bbbbdcf0` | `artifacts/certification/runtime/RTC-REQ-063/apps_rg_static_enforcement_063_evidence.json` |

</details>

<details><summary><b>RTC-REQ-064</b> — ✅ SIGNED_OFF — Production cache mutation through UWG only</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `bec3caeceabce6600275c1b881a2d132db4fe6ad0eefd867ebd2bd2cdf6bdd43`
- row_evidence_sha256: `672e7c889faa59f454f31faa42719b5fe5b7be9e4f0ba2a3b740d8862c410861`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-aff164670db` | `artifacts/certification/runtime/RTC-REQ-064/apps_rg_no_bypass_064_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-94a14a642de` | `artifacts/certification/runtime/RTC-REQ-064/apps_rg_no_bypass_064_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-96e2972a7c1` | `artifacts/certification/runtime/RTC-REQ-064/apps_rg_no_bypass_064_evidence.json` |
| no_bypass | ✓ |  | `ASRT-aca6fbfdee4` | `artifacts/certification/runtime/RTC-REQ-064/apps_rg_no_bypass_064_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-7162a6ec7f1` | `artifacts/certification/runtime/RTC-REQ-064/apps_rg_no_bypass_064_evidence.json` |
| uwg_write_path | ✓ |  | `ASRT-0c6335526c5` | `artifacts/certification/runtime/RTC-REQ-064/apps_rg_no_bypass_064_evidence.json` |

</details>

<details><summary><b>RTC-REQ-065</b> — ✅ SIGNED_OFF — Cache lineage required for factual answers</summary>

- claim_type: `COMPONENT_RUNTIME`
- row_digest: `7013f5932327676423d2a4ccb20f8b1df62d90ca998f0d89173c30fe208fcc17`
- row_evidence_sha256: `41fe37a25b2eb08c5b863fd40e15c80c7f0fcf448071d771f7f1b3c98cdfc094`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-6fa0d6eb29f` | `artifacts/certification/runtime/RTC-REQ-065/apps_rg_component_runtime_065_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-28431acdf80` | `artifacts/certification/runtime/RTC-REQ-065/apps_rg_component_runtime_065_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-bca5ff90f42` | `artifacts/certification/runtime/RTC-REQ-065/apps_rg_component_runtime_065_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-f7422ac1b05` | `artifacts/certification/runtime/RTC-REQ-065/apps_rg_component_runtime_065_evidence.json` |
| evidence_manifest_hash | ✓ |  | `ASRT-04331d7789a` | `artifacts/certification/runtime/RTC-REQ-065/apps_rg_component_runtime_065_evidence.json` |

</details>

<details><summary><b>RTC-REQ-066</b> — ✅ SIGNED_OFF — Cache invalidation proof</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `b67250594098db4f527b5a2c5d13287a85a765962673321ecf2b3c6b13c5639b`
- row_evidence_sha256: `b2579bce92675795de4f196fd75d88076fa21acf517ee5d0abc5560e48891389`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-3880894c6ab` | `artifacts/certification/runtime/RTC-REQ-066/apps_rg_static_enforcement_066_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-bddf5b9c533` | `artifacts/certification/runtime/RTC-REQ-066/apps_rg_static_enforcement_066_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-7e766b65d80` | `artifacts/certification/runtime/RTC-REQ-066/apps_rg_static_enforcement_066_evidence.json` |
| ci_gate | ✓ |  | `ASRT-56443a1dc87` | `artifacts/certification/runtime/RTC-REQ-066/apps_rg_static_enforcement_066_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-ef2c9a07cf6` | `artifacts/certification/runtime/RTC-REQ-066/apps_rg_static_enforcement_066_evidence.json` |

</details>

<details><summary><b>RTC-REQ-067</b> — ✅ SIGNED_OFF — L4 cache state schema fields accounted</summary>

- claim_type: `STATIC_CONTRACT`
- row_digest: `6d2e35f8014dfc4d0e2a76b654e43e87aa2cdb12476e4ba5c76a651d0c978522`
- row_evidence_sha256: `df93373ce7d6f6f4c7b97f20f280967349418abd9ac073ac871a682ed8f87553`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-61e00022652` | `artifacts/certification/runtime/RTC-REQ-067/apps_rg_static_contract_067_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-b16689f019b` | `artifacts/certification/runtime/RTC-REQ-067/apps_rg_static_contract_067_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-4aa0a921645` | `artifacts/certification/runtime/RTC-REQ-067/apps_rg_static_contract_067_evidence.json` |
| required_artifacts | ✓ |  | `ASRT-81f9a8ce969` | `artifacts/certification/runtime/RTC-REQ-067/apps_rg_static_contract_067_evidence.json` |
| artifact_payload_hash | ✓ |  | `ASRT-2611e6b3621` | `artifacts/certification/runtime/RTC-REQ-067/apps_rg_static_contract_067_evidence.json` |

</details>

<details><summary><b>RTC-REQ-070</b> — ✅ SIGNED_OFF — No direct durable write from L2</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `026d3117737159cf471b837460faffb8e2f63348d96d21b31664995591800f54`
- row_evidence_sha256: `ff5dd540bbfa1ca7a5cb6d2bd4364223c4354c4e7830d8af2de46228ae40ce7c`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-0d1d98d466b` | `artifacts/certification/runtime/RTC-REQ-070/apps_rg_no_bypass_070_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-8869d997476` | `artifacts/certification/runtime/RTC-REQ-070/apps_rg_no_bypass_070_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-c319225b4d0` | `artifacts/certification/runtime/RTC-REQ-070/apps_rg_no_bypass_070_evidence.json` |
| no_bypass | ✓ |  | `ASRT-db4ddc569b1` | `artifacts/certification/runtime/RTC-REQ-070/apps_rg_no_bypass_070_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-20b668c3585` | `artifacts/certification/runtime/RTC-REQ-070/apps_rg_no_bypass_070_evidence.json` |
| uwg_write_path | ✓ |  | `ASRT-f54c2a92806` | `artifacts/certification/runtime/RTC-REQ-070/apps_rg_no_bypass_070_evidence.json` |

</details>

<details><summary><b>RTC-REQ-071</b> — ✅ SIGNED_OFF — No direct durable write from L6</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `a0203c2b65adc685ae395713db7e31f76695ba7739a21528ebd93dc5e651b940`
- row_evidence_sha256: `b80ac53ae3efd87c356d862dd79dfca16318dc37af59cd7cad7437362ed38cae`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-2b353ba4da1` | `artifacts/certification/runtime/RTC-REQ-071/apps_rg_no_bypass_071_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-ba1561101b3` | `artifacts/certification/runtime/RTC-REQ-071/apps_rg_no_bypass_071_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-9dce4c5ab83` | `artifacts/certification/runtime/RTC-REQ-071/apps_rg_no_bypass_071_evidence.json` |
| no_bypass | ✓ |  | `ASRT-2c0ee5dd6b0` | `artifacts/certification/runtime/RTC-REQ-071/apps_rg_no_bypass_071_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-5896050cc20` | `artifacts/certification/runtime/RTC-REQ-071/apps_rg_no_bypass_071_evidence.json` |
| uwg_write_path | ✓ |  | `ASRT-4351d06b087` | `artifacts/certification/runtime/RTC-REQ-071/apps_rg_no_bypass_071_evidence.json` |

</details>

<details><summary><b>RTC-REQ-072</b> — ✅ SIGNED_OFF — UWG write sequence complete</summary>

- claim_type: `INTEGRATED_RUNTIME`
- row_digest: `08749c2729c5279a4807b363faee935637a2b57555daebb3f99e05d61098bd35`
- row_evidence_sha256: `02d471a1c4f03f6c217f166f67bb415c26d13bc375895aa749bebd5c3291e482`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-b91a88afa6d` | `artifacts/certification/runtime/RTC-REQ-072/apps_rg_integrated_072_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-959370109be` | `artifacts/certification/runtime/RTC-REQ-072/apps_rg_integrated_072_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-542114351c4` | `artifacts/certification/runtime/RTC-REQ-072/apps_rg_integrated_072_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-2e5cf3e2960` | `artifacts/certification/runtime/RTC-REQ-072/apps_rg_integrated_072_evidence.json` |
| otel_trace | ✓ |  | `ASRT-7a51e5b3544` | `artifacts/certification/runtime/RTC-REQ-072/apps_rg_integrated_072_evidence.json` |
| source_root_binding | ✓ |  | `ASRT-f5c531bf8aa` | `artifacts/certification/runtime/RTC-REQ-072/apps_rg_integrated_072_evidence.json` |
| artifact_payload_hash | ✓ |  | `ASRT-75fa1a70ee0` | `artifacts/certification/runtime/RTC-REQ-072/apps_rg_integrated_072_evidence.json` |
| uwg_write_path | ✓ |  | `ASRT-c7eaa68ff00` | `artifacts/certification/runtime/RTC-REQ-072/apps_rg_integrated_072_evidence.json` |

</details>

<details><summary><b>RTC-REQ-073</b> — ✅ SIGNED_OFF — L4 read-surface refresh after commit</summary>

- claim_type: `COMPONENT_RUNTIME`
- row_digest: `d8027ef14cd499e2eda28e6f1efe4d362d4c8b6dfe9f3f197973045719cc2419`
- row_evidence_sha256: `20c48d809cb3994c685ecbefe34cc5dd194773ebe2566cdd885a5c62b578676d`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-0a864127fb1` | `artifacts/certification/runtime/RTC-REQ-073/apps_rg_component_runtime_073_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-904d5a6a6be` | `artifacts/certification/runtime/RTC-REQ-073/apps_rg_component_runtime_073_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-c801ecd4064` | `artifacts/certification/runtime/RTC-REQ-073/apps_rg_component_runtime_073_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-38ccb6c4f6f` | `artifacts/certification/runtime/RTC-REQ-073/apps_rg_component_runtime_073_evidence.json` |
| evidence_manifest_hash | ✓ |  | `ASRT-33eeec906cc` | `artifacts/certification/runtime/RTC-REQ-073/apps_rg_component_runtime_073_evidence.json` |

</details>

<details><summary><b>RTC-REQ-080</b> — ✅ SIGNED_OFF — UNKNOWN is never PASS</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `f692a1bec4d822efa3dbe19dff5d93955b51f5e21648d7baf686039a5024e909`
- row_evidence_sha256: `910ec4bd1c60154ccb8b14851f407f9ef37cab66be18675d42d574d4ee7eab78`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-d2e5d0daf41` | `artifacts/certification/runtime/RTC-REQ-080/apps_rg_no_bypass_080_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-134b5060ff8` | `artifacts/certification/runtime/RTC-REQ-080/apps_rg_no_bypass_080_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-8263a7bd012` | `artifacts/certification/runtime/RTC-REQ-080/apps_rg_no_bypass_080_evidence.json` |
| no_bypass | ✓ |  | `ASRT-166c71dbdc3` | `artifacts/certification/runtime/RTC-REQ-080/apps_rg_no_bypass_080_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-fd7212bf288` | `artifacts/certification/runtime/RTC-REQ-080/apps_rg_no_bypass_080_evidence.json` |

</details>

<details><summary><b>RTC-REQ-081</b> — ✅ SIGNED_OFF — NOT_APPLICABLE requires reason</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `6524bc4a9c7118557ea416eff943b8cc09226fa6270426abe77f0bcd646fb54d`
- row_evidence_sha256: `5ee27b9904b9085d8d3c778590d08b82cbeaaeae9329b62e74cc58c7607a82b7`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-c4d456cfd58` | `artifacts/certification/runtime/RTC-REQ-081/apps_rg_no_bypass_081_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-a790a19855a` | `artifacts/certification/runtime/RTC-REQ-081/apps_rg_no_bypass_081_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-feeb3a0d150` | `artifacts/certification/runtime/RTC-REQ-081/apps_rg_no_bypass_081_evidence.json` |
| no_bypass | ✓ |  | `ASRT-9216096e478` | `artifacts/certification/runtime/RTC-REQ-081/apps_rg_no_bypass_081_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-0e8c9b2e0a2` | `artifacts/certification/runtime/RTC-REQ-081/apps_rg_no_bypass_081_evidence.json` |

</details>

<details><summary><b>RTC-REQ-082</b> — ✅ SIGNED_OFF — Gate verdicts are not final X3</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `b5694317d2ba72b3d8591562ff604bbcd29c2232d09193e7c93aeee292d33858`
- row_evidence_sha256: `e52b036cf1a19313579e5c134672ceb0c4a03cf9805ddd54675451f472d52579`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-a25ebfd29e5` | `artifacts/certification/runtime/RTC-REQ-082/apps_rg_static_enforcement_082_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-dc428084493` | `artifacts/certification/runtime/RTC-REQ-082/apps_rg_static_enforcement_082_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-538edb84a6e` | `artifacts/certification/runtime/RTC-REQ-082/apps_rg_static_enforcement_082_evidence.json` |
| ci_gate | ✓ |  | `ASRT-cb6be65b3a1` | `artifacts/certification/runtime/RTC-REQ-082/apps_rg_static_enforcement_082_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-29ed70b9f5e` | `artifacts/certification/runtime/RTC-REQ-082/apps_rg_static_enforcement_082_evidence.json` |

</details>

<details><summary><b>RTC-REQ-083</b> — ✅ SIGNED_OFF — Negative controls must match expected fail reason</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `852aa3ab794ccaf9ab8e9e827816bc71df8314ca42b8ead19aad5bb39afa5f91`
- row_evidence_sha256: `4450af20c2f07f3ae876ca56b611936a1b8a81818d387c7ecf182017f53442b7`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-374ac4264cb` | `artifacts/certification/runtime/RTC-REQ-083/apps_rg_no_bypass_083_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-15dd86e5325` | `artifacts/certification/runtime/RTC-REQ-083/apps_rg_no_bypass_083_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-1f20af530cb` | `artifacts/certification/runtime/RTC-REQ-083/apps_rg_no_bypass_083_evidence.json` |
| no_bypass | ✓ |  | `ASRT-fe8a19f852a` | `artifacts/certification/runtime/RTC-REQ-083/apps_rg_no_bypass_083_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-a6ab2a1ff40` | `artifacts/certification/runtime/RTC-REQ-083/apps_rg_no_bypass_083_evidence.json` |
| negative_controls | ✓ |  | `ASRT-d5a69ea22dc` | `artifacts/certification/runtime/RTC-REQ-083/apps_rg_no_bypass_083_evidence.json` |
| expected_fail_reason | ✓ |  | `ASRT-7cc68d16b0a` | `artifacts/certification/runtime/RTC-REQ-083/apps_rg_no_bypass_083_evidence.json` |

</details>

<details><summary><b>RTC-REQ-084</b> — ✅ SIGNED_OFF — No bypass mutation suite required</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `8129b8ed4c125bb5189e4416d1828007b3d49074b11921c2324527c660d86123`
- row_evidence_sha256: `e37cddd9ddfe6ccd1bee27cdddbe7bf577e27dd3fba77fdc415c0de36687f7d2`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-ef3182e0510` | `artifacts/certification/runtime/RTC-REQ-084/apps_rg_no_bypass_084_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-2434317cacf` | `artifacts/certification/runtime/RTC-REQ-084/apps_rg_no_bypass_084_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-57e4fb31c74` | `artifacts/certification/runtime/RTC-REQ-084/apps_rg_no_bypass_084_evidence.json` |
| no_bypass | ✓ |  | `ASRT-9ba1d2b536b` | `artifacts/certification/runtime/RTC-REQ-084/apps_rg_no_bypass_084_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-a88dfa1056e` | `artifacts/certification/runtime/RTC-REQ-084/apps_rg_no_bypass_084_evidence.json` |

</details>

<details><summary><b>RTC-REQ-090</b> — ✅ SIGNED_OFF — U0 intake emits validated or rejected request only</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `89aa98aa772cd15f342b4c2acd92b74efa049597dac88eea4d4934cc034a9ebd`
- row_evidence_sha256: `3b5cdf40b48c2390df515d6cb56012d0ff12b201bf4ba51ef90a7c50b939a91c`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-04bdab169a4` | `artifacts/certification/runtime/RTC-REQ-090/apps_rg_static_enforcement_090_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-4efe24fdd12` | `artifacts/certification/runtime/RTC-REQ-090/apps_rg_static_enforcement_090_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-ca8a20d41e4` | `artifacts/certification/runtime/RTC-REQ-090/apps_rg_static_enforcement_090_evidence.json` |
| ci_gate | ✓ |  | `ASRT-ae37ea92af0` | `artifacts/certification/runtime/RTC-REQ-090/apps_rg_static_enforcement_090_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-0658630c7cf` | `artifacts/certification/runtime/RTC-REQ-090/apps_rg_static_enforcement_090_evidence.json` |

</details>

<details><summary><b>RTC-REQ-091</b> — ✅ SIGNED_OFF — L1 plans but does not route/retrieve/execute</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `466c5a657d603a73580b7993b8ab76da3d4022ad4b1b340cef43146cf427a880`
- row_evidence_sha256: `fb756f4a7f327a91e835ded41b02bb49365389eb62149036388892573394dde6`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-b980b68f0ca` | `artifacts/certification/runtime/RTC-REQ-091/apps_rg_static_enforcement_091_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-f4daa40fe2b` | `artifacts/certification/runtime/RTC-REQ-091/apps_rg_static_enforcement_091_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-bcc9b7b0c6e` | `artifacts/certification/runtime/RTC-REQ-091/apps_rg_static_enforcement_091_evidence.json` |
| ci_gate | ✓ |  | `ASRT-77450ef5899` | `artifacts/certification/runtime/RTC-REQ-091/apps_rg_static_enforcement_091_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-1bad0df38c9` | `artifacts/certification/runtime/RTC-REQ-091/apps_rg_static_enforcement_091_evidence.json` |

</details>

<details><summary><b>RTC-REQ-092</b> — ✅ SIGNED_OFF — L0 emits exactly one deterministic RouteContract</summary>

- claim_type: `COMPONENT_RUNTIME`
- row_digest: `0d212eb3f638d25edfb278e0aba53d5f1a68442b0576dd5a2ceb5bce2d321d61`
- row_evidence_sha256: `9c6117fd66d45fbef054cc92c4c4ec884ef0040b66105122adcce22aaa994296`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-59e3b2ef0ad` | `artifacts/certification/runtime/RTC-REQ-092/apps_rg_component_runtime_092_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-fa687bd867c` | `artifacts/certification/runtime/RTC-REQ-092/apps_rg_component_runtime_092_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-24d492b5fde` | `artifacts/certification/runtime/RTC-REQ-092/apps_rg_component_runtime_092_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-452931bac5c` | `artifacts/certification/runtime/RTC-REQ-092/apps_rg_component_runtime_092_evidence.json` |
| evidence_manifest_hash | ✓ |  | `ASRT-b7ecd90b0e9` | `artifacts/certification/runtime/RTC-REQ-092/apps_rg_component_runtime_092_evidence.json` |

</details>

<details><summary><b>RTC-REQ-093</b> — ✅ SIGNED_OFF — C0 retrieves evidence only</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `9aa183735b78a75d88db74fa405fca176994270a92b389a850ef073450b0d973`
- row_evidence_sha256: `420c7f7fcb8b5ad2e919ecb88739986eeacc28b03edeb54f7216f9bae2640c18`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-575e9f81c62` | `artifacts/certification/runtime/RTC-REQ-093/apps_rg_static_enforcement_093_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-07500ee82ac` | `artifacts/certification/runtime/RTC-REQ-093/apps_rg_static_enforcement_093_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-9718ab75607` | `artifacts/certification/runtime/RTC-REQ-093/apps_rg_static_enforcement_093_evidence.json` |
| ci_gate | ✓ |  | `ASRT-3426f1dce17` | `artifacts/certification/runtime/RTC-REQ-093/apps_rg_static_enforcement_093_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-e6bc2ef7309` | `artifacts/certification/runtime/RTC-REQ-093/apps_rg_static_enforcement_093_evidence.json` |

</details>

<details><summary><b>RTC-REQ-094</b> — ✅ SIGNED_OFF — Prompt Assembly composes only</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `3be86fa76fac27ae0e5ae3030d3da9d920a4d35ca5c759b548450947f22413bb`
- row_evidence_sha256: `0cc856a236f1111fbf848a946a7bc5612adf57a9e5f1b5baf0a0af6602bac31b`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-a675441cfc2` | `artifacts/certification/runtime/RTC-REQ-094/apps_rg_static_enforcement_094_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-57d472c05fc` | `artifacts/certification/runtime/RTC-REQ-094/apps_rg_static_enforcement_094_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-9e937e1b262` | `artifacts/certification/runtime/RTC-REQ-094/apps_rg_static_enforcement_094_evidence.json` |
| ci_gate | ✓ |  | `ASRT-e3bef8ee611` | `artifacts/certification/runtime/RTC-REQ-094/apps_rg_static_enforcement_094_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-3f36af84cf5` | `artifacts/certification/runtime/RTC-REQ-094/apps_rg_static_enforcement_094_evidence.json` |

</details>

<details><summary><b>RTC-REQ-095</b> — ✅ SIGNED_OFF — L2 bounded execution and sealing only</summary>

- claim_type: `COMPONENT_RUNTIME`
- row_digest: `f3fa4b5bf4f51a409741ec80b292e9f492bb90f4fcce05af812f9f4d7518b0a1`
- row_evidence_sha256: `81fed2f53a9a77bc33f938060ba3d12bcf62492c7a785c62b6981ec654a63403`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-5b16a5648db` | `artifacts/certification/runtime/RTC-REQ-095/apps_rg_component_runtime_095_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-57bb303965d` | `artifacts/certification/runtime/RTC-REQ-095/apps_rg_component_runtime_095_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-896dc5c09ed` | `artifacts/certification/runtime/RTC-REQ-095/apps_rg_component_runtime_095_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-839a19f54a5` | `artifacts/certification/runtime/RTC-REQ-095/apps_rg_component_runtime_095_evidence.json` |
| evidence_manifest_hash | ✓ |  | `ASRT-efe3ad3ee99` | `artifacts/certification/runtime/RTC-REQ-095/apps_rg_component_runtime_095_evidence.json` |

</details>

<details><summary><b>RTC-REQ-096</b> — ✅ SIGNED_OFF — Exit emits exactly one X3 and does not write L4</summary>

- claim_type: `INTEGRATED_RUNTIME`
- row_digest: `002d399c28920a9f93b8aa9fa1c72cc39dd2066d838bc2c975160f765c587b08`
- row_evidence_sha256: `6c880649a223ee5a9f71cf99419c58b254366305017943d9e7f33c522387da70`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-dccbd4573fe` | `artifacts/certification/runtime/RTC-REQ-096/apps_rg_runtime_evidence_chain_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-dda5e95d695` | `artifacts/certification/runtime/RTC-REQ-096/apps_rg_runtime_evidence_chain_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-1fa87c171ee` | `artifacts/certification/runtime/RTC-REQ-096/apps_rg_runtime_evidence_chain_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-93f41934805` | `artifacts/certification/runtime/RTC-REQ-096/apps_rg_runtime_evidence_chain_evidence.json` |
| otel_trace | ✓ |  | `ASRT-93ad83657a9` | `artifacts/certification/runtime/RTC-REQ-096/apps_rg_runtime_evidence_chain_evidence.json` |
| source_root_binding | ✓ |  | `ASRT-97e8ade2528` | `artifacts/certification/runtime/RTC-REQ-096/apps_rg_runtime_evidence_chain_evidence.json` |
| artifact_payload_hash | ✓ |  | `ASRT-552acccbdde` | `artifacts/certification/runtime/RTC-REQ-096/apps_rg_runtime_evidence_chain_evidence.json` |

</details>

<details><summary><b>RTC-REQ-097</b> — ✅ SIGNED_OFF — L6 completed-run learning only</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `812f7f91ad3b8d6983be71a8e76331e112955e96cfa163d00e5887da3c57783e`
- row_evidence_sha256: `752330602cdf58dd9b41baf5eb8d4a716fa27ad1a4c7943c39a339f815935b13`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-29b15314267` | `artifacts/certification/runtime/RTC-REQ-097/apps_rg_no_bypass_097_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-697b780ef24` | `artifacts/certification/runtime/RTC-REQ-097/apps_rg_no_bypass_097_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-da435b92ca9` | `artifacts/certification/runtime/RTC-REQ-097/apps_rg_no_bypass_097_evidence.json` |
| no_bypass | ✓ |  | `ASRT-54b435cb68b` | `artifacts/certification/runtime/RTC-REQ-097/apps_rg_no_bypass_097_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-38818cc7f48` | `artifacts/certification/runtime/RTC-REQ-097/apps_rg_no_bypass_097_evidence.json` |

</details>

<details><summary><b>RTC-REQ-100</b> — ✅ SIGNED_OFF — Semantic cache certification report required</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `42c63155b4ac3e0ab214fab9025ae934bb6ee764fb400bdc56abb015f4649e49`
- row_evidence_sha256: `ce0547d1a3f1a054b5dd9d6fbf2399e12fc119106f5a8dd015188e646b348202`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-09b8aed3240` | `artifacts/certification/runtime/RTC-REQ-100/apps_rg_static_enforcement_100_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-91a275069a2` | `artifacts/certification/runtime/RTC-REQ-100/apps_rg_static_enforcement_100_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-89bb8b8333d` | `artifacts/certification/runtime/RTC-REQ-100/apps_rg_static_enforcement_100_evidence.json` |
| ci_gate | ✓ |  | `ASRT-9eaa6ae5ce2` | `artifacts/certification/runtime/RTC-REQ-100/apps_rg_static_enforcement_100_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-a88fc19c1b9` | `artifacts/certification/runtime/RTC-REQ-100/apps_rg_static_enforcement_100_evidence.json` |

</details>

<details><summary><b>RTC-REQ-101</b> — ✅ SIGNED_OFF — Runtime certification report required</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `d98723ffdc2cc17a6442882722df79b90cd50acaadfe950d5a89f5f585d8c160`
- row_evidence_sha256: `693642b00fd155ad4eba12ff391fa08abcb71aca8d98497702a2ec6849ec840e`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-eafb8f202bb` | `artifacts/certification/runtime/RTC-REQ-101/apps_rg_static_enforcement_101_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-c47e585535c` | `artifacts/certification/runtime/RTC-REQ-101/apps_rg_static_enforcement_101_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-690c1bc4bc5` | `artifacts/certification/runtime/RTC-REQ-101/apps_rg_static_enforcement_101_evidence.json` |
| ci_gate | ✓ |  | `ASRT-01fcd331359` | `artifacts/certification/runtime/RTC-REQ-101/apps_rg_static_enforcement_101_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-d14904e766a` | `artifacts/certification/runtime/RTC-REQ-101/apps_rg_static_enforcement_101_evidence.json` |

</details>

<details><summary><b>RTC-REQ-102</b> — ✅ SIGNED_OFF — Certification language scoped by proof class</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `c846b67f5258abbafe93d84177f2488ac4cfad6211cb3179772cb4b5e2027fc8`
- row_evidence_sha256: `43981b17ad889ee067d952bc611573325162b1f079d2d7303f4aa40c682d0bc9`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-f495de0a585` | `artifacts/certification/runtime/RTC-REQ-102/apps_rg_static_enforcement_102_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-00921f70dab` | `artifacts/certification/runtime/RTC-REQ-102/apps_rg_static_enforcement_102_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-2ce04167b77` | `artifacts/certification/runtime/RTC-REQ-102/apps_rg_static_enforcement_102_evidence.json` |
| ci_gate | ✓ |  | `ASRT-baa3f5dbaa4` | `artifacts/certification/runtime/RTC-REQ-102/apps_rg_static_enforcement_102_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-8d509ba3f98` | `artifacts/certification/runtime/RTC-REQ-102/apps_rg_static_enforcement_102_evidence.json` |

</details>

<details><summary><b>RTC-REQ-103</b> — ✅ SIGNED_OFF — Allowed partial language</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `d963cec8119bbe453e962caebc7a3cbe7361f841dfc8fdee308a20be654f51d9`
- row_evidence_sha256: `661c923c35252d7f21ad2114d543341de085d12c4d6c2071e4cf175363de1c81`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-c6dc2a47032` | `artifacts/certification/runtime/RTC-REQ-103/apps_rg_static_enforcement_103_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-f8254fcaf0a` | `artifacts/certification/runtime/RTC-REQ-103/apps_rg_static_enforcement_103_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-23210a204e4` | `artifacts/certification/runtime/RTC-REQ-103/apps_rg_static_enforcement_103_evidence.json` |
| ci_gate | ✓ |  | `ASRT-8565af4b93a` | `artifacts/certification/runtime/RTC-REQ-103/apps_rg_static_enforcement_103_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-b245ae7b541` | `artifacts/certification/runtime/RTC-REQ-103/apps_rg_static_enforcement_103_evidence.json` |

</details>

<details><summary><b>RTC-REQ-110</b> — ✅ SIGNED_OFF — Matrix schema CI gate</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `2a66679918e07e548246b3aa94366cbb8f56fb6c825c0d7a4e456c44a572149d`
- row_evidence_sha256: `47fad72d7013b62b60405d5915fbaf459a53f75a3053b2139f65c1d3717ac60f`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-a7d0bfe9886` | `artifacts/certification/positive_control_RTC-REQ-110.json` |
| verifier_exit_zero | ✓ |  | `ASRT-209c57225b2` | `artifacts/certification/positive_control_RTC-REQ-110.json` |
| last_verified_timestamp | ✓ |  | `ASRT-bfbb921e9fc` | `artifacts/certification/positive_control_RTC-REQ-110.json` |
| ci_gate | ✓ |  | `ASRT-8b6e5706c63` | `artifacts/certification/ci_gate_binding_report.json` |
| layer_boundary | ✓ |  | `ASRT-7e79db29e04` | `artifacts/certification/layer_boundary_report_csv_gate.json` |

</details>

<details><summary><b>RTC-REQ-111</b> — ✅ SIGNED_OFF — Acceptance legality CI gate</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `3f7adb30b0e8f5ffe79eada61dac9081085da4ba092e5612b36b351beb3e91cf`
- row_evidence_sha256: `04b83e12146da6d7f920762b4e25bf395d5b64f1dd31c122afd7fca89004ab27`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-d678c6e50d4` | `artifacts/certification/positive_control_RTC-REQ-111.json` |
| verifier_exit_zero | ✓ |  | `ASRT-93459078c61` | `artifacts/certification/positive_control_RTC-REQ-111.json` |
| last_verified_timestamp | ✓ |  | `ASRT-14042f155fc` | `artifacts/certification/positive_control_RTC-REQ-111.json` |
| ci_gate | ✓ |  | `ASRT-ee95b317fb6` | `artifacts/certification/ci_gate_binding_report.json` |
| layer_boundary | ✓ |  | `ASRT-71b5c6888b4` | `artifacts/certification/layer_boundary_report_csv_gate.json` |

</details>

<details><summary><b>RTC-REQ-112</b> — ✅ SIGNED_OFF — Semantic cache CI gate</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `859d80004530e943b87b226faaca8d81f0472f3aef456374268cf83e0a8f4f7a`
- row_evidence_sha256: `5f4de4b4fd7c45f25c3eb77b364547f92b4b20cd3024c9a20a089c63487259e6`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-d4a9d7ff257` | `artifacts/certification/runtime/RTC-REQ-112/apps_rg_no_bypass_112_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-82e5f4efeb6` | `artifacts/certification/runtime/RTC-REQ-112/apps_rg_no_bypass_112_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-0dc33516fc7` | `artifacts/certification/runtime/RTC-REQ-112/apps_rg_no_bypass_112_evidence.json` |
| no_bypass | ✓ |  | `ASRT-ebc068ebd98` | `artifacts/certification/runtime/RTC-REQ-112/apps_rg_no_bypass_112_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-4ba698128a6` | `artifacts/certification/runtime/RTC-REQ-112/apps_rg_no_bypass_112_evidence.json` |

</details>

<details><summary><b>RTC-REQ-113</b> — ✅ SIGNED_OFF — OTEL collector CI gate</summary>

- claim_type: `OBSERVABILITY_RUNTIME`
- row_digest: `f675703c09b38d5fbe894199224f14bb458aa65180a603674ce16156dadb0134`
- row_evidence_sha256: `51620094976ed63c55be5fd476db98b0cfdb6ce9172664226f851819b47556a3`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-500ff95b3e0` | `artifacts/certification/runtime/RTC-REQ-113/apps_rg_observability_113_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-64560d36701` | `artifacts/certification/runtime/RTC-REQ-113/apps_rg_observability_113_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-b07bc99e148` | `artifacts/certification/runtime/RTC-REQ-113/apps_rg_observability_113_evidence.json` |
| otel_trace | ✓ |  | `ASRT-2ca7981a173` | `artifacts/certification/runtime/RTC-REQ-113/apps_rg_observability_113_evidence.json` |

</details>

<details><summary><b>RTC-REQ-114</b> — ✅ SIGNED_OFF — Replay CI gate</summary>

- claim_type: `REPLAY_RUNTIME`
- row_digest: `e6fccebc3a96394e3884c070f8a9739f384b36c1d3442b9e3d71dc40d1fff394`
- row_evidence_sha256: `e609dc13692e2d473577e1c76fc8253fee0d31b7c4a9d703e18874eb5d04aa24`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-0cdab1bccd8` | `artifacts/certification/runtime/RTC-REQ-114/apps_rg_replay_114_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-77771cbe71f` | `artifacts/certification/runtime/RTC-REQ-114/apps_rg_replay_114_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-1fff91ac319` | `artifacts/certification/runtime/RTC-REQ-114/apps_rg_replay_114_evidence.json` |
| replay_receipt | ✓ |  | `ASRT-6b77a37124e` | `artifacts/certification/runtime/RTC-REQ-114/apps_rg_replay_114_evidence.json` |

</details>

<details><summary><b>RTC-REQ-115</b> — ✅ SIGNED_OFF — No-bypass mutation CI gate</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `1e827de32227f6ad302147c6c8b176504481acb29407b0642f050b952f782fc0`
- row_evidence_sha256: `f54bcbc57217bb1d3a327f94b7526c030c7bdb0f79ac9855fc96bda8b6799f0c`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-d91a1c81926` | `artifacts/certification/runtime/RTC-REQ-115/apps_rg_no_bypass_115_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-fff02b47066` | `artifacts/certification/runtime/RTC-REQ-115/apps_rg_no_bypass_115_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-593dabbb538` | `artifacts/certification/runtime/RTC-REQ-115/apps_rg_no_bypass_115_evidence.json` |
| no_bypass | ✓ |  | `ASRT-ddcf4d3a083` | `artifacts/certification/runtime/RTC-REQ-115/apps_rg_no_bypass_115_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-eba81557150` | `artifacts/certification/runtime/RTC-REQ-115/apps_rg_no_bypass_115_evidence.json` |

</details>

<details><summary><b>RTC-REQ-120</b> — ✅ SIGNED_OFF — 100.0% runtime certification definition</summary>

- claim_type: `INTEGRATED_RUNTIME`
- row_digest: `30bb0ff61aaf9973eae85a6ad575849dfc9f851691b9468544f7121d16c803d7`
- row_evidence_sha256: `90be3a787915e8f7d98530315de9552bd219b2fc42503eeef86785350c408685`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-648d30a51db` | `artifacts/certification/runtime/RTC-REQ-120/apps_rg_integrated_120_capstone_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-66e819004dd` | `artifacts/certification/runtime/RTC-REQ-120/apps_rg_integrated_120_capstone_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-74ce06fc5dd` | `artifacts/certification/runtime/RTC-REQ-120/apps_rg_integrated_120_capstone_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-c81cc7d7c2a` | `artifacts/certification/runtime/RTC-REQ-120/apps_rg_integrated_120_capstone_evidence.json` |
| otel_trace | ✓ |  | `ASRT-3f4cf4c09f7` | `artifacts/certification/runtime/RTC-REQ-120/apps_rg_integrated_120_capstone_evidence.json` |
| source_root_binding | ✓ |  | `ASRT-a1e4accd937` | `artifacts/certification/runtime/RTC-REQ-120/apps_rg_integrated_120_capstone_evidence.json` |
| artifact_payload_hash | ✓ |  | `ASRT-b595dec9225` | `artifacts/certification/runtime/RTC-REQ-120/apps_rg_integrated_120_capstone_evidence.json` |

</details>

<details><summary><b>RTC-REQ-121</b> — ✅ SIGNED_OFF — 100.0% static enforcement coverage separate from runtime certification</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `a1f42307c69a8c7db81941beb6997b36e2509adc0e0886be7e2ce10774777e8b`
- row_evidence_sha256: `a1c7efd302207530c954a094de5a9dc511c53af1046f17dda46a700f6b86b8b5`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-a69add3895d` | `artifacts/certification/runtime/RTC-REQ-121/apps_rg_static_enforcement_121_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-2ebe70890e6` | `artifacts/certification/runtime/RTC-REQ-121/apps_rg_static_enforcement_121_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-c650dbc1d24` | `artifacts/certification/runtime/RTC-REQ-121/apps_rg_static_enforcement_121_evidence.json` |
| ci_gate | ✓ |  | `ASRT-b609d7a25d5` | `artifacts/certification/runtime/RTC-REQ-121/apps_rg_static_enforcement_121_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-8cf2c58f512` | `artifacts/certification/runtime/RTC-REQ-121/apps_rg_static_enforcement_121_evidence.json` |

</details>

<details><summary><b>RTC-REQ-122</b> — ✅ SIGNED_OFF — No scoped blockers in final claim</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `0ae0171e612a384ed9cf0e4d8c6375712f9eb13f1cf41dbac7abcf16d4a85558`
- row_evidence_sha256: `429e2f2826e5a942431dc3af245b951b9574a693a6d6dad4ac6880fe6996b2fd`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-8fc48a8da6e` | `artifacts/certification/runtime/RTC-REQ-122/apps_rg_static_enforcement_122_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-d4049f30a66` | `artifacts/certification/runtime/RTC-REQ-122/apps_rg_static_enforcement_122_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-6121a2594aa` | `artifacts/certification/runtime/RTC-REQ-122/apps_rg_static_enforcement_122_evidence.json` |
| ci_gate | ✓ |  | `ASRT-d8b0b26016e` | `artifacts/certification/runtime/RTC-REQ-122/apps_rg_static_enforcement_122_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-404ddfb588c` | `artifacts/certification/runtime/RTC-REQ-122/apps_rg_static_enforcement_122_evidence.json` |

</details>

<details><summary><b>RTC-REQ-123</b> — ✅ SIGNED_OFF — Artifact payload content-hash validation</summary>

- claim_type: `NO_BYPASS_RUNTIME`
- row_digest: `ca860ee1637ec832618a778664c1a41c21beaa9c3b4383ebdabc7ea43cd56660`
- row_evidence_sha256: `daf63f3d82bbb628fc2fc034721032acd0bd8ca368635b6ab538beba12d9f205`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-6a5f95e559d` | `artifacts/certification/runtime/RTC-REQ-123/apps_rg_no_bypass_123_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-e144fc6c475` | `artifacts/certification/runtime/RTC-REQ-123/apps_rg_no_bypass_123_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-21ea32e64b5` | `artifacts/certification/runtime/RTC-REQ-123/apps_rg_no_bypass_123_evidence.json` |
| no_bypass | ✓ |  | `ASRT-a1092a52e16` | `artifacts/certification/runtime/RTC-REQ-123/apps_rg_no_bypass_123_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-26e05313f54` | `artifacts/certification/runtime/RTC-REQ-123/apps_rg_no_bypass_123_evidence.json` |

</details>

<details><summary><b>RTC-REQ-124</b> — ✅ SIGNED_OFF — Single repo root and output directory binding</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `cacde0e19624817631a5a80272cf2110cf973a6622f7f84ea5a13e55e23ab1f7`
- row_evidence_sha256: `083a0f2c9290a23507d97cd5407de10b1b25ae11383ea8bdbb2da6f3a794ffe5`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-94891252987` | `artifacts/certification/runtime/RTC-REQ-124/apps_rg_static_enforcement_124_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-bb6ab211f4c` | `artifacts/certification/runtime/RTC-REQ-124/apps_rg_static_enforcement_124_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-6705f248317` | `artifacts/certification/runtime/RTC-REQ-124/apps_rg_static_enforcement_124_evidence.json` |
| ci_gate | ✓ |  | `ASRT-ad2dd3ff887` | `artifacts/certification/runtime/RTC-REQ-124/apps_rg_static_enforcement_124_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-aeb1e4a3af2` | `artifacts/certification/runtime/RTC-REQ-124/apps_rg_static_enforcement_124_evidence.json` |

</details>

<details><summary><b>RTC-REQ-125</b> — ✅ SIGNED_OFF — Semantic cache production-threshold ADR gate</summary>

- claim_type: `PRODUCTION_DEPENDENCY_RUNTIME`
- row_digest: `60af6035677f47a501865c6444e095517fffecba86b0749e1bdb03d2e5c980b3`
- row_evidence_sha256: `9c117b62ab76d2a4210f71988bdf86b4100336058afea87ab628b9351ccf9947`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-8c479ef993b` | `artifacts/certification/runtime/RTC-REQ-125/apps_rg_production_dep_125_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-3d5551dff72` | `artifacts/certification/runtime/RTC-REQ-125/apps_rg_production_dep_125_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-59a68baab2f` | `artifacts/certification/runtime/RTC-REQ-125/apps_rg_production_dep_125_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-7c93a8a629f` | `artifacts/certification/runtime/RTC-REQ-125/apps_rg_production_dep_125_evidence.json` |
| certifier_signature | ✓ |  | `ASRT-9a7db7e9e74` | `artifacts/certification/runtime/RTC-REQ-125/apps_rg_production_dep_125_evidence.json` |

</details>

<details><summary><b>RTC-REQ-126</b> — ✅ SIGNED_OFF — Embedding fallback must be explicit fail-closed or mismatch-explained</summary>

- claim_type: `PRODUCTION_DEPENDENCY_RUNTIME`
- row_digest: `6d7595a4edf1186f9c7b7fdfb24ec5729f47868af864a7acff270bb7d0e73532`
- row_evidence_sha256: `9338158caa34fec12d03a4aa22c88e28b290a8bfd288a781082f1f300bcae238`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-c24241d923b` | `artifacts/certification/runtime/RTC-REQ-126/apps_rg_production_dep_126_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-d9ebd6d51a0` | `artifacts/certification/runtime/RTC-REQ-126/apps_rg_production_dep_126_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-8abfeba9874` | `artifacts/certification/runtime/RTC-REQ-126/apps_rg_production_dep_126_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-d038a314bcf` | `artifacts/certification/runtime/RTC-REQ-126/apps_rg_production_dep_126_evidence.json` |
| certifier_signature | ✓ |  | `ASRT-fe23efa60d6` | `artifacts/certification/runtime/RTC-REQ-126/apps_rg_production_dep_126_evidence.json` |

</details>

<details><summary><b>RTC-REQ-127</b> — ✅ SIGNED_OFF — Composition proof cannot promote final acceptance automatically</summary>

- claim_type: `STATIC_ENFORCEMENT`
- row_digest: `6c64b7f2e4428572a3a64b9169d88bedda2c772148af031930890fbc05283be9`
- row_evidence_sha256: `16991b419e827247f1bb235dc7d43b0e8e36348fc72293eeca7f8d1b7cd9d3fa`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-b2f68723f38` | `artifacts/certification/runtime/RTC-REQ-127/apps_rg_static_enforcement_127_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-cf150dffe76` | `artifacts/certification/runtime/RTC-REQ-127/apps_rg_static_enforcement_127_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-62de304e23d` | `artifacts/certification/runtime/RTC-REQ-127/apps_rg_static_enforcement_127_evidence.json` |
| ci_gate | ✓ |  | `ASRT-b176736945e` | `artifacts/certification/runtime/RTC-REQ-127/apps_rg_static_enforcement_127_evidence.json` |
| layer_boundary | ✓ |  | `ASRT-b38a6f32d39` | `artifacts/certification/runtime/RTC-REQ-127/apps_rg_static_enforcement_127_evidence.json` |

</details>

<details><summary><b>RTC-REQ-128</b> — ✅ SIGNED_OFF — Gate verdict bundle consumed by Exit</summary>

- claim_type: `INTEGRATED_RUNTIME`
- row_digest: `296afeca6dada7bceddbb375d91dd6c2c73783d151fd7a0b5763dff1fbe2d3d0`
- row_evidence_sha256: `ae3fa275745d398b0a8f12469ccd1983ce6aaef4b0e36a382b73fe280d5eaa3f`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-41064920a75` | `artifacts/certification/runtime/RTC-REQ-128/apps_rg_runtime_evidence_chain_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-544e2491820` | `artifacts/certification/runtime/RTC-REQ-128/apps_rg_runtime_evidence_chain_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-be9a3105b89` | `artifacts/certification/runtime/RTC-REQ-128/apps_rg_runtime_evidence_chain_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-e3b45f844c9` | `artifacts/certification/runtime/RTC-REQ-128/apps_rg_runtime_evidence_chain_evidence.json` |
| otel_trace | ✓ |  | `ASRT-ae1a980b20a` | `artifacts/certification/runtime/RTC-REQ-128/apps_rg_runtime_evidence_chain_evidence.json` |
| source_root_binding | ✓ |  | `ASRT-84d3db765a5` | `artifacts/certification/runtime/RTC-REQ-128/apps_rg_runtime_evidence_chain_evidence.json` |
| artifact_payload_hash | ✓ |  | `ASRT-32917baffe6` | `artifacts/certification/runtime/RTC-REQ-128/apps_rg_runtime_evidence_chain_evidence.json` |

</details>

<details><summary><b>RTC-REQ-129</b> — ✅ SIGNED_OFF — R1B score distribution calibration dataset</summary>

- claim_type: `PRODUCTION_DEPENDENCY_RUNTIME`
- row_digest: `72168b54e4a8bb17da4b5321e60bb4fcf0dbef9211f6089c54fb8a873922e600`
- row_evidence_sha256: `41fa84dd752d3aa40e72cb766238970942aeb2220ab428c3aea9816f40000d51`

| Control | Passed | Reason | Assertion | Artifact |
|---|:---:|---|---|---|
| verifier_pass | ✓ |  | `ASRT-1566d22e9f1` | `artifacts/certification/runtime/RTC-REQ-129/apps_rg_production_dep_129_evidence.json` |
| verifier_exit_zero | ✓ |  | `ASRT-ce91f392e8c` | `artifacts/certification/runtime/RTC-REQ-129/apps_rg_production_dep_129_evidence.json` |
| last_verified_timestamp | ✓ |  | `ASRT-3e95d45858b` | `artifacts/certification/runtime/RTC-REQ-129/apps_rg_production_dep_129_evidence.json` |
| runtime_evidence | ✓ |  | `ASRT-dbca4e6804c` | `artifacts/certification/runtime/RTC-REQ-129/apps_rg_production_dep_129_evidence.json` |
| certifier_signature | ✓ |  | `ASRT-cfb0c9761a1` | `artifacts/certification/runtime/RTC-REQ-129/apps_rg_production_dep_129_evidence.json` |

</details>
