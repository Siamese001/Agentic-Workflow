# File: main_v10_7.py
# Version: 10.7 (Refactored)
#
# v10.7 REFACTOR CHANGES:
# - UPDATED: All versioning to v10_7.
# - UPDATED: create_workflow_context call updated to v10_7.
#
# v10.7 MAJOR CHANGES:
# - IMPLEMENTED (Fix #9): run_workflow_async refactored to use
#   `app.astream_events` to listen for `on_chat_model_stream` events.
#   This now prints real-time streaming tokens (thoughts, partial JSON)
#   from the ReAct conductors.
# - IMPLEMENTED (Fix #30): Checks for 'failed_constitution' in the
#   final state to correctly report constitutional failures.
# - FIXED: All v10_5 imports and class names updated to v10_7.
# - FIXED: Changed config file name to master_config_v10_7.json.

import argparse
import asyncio
import json
import logging
import os
import sys
import uuid
from typing import Any

# v10.7: Import from new orchestration/stacks
from agent_orchestration_v10_7 import get_graph_app

# v10.7: Import from new core
from core_v10_7 import (
    ConfigV10_7,
    FileIOError,
    MainGraphState,
    WorkflowError,
    cleanup_workflow_chroma_collection,
    create_workflow_context,
    get_checkpointer,
)

# v10.7: Logger name updated
logger = logging.getLogger("main_v10_7")

def setup_logging(config: ConfigV10_7, debug_mode: bool = False):
    """Configure logging, now accepts a config object."""
    log_dir = os.path.dirname(config.logging_config.log_file)
    os.makedirs(log_dir, exist_ok=True)

    level = logging.DEBUG if debug_mode else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.logging_config.log_file),
            logging.StreamHandler(sys.stdout) # v10.7: Log to stdout for streaming
        ]
    )

    # Configure metrics logger
    metrics_log_path = config.logging_config.metrics_log_path
    metrics_logger = logging.getLogger("core_v10_7.MetricsCollector")
    metrics_logger.setLevel(logging.INFO)
    try:
        metrics_logger.addHandler(logging.FileHandler(metrics_log_path))
    except OSError as e:
        logging.error(f"Failed to add file handler for metrics logger: {e}")

    logger.info(f"v10.7 Logging initialized: {config.logging_config.log_file}")
    logger.info(f"v10.7 Metrics logging to: {metrics_log_path}")

def load_job_input(path: str) -> dict[str, Any]:
    """Load job input JSON"""
    try:
        with open(path) as f:
            data = json.load(f)
        logger.info(f"Loaded job input: {path}")
        return data
    except OSError as e:
        raise FileIOError(f"Failed to load {path}: {e}")
    except json.JSONDecodeError as e:
        raise FileIOError(f"Invalid JSON in {path}: {e}")

