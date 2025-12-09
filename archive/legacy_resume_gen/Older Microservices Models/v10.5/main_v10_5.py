# File: main_v10_5.py  
# Version: 10.5 (Refactored)
#
# v10.5 REFACTOR CHANGES:
# - REMOVED: All duplicated Composition Root logic (68 lines).
# - ADDED: Call to core_v10_5.create_workflow_context() helper.
# - REMOVED: All duplicated ChromaDB cleanup logic (11 lines).
# - ADDED: Call to core_v10_5.cleanup_workflow_chroma_collection() helper.
# - REMOVED: Unnecessary imports (redis, chromadb, service classes).
#
# v10.5 MAJOR CHANGES:
# - IMPLEMENTED (Fix #8, #13): Composition root (run_workflow_async)
#   now instantiates and injects MetricsCollector and SemanticValidator
#   into the WorkflowContext.
# - IMPLEMENTED (Fix #8): Added logging for final metrics summary.
# - FIXED: All v10_4 imports and class names updated to v10_5
#   (e.g., core_v10_5, agent_orchestration_v10_5, ConfigV10_5).
# - FIXED: Changed config file name to master_config_v10_5.json.
# - FIXED: Updated MainGraphState.from_dict call for new state.

import os
import sys
import json
import logging
import asyncio
import argparse
import uuid
# import redis # v10.5 REFACTOR: Removed
# import chromadb # v10.5 REFACTOR: Removed
# from chromadb.utils import embedding_functions # v10.5 REFACTOR: Removed
from datetime import datetime
from typing import Dict, Any

# v10.5: Import from new core
from core_v10_5 import (
    ConfigV10_5, WorkflowContext, MainGraphState,
    FileIOError, CostCeilingExceededError, WorkflowError,
    # v10.5: Import all services to be injected
    # CacheManager, CostTracker, FeedbackLogReader, ProposedRulesLoader, # v10.5 REFACTOR: Removed
    # PromptTemplateManager, ResponseValidator, ContextBudgetManager, # v10.5 REFACTOR: Removed
    # MetricsCollector, SemanticValidator # v10.5 REFACTOR: Removed
    # v10.5 REFACTOR: Import new helper functions
    create_workflow_context, cleanup_workflow_chroma_collection
)
# v10.5: Import from new orchestration/stacks
from agent_orchestration_v10_5 import get_graph_app
from agent_stacks_v10_5 import PIISanitizerAgent
try:
    from langgraph.checkpoint.redis import RedisSaver
except ImportError:
    from langgraph.checkpoint.sqlite import SqliteSaver as RedisSaver

# v10.5: Logger name updated
logger = logging.getLogger("main_v10_5")

