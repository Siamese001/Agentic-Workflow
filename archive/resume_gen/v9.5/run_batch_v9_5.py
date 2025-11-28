# File: run_batch_v9_5.py
# Overwrites: run_batch_v9_0.py
# Version: 9.5 (Privacy & Provenance)
#
# v9.5 (Privacy & Provenance) CHANGES:
# - Imports from v9_5 modules.

import os
import csv
import json
import logging
import shutil
import concurrent.futures
import uuid
from datetime import datetime
from typing import Dict, Any

# Imports from its *own* versioned files (v9.5)
from main_v9_5 import setup_logging, load_job_input
from core_v9_5 import CONFIG, CircuitBreakerOpenError

# v9.5: Import the graph builder and checkpointer
from agent_swarm_v9_5 import get_graph_app, PIISanitizerAgent
from langgraph.checkpoint.redis import RedisSaver

# v9.5: Import the meta-learner
try:
    from run_learning_v9_5 import run_meta_learning
    META_LEARNER_AVAILABLE = True
except ImportError:
    META_LEARNER_AVAILABLE = False


logger = logging.getLogger("batch_runner_v9_5")
try:
    setup_logging(debug_mode=False)
except Exception as e:
    print(f"Warning: setup_logging failed: {e}")
    logging.basicConfig(level=logging.INFO)


BATCH_QUEUE_DIR = "batch_queue"
BATCH_COMPLETE_DIR = "batch_complete"
SUMMARY_FILE = "batch_summary_v9_5.csv"

# --- v9.0: Graph Setup (will be re-initialized in each process) ---
checkpointer = None
app = None

def get_compiled_graph():
    """
    Initializes the graph and checkpointer *within* a new process.
    v9.0: Passes 'enable_hil=False' to the graph builder.
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
        app = get_graph_app(checkpointer, enable_hil=False)
    return app, checkpointer

def process_single_job(job_path: str) -> Dict[str, Any]:
    """
    Wraps the execution of a single job for the parallel executor.
    Returns a dictionary for the summary CSV.
    """
    company, title, status, workflow_id, error_msg = "N/A", "N/A", "FATAL", "N/A", ""
logger.info(f"--- Starting v9.5 job: {os.path.basename(job_path)} ---")

    try:
        # Load job input
        job_input_data = load_job_input(job_path)
        company = job_input_data.get('company_name', 'N/A')
        title = job_input_data.get('job_title', 'N/A')

        # --- v7.5: Cost Ceiling Check (Unchanged) ---
        jd_length = len(job_input_data.get('job_description', ''))
        estimated_tokens = (jd_length * 0.75) + 30000
        estimated_cost = (estimated_tokens / 1000) * 0.005
        
        cost_ceiling = CONFIG.cost_config.cost_ceiling_per_workflow
        if estimated_cost > cost_ceiling:
            raise Exception(f"Cost ceiling exceeded (Est: ${estimated_cost:.2f})")

        # --- v7.5: Run the Graph ---
        app, _ = get_compiled_graph()
        
        # Load master resume
        master_resume = load_job_input(CONFIG.file_paths.default_master_resume)

        # --- v9.5: Sanitize PII (Item #1) ---
        sanitizer = PIISanitizerAgent()
        sanitized_resume = sanitizer.run(master_resume)
        # -------------------------------------

        workflow_id = str(uuid.uuid4())
        run_config = {"configurable": {"thread_id": workflow_id}}
        
        # Define the initial state for the graph
        inputs = {
            "master_resume": sanitized_resume, # v9.5: Use sanitized resume
            "job_input": {
                "raw_jd": job_input_data['job_description'],
                "company": job_input_data['company_name'],
                "job_title": job_input_data['job_title']
            },
            "artifacts": {},
            "replan_count": 0,
            "workflow_id": workflow_id,
            "original_draft": "",
            "human_approved_draft": "",
            "preference_insight": None,
            "provenance_ledger": [] # v9.5: Init provenance ledger (Item #2)
        }
        
        # --- v7.5: Invoke the Graph ---
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
        
logger.info(f"--- Finished v9.5 job: {company} - {title} ---")
        
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
    os.makedirs(BATCH_QUEUE_DIR, exist_ok=True)
    os.makedirs(BATCH_COMPLETE_DIR, exist_ok=True)
    
    job_files = [os.path.join(BATCH_QUEUE_DIR, f) for f in os.listdir(BATCH_QUEUE_DIR) if f.endswith('.json')]
    if not job_files:
logger.info("v9.5 Batch process starting. No jobs found in queue.")
        return

logger.info(f"v9.5 Batch process starting. Found {len(job_files)} jobs.")
    
    max_workers = CONFIG.batch_config.max_parallel_workers
    logger.info(f"Running batch with up to {max_workers} parallel workers.")

    if not os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "company_name", "job_title", "overall_status", "workflow_id", "error_message"])

    # v7.5: Use ProcessPoolExecutor to run jobs in parallel
    all_results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        try:
            results_iterable = executor.map(process_single_job, job_files)
            all_results = list(results_iterable)
        except Exception as e:
            logger.critical(f"A critical error occurred during parallel execution: {e}")
            
    # Write results to CSV
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
        
logger.info(f"v9.5 Batch process complete.")
    
    # Meta-Learning trigger
    if CONFIG.meta_loop_config.enable_meta_learning:
        logger.info("Post-batch meta-learning enabled. Triggering learning loop...")
        if META_LEARNER_AVAILABLE:
            try:
                run_meta_learning()
                logger.info("Meta-learning loop completed successfully.")
            except Exception as e:
                logger.error(f"Meta-learning loop failed: {e}")
        else:
logger.warning("Meta-learning is enabled, but 'run_learning_v9_5' could not be imported.")
    else:
        logger.info("Post-batch meta-learning is disabled in config. Skipping.")


if __name__ == "__main__":
    run_batch()