async def run_workflow_async(
    config: ConfigV10_7,
    job_input_path: str,
    master_resume_path: str,
    debug_mode: bool = False,
    enable_hil: bool = True,
    enable_mcp: bool | None = None
) -> dict[str, Any]:
    """Run workflow asynchronously with v10.7 streaming and validation"""

    logger.info("===== Starting v10.7 Instructional Injection Workflow =====")

    job_input_data = load_job_input(job_input_path)
    master_resume = load_job_input(master_resume_path)

    company = job_input_data.get('company_name', 'N/A')
    title = job_input_data.get('job_title', 'N/A')

    logger.info(f"Job: {company} - {title}")

    # --- v10.7: REFACTOR: COMPOSITION ROOT ---
    context = create_workflow_context(config, db=config.redis_config.db)
    # --- v10.7: REFACTOR END ---

    checkpointer = get_checkpointer(config)

    app = get_graph_app(checkpointer, context, enable_hil=enable_hil, enable_mcp=enable_mcp)

    workflow_id = str(uuid.uuid4())
    context.workflow_id = workflow_id
    run_config = {"configurable": {"thread_id": workflow_id}}

    initial_state = MainGraphState()
    initial_state.resume.master_resume = master_resume
    initial_state.job.raw_jd = job_input_data['job_description']
    initial_state.job.company = job_input_data['company_name']
    initial_state.job.job_title = job_input_data['job_title']
    initial_state.metadata.workflow_id = workflow_id

    state_dict = initial_state.to_dict()

    logger.info(f"Workflow ID: {workflow_id}")

    try:
        final_state_dict = None

        # v10.7 (Fix #9): Use astream_events for real-time streaming
        current_node = ""
        print("\n--- Workflow Stream (v10.7) ---", flush=True)

        async for event in app.astream_events(state_dict, run_config, version="v1"):
            kind = event["event"]

            if kind == "on_graph_start":
                logger.info("Graph execution started.")

            if kind == "on_node_start":
                current_node = event["data"]["name"]
                logger.info(f"\n--- Executing Node: {current_node} ---")

            # v10.7 (Fix #9): Handle real-time token streaming
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    # Print the streaming token to stdout
                    print(chunk.content, end="", flush=True)

            if kind == "on_node_end":
                if current_node in event["data"]["output"]:
                    final_state_dict = event["data"]["output"][current_node]

                if current_node == "HIL_PAUSE":
                    print("\n", flush=True) # Newline after streaming
                    logger.warning("="*80)
                    logger.warning("🛑 WORKFLOW PAUSED: HUMAN INPUT REQUIRED 🛑")
                    logger.warning(f"Please review and provide feedback for: {workflow_id}")
                    logger.warning("="*80)

            if kind == "on_graph_end":
                final_state_dict = event["data"]["output"]
                print("\n--- Workflow Stream Complete ---", flush=True)

        if final_state_dict is None:
            raise WorkflowError("Graph stream finished with no final state.")

        # v10.7: Check for rejection
        if "REJECT_JOB" in final_state_dict:
             logger.error(f"Workflow {workflow_id} REJECTED.")
             raise WorkflowError("Workflow rejected, likely due to prompt injection.")

        # v10.7 (Fix #30): Check for constitutional failure
        if "failed_constitution" in final_state_dict.get("qa", {}).get("constitutional_review", {}):
             logger.error(f"Workflow {workflow_id} FAILED CONSTITUTIONAL REVIEW.")
             raise WorkflowError("Workflow rejected due to constitutional failure.")

        final_state = MainGraphState.from_dict(final_state_dict)

        cache_stats = context.cache_manager.get_stats()
        logger.info(f"Cache performance: {cache_stats}")

        cost_summary = context.cost_tracker.get_cost_summary(workflow_id)
        logger.info(f"Total workflow cost: ${cost_summary['total_workflow_cost']:.4f}")

        logger.info("--- Workflow Metrics Summary (v10.7) ---")
        for metric in context.metrics_collector.get_summary():
             logger.info(f"  - {metric['agent_name']}::{metric['task_name']} | {metric['duration_ms']:.2f}ms | Success: {metric['success']}")

        # v10.7 REFACTOR: Call centralized cleanup helper
        cleanup_workflow_chroma_collection(context)

        return {
            "status": "SUCCESS",
            "workflow_id": workflow_id,
            "cost": cost_summary['total_workflow_cost'],
            "cache_stats": cache_stats,
            "final_artifacts": final_state.artifacts.artifacts
        }

    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        return {
            "status": "FAILED_FATAL",
            "workflow_id": workflow_id,
            "error": str(e)
        }

    finally:
        logger.info("===== v10.7 Workflow Complete =====")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Resume Generation Engine v10.7")
    parser.add_argument('-j', '--job', required=True, help='Path to job_input.json')
    parser.add_argument('-m', '--master', required=True, help='Path to master_resume.json')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-hil', action='store_true', help='Disable Human-in-the-Loop')

    mcp_group = parser.add_mutually_exclusive_group()
    mcp_group.add_argument('--disable-mcp', action='store_true', help='Disable MCP wrapping even if config enables it')
    mcp_group.add_argument('--enable-mcp', action='store_true', help='Force enable MCP wrapping even if config disables it')

    args = parser.parse_args()

    # v10.7: Instantiate ConfigV10_7 here, ONCE.
    try:
        config = ConfigV10_7("master_config_v10_7.json")
    except Exception as e:
        print(f"FATAL: Failed to load master_config_v10_7.json: {e}", file=sys.stderr)
        sys.exit(1)

    setup_logging(config, debug_mode=args.debug)

    mcp_toggle: bool | None = None
    if args.disable_mcp:
        mcp_toggle = False
    elif args.enable_mcp:
        mcp_toggle = True

    result = asyncio.run(run_workflow_async(
        config=config,
        job_input_path=args.job,
        master_resume_path=args.master,
        debug_mode=args.debug,
        enable_hil=not args.no_hil,
        enable_mcp=mcp_toggle
    ))

    print("\n" + "="*80)
    print(f"WORKFLOW RESULT: {result['status']}")
    print(f"Workflow ID: {result.get('workflow_id')}")
    if result.get('status') == 'SUCCESS':
        print(f"Total Cost: ${result.get('cost', 0.0):.4f}")
        print(f"Cache Stats: {result.get('cache_stats')}")
    else:
        print(f"Error: {result.get('error')}")
    print("="*80)

    if result['status'] == 'SUCCESS':
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

# ============================================================================
# END OF main_v10_7.py
# ============================================================================
