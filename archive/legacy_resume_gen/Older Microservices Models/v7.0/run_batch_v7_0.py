# File: run_batch_v7_0.py
# Overwrites: run_batch_v6_5.py
# Version: 7.0 (LangGraph + Redis)
#
# v7.0 (Phase 1) CHANGES:
# - Imports from v7_0.
# - DELETED 'WorkflowV65' import, as it no longer exists.
# - Replaced 'process_single_job' logic to invoke the LangGraph app,
#   mimicking main_v7_0.py's setup for each parallel process.

import os
import csv
import json
import logging
import shutil
import concurrent.futures
import uuid
from datetime import datetime
from typing import Dict, Any

# Imports from its *own* versioned files (v7.0)
from main_v7_0 import setup_logging, load_job_input # Import helpers from main
from core_v7_0 import CONFIG, CircuitBreakerOpenError

# v7.0: Import the graph builder and checkpointer
from agent_swarm_v7_0 import get_graph_app
from langgraph.checkpoint.redis import RedisSaver

# v7.0: Import the meta-learner
try:
    from run_learning_v7_0 import run_meta_learning
    META_LEARNER_AVAILABLE = True
except ImportError:
    META_LEARNER_AVAILABLE = False


logger = logging.getLogger("batch_runner_v7_0")
try:
    setup_logging(debug_mode=False)
except Exception as e:
    print(f"Warning: setup_logging failed: {e}")
    logging.basicConfig(level=logging.INFO)


BATCH_QUEUE_DIR = "batch_queue"
BATCH_COMPLETE_DIR = "batch_complete"
SUMMARY_FILE = "batch_summary_v7_0.csv"

# --- v7.0: Graph Setup (will be re-initialized in each process) ---
# We define them here to show intent; they must be created
# inside the 'process_single_job' function to be process-safe.
checkpointer = None
app = None

def get_compiled_graph():
    """
    Initializes the graph and checkpointer *within* a new process.
    This is critical for ProcessPoolExecutor.
    """
    global checkpointer, app
    if checkpointer is None:
        redis_config = CONFIG.redis_config
        checkpointer = RedisSaver(
            host=redis_config.host,
            port=redis_config.port,
            db=redis_config.db
        )
    if app is None:
        app = get_graph_app(checkpointer)
    return app, checkpointer

def process_single_job(job_path: str) -> Dict[str, Any]:
    """
    Wraps the execution of a single job for the parallel executor.
    Returns a dictionary for the summary CSV.
    """
    company, title, status, workflow_id, error_msg = "N/A", "N/A", "FATAL", "N/A", ""
    logger.info(f"--- Starting v7.0 job: {os.path.basename(job_path)} ---")

    try:
        # Load job input
        job_input_data = load_job_input(job_path)
        company = job_input_data.get('company_name', 'N/A')
        title = job_input_data.get('job_title', 'N/A')

        # --- v7.0: Cost Ceiling Check (Unchanged) ---
        jd_length = len(job_input_data.get('job_description', ''))
        estimated_tokens = (jd_length * 0.75) + 30000 # 30k token assumption
        estimated_cost = (estimated_tokens / 1000) * 0.005 # $0.005 avg cost
        
        cost_ceiling = CONFIG.cost_config.cost_ceiling_per_workflow
        if estimated_cost > cost_ceiling:
            raise Exception(f"Cost ceiling exceeded (Est: ${estimated_cost:.2f})")

        # --- v7.0: Run the Graph ---
        # Get the process-local instance of the graph
        app, _ = get_compiled_graph()
        
        # Load master resume (path from config)
        master_resume = load_job_input(CONFIG.file_paths.default_master_resume)

        workflow_id = str(uuid.uuid4())
        
        # This config maps the run to a specific "thread_id" in Redis.
        run_config = {"configurable": {"thread_id": workflow_id}}
        
        # Define the initial state for the graph
        inputs = {
            "master_resume": master_resume,
            "job_input": {
                "raw_jd": job_input_data['job_description'],
                "company": job_input_data['company_name'],
                "job_title": job_input_data['job_title']
            },
            "artifacts": {},
            "replan_count": 0,
            "workflow_id": workflow_id
        }
        
        # --- v7.0: Invoke the Graph ---
        final_state = app.invoke(inputs, config=run_config)
        
        # Extract results
        validation = final_state.get('artifacts', {}).get('validation_results', {})
        if validation.get('overall_passed', False):
            status = "SUCCESS"
            error_msg = ""
        else:
            status = "FAILED_QA"
            failed_count = validation.get('failed_checks_count', 0)
            error_msg = f"{failed_count} QA check(s) failed."

    except CircuitBreakerOpenError as e:
        logger.error(f"Job {os.path.basename(job_path)} skipped. Circuit breaker is OPEN: {e}")
        status, error_msg = "SKIPPED", f"CircuitBreakerOpen: {e}"

    except Exception as e:
        logger.critical(f"FATAL error running job {os.path.basename(job_path)}: {e}", exc_info=True)
        status, error_msg = "FAILED_FATAL", str(e)
        
    finally:
        # Move file to complete
        try:
            shutil.move(job_path, os.path.join(BATCH_COMPLETE_DIR, os.path.basename(job_path)))
        except Exception as e:
            logger.error(f"Failed to move file {os.path.basename(job_path)}: {e}")
        
        logger.info(f"--- Finished v7.0 job: {company} - {title} ---")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "company": company,
            "title": title,
            "status": status,
            "workflow_id": workflow_id,
            "error": error_msg,
            "job_file": job_path
        }


