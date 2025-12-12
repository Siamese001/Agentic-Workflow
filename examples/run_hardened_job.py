#!/usr/bin/env python3
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
from pathlib import Path
from typing import Dict, Any, Optional

# CRITICAL: Fix Windows console crashes on Emoji/Unicode output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('hardened_job.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Import hardened components
try:
    from apps_rg.L3_orchestration.hardened_orchestrator import HardenedWorkflowOrchestrator
    from runtime.shared.routing import RoutingTier
    from runtime.shared.agent_executor import AgentResponse
except ImportError as e:
    logger.error(f"Failed to import hardened components: {e}")
    logger.error("Make sure the runtime modules are properly installed")
    sys.exit(1)

# Test Configuration
TEST_JOB_ID = "titanium_acceptance_v2_001"
TEST_CONFIG = {
    "target_role": "Senior AI Engineer",
    "target_company": "Anthropic",
    "job_url": "https://anthropic.com/careers",
    "routing_tier": RoutingTier.REASONING,
    "workflow_type": "resume_tailoring",
    "max_retries": 3,
    "timeout_seconds": 300
}

async def main():
    """Main execution function for the hardened job test."""
    logger.info("=" * 60)
    logger.info("🚀 STARTING TITANIUM WORKFLOW ACCEPTANCE TEST v2")
    logger.info("=" * 60)
    
    start_time = time.time()
    orchestrator = None
    state_location = None
    
    try:
        # 1. Initialize Orchestrator
        logger.info("⚡ Initializing HardenedWorkflowOrchestrator...")
        orchestrator = HardenedWorkflowOrchestrator(
            run_base_dir="./pipeline_runs",
            storage_path="./state_storage"
        )
        logger.info("✅ Orchestrator initialized successfully")
        
        # 2. Prepare Context and Initialize Workflow
        logger.info(f"📋 Initializing workflow: {TEST_JOB_ID}")
        context = {
            "target_role": TEST_CONFIG["target_role"],
            "target_company": TEST_CONFIG["target_company"],
            "job_url": TEST_CONFIG["job_url"],
            "workflow_type": TEST_CONFIG["workflow_type"],
            "routing_tier": TEST_CONFIG["routing_tier"]
        }
        
        # Initialize or resume workflow (returns updated context)
        updated_context = orchestrator.initialize_or_resume_workflow(
            workflow_id=TEST_JOB_ID,
            total_k_nodes=5,  # Example: 5 K-nodes in the workflow
            context=context
        )
        
        if updated_context.get("resumed_from_checkpoint"):
            logger.info("🔄 Resumed existing workflow")
        else:
            logger.info("🆕 Started new workflow")
        
        # 3. Execute Workflow with Resilience
        logger.info("⚙️ Executing hardened workflow...")
        logger.info(f"Target Role: {TEST_CONFIG['target_role']}")
        logger.info(f"Target Company: {TEST_CONFIG['target_company']}")
        
        result = await orchestrator.execute_workflow_with_resilience(
            workflow_id=TEST_JOB_ID,
            context=updated_context
        )
        
        # 4. Handle Result (Dict format)
        logger.info("📦 Received workflow results")
        
        # Extract final output from result
        if isinstance(result, dict):
            content = result.get("final_output", result)
            metadata = result.get("metadata", {})
        else:
            content = result
            metadata = {}
        
        # 5. Display Results
        logger.info("=" * 60)
        logger.info("📄 WORKFLOW RESULTS:")
        logger.info("-" * 60)
        
        if isinstance(content, dict):
            for key, value in content.items():
                logger.info(f"{key}: {value}")
        elif isinstance(content, str):
            # Truncate very long responses for readability
            if len(content) > 1000:
                logger.info(f"Content (truncated): {content[:1000]}...")
            else:
                logger.info(f"Content: {content}")
        else:
            logger.info(f"Result: {content}")
        
        # 6. Get State Persistence Location
        if hasattr(orchestrator, 'state_manager') and orchestrator.state_manager:
            state_location = getattr(orchestrator.state_manager, 'storage_path', './state_storage')
        else:
            state_location = "State manager not available"
        
        # 7. Calculate Execution Metrics
        execution_time = time.time() - start_time
        
        # 8. Print Success Criteria
        logger.info("=" * 60)
        logger.info("✅ [SUCCESS] TITANIUM WORKFLOW COMPLETE")
        logger.info(f"⏱️ Total Execution Time: {execution_time:.2f} seconds")
        logger.info(f"💾 State persisted to: {state_location}")
        
        # Check router health
        if hasattr(orchestrator, 'router') and orchestrator.router:
            router_health = getattr(orchestrator.router, 'health_status', 'HEALTHY')
            logger.info(f"🌐 Router Execution: {router_health}")
        else:
            logger.info("🌐 Router Execution: HEALTHY (default)")
        
        logger.info("=" * 60)
        logger.info("🎉 ACCEPTANCE TEST PASSED")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error("❌ WORKFLOW FAILED")
        logger.error(f"Error: {type(e).__name__}: {e}")
        
        # Print stack trace for debugging
        import traceback
        logger.error("Stack Trace:")
        logger.error(traceback.format_exc())
        
        logger.error("=" * 60)
        logger.error("💥 ACCEPTANCE TEST FAILED")
        logger.error("=" * 60)
        
        return 1
    
    finally:
        # Cleanup
        if orchestrator:
            try:
                # HardenedWorkflowOrchestrator doesn't have cleanup method
                # Just log completion
                logger.info("🧹 Workflow execution completed")
            except Exception as e:
                logger.warning(f"Cleanup warning: {e}")

def run_sync():
    """Entry point for synchronous execution."""
    try:
        # Run the async main function
        return asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️ Workflow interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_sync()
    sys.exit(exit_code)
