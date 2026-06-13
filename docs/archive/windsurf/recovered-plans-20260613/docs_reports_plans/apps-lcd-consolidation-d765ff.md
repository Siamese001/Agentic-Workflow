# Apps LCD Consolidation Plan

Consolidate all three `apps_*` folders from their current 10-14 folder sprawl (with 3-level nesting and massive junk drawers) down to the LCD 6-folder standard, matching `agentic_core/` conventions.

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


## Current State Audit

### apps_rg (13 top-level folders, 173 files)

| Folder | Files | Nesting | Problem |
|--------|-------|---------|---------|
| engines/ | 78 | **9 subfolders** (base/, generation/, hops/, orchestration/, quality/, refinement/, retrieval/, safety/, utils/) | LCD violation: 3-level deep. `engines/utils/` is a 22-file junk drawer full of Agents, Strategies, and Orchestrators |
| shared/ | 43 | **4 subfolders** (core/, reasoning/, tools/, utils/) | Duplicates LCD folders. `shared/tools/` has 34 files |
| domain/ | 6 | **2 subfolders** (config/, utils/) | Nested config/ and utils/ inside domain/ — files belong in top-level config/ and types/ |
| logic_nodes/ | 6 | flat | Non-LCD folder — these are types files (`*_types.py`) |
| scripts/ | 10 | flat | OK — nuance folder per LCD+ |
| config/ | 3 | flat | OK |
| types/ | 7 | flat | OK |
| validation/ | 5 | flat | OK — maps to validators/ |
| utils/ | 7 | flat | Contains 5 `.md` reports — wrong folder |
| reasoning/ | 4 | flat | OK |
| asset_library/ | 1 | **empty** (only `__init__.py`) | Delete |
| core/ | 1 | **empty** | Delete |
| system_flow/ | 1 | **empty** | Delete |

### apps_lic (14 top-level folders, 147 files)

| Folder | Files | Nesting | Problem |
|--------|-------|---------|---------|
| engines/ | 47 | flat | Contains 30+ Agents, types, configs mixed together — needs classification |
| shared/ | 58 | **3 subfolders** (core/, reasoning/, tools/) | Duplicates LCD. `shared/tools/` has 47 files |
| domain/ | 19 | **2 subfolders** (config/, utils/) | Nested config/ and utils/. `domain/utils/` has types, strategies, configs mixed |
| logic_nodes/ | 2 | flat | Non-LCD — types files |
| scripts/ | 5 | flat | OK |
| config/ | 1 | **empty** | Only `__init__.py` |
| types/ | 5 | flat | OK |
| validation/ | 3 | flat | OK — maps to validators/ |
| reports/ | 2 | flat | `.md` files — move to docs/ |
| reasoning/ | 1 | **empty** | Only `__init__.py` |
| asset_library/ | 1 | **empty** | Delete |
| system_flow/ | 1 | **empty** | Delete |
| tools/ | 1 | **empty** | Delete |
| utils/ | 1 | **empty** | Delete |

### apps_shared (11 top-level folders, 236 files)

