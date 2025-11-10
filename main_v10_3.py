# File: main_v10_3.py  
# Version: 10.3 (Instructional Injection)
#
# v10.3 MAJOR CHANGES:
# - Enforced Strict Dependency Injection: Removed the global `CONFIG`
#   singleton instance.
# - Eliminated Service Locator Pattern: `main()` now creates the `ConfigV10_3`
#   object and passes it to `run_workflow_async`.
# - True Composition Root: `run_workflow_async` now instantiates all 10+
#   core services (CacheManager, PromptTemplateManager, ResponseValidator,
#   ContextBudgetManager, etc.) and injects them into the
#   `WorkflowContext` constructor, which no longer creates its own dependencies.

import os
import sys
import json
import logging
import asyncio
import argparse
import uuid
import redis
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
from typing import Dict, Any

# v10.3: Import from new core
from core_v10_3 import (
    ConfigV10_3, WorkflowContext, MainGraphState,
    FileIOError, CostCeilingExceededError,
    # v10.3: Import all services to be injected
    CacheManager, CostTracker, FeedbackLogReader, ProposedRulesLoader,
    PromptTemplateManager, ResponseValidator, ContextBudgetManager
)
# v10.3: Import from new orchestration/stacks
from agent_orchestration_v10_3 import get_graph_app
from agent_stacks_v10_3 import PIISanitizerAgent
from langgraph.checkpoint.redis import RedisSaver

logger = logging.getLogger("main_v10_3")

# v10.3: DELETED the global CONFIG singleton instance.
# CONFIG = ConfigV10_2("master_config_v10_2.json") # GONE

def setup_logging(config: ConfigV10_3, debug_mode: bool = False):
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
    
    logger.info(f"v1S0.3 Logging initialized: {config.logging_config.log_file}")

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
    config: ConfigV10_3, # v10.3: Config is now injected
    job_input_path: str,
    master_resume_path: str,
    debug_mode: bool = False,
    enable_hil: bool = True
) -> Dict[str, Any]:
    """Run workflow asynchronously with v10.3 Hybrid RAG & Validation"""
    
    logger.info(f"===== Starting v10.3 Instructional Injection Workflow =====")
    
    job_input_data = load_job_input(job_input_path)
    master_resume = load_job_input(master_resume_path)
    
    company = job_input_data.get('company_name', 'N/A')
    title = job_input_data.get('job_title', 'N/A')
    
    logger.info(f"Job: {company} - {title}")
    
    # --- v10.3: TRUE COMPOSITION ROOT START ---
    
    # 1. Initialize Clients (Redis, ChromaDB)
    redis_client = redis.Redis(
        host=config.redis_config.host,
        port=config.redis_config.port,
        db=config.redis_config.db
    )
    
    if config.chromadb_config.use_http_client:
        chromadb_client = chromadb.HttpClient(
            host=config.chromadb_config.host,
            port=config.chromadb_config.port
        )
    else:
        chromadb_client = chromadb.PersistentClient(
            path=config.chromadb_config.persistent_path
        )
    logger.info("Initialized ChromaDB client (v10.3)")

    # 2. Initialize Core Services (All 7+ services)
    cache_manager = CacheManager(
        redis_client,
        ttl_seconds=config.caching_config.cache_ttl_seconds
    )
    cost_tracker = CostTracker()
    feedback_reader = FeedbackLogReader(
        config.meta_loop_config.feedback_log_path
    )
    rules_loader = ProposedRulesLoader(
        config.meta_loop_config.proposed_rules_path
    )
    
    # v10.3: Instantiate new services
    prompt_manager = PromptTemplateManager()
    response_validator = ResponseValidator()
    context_budget_manager = ContextBudgetManager(
        default_token_limit=config.performance_config.default_token_limit
    )
    
    # 3. Initialize and INJECT all services into WorkflowContext
    context = WorkflowContext(
        config=config, # v10.3: Pass the injected config
        redis_client=redis_client,
        chromadb_client=chromadb_client,
        cache_manager=cache_manager,
        cost_tracker=cost_tracker,
        feedback_reader=feedback_reader,
        rules_loader=rules_loader,
        prompt_manager=prompt_manager, # v10.3: Inject
        response_validator=response_validator, # v10.3: Inject
        context_budget_manager=context_budget_manager # v10.3: Inject
    )
    logger.info("Initialized WorkflowContext with v10.3 injected services")
    
    # --- v10.3: COMPOSITION ROOT END ---
    
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
        
        final_state = MainGraphState.from_dict(final_state_dict)
        
        cache_stats = context.cache_manager.get_stats()
        logger.info(f"Cache performance: {cache_stats}")
        
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        logger.info(f"Total workflow cost: ${cost_summary['total_workflow_cost']:.4f}")
        
        # v10.3: Cleanup ChromaDB collection for this workflow
        try:
            logger.info(f"Cleaning up ChromaDB collection for workflow: {workflow_id}")
            collection = chromadb_client.get_collection(
                name=config.chromadb_config.default_collection_name
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
        logger.info(f"===== v10.3 Workflow Complete =====")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Resume Generation Engine v10.3")
    parser.add_argument('-j', '--job', required=True, help='Path to job_input.json')
    parser.add_argument('-m', '--master', required=True, help='Path to master_resume.json')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-hil', action='store_true', help='Disable Human-in-the-Loop')
    
    args = parser.parse_args()
    
    # v10.3: Instantiate ConfigV10_3 here, ONCE.
    try:
        config = ConfigV10_3("master_config_v10_3.json")
    except Exception as e:
        print(f"FATAL: Failed to load master_config_v10_3.json: {e}", file=sys.stderr)
        sys.exit(1)
    
    setup_logging(config, debug_mode=args.debug)
    
    result = asyncio.run(run_workflow_async(
        config=config, # v10.3: Inject the config object
        job_input_path=args.job,
        master_resume_path=args.master,
        debug_mode=args.debug,
        enable_hil=not args.no_hil
    ))
    
    print("\n" + "="*80)
    print(f"WORKFLOW RESULT: {result['status']}")
    print(f"Workflow ID: {result.get('workflow_id')}")
    # ... (Rest of the print statements) ...
    print("="*80)
    
    if result['status'] == 'SUCCESS':
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

# ============================================================================
# END OF main_v10_3.py
# ============================================================================