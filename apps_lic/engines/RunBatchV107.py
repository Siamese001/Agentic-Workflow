# File: run_batch_v10_7.py
# Version: 10.7 (Refactored)
#
# v10.7 REFACTOR CHANGES:
# - UPDATED: All versioning to v10_7 (e.g., core_v10_7, ConfigV10_7).
# - UPDATED: create_workflow_context call updated to v10_7.
#
# v10.7 MAJOR CHANGES:
# - IMPLEMENTED (Fix #25): Added backpressure check. The batch
#   will not run if the number of files in BATCH_QUEUE_DIR
#   exceeds config.batch_config.max_batch_queue_size.
# - FIXED: All v10_5 imports and class names updated to v10_7.

import asyncio
import csv
import logging
import os
import shutil
import sys
import uuid
from datetime import datetime
from typing import Any

# v10.7: Import from new orchestration/stacks
from agent_orchestration_v10_7 import get_graph_app
from core_v10_7 import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    ConfigV10_7,
    MainGraphState,
    WorkflowContext,
    WorkflowError,
    cleanup_workflow_chroma_collection,
    # v10.7: Import new helper functions
    create_workflow_context,
    get_checkpointer,
)

# v10.7: Import from new main/core
from main_v10_7 import load_job_input, setup_logging

try:
    # v10.7: Import new meta-learner
    from run_learning_v10_7 import run_meta_learning
    META_LEARNER_AVAILABLE = True
except ImportError:
    META_LEARNER_AVAILABLE = False
    logging.getLogger("batch_runner_v10_7").warning("Meta-learning module (run_learning_v10_7.py) not found.")

logger = logging.getLogger("batch_runner_v10_7")

BATCH_QUEUE_DIR = "batch_queue"
BATCH_COMPLETE_DIR = "batch_complete"
SUMMARY_FILE = "batch_summary_v10_7.csv"

# ============================================================================
# ROW 7: BATCH FEEDBACK AGGREGATOR (Preserved)
# ============================================================================

class BatchFeedbackAggregator:
    """ROW 7: Aggregates feedback across batch jobs"""
    def __init__(self):
        self.job_results: list[dict[str, Any]] = []

    def add_job_result(self, result: dict[str, Any]):
        self.job_results.append(result)

    def get_batch_summary(self) -> dict[str, Any]:
        if not self.job_results: return {}
        total_jobs = len(self.job_results)
        successful = sum(1 for r in self.job_results if r['status'] == 'SUCCESS')
        total_cost = sum(r.get('cost', 0.0) for r in self.job_results)
        avg_cost = total_cost / total_jobs if total_jobs > 0 else 0.0

        return {
            "timestamp": datetime.now().isoformat(), "total_jobs": total_jobs,
            "successful": successful, "success_rate": successful / total_jobs if total_jobs > 0 else 0.0,
            "total_cost": total_cost, "avg_cost_per_job": avg_cost,
            "batch_health_score": (successful / total_jobs * 100) if total_jobs > 0 else 0.0
        }

# ============================================================================
# ROW 6: ASYNC BATCH PROCESSING ENGINE (v10.7)
# ============================================================================