| Folder | Files | Nesting | Problem |
|--------|-------|---------|---------|
| **common_utils/** | **197** | flat | **CRITICAL JUNK DRAWER**: 48 types, 17 configs, 13 validators, 11 strategies, 17 utility scripts, 14 fix/migration scripts, 73 other mixed classes. This single folder is 84% of apps_shared |
| config/ | 5 | flat | OK |
| utils/ | 10 | flat | OK |
| core_components/ | 6 | flat | Non-LCD — has types + embeddings mixed |
| agents/ | 2 | flat | Only AppBase.py — merge into reasoning/ or keep as nuance |
| mixins/ | 4 | flat | OK — belongs in utils/ per LCD |
| data/ | 3 | flat | Nuance (JSON data files) |
| integration/ | 2 | flat | Only 1 config file |
| llm/ | 3 | flat | Only 2 files + init |
| scripts/ | 3 | flat | OK |
| tools/ | 1 | **empty** | Delete |

---

## Target LCD Structure for Apps

Each `apps_*` folder gets the same 6-folder LCD skeleton, plus 1-2 nuance folders where justified:

```
apps_{name}/
├── config/        # App-level configuration
├── types/         # Data models, enums, protocols, exceptions
├── reasoning/     # Agents, orchestrators, strategies, planners
├── engines/       # Domain engines (FLAT — no subfolders)
├── validators/    # Validation logic
├── utils/         # Shared utilities, mixins, helpers
├── tools/         # Tool implementations (callable tools)
├── scripts/       # Ops scripts (nuance)
└── data/          # Static data files (nuance, apps_shared only)
```

**Key differences from agentic_core LCD:**
- `engines/` replaces `enforcement/` — apps don't enforce architectural rules, they have domain engines
- `tools/` is a top-level folder (apps have many callable tools)
- No `shared/` or `domain/` — those concepts are absorbed into the 6 folders

---

## Phase 1: Delete Empty Folders ()

Delete folders that contain only `__init__.py`:
- `apps_rg/asset_library/`, `apps_rg/core/`, `apps_rg/system_flow/`
- `apps_lic/asset_library/`, `apps_lic/system_flow/`, `apps_lic/tools/`, `apps_lic/utils/`
- `apps_shared/tools/`

Also delete empty `apps_lic/config/` and `apps_lic/reasoning/` (only `__init__.py`, real files elsewhere).

## Phase 2: Relocate Misplaced Non-Python Files ()

- `apps_rg/utils/*.md` (5 reports) → `docs/reports/apps_rg/`
- `apps_lic/reports/*.md` (2 reports) → `docs/reports/apps_lic/`
- `apps_lic/domain/config/*.json` → `apps_lic/config/`
- `apps_lic/domain/utils/*.json` → `apps_lic/config/`
- `apps_rg/domain/config/*.json` → `apps_rg/config/`

## Phase 3: Dissolve `domain/` Nesting (per app)

### apps_rg/domain/ (4 real files)
| File | From | To |
|------|------|----|
| `AgentSpec.py` | domain/config/ | config/ |
| `sovereign_config_loader_config.py` | domain/config/ | config/ |
| `PromptTemplate.py` | domain/utils/ | utils/ |

### apps_lic/domain/ (15 real files)
| File | From | To |
|------|------|----|
| `ArchetypeIndicatorsAgent.py` | domain/config/ | reasoning/ |
| `archetype_indicator_config.py` | domain/config/ | config/ |
| `loader.py` | domain/config/ | config/ |
| `route_types.py` | domain/config/ | types/ |
| `IndustrysensitivityStrategy.py` | domain/utils/ | reasoning/ |
| `message_route_types.py` | domain/utils/ | types/ |
| `placeholder_detector_agent_config.py` | domain/utils/ | config/ |
| `qa_block_type_types.py` | domain/utils/ | types/ |
| `recipient_archetype_types.py` | domain/utils/ | types/ |
| `retry_policy.py` | domain/utils/ | config/ |
| `route_types.py` (dup name) | domain/utils/ | types/ (rename: `message_route_types_lic.py` or merge) |
| `SpecialistDraftPacket.py` | domain/utils/ | types/ |
| `validation_severity_types.py` | domain/utils/ | types/ |

Delete `domain/` after emptying.

## Phase 4: Flatten `engines/` Nesting in apps_rg

Current: 9 subfolders → Target: flat

| Current Subfolder | File Count | Action |
|---|---|---|
| engines/base/ | 2 | Merge into engines/ root |
| engines/generation/ | 6 | Merge into engines/ root |
| engines/hops/ | 2 | Merge into engines/ root |
| engines/orchestration/ | 8 | Merge into engines/ root |
| engines/quality/ | 7 | Merge into engines/ root |
| engines/refinement/ | 12 | Merge into engines/ root |
| engines/retrieval/ | 4 | Merge into engines/ root |
| engines/safety/ | 6 | Merge into engines/ root |
| **engines/utils/** | **22** | **Classify and redistribute** (see below) |

### engines/utils/ Redistribution (22 files → correct LCD folders)

| File | Classification | Target |
|------|----------------|--------|
| `ATSCompatibilityAgent.py` | AGENT | reasoning/ |
| `BrandComplianceAgent.py` | AGENT | reasoning/ |
| `CampaignPlannerAgent.py` | AGENT | reasoning/ |
| `ContentQualityAgent.py` | AGENT | reasoning/ |
| `ContentStrategyAgent.py` | AGENT | reasoning/ |
| `ExecutiveSummaryOutputAgent.py` | AGENT | reasoning/ |
| `FactCheckAgent.py` | AGENT | reasoning/ |
| `HeadlineOutputAgent.py` | AGENT | reasoning/ |
| `ProactiveAgent.py` | AGENT | reasoning/ |
| `RgReflectionAgent.py` | AGENT | reasoning/ |
| `RgStrategicPlannerAgent.py` | AGENT | reasoning/ |
| `RgTemplateOptimizerAgent.py` | AGENT | reasoning/ |
| `SectionBalanceAgent.py` | AGENT | reasoning/ |
| `RgHealingOrchestrator.py` | ORCHESTRATOR | reasoning/ |
| `RgResumeOrchestrator.py` | ORCHESTRATOR | reasoning/ |
| `HardenedanthropicexecutorStrategy.py` | STRATEGY | reasoning/ |
| `HardenedopenaiexecutorStrategy.py` | STRATEGY | reasoning/ |
| `AllProvidersDownError.py` | EXCEPTION | types/ |
| `routing_tier_types.py` | TYPES | types/ |
| `agent_executor.py` | UTILITY | utils/ |
| `deep_brain_harvester.py` | UTILITY | utils/ |
| `providers_anthropic_client.py` | UTILITY | utils/ |

## Phase 5: Dissolve `shared/` Nesting (per app)

### apps_rg/shared/ (39 real files)
| Subfolder | Files | Target |
|-----------|-------|--------|
| shared/core/ (3) | `RGAgentBase.py`, `SovereignContext.py`, `mixins.py` | utils/ (base + mixins), types/ (context) |
| shared/reasoning/ (1) | `ReasoningToggles.py` | config/ |
| shared/tools/ (34) | All tool implementations | tools/ |
| shared/utils/ (1) | `mixins.py` | utils/ |

### apps_lic/shared/ (54 real files)
| Subfolder | Files | Target |
|-----------|-------|--------|
| shared/core/ (5) | `LICAgentBase.py`, `ManifestManager.py`, `ImmutableStagingBuffer.py`, `TraceRegistry.py`, `mixins.py` | utils/ (base + mixins), types/ (buffer, registry) |
| shared/reasoning/ (2) | `ReasoningToggles.py`, `cot.py` | config/ (toggles), utils/ (cot) |
| shared/tools/ (47) | All tool implementations | tools/ |

Delete `shared/` after emptying.

## Phase 6: Rename `validation/` → `validators/` (consistency)

Both `apps_rg/validation/` and `apps_lic/validation/` → rename to `validators/` per LCD standard.

## Phase 7: Absorb `logic_nodes/` → `types/`

- `apps_rg/logic_nodes/` (5 `*_types.py` files) → `apps_rg/types/`
- `apps_lic/logic_nodes/` (1 `*_types.py` file) → `apps_lic/types/`

## Phase 8: Decompose `apps_shared/common_utils/` (THE BIG ONE)

197 files in one folder → classify and distribute into LCD structure.

| Classification | Count | Target |
|---|---|---|
| `*_types.py` | 48 | types/ |
| `*_config.py` | 17 | config/ |
| `*_validator.py` | 13 | validators/ (new) |
| `*Strategy.py` | 11 | reasoning/ (new) |
| `*Orchestrator.py` | 3 | reasoning/ |
| `utilities_*` scripts | 17 | scripts/ |
| `fix_*` / `update_*` / `restore_*` scripts | 14 | scripts/ |
| Other classes/modules | 73 | Classify by AST: Agents→reasoning/, types→types/, utils→utils/ |

After this phase, `common_utils/` is deleted and `apps_shared/` has the LCD skeleton.

### apps_shared Additional Absorptions
| Folder | Files | Target |
|--------|-------|--------|
| core_components/ (5) | `EmbedJobDescription.py` etc. | utils/ or reasoning/ |
| core_components/ (1) | `integration_layer_types.py` | types/ |
| integration/ (1) | `integration_config.py` | config/ |
| llm/ (2) | `context_manager.py`, `prompt_optimizer_types.py` | utils/ (manager), types/ (types) |
| mixins/ (3) | `analysis_mixin.py` etc. | utils/ |
| agents/ (1) | `AppBase.py` | utils/ (base class) |

Delete `common_utils/`, `core_components/`, `integration/`, `llm/`, `mixins/`, `agents/` after emptying.

## Phase 9: Mass Import Fix

After all moves:
1. Script to find all `from apps_*/old_path import X` and rewrite to `from apps_*/new_path import X`
2. Run `python -m py_compile` on all moved files
3. Run `ruff check` to verify
4. Run existing test suite

## Phase 10: Update FileClassificationAgent

Update `apps_valid_folders` and `app_territory_map` in `FileClassificationAgent.py` to reflect the new LCD structure (remove dissolved folders, add `validators/`).

---

## Summary Metrics

| Metric | Before | After |
|--------|--------|-------|
| apps_rg top-level folders | 13 | 8 (config, types, reasoning, engines, validators, utils, tools, scripts) |
| apps_lic top-level folders | 14 | 8 |
| apps_shared top-level folders | 11 | 8 (+ data/ nuance) |
| Max nesting depth | 3 (engines/utils/Agent.py) | 1 (flat) |
| Empty folders | 15 | 0 |
| Junk drawers (>20 mixed files) | 4 (engines/utils, shared/tools x2, common_utils) | 0 |
| Files in biggest folder | 197 (common_utils/) | ~50 max (tools/) |

## Execution Order

1. Phase 1-2: Delete empties + relocate non-Python (safe, no import changes)
2. Phase 3: Dissolve `domain/` (small, 4+15 files)
3. Phase 4: Flatten `engines/` (apps_rg only, 22 files redistributed)
4. Phase 5: Dissolve `shared/` (39+54 files)
5. Phase 6-7: Rename validation→validators, absorb logic_nodes (trivial renames)
6. **Phase 8: Decompose common_utils/** (197 files — highest risk, do last)
7. Phase 9: Mass import fix (automated)
8. Phase 10: Update FileClassificationAgent config

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

