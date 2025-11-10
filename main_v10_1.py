# File: main_v10_1.py  
# Version: 10.1 (Feedback-Driven Adaptation)

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

from core_v10_1 import (
    CONFIG, WorkflowContext, MainGraphState,
    FileIOError, CostCeilingExceededError
)
from agent_swarm_v10_1 import get_graph_app, PIISanitizerAgent
from langgraph.checkpoint.redis import RedisSaver

logger = logging.getLogger("main_v10_1")

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
    
    logger.info(f"v10.1 Logging initialized: {CONFIG.logging_config.log_file}")

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

async def run_workflow_async(
    job_input_path: str,
    master_resume_path: str,
    debug_mode: bool = False
) -> Dict[str, Any]:
    """Run workflow asynchronously with feedback-driven adaptation"""
    
    logger.info(f"===== Starting v10.1 Feedback-Driven Workflow ({datetime.now().isoformat()}) =====")
    
    job_input_data = load_job_input(job_input_path)
    master_resume = load_job_input(master_resume_path)
    
    company = job_input_data.get('company_name', 'N/A')
    title = job_input_data.get('job_title', 'N/A')
    
    logger.info(f"Job: {company} - {title}")
    
    redis_client = redis.Redis(
        host=CONFIG.redis_config.host,
        port=CONFIG.redis_config.port,
        db=CONFIG.redis_config.db
    )
    
    context = WorkflowContext(CONFIG, redis_client)
    logger.info("Initialized WorkflowContext with feedback-driven dependencies")
    
    checkpointer = RedisSaver(
        host=CONFIG.redis_config.host,
        port=CONFIG.redis_config.port,
        db=CONFIG.redis_config.db
    )
    
    app = get_graph_app(checkpointer, context, enable_hil=False)
    logger.info("Compiled LangGraph workflow with feedback-driven agents")
    
    sanitizer = PIISanitizerAgent(context)
    sanitized_resume = sanitizer.run(master_resume)
    logger.info("PII sanitization complete")
    
    workflow_id = str(uuid.uuid4())
    run_config = {"configurable": {"thread_id": workflow_id}}
    
    redis_client.set("current_workflow_id", workflow_id, ex=3600)
    
    initial_state = MainGraphState()
    initial_state.resume.master_resume = master_resume
    initial_state.resume.sanitized_resume = sanitized_resume
    initial_state.job.raw_jd = job_input_data['job_description']
    initial_state.job.company = job_input_data['company_name']
    initial_state.job.job_title = job_input_data['job_title']
    initial_state.metadata.workflow_id = workflow_id
    
    state_dict = initial_state.to_dict()
    
    logger.info(f"Workflow ID: {workflow_id}")
    
    try:
        final_state_dict = await asyncio.to_thread(
            app.invoke,
            state_dict,
            run_config
        )
        
        final_state = MainGraphState.from_dict(final_state_dict)
        
        cache_stats = context.cache_manager.get_stats()
        logger.info(f"Cache performance: {cache_stats}")
        
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        logger.info(f"Total workflow cost: ${cost_summary['total_workflow_cost']:.4f}")
        
        return {
            "status": "SUCCESS",
            "workflow_id": workflow_id,
            "cost": cost_summary['total_workflow_cost'],
            "cache_stats": cache_stats
        }
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        return {
            "status": "FAILED_FATAL",
            "workflow_id": workflow_id,
            "error": str(e)
        }
    
    finally:
        logger.info(f"===== v10.1 Workflow Complete =====")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Resume Generation Engine v10.1")
    parser.add_argument('-j', '--job', required=True, help='Path to job_input.json')
    parser.add_argument('-m', '--master', required=True, help='Path to master_resume.json')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    setup_logging(debug_mode=args.debug)
    
    result = asyncio.run(run_workflow_async(
        args.job,
        args.master,
        debug_mode=args.debug
    ))
    
    print("\n" + "="*80)
    print(f"WORKFLOW RESULT: {result['status']}")
    print(f"Workflow ID: {result.get('workflow_id')}")
    
    if 'cost' in result:
        print(f"Total Cost: ${result['cost']:.4f}")
    
    if 'cache_stats' in result:
        stats = result['cache_stats']
        print(f"Cache Hit Rate: {stats['hit_rate_pct']:.1f}%")
    
    print("="*80)
    
    if result['status'] == 'SUCCESS':
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

# ============================================================================
# END OF main_v10_1.py
# ============================================================================
