# File: main_v10_0.py
# Version: 10.0 (Modularity, Caching, Async Performance)
#
# v10.0 MAJOR CHANGES:
# ROW 4: Uses WorkflowContext for dependency injection
# ROW 5: Integrated caching layer
# ROW 6: Async workflow execution

import os
import sys
import json
import logging
import asyncio
import argparse
import uuid
import redis
from datetime import datetime
from typing import Dict, Any

from core_v10_0 import (
    CONFIG, WorkflowContext, MainGraphState,
    FileIOError, CostCeilingExceededError
)
from agent_swarm_v10_0 import get_graph_app, PIISanitizerAgent
from langgraph.checkpoint.redis import RedisSaver

logger = logging.getLogger("main_v10_0")

# ============================================================================
# SETUP
# ============================================================================

def setup_logging(debug_mode: bool = False):
    """Configure logging"""
    log_dir = os.path.dirname(CONFIG.logging_config.log_file)
    os.makedirs(log_dir, exist_ok=True)
    
    level = logging.DEBUG if debug_mode else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(CONFIG.logging_config.log_file),
            logging.StreamHandler()
        ]
    )
    
    logger.info(f"v10.0 Logging initialized: {CONFIG.logging_config.log_file}")

def load_job_input(path: str) -> Dict[str, Any]:
    """Load job input JSON"""
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded job input: {path}")
        return data
    except (IOError, OSError) as e:
        raise FileIOError(f"Failed to load {path}: {e}")
    except json.JSONDecodeError as e:
        raise FileIOError(f"Invalid JSON in {path}: {e}")

# ============================================================================
# ROW 6: ASYNC WORKFLOW EXECUTION
# ============================================================================

async def run_workflow_async(
    job_input_path: str,
    master_resume_path: str,
    debug_mode: bool = False
) -> Dict[str, Any]:
    """Run workflow asynchronously with caching and dependency injection"""
    
    logger.info(f"===== Starting v10.0 Async Workflow ({datetime.now().isoformat()}) =====")
    
    # Load inputs
    job_input_data = load_job_input(job_input_path)
    master_resume = load_job_input(master_resume_path)
    
    company = job_input_data.get('company_name', 'N/A')
    title = job_input_data.get('job_title', 'N/A')
    
    logger.info(f"Job: {company} - {title}")
    
    # Row 4: Initialize dependency injection context
    redis_client = redis.Redis(
        host=CONFIG.redis_config.host,
        port=CONFIG.redis_config.port,
        db=CONFIG.redis_config.db
    )
    
    context = WorkflowContext(CONFIG, redis_client)
    logger.info("Initialized WorkflowContext with dependency injection")
    
    # Initialize checkpointer
    checkpointer = RedisSaver(
        host=CONFIG.redis_config.host,
        port=CONFIG.redis_config.port,
        db=CONFIG.redis_config.db
    )
    
    # Build graph with injected context
    app = get_graph_app(checkpointer, context, enable_hil=False)
    logger.info("Compiled LangGraph workflow with injected context")
    
    # Sanitize PII locally (v9.9 security preserved)
    sanitizer = PIISanitizerAgent()
    sanitized_resume = sanitizer.run(master_resume)
    logger.info("PII sanitization complete (local processing)")
    
    # Generate workflow ID
    workflow_id = str(uuid.uuid4())
    run_config = {"configurable": {"thread_id": workflow_id}}
    
    # Build initial state (Row 4: Modular state)
    initial_state = MainGraphState()
    initial_state.resume.master_resume = master_resume
    initial_state.resume.sanitized_resume = sanitized_resume
    initial_state.job.raw_jd = job_input_data['job_description']
    initial_state.job.company = job_input_data['company_name']
    initial_state.job.job_title = job_input_data['job_title']
    initial_state.metadata.workflow_id = workflow_id
    
    state_dict = initial_state.to_dict()
    
    logger.info(f"Workflow ID: {workflow_id}")
    logger.info("Executing async workflow with caching enabled...")
    
    try:
        # Row 6: Async invocation
        final_state_dict = await asyncio.to_thread(
            app.invoke,
            state_dict,
            run_config
        )
        
        final_state = MainGraphState.from_dict(final_state_dict)
        
        # Get cache stats (Row 5)
        cache_stats = context.cache_manager.get_stats()
        logger.info(f"Cache performance: {cache_stats}")
        
        # Get cost summary
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        logger.info(f"Total workflow cost: ${cost_summary['total_workflow_cost']:.4f}")
        
        # Validation results
        validation = final_state.artifacts.artifacts.get('validation_results', {})
        if validation.get('overall_passed', False):
            logger.info("✓ Workflow completed successfully")
            status = "SUCCESS"
        else:
            logger.warning("✗ Workflow completed with QA failures")
            status = "FAILED_QA"
        
        return {
            "status": status,
            "workflow_id": workflow_id,
            "validation": validation,
            "cost": cost_summary['total_workflow_cost'],
            "cache_stats": cache_stats,
            "artifacts": final_state.artifacts.artifacts
        }
        
    except CostCeilingExceededError as e:
        logger.error(f"Cost ceiling exceeded: {e}")
        return {
            "status": "FAILED_COST",
            "workflow_id": workflow_id,
            "error": str(e)
        }
    
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        return {
            "status": "FAILED_FATAL",
            "workflow_id": workflow_id,
            "error": str(e)
        }
    
    finally:
        logger.info(f"===== v10.0 Workflow Complete =====")

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Resume Generation Engine v10.0")
    parser.add_argument('-j', '--job', required=True, help='Path to job_input.json')
    parser.add_argument('-m', '--master', required=True, help='Path to master_resume.json')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(debug_mode=args.debug)
    
    # Run async workflow
    result = asyncio.run(run_workflow_async(
        args.job,
        args.master,
        debug_mode=args.debug
    ))
    
    # Print result summary
    print("\n" + "="*80)
    print(f"WORKFLOW RESULT: {result['status']}")
    print(f"Workflow ID: {result.get('workflow_id')}")
    
    if 'cost' in result:
        print(f"Total Cost: ${result['cost']:.4f}")
    
    if 'cache_stats' in result:
        stats = result['cache_stats']
        print(f"Cache Hit Rate: {stats['hit_rate_pct']:.1f}% ({stats['hits']}/{stats['hits']+stats['misses']})")
    
    if 'validation' in result:
        val = result['validation']
        print(f"QA Validation: {'PASSED' if val.get('overall_passed') else 'FAILED'}")
        if not val.get('overall_passed'):
            print(f"Failed Checks: {len(val.get('checks', []))}")
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    
    print("="*80)
    
    # Exit code
    if result['status'] == 'SUCCESS':
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

# ============================================================================
# END OF main_v10_0.py
# ============================================================================