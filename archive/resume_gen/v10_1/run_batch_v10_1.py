# File: run_batch_v10_1.py
# Version: 10.1 (Aspirational Design Implementation)
#
# v10.1 MAJOR CHANGES:
# - Explicitly DISABLED HIL for batch runs (enable_hil=False)
# - Preserved async batch processing with semaphore
# - Preserved meta-learning trigger for closed-loop feedback
# - MODULARITY OVERWRITE: Imports now point to agent_orchestration_v10_1 and agent_stacks_v10_1

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

from main_v10_1 import setup_logging, load_job_input
from core_v10_1 import (
    CONFIG, WorkflowContext, MainGraphState,
    CircuitBreakerOpenError, CostCeilingExceededError,
    FileIOError
)
# MODULARITY OVERWRITE: Import from new locations
from agent_orchestration_v10_1 import get_graph_app
from agent_stacks_v10_1 import PIISanitizerAgent
from langgraph.checkpoint.redis import RedisSaver

try:
    from run_learning_v10_1 import run_meta_learning
    META_LEARNER_AVAILABLE = True
    logging.getLogger("batch_runner_v10_1").info("Meta-learning module loaded successfully.")
except ImportError:
    META_LEARNER_AVAILABLE = False
    logging.getLogger("batch_runner_v10_1").warning("Meta-learning module (run_learning_v10_1.py) not found. Batch will run without meta-learning trigger.")

logger = logging.getLogger("batch_runner_v10_1")

try:
    setup_logging(debug_mode=False)
except Exception as e:
    print(f"Warning: setup_logging failed: {e}")
    logging.basicConfig(level=logging.INFO)

BATCH_QUEUE_DIR = "batch_queue"
BATCH_COMPLETE_DIR = "batch_complete"
SUMMARY_FILE = "batch_summary_v10_1.csv"

# ============================================================================
# ROW 7: BATCH FEEDBACK AGGREGATOR
# ============================================================================

class BatchFeedbackAggregator:
    """ROW 7: Aggregates feedback across batch jobs"""
    
    def __init__(self):
        self.job_results: List[Dict[str, Any]] = []
    
    def add_job_result(self, result: Dict[str, Any]):
        """Add a completed job result"""
        self.job_results.append(result)
    
    def get_batch_summary(self) -> Dict[str, Any]:
        """Generate batch-level feedback summary"""
        if not self.job_results:
            return {}
        
        total_jobs = len(self.job_results)
        successful = sum(1 for r in self.job_results if r['status'] == 'SUCCESS')
        
        total_cost = sum(r.get('cost', 0.0) for r in self.job_results)
        avg_cost = total_cost / total_jobs if total_jobs > 0 else 0.0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_jobs": total_jobs,
            "successful": successful,
            "success_rate": successful / total_jobs if total_jobs > 0 else 0.0,
            "total_cost": total_cost,
            "avg_cost_per_job": avg_cost,
            "batch_health_score": (successful / total_jobs * 100) if total_jobs > 0 else 0.0
        }

# ============================================================================
# ROW 6: ASYNC BATCH PROCESSING ENGINE
# ============================================================================

