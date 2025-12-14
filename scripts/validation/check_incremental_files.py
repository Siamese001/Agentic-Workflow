import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
LOGGER = logging.getLogger(__name__)
import sys
SOVEREIGN_EXCLUSION_LIST = ['fix_canon_violations.py', 'docstring_debt.py', '__init__.py', 'verify_installation.py', 'shared_utilities.py', 'test_utils.py', 'test_security_controls.py', 'test_runtime_ops.py', 'test_pipeline_ops.py', 'test_logic_ops.py', 'test_cache_ops.py', 'test_scripts.py', 'test_planning_schema_validation.py', 'test_models.py', 'test_memory_schema_validation.py', 'test_multi_provider_clients.py', 'test_cache_regression.py', 'test_cache.py', 'test_prompt_governance.py', 'test_observability.py', 'validate_safety_ethics.py', 'update_update_safety_usage.py', 'update_track_safety_cost.py', 'update_enforce_safety_budget.py', 'state_update_safety_usage.py', 'safety_validate_safety_ethics.py', 'safety_enforce_safety_filters.py', 'enforce_safety_filters.py', 'che_update_track_safety_cost.py', 'che_update_enforce_safety_budget.py', 'validate-phase-group_retrieval-ops.py', 'validate-phase-group.py', 'expand-phase-group_vectorization-ops.py', 'expand-phase-group.py', 'route-phase-group.py']
ARCHIVE_SOURCE_LIST = ['constitutional_ai_system.py', 'content_quality_enhancements.py', 'enhanced_semantic_cache.py', 'enhancement_demo.py', 'goal_alignment_engine.py', 'hybrid_scoring.py', 'intelligence_bundles.py', 'lic_demo.py', 'lic_retrieval_demo.py', 'hardening_demo.py', 'enhanced_orchestrator.py', 'fusion_planner.py', 'grounding_planner.py', 'insights_engine.py', 'rag_pipeline.py', 'research_planner.py', 'retrieval_hardening.py', 'lic_profile_planner.py', 'lic_rag.py', 'lic_research_planner.py', 'meta_learning_system.py', 'retrieval_enhancements.py', 'rg_orchestrator.py', 'rg_planner.py', 'rg_state.py', 'safety_enhancements.py']
hardened_exclusion_set = {f.lower() for f in ConfigurationService().SOVEREIGN_EXCLUSION_LIST}
net_incremental_files = []
duplicates_found = []
for archive_file in ConfigurationService().ARCHIVE_SOURCE_LIST:
    if archive_file.lower() not in ConfigurationService().hardened_exclusion_set:
        ConfigurationService().net_incremental_files.append(archive_file)
    else:
        ConfigurationService().duplicates_found.append(archive_file)
if ConfigurationService().net_incremental_files:
    ConfigurationService().logger.info(f'\nFound {len(ConfigurationService().net_incremental_files)} net incremental files:')
    for filename in ConfigurationService().net_incremental_files:
        ConfigurationService().logger.info(f'  - {ConfigurationService().filename}')
else:
    ConfigurationService().logger.info('No net incremental files found')
if ConfigurationService().duplicates_found:
    ConfigurationService().logger.info('\nDuplicate files found:')
    for filename in ConfigurationService().duplicates_found:
        ConfigurationService().logger.info(f'  - {ConfigurationService().filename}')
sys.exit(0)