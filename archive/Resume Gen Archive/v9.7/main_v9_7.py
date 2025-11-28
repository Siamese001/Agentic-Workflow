# File: main_v9_7.py
# Overwrites: main_v9_6.py
# Version: 9.7 (P0 Enhancements)

# v9.7 P0 CHANGES:
# - Updated imports to v9_7 modules
# - Added initial state fields for ToT and local retry tracking
# - Version tracking updated to 9.7

# ============================================================================
# EXTERNAL IMPORTS
# ============================================================================
import argparse
import json
import logging
import logging.handlers
import os
import sys
import uuid
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import from consolidated modules (v9.7)
from core_v9_7 import (
    CONFIG, DATA_DIR, OUTPUT_DIR, CACHE_DIR
)

# v9.7: Import from the new graph builder
from agent_swarm_v9_7 import get_graph_app, PIISanitizerAgent

# v7.5: Import LangGraph + Redis
from langgraph.checkpoint.redis import RedisSaver

logger = logging.getLogger(__name__)

# Version info
__version__ = "9.7.0-p0-enhancements"

class JsonFormatter(logging.Formatter):
    """Formats log records as JSON objects."""
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "workflow_id": getattr(record, "workflow_id", "N/A"),
        }
        if "duration_ms" in record.__dict__:
            log_record["duration_ms"] = record.duration_ms
        if "status" in record.__dict__:
            log_record["status"] = record.status
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        # Include correlation IDs if present
        if hasattr(CONFIG.logging_config, 'correlation_ids') and CONFIG.logging_config.correlation_ids:
             if hasattr(record, 'correlation_id'):
                log_record['correlation_id'] = record.correlation_id
        
        return json.dumps(log_record)

logger = logging.getLogger(__name__)

# HELPER FUNCTIONS
# ============================================================================

def load_job_input(filepath: str) -> Dict[str, Any]:
    """Load job input from JSON file."""
    try:
        with open(filepath, 'r') as f:
            job_input = json.load(f)
        
        required_fields = ['company_name', 'job_title', 'job_description']
        missing_fields = [f for f in required_fields if f not in job_input]
        
        if missing_fields:
            raise ValueError(f"Missing required fields in job input: {missing_fields}")
        
        return job_input
    except Exception as e:
        logger.error(f"Failed to load job input: {e}")
        raise

def setup_logging(debug_mode: bool):
    """
    Configure structured logging based on CONFIG.
    """
    try:
        from core_v9_7 import CONFIG as LOG_CONFIG
    except ImportError:
        print("CRITICAL: core_v9_7.py not found. Logging setup failed.", file=sys.stderr)
        logging.basicConfig(level=logging.DEBUG if debug_mode else logging.INFO)
        return

    log_config = LOG_CONFIG.logging_config
    
    if debug_mode:
        log_level = log_config.debug_log_level
    else:
        log_level = log_config.log_level
        
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove default handler
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add File Handler (JSON) from CONFIG
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_config.log_file,
            maxBytes=log_config.log_rotation.max_bytes,
            backupCount=log_config.log_rotation.backup_count
        )
        
        if log_config.log_format == "json":
            file_handler.setFormatter(JsonFormatter())
        else:
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(workflow_id)s - %(message)s'))
            
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Error setting up file logger: {e}", file=sys.stderr)

    # Add Console Handler
    try:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        root_logger.addHandler(console_handler)
    except Exception as e:
        print(f"Error setting up console logger: {e}", file=sys.stderr)

    logger.info(f"Logging configured. Level: {log_level}, File: {log_config.log_file}")


