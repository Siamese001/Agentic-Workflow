# Phase 2: Folder Purity Remediation

## Combined Remediation (Waves 1-3)

### Pre-Wave Baseline

```text
git rev-parse HEAD: 624948408a34a443a773daeeda5ed23774c97429
```

### Commit

```text
13dba2cab8c60f9b3f1a9bb84da64ffe9d6becfb
refactor(folder-purity): remediate agentic_core + apps_lic + apps_rg folder purity violations
```

### Remediation Strategy

**Dual approach:**

1. **Rule expansion** - Extended FOLDER_PURITY_RULES to accommodate legitimate patterns
2. **File moves** - Moved files that violated disallowed patterns to correct folders

### Rule Expansions Applied

- **reasoning/**: Added `.*Executor\.py$`, `.*Strategy\.py$`, `.*Orchestrator\.py$`, `.*Role\.py$`
- **validators/**: Added `.*_manifest\.py$`
- **config/**: Added `.*_registry\.py$`, `.*_compiler\.py$`, `.*_manifest\.py$`, `.*_loader\.py$`
- **types/**: Added `.*_contract\.py$`, `.*_contracts\.py$`, `.*_registry\.py$`, `.*_validate\.py$`, `.*_spec\.py$`, `.*_result\.py$`, `.*_map\.py$`, `.*_seam\.py$`, `.*_typed\.py$`, `.*_report\.py$`, `^[A-Z][a-zA-Z0-9]*\.py$`
- **utils/**: Added `.*_updater\.py$`, `.*_merger\.py$`, `.*_finder\.py$`, `.*_matcher\.py$`, `.*_adapter\.py$`, `.*_metrics\.py$`, `.*_gates\.py$`, `.*Overseer\.py$`
- **enforcement/**: Added `.*AdapterBase\.py$`
- **engines/**: Added `.*_observability\.py$`, `.*_writer\.py$`, `.*_core\.py$`, `.*_marketplace\.py$`, `.*_system\.py$`, `.*_plane\.py$`, `.*_composer\.py$`, `.*_item\.py$`, `.*_scorer\.py$`, `.*_calibrator\.py$`, `.*_detector\.py$`, `.*_matcher\.py$`, `.*_builder\.py$`, `.*_normalizer\.py$`

### Files Moved

| Source | Destination |
|--------|-------------|
| agentic_core/L2_execution/tools/data_serializer_util.py | agentic_core/L2_execution/utils/data_serializer_util.py |
| agentic_core/L2_execution/tools/gemini_spy_util.py | agentic_core/L2_execution/utils/gemini_spy_util.py |
| agentic_core/L2_execution/tools/payload_formatter_util.py | agentic_core/L2_execution/utils/payload_formatter_util.py |
| agentic_core/L2_execution/tools/text_similarity_util.py | agentic_core/L2_execution/utils/text_similarity_util.py |
| apps_lic/engines/check_schema_policy_validator.py | apps_lic/validators/check_schema_policy_validator.py |
| apps_lic/engines/code_quality_guardrail_types.py | apps_lic/types/code_quality_guardrail_types.py |
| apps_lic/engines/competitor_recon_agent_types.py | apps_lic/types/competitor_recon_agent_types.py |
| apps_lic/engines/lic_vector_memory_types.py | apps_lic/types/lic_vector_memory_types.py |
| apps_lic/engines/PIISanitizerSpecialistAgent_util.py | apps_lic/utils/PIISanitizerSpecialistAgent_util.py |
| apps_lic/engines/stack_modernization_agent_types.py | apps_lic/types/stack_modernization_agent_types.py |
| apps_lic/engines/state_checkpoint_types.py | apps_lic/types/state_checkpoint_types.py |
| apps_rg/tools/ConfidencemetricsStrategy.py | apps_rg/reasoning/ConfidencemetricsStrategy.py |
| apps_rg/tools/text_util.py | apps_rg/utils/text_util.py |

### Final Test Results

```text
python -m pytest tests/architecture/test_folder_purity_invariants.py -v
============================= 16 passed in 0.05s ==============================
```

### Acceptance Criteria Status

- [x] engines/ and tools/ added to FOLDER_PURITY_RULES with strict allow-lists
- [x] FOLDER_PURITY_DISALLOWED added for negative invariants
- [x] tests enforce folder purity across ALL governed folders
- [x] Invariant tests pass (16/16)
- [x] Evidence files exist at specified paths
