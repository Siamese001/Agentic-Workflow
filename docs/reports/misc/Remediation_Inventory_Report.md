# Remediation Inventory Report

## Phase 1: Resolution Asymmetry Landmines

**Total Agents with Landmines:** 27

**Total Landmines Found:** 79


### Summary Table

| Agent Name | Landmine Found | Remediation Status | Test Pass Rate |
| :--- | :--- | :--- | :--- |
| `ASTValidatorAgent` | Resolution Asymmetry (6) | PENDING | 0% |
| `AgentCategory` | Resolution Asymmetry (5) | PENDING | 0% |
| `AgentPermission` | Resolution Asymmetry (1) | PENDING | 0% |
| `ArchitectureGovernorAgent` | Resolution Asymmetry (3) | PENDING | 0% |
| `AutonomousThreatEvolutionAgent` | Resolution Asymmetry (1) | PENDING | 0% |
| `AutonomyGuardianAgent` | Resolution Asymmetry (3) | PENDING | 0% |
| `CheckpointManagerAgent` | Resolution Asymmetry (1) | PENDING | 0% |
| `CodeDeduplicationAgent` | Resolution Asymmetry (2) | PENDING | 0% |
| `CodeHealerAgent` | Resolution Asymmetry (12) | PENDING | 0% |
| `CompositeGuardrailAgent` | Resolution Asymmetry (8) | PENDING | 0% |
| `CredentialScannerAgent` | Resolution Asymmetry (1) | PENDING | 0% |
| `FileClassificationAgent` | Resolution Asymmetry (3) | PENDING | 0% |
| `FilesystemSSOTReconcilerAgent` | Resolution Asymmetry (6) | PENDING | 0% |
| `GovernanceAgent` | Resolution Asymmetry (3) | PENDING | 0% |
| `HierarchyAgent` | Resolution Asymmetry (3) | PENDING | 0% |
| `MCPGuardianAgent` | Resolution Asymmetry (1) | PENDING | 0% |
| `NamingAgent` | Resolution Asymmetry (1) | PENDING | 0% |
| `NervousSystemAgent` | Resolution Asymmetry (1) | PENDING | 0% |
| `PineconeSovereignAgent` | Resolution Asymmetry (2) | PENDING | 0% |
| `PreCommitSovereignAgent` | Resolution Asymmetry (1) | PENDING | 0% |
| `ReportLocationAgent` | Resolution Asymmetry (1) | PENDING | 0% |
| `RootHygieneAgent` | Resolution Asymmetry (1) | PENDING | 0% |
| `StructureHealerAgent` | Resolution Asymmetry (6) | PENDING | 0% |
| `SubAtomicRegistryAgent` | Resolution Asymmetry (1) | PENDING | 0% |
| `SystemArchitectAgent` | Resolution Asymmetry (1) | PENDING | 0% |
| `ValidationOrchestratorAgent` | Resolution Asymmetry (1) | PENDING | 0% |
| `input_validation_guardrail_agent_config` | Resolution Asymmetry (4) | PENDING | 0% |

### Detailed Findings


#### ASTValidatorAgent

- **File Path:** `agentic_core\L1_cognition\thought_engine\ast_validator_agent_validator.py`
- **Line:** 175
- **Detection Method:** validate_bare_except
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns list[dict[str, Any]], healer uses unstructured params

#### ASTValidatorAgent

- **File Path:** `agentic_core\L1_cognition\thought_engine\ast_validator_agent_validator.py`
- **Line:** 175
- **Detection Method:** validate_empty_except
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns list[dict[str, Any]], healer uses unstructured params

#### ASTValidatorAgent

- **File Path:** `agentic_core\L1_cognition\thought_engine\ast_validator_agent_validator.py`
- **Line:** 175
- **Detection Method:** validate_eval_exec
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns list[dict[str, Any]], healer uses unstructured params

#### ASTValidatorAgent