def print_summary(results: Dict[str, Any], workflow_id: str, start_time: datetime):
    """Print workflow execution summary from final graph state."""
    print("\n" + "=" * 80)
    print(f"WORKFLOW EXECUTION SUMMARY (v9.7 P0 Enhancements)")
    print("=" * 80)
    
    execution_time = (datetime.now() - start_time).total_seconds()
    
    final_state = results
    validation = final_state.get('artifacts', {}).get('validation_results', {})
    
    # Determine overall status
    if validation.get('overall_passed', False):
        status = "✅ SUCCESS"
    else:
        status = "❌ FAILED_QA"
        
    print(f"\nStatus: {status}")
    print(f"\nExecution Time: {execution_time:.2f}s")
    print(f"Version: {__version__}")
    print(f"Workflow ID: {workflow_id}")
    
    # P0 Enhancements Summary
    print(f"\n--- P0 Enhancements Active ---")
    print(f"SafetyGuardStack: {'✓' if CONFIG.agent_stacks.safety_stack_enabled else '✗'}")
    print(f"Tree-of-Thoughts Strategy: {'✓' if CONFIG.agent_stacks.strategy_tot_enabled else '✗'}")
    print(f"LLM-Driven Prompting: {'✓' if CONFIG.agent_stacks.prompt_llm_driven else '✗'}")
    print(f"Local Self-Correction: {'✓' if CONFIG.agent_stacks.enable_local_retries else '✗'}")
    
    # Local retry stats
    local_retries = final_state.get('local_retry_count', 0)
    if local_retries > 0:
        print(f"\nLocal Self-Correction Retries: {local_retries}")
    
    # Validation results
    if validation:
        print(f"\nValidation Passed: {validation.get('overall_passed', False)}")
        failures = validation.get('failed_checks', [])
        if failures:
            print(f"Failed Checks ({len(failures)}):")
            for fail in failures[:5]:
                agent = fail.get('agent_name', fail.get('check_name', 'N/A'))
                details = fail.get('error', fail.get('details', 'No details'))
                print(f"  - {agent}: {details}")
            if len(failures) > 5:
                print(f"  ... and {len(failures) - 5} more.")

    # Artifacts
    artifacts = final_state.get('artifacts', {})
    if artifacts:
        print(f"\nArtifacts Generated: {len(artifacts)}")
        print(f"  - parsed_jd: {'OK' if 'parsed_jd' in artifacts else 'MISSING'}")
        print(f"  - selected_strategy: {'OK' if 'selected_strategy' in final_state else 'MISSING'}")
        print(f"  - engineered_prompt: {'OK' if 'engineered_prompt' in artifacts else 'MISSING'}")
        print(f"  - final_draft: {'OK' if 'final_draft' in artifacts else 'MISSING'}")
    
    print("\n" + "=" * 80)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def setup_tracing():
    """Configures LangSmith tracing if enabled."""
    if CONFIG.tracing_config.langsmith_enabled:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_API_KEY"] = str(CONFIG.tracing_config.langsmith_api_key)
        os.environ["LANGCHAIN_PROJECT"] = "ResumeFactory_v9_7"
        logger.info("✅ LangSmith Tracing is ENABLED.")
    else:
        logger.warning("LangSmith Tracing is DISABLED.")


