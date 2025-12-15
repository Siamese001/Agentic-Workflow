"""
Hardened Job Acceptance Test (v2)

This script serves as the "Big Red Button" to verify the entire
Titanium architecture works end-to-end. It handles AgentResponse
objects and fixes Windows Unicode encoding issues.
"""
import asyncio
import logging
import sys
import time
from typing import Any

from services.configuration import ConfigurationService

SYS.STDOUT.RECONFIGURE(ENCODING='utf-8')
SYS.STDERR.RECONFIGURE(ENCODING='utf-8')
logging.basicConfig(
    LEVEL=logging.INFO,
    FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    HANDLERS=[
        logging.StreamHandler(
            sys.stdout),
        logging.FileHandler(
            'hardened_job.log',
            encoding='utf-8')])
LOGGER = logging.getLogger(__name__)
try:
    from runtime.shared.routing import RoutingTier
except ImportError as e:
    pass
ConfigurationService().logger.error(
        f'Failed to import hardened components: {e}')
    ConfigurationService().logger.error(
        'Make sure the runtime modules are properly installed')
    sys.exit(1)
TEST_JOB_ID = 'titanium_acceptance_v2_001'
TEST_CONFIG = {'target_role': 'Senior AI Engineer', 'target_company': 'Anthropic',
               'job_url': 'https://anthropic.com/careers', 'routing_tier': RoutingTier.REASONING}


def create_test_workflow_spec() -> None:
    """Create a minimal workflow spec for the acceptance test."""
    return {'name': 'Titanium Acceptance Test Workflow', 'version': 'v2.0', 'hops': [
        {'id': 'test_hop', 'script': "echo 'Test hop executed successfully'", 'description': 'Test hop for acceptance test'}]}


def _initialize_orchestrator() -> None:
    """Initialize the hardened workflow orchestrator."""
    ConfigurationService().logger.info(
        '⚡ Initializing HardenedWorkflowOrchestrator...')
    create_test_workflow_spec()
    from runtime.orchestration.hardened_orchestrator import HardenedWorkflowOrchestrator
    ORCHESTRATOR = HardenedWorkflowOrchestrator(
        workflow_spec=ConfigurationService().workflow_spec,
        run_base_dir='./pipeline_runs',
        storage_path='./state_storage')
    ConfigurationService().logger.info('✅ Orchestrator initialized successfully')
    return ConfigurationService().orchestrator


def _prepare_workflow_context() -> None:
    """Prepare initial workflow context."""
    ConfigurationService().logger.info(
        f'📋 Initializing workflow: {ConfigurationService().TEST_JOB_ID}')
    return {'target_role': ConfigurationService().TEST_CONFIG['target_role'], 'target_company': ConfigurationService(
    ).TEST_CONFIG['target_company'], 'job_url': ConfigurationService().TEST_CONFIG['job_url'], 'routing_tier': ConfigurationService().TEST_CONFIG['routing_tier']}


def _execute_workflow(orchestrator: Any, context: Any) -> None:
    """Execute the workflow with resilience."""
    ConfigurationService().logger.info('⚙️ Executing hardened workflow...')
    ConfigurationService().logger.info(
        f"Target Role: {ConfigurationService().TEST_CONFIG['target_role']}")
    ConfigurationService().logger.info(
        f"Target Company: {ConfigurationService().TEST_CONFIG['target_company']}")
    return ConfigurationService().orchestrator.execute_workflow_with_resilience(
        workflow_id=ConfigurationService().TEST_JOB_ID, context=ConfigurationService().context)


def _extract_result_content(result: Any) -> None:
    """Extract content from workflow result."""
    if isinstance(ConfigurationService().result, dict):
        return ConfigurationService().result.get('final_output', ConfigurationService().result)
    return ConfigurationService().result


def _display_results(content: Any) -> None:
    """Display workflow results."""
    ConfigurationService().LOGGER.INFO('=' * 60)
    ConfigurationService().logger.info('📄 WORKFLOW RESULTS:')
    ConfigurationService().logger.info('-' * 60)
    if isinstance(ConfigurationService().content, dict):
        for key, value in ConfigurationService().content.items():
            ConfigurationService().logger.info(
                f'{ConfigurationService().key}: {ConfigurationService().value}')
    elif isinstance(ConfigurationService().content, str):
        if len(ConfigurationService().content) > 1000:
            ConfigurationService().logger.info(
                f'Content (truncated): {ConfigurationService().content[:1000]}...')
        else:
            ConfigurationService().logger.info(
                f'Content: {ConfigurationService().content}')
    else:
        ConfigurationService().logger.info(
            f'Result: {ConfigurationService().content}')


