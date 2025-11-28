# File: run_batch_v6_2.py
# NEW: Batch processing harness for v6.2
# Processes all job_input.json files in batch_queue/ folder
# Writes one-line summaries to batch_summary_v6_2.csv
# Moves completed files to batch_complete/

import os
import csv
import json
import logging
import shutil
from datetime import datetime

# Imports from its *own* versioned files
from main_v6_2 import WorkflowV62, setup_logging 
from core_v6_2 import CONFIG, CircuitBreakerOpenError

logger = logging.getLogger("batch_runner_v6_2")
setup_logging(debug_mode=False)

BATCH_QUEUE_DIR = "batch_queue"
BATCH_COMPLETE_DIR = "batch_complete"
SUMMARY_FILE = "batch_summary_v6_2.csv"

def run_batch():
    """
    Main batch processing loop.
    Processes all .json files in batch_queue/ directory.
    """
    # Ensure directories exist
    os.makedirs(BATCH_QUEUE_DIR, exist_ok=True)
    os.makedirs(BATCH_COMPLETE_DIR, exist_ok=True)
    
    # Get all job files
    job_files = [f for f in os.listdir(BATCH_QUEUE_DIR) if f.endswith('.json')]
    logger.info(f"v6.2 Batch process starting. Found {len(job_files)} jobs.")
    consecutive_failures = 0
    FAILURE_THRESHOLD = 3  # v6.2: Alerting - halt batch after 3 consecutive failures


    # Initialize summary file if it doesn't exist
    if not os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "company_name", "job_title", "overall_status", "workflow_id", "error_message"])

    # Process each job
    for job_file in job_files:
        job_path = os.path.join(BATCH_QUEUE_DIR, job_file)
        company, title, status, workflow_id, error = "N/A", "N/A", "FATAL", "N/A", ""

        try:
            # Load job input
            with open(job_path, 'r') as f:
                job_input = json.load(f)
            company = job_input.get('company_name', 'N/A')
            title = job_input.get('job_title', 'N/A')
            logger.info(f"--- Starting v6.2 job: {company} - {title} ---")

            # --- v6.2: Cost Ceiling Check (Spell #6) - ACTIVATED ---
            # Simple heuristic: estimate cost based on job description length
            jd_length = len(job_input.get('job_description', ''))
            # Rough estimate: 0.75 tokens per char, $0.0006 per 1K output tokens
            # Assume ~10 hops with 2K tokens each = 20K tokens total
            estimated_tokens = (jd_length * 0.75) + 20000
            estimated_cost = (estimated_tokens / 1000) * 0.0006
            
            cost_ceiling = CONFIG.cost_config.cost_ceiling_per_workflow
            if estimated_cost > cost_ceiling:
                logger.warning(f"Job {job_file} skipped. Est cost ${estimated_cost:.2f} > ceiling ${cost_ceiling}")
                status, error = "SKIPPED", f"Cost ceiling exceeded (Est: ${estimated_cost:.2f})"
                consecutive_failures = 0  # Don't count as failure
                continue

            # Run workflow
            workflow = WorkflowV62()
            results = workflow.run(
                job_description=job_input['job_description'],
                company_name=company,
                job_title=title,
                master_resume_path=CONFIG.file_paths.default_master_resume,
                output_dir=None
            )
            
            # Extract results
            status = results.get('overall_status', 'FAILED')
            workflow_id = results.get('execution_metadata', {}).get('workflow_id', 'N/A')
            error = results.get('error', '')
            
            # Reset failure counter on success
            consecutive_failures = 0

        # --- v6.2: Circuit Breaker Catch (Spell #5) ---
        except CircuitBreakerOpenError as e:
            logger.error(f"Job {job_file} skipped. Circuit breaker is OPEN: {e}")
            status, error = "SKIPPED", f"CircuitBreakerOpen: {e}"
            consecutive_failures += 1

        except Exception as e:
            logger.critical(f"FATAL error running job {job_file}: {e}", exc_info=True)
            error = str(e)
            consecutive_failures += 1
            
        finally:
            # Write summary line
            with open(SUMMARY_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now().isoformat(), company, title, status, workflow_id, error])
            
            # Move file to complete
            try:
                shutil.move(job_path, os.path.join(BATCH_COMPLETE_DIR, job_file))
            except Exception as e:
                logger.error(f"Failed to move file {job_file}: {e}")
            
            logger.info(f"--- Finished v6.2 job: {company} - {title} ---")
            
            # --- v6.2: Alerting (Spell #9) ---
            if consecutive_failures >= FAILURE_THRESHOLD:
                logger.critical(f"BATCH HALTED: {consecutive_failures} consecutive failures. Stopping batch.")
                break  # Stop the batch

    logger.info(f"v6.2 Batch process complete.")

if __name__ == "__main__":
    run_batch()
