# FILE: v10_9_clean/run_batch_v10_9.py
"""
Unified Batch Runner (v10_9) - PRODUCTION READY

This module restores the "Fleet Control Plane" capabilities from v10.7.
It wraps the L1->L5 runtime in a resilient batch processing harness.

Capabilities Restored:
    • Semaphore-based Concurrency Control
    • Circuit Breaker (Stop on Cascading Failures)
    • Backpressure (Queue Size Limits)
    • Post-Batch Meta-Learning Trigger
    • CSV Summary Reporting

Architecture:
    • External Orchestrator (Calls main_v10_9)
    • File-based Queue (./batch_queue -> ./batch_complete)
"""

from __future__ import annotations
import asyncio
import logging
import os
import json
import shutil
import time
import csv
from dataclasses import dataclass
from typing import List, Dict, Any

from main_v10_9 import run_workflow_v10_9
from meta_learning import run_meta_learning_loop
from observability import Telemetry

# Config Defaults
BATCH_QUEUE_DIR = "batch_queue"
BATCH_COMPLETE_DIR = "batch_complete"
BATCH_ERROR_DIR = "batch_error"
SUMMARY_FILE = "batch_summary_v10_9.csv"
MAX_CONCURRENCY = 5
CIRCUIT_BREAKER_THRESHOLD = 3
MAX_QUEUE_SIZE = 100

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/batch_v10_9.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("v10_9.batch")

# ============================================================================
# 1. RESILIENCE PRIMITIVES
# ============================================================================

class CircuitBreaker:
    """
    Protects the system from runaway costs/errors.
    """
    def __init__(self, threshold: int):
        self.threshold = threshold
        self.failures = 0
        self.is_open = False

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.threshold:
            self.is_open = True
            logger.error(f"🔥 CIRCUIT BREAKER TRIPPED after {self.failures} failures.")

    def record_success(self):
        self.failures = 0

    def check(self):
        if self.is_open:
            raise RuntimeError("Circuit Breaker is OPEN. Batch halted.")

# ============================================================================
# 2. JOB PROCESSOR
# ============================================================================

async def process_job(
    filepath: str, 
    semaphore: asyncio.Semaphore, 
    breaker: CircuitBreaker
) -> Dict[str, Any]:
    """
    Executes a single job file through the v10.9 runtime.
    """
    filename = os.path.basename(filepath)
    
    async with semaphore:
        breaker.check()
        
        logger.info(f"▶️ Starting job: {filename}")
        start_time = time.time()
        
        try:
            # 1. Load Input
            with open(filepath, 'r') as f:
                job_input = json.load(f)

            # 2. Execute Runtime (L1->L5)
            # We map the raw input to the expected state structure
            initial_state = {
                "workflow_id": f"batch_{int(start_time)}_{filename}",
                "job": job_input.get("job_description", {}),
                "resume": {"master_resume": job_input.get("master_resume", {})},
                "objective": f"Optimize resume for {job_input.get('company_name', 'Target')}",
                "audience": "recruiter"
            }
            
            result_state = await run_workflow_v10_9(initial_state)
            
            # 3. Verify Outcome
            qa_res = result_state.get("qa_result", {})
            passed = qa_res.get("report", {}).get("passed", False)
            
            if not passed:
                logger.warning(f"⚠️ Job {filename} failed QA validation.")
                # We count this as a soft failure, but don't trip breaker unless it crashes
            
            # 4. Finalize
            breaker.record_success()
            duration = time.time() - start_time
            
            # Move to complete
            os.makedirs(BATCH_COMPLETE_DIR, exist_ok=True)
            shutil.move(filepath, os.path.join(BATCH_COMPLETE_DIR, filename))
            
            logger.info(f"✅ Finished {filename} in {duration:.2f}s")
            
            return {
                "file": filename,
                "status": "SUCCESS" if passed else "QA_FAIL",
                "duration": duration,
                "cost": 0.05, # Placeholder until CostTracker is fully wired
                "confidence": qa_res.get("confidence", 0.0)
            }

        except Exception as e:
            logger.error(f"❌ Failed {filename}: {e}", exc_info=True)
            breaker.record_failure()
            
            # Move to error
            os.makedirs(BATCH_ERROR_DIR, exist_ok=True)
            shutil.move(filepath, os.path.join(BATCH_ERROR_DIR, filename))
            
            return {
                "file": filename,
                "status": "CRASH",
                "error": str(e),
                "duration": time.time() - start_time
            }

# ============================================================================
# 3. BATCH ORCHESTRATOR
# ============================================================================

async def run_batch():
    # 1. Setup
    os.makedirs(BATCH_QUEUE_DIR, exist_ok=True)
    files = [os.path.join(BATCH_QUEUE_DIR, f) for f in os.listdir(BATCH_QUEUE_DIR) if f.endswith(".json")]
    
    if not files:
        logger.info("No jobs in queue.")
        return

    # 2. Backpressure Check
    if len(files) > MAX_QUEUE_SIZE:
        logger.error(f"Backpressure limit exceeded ({len(files)} > {MAX_QUEUE_SIZE}). Aborting.")
        return

    logger.info(f"🚀 Starting Batch: {len(files)} jobs | Concurrency: {MAX_CONCURRENCY}")

    # 3. Execution Loop
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    breaker = CircuitBreaker(CIRCUIT_BREAKER_THRESHOLD)
    
    tasks = [process_job(f, semaphore, breaker) for f in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 4. Reporting
    valid_results = [r for r in results if isinstance(r, dict)]
    _write_summary(valid_results)
    
    # 5. Meta-Learning Trigger
    logger.info("🧠 Triggering Meta-Learning Loop...")
    await run_meta_learning_loop()
    
    logger.info("🏁 Batch Complete.")

def _write_summary(results: List[Dict[str, Any]]):
    if not results: return
    
    path = os.path.join(BATCH_COMPLETE_DIR, SUMMARY_FILE)
    keys = results[0].keys()
    
    write_header = not os.path.exists(path)
    
    with open(path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        if write_header:
            writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    asyncio.run(run_batch())
