# File: main_v10_2.py  
# Version: 10.2 (ChromaDB Semantic RAG)
#
# v10.2 MAJOR CHANGES:
# - Imports and versioning updated to v10.2
# - Added chromadb import and client initialization
# - Injected chromadb_client into WorkflowContext

import os
import sys
import json
import logging
import asyncio
import argparse
import uuid
import redis
import chromadb # v10.2: Added
from chromadb.utils import embedding_functions # v10.2: Added
from datetime import datetime
from typing import Dict, Any

# v10.2: Import from new core
from core_v10_2 import (
    ConfigV10_2, WorkflowContext, MainGraphState,
    FileIOError, CostCeilingExceededError,
    CacheManager, CostTracker, FeedbackLogReader, ProposedRulesLoader
)
# v10.2: Import from new orchestration/stacks
from agent_orchestration_v10_2 import get_graph_app
from agent_stacks_v10_2 import PIISanitizerAgent
from langgraph.checkpoint.redis import RedisSaver

logger = logging.getLogger("main_v10_2")

# v10.2: Load new config class
CONFIG = ConfigV10_2("master_config_v10_2.json")

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
    
    logger.info(f"v10.2 Logging initialized: {CONFIG.logging_config.log_file}")

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
    debug_mode: bool = False,
    enable_hil: bool = True
) -> Dict[str, Any]:
    """Run workflow asynchronously with v10.2 ChromaDB RAG"""
    
    logger.info(f"===== Starting v10.2 Semantic RAG Workflow ({datetime.now().isoformat()}) =====")
    
    job_input_data = load_job_input(job_input_path)
    master_resume = load_job_input(master_resume_path)
    
    company = job_input_data.get('company_name', 'N/A')
    title = job_input_data.get('job_title', 'N/A')
    
    logger.info(f"Job: {company} - {title}")
    
    # --- v10.2: COMPOSITION ROOT START ---
    
    # 1. Initialize Redis Client
    redis_client = redis.Redis(
        host=CONFIG.redis_config.host,
        port=CONFIG.redis_config.port,
        db=CONFIG.redis_config.db
    )
    
    # 2. v10.2: Initialize ChromaDB Client
    if CONFIG.chromadb_config.use_http_client:
        chromadb_client = chromadb.HttpClient(
            host=CONFIG.chromadb_config.host,
            port=CONFIG.chromadb_config.port
        )
    else:
        chromadb_client = chromadb.PersistentClient(
            path=CONFIG.chromadb_config.persistent_path
        )
    logger.info("Initialized ChromaDB client for semantic RAG")

    # 3. Initialize Core Services
    cache_manager = CacheManager(
        redis_client,
        ttl_seconds=CONFIG.caching_config.cache_ttl_seconds
    )
    cost_tracker = CostTracker()
    feedback_reader = FeedbackLogReader(
        CONFIG.meta_loop_config.feedback_log_path
    )
    rules_loader = ProposedRulesLoader(
        CONFIG.meta_loop_config.proposed_rules_path
    )
    
    # 4. Initialize and Inject into WorkflowContext
    context = WorkflowContext(
        config=CONFIG,
        redis_client=redis_client,
        chromadb_client=chromadb_client, # v10.2: Injected
        cache_manager=cache_manager,
        cost_tracker=cost_tracker,
        feedback_reader=feedback_reader,
        rules_loader=rules_loader
    )
    logger.info("Initialized WorkflowContext with v10.2 dependencies (incl. ChromaDB)")
    
    # --- v10.2: COMPOSITION ROOT END ---
    
    checkpointer = RedisSaver(
        host=CONFIG.redis_config.host,
        port=CONFIG.redis_config.port,
        db=CONFIG.redis_config.db
    )
    
    app = get_graph_app(checkpointer, context, enable_hil=enable_hil)
    if enable_hil:
        logger.info("Compiled LangGraph workflow with HIL (Human-in-the-Loop) ENABLED")
    else:
        logger.info("Compiled LangGraph workflow with HIL (Human-in-the-Loop) DISABLED")
    
    sanitizer = PIISanitizerAgent(context)
    sanitized_resume = sanitizer.run(master_resume)
    logger.info("PII sanitization complete")
    
    workflow_id = str(uuid.uuid4())
    context.workflow_id = workflow_id # Set workflow_id on the context
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
        final_state_dict = None
        
        # Run async, streaming logs
        async for s in app.astream(state_dict, run_config):
            node_name = list(s.keys())[0]
            logger.info(f"--- Executing Node: {node_name} ---")
            if debug_mode:
                logger.debug(json.dumps(s[node_name], indent=2))
            
            # Check for HIL pause
            if node_name == "HIL_PAUSE":
                logger.warning("="*80)
                logger.warning("🛑 WORKFLOW PAUSED: HUMAN INPUT REQUIRED 🛑")
                logger.warning(f"Please review the strategy and provide feedback for workflow: {workflow_id}")
                logger.warning("="*80)
            
            final_state_dict = s[node_name]
        
        # Get final state from the last message
        final_state = MainGraphState.from_dict(final_state_dict)
        
        cache_stats = context.cache_manager.get_stats()
        logger.info(f"Cache performance: {cache_stats}")
        
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        logger.info(f"Total workflow cost: ${cost_summary['total_workflow_cost']:.4f}")
        
        # v10.2: Cleanup ChromaDB collection for this workflow
        try:
            logger.info(f"Cleaning up ChromaDB collection for workflow: {workflow_id}")
            collection = chromadb_client.get_collection(
                name=CONFIG.chromadb_config.default_collection_name
            )
            collection.delete(where={"workflow_id": workflow_id})
            logger.info("ChromaDB cleanup complete.")
        except Exception as e:
            logger.warning(f"Failed to cleanup ChromaDB collection: {e}")

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
        logger.info(f"===== v10.2 Workflow Complete =====")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Resume Generation Engine v10.2")
    parser.add_argument('-j', '--job', required=True, help='Path to job_input.json')
    parser.add_argument('-m', '--master', required=True, help='Path to master_resume.json')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-hil', action='store_true', help='Disable Human-in-the-Loop')
    
    args = parser.parse_args()
    
    setup_logging(debug_mode=args.debug)
    
    result = asyncio.run(run_workflow_async(
        args.job,
        args.master,
        debug_mode=args.debug,
        enable_hil=not args.no_hil
    ))
    
    print("\n" + "="*80)
    print(f"WORKFLOW RESULT: {result['status']}")
    print(f"Workflow ID: {result.get('workflow_id')}")
    
    if 'cost' in result:
        print(f"Total Cost: ${result['cost']:.4f}")
    
    if 'cache_stats' in result:
        stats = result['cache_stats']
        print(f"Cache Hit Rate: {stats['hit_rate_pct']:.1f}%")
        
    if 'final_artifacts' in result:
        print("\n--- Final Artifacts ---")
        print(json.dumps(result['final_artifacts'], indent=2))
    
    print("="*80)
    
    if result['status'] == 'SUCCESS':
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

# ============================================================================
# END OF main_v10_2.py
# ============================================================================