def run_batch():
    """
    Main batch processing loop.
    Processes all .json files in batch_queue/ directory in parallel.
    """
    # (Setup logic... NO CHANGES from v6.5)
    os.makedirs(BATCH_QUEUE_DIR, exist_ok=True)
    os.makedirs(BATCH_COMPLETE_DIR, exist_ok=True)
    
    job_files = [os.path.join(BATCH_QUEUE_DIR, f) for f in os.listdir(BATCH_QUEUE_DIR) if f.endswith('.json')]
    if not job_files:
        logger.info("v7.0 Batch process starting. No jobs found in queue.")
        return

    logger.info(f"v7.0 Batch process starting. Found {len(job_files)} jobs.")
    
    max_workers = CONFIG.batch_config.max_parallel_workers
    logger.info(f"Running batch with up to {max_workers} parallel workers.")

    if not os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "company_name", "job_title", "overall_status", "workflow_id", "error_message"])

    # v7.0: Use ProcessPoolExecutor to run jobs in parallel
    all_results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        try:
            results_iterable = executor.map(process_single_job, job_files)
            all_results = list(results_iterable) # Collect all results
        except Exception as e:
            logger.critical(f"A critical error occurred during parallel execution: {e}")
            
    # (Write results to CSV... NO CHANGES from v6.5)
    try:
        with open(SUMMARY_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            for summary in all_results:
                writer.writerow([
                    summary["timestamp"], summary["company"], summary["title"],
                    summary["status"], summary["workflow_id"], summary["error"]
                ])
        logger.info(f"Batch summary CSV updated with {len(all_results)} results.")
    except Exception as e:
        logger.error(f"Failed to write batch summary to CSV: {e}")
        
    logger.info(f"v7.0 Batch process complete.")
    
    # (Meta-Learning trigger... NO CHANGES from v6.5)
    if CONFIG.meta_loop_config.enable_meta_learning:
        logger.info("Post-batch meta-learning enabled. Triggering learning loop...")
        if META_LEARNER_AVAILABLE:
            try:
                run_meta_learning() # v7.0 update
                logger.info("Meta-learning loop completed successfully.")
            except Exception as e:
                logger.error(f"Meta-learning loop failed: {e}")
        else:
            logger.warning("Meta-learning is enabled, but 'run_learning_v7_0' could not be imported.")
    else:
        logger.info("Post-batch meta-learning is disabled in config. Skipping.")


if __name__ == "__main__":
    run_batch()