class CircuitBreaker:
    """Circuit breaker for batch processing"""
    
    def __init__(self, failure_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.is_open = False
        self.logger = logging.getLogger(f"{__name__}.CircuitBreaker")
    
    def record_success(self):
        """Record successful job"""
        self.failure_count = 0
        self.is_open = False
    
    def record_failure(self):
        """Record failed job"""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            self.logger.error(f"Circuit breaker OPEN after {self.failure_count} failures")
    
    def check(self):
        """Check if circuit breaker is open"""
        if self.is_open:
            raise CircuitBreakerOpenError(f"Circuit breaker open after {self.failure_count} failures")

async def process_single_job_async(
    job_file: str,
    master_resume_path: str,
    context: WorkflowContext,
    app, # The compiled graph app
    circuit_breaker: CircuitBreaker,
    batch_aggregator: BatchFeedbackAggregator
) -> Dict[str, Any]:
    """Process a single job asynchronously"""
    
    job_name = os.path.basename(job_file)
    logger.info(f"Processing job: {job_name}")
    
    job_input_data = {}
    workflow_id = str(uuid.uuid4()) # Generate ID even if setup fails
    context.workflow_id = workflow_id # Set on context for this job's agents
    
    try:
        # Check circuit breaker
        circuit_breaker.check()
        
        # Load job input
        job_input_data = load_job_input(job_file)
        master_resume = load_job_input(master_resume_path)
        
        company = job_input_data.get('company_name', 'N/A')
        title = job_input_data.get('job_title', 'N/A')
        
        # Sanitize PII
        sanitizer = PIISanitizerAgent(context)
        sanitized_resume = sanitizer.run(master_resume)
        
        # Generate workflow ID
        run_config = {"configurable": {"thread_id": workflow_id}}
        
        context.redis_client.set("current_workflow_id", workflow_id, ex=3600)
        
        # Initialize state
        initial_state = MainGraphState()
        initial_state.resume.master_resume = master_resume
        initial_state.resume.sanitized_resume = sanitized_resume
        initial_state.job.raw_jd = job_input_data['job_description']
        initial_state.job.company = job_input_data['company_name']
        initial_state.job.job_title = job_input_data['job_title']
        initial_state.metadata.workflow_id = workflow_id
        
        state_dict = initial_state.to_dict()
        
        # Run workflow (non-streaming, as it's a batch)
        final_state_dict = None
        async for s in app.astream(state_dict, run_config):
            # We don't need to log every step in batch, just get the final state
            final_state_dict = s[list(s.keys())[0]]

        if final_state_dict is None:
            raise WorkflowError("Workflow returned no final state.")

        final_state = MainGraphState.from_dict(final_state_dict)
        
        # Get cost
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        total_cost = cost_summary['total_workflow_cost']
        
        # Move job to complete
        complete_path = os.path.join(BATCH_COMPLETE_DIR, job_name)
        shutil.move(job_file, complete_path)
        
        result = {
            "job_file": job_name,
            "company_name": company,
            "job_title": title,
            "status": "SUCCESS",
            "workflow_id": workflow_id,
            "cost": total_cost,
            "error": None
        }
        
        circuit_breaker.record_success()
        batch_aggregator.add_job_result(result)
        
        logger.info(f"✓ Completed: {company} - {title} (${total_cost:.4f})")
        
        return result
        
    except CircuitBreakerOpenError as e:
        logger.error(f"✗ Circuit breaker open for {job_name}: {e}")
        result = {
            "job_file": job_name,
            "company_name": job_input_data.get('company_name', 'N/A'),
            "job_title": job_input_data.get('job_title', 'N/A'),
            "status": "FAILED_CIRCUIT_BREAKER",
            "workflow_id": workflow_id,
            "cost": 0.0,
            "error": str(e)
        }
        batch_aggregator.add_job_result(result)
        return result
        
    except Exception as e:
        logger.error(f"✗ Failed job {job_name}: {e}", exc_info=True)
        circuit_breaker.record_failure()
        
        result = {
            "job_file": job_name,
            "company_name": job_input_data.get('company_name', 'N/A'),
            "job_title": job_input_data.get('job_title', 'N/A'),
            "status": "FAILED_FATAL",
            "workflow_id": workflow_id,
            "cost": 0.0,
            "error": str(e)
        }
        batch_aggregator.add_job_result(result)
        return result

async def run_batch_async():
    """Main async batch processing with semaphore concurrency control"""
    
    os.makedirs(BATCH_QUEUE_DIR, exist_ok=True)
    os.makedirs(BATCH_COMPLETE_DIR, exist_ok=True)
    
    job_files = [
        os.path.join(BATCH_QUEUE_DIR, f) 
        for f in os.listdir(BATCH_QUEUE_DIR) 
        if f.endswith('.json')
    ]
    
    if not job_files:
        logger.info("v10.1 Batch process starting. No jobs found.")
        return
    
    logger.info(f"===== v10.1 Async Batch Process Starting =====")
    logger.info(f"Found {len(job_files)} jobs in queue")
    
    # Initialize shared resources
    redis_client = redis.Redis(
        host=CONFIG.redis_config.host,
        port=CONFIG.redis_config.port,
        db=CONFIG.redis_config.db
    )
    
    context = WorkflowContext(CONFIG, redis_client)
    logger.info("Initialized shared WorkflowContext")
    
    batch_aggregator = BatchFeedbackAggregator()
    circuit_breaker = CircuitBreaker(
        failure_threshold=CONFIG.batch_config.circuit_breaker_failure_threshold
    )
    
    checkpointer = RedisSaver(
        host=CONFIG.redis_config.host,
        port=CONFIG.redis_config.port,
        db=CONFIG.redis_config.db
    )
    
    # CRITICAL: Disable HIL for batch processing
    app = get_graph_app(checkpointer, context, enable_hil=False)
    logger.info("Compiled shared LangGraph workflow (HIL DISABLED)")
    
    # Initialize CSV summary
    if not os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "company_name", "job_title", 
                "overall_status", "workflow_id", "cost_usd", "error_message"
            ])
    
    # Semaphore for concurrency control
    max_workers = CONFIG.batch_config.max_parallel_workers
    semaphore = asyncio.Semaphore(max_workers)
    logger.info(f"Using semaphore with {max_workers} concurrent workers")
    
    master_resume_path = CONFIG.file_paths.default_master_resume
    
    async def process_with_semaphore(job_file):
        """Process job with semaphore"""
        async with semaphore:
            # CRITICAL: Create a job-specific context to prevent race conditions
            # All jobs share Redis, but not the context object itself
            job_context = WorkflowContext(CONFIG, redis_client)
            
            # Re-compile the app with the job-specific context
            # This is lightweight as the graph structure is cached
            job_app = get_graph_app(checkpointer, job_context, enable_hil=False)
            
            return await process_single_job_async(
                job_file,
                master_resume_path,
                job_context, # Pass job-specific context
                job_app,     # Pass job-specific app
                circuit_breaker,
                batch_aggregator
            )
    
    # Process all jobs concurrently with semaphore control
    logger.info(f"Starting parallel processing ({max_workers} workers)...")
    start_time = datetime.now()
    
    results = await asyncio.gather(*[
        process_with_semaphore(job_file) 
        for job_file in job_files
    ], return_exceptions=True)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Write results to CSV
    with open(SUMMARY_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Job raised exception: {result}")
                continue
            
            writer.writerow([
                datetime.now().isoformat(),
                result['company_name'],
                result['job_title'],
                result['status'],
                result['workflow_id'],
                f"{result['cost']:.4f}",
                result['error'] or ""
            ])
    
    # Generate batch summary
    batch_summary = batch_aggregator.get_batch_summary()
    
    logger.info(f"\n{'='*80}")
    logger.info(f"BATCH PROCESSING COMPLETE")
    logger.info(f"  Total Jobs: {batch_summary.get('total_jobs', 0)}")
    logger.info(f"  Successful: {batch_summary.get('successful', 0)}")
    logger.info(f"  Success Rate: {batch_summary.get('success_rate', 0.0):.1%}")
    logger.info(f"  Total Cost: ${batch_summary.get('total_cost', 0.0):.4f}")
    logger.info(f"  Avg Cost/Job: ${batch_summary.get('avg_cost_per_job', 0.0):.4f}")
    logger.info(f"  Duration: {duration:.1f}s")
    logger.info(f"  Throughput: {len(job_files)/duration:.2f} jobs/sec")
    logger.info(f"  Batch Health Score: {batch_summary.get('batch_health_score', 0.0):.1f}%")
    logger.info(f"{'='*80}\n")
    
    # Cache stats (from the last job's context, as an approximation)
    cache_stats = context.cache_manager.get_stats()
    logger.info(f"Cache performance: Hit rate {cache_stats['hit_rate_pct']:.1f}%")
    
    # Optionally trigger meta-learning
    if META_LEARNER_AVAILABLE and CONFIG.meta_loop_config.enable_meta_learning:
        logger.info("Triggering meta-learning loop...")
        try:
            await run_meta_learning()
        except Exception as e:
            logger.error(f"Meta-learning failed: {e}")
    elif not META_LEARNER_AVAILABLE:
        logger.info("Meta-learning disabled (module not found).")
    else:
        logger.info("Meta-learning disabled (config).")
    
    logger.info("v10.1 Batch process complete.")

def run_batch():
    """Synchronous wrapper for async batch processing"""
    asyncio.run(run_batch_async())

if __name__ == "__main__":
    run_batch()

# ============================================================================
# END OF run_batch_v10_1.py
# ============================================================================