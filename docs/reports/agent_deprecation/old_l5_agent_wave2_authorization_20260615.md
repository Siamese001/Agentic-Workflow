# Old L5 Agent Wave 2 Authorization Packet

Plan: `old-l5-agent-retirement-a94f6c`
Date: 2026-06-15
Source manifest: `docs/reports/agent_deprecation/old_l5_agent_retirement_manifest_20260615.json`

## Decision

User approval authorizes the remaining Old L5 cohort for deprecation planning and caller migration. It does not authorize immediate physical archive/delete for files without replacement proof, zero-consumer proof, and any required cooling window.

Operational interpretation:

- `COOLING_WINDOW_AUTHORIZED`: deletion was already authorized on 2026-04-24; physical archive remains blocked until 2026-07-23 and zero-live-consumer proof.
- `UNCLASSIFIED_OLD_L5_AGENT`: deprecation is now approved; each file needs classification, replacement/caller proof, then a future deletion receipt before physical removal.
- `LARGE_FACADE_RETIREMENT`: split to W3 blocker packet; do not modernize in place.
- `VALIDATOR_DUPLICATE_OR_SHIM`: treat as duplicate/shim cleanup candidate after import ownership is proven.

## Manifest Summary

| Bucket | Count | W2 disposition |
|---|---:|---|
| `COOLING_WINDOW_AUTHORIZED` | 21 | Keep in W4 queue; migrate live references first |
| `UNCLASSIFIED_OLD_L5_AGENT` | 45 | Deprecation-authorized; deletion deferred to per-file proof |
| `LARGE_FACADE_RETIREMENT` | 5 | Split to W3 large-facade retirement |
| `VALIDATOR_DUPLICATE_OR_SHIM` | 1 | Duplicate/shim follow-up after consumer proof |

## Already Authorized Queue

| Candidate | LOC | Raw refs | ADG fan-in | Replacement / note |
|---|---:|---:|---:|---|
| `ArchitectureGovernorValidatorAgent.py` | 56 | 3 | 6 | No replacement recorded |
| `AutonomyGuardianAgent.py` | 521 | 5 | 41 | No replacement recorded |
| `BenchmarkingAgent.py` | 61 | 3 | 4 | No replacement recorded |
| `BootstrapAgent.py` | 74 | 4 | 5 | No replacement recorded |
| `CodeDeduplicationAgent.py` | 106 | 3 | 4 | No replacement recorded |
| `CodeDetectorAgent.py` | 63 | 5 | 6 | `agentic_core.L5_safety.utils.code_detector_util` |
| `CodeEnforcerAgent.py` | 55 | 5 | 4 | `agentic_core.L5_safety.utils.code_enforcer_util` |
| `CodeFormatterAgent.py` | 53 | 3 | 2 | No replacement recorded |
| `CodeJanitorAgent.py` | 64 | 5 | 5 | `agentic_core.L5_safety.utils.code_janitor_util` |
| `CodeValidatorAgent.py` | 73 | 4 | 8 | `agentic_core.L5_safety.utils.code_validator_util` |
| `ComplexityAnalyzerAgent.py` | 72 | 3 | 8 | No replacement recorded |
| `CostGovernorAgent.py` | 44 | 3 | 5 | No replacement recorded |
| `CredentialScannerAgent.py` | 110 | 3 | 8 | No replacement recorded |
| `DependencyPruningAgent.py` | 74 | 3 | 6 | No replacement recorded |
| `GovernanceAgent.py` | 1178 | 6 | 129 | Direct-call paths; emits `DeprecationWarning` |
| `LocationHealerAgent.py` | 38 | 4 | 0 | `agentic_core.L5_safety.utils.location_healer_util` |
| `RedSentinelAgent.py` | 496 | 3 | 35 | No replacement recorded |
| `StructureHealerAgent.py` | 600 | 7 | 51 | No replacement recorded |
| `validators/CodeJanitorAgent.py` | 169 | 3 | 0 | Duplicate shim |
| `validators/GovernanceAgent.py` | 171 | 6 | 0 | Duplicate shim |
| `validators/PascalSovereigntyAgent.py` | 171 | 3 | 0 | Duplicate shim |

## Remaining Old L5 Cohort

Deletion is not safe for these files in W2. The authorized action is to stop treating them as strategic architecture, classify caller ownership, and split deletion to replacement-backed follow-up waves.

