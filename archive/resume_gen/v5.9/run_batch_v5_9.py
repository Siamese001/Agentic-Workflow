# File: run_batch_v5_9.py
# NEW: Batch processing harness for v5.9
# Processes all job_input.json files in batch_queue/ folder
# Writes one-line summaries to batch_summary_v5_9.csv
# Moves completed files to batch_complete/

import os
import csv
import json
import logging
import shutil
from datetime import datetime

# Imports from its *own* versioned files
from main_v5_9 import WorkflowV59, setup_logging 
from core_v5_9 import CONFIG

logger = logging.getLogger("batch_runner_v5_9")
setup_logging(debug_mode=False)

BATCH_QUEUE_DIR = "batch_queue"
BATCH_COMPLETE_DIR = "batch_complete"
SUMMARY_FILE = "batch_summary_v5_9.csv"

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
    logger.info(f"v5.9 Batch process starting. Found {len(job_files)} jobs.")

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
            logger.info(f"--- Starting v5.9 job: {company} - {title} ---")

            # Run workflow
            workflow = WorkflowV59()
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

        except Exception as e:
            logger.critical(f"FATAL error running job {job_file}: {e}", exc_info=True)
            error = str(e)
            
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
            
            logger.info(f"--- Finished v5.9 job: {company} - {title} ---")

    logger.info(f"v5.9 Batch process complete. Processed {len(job_files)} jobs.")

if __name__ == "__main__":
    run_batch()