def setup_logging(config: ConfigV10_5, debug_mode: bool = False):
    """Configure logging, now accepts a config object."""
    log_dir = os.path.dirname(config.logging_config.log_file)
    os.makedirs(log_dir, exist_ok=True)
    
    level = logging.DEBUG if debug_mode else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.logging_config.log_file),
            logging.StreamHandler()
        ]
    )
    
    # Also configure metrics logger
    metrics_log_path = config.logging_config.metrics_log_path
    metrics_logger = logging.getLogger("core_v10_5.MetricsCollector")
    metrics_logger.setLevel(logging.INFO)
    try:
        metrics_logger.addHandler(logging.FileHandler(metrics_log_path))
    except (IOError, OSError) as e:
        logging.error(f"Failed to add file handler for metrics logger: {e}")
    
    logger.info(f"v10.5 Logging initialized: {config.logging_config.log_file}")
    logger.info(f"v10.5 Metrics logging to: {metrics_log_path}")

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
    config: ConfigV10_5, # v10.5
    job_input_path: str,
    master_resume_path: str,
    debug_mode: bool = False,
    enable_hil: bool = True
) -> Dict[str, Any]:
    """Run workflow asynchronously with v10.5 Hybrid RAG & Validation"""
    
    logger.info(f"===== Starting v10.5 Instructional Injection Workflow =====")
    
    job_input_data = load_job_input(job_input_path)
    master_resume = load_job_input(master_resume_path)
    
    company = job_input_data.get('company_name', 'N/A')
    title = job_input_data.get('job_title', 'N/A')
    
    logger.info(f"Job: {company} - {title}")
    
    # --- v10.5: REFACTOR: COMPOSITION ROOT ---
    # Call the centralized helper function from core_v10_5
    context = create_workflow_context(config, db=config.redis_config.db)
    # --- v10.5: REFACTOR END ---
    
    checkpointer = RedisSaver(
        host=config.redis_config.host,
        port=config.redis_config.port,
        db=config.redis_config.db
    )
    
    app = get_graph_app(checkpointer, context, enable_hil=enable_hil)
    
    sanitizer = PIISanitizerAgent(context)
    sanitized_resume = sanitizer.run(master_resume)
    logger.info("PII sanitization complete")
    
    workflow_id = str(uuid.uuid4())
    context.workflow_id = workflow_id # Set workflow_id on the context
    run_config = {"configurable": {"thread_id": workflow_id}}
    
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
        final_state_dict = None
        
        async for s in app.astream(state_dict, run_config):
            node_name = list(s.keys())[0]
            logger.info(f"--- Executing Node: {node_name} ---")
            if debug_mode:
                logger.debug(json.dumps(s[node_name], indent=2))
            
            if node_name == "HIL_PAUSE":
                logger.warning("="*80)
                logger.warning("🛑 WORKFLOW PAUSED: HUMAN INPUT REQUIRED 🛑")
                logger.warning(f"Please review and provide feedback for: {workflow_id}")
                logger.warning("="*80)
            
            final_state_dict = s[node_name]
        
        # v10.5: Check for rejection
        if "REJECT_JOB" in final_state_dict:
             logger.error(f"Workflow {workflow_id} REJECTED.")
             raise WorkflowError("Workflow rejected, likely due to prompt injection.")

        final_state = MainGraphState.from_dict(final_state_dict)
        
        cache_stats = context.cache_manager.get_stats()
        logger.info(f"Cache performance: {cache_stats}")
        
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        logger.info(f"Total workflow cost: ${cost_summary['total_workflow_cost']:.4f}")
        
        # v10.5 (Fix #8): Log metrics summary
        logger.info(f"--- Workflow Metrics Summary (v10.5) ---")
        for metric in context.metrics_collector.get_summary():
             logger.info(f"  - {metric['agent_name']}::{metric['task_name']} | {metric['duration_ms']:.2f}ms | Success: {metric['success']}")
        
        # v10.5 REFACTOR: Call centralized cleanup helper
        cleanup_workflow_chroma_collection(context)

        return {
            "status": "SUCCESS",
            "workflow_id": workflow_id,
            "cost": cost_summary['total_workflow_cost'],
            "cache_stats": cache_stats,
            "final_artifacts": final_state.artifacts.artifacts
        }
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        return {
            "status": "FAILED_FATAL",
            "workflow_id": workflow_id,
            "error": str(e)
        }
    
    finally:
        logger.info(f"===== v10.5 Workflow Complete =====")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Resume Generation Engine v10.5")
    parser.add_argument('-j', '--job', required=True, help='Path to job_input.json')
    parser.add_argument('-m', '--master', required=True, help='Path to master_resume.json')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-hil', action='store_true', help='Disable Human-in-the-Loop')
    
    args = parser.parse_args()
    
    # v10.5: Instantiate ConfigV10_5 here, ONCE.
    try:
        config = ConfigV10_5("master_config_v10_5.json")
    except Exception as e:
        print(f"FATAL: Failed to load master_config_v10_5.json: {e}", file=sys.stderr)
        sys.exit(1)
    
    setup_logging(config, debug_mode=args.debug)
    
    result = asyncio.run(run_workflow_async(
        config=config, # v10.5: Inject the config object
        job_input_path=args.job,
        master_resume_path=args.master,
        debug_mode=args.debug,
        enable_hil=not args.no_hil
    ))
    
    print("\n" + "="*80)
    print(f"WORKFLOW RESULT: {result['status']}")
    print(f"Workflow ID: {result.get('workflow_id')}")
    if result.get('status') == 'SUCCESS':
        print(f"Total Cost: ${result.get('cost', 0.0):.4f}")
        print(f"Cache Stats: {result.get('cache_stats')}")
    else:
        print(f"Error: {result.get('error')}")
    print("="*80)
    
    if result['status'] == 'SUCCESS':
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

# ============================================================================
# END OF main_v10_5.py
# ============================================================================