| Candidate | LOC | Raw refs | ADG fan-in | W2 disposition |
|---|---:|---:|---:|---|
| `AdversarialProbeAgent.py` | 368 | 3 | 14 | Security/test harness candidate; prove current caller need |
| `AdversarialRedTeamerAgent.py` | 666 | 4 | 57 | Security/test harness candidate; prove current caller need |
| `AutonomousThreatEvolutionAgent.py` | 329 | 3 | 31 | Security/test harness candidate; prove current caller need |
| `BoundaryTestingAgent.py` | 391 | 3 | 17 | Test harness candidate; prove current caller need |
| `ChaosEngineeringAgent.py` | 362 | 3 | 21 | Resilience harness candidate; prove current caller need |
| `CognitiveDispositionAgent.py` | 384 | 10 | 28 | Roster/seam candidate; migrate or remove from roster |
| `ConstitutionalReviewerAgent.py` | 298 | 6 | 21 | Governance review candidate; prove replacement |
| `DDDAlignmentAgent.py` | 590 | 5 | 35 | Governance review candidate; prove replacement |
| `DocstringComplianceAgent.py` | 324 | 3 | 24 | Static-rule utility candidate |
| `DocumentationAgent.py` | 280 | 5 | 15 | Static-rule utility candidate |
| `DuplicateCodeDetectorAgent.py` | 597 | 3 | 58 | Static detector utility candidate |
| `DynamicSealAgent.py` | 413 | 4 | 53 | Governance runtime candidate; prove live usage |
| `GenerativeGuardAgent.py` | 360 | 3 | 33 | Safety guard candidate; prove live usage |
| `GitHygieneAgent.py` | 418 | 4 | 33 | Static utility/script candidate |
| `GospelSyncAgent.py` | 296 | 4 | 18 | Governance sync candidate; prove live usage |
| `GravityLeakHealerAgent.py` | 147 | 3 | 1 | Alias/shim candidate |
| `HygieneGuardianAgent.py` | 605 | 5 | 57 | Duplicate with validator surface; prove owner |
| `IntegrityGateExecutorAgent.py` | 726 | 3 | 44 | Gate executor candidate; prove runtime owner |
| `InterfaceBoundaryAgent.py` | 303 | 4 | 20 | Boundary rule utility candidate |
| `L5SafetyExerciserAgent.py` | 395 | 4 | 20 | Test/exerciser candidate; prove live usage |
| `NamingAgent.py` | 282 | 9 | 9 | Naming utility candidate; caller migration required |
| `NeuralAutoImmuneAgent.py` | 210 | 5 | 7 | Safety guard candidate; prove live usage |
| `PolicyNeuralAutoImmuneAgent.py` | 254 | 4 | 10 | Safety guard candidate; prove live usage |
| `PreCommitSovereignAgent.py` | 474 | 7 | 85 | Hook/governance candidate; prove replacement |
| `PredictiveCostAuditorAgent.py` | 569 | 4 | 38 | Cost/risk review candidate; prove live usage |
| `RedTeamAgent.py` | 472 | 7 | 39 | Security/test harness candidate; prove current caller need |
| `RegressionOracleAgent.py` | 544 | 5 | 33 | Test harness candidate; prove replacement |
| `ReportLocationAgent.py` | 437 | 4 | 27 | Report-location utility candidate |
| `ResourceManagerAgent.py` | 456 | 7 | 13 | Runtime manager candidate; prove live usage |
| `SafetyDetectorAgent.py` | 393 | 6 | 28 | Safety detector utility candidate |
| `SafetyExecutorAgent.py` | 444 | 6 | 22 | Safety executor candidate; prove live usage |
| `SafetyInspectorAgent.py` | 634 | 4 | 53 | Safety inspection utility candidate |
| `SecurityManagerAgent.py` | 490 | 6 | 31 | Security manager candidate; prove live usage |
| `SelfUpdatingSafetyEngineAgent.py` | 636 | 3 | 46 | Runtime/governance candidate; prove live usage |
| `SovereignActionPlaneAgent.py` | 695 | 6 | 80 | Runtime action-plane candidate; prove live usage |
| `SprawlInspectorAgent.py` | 304 | 4 | 25 | Static detector utility candidate |
| `StructuralEngineerAgent.py` | 430 | 4 | 60 | Structure utility candidate; caller migration required |
| `StructuralValidatorAgent.py` | 422 | 7 | 38 | Validator facade candidate; prove canonical owner |
| `StructureEnforcerAgent.py` | 559 | 10 | 45 | Structure utility candidate; caller migration required |
| `SystemArchitectAgent.py` | 696 | 8 | 99 | Governance planner candidate; prove live usage |
| `TerritoryChangeHandlerAgent.py` | 308 | 4 | 27 | Territory utility candidate |
| `TestGeneratorAgent.py` | 425 | 4 | 48 | Test harness candidate; prove replacement |
| `TypeHintFixerAgent.py` | 228 | 4 | 13 | Static utility/script candidate |
| `TypeMechanicAgent.py` | 354 | 5 | 40 | Static utility/script candidate |
| `UnusedCleanupAgent.py` | 223 | 3 | 4 | Static utility/script candidate |

## Required Follow-Up Gates

1. For each unclassified file, prove whether it has a runtime caller, generated-only caller, test-only caller, or no current caller.
2. If runtime callers remain, migrate those callers to an existing utility or create a separate extraction plan.
3. Add deletion metadata only after replacement and consumer proof are attached.
4. Do not use skip markers to hide obsolete tests; rewrite or delete tests in the deletion wave.
5. Physical archive/delete remains a W4 action and is not performed by W2.
