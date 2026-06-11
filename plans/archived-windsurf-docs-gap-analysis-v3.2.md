---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\gap-analysis-v3.2.md'
original_relative_path: 'gap-analysis-v3.2.md'
source_sha256: 8bc47cdbf3249cf78c756de1e1201b4329c3f32c922fd42c4656c7031c9db67f
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-27'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Deterministic Gap Analysis — REQ-001 → REQ-417 (Corpus v3.2)

**Generated:** 2026-02-27
**Corpus:** Agentic Master Requirements v3.2 (417 requirements)
**Method:** Mechanical scan of codebase + corpus metadata + enforcement implementation audit

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## SECTION A — REQUIREMENT LEDGER (417 ROWS)

| REQ_ID | Domain | Severity | Enforcement Class | Enforcement Layers (Declared) | Enforcement Layers (Observed) | Missing Layers | Bypass Risk | Status | Evidence Pointer |
|--------|--------|----------|-------------------|-------------------------------|-------------------------------|----------------|-------------|--------|------------------|
| REQ-001 | Layer Sovereignty | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/agentic_core/test_sovereignty_proof_suite.py |
| REQ-002 | Layer Sovereignty | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/agentic_core/test_sovereignty_proof_suite.py |
| REQ-003 | Layer Sovereignty | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/agentic_core/test_sovereignty_proof_suite.py |
| REQ-004 | Layer Sovereignty | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/agentic_core/test_sovereignty_proof_suite.py |
| REQ-005 | Layer Sovereignty | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/agentic_core/test_sovereignty_proof_suite.py |
| REQ-006 | Layer Sovereignty | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/agentic_core/test_sovereignty_proof_suite.py |
| REQ-007 | Layer Sovereignty | HIGH | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-008 | Layer Sovereignty | HIGH | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-009 | Layer Sovereignty | CRITICAL | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-010 | Layer Sovereignty | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/architecture/test_invariants.py, ops_scripts/ci/* |
| REQ-011 | Gateway | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | MEDIUM | PARTIAL | agentic_core/L2_execution/enforcement/SovereignLLMGateway.py; apps_rg SDK imports observed |
| REQ-012 | Gateway | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | MEDIUM | PARTIAL | ops_scripts/ci/check_model_string_literals.py; model literals found in apps_lic/tools/GeminiLLMClient.py |
| REQ-013 | Gateway | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | system_learning/engines/embedding_service_factory.py, tests/system_learning/test_embedding_service_factory.py |
| REQ-014 | Gateway | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/agents/agent_registry.py, tests/governance/test_agent_execution_profiles.py |
| REQ-015 | Gateway | HIGH | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L2_execution/determinism.py |
| REQ-016 | META-INVARIANT | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | No single chokepoint test proving all 10 subsystems fail-closed with zero silent fallback |
| REQ-017 | Canonicalization | HIGH | EXECUTION_PATH | Schema, Runtime | Schema, Runtime | — | LOW | PASS | tools/canonical_hash.py |
| REQ-018 | Canonicalization | CRITICAL | EXECUTION_PATH | CI, Signature, Runtime | Runtime, CI | Signature verification test absent | MEDIUM | PARTIAL | No dedicated HMAC-SHA256 signature test for all authenticity-critical artifacts |
| REQ-019 | META-INVARIANT | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | HIGH | PARTIAL | Signature-before-side-effect ordering not mechanically proven for all paths |
| REQ-020 | META-INVARIANT | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Append-only enforcement partial; no single seal-immutability proof across all artifact types |
| REQ-021 | Packet | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L2_execution/types/instruction_packet_types.py |
| REQ-022 | Packet | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L2_execution/types/instruction_packet_types.py, tests/agentic_core/L2_execution/types/test_instruction_packet.py |
| REQ-023 | Replay | CRITICAL | EXECUTION_PATH | Runtime, Replay | Runtime, Replay | — | LOW | PASS | agentic_core/L2_execution/determinism/replay_guard.py |
| REQ-024 | Envelope | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L2_execution/types/sandbox_envelope_types.py, tests/agentic_core/L2_execution/types/test_sandbox_envelope.py |
| REQ-025 | Budget | CRITICAL | EXECUTION_PATH | Runtime, CI, Schema | Runtime, CI, Schema | — | LOW | PASS | tests/guardian/test_v15_p11_token_cap_enforced.py |
| REQ-026 | Tools | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L2_execution/types/instruction_packet_types.py |
| REQ-027 | Tools | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | agentic_core/L2_execution/tools/safe_subprocess.py |
| REQ-028 | Tools | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/governance/test_preventative_sandbox.py |
| REQ-029 | Mutation | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | agentic_core/L2_execution/UniversalWriteGateway.py, agentic_core/interfaces/write_gateway.py |
| REQ-030 | Mutation | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/agentic_core/L2_execution/enforcement/test_uwg_hard_block.py |
| REQ-031 | Mutation | HIGH | STRUCTURAL | AST, Runtime | AST, Runtime | — | LOW | PASS | agentic_core/L2_execution/UniversalWriteGateway.py |
| REQ-032 | Artifact | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_v15_artifact_typing_migration.py |
| REQ-033 | Artifact | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/traceability_types.py |
| REQ-034 | Artifact | CRITICAL | EXECUTION_PATH | Runtime, Replay | Runtime, Replay | — | LOW | PASS | agentic_core/L6_observability/engines/replay_key_computer.py |
| REQ-035 | Determinism | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Single-emission-per-wave not mechanically enforced across all artifact types |
| REQ-036 | Determinism | CRITICAL | EXECUTION_PATH | Replay, Runtime | Replay, Runtime | — | LOW | PASS | tests/unit_min_deps/test_deterministic_replay.py |
| REQ-037 | Determinism | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/agentic_core/L2_execution/test_deterministic_providers.py |
| REQ-038 | Healing | CRITICAL | STRUCTURAL | AST | AST | — | LOW | PASS | tests/governance/test_heal_model_routing_enabled_path.py |
| REQ-039 | Healing | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/governance/test_heal_escalation_flag_contract.py |
| REQ-040 | Healing | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | tests/governance/test_heal_policy_model_escalation_flag.py |
| REQ-041 | Healing | MEDIUM | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L2_execution/types/self_healing_trigger_types.py |
| REQ-042 | Healing | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | agentic_core/L2_execution/types/self_healing_trigger_types.py |
| REQ-043 | Healing | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/governance/test_heal_escalation_flag_contract.py |
| REQ-044 | Healing | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | tests/governance/test_heal_policy_model_escalation_flag.py |
| REQ-045 | RAG | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/system_learning/test_embedding_sovereignty.py |
| REQ-046 | RAG | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/system_learning/test_embedding_service_factory.py |
| REQ-047 | RAG | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-048 | RAG | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/system_learning/test_embedding_service_factory.py |
| REQ-049 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/change_package_impl.py, tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py |
| REQ-050 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/l4_version_store.py |
| REQ-051 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, Signature | Runtime, Signature | — | LOW | PASS | system_learning/engines/change_package_impl.py |
| REQ-052 | Meta-Learning | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | system_learning/engines/change_package_impl.py |
| REQ-053 | Meta-Learning | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-054 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/change_package_impl.py |
| REQ-055 | Meta-Learning | CRITICAL | STRUCTURAL | AST, CI | AST, CI | — | LOW | PASS | ops_scripts/ci/check_llm_sdk_imports.py |
| REQ-056 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/enforcement/dual_injection_proposal_gate.py |
| REQ-057 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/enforcement/dual_injection_proposal_gate.py |
| REQ-058 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/pipelines/meta_learning_pipeline.py |
| REQ-059 | Meta-Learning | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | system_learning/pipelines/meta_learning_pipeline.py |
| REQ-060 | Meta-Learning | CRITICAL | EXECUTION_PATH | Replay, Runtime | Replay, Runtime | — | MEDIUM | PARTIAL | Replay harness exists but no proven two-run identical digest for full pipeline |
| REQ-061 | Meta-Learning | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-062 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/pipelines/meta_learning_pipeline.py |
| REQ-063 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, Replay | Runtime, Replay | — | MEDIUM | PARTIAL | Proposer ordering deterministic; replay proof of subset determinism absent |
| REQ-064 | Meta-Learning | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-065 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/unit_min_deps/system_learning/test_replay_validator_b3.py |
| REQ-066 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/enforcement/shadow_replay_validator.py |
| REQ-067 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-068 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/unit_min_deps/system_learning/test_replay_validator_b3.py |
| REQ-069 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/unit_min_deps/system_learning/test_replay_validator_b3.py |
| REQ-070 | Meta-Learning | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-071 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, Signature | Runtime, Signature | — | MEDIUM | PARTIAL | HMAC signing present; UWG routing for intake not mechanically proven |
| REQ-072 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/l4_version_store.py |
| REQ-073 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/pipelines/approval_gates.py, tests/unit_min_deps/system_learning/test_approval_gates.py |
| REQ-074 | Meta-Learning | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-075 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_guardian_change_package_activation.py |
| REQ-076 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/change_package_impl.py |
| REQ-077 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/system_learning/test_embedding_sovereignty.py |
| REQ-078 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_guardian_change_package_activation.py |
| REQ-079 | Meta-Learning | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/l4_state_writer.py |
| REQ-080 | Guardian | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p0_compliance.py |
| REQ-081 | Guardian | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p1_compliance.py |
| REQ-082 | Guardian | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p2_compliance.py |
| REQ-083 | Guardian | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p3_compliance.py |
| REQ-084 | Guardian | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p5_compliance.py |
| REQ-085 | HIL | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | MEDIUM | PARTIAL | Schema fields declared; no test proving reviewer_sig verification at runtime |
| REQ-086 | HIL | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | MEDIUM | PARTIAL | Schema defined; L5 re-clear after MODIFY_DIFF not mechanically verified |
| REQ-087 | HIL | CRITICAL | EXECUTION_PATH | Signature, Runtime | Runtime | Signature invalidation test absent | HIGH | FAIL | No test proving old signatures invalidated after MODIFY_DIFF |
| REQ-088 | Incident | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | agentic_core/L3_orchestration/types/cognitive_diff_types.py |
| REQ-089 | Incident | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p6_compliance.py |
| REQ-090 | Vigilance | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | agentic_core/L6_observability/types/vigilance_event_types.py |
| REQ-091 | Vigilance | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Tier III freeze declared; not all 5 subsystem freezes (UWG, tokens, promotion, routing, meta-learning) independently tested |
| REQ-092 | Prompt Governance | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-093 | Prompt Governance | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/governance/test_generation_routing_enforcement.py |
| REQ-094 | Prompt Governance | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/routing_artifact_types.py |
| REQ-095 | Prompt Governance | CRITICAL | EXECUTION_PATH | AST, Replay, Runtime | AST, Runtime | Replay proof absent for sorted fragment composition | MEDIUM | PARTIAL | No replay test proving deterministic prompt composition |
| REQ-096 | Prompt Governance | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | agentic_core/L0_routing/types/governance_types.py |
| REQ-097 | Auth | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_capability_chokepoint.py |
| REQ-098 | Auth | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L2_execution/types/capability_token_types.py |
| REQ-099 | Auth | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L2_execution/enforcement/capability_chokepoint.py |
| REQ-100 | Auth | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L2_execution/enforcement/capability_chokepoint_gate.py |
| REQ-101 | Auth | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | tests/agentic_core/L2_execution/types/test_sandbox_envelope.py |
| REQ-102 | Kill-Switch | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/system_learning/test_embedding_sovereignty.py |
| REQ-103 | Kill-Switch | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/unit_min_deps/system_learning/test_approval_gates.py |
| REQ-104 | Kill-Switch | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/governance/test_heal_escalation_flag_contract.py |
| REQ-105 | Replay | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/replay/replay_envelope.py |
| REQ-106 | Replay | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Replay sandbox exists; no test proving network IO and SDK are blocked at runtime |
| REQ-107 | Replay | CRITICAL | EXECUTION_PATH | Replay, Runtime | Replay, Runtime | — | LOW | PASS | tests/governance/test_replay_integrity.py |
| REQ-108 | Replay | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/unit_min_deps/test_vllm_replay_tamper_roundtrip.py |
| REQ-109 | Replay | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/governance/test_phase11_universal_replay_lock.py |
| REQ-110 | Replay | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L4_state/types/replay_bundle_types.py |
| REQ-111 | Determinism Canon | CRITICAL | STRUCTURAL | AST, CI | AST, CI | — | MEDIUM | PARTIAL | AST scan exists; uuid4 found in 86 files incl. core modules (tracing_mixin, governance_contracts) |
| REQ-112 | Determinism Canon | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tools/canonical_hash.py |
| REQ-113 | Determinism Canon | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tools/canonical_hash.py |
| REQ-114 | Determinism Canon | CRITICAL | EXECUTION_PATH | AST, Runtime, CI | AST, Runtime | CI ratchet for wall-clock not observed | MEDIUM | PARTIAL | datetime.now found in 421 files; no CI gate specifically blocking wall-clock in determinism paths |
| REQ-115 | Determinism Canon | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/agentic_core/L3_orchestration/reasoning/test_semantic_clock_propagation.py |
| REQ-116 | Determinism Canon | CRITICAL | STRUCTURAL | CI | CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-117 | Sovereignty | CRITICAL | STRUCTURAL | AST, CI | AST, CI | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-118 | Sovereignty | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | MEDIUM | PARTIAL | AST scan for reflection exists; runtime guard for setattr on core classes not mechanically proven |
| REQ-119 | Sovereignty | CRITICAL | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-120 | Sovereignty | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | agentic_core/L2_execution/tools/safe_subprocess.py, agentic_core/L5_safety/utils/subprocess_security_util.py |
| REQ-121 | Sovereignty | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | ToolTranscript type exists; hash-binding to ExecutionTrace not verified for all subprocess calls |
| REQ-122 | Sovereignty | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/agentic_core/L2_execution/types/test_sandbox_envelope.py |
| REQ-123 | Sovereignty | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L2_execution/enforcement/SovereignLLMGateway.py |
| REQ-124 | Sovereignty | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/system_learning/test_embedding_sovereignty.py |
| REQ-125 | Sovereignty | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_l4_state_write_sovereignty.py |
| REQ-126 | Sovereignty | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | MEDIUM | PARTIAL | No config mutation without ChangePackage not fully proven; env mutation AST scan exists |
| REQ-127 | Sovereignty | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/l4_version_store.py |
| REQ-128 | Sovereignty | CRITICAL | EXECUTION_PATH | Runtime, Signature | Runtime, Signature | — | LOW | PASS | system_learning/engines/change_package_impl.py |
| REQ-129 | Sovereignty | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | MEDIUM | PARTIAL | No mutable global AST scan present; SovereigntyError hierarchy exists but halt-on-exception not proven for all paths |
| REQ-130 | Sovereignty | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/governance_types.py |
| REQ-131 | Sovereignty | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-132 | Sovereignty | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-133 | Sovereignty | CRITICAL | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-134 | Sovereignty | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | ops_scripts/ci/enforcement_audit.py |
| REQ-135 | Governance | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p0_compliance.py |
| REQ-136 | Governance | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | MEDIUM | PARTIAL | Typed schemas exist; version mismatch abort not proven for all cross-layer calls |
| REQ-137 | Governance | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | agentic_core/L0_routing/enforcement/traceability_contracts.py |
| REQ-138 | Governance | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L2_execution/determinism/replay_guard.py |
| REQ-139 | Governance | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/determinism_types.py |
| REQ-140 | Seam | CRITICAL | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-141 | Seam | HIGH | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-142 | Seam | CRITICAL | EXECUTION_PATH | AST, Runtime, Replay | AST, Runtime | Replay proof absent for seam determinism | MEDIUM | PARTIAL | Seam audit artifact exists; replay determinism not mechanically proven |
| REQ-143 | Seam | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-144 | CI | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-145 | CI | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-146 | CI | CRITICAL | STRUCTURAL | AST, CI | AST, CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-147 | CI Ratchet | CRITICAL | STRUCTURAL | CI | CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-148 | CI Ratchet | CRITICAL | EXECUTION_PATH | AST, CI, Runtime | AST, CI, Runtime | — | LOW | PASS | ops_scripts/ci/check_llm_sdk_imports.py |
| REQ-149 | CI Ratchet | CRITICAL | STRUCTURAL | AST, Schema | AST, Schema | — | LOW | PASS | tests/architecture/test_compile_time_frozen_governance.py |
| REQ-150 | CI Ratchet | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/governance/test_phase8_signature_boundary.py |
| REQ-151 | CI Ratchet | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_v15_p1_compliance.py |
| REQ-152 | CI Ratchet | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p2_compliance.py |
| REQ-153 | CI Ratchet | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_v15_p3_compliance.py |
| REQ-154 | Boundary | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/agentic_core/L2_execution/types/test_sandbox_envelope.py |
| REQ-155 | Discovery | HIGH | EXECUTION_PATH | Runtime, CI, Schema | Runtime, CI, Schema | — | LOW | PASS | artifacts/discovery/agent_discovery_full.json |
| REQ-156 | Discovery | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | ops_scripts/ci/active_set_ssot_check.py |
| REQ-157 | Trace | CRITICAL | EXECUTION_PATH | Replay, Schema, Runtime | Runtime, Schema | Replay verification of transcript_hash absent | MEDIUM | PARTIAL | Schema fields exist; no replay test verifying transcript_hash canonical order |
| REQ-158 | Trace | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay tamper detection not independently tested | MEDIUM | PARTIAL | HashChainAuditLog type exists; reorder tamper test not found |
| REQ-159 | Evidence | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/traceability_types.py |
| REQ-160 | Override | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/governance_types.py |
| REQ-161 | Surgical | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | agentic_core/L5_safety/config/structure_blueprint/ |
| REQ-162 | Surgical | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p6_compliance.py |
| REQ-163 | Capability Tokens | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L2_execution/types/capability_token_types.py |
| REQ-164 | Capability Tokens | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_capability_chokepoint.py |
| REQ-165 | Capability Tokens | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/unit_min_deps/L0_routing/test_time_shifted_consumption.py |
| REQ-166 | Side-Effect Registry | CRITICAL | EXECUTION_PATH | AST, Runtime, Schema | AST, Runtime, Schema | — | LOW | PASS | tests/guardian/test_v15_p2_compliance.py |
| REQ-167 | Side-Effect Registry | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p2_compliance.py |
| REQ-168 | Side-Effect Registry | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tests/guardian/test_v15_p2_compliance.py |
| REQ-169 | Promotion State | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/l4_version_store.py |
| REQ-170 | Promotion State | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_guardian_change_package_activation.py |
| REQ-171 | Promotion State | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-172 | Promotion State | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_guardian_change_package_activation.py |
| REQ-173 | Emergency Freeze | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L6_observability/types/vigilance_event_types.py |
| REQ-174 | Emergency Freeze | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p6_compliance.py |
| REQ-175 | Artifact Legality | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_v15_artifact_typing_migration.py |
| REQ-176 | Artifact Legality | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tests/guardian/test_v15_artifact_typing_migration.py |
| REQ-177 | Artifact Legality | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | HIGH | PARTIAL | Signature-before-use ordering not proven for all artifact consumption paths |
| REQ-178 | Sovereignty Matrix | CRITICAL | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-179 | Sovereignty Matrix | CRITICAL | EXECUTION_PATH | AST, Runtime, CI | AST, Runtime, CI | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-180 | Phase Lock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_guardian_change_package_activation.py |
| REQ-181 | Phase Lock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/governance/test_generation_routing_enforcement.py |
| REQ-182 | TraceID Canon | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L0_routing/enforcement/governance_contracts.py |
| REQ-183 | Canonical Hashing | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tools/canonical_hash.py |
| REQ-184 | Canonical Hashing | CRITICAL | EXECUTION_PATH | AST, Replay, Runtime | AST, Runtime | Replay proof absent | MEDIUM | PARTIAL | Canonical serializer exists; no replay test proving deterministic AST serializer |
| REQ-185 | Canonical Hashing | CRITICAL | EXECUTION_PATH | AST, Runtime, Schema | AST, Runtime, Schema | — | LOW | PASS | tools/canonical_hash.py |
| REQ-186 | HMAC Custody | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | MEDIUM | PARTIAL | Key loading exists; no test proving key NOT in repo via AST scan |
| REQ-187 | HMAC Custody | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/crypto_trust_types.py |
| REQ-188 | Signature Enclave | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | MEDIUM | PARTIAL | SignatureEnclave type exists (crypto_trust_types.py); no test proving ALL signing routes through enclave |
| REQ-189 | Signature Enclave | CRITICAL | EXECUTION_PATH | AST, Runtime, Replay | AST, Runtime | Replay determinism not proven for enclave | MEDIUM | PARTIAL | Enclave isolation from L2 not mechanically verified |
| REQ-190 | Signature Enclave | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/crypto_trust_types.py |
| REQ-191 | Semantic Clock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/agentic_core/L3_orchestration/reasoning/test_semantic_clock_propagation.py |
| REQ-192 | Semantic Clock | CRITICAL | EXECUTION_PATH | Runtime, Replay, Schema | Runtime, Schema | Replay proof absent | MEDIUM | PARTIAL | Canonical serialization exists; no replay test proving clock advancement determinism |
| REQ-193 | Semantic Clock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/agentic_core/L3_orchestration/reasoning/test_semantic_clock_propagation.py |
| REQ-194 | Knowledge Supervisor | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-195 | Knowledge Supervisor | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | system_learning/engines/change_package_impl.py |
| REQ-196 | Knowledge Supervisor | HIGH | EXECUTION_PATH | AST, Runtime, Schema | AST, Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-197 | Knowledge Supervisor | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/pipelines/approval_gates.py |
| REQ-198 | RAG Custody | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-199 | RAG Custody | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | MEDIUM | PARTIAL | CitationBundle type exists; no test proving final output cites CitationBundle ID |
| REQ-200 | RAG Custody | CRITICAL | STRUCTURAL | AST, Schema | AST, Schema | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-201 | RAG Custody | CRITICAL | EXECUTION_PATH | CI, Replay, Runtime | Runtime, CI | Replay proof absent | MEDIUM | PARTIAL | Retrieval determinism not replay-proven |
| REQ-202 | Guardian Meta | CRITICAL | EXECUTION_PATH | CI, Runtime | CI, Runtime | — | LOW | PASS | tests/guardian/test_guardian_meta_coverage.py |
| REQ-203 | Guardian Meta | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p5_compliance.py |
| REQ-204 | Guardian Meta | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-205 | Guardian Meta | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p0_compliance.py |
| REQ-206 | L0 Seam | CRITICAL | EXECUTION_PATH | AST, Runtime, CI | AST, Runtime, CI | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-207 | Incident Telemetry | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L6_observability/types/vigilance_event_types.py |
| REQ-208 | Incident Telemetry | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p6_compliance.py |
| REQ-209 | Incident Telemetry | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p6_compliance.py |
| REQ-210 | Cognitive Diff | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L3_orchestration/types/cognitive_diff_types.py |
| REQ-211 | Cognitive Diff | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Signed diff not independently verified for all Tier III emissions |
| REQ-212 | Cognitive Diff | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay test for diff mismatch absent | MEDIUM | PARTIAL | No test proving diff mismatch fails replay |
| REQ-213 | Boundary Snapshot | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/snapshots/snapshot_factory.py |
| REQ-214 | Boundary Snapshot | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/snapshots/snapshot_factory.py |
| REQ-215 | Boundary Snapshot | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/l4_version_store.py |
| REQ-216 | Budget Routing | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tests/agentic_core/L3_orchestration/reasoning/test_token_budget_enforcement.py |
| REQ-217 | Budget Routing | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tests/agentic_core/L3_orchestration/reasoning/test_token_budget_enforcement.py |
| REQ-218 | Budget Routing | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_v15_p11_token_cap_enforced.py |
| REQ-219 | Law Slot Handler | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_v15_p2_wave2_2_gate_tooling.py |
| REQ-220 | Law Slot Handler | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tests/guardian/test_v15_p2_compliance.py |
| REQ-221 | Law Slot Handler | CRITICAL | STRUCTURAL | AST, Schema | AST, Schema | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-222 | Law Slot Handler | CRITICAL | EXECUTION_PATH | Runtime, Replay | Runtime | Replay determinism not proven | MEDIUM | PARTIAL | No replay proof for LawSlotHandler determinism |
| REQ-223 | MRO Integrity | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_mro_integrity.py |
| REQ-224 | MRO Integrity | CRITICAL | EXECUTION_PATH | Runtime, CI, Schema | Runtime, CI, Schema | — | LOW | PASS | tests/core/test_mro_new_diamond_check.py |
| REQ-225 | MRO Integrity | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_mro_integrity.py |
| REQ-226 | MRO Integrity | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_mro_integrity.py |
| REQ-227 | Structure Blueprint | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L5_safety/config/structure_blueprint/ |
| REQ-228 | Structure Blueprint | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/unit/structure_blueprint/test_enforcement_counters.py |
| REQ-229 | Structure Blueprint | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | ops_scripts/ci/active_set_ssot_check.py |
| REQ-230 | Structure Blueprint | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L5_safety/config/structure_blueprint/ |
| REQ-231 | SSOT Enforcement | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tests/unit_min_deps/test_ssot_mutation_fence.py |
| REQ-232 | SSOT Enforcement | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tests/unit_min_deps/test_ssot_mutation_fence.py |
| REQ-233 | SSOT Enforcement | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_ssot_no_self_mutation.py |
| REQ-234 | Structural Lock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/unit/structure_blueprint/test_enforcement_counters.py |
| REQ-235 | Structural Lock | CRITICAL | STRUCTURAL | AST, Schema | AST, Schema | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-236 | Structural Lock | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | MEDIUM | PARTIAL | Blueprint hash binding declared in types; not verified in all 5 artifact types |
| REQ-237 | Structural Lock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p6_compliance.py |
| REQ-238 | Structural Lock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p6_compliance.py |
| REQ-239 | Quorum Governance | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | HIGH | PARTIAL | N-of-M signature threshold declared in types; no test proving quorum enforcement at runtime |
| REQ-240 | Quorum Governance | CRITICAL | EXECUTION_PATH | Runtime, Signature | Runtime, Signature | — | HIGH | PARTIAL | Unique identity binding not independently tested |
| REQ-241 | Rollback Integrity | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/unit_min_deps/system_learning/test_version_store.py |
| REQ-242 | Rollback Integrity | CRITICAL | EXECUTION_PATH | Replay, Schema, Runtime | Runtime, Schema | Replay test absent | MEDIUM | PARTIAL | Rollback events not replay-tested |
| REQ-243 | Audit Completeness | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | MEDIUM | PARTIAL | WaveAuditSummary type not located in codebase |
| REQ-244 | Audit Completeness | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Immutability post-seal for wave summaries not proven |
| REQ-245 | Human Override | CRITICAL | EXECUTION_PATH | Runtime, Schema, Signature | Runtime, Schema | Signature verification absent | MEDIUM | PARTIAL | TTL + reviewer_sig fields exist; auto-revoke on expiry not tested |
| REQ-246 | Human Override | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/governance_types.py |
| REQ-247 | Policy Exception | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | MEDIUM | PARTIAL | No-wildcard scope enforcement not mechanically verified |
| REQ-248 | Policy Exception | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | TTL enforcement for overrides not independently tested |
| REQ-249 | Artifact Registry | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L2_execution/cid_registry.py |
| REQ-250 | Artifact Registry | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L2_execution/cid_registry.py |
| REQ-251 | Drift Escalation | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L6_observability/types/vigilance_event_types.py |
| REQ-252 | Drift Escalation | HIGH | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | system_learning/constraints/delta_enforcer.py |
| REQ-253 | Cross-Wave Integrity | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | MEDIUM | PARTIAL | prev_wave_hash linking not independently verified |
| REQ-254 | Cross-Wave Integrity | CRITICAL | EXECUTION_PATH | Runtime, Replay | Runtime | Replay test absent | MEDIUM | PARTIAL | Hash chain replay test for cross-wave not found |
| REQ-255 | Governance | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p0_compliance.py |
| REQ-256 | Governance | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | MEDIUM | PARTIAL | Typed schemas exist; version mismatch abort not proven for all cross-layer calls |
| REQ-257 | Governance | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | agentic_core/L0_routing/enforcement/traceability_contracts.py |
| REQ-258 | Governance | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L2_execution/determinism/replay_guard.py |
| REQ-259 | Governance | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/determinism_types.py |
| REQ-260 | Governance | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/l4_version_store.py |
| REQ-261 | Governance | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/boundary_types.py |
| REQ-262 | Governance | CRITICAL | EXECUTION_PATH | Runtime, Replay | Runtime | Replay proof absent | MEDIUM | PARTIAL | Governance enforcement determinism not replay-proven |
| REQ-263 | Governance | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-264 | Governance | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/governance_types.py |
| REQ-265 | Seam | CRITICAL | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-266 | Seam | HIGH | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-267 | Seam | CRITICAL | EXECUTION_PATH | AST, Runtime, Replay | AST, Runtime | Replay absent | MEDIUM | PARTIAL | Seam determinism not replay-proven |
| REQ-268 | Seam | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-269 | Seam | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/governance_types.py |
| REQ-270 | Seam | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | MEDIUM | PARTIAL | No mutable reference passing across layer boundary not independently tested |
| REQ-271 | Seam | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-272 | Seam | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L6_observability/types/vigilance_event_types.py |
| REQ-273 | Seam | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay absent | MEDIUM | PARTIAL | Seam modules not replay-tested |
| REQ-274 | Seam | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | agentic_core/L0_routing/enforcement/execution_gateway.py |
| REQ-275 | CI | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-276 | CI | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-277 | CI | CRITICAL | STRUCTURAL | AST, CI | AST, CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-278 | CI Ratchet | CRITICAL | STRUCTURAL | CI | CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-279 | CI Ratchet | CRITICAL | EXECUTION_PATH | AST, CI, Runtime | AST, CI, Runtime | — | LOW | PASS | ops_scripts/ci/check_llm_sdk_imports.py |
| REQ-280 | CI Ratchet | CRITICAL | STRUCTURAL | AST, Schema | AST, Schema | — | LOW | PASS | tests/architecture/test_compile_time_frozen_governance.py |
| REQ-281 | CI Ratchet | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/governance/test_phase8_signature_boundary.py |
| REQ-282 | CI Ratchet | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_v15_p1_compliance.py |
| REQ-283 | CI Ratchet | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p2_compliance.py |
| REQ-284 | CI Ratchet | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_v15_p3_compliance.py |
| REQ-285 | CI Ratchet | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-286 | CI Ratchet | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-287 | CI Ratchet | CRITICAL | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-288 | CI Ratchet | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-289 | CI Ratchet | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay absent | MEDIUM | PARTIAL | CI pipeline determinism not replay-proven |
| REQ-290 | CI Ratchet | HIGH | STRUCTURAL | CI, Schema | CI, Schema | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-291 | CI Ratchet | CRITICAL | STRUCTURAL | AST, CI | AST, CI | — | LOW | PASS | ops_scripts/ci/ |
| REQ-292 | CI Ratchet | HIGH | STRUCTURAL | CI, Schema | CI, Schema | — | LOW | PASS | ops_scripts/ci/enforcement_audit.py |
| REQ-293 | CI Ratchet | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | ops_scripts/ci/enforcement_audit.py |
| REQ-294 | CI Ratchet | CRITICAL | EXECUTION_PATH | Runtime, CI, Schema | Runtime, CI, Schema | — | LOW | PASS | tests/guardian/test_v15_p0_compliance.py |
| REQ-295 | Boundary | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/agentic_core/L2_execution/types/test_sandbox_envelope.py |
| REQ-296 | Discovery | HIGH | EXECUTION_PATH | Runtime, CI, Schema | Runtime, CI, Schema | — | LOW | PASS | artifacts/discovery/agent_discovery_full.json |
| REQ-297 | Discovery | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | ops_scripts/ci/active_set_ssot_check.py |
| REQ-298 | Discovery | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay absent | MEDIUM | PARTIAL | Discovery determinism not replay-proven |
| REQ-299 | Discovery | HIGH | STRUCTURAL | AST, CI | AST, CI | — | LOW | PASS | ops_scripts/ci/active_set_snapshot_check.py |
| REQ-300 | Discovery | HIGH | STRUCTURAL | CI, Schema | CI, Schema | — | LOW | PASS | artifacts/discovery/agent_discovery_full.json |
| REQ-301 | Discovery | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | ops_scripts/ci/active_set_ssot_check.py |
| REQ-302 | Trace | CRITICAL | EXECUTION_PATH | Replay, Schema, Runtime | Runtime, Schema | Replay absent | MEDIUM | PARTIAL | Duplicate of REQ-157 pattern; transcript_hash replay not verified |
| REQ-303 | Trace | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay absent | MEDIUM | PARTIAL | Duplicate of REQ-158 pattern; tamper detection replay absent |
| REQ-304 | Trace | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L0_routing/enforcement/traceability_contracts.py |
| REQ-305 | Trace | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/traceability_types.py |
| REQ-306 | Evidence | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/traceability_types.py |
| REQ-307 | Evidence | CRITICAL | EXECUTION_PATH | Replay, Schema, Runtime | Runtime, Schema | Replay absent | MEDIUM | PARTIAL | Evidence replay verification absent |
| REQ-308 | Evidence | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | MEDIUM | PARTIAL | ToolTranscript hash-binding to ExecutionTrace not verified for all paths |
| REQ-309 | Evidence | HIGH | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-310 | Override | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/governance_types.py |
| REQ-311 | Surgical | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | agentic_core/L5_safety/config/structure_blueprint/ |
| REQ-312 | Surgical | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p6_compliance.py |
| REQ-313 | Surgical | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay absent | MEDIUM | PARTIAL | Surgical edit determinism not replay-proven |
| REQ-314 | Surgical | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L5_safety/config/structure_blueprint/ |
| REQ-315 | SSOT | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tests/unit_min_deps/test_ssot_mutation_fence.py |
| REQ-316 | SSOT | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tests/unit_min_deps/test_ssot_mutation_fence.py |
| REQ-317 | SSOT | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_ssot_no_self_mutation.py |
| REQ-318 | SSOT | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-319 | SSOT | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_ssot_no_self_mutation.py |
| REQ-320 | SSOT | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay absent | MEDIUM | PARTIAL | SSOT serialization determinism not replay-proven |
| REQ-321 | SSOT | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p6_compliance.py |
| REQ-322 | SSOT | CRITICAL | STRUCTURAL | CI, Schema | CI, Schema | — | LOW | PASS | tests/architecture/test_compile_time_frozen_governance.py |
| REQ-323 | Side-Effect Registry | CRITICAL | EXECUTION_PATH | AST, Runtime, Schema | AST, Runtime, Schema | — | LOW | PASS | tests/guardian/test_v15_p2_compliance.py |
| REQ-324 | Side-Effect Registry | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p2_compliance.py |
| REQ-325 | Side-Effect Registry | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tests/guardian/test_v15_p2_compliance.py |
| REQ-326 | Side-Effect Registry | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tests/guardian/test_v15_p2_compliance.py |
| REQ-327 | Side-Effect Registry | CRITICAL | EXECUTION_PATH | Runtime, Replay | Runtime | Replay absent | MEDIUM | PARTIAL | Observed vs declared comparison determinism not replay-proven |
| REQ-328 | Side-Effect Registry | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/engines/l4_version_store.py |
| REQ-329 | Side-Effect Registry | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p2_compliance.py |
| REQ-330 | Side-Effect Registry | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | system_learning/pipelines/approval_gates.py |
| REQ-331 | Side-Effect Registry | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay absent | MEDIUM | PARTIAL | Registry query determinism not replay-proven |
| REQ-332 | Side-Effect Registry | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/enforcement/traceability_contracts.py |
| REQ-333 | Promotion State | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/l4_version_store.py |
| REQ-334 | Promotion State | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_guardian_change_package_activation.py |
| REQ-335 | Promotion State | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-336 | Promotion State | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_guardian_change_package_activation.py |
| REQ-337 | Promotion State | CRITICAL | EXECUTION_PATH | Runtime, Replay | Runtime | Replay absent | MEDIUM | PARTIAL | Promotion decision determinism not replay-proven |
| REQ-338 | Promotion State | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-339 | Promotion State | CRITICAL | EXECUTION_PATH | Runtime, Guardian | Runtime, Guardian | — | LOW | PASS | tests/guardian/test_guardian_change_package_activation.py |
| REQ-340 | Promotion State | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-341 | Promotion State | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/l4_version_store.py |
| REQ-342 | Promotion State | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-343 | Emergency Freeze | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L6_observability/types/vigilance_event_types.py |
| REQ-344 | Emergency Freeze | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p6_compliance.py |
| REQ-345 | Emergency Freeze | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | WriteGateway disable on freeze not independently tested |
| REQ-346 | Emergency Freeze | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Promotion halt on freeze not independently tested |
| REQ-347 | Emergency Freeze | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Routing block on freeze not independently tested |
| REQ-348 | Emergency Freeze | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Freeze persistence in L4 across restart not tested |
| REQ-349 | Emergency Freeze | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | All-or-nothing freeze invariant not independently tested |
| REQ-350 | Emergency Freeze | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L6_observability/types/vigilance_event_types.py |
| REQ-351 | Emergency Freeze | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L6_observability/types/vigilance_event_types.py |
| REQ-352 | Artifact Legality | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_v15_artifact_typing_migration.py |
| REQ-353 | Artifact Legality | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tests/guardian/test_v15_artifact_typing_migration.py |
| REQ-354 | Artifact Legality | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | HIGH | PARTIAL | Signature-before-use ordering not mechanically proven for all artifact paths |
| REQ-355 | Artifact Legality | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | agentic_core/L2_execution/cid_registry.py |
| REQ-356 | Artifact Legality | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tests/guardian/test_v15_artifact_typing_migration.py |
| REQ-357 | Artifact Legality | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_artifact_typing_migration.py |
| REQ-358 | Artifact Legality | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L6_observability/types/vigilance_event_types.py |
| REQ-359 | Artifact Legality | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/determinism_types.py |
| REQ-360 | Artifact Legality | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay absent | MEDIUM | PARTIAL | Artifact legality determinism not replay-proven |
| REQ-361 | Sovereignty Matrix | CRITICAL | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-362 | Sovereignty Matrix | CRITICAL | EXECUTION_PATH | AST, Runtime, CI | AST, Runtime, CI | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-363 | Sovereignty Matrix | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-364 | Sovereignty Matrix | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/l4_version_store.py |
| REQ-365 | Sovereignty Matrix | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | No dynamic capability acquisition invariant not independently tested |
| REQ-366 | Sovereignty Matrix | CRITICAL | STRUCTURAL | AST | AST | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-367 | Sovereignty Matrix | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p0_compliance.py |
| REQ-368 | Sovereignty Matrix | HIGH | STRUCTURAL | AST, Schema | AST, Schema | — | LOW | PASS | tests/architecture/test_invariants.py |
| REQ-369 | Sovereignty Matrix | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/enforcement/traceability_contracts.py |
| REQ-370 | Sovereignty Matrix | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | .github/workflows/guardian-tests.yml |
| REQ-371 | Phase Lock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_guardian_change_package_activation.py |
| REQ-372 | Phase Lock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/governance/test_generation_routing_enforcement.py |
| REQ-373 | Phase Lock | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | system_learning/types/meta_learning_types.py |
| REQ-374 | Phase Lock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | system_learning/engines/l4_version_store.py |
| REQ-375 | Phase Lock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Phase lock persistence across restart not independently tested |
| REQ-376 | TraceID Canon | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L0_routing/enforcement/governance_contracts.py |
| REQ-377 | TraceID Canon | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L0_routing/enforcement/governance_contracts.py |
| REQ-378 | TraceID Canon | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay absent | MEDIUM | PARTIAL | TraceID generation determinism not replay-proven |
| REQ-379 | TraceID Canon | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L0_routing/enforcement/governance_contracts.py |
| REQ-380 | Canonical Hashing | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tools/canonical_hash.py |
| REQ-381 | Canonical Hashing | CRITICAL | EXECUTION_PATH | AST, Replay, Runtime | AST, Runtime | Replay absent | MEDIUM | PARTIAL | Deterministic AST serializer not replay-proven |
| REQ-382 | Canonical Hashing | CRITICAL | EXECUTION_PATH | AST, Runtime, Schema | AST, Runtime, Schema | — | LOW | PASS | tools/canonical_hash.py |
| REQ-383 | Canonical Hashing | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | LOW | PASS | tools/canonical_hash.py |
| REQ-384 | Canonical Hashing | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay absent | MEDIUM | PARTIAL | Hash computation determinism not independently replay-proven |
| REQ-385 | Canonical Hashing | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tools/canonical_hash.py |
| REQ-386 | Canonical Hashing | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/guardian/test_v15_p6_compliance.py |
| REQ-387 | Canonical Hashing | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tools/canonical_hash.py |
| REQ-388 | Canonical Hashing | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | tools/canonical_hash.py |
| REQ-389 | Canonical Hashing | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/traceability_types.py |
| REQ-390 | HMAC Custody | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | MEDIUM | PARTIAL | Key NOT in repo not mechanically verified via AST scan |
| REQ-391 | HMAC Custody | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/crypto_trust_types.py |
| REQ-392 | HMAC Custody | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Key rotation atomicity not independently tested |
| REQ-393 | HMAC Custody | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | MEDIUM | PARTIAL | Key scope limiting not independently tested |
| REQ-394 | HMAC Custody | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/crypto_trust_types.py |
| REQ-395 | HMAC Custody | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay absent | MEDIUM | PARTIAL | HMAC determinism not replay-proven |
| REQ-396 | HMAC Custody | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Expired key rejection no-grace-period not independently tested |
| REQ-397 | HMAC Custody | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/crypto_trust_types.py |
| REQ-398 | Signature Enclave | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | MEDIUM | PARTIAL | All signing through enclave not proven; 5 files reference SignatureEnclave |
| REQ-399 | Signature Enclave | CRITICAL | EXECUTION_PATH | AST, Runtime, Replay | AST, Runtime | Replay absent | MEDIUM | PARTIAL | Enclave determinism not replay-proven |
| REQ-400 | Signature Enclave | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/crypto_trust_types.py |
| REQ-401 | Signature Enclave | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | agentic_core/L0_routing/types/crypto_trust_types.py |
| REQ-402 | Signature Enclave | HIGH | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/crypto_trust_types.py |
| REQ-403 | Signature Enclave | CRITICAL | EXECUTION_PATH | AST, Runtime | AST, Runtime | — | HIGH | PARTIAL | Enclave process isolation from L2 not mechanically verified |
| REQ-404 | Signature Enclave | CRITICAL | EXECUTION_PATH | Replay, Runtime | Runtime | Replay absent | MEDIUM | PARTIAL | Batch signing determinism not replay-proven |
| REQ-405 | Signature Enclave | HIGH | EXECUTION_PATH | Runtime | Runtime | — | LOW | PASS | agentic_core/L0_routing/types/crypto_trust_types.py |
| REQ-406 | Signature Enclave | CRITICAL | EXECUTION_PATH | Runtime, Schema | Runtime, Schema | — | LOW | PASS | agentic_core/L0_routing/types/crypto_trust_types.py |
| REQ-407 | Signature Enclave | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Startup key integrity verification not independently tested |
| REQ-408 | Semantic Clock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/agentic_core/L3_orchestration/reasoning/test_semantic_clock_propagation.py |
| REQ-409 | Semantic Clock | CRITICAL | EXECUTION_PATH | Runtime, Replay, Schema | Runtime, Schema | Replay absent | MEDIUM | PARTIAL | Clock advancement determinism not replay-proven |
| REQ-410 | Semantic Clock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/agentic_core/L3_orchestration/reasoning/test_semantic_clock_propagation.py |
| REQ-411 | Semantic Clock | CRITICAL | EXECUTION_PATH | AST, Runtime, CI | AST, Runtime | CI wall-clock scan absent | MEDIUM | PARTIAL | No CI gate specifically blocking wall-clock in determinism paths alongside clock |
| REQ-412 | Semantic Clock | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | tests/agentic_core/L3_orchestration/reasoning/test_semantic_clock_propagation.py |
| REQ-413 | Provider Binding Determinism | CRITICAL | EXECUTION_PATH | Runtime, CI, Replay | Runtime, CI | Replay absent | MEDIUM | PARTIAL | Digest includes provider metadata; replay proof with provider binding absent |
| REQ-414 | Network Egress Guard | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | HIGH | PARTIAL | Runtime egress filter at L2 boundary not proven; raw HTTP found in apps (requests.get/post) |
| REQ-415 | Provider Substitution Prohibition | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | MEDIUM | PARTIAL | Fail-closed on provider failure not independently tested with negative control |
| REQ-416 | CRITICAL Dual Enforcement Guarantee | CRITICAL | EXECUTION_PATH | Runtime, CI | Runtime, CI | — | LOW | PASS | ops_scripts/ci/enforcement_audit.py (0 audit failures) |
| REQ-417 | Dynamic Runtime Mutation Prohibition | CRITICAL | EXECUTION_PATH | AST, Runtime, CI | AST, Runtime | Runtime guard at module load absent | HIGH | PARTIAL | AST scan exists; setattr/monkeypatch found in 188 files; runtime guard at module load/class definition not mechanically proven |

---

## SECTION B — ENFORCEMENT COVERAGE MATRIX

| Enforcement Type | Present Count | Missing Count |
|------------------|--------------|---------------|
| Runtime          | 392          | 25            |
| AST / Static     | 112          | 0             |
| CI Ratchet       | 246          | 8             |
| Replay           | 13           | 24            |
| Signature        | 6            | 4             |
| Schema           | 102          | 0             |
| Guardian         | 1            | 0             |

---

## SECTION C — CRITICAL FAILURES

| REQ_ID | Violation Type | Missing Enforcement | Evidence |
|--------|----------------|---------------------|----------|
| REQ-087 | Signature invalidation absent | No test proving old signatures invalidated after MODIFY_DIFF | No test file found for MODIFY_DIFF invalidation |

---

## SECTION D — BYPASS EXPOSURE SUMMARY

- **Gateway bypass exposures: 3** — SDK imports found in apps_rg/reasoning/HardenedopenaiexecutorStrategy.py, apps_rg/tools/ResumeGenerator.py, apps_rg/utils/providers_anthropic_client_util.py (REQ-011, REQ-012)
- **Egress violations: 5** — Raw HTTP (requests.get/post, httpx) found in apps code and ops_scripts outside SovereignLLMGateway; localhost egress not gated (REQ-414)
- **UWG bypass exposures: 0** — No direct FS/DB/vector writes found outside UWG in core layers
- **Runtime mutation exposures: HIGH** — setattr/monkeypatch found in 188 files (mostly tests, but core modules include instruction_packet.py, sandbox_envelope.py); importlib.reload in 10 files (REQ-417)
- **Determinism violations: 2** — uuid4 in core modules (tracing_mixin.py, governance_contracts.py) (REQ-111); datetime.now pervasive (REQ-114)
- **Signature-after-side-effect violations: UNVERIFIED** — No mechanical proof that signature verification precedes side-effects in all consumption paths (REQ-019, REQ-177, REQ-354)
- **Replay bypass exposures: 24** — 24 requirements declare Replay as enforcement layer but no replay test proving the specific invariant (REQ-060, REQ-063, REQ-095, REQ-142, REQ-157, REQ-158, REQ-184, REQ-192, REQ-201, REQ-212, REQ-222, REQ-242, REQ-254, REQ-262, REQ-267, REQ-273, REQ-289, REQ-298, REQ-302, REQ-303, REQ-307, REQ-313, REQ-320, REQ-327, REQ-331, REQ-337, REQ-360, REQ-378, REQ-381, REQ-384, REQ-395, REQ-399, REQ-404, REQ-409, REQ-413)

---

## SECTION E — COMPLIANCE METRICS

- **Total PASS:** 348
- **Total PARTIAL:** 68
- **Total FAIL:** 1
- **% PASS:** 83.5%
- **% FAIL:** 0.2%
- **CRITICAL FAIL count:** 1
- **CRITICAL PARTIAL count:** 56

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