- **File Path:** `agentic_core\L1_cognition\thought_engine\ast_validator_agent_validator.py`
- **Line:** 175
- **Detection Method:** validate_dangerous_builtins
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns list[dict[str, Any]], healer uses unstructured params

#### ASTValidatorAgent

- **File Path:** `agentic_core\L1_cognition\thought_engine\ast_validator_agent_validator.py`
- **Line:** 175
- **Detection Method:** validate_debugger
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns list[dict[str, Any]], healer uses unstructured params

#### ASTValidatorAgent

- **File Path:** `agentic_core\L1_cognition\thought_engine\ast_validator_agent_validator.py`
- **Line:** 175
- **Detection Method:** validate_all
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, list[dict[str, Any]]], healer uses unstructured params

#### AgentCategory

- **File Path:** `agentic_core\base_agents\UnifiedAgent.py`
- **Line:** 123
- **Detection Method:** _scan_violations
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns List[Dict[str, Any]], healer uses unstructured params

#### AgentCategory

- **File Path:** `agentic_core\base_agents\UnifiedAgent.py`
- **Line:** 430
- **Detection Method:** _scan_violations
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns List[Dict[str, Any]], healer uses unstructured params

#### AgentCategory

- **File Path:** `agentic_core\base_agents\UnifiedAgent.py`
- **Line:** 523
- **Detection Method:** _scan_violations
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns List[Dict[str, Any]], healer uses unstructured params

#### AgentCategory

- **File Path:** `agentic_core\base_agents\UnifiedAgent.py`
- **Line:** 688
- **Detection Method:** _scan_violations
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns List[Dict[str, Any]], healer uses unstructured params

#### AgentCategory

- **File Path:** `agentic_core\base_agents\UnifiedAgent.py`
- **Line:** 801
- **Detection Method:** _scan_violations
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns List[Dict[str, Any]], healer uses unstructured params

#### AgentPermission

- **File Path:** `agentic_core\L5_safety\policy_engine\security_manager_agent_types.py`
- **Line:** 126
- **Detection Method:** restore_checkpoint
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any] | None, healer uses unstructured params

#### ArchitectureGovernorAgent

- **File Path:** `agentic_core\L5_safety\validators\ArchitectureGovernorAgent.py`
- **Line:** 250
- **Detection Method:** _orchestrate_guardian_scan
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### ArchitectureGovernorAgent

- **File Path:** `agentic_core\L5_safety\validators\ArchitectureGovernorAgent.py`
- **Line:** 250
- **Detection Method:** validate_architectural_patterns
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### ArchitectureGovernorAgent

- **File Path:** `agentic_core\L5_safety\validators\ArchitectureGovernorAgent.py`
- **Line:** 250
- **Detection Method:** _check_baseline_drift
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns list[dict[str, Any]], healer uses unstructured params

#### AutonomousThreatEvolutionAgent

- **File Path:** `agentic_core\L5_safety\guardrails\autonomous_threat_evolution_agent.py`
- **Line:** 104
- **Detection Method:** _load_recent_detections
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns list[dict], healer uses unstructured params

#### AutonomyGuardianAgent

- **File Path:** `agentic_core\L5_safety\validators\autonomy_guardian_agent.py`
- **Line:** 244
- **Healing Method:** heal_repository
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: replace

#### AutonomyGuardianAgent

- **File Path:** `agentic_core\L5_safety\validators\autonomy_guardian_agent.py`
- **Line:** 244
- **Healing Method:** heal_repository
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: split

#### AutonomyGuardianAgent

- **File Path:** `agentic_core\L5_safety\validators\autonomy_guardian_agent.py`
- **Line:** 244
- **Healing Method:** heal_repository
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: join

#### CheckpointManagerAgent

- **File Path:** `agentic_core\L4_state\validation_context\checkpoint_manager_agent.py`
- **Line:** 719
- **Detection Method:** list_checkpoints
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns list[dict[str, Any]], healer uses unstructured params

#### CodeDeduplicationAgent