async def process_single_job_async(
    job_file: str,
    master_resume_path: str,
    context: WorkflowContext, # v10.7: This is the JOB-SPECIFIC context
    app, # The compiled graph app
    circuit_breaker: CircuitBreaker,
    batch_aggregator: BatchFeedbackAggregator
) -> dict[str, Any]:
    """Process a single job asynchronously"""

    job_name = os.path.basename(job_file)
    logger.info(f"Processing job: {job_name}")

    job_input_data = {}
    workflow_id = str(uuid.uuid4())
    context.workflow_id = workflow_id # Set on job-specific context

    try:
        circuit_breaker.check()

        job_input_data = load_job_input(job_file)
        master_resume = load_job_input(master_resume_path)

        company = job_input_data.get('company_name', 'N/A')
        title = job_input_data.get('job_title', 'N/A')

        run_config = {"configurable": {"thread_id": workflow_id}}

        initial_state = MainGraphState()
        initial_state.resume.master_resume = master_resume
        initial_state.job.raw_jd = job_input_data['job_description']
        initial_state.job.company = job_input_data['company_name']
        initial_state.job.job_title = job_input_data['job_title']
        initial_state.metadata.workflow_id = workflow_id
        initial_state.metadata.complexity = "unknown" # Set by graph

        state_dict = initial_state.to_dict()

        final_state_dict = None
        async for s in app.astream(state_dict, run_config):
            final_state_dict = s[list(s.keys())[0]]

        if final_state_dict is None:
            raise WorkflowError("Workflow returned no final state.")

        if "REJECT_JOB" in final_state_dict:
             logger.error(f"Workflow {workflow_id} REJECTED.")
             raise WorkflowError("Workflow rejected, likely due to prompt injection or constitutional failure.")

        final_state = MainGraphState.from_dict(final_state_dict)
        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        total_cost = cost_summary['total_workflow_cost']

        complete_path = os.path.join(BATCH_COMPLETE_DIR, job_name)
        shutil.move(job_file, complete_path)

        # v10.7 REFACTOR: Call centralized cleanup helper
        cleanup_workflow_chroma_collection(context)

        result = {
            "job_file": job_name, "company_name": company, "job_title": title,
            "status": "SUCCESS", "workflow_id": workflow_id, "cost": total_cost, "error": None
        }

        circuit_breaker.record_success()
        batch_aggregator.add_job_result(result)
        logger.info(f"✓ Completed: {company} - {title} (${total_cost:.4f})")
        return result

    except (CircuitBreakerOpenError, Exception) as e:
        if not isinstance(e, CircuitBreakerOpenError):
            logger.error(f"✗ Failed job {job_name}: {e}", exc_info=True)
            circuit_breaker.record_failure()

        result = {
            "job_file": job_name, "company_name": job_input_data.get('company_name', 'N/A'),
            "job_title": job_input_data.get('job_title', 'N/A'),
            "status": "FAILED_CIRCUIT_BREAKER" if isinstance(e, CircuitBreakerOpenError) else "FAILED_FATAL",
            "workflow_id": workflow_id, "cost": 0.0, "error": str(e)
        }
        batch_aggregator.add_job_result(result)
        return result