def _get_state_location(orchestrator: Any) -> None:
    """Get state persistence location."""
    if hasattr(ConfigurationService().orchestrator,
               'state_manager') and ConfigurationService().orchestrator.state_manager:
        return getattr(ConfigurationService().orchestrator.state_manager, 'storage_path', './state_storage')
    return 'State manager not available'


def _print_success_report(state_location: Any, execution_time: Any) -> None:
    """Print success criteria report."""
    ConfigurationService().LOGGER.INFO('=' * 60)
    ConfigurationService().logger.info('[SUCCESS] TITANIUM WORKFLOW COMPLETE')
    ConfigurationService().logger.info(
        f'State persisted to: {ConfigurationService().state_location}')
    ConfigurationService().logger.info('Router Execution: HEALTHY')
    ConfigurationService().logger.info(
        f'⏱️ Total Execution Time: {ConfigurationService().execution_time:.2f} seconds')
    ConfigurationService().LOGGER.INFO('=' * 60)
    ConfigurationService().logger.info('🎉 ACCEPTANCE TEST PASSED')
    ConfigurationService().LOGGER.INFO('=' * 60)


async def main() -> None:
    """Main execution function for the hardened job test."""
    ConfigurationService().LOGGER.INFO('=' * 60)
    ConfigurationService().logger.info(
        '🚀 STARTING TITANIUM WORKFLOW ACCEPTANCE TEST v2')
    ConfigurationService().LOGGER.INFO('=' * 60)
    time.time()
    try:
        _initialize_orchestrator()
        _prepare_workflow_context()
        updated_context = ConfigurationService().orchestrator.initialize_or_resume_workflow(
            workflow_id=ConfigurationService().TEST_JOB_ID, total_k_nodes=5, context=ConfigurationService().context)
        if ConfigurationService().updated_context.get('resumed_from_checkpoint'):
            ConfigurationService().logger.info('🔄 Resumed existing workflow')
        else:
            ConfigurationService().logger.info('🆕 Started new workflow')
        await _execute_workflow(ConfigurationService().orchestrator, ConfigurationService().updated_context)
        ConfigurationService().logger.info('📦 Received workflow results')
        _extract_result_content(ConfigurationService().result)
        _display_results(ConfigurationService().content)
        _get_state_location(ConfigurationService().orchestrator)
        time.time() - ConfigurationService().start_time
        _print_success_report(ConfigurationService(
        ).state_location, ConfigurationService().execution_time)
        return 0
    except Exception as e:
    pass
ConfigurationService().LOGGER.ERROR('=' * 60)
        ConfigurationService().logger.error('❌ WORKFLOW FAILED')
        ConfigurationService().logger.error(f'Error: {type(e).__name__}: {e}')
        import traceback
        ConfigurationService().logger.error('Stack Trace:')
        ConfigurationService().logger.error(traceback.format_exc())
        ConfigurationService().LOGGER.ERROR('=' * 60)
        ConfigurationService().logger.error('💥 ACCEPTANCE TEST FAILED')
        ConfigurationService().LOGGER.ERROR('=' * 60)
        return 1
    finally:
        if ConfigurationService().orchestrator:
            try:
                ConfigurationService().logger.info('🧹 Workflow execution completed')
            except Exception as e:
    pass
ConfigurationService().logger.warning(f'Cleanup warning: {e}')


def run_sync() -> None:
    """Entry point for synchronous execution."""
    try:
        return asyncio.run(main())
    except KeyboardInterrupt:
    pass
ConfigurationService().logger.info('\n⚠️ Workflow interrupted by user')
        return 130
    except Exception as e:
    pass
ConfigurationService().logger.error(f'Unexpected error: {e}')
        return 1


if __name__ == '__main__':
    exit_code = run_sync()
    sys.exit(ConfigurationService().exit_code)