- **File Path:** `agentic_core\L5_safety\validators\code_deduplication_agent.py`
- **Line:** 707
- **Detection Method:** detect_dead_code
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### CodeDeduplicationAgent

- **File Path:** `agentic_core\L5_safety\validators\code_deduplication_agent.py`
- **Line:** 707
- **Detection Method:** scan_dead_code
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### CodeHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\code_healer_agent.py`
- **Line:** 275
- **Healing Method:** heal_imports
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: split

#### CodeHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\code_healer_agent.py`
- **Line:** 275
- **Healing Method:** heal_imports
- **Asymmetry Type:** String-based Operations
- **Evidence:** Direct file I/O with path string

#### CodeHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\code_healer_agent.py`
- **Line:** 275
- **Healing Method:** heal_imports
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: join

#### CodeHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\code_healer_agent.py`
- **Line:** 275
- **Healing Method:** heal_imports
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: split

#### CodeHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\code_healer_agent.py`
- **Line:** 349
- **Healing Method:** heal_canon
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: split

#### CodeHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\code_healer_agent.py`
- **Line:** 349
- **Healing Method:** heal_canon
- **Asymmetry Type:** String-based Operations
- **Evidence:** Direct file I/O with path string

#### CodeHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\code_healer_agent.py`
- **Line:** 349
- **Healing Method:** heal_canon
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: join

#### CodeHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\code_healer_agent.py`
- **Line:** 349
- **Healing Method:** heal_canon
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: replace

#### CodeHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\code_healer_agent.py`
- **Line:** 349
- **Healing Method:** heal_canon
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: replace

#### CodeHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\code_healer_agent.py`
- **Line:** 409
- **Healing Method:** heal_structural
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: split

#### CodeHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\code_healer_agent.py`
- **Line:** 409
- **Healing Method:** heal_structural
- **Asymmetry Type:** String-based Operations
- **Evidence:** Direct file I/O with path string

#### CodeHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\code_healer_agent.py`
- **Line:** 409
- **Healing Method:** heal_structural
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: join

#### CompositeGuardrailAgent

- **File Path:** `agentic_core\L5_safety\validators\composite_guardrail_agent_types.py`
- **Line:** 394
- **Detection Method:** check
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### CompositeGuardrailAgent

- **File Path:** `agentic_core\L5_safety\validators\composite_guardrail_agent_types.py`
- **Line:** 394
- **Detection Method:** check
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### CompositeGuardrailAgent

- **File Path:** `agentic_core\L5_safety\validators\composite_guardrail_agent_types.py`
- **Line:** 394
- **Detection Method:** check
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### CompositeGuardrailAgent

- **File Path:** `agentic_core\L5_safety\validators\composite_guardrail_agent_types.py`
- **Line:** 394
- **Detection Method:** check
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### CompositeGuardrailAgent

- **File Path:** `agentic_core\L5_safety\validators\composite_guardrail_agent_types.py`
- **Line:** 394
- **Detection Method:** check
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### CompositeGuardrailAgent

- **File Path:** `agentic_core\L5_safety\validators\composite_guardrail_agent_types.py`
- **Line:** 394
- **Detection Method:** check
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### CompositeGuardrailAgent

- **File Path:** `agentic_core\L5_safety\validators\composite_guardrail_agent_types.py`
- **Line:** 394
- **Detection Method:** check
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### CompositeGuardrailAgent

- **File Path:** `agentic_core\L5_safety\validators\composite_guardrail_agent_types.py`
- **Line:** 394
- **Detection Method:** check
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### CredentialScannerAgent

- **File Path:** `agentic_core\L5_safety\validators\credential_scanner_agent_types.py`
- **Line:** 397
- **Detection Method:** scan_for_credentials
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### FileClassificationAgent

- **File Path:** `agentic_core\L5_safety\validators\FileClassificationAgent.py`
- **Line:** 1443
- **Detection Method:** _detect_test_patterns
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, bool], healer uses unstructured params

#### FileClassificationAgent

