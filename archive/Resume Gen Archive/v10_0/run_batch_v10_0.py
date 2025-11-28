# File: run_batch_v10_0.py
# Version: 10.0 (Modularity, Caching, Async Performance)
#
# v10.0 MAJOR CHANGES:
# ROW 4: Uses WorkflowContext for dependency injection
# ROW 5: Shared cache across batch jobs
# ROW 6: Async batch processing with better concurrency

import os
import csv
import json
import logging
import shutil
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List
import redis

from main_v10_0 import setup_logging, load_job_input
from core_v10_0 import (
    CONFIG, WorkflowContext, MainGraphState,
    CircuitBreakerOpenError, CostCeilingExceededError,
    FileIOError
)
from agent_swarm_v10_0 import get_graph_app, PIISanitizerAgent
from langgraph.checkpoint.redis import RedisSaver

# Meta-learner import
try:
    from run_learning_v10_0 import run_meta_learning
    META_LEARNER_AVAILABLE = True
except ImportError:
    META_LEARNER_AVAILABLE = False

logger = logging.getLogger("batch_runner_v10_0")

try:
    setup_logging(debug_mode=False)
except Exception as e:
    print(f"Warning: setup_logging failed: {e}")
    logging.basicConfig(level=logging.INFO)

BATCH_QUEUE_DIR = "batch_queue"
BATCH_COMPLETE_DIR = "batch_complete"
SUMMARY_FILE = "batch_summary_v10_0.csv"

# ============================================================================
# ROW 6: ASYNC BATCH PROCESSING
# ============================================================================

async def process_single_job_async(
    job_path: str,
    context: WorkflowContext,
    checkpointer: RedisSaver,
    app
) -> Dict[str, Any]:
    """Process single job asynchronously"""
    company, title, status, workflow_id, error_msg = "N/A", "N/A", "FATAL", "N/A", ""
    cost = 0.0
    
    logger.info(f"--- Starting v10.0 async job: {os.path.basename(job_path)} ---")
    
    try:
        job_input_data = load_job_input(job_path)
        company = job_input_data.get('company_name', 'N/A')
        title = job_input_data.get('job_title', 'N/A')
        
        # Cost estimation
        jd_length = len(job_input_data.get('job_description', ''))
        estimated_tokens = (jd_length * 0.75) + 30000
        estimated_cost = (estimated_tokens / 1000) * 0.005
        
        cost_ceiling = CONFIG.cost_config.cost_ceiling_per_workflow
        if estimated_cost > cost_ceiling:
            raise CostCeilingExceededError(
                f"Estimated cost ${estimated_cost:.2f} exceeds ceiling ${cost_ceiling:.2f}"
            )
        
        # Load master resume
        master_resume = load_job_input(CONFIG.file_paths.default_master_resume)
        
        # Sanitize PII locally
        sanitizer = PIISanitizerAgent()
        sanitized_resume = sanitizer.run(master_resume)
        
        # Build initial state
        workflow_id = str(uuid.uuid4())
        run_config = {"configurable": {"thread_id": workflow_id}}
        
        initial_state = MainGraphState()
        initial_state.resume.master_resume = master_resume
        initial_state.resume.sanitized_resume = sanitized_resume
        initial_state.job.raw_jd = job_input_data['job_description']
        initial_state.job.company = job_input_data['company_name']
        initial_state.job.job_title = job_input_data['job_title']
        initial_state.metadata.workflow_id = workflow_id
        
        state_dict = initial_state.to_dict()
        
        # Execute workflow (async via thread pool)
        final_state_dict = await asyncio.to_thread(
            app.invoke,
            state_dict,
            run_config
        )
        
        final_state = MainGraphState.from_dict(final_state_dict)
        
        # Get actual cost
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        cost = cost_summary.get('total_workflow_cost', 0.0)
        
        # Check validation
        validation = final_state.artifacts.artifacts.get('validation_results', {})
        if validation.get('overall_passed', False):
            status = "SUCCESS"
            error_msg = ""
        else:
            status = "FAILED_QA"
            failed_checks = validation.get('checks', [])
            failed_count = sum(1 for c in failed_checks if not c.get('passed', True))
            error_msg = f"{failed_count} QA check(s) failed."
    
    except CircuitBreakerOpenError as e:
        logger.error(f"Job {os.path.basename(job_path)} skipped. Circuit breaker OPEN: {e}")
        status, error_msg = "SKIPPED", f"CircuitBreakerOpen: {e}"
    
    except CostCeilingExceededError as e:
        logger.error(f"Job {os.path.basename(job_path)} cost ceiling exceeded: {e}")
        status, error_msg = "FAILED_COST", str(e)
    
    except Exception as e:
        logger.critical(f"FATAL error in {os.path.basename(job_path)}: {e}", exc_info=True)
        status, error_msg = "FAILED_FATAL", str(e)
    
    finally:
        try:
            shutil.move(job_path, os.path.join(BATCH_COMPLETE_DIR, os.path.basename(job_path)))
        except Exception as e:
            logger.error(f"Failed to move file: {e}")
        
        logger.info(f"--- Finished v10.0 job: {company} - {title} (${cost:.4f}) ---")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "company": company,
            "title": title,
            "status": status,
            "workflow_id": workflow_id,
            "error": error_msg,
            "cost": cost,
            "job_file": os.path.basename(job_path)
        }

