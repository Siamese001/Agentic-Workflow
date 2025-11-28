# File: run_batch_v9_9.py
# Overwrites: run_batch_v9_8.py
# Version: 9.9 (Security & Error Handling Hardening)
#
# v9.9 P1/P2 CHANGES:
# - Updated imports to v9_8 modules
# - Version tracking to 9.8
# - Added P2: Cost tracking in batch summary

import os
import csv
import json
import logging
import shutil
import concurrent.futures
import uuid
from datetime import datetime
from typing import Dict, Any

# Imports from v9.9 versioned files
from main_v9_9 import setup_logging, load_job_input
from core_v9_9 import CONFIG, CircuitBreakerOpenError, COST_TRACKER

# v9.9: Import graph builder and checkpointer
from agent_swarm_v9_9 import get_graph_app, PIISanitizerAgent
from langgraph.checkpoint.redis import RedisSaver

# v9.9: Import meta-learner
try:
    from run_learning_v9_9 import run_meta_learning
    META_LEARNER_AVAILABLE = True
except ImportError:
    META_LEARNER_AVAILABLE = False


logger = logging.getLogger("batch_runner_v9_9")
try:
    setup_logging(debug_mode=False)
except Exception as e:
    print(f"Warning: setup_logging failed: {e}")
    logging.basicConfig(level=logging.INFO)


BATCH_QUEUE_DIR = "batch_queue"
BATCH_COMPLETE_DIR = "batch_complete"
SUMMARY_FILE = "batch_summary_v9_9.csv"

checkpointer = None
app = None

def get_compiled_graph():
    """Initialize graph and checkpointer within new process."""
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
    """Execute single job for parallel executor."""
    company, title, status, workflow_id, error_msg = "N/A", "N/A", "FATAL", "N/A", ""
    cost = 0.0
    
    logger.info(f"--- Starting v9.9 job: {os.path.basename(job_path)} ---")

    try:
        job_input_data = load_job_input(job_path)
        company = job_input_data.get('company_name', 'N/A')
        title = job_input_data.get('job_title', 'N/A')

        jd_length = len(job_input_data.get('job_description', ''))
        estimated_tokens = (jd_length * 0.75) + 30000
        estimated_cost = (estimated_tokens / 1000) * 0.005
        
        cost_ceiling = CONFIG.cost_config.cost_ceiling_per_workflow
        if estimated_cost > cost_ceiling:
            raise Exception(f"Cost ceiling exceeded (Est: ${estimated_cost:.2f})")

        app, _ = get_compiled_graph()
        master_resume = load_job_input(CONFIG.file_paths.default_master_resume)

        sanitizer = PIISanitizerAgent()
        sanitized_resume = sanitizer.run(master_resume)

        workflow_id = str(uuid.uuid4())
        run_config = {"configurable": {"thread_id": workflow_id}}
        
        inputs = {
            "master_resume": sanitized_resume,
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
            "provenance_ledger": [],
            # P0 additions
            "strategy_thoughts": [],
            "selected_strategy": None,
            "local_retry_count": 0,
            "bullet_critique_history": [],
            # P1 additions
            "conductor_thoughts": [],
            "conductor_plan": None,
            "available_tools": [],
            "tool_execution_history": [],
            "ambiguity_detected": False,
            "hil_feedback_queue": [],
            "hil_responses": [],
            # P2 additions
            "agent_costs": {},
            "total_workflow_cost": 0.0,
            "agent_reliability_scores": {}
        }
        
        final_state = app.invoke(inputs, config=run_config)
        
        # P2: Get actual cost
        cost_summary = COST_TRACKER.get_cost_summary()
        cost = cost_summary.get('total_workflow_cost', 0.0)
        
        validation = final_state.get('artifacts', {}).get('validation_results', {})
        if validation.get('overall_passed', False):
            status = "SUCCESS"
            error_msg = ""
        else:
            status = "FAILED_QA"
            failed_count = validation.get('failed_checks_count', len(validation.get('failed_checks', [])))
            error_msg = f"{failed_count} QA check(s) failed."

    except CircuitBreakerOpenError as e:
        logger.error(f"Job {os.path.basename(job_path)} skipped. Circuit breaker OPEN: {e}")
        status, error_msg = "SKIPPED", f"CircuitBreakerOpen: {e}"

    except Exception as e:
        logger.critical(f"FATAL error: {e}", exc_info=True)
        status, error_msg = "FAILED_FATAL", str(e)
        
    finally:
        try:
            shutil.move(job_path, os.path.join(BATCH_COMPLETE_DIR, os.path.basename(job_path)))
        except Exception as e:
            logger.error(f"Failed to move file: {e}")
        
        logger.info(f"--- Finished v9.9 job: {company} - {title} ---")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "company": company,
            "title": title,
            "status": status,
            "workflow_id": workflow_id,
            "error": error_msg,
            "cost": cost,
            "job_file": job_path
        }


def run_batch():
    """Main batch processing loop."""
    os.makedirs(BATCH_QUEUE_DIR, exist_ok=True)
    os.makedirs(BATCH_COMPLETE_DIR, exist_ok=True)
    
    job_files = [os.path.join(BATCH_QUEUE_DIR, f) for f in os.listdir(BATCH_QUEUE_DIR) if f.endswith('.json')]
    if not job_files:
        logger.info("v9.9 Batch process starting. No jobs found.")
        return

    logger.info(f"v9.9 Batch process starting. Found {len(job_files)} jobs.")
    
    max_workers = CONFIG.batch_config.max_parallel_workers
    logger.info(f"Running with {max_workers} parallel workers.")

    if not os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "company_name", "job_title", "overall_status", "workflow_id", "cost_usd", "error_message"])

    all_results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        try:
            results_iterable = executor.map(process_single_job, job_files)
            all_results = list(results_iterable)
        except Exception as e:
            logger.critical(f"Critical error during parallel execution: {e}")
            
    try:
        with open(SUMMARY_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            for summary in all_results:
                writer.writerow([
                    summary["timestamp"], summary["company"], summary["title"],
                    summary["status"], summary["workflow_id"], summary.get("cost", 0.0), summary["error"]
                ])
        logger.info(f"Batch summary updated with {len(all_results)} results.")
    except Exception as e:
        logger.error(f"Failed to write batch summary: {e}")
    
    # P2: Cost summary
    total_cost = sum(r.get("cost", 0.0) for r in all_results)
    logger.info(f"Total batch cost: ${total_cost:.4f}")
        
    logger.info(f"v9.9 Batch process complete.")
    
    if CONFIG.meta_loop_config.enable_meta_learning:
        logger.info("Post-batch meta-learning enabled...")
        if META_LEARNER_AVAILABLE:
            try:
                run_meta_learning()
                logger.info("Meta-learning loop completed.")
            except Exception as e:
                logger.error(f"Meta-learning failed: {e}")
        else:
            logger.warning("Meta-learning enabled but 'run_learning_v9_8' not found.")
    else:
        logger.info("Post-batch meta-learning disabled.")


if __name__ == "__main__":
    run_batch()