- **File Path:** `agentic_core\L5_safety\validators\FileClassificationAgent.py`
- **Line:** 1443
- **Detection Method:** _detect_script_patterns
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, bool], healer uses unstructured params

#### FileClassificationAgent

- **File Path:** `agentic_core\L5_safety\validators\FileClassificationAgent.py`
- **Line:** 1443
- **Detection Method:** _detect_type_patterns
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, bool], healer uses unstructured params

#### FilesystemSSOTReconcilerAgent

- **File Path:** `agentic_core\L5_safety\validators\FilesystemSSOTReconcilerAgent.py`
- **Line:** 112
- **Detection Method:** _detect_drift
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns list[dict[str, Any]], healer uses unstructured params

#### FilesystemSSOTReconcilerAgent

- **File Path:** `agentic_core\L5_safety\validators\FilesystemSSOTReconcilerAgent.py`
- **Line:** 112
- **Detection Method:** detect_root_drift
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### FilesystemSSOTReconcilerAgent

- **File Path:** `agentic_core\L5_safety\validators\FilesystemSSOTReconcilerAgent.py`
- **Line:** 112
- **Detection Method:** scan_root_folders
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### FilesystemSSOTReconcilerAgent

- **File Path:** `agentic_core\L5_safety\validators\FilesystemSSOTReconcilerAgent.py`
- **Line:** 1338
- **Detection Method:** _detect_drift
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns list[dict[str, Any]], healer uses unstructured params

#### FilesystemSSOTReconcilerAgent

- **File Path:** `agentic_core\L5_safety\validators\FilesystemSSOTReconcilerAgent.py`
- **Line:** 1338
- **Detection Method:** detect_root_drift
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### FilesystemSSOTReconcilerAgent

- **File Path:** `agentic_core\L5_safety\validators\FilesystemSSOTReconcilerAgent.py`
- **Line:** 1338
- **Detection Method:** scan_root_folders
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### GovernanceAgent

- **File Path:** `agentic_core\L5_safety\validators\GovernanceAgent.py`
- **Line:** 1007
- **Detection Method:** _check_nesting_depth
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns list[dict[str, Any]], healer uses unstructured params

#### GovernanceAgent

- **File Path:** `agentic_core\L5_safety\validators\GovernanceAgent.py`
- **Line:** 1007
- **Detection Method:** check_complexity
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns list[dict[str, Any]], healer uses unstructured params

#### GovernanceAgent

- **File Path:** `agentic_core\L5_safety\validators\GovernanceAgent.py`
- **Line:** 1007
- **Detection Method:** validate_architecture
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### HierarchyAgent

- **File Path:** `agentic_core\L5_safety\validators\HierarchyagentStrategy.py`
- **Line:** 1132
- **Detection Method:** scan_root_violations
- **Healing Method:** heal_hierarchy
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### HierarchyAgent

- **File Path:** `agentic_core\L5_safety\validators\HierarchyagentStrategy.py`
- **Line:** 1255
- **Detection Method:** scan_root_violations
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### HierarchyAgent

- **File Path:** `agentic_core\L5_safety\validators\HierarchyagentStrategy.py`
- **Line:** 1459
- **Detection Method:** scan_root_violations
- **Healing Method:** heal_root_violations
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### MCPGuardianAgent

- **File Path:** `agentic_core\L5_safety\validators\MCPGuardianAgent.py`
- **Line:** 288
- **Detection Method:** scan_codebase
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### NamingAgent

- **File Path:** `agentic_core\L5_safety\validators\naming_agent_validator.py`
- **Line:** 60
- **Detection Method:** scan_repository_duplicates
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict, healer uses unstructured params

#### NervousSystemAgent

- **File Path:** `agentic_core\L3_orchestration\workflow_engines\nervous_system_agent.py`
- **Line:** 800
- **Detection Method:** validate_architecture
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### PineconeSovereignAgent

