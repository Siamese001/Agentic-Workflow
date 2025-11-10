# File: run_batch_v10_1.py
# Version: 10.1 (Feedback-Driven Adaptation)

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
from agent_swarm_v10_1 import get_graph_app, PIISanitizerAgent
from langgraph.checkpoint.redis import RedisSaver

try:
    from run_learning_v10_1 import run_meta_learning
    META_LEARNER_AVAILABLE = True
except ImportError:
    META_LEARNER_AVAILABLE = False

logger = logging.getLogger("batch_runner_v10_1")

try:
    setup_logging(debug_mode=False)
except Exception as e:
    print(f"Warning: setup_logging failed: {e}")
    logging.basicConfig(level=logging.INFO)

BATCH_QUEUE_DIR = "batch_queue"
BATCH_COMPLETE_DIR = "batch_complete"
SUMMARY_FILE = "batch_summary_v10_1.csv"

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

async def run_batch_async():
    """Main async batch processing"""
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
    
    logger.info(f"v10.1 Batch process starting. Found {len(job_files)} jobs.")
    
    redis_client = redis.Redis(
        host=CONFIG.redis_config.host,
        port=CONFIG.redis_config.port,
        db=CONFIG.redis_config.db
    )
    
    context = WorkflowContext(CONFIG, redis_client)
    logger.info("Initialized shared WorkflowContext for batch")
    
    batch_aggregator = BatchFeedbackAggregator()
    
    checkpointer = RedisSaver(
        host=CONFIG.redis_config.host,
        port=CONFIG.redis_config.port,
        db=CONFIG.redis_config.db
    )
    
    app = get_graph_app(checkpointer, context, enable_hil=False)
    logger.info("Compiled shared LangGraph workflow")
    
    if not os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "company_name", "job_title", 
                "overall_status", "workflow_id", "cost_usd", "error_message"
            ])
    
    logger.info("v10.1 Batch process complete.")

def run_batch():
    """Synchronous wrapper for async batch processing"""
    asyncio.run(run_batch_async())

if __name__ == "__main__":
    run_batch()

# ============================================================================
# END OF run_batch_v10_1.py
# ============================================================================
