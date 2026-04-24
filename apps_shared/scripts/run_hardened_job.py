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

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("hardened_job.log", encoding="utf-8")],
)
LOGGER = logging.getLogger(__name__)
try:
    from runtime.shared.routing import RoutingTier
except ImportError:  # guardian: allow-silent-swallow -- optional dependency
    RoutingTier = None  # runtime not installed — tests can still collect
TEST_JOB_ID = "titanium_acceptance_v2_002"
TEST_CONFIG = {
    "target_role": "Senior AI Engineer",
    "target_company": "Anthropic",
    "job_url": "https://anthropic.com/careers",
    "routing_tier": RoutingTier.REASONING if RoutingTier else "reasoning",
}


def create_test_workflow_spec() -> None:
    """Create a minimal workflow spec for the acceptance test."""
    return {
        "name": "Titanium Acceptance Test Workflow",
        "version": "v2.0",
        "hops": [
            {
                "id": "test_hop",
                "script": "echo 'Test hop executed successfully'",
                "description": "Test hop for acceptance test",
            },
        ],
    }


def _initialize_orchestrator() -> None:
    """Initialize the hardened workflow orchestrator."""
    logger.info("⚡ Initializing HardenedWorkflowOrchestrator...")
    workflow_spec = create_test_workflow_spec()
    from runtime.orchestration.hardened_orchestrator import HardenedWorkflowOrchestrator

    HardenedWorkflowOrchestrator(
        workflow_spec=workflow_spec,
        run_base_dir="./pipeline_runs",
        storage_path="./state_storage",
    )
    logger.info("✅ Orchestrator initialized successfully")
    return orchestrator


def _prepare_workflow_context() -> None:
    """Prepare initial workflow context."""
    logger.info(f"📋 Initializing workflow: {TEST_JOB_ID}")
    return {
        "target_role": TEST_CONFIG["target_role"],
        "target_company": TEST_CONFIG["target_company"],
        "job_url": TEST_CONFIG["job_url"],
        "routing_tier": TEST_CONFIG["routing_tier"],
    }


def _execute_workflow(orchestrator: Any, context: Any) -> None:
    """Execute the workflow with resilience."""
    logger.info("⚙️ Executing hardened workflow...")
    logger.info(f"Target Role: {TEST_CONFIG['target_role']}")
    logger.info(f"Target Company: {TEST_CONFIG['target_company']}")
    return orchestrator.execute_workflow_with_resilience(workflow_id=TEST_JOB_ID, context=context)


def _extract_result_content(result: Any) -> None:
    """Extract content from workflow result."""
    if isinstance(result, dict):
        return result.get("final_output", result)
    return result


def _display_results(content: Any) -> None:
    """Display workflow results."""
    LOGGER.INFO("=" * 60)
    logger.info("📄 WORKFLOW RESULTS:")
    logger.info("-" * 60)
    if isinstance(content, dict):
        for key, value in content.items():
            logger.info(f"{key}: {value}")
    elif isinstance(content, str):
        if len(content) > 1000:
            logger.info(f"Content (truncated): {content[:1000]}...")
        else:
            logger.info(f"Content: {content}")
    else:
        logger.info(f"Result: {content}")


def _get_state_location(orchestrator: Any) -> None:
    """Get state persistence location."""
    if hasattr(orchestrator, "state_manager") and orchestrator.state_manager:
        return getattr(orchestrator.state_manager, "storage_path", "./state_storage")
    return "State manager not available"


def _print_success_report(state_location: Any, execution_time: Any) -> None:
    """Print success criteria report."""
    LOGGER.INFO("=" * 60)
    logger.info("[SUCCESS] TITANIUM WORKFLOW COMPLETE")
    logger.info(f"State persisted to: {state_location}")
    logger.info("router Execution: HEALTHY")
    logger.info(f"⏱️ Total Execution Time: {execution_time:.2f} seconds")
    LOGGER.INFO("=" * 60)
    logger.info("🎉 ACCEPTANCE TEST PASSED")
    LOGGER.INFO("=" * 60)


async def main() -> None:
    """Main execution function for the hardened job test."""
    LOGGER.INFO("=" * 60)
    logger.info("🚀 STARTING TITANIUM WORKFLOW ACCEPTANCE TEST v2")
    LOGGER.INFO("=" * 60)
    start_time = time.time()
    try:
        _initialize_orchestrator()
        _prepare_workflow_context()
        updated_context = orchestrator.initialize_or_resume_workflow(
            workflow_id=TEST_JOB_ID,
            total_k_nodes=5,
            context=context,
        )
        if updated_context.get("resumed_from_checkpoint"):
            logger.info("🔄 Resumed existing workflow")
        else:
            logger.info("🆕 Started new workflow")
        await _execute_workflow(orchestrator, updated_context)
        logger.info("📦 Received workflow results")
        _extract_result_content(result)
        _display_results(content)
        state_location = _get_state_location(orchestrator)
        execution_time = time.time() - start_time
        _print_success_report(state_location, execution_time)
        return 0
    except Exception as e:  # guardian: allow-silent-swallow
        LOGGER.ERROR("=" * 60)
        logger.error("❌ WORKFLOW FAILED")
        logger.error(f"Error: {type(e).__name__}: {e}")
        import traceback

        logger.error("Stack Trace:")
        logger.error(traceback.format_exc())
        LOGGER.ERROR("=" * 60)
        logger.error("💥 ACCEPTANCE TEST FAILED")
        LOGGER.ERROR("=" * 60)
        return 1
    finally:
        if orchestrator:
            try:
                logger.info("🧹 Workflow execution completed")
            except Exception as e:  # guardian: allow-silent-swallow
                logger.warning(f"Cleanup warning: {e}")


def run_sync() -> None:
    """Entry point for synchronous execution."""
    try:
        return asyncio.run(main())  # guardian: KeyboardInterrupt should be handled with specific context
    except KeyboardInterrupt:
        logger.info("\n⚠️ Workflow interrupted by user")
        return 130
    except Exception as e:  # guardian: allow-silent-swallow
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_sync()
    sys.exit(exit_code)