- **File Path:** `agentic_core\L5_safety\validators\pinecone_sovereign_agent.py`
- **Line:** 481
- **Detection Method:** health_check
- **Healing Method:** health_check
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict, healer uses unstructured params

#### PineconeSovereignAgent

- **File Path:** `agentic_core\L5_safety\validators\pinecone_sovereign_agent.py`
- **Line:** 525
- **Detection Method:** health_check
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict, healer uses unstructured params

#### PreCommitSovereignAgent

- **File Path:** `agentic_core\L5_safety\validators\pre_commit_sovereign_agent.py`
- **Line:** 81
- **Detection Method:** validate_staged_files
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### ReportLocationAgent

- **File Path:** `agentic_core\L5_safety\validators\ReportLocationAgent.py`
- **Line:** 239
- **Detection Method:** validate
- **Healing Method:** heal
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### RootHygieneAgent

- **File Path:** `agentic_core\L5_safety\validators\root_hygiene_agent.py`
- **Line:** 291
- **Detection Method:** scan_root_violations
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### StructureHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\structure_healer_agent_types.py`
- **Line:** 181
- **Healing Method:** heal_naming
- **Asymmetry Type:** String-based Operations
- **Evidence:** Direct file I/O with path string

#### StructureHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\structure_healer_agent_types.py`
- **Line:** 181
- **Healing Method:** heal_naming
- **Asymmetry Type:** String-based Operations
- **Evidence:** Direct file I/O with path string

#### StructureHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\structure_healer_agent_types.py`
- **Line:** 228
- **Healing Method:** heal_gravity
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: split

#### StructureHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\structure_healer_agent_types.py`
- **Line:** 228
- **Healing Method:** heal_gravity
- **Asymmetry Type:** String-based Operations
- **Evidence:** Direct file I/O with path string

#### StructureHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\structure_healer_agent_types.py`
- **Line:** 228
- **Healing Method:** heal_gravity
- **Asymmetry Type:** String-based Operations
- **Evidence:** Direct file I/O with path string

#### StructureHealerAgent

- **File Path:** `agentic_core\L5_safety\policy_engine\structure_healer_agent_types.py`
- **Line:** 228
- **Healing Method:** heal_gravity
- **Asymmetry Type:** String-based Operations
- **Evidence:** Uses string operation: join

#### SubAtomicRegistryAgent

- **File Path:** `agentic_core\L2_execution\tool_registry\sub_atomic_registry_agent.py`
- **Line:** 443
- **Detection Method:** _get_phase4_detector_healer_router_executor_mapping
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, type], healer uses unstructured params

#### SystemArchitectAgent

- **File Path:** `agentic_core\L5_safety\validators\system_architect_agent.py`
- **Line:** 400
- **Detection Method:** validate_core_architecture
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### ValidationOrchestratorAgent

- **File Path:** `agentic_core\L2_execution\tool_registry\validation_orchestrator_agent.py`
- **Line:** 314
- **Detection Method:** check_cache
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any] | None, healer uses unstructured params

#### input_validation_guardrail_agent_config

- **File Path:** `agentic_core\L5_safety\guardrails\input_validation_guardrail_agent_config.py`
- **Line:** 212
- **Detection Method:** _detect_pii
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### input_validation_guardrail_agent_config

- **File Path:** `agentic_core\L5_safety\guardrails\input_validation_guardrail_agent_config.py`
- **Line:** 212
- **Detection Method:** _detect_prompt_injection
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### input_validation_guardrail_agent_config

- **File Path:** `agentic_core\L5_safety\guardrails\input_validation_guardrail_agent_config.py`
- **Line:** 212
- **Detection Method:** _detect_bias
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

#### input_validation_guardrail_agent_config

- **File Path:** `agentic_core\L5_safety\guardrails\input_validation_guardrail_agent_config.py`
- **Line:** 212
- **Detection Method:** _validate_format
- **Healing Method:** heal_repository
- **Asymmetry Type:** Detection/Healing Mismatch
- **Evidence:** Detector returns dict[str, Any], healer uses unstructured params

