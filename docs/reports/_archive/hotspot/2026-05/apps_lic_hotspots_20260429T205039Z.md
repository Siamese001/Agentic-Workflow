# `apps_lic` — ADG Hotspot Report (W0.1)

Generated: `2026-04-29T20:50:39Z`
Snapshot: `adg_indexed_04292026_1606.sqlite`
Severity (Phase B): **HIGH (canary surface)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_04292026_1606.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 245 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|
| `ADG::Symbol::apps_lic.types.ValidationResult` | `apps_lic/types/__init__.py` | 7 |
| `ADG::Symbol::apps_lic.engines.control_plane.ControlPlane` | `apps_lic/engines/control_plane.py` | 7 |
| `ADG::Symbol::apps_lic.types.state_checkpoint_types.LICStateManager` | `apps_lic/types/state_checkpoint_types.py` | 6 |
| `ADG::Symbol::apps_lic.types.DraftPackage` | `apps_lic/types/__init__.py` | 6 |
| `ADG::Symbol::apps_lic.types.CampaignResult` | `apps_lic/types/__init__.py` | 6 |
| `ADG::Symbol::apps_lic.engines.control_plane.PolicyAction` | `apps_lic/engines/control_plane.py` | 6 |
| `ADG::Symbol::apps_lic.utils.manifest_manager_util.ManifestManager` | `apps_lic/utils/manifest_manager_util.py` | 4 |
| `ADG::Symbol::apps_lic.utils.lic_agent_base_util.LICAgentBase` | `apps_lic/utils/lic_agent_base_util.py` | 4 |
| `ADG::Symbol::apps_lic.types.TraceRegistry.TraceRegistry` | `apps_lic/types/TraceRegistry.py` | 4 |
| `ADG::Symbol::apps_lic.types.CampaignRequest` | `apps_lic/types/__init__.py` | 4 |
| `ADG::Symbol::apps_lic.types.CampaignRunSummary` | `apps_lic/types/__init__.py` | 3 |
| `ADG::Symbol::apps_lic.engines.control_plane` | `apps_lic/engines/control_plane.py` | 3 |
| `ADG::Symbol::apps_lic.utils.lic_engine_validation_capability_util.LICEngineValidationCapability` | `apps_lic/utils/lic_engine_validation_capability_util.py` | 2 |
| `ADG::Symbol::apps_lic.utils.archetype_indicator_util.ArchetypeIndicator` | `apps_lic/utils/archetype_indicator_util.py` | 2 |
| `ADG::Symbol::apps_lic.utils.PIISanitizerSpecialistAgent_util.PII_SanitizerSpecialistAgent` | `apps_lic/utils/PIISanitizerSpecialistAgent_util.py` | 2 |

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_lic/utils/lic_agent_base_util.py` | `apps_lic/utils/lic_agent_base_util.py` | 85 |
| `ADG::Module::apps_lic/reasoning/GovernanceShieldAgent.py` | `apps_lic/reasoning/GovernanceShieldAgent.py` | 83 |
| `ADG::Module::apps_lic/config/retry_policy_config.py` | `apps_lic/config/retry_policy_config.py` | 82 |
| `ADG::Module::apps_lic/utils/PIISanitizerSpecialistAgent_util.py` | `apps_lic/utils/PIISanitizerSpecialistAgent_util.py` | 81 |
| `ADG::Module::apps_lic/reasoning/OutreachSignalRouterAgent.py` | `apps_lic/reasoning/OutreachSignalRouterAgent.py` | 81 |
| `ADG::Module::apps_lic/reasoning/OutreachLearningAgent.py` | `apps_lic/reasoning/OutreachLearningAgent.py` | 80 |
| `ADG::Module::apps_lic/engines/control_plane.py` | `apps_lic/engines/control_plane.py` | 79 |
| `ADG::Module::apps_lic/types/app_content_validator_agent_types.py` | `apps_lic/types/app_content_validator_agent_types.py` | 77 |
| `ADG::Module::apps_lic/types/TraceRegistry.py` | `apps_lic/types/TraceRegistry.py` | 77 |
| `ADG::Module::apps_lic/reasoning/OutreachValidationExecutorAgent.py` | `apps_lic/reasoning/OutreachValidationExecutorAgent.py` | 76 |
| `ADG::Module::apps_lic/reasoning/LicHealingOrchestrator.py` | `apps_lic/reasoning/LicHealingOrchestrator.py` | 76 |
| `ADG::Module::apps_lic/utils/manifest_manager_util.py` | `apps_lic/utils/manifest_manager_util.py` | 75 |
| `ADG::Module::apps_lic/types/state_checkpoint_types.py` | `apps_lic/types/state_checkpoint_types.py` | 75 |
| `ADG::Module::apps_lic/config/reasoning_toggles_config.py` | `apps_lic/config/reasoning_toggles_config.py` | 75 |
| `ADG::Module::apps_lic/reasoning/HOPPipelineExecutor.py` | `apps_lic/reasoning/HOPPipelineExecutor.py` | 74 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **75**

- `apps_lic/engines/__init__.py`
- `apps_lic/engines/__init__.py`
- `apps_lic/engines/__init__.py`
- `apps_lic/engines/control_plane.py`
- `apps_lic/engines/control_plane.py`
- `apps_lic/engines/control_plane.py`
- `apps_lic/engines/control_plane.py`
- `apps_lic/engines/control_plane.py`
- `apps_lic/engines/control_plane.py`
- `apps_lic/engines/hop_stage_registry.py`
- `apps_lic/engines/hop_stage_registry.py`
- `apps_lic/engines/lic_spine_adapter.py`
- `apps_lic/engines/message_body_composer.py`
- `apps_lic/reasoning/DispatchOutreachToolsAgent.py`
- `apps_lic/reasoning/ExecutiveStrategyAgent.py`
- `apps_lic/reasoning/GovernanceShieldAgent.py`
- `apps_lic/reasoning/GovernanceShieldAgent.py`
- `apps_lic/reasoning/GovernanceShieldAgent.py`
- `apps_lic/reasoning/GovernanceShieldAgent.py`
- `apps_lic/reasoning/GovernanceShieldAgent.py`
- `apps_lic/reasoning/HOPPipelineExecutor.py`
- `apps_lic/reasoning/HOPPipelineExecutor.py`
- `apps_lic/reasoning/HOPPipelineExecutor.py`
- `apps_lic/reasoning/IndustrysensitivityStrategy.py`
- `apps_lic/reasoning/IntelligenceLibrarianAgent.py`
- `apps_lic/reasoning/LICValidationExecutor.py`
- `apps_lic/reasoning/LICValidationExecutor.py`
- `apps_lic/reasoning/LICValidationExecutor.py`
- `apps_lic/reasoning/LicCodeInterpreter.py`
- `apps_lic/reasoning/LicHealingOrchestrator.py`
- ... +45 more

## mv_hotspot_centrality (top 10 within app)

Rows: 10
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2637, 'ADG::Module::apps_lic/types/__init__.py', 'L_APP', 'apps_lic/types/__init__.py', 29, 10, 39, 0.0352, 0.0035, 2637, 'ADG::Module::apps_lic/types/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/types/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'a4c4e42348003504b847c4307eedcdf867c887bd')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2583, 'ADG::Module::apps_lic/engines/control_plane.py', 'L_APP', 'apps_lic/engines/control_plane.py', 18, 79, 97, 0.1727, 0.0022, 2583, 'ADG::Module::apps_lic/engines/control_plane.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/engines/control_plane.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '3b7b87a0426da0526790ac6ebd9120823222e2ea')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2634, 'ADG::Module::apps_lic/types/PromptTemplate.py', 'L_APP', 'apps_lic/types/PromptTemplate.py', 12, 6, 18, 0.0087, 0.0015, 2634, 'ADG::Module::apps_lic/types/PromptTemplate.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/types/PromptTemplate.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '013dd32b2a1e868efd32961a05f4f916ac2be423')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2656, 'ADG::Module::apps_lic/utils/archetype_indicator_util.py', 'L_APP', 'apps_lic/utils/archetype_indicator_util.py', 12, 4, 16, 0.0058, 0.0015, 2656, 'ADG::Module::apps_lic/utils/archetype_indicator_util.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/utils/archetype_indicator_util.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '36cb3ee7417faf75027dc33412fb2e211aff74b4')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2576, 'ADG::Module::apps_lic/config/archetype_indicator_config.py', 'L_APP', 'apps_lic/config/archetype_indicator_config.py', 11, 10, 21, 0.0134, 0.0013, 2576, 'ADG::Module::apps_lic/config/archetype_indicator_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/config/archetype_indicator_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '97a782aaa992ab8e3ea9b43024630873a0ccf72a')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2609, 'ADG::Module::apps_lic/reasoning/OutreachLearningAgent.py', 'L_APP', 'apps_lic/reasoning/OutreachLearningAgent.py', 11, 80, 91, 0.1068, 0.0013, 2609, 'ADG::Module::apps_lic/reasoning/OutreachLearningAgent.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/reasoning/OutreachLearningAgent.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'bf3323049496ad6afa254a199c168fdc35245b9f')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2613, 'ADG::Module::apps_lic/reasoning/OutreachValidationExecutorAgent.py', 'L_APP', 'apps_lic/reasoning/OutreachValidationExecutorAgent.py', 10, 76, 86, 0.0923, 0.0012, 2613, 'ADG::Module::apps_lic/reasoning/OutreachValidationExecutorAgent.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/reasoning/OutreachValidationExecutorAgent.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'a4725c151d971d94332fd067416fb0ebfe6861eb')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2654, 'ADG::Module::apps_lic/utils/PIISanitizerSpecialistAgent_util.py', 'L_APP', 'apps_lic/utils/PIISanitizerSpecialistAgent_util.py', 8, 81, 89, 0.0787, 0.001, 2654, 'ADG::Module::apps_lic/utils/PIISanitizerSpecialistAgent_util.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/utils/PIISanitizerSpecialistAgent_util.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'c04403985deb2e5a9756fc601fe05815e406a169')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2651, 'ADG::Module::apps_lic/types/state_checkpoint_types.py', 'L_APP', 'apps_lic/types/state_checkpoint_types.py', 6, 75, 81, 0.0546, 0.0007, 2651, 'ADG::Module::apps_lic/types/state_checkpoint_types.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/types/state_checkpoint_types.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '696e12cae1d7db09ae7973c02f5f54b5c95644db')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2577, 'ADG::Module::apps_lic/config/knowledge_base.py', 'L_APP', 'apps_lic/config/knowledge_base.py', 5, 12, 17, 0.0073, 0.0006, 2577, 'ADG::Module::apps_lic/config/knowledge_base.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/config/knowledge_base.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '7a8955e76d712a7509382443512461cfa83d3319')

## mv_dependency_cone_risk (top 10 within app)

Rows: 10
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2637, 'ADG::Module::apps_lic/types/__init__.py', 'L_APP', 'apps_lic/types/__init__.py', 8, 0, 0, 8, 8.0, 2637, 'ADG::Module::apps_lic/types/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/types/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'a4c4e42348003504b847c4307eedcdf867c887bd')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2583, 'ADG::Module::apps_lic/engines/control_plane.py', 'L_APP', 'apps_lic/engines/control_plane.py', 5, 0, 0, 5, 5.0, 2583, 'ADG::Module::apps_lic/engines/control_plane.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/engines/control_plane.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '3b7b87a0426da0526790ac6ebd9120823222e2ea')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2633, 'ADG::Module::apps_lic/types/ImmutableStagingBuffer.py', 'L_APP', 'apps_lic/types/ImmutableStagingBuffer.py', 4, 0, 0, 4, 4.0, 2633, 'ADG::Module::apps_lic/types/ImmutableStagingBuffer.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/types/ImmutableStagingBuffer.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '70ea117a53ae81954ccd9d2ac1bdaa424bef776c')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2659, 'ADG::Module::apps_lic/utils/lic_agent_base_util.py', 'L_APP', 'apps_lic/utils/lic_agent_base_util.py', 4, 0, 0, 4, 4.0, 2659, 'ADG::Module::apps_lic/utils/lic_agent_base_util.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/utils/lic_agent_base_util.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '494918bfe86985b0c7d9f9859ebda4727fd75663')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2577, 'ADG::Module::apps_lic/config/knowledge_base.py', 'L_APP', 'apps_lic/config/knowledge_base.py', 3, 0, 0, 3, 3.0, 2577, 'ADG::Module::apps_lic/config/knowledge_base.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/config/knowledge_base.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '7a8955e76d712a7509382443512461cfa83d3319')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2598, 'ADG::Module::apps_lic/reasoning/GovernanceShieldAgent.py', 'L_APP', 'apps_lic/reasoning/GovernanceShieldAgent.py', 3, 0, 0, 3, 3.0, 2598, 'ADG::Module::apps_lic/reasoning/GovernanceShieldAgent.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/reasoning/GovernanceShieldAgent.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '4481bb415e960007be6b763353572dfd41254cf8')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2636, 'ADG::Module::apps_lic/types/TraceRegistry.py', 'L_APP', 'apps_lic/types/TraceRegistry.py', 3, 0, 0, 3, 3.0, 2636, 'ADG::Module::apps_lic/types/TraceRegistry.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/types/TraceRegistry.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '2d07c55408987338e80d5c4a4d4102764e282876')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2589, 'ADG::Module::apps_lic/integrations/governed_lic_run.py', 'L_APP', 'apps_lic/integrations/governed_lic_run.py', 2, 0, 0, 2, 2.0, 2589, 'ADG::Module::apps_lic/integrations/governed_lic_run.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/integrations/governed_lic_run.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '2e5a437fd7822a7e1af3ed5d9f47dc4e2f3a4bc4')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2599, 'ADG::Module::apps_lic/reasoning/HOPPipelineExecutor.py', 'L_APP', 'apps_lic/reasoning/HOPPipelineExecutor.py', 2, 0, 0, 2, 2.0, 2599, 'ADG::Module::apps_lic/reasoning/HOPPipelineExecutor.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/reasoning/HOPPipelineExecutor.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '938bd859cc56e9ea0d860dc9939a9eecc596c372')
- ('cf3b6a26c9da1677e9f2d1857e414b14dd03dabe', 2602, 'ADG::Module::apps_lic/reasoning/LICValidationExecutor.py', 'L_APP', 'apps_lic/reasoning/LICValidationExecutor.py', 2, 0, 0, 2, 2.0, 2602, 'ADG::Module::apps_lic/reasoning/LICValidationExecutor.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/reasoning/LICValidationExecutor.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5f651eba48cae8e5ddb42f54afba3c847a7b6c69')

## mv_chokepoint_bridges

_view not present in this snapshot_

## v_p0_apps_direct_infra (P0 violation — apps directly importing infra)

Rows: 1
- ('__error__', 'no such column: source_file')

## SC/AP Violations (top 30 by severity)

Rows: 1

| Severity | Kind | File | Line | Message |
|---|---|---|---:|---|

## Recommendations (derived)

- **Most-depended-on files (highest blast radius if changed):**
  - `apps_lic/types/__init__.py` (fan-in 7) — touch only with explicit Author-Gate
  - `apps_lic/engines/control_plane.py` (fan-in 7) — touch only with explicit Author-Gate
  - `apps_lic/types/state_checkpoint_types.py` (fan-in 6) — touch only with explicit Author-Gate
  - `apps_lic/types/__init__.py` (fan-in 6) — touch only with explicit Author-Gate
  - `apps_lic/types/__init__.py` (fan-in 6) — touch only with explicit Author-Gate
- **Broadest reachers (most likely to consolidate):**
  - `apps_lic/utils/lic_agent_base_util.py` (fan-out 85)
  - `apps_lic/reasoning/GovernanceShieldAgent.py` (fan-out 83)
  - `apps_lic/config/retry_policy_config.py` (fan-out 82)
  - `apps_lic/utils/PIISanitizerSpecialistAgent_util.py` (fan-out 81)
  - `apps_lic/reasoning/OutreachSignalRouterAgent.py` (fan-out 81)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

