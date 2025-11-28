# File: run_batch_v6.5.py
# Overwrites: run_batch_v6_4.py
# v6.5: Parallel Batch Processing & Automated Learning
#
# v6.5 (Based on v7.0 Architecture) CHANGES:
# - Updated all imports from v6_4 to v6_5.
# - Imports 'WorkflowV65' from 'main_v6.5'.
# - Imports 'run_meta_learning' from 'run_learning_v6_5'.
# - Updated cost estimation logic in 'process_single_job' to reflect
#   the new v7.0 architecture (30k token assumption, $0.005 avg cost).
# - Updated logger name and summary file name to v6.5.

import os
import csv
import json
import logging
import shutil
import concurrent.futures
from datetime import datetime
from typing import Dict, Any

# Imports from its *own* versioned files (v6.5)
from main_v6_5 import WorkflowV65, setup_logging
from core_v6_5 import CONFIG, CircuitBreakerOpenError

# v6.5: Import the meta-learner to be triggered automatically
try:
    from run_learning_v6_5 import run_meta_learning
    META_LEARNER_AVAILABLE = True
except ImportError:
    META_LEARNER_AVAILABLE = False


logger = logging.getLogger("batch_runner_v6_5")
# Note: setup_logging() is called from main_v6_5, which uses core_v6_5's CONFIG
# This is safe as long as this script isn't run *before* core_v6_5/config exist
# We'll call it here to be safe.
try:
    setup_logging(debug_mode=False)
except Exception as e:
    print(f"Warning: setup_logging failed (this is ok if core_v6_5 not fully present): {e}")
    logging.basicConfig(level=logging.INFO)


BATCH_QUEUE_DIR = "batch_queue"
BATCH_COMPLETE_DIR = "batch_complete"
SUMMARY_FILE = "batch_summary_v6_5.csv"

def process_single_job(job_path: str) -> Dict[str, Any]:
    """
    Wraps the execution of a single job for the parallel executor.
    Returns a dictionary for the summary CSV.
    """
    company, title, status, workflow_id, error = "N/A", "N/A", "FATAL", "N/A", ""
    logger.info(f"--- Starting v6.5 job: {os.path.basename(job_path)} ---")

    try:
        # Load job input
        with open(job_path, 'r') as f:
            job_input = json.load(f)
        company = job_input.get('company_name', 'N/A')
        title = job_input.get('job_title', 'N/A')

        # --- v6.5: Cost Ceiling Check (Updated for v7.0 Architecture) ---
        jd_length = len(job_input.get('job_description', ''))
        # Use new token/cost assumptions from agent_swarm_v6.5
        estimated_tokens = (jd_length * 0.75) + 30000 # 30k token assumption
        estimated_cost = (estimated_tokens / 1000) * 0.005 # $0.005 avg cost
        
        cost_ceiling = CONFIG.cost_config.cost_ceiling_per_workflow
        if estimated_cost > cost_ceiling:
            logger.warning(f"Job {os.path.basename(job_path)} skipped. Est cost ${estimated_cost:.2f} > ceiling ${cost_ceiling}")
            status, error = "SKIPPED", f"Cost ceiling exceeded (Est: ${estimated_cost:.2f})"
            return {
                "timestamp": datetime.now().isoformat(),
                "company": company,
                "title": title,
                "status": status,
                "workflow_id": "N/A",
                "error": error,
                "job_file": job_path
            }

        # Run workflow
        workflow = WorkflowV65() # v6.5 update
        results = workflow.run(
            job_description=job_input['job_description'],
            company_name=company,
            job_title=title,
            master_resume_path=CONFIG.file_paths.default_master_resume,
            output_dir=None
        )
        
        # Extract results
        status = results.get('overall_status', 'FAILED_FATAL')
        workflow_id = results.get('execution_metadata', {}).get('workflow_id', 'N/A')
        error = results.get('error', '')

    except CircuitBreakerOpenError as e:
        logger.error(f"Job {os.path.basename(job_path)} skipped. Circuit breaker is OPEN: {e}")
        status, error = "SKIPPED", f"CircuitBreakerOpen: {e}"

    except Exception as e:
        logger.critical(f"FATAL error running job {os.path.basename(job_path)}: {e}", exc_info=True)
        error = str(e)
        
    finally:
        # Move file to complete
        try:
            shutil.move(job_path, os.path.join(BATCH_COMPLETE_DIR, os.path.basename(job_path)))
        except Exception as e:
            logger.error(f"Failed to move file {os.path.basename(job_path)}: {e}")
        
        logger.info(f"--- Finished v6.5 job: {company} - {title} ---")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "company": company,
            "title": title,
            "status": status,
            "workflow_id": workflow_id,
            "error": error,
            "job_file": job_path
        }


def run_batch():
    """
    Main batch processing loop.
    Processes all .json files in batch_queue/ directory in parallel.
    """
    # Ensure directories exist
    os.makedirs(BATCH_QUEUE_DIR, exist_ok=True)
    os.makedirs(BATCH_COMPLETE_DIR, exist_ok=True)
    
    # Get all job files
    job_files = [os.path.join(BATCH_QUEUE_DIR, f) for f in os.listdir(BATCH_QUEUE_DIR) if f.endswith('.json')]
    if not job_files:
        logger.info("v6.5 Batch process starting. No jobs found in queue.")
        return

    logger.info(f"v6.5 Batch process starting. Found {len(job_files)} jobs.")
    
    # v6.5: Read parallel worker count from config
    max_workers = CONFIG.batch_config.max_parallel_workers
    logger.info(f"Running batch with up to {max_workers} parallel workers.")

    # Initialize summary file if it doesn't exist
    if not os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "company_name", "job_title", "overall_status", "workflow_id", "error_message"])

    # v6.5: Use ProcessPoolExecutor to run jobs in parallel
    all_results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # map() runs the function for each item and returns results in order
        try:
            results_iterable = executor.map(process_single_job, job_files)
            all_results = list(results_iterable) # Collect all results
        except Exception as e:
            logger.critical(f"A critical error occurred during parallel execution: {e}")
            
    # Now, write all results to CSV at once
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
        
    logger.info(f"v6.5 Batch process complete.")
    
    # --- v6.5: Automated Post-Batch Meta-Learning ---
    if CONFIG.meta_loop_config.enable_meta_learning:
        logger.info("Post-batch meta-learning enabled. Triggering learning loop...")
        if META_LEARNER_AVAILABLE:
            try:
                run_meta_learning() # v6.5 update
                logger.info("Meta-learning loop completed successfully.")
            except Exception as e:
                logger.error(f"Meta-learning loop failed: {e}")
        else:
            logger.warning("Meta-learning is enabled, but 'run_learning_v6_5' could not be imported.")
    else:
        logger.info("Post-batch meta-learning is disabled in config. Skipping.")


if __name__ == "__main__":
    run_batch()