async def run_batch_async(config: ConfigV10_7): # v10.7
    """Main async batch processing with semaphore concurrency control"""

    os.makedirs(BATCH_QUEUE_DIR, exist_ok=True)
    os.makedirs(BATCH_COMPLETE_DIR, exist_ok=True)

    job_files = [
        os.path.join(BATCH_QUEUE_DIR, f)
        for f in os.listdir(BATCH_QUEUE_DIR)
        if f.endswith('.json')
    ]

    if not job_files:
        logger.info("v10.7 Batch process starting. No jobs found.")
        return

    logger.info("===== v10.7 Async Batch Process Starting =====")

    # v10.7 (Fix #25): Backpressure Check
    max_queue_size = config.batch_config.max_batch_queue_size
    if len(job_files) > max_queue_size:
        logger.error(f"BACKPRESSURE: Batch queue size ({len(job_files)}) exceeds limit ({max_queue_size}).")
        logger.error("Batch run aborted. Clear queue before retrying.")
        return

    logger.info(f"Found {len(job_files)} jobs in queue (limit: {max_queue_size})")

    # --- v10.7: REFACTOR: COMPOSITION ROOT ---
    # Create a single, shared context to hold all instantiated services
    shared_context = create_workflow_context(config, db=config.redis_config.db)

    # Unpack shared services to be injected into job-specific contexts
    redis_client = shared_context.redis_client
    chromadb_client = shared_context.chromadb_client
    cache_manager = shared_context.cache_manager
    cost_tracker = shared_context.cost_tracker
    feedback_reader = shared_context.feedback_reader
    rules_loader = shared_context.rules_loader
    prompt_manager = shared_context.prompt_manager
    response_validator = shared_context.response_validator
    context_budget_manager = shared_context.context_budget_manager
    metrics_collector = shared_context.metrics_collector
    semantic_validator = shared_context.semantic_validator

    checkpointer = get_checkpointer(config)
    # --- v10.7: REFACTOR END ---

    batch_aggregator = BatchFeedbackAggregator()
    circuit_breaker = CircuitBreaker(
        failure_threshold=config.batch_config.circuit_breaker_failure_threshold
    )

    max_workers = config.batch_config.max_parallel_workers
    semaphore = asyncio.Semaphore(max_workers)
    master_resume_path = config.file_paths.default_master_resume

    async def process_with_semaphore(job_file):
        """Process job with semaphore"""
        async with semaphore:
            # v10.7: Create a job-specific context by injecting
            # all the SHARED services created above.
            job_context = WorkflowContext(
                config=config,
                redis_client=redis_client,
                chromadb_client=chromadb_client,
                cache_manager=cache_manager,
                cost_tracker=cost_tracker,
                feedback_reader=feedback_reader,
                rules_loader=rules_loader,
                prompt_manager=prompt_manager,
                response_validator=response_validator,
                context_budget_manager=context_budget_manager,
                metrics_collector=metrics_collector,
                semantic_validator=semantic_validator,
                embedding_function=shared_context.embedding_function
            )
            # v10.7: Manually inject the circular dependency
            job_context.context_budget_manager = ContextBudgetManager(
                config=config,
                model_client_getter=job_context.get_model_client
            )

            job_app = get_graph_app(
                checkpointer,
                job_context,
                enable_hil=False,
                enable_mcp=job_context.wrap_mcp_nodes,
            )

            return await process_single_job_async(
                job_file,
                master_resume_path,
                job_context, # Pass job-specific context
                job_app,     # Pass job-specific app
                circuit_breaker,
                batch_aggregator
            )

    logger.info(f"Starting parallel processing ({max_workers} workers)...")
    start_time = datetime.now()

    results = await asyncio.gather(*[
        process_with_semaphore(job_file)
        for job_file in job_files
    ], return_exceptions=True)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # v10.7: Write CSV summary
    batch_summary = batch_aggregator.get_batch_summary()
    if batch_summary:
        summary_path = os.path.join(BATCH_COMPLETE_DIR, SUMMARY_FILE)
        file_exists = os.path.isfile(summary_path)
        try:
            with open(summary_path, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=batch_summary.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(batch_summary)
            logger.info(f"Wrote batch summary to {summary_path}")
        except OSError as e:
            logger.error(f"Failed to write batch summary: {e}")

    logger.info("BATCH PROCESSING COMPLETE (v10.7)")
    logger.info(f"  Total Jobs: {batch_summary.get('total_jobs', 0)}")
    logger.info(f"  Success Rate: {batch_summary.get('success_rate', 0.0):.1%}")
    logger.info(f"  Total Cost: ${batch_summary.get('total_cost', 0.0):.4f}")

    # v10.7: Log metrics summary for the *entire* batch
    logger.info("--- Batch Metrics Summary (v10.7) ---")
    for metric in metrics_collector.get_summary():
         logger.info(f"  - {metric['agent_name']}::{metric['task_name']} | {metric['duration_ms']:.2f}ms | Success: {metric['success']}")

    # Optionally trigger meta-learning
    if META_LEARNER_AVAILABLE and config.meta_loop_config.enable_meta_learning:
        logger.info("Triggering meta-learning loop (v10.7)...")
        try:
            # v10.7: Pass the config object to the meta-learner
            await run_meta_learning(config)
        except Exception as e:
            logger.error(f"Meta-learning failed: {e}")

    logger.info("v10.7 Batch process complete.")

def run_batch():
    """Synchronous wrapper for async batch processing"""
    # v10.7: Instantiate ConfigV10_7 here, ONCE.
    try:
        config = ConfigV10_7("master_config_v10_7.json")
    except Exception as e:
        print(f"FATAL: Failed to load master_config_v10_7.json: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        setup_logging(config, debug_mode=False)
    except Exception as e:
        print(f"Warning: setup_logging failed: {e}")
        logging.basicConfig(level=logging.INFO)

    # v10.7: Inject the config object
    asyncio.run(run_batch_async(config))

if __name__ == "__main__":
    run_batch()

# ============================================================================
# END OF run_batch_v10_7.py
# ============================================================================