### Registry Build: Detector -> Healer -> Resolution Gap

```json

{
  "AgentCategory": {
    "detector": "_scan_violations",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns List[Dict[str, Any]], healer uses unstructured params"
  },
  "ASTValidatorAgent": {
    "detector": "validate_bare_except",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns list[dict[str, Any]], healer uses unstructured params"
  },
  "SubAtomicRegistryAgent": {
    "detector": "_get_phase4_detector_healer_router_executor_mapping",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, type], healer uses unstructured params"
  },
  "ValidationOrchestratorAgent": {
    "detector": "check_cache",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any] | None, healer uses unstructured params"
  },
  "NervousSystemAgent": {
    "detector": "validate_architecture",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any], healer uses unstructured params"
  },
  "CheckpointManagerAgent": {
    "detector": "list_checkpoints",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns list[dict[str, Any]], healer uses unstructured params"
  },
  "AutonomousThreatEvolutionAgent": {
    "detector": "_load_recent_detections",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns list[dict], healer uses unstructured params"
  },
  "input_validation_guardrail_agent_config": {
    "detector": "_detect_pii",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any], healer uses unstructured params"
  },
  "CodeHealerAgent": {
    "detector": "unknown",
    "healer": "heal_imports",
    "gap": "String-based Operations",
    "evidence": "Uses string operation: split"
  },
  "AgentPermission": {
    "detector": "restore_checkpoint",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any] | None, healer uses unstructured params"
  },
  "StructureHealerAgent": {
    "detector": "unknown",
    "healer": "heal_naming",
    "gap": "String-based Operations",
    "evidence": "Direct file I/O with path string"
  },
  "ArchitectureGovernorAgent": {
    "detector": "_orchestrate_guardian_scan",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any], healer uses unstructured params"
  },
  "AutonomyGuardianAgent": {
    "detector": "unknown",
    "healer": "heal_repository",
    "gap": "String-based Operations",
    "evidence": "Uses string operation: replace"
  },
  "CodeDeduplicationAgent": {
    "detector": "detect_dead_code",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any], healer uses unstructured params"
  },
  "CompositeGuardrailAgent": {
    "detector": "check",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any], healer uses unstructured params"
  },
  "CredentialScannerAgent": {
    "detector": "scan_for_credentials",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any], healer uses unstructured params"
  },
  "FileClassificationAgent": {
    "detector": "_detect_test_patterns",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, bool], healer uses unstructured params"
  },
  "FilesystemSSOTReconcilerAgent": {
    "detector": "_detect_drift",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns list[dict[str, Any]], healer uses unstructured params"
  },
  "GovernanceAgent": {
    "detector": "_check_nesting_depth",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns list[dict[str, Any]], healer uses unstructured params"
  },
  "HierarchyAgent": {
    "detector": "scan_root_violations",
    "healer": "heal_hierarchy",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any], healer uses unstructured params"
  },
  "MCPGuardianAgent": {
    "detector": "scan_codebase",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any], healer uses unstructured params"
  },
  "NamingAgent": {
    "detector": "scan_repository_duplicates",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict, healer uses unstructured params"
  },
  "PineconeSovereignAgent": {
    "detector": "health_check",
    "healer": "health_check",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict, healer uses unstructured params"
  },
  "PreCommitSovereignAgent": {
    "detector": "validate_staged_files",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any], healer uses unstructured params"
  },
  "ReportLocationAgent": {
    "detector": "validate",
    "healer": "heal",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any], healer uses unstructured params"
  },
  "RootHygieneAgent": {
    "detector": "scan_root_violations",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any], healer uses unstructured params"
  },
  "SystemArchitectAgent": {
    "detector": "validate_core_architecture",
    "healer": "heal_repository",
    "gap": "Detection/Healing Mismatch",
    "evidence": "Detector returns dict[str, Any], healer uses unstructured params"
  }
}

```


### SSOT Compliance Check

All identified agents are in SSOT-approved paths.