def main():
    """
    Main entry point for V9.7 Workflow with P0 Enhancements.
    """
    script_path = os.path.relpath(__file__) if "__file__" in globals() else "main_v9_7.py"
    
    try:
        default_job_input = CONFIG.file_paths.default_job_input
        default_master_resume = CONFIG.file_paths.default_master_resume
    except Exception as e:
        print(f"FATAL: Could not load file_paths from config: {e}", file=sys.stderr)
        default_job_input = "job_input.json"
        default_master_resume = "master_resume.json"
    
    parser = argparse.ArgumentParser(
        description=f'V9.7 LangGraph Workflow with P0 Enhancements (Version: {__version__})',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python {script_path}                           # Run with default {default_job_input}
  python {script_path} -j custom_job.json        # Use custom job input file
  python {script_path} -m custom_master.json     # Use custom master resume
  python {script_path} -o /path/to/output        # Specify output directory
  python {script_path} --debug                   # Enable debug mode

P0 Enhancements:
  - SafetyGuardStack: Architectural separation of bias detection from QA
  - Tree-of-Thoughts Strategy: Multi-path strategic reasoning
  - LLM-Driven Prompting: Dynamic prompt engineering
  - Local Self-Correction: Bullet-level critique loops
        """
    )
    
    parser.add_argument(
        '-j', '--job-input',
        type=str,
        default=default_job_input,
        help=f'Path to job input JSON file (default: {default_job_input})'
    )
    
    parser.add_argument(
        '-m', '--master-resume',
        type=str,
        default=default_master_resume,
        help=f'Path to master resume JSON file (default: {default_master_resume})'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default=str(OUTPUT_DIR),
        help=f'Output directory for generated files (default: {OUTPUT_DIR})'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'V9.7 LangGraph Workflow (P0 Enhancements) - Version {__version__}'
    )
    
    args = parser.parse_args()
    
    # Configure Structured Logging
    setup_logging(args.debug)
    
    # --- v7.5: Setup Tracing ---
    setup_tracing()
    
    try:
        # --- v7.5: Setup Persistence ---
        redis_config = CONFIG.redis_config
        checkpointer = RedisSaver(
            host=redis_config.host,
            port=redis_config.port,
            db=redis_config.db
        )
        logger.info(f"✅ Connected to Redis checkpointer at {redis_config.host}:{redis_config.port}")
        
        # --- v7.5: Get Compiled Graph (HIL DISABLED for v9.7 batch focus) ---
        app = get_graph_app(
            checkpointer=checkpointer, 
            enable_hil=False
        )
        
        # Load real data
        job_input = load_job_input(args.job_input)
        master_resume = load_job_input(args.master_resume)
        
        # --- v9.5: Sanitize PII (Item #1) ---
        sanitizer = PIISanitizerAgent()
        sanitized_resume = sanitizer.run(master_resume)
        # -------------------------------------
        
        start_time = datetime.now()
        workflow_id = str(uuid.uuid4())
        
        run_config = {"configurable": {"thread_id": workflow_id}}
        
        # Define the initial state for the graph (v9.7 with P0 fields)
        inputs = {
            "master_resume": sanitized_resume,
            "job_input": {
                "raw_jd": job_input['job_description'],
                "company": job_input['company_name'],
                "job_title": job_input['job_title']
            },
            "artifacts": {},
            "replan_count": 0,
            "workflow_id": workflow_id,
            "original_draft": "",
            "human_approved_draft": "",
            "preference_insight": None,
            "provenance_ledger": [],
            # P0 additions:
            "strategy_thoughts": [],
            "selected_strategy": None,
            "local_retry_count": 0,
            "bullet_critique_history": []
        }
        
        logger.info(f"🚀 Starting v9.7 (P0 Enhancements) Workflow. ID: {workflow_id}")
        
        # --- v7.5: Run the Graph ---
        current_state = app.invoke(inputs, config=run_config)
        
        # --- v7.5: Save Artifacts ---
        if args.output_dir:
            output_path = Path(args.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            safe_company = re.sub(r'[^a-zA-Z0-9_-]', '_', job_input['company_name'])
            safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', job_input['job_title'])
            base_filename = f"{safe_company}_{safe_title}"
            
            # Save final draft
            final_draft = current_state.get('artifacts', {}).get('final_draft', "")
            if final_draft:
                draft_file = output_path / f"{base_filename}_final_draft_v9.7.txt"
                with open(draft_file, 'w') as f:
                    f.write(str(final_draft))
                logger.info(f"Saved final draft to: {draft_file}")
        
        # Print summary
        print_summary(current_state, workflow_id, start_time)
        
        if current_state.get('artifacts', {}).get('validation_results', {}).get('overall_passed'):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Workflow interrupted by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"❌ Fatal error in main execution: {e}", exc_info=args.debug)
        sys.exit(1)

if __name__ == "__main__":
    main()