async def run_batch_async():
    """Main async batch processing with shared context and caching"""
    os.makedirs(BATCH_QUEUE_DIR, exist_ok=True)
    os.makedirs(BATCH_COMPLETE_DIR, exist_ok=True)
    
    job_files = [
        os.path.join(BATCH_QUEUE_DIR, f) 
        for f in os.listdir(BATCH_QUEUE_DIR) 
        if f.endswith('.json')
    ]
    
    if not job_files:
        logger.info("v10.0 Batch process starting. No jobs found.")
        return
    
    logger.info(f"v10.0 Batch process starting. Found {len(job_files)} jobs.")
    
    # Row 4: Initialize shared context for all jobs
    redis_client = redis.Redis(
        host=CONFIG.redis_config.host,
        port=CONFIG.redis_config.port,
        db=CONFIG.redis_config.db
    )
    
    context = WorkflowContext(CONFIG, redis_client)
    logger.info("Initialized shared WorkflowContext for batch")
    
    # Initialize checkpointer
    checkpointer = RedisSaver(
        host=CONFIG.redis_config.host,
        port=CONFIG.redis_config.port,
        db=CONFIG.redis_config.db
    )
    
    # Build graph once (shared across jobs)
    app = get_graph_app(checkpointer, context, enable_hil=False)
    logger.info("Compiled shared LangGraph workflow")
    
    # Initialize CSV
    if not os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "company_name", "job_title", 
                "overall_status", "workflow_id", "cost_usd", "error_message"
            ])
    
    # Row 6: Process jobs with controlled concurrency
    max_concurrent = CONFIG.performance_config.max_concurrent_llm_calls
    logger.info(f"Processing with max concurrency: {max_concurrent}")
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_semaphore(job_path):
        async with semaphore:
            return await process_single_job_async(job_path, context, checkpointer, app)
    
    # Execute all jobs with concurrency control
    tasks = [process_with_semaphore(job_path) for job_path in job_files]
    all_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle exceptions and write results
    processed_results = []
    for i, result in enumerate(all_results):
        if isinstance(result, Exception):
            logger.error(f"Job {job_files[i]} failed with exception: {result}")
            processed_results.append({
                "timestamp": datetime.now().isoformat(),
                "company": "ERROR",
                "title": "ERROR",
                "status": "FAILED_FATAL",
                "workflow_id": "N/A",
                "error": str(result),
                "cost": 0.0,
                "job_file": os.path.basename(job_files[i])
            })
        else:
            processed_results.append(result)
    
    # Write to CSV
    try:
        with open(SUMMARY_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            for summary in processed_results:
                writer.writerow([
                    summary["timestamp"], summary["company"], summary["title"],
                    summary["status"], summary["workflow_id"], 
                    summary.get("cost", 0.0), summary["error"]
                ])
        logger.info(f"Batch summary updated with {len(processed_results)} results.")
    except Exception as e:
        logger.error(f"Failed to write batch summary: {e}")
    
    # Row 5: Cache performance stats
    cache_stats = context.cache_manager.get_stats()
    logger.info(f"Batch cache performance: {cache_stats}")
    
    # Cost summary
    total_cost = sum(r.get("cost", 0.0) for r in processed_results)
    logger.info(f"Total batch cost: ${total_cost:.4f}")
    
    # Status breakdown
    status_counts = {}
    for r in processed_results:
        status = r.get("status", "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    logger.info(f"Status breakdown: {status_counts}")
    logger.info(f"v10.0 Batch process complete.")
    
    # Meta-learning
    if CONFIG.meta_loop_config.enable_meta_learning:
        logger.info("Post-batch meta-learning enabled...")
        if META_LEARNER_AVAILABLE:
            try:
                await run_meta_learning()
                logger.info("Meta-learning loop completed.")
            except Exception as e:
                logger.error(f"Meta-learning failed: {e}")
        else:
            logger.warning("Meta-learning enabled but 'run_learning_v10_0' not found.")
    else:
        logger.info("Post-batch meta-learning disabled.")

def run_batch():
    """Synchronous wrapper for async batch processing"""
    asyncio.run(run_batch_async())

if __name__ == "__main__":
    run_batch()

# ============================================================================
# END OF run_batch_v10_0.py
# ============================================================================