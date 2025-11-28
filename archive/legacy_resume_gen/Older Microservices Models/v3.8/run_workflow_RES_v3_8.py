# File: run_workflow_RES_v3_8.py
# Version: 3.8.0 - V3.8 Agentic Architecture with Async Governor
# Smart launcher with async execution support - Complete Migration

import argparse
import json
import os
import sys
import asyncio
from datetime import datetime
import logging

# Configure logging for the launcher
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the main components from the v3.8 modules
try:
    from workflow_RES_v3_8 import (
        WorkflowOrchestrator, 
        load_master_resume,
        __version__
    )
    from config_RES_v3_8 import CONFIG, OUTPUT_DIR, DATA_DIR
except ImportError as e:
    logger.critical(f"Error: Could not import from v3.8 modules (workflow_RES_v3_8.py, config_RES_v3_8.py)")
    logger.critical(f"Details: {e}")
    logger.critical("Please ensure workflow_RES_v3_8.py, config_RES_v3_8.py, and all other modules are in the same directory.")
    sys.exit(1)


def load_job_input(filename: str) -> dict:
    """Loads the job input JSON file with error handling."""
    if not os.path.exists(filename):
        logger.critical("=" * 80)
        logger.critical(f"⚠️ FATAL ERROR: {filename} not found.")
        logger.critical(f"Please create a '{filename}' file in this directory.")
        logger.critical("=" * 80)
        sys.exit(1)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        logger.critical("=" * 80)
        logger.critical(f"⚠️ FATAL ERROR: Failed to parse {filename}.")
        logger.critical(f"   Please check the JSON for errors (e.g., missing comma, extra comma).")
        logger.critical(f"   Details: {e}")
        logger.critical("=" * 80)
        sys.exit(1)
    except Exception as e:
        logger.critical("=" * 80)
        logger.critical(f"⚠️ FATAL ERROR: An unexpected error occurred loading {filename}: {e}")
        logger.critical("=" * 80)
        sys.exit(1)


def list_available_runs():
    """Lists all available run directories for resume."""
    workflow_outputs_dir = str(OUTPUT_DIR)
    if not os.path.exists(workflow_outputs_dir):
        logger.info("No workflow_outputs directory found. No runs available to resume.")
        return
    
    run_dirs = [d for d in os.listdir(workflow_outputs_dir) 
                if os.path.isdir(os.path.join(workflow_outputs_dir, d))]
    
    if not run_dirs:
        logger.info("No runs found in workflow_outputs directory.")
        return
    
    logger.info("\nAvailable runs:")
    logger.info("-" * 80)
    for run_id in sorted(run_dirs):
        manifest_path = os.path.join(workflow_outputs_dir, run_id, "run_manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                company = manifest.get('job_input', {}).get('company_name', 'Unknown')
                title = manifest.get('job_input', {}).get('job_title', 'Unknown')
                start_time = manifest.get('start_time_utc', 'Unknown')
                logger.info(f"  {run_id}: {company} - {title} (Started: {start_time})")
            except:
                logger.warning(f"  {run_id}: (manifest unreadable)")
        else:
            logger.warning(f"  {run_id}: (no manifest)")
    logger.info("-" * 80)


def main():
    """
    V3.8 Launcher for Resume Workflow Engine with async execution.
    """
    script_path = os.path.relpath(__file__) if "__file__" in globals() else "run_workflow_RES_v3_8.py"
    
    parser = argparse.ArgumentParser(
        description=f"Resume Workflow Engine v{__version__} - V3.8 Agentic Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Start a new run (assuming job_input.json is in the data dir)
  python {script_path} --job-input "{DATA_DIR / 'job_input.json'}"
  
  # Resume an existing run
  python {script_path} --resume-id a6be50ce
  
  # List available runs
  python {script_path} --list-runs
        """
    )
    
    # Group for starting a new run
    new_run_group = parser.add_argument_group('New Run')
    new_run_group.add_argument(
        '--job-input', 
        type=str,
        metavar='PATH',
        help="Path to job_input.json file to start a new run."
    )
    
    # Group for resuming an existing run
    resume_run_group = parser.add_argument_group('Resume Run')
    resume_run_group.add_argument(
        '--resume-id', 
        type=str,
        metavar='RUN_ID',
        help="A specific run_id (e.g., a6be50ce) to resume."
    )
    
    # Utility
    parser.add_argument(
        '--list-runs',
        action='store_true',
        help="List all available runs that can be resumed."
    )

    args = parser.parse_args()
    
    # Handle list-runs
    if args.list_runs:
        list_available_runs()
        sys.exit(0)
    
    # Validate that either --resume-id or --job-input is provided
    if not args.resume_id and not args.job_input:
        logger.error("=" * 80)
        logger.error("Error: You must provide either --job-input or --resume-id.")
        logger.error("=" * 80)
        parser.print_help()
        sys.exit(1)
    
    if args.resume_id and args.job_input:
        logger.error("=" * 80)
        logger.error("Error: Cannot specify both --resume-id and --job-input.")
        logger.error("Use --resume-id to resume an existing run, or --job-input to start a new one.")
        logger.error("=" * 80)
        sys.exit(1)
    
    logger.info("=" * 80)
    logger.info(f"--- Resume Workflow Engine v{__version__} (V3.8 Architecture) ---")
    logger.info("=" * 80)
    
    # Load master resume data
    logger.info("Loading master resume data...")
    try:
        master_resume_data = load_master_resume()
        logger.info("✔ Master resume loaded successfully")
    except Exception as e:
        logger.critical(f"✗ Failed to load master resume: {e}")
        sys.exit(1)
    
    # Validate Args and Initialize Orchestrator
    orchestrator = None
    try:
        if args.resume_id:
            logger.info(f"Mode: RESUME")
            logger.info(f"Attempting to resume workflow for run_id: {args.resume_id}")
            
            orchestrator = WorkflowOrchestrator(
                config=CONFIG,
                master_resume=master_resume_data,
                run_id=args.resume_id
            )
            
            # Print resume context
            logger.info(f"Run Directory: {orchestrator.run_path}")
            logger.info(f"Job: {orchestrator.job_input.get('company_name')} - {orchestrator.job_input.get('job_title')}")
            
        elif args.job_input:
            logger.info(f"Mode: NEW RUN")
            logger.info(f"Starting new workflow from: {args.job_input}")
            print()
            
            job_input_data = load_job_input(args.job_input)
            
            # Validate job input
            company_name = job_input_data.get("company_name", "").strip()
            job_title = job_input_data.get("job_title", "").strip()
            job_description = job_input_data.get("job_description", "").strip()
            jd_url = job_input_data.get("jd_url", "").strip()
            
            if not job_description:
                logger.info("=" * 80)
                logger.error(f"⚠️ ERROR: 'job_description' in {args.job_input} is empty.")
                logger.info(f"Please paste the job description into {args.job_input} and retry.")
                logger.info("=" * 80)
                sys.exit(1)
                
            if not company_name or not job_title:
                logger.info("=" * 80)
                logger.error(f"⚠️ ERROR: 'company_name' or 'job_title' in {args.job_input} is empty.")
                logger.info(f"Please set these variables in {args.job_input} and retry.")
                logger.info("=" * 80)
                sys.exit(1)
            
            logger.info("Workflow Inputs:")
            logger.info(f"  Company: {company_name}")
            logger.info(f"  Title: {job_title}")
            logger.info(f"  URL: {jd_url if jd_url else 'Not provided'}")
            logger.info(f"  Job Description: {len(job_description)} characters")
            print()
            
            orchestrator = WorkflowOrchestrator(
                config=CONFIG,
                master_resume=master_resume_data,
                job_input=job_input_data
            )
            
            logger.info(f"Created new run with ID: {orchestrator.run_id}")
            logger.info(f"Run Directory: {orchestrator.run_path}")
            print()
            
    except FileNotFoundError as e:
        logger.info("=" * 80)
        logger.error(f"⚠️ ERROR: {e}")
        logger.info("=" * 80)
        sys.exit(1)
    except ValueError as e:
        logger.info("=" * 80)
        logger.error(f"⚠️ ERROR: {e}")
        logger.info("=" * 80)
        sys.exit(1)
    except Exception as e:
        logger.info("=" * 80)
        logger.critical(f"⚠️ FATAL ERROR during initialization: {e}")
        logger.info("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Execute the workflow with async support
    logger.info("=" * 80)
    logger.info("Starting V3.8 async workflow execution...")
    logger.info("=" * 80)
    print()
    
    try:
        workflow_start_time = datetime.now()
        
        # Use asyncio.run for async execution
        result = asyncio.run(orchestrator.execute())
        
        workflow_end_time = datetime.now()
        workflow_duration = (workflow_end_time - workflow_start_time).total_seconds()
        
        # Print final summary
        logger.info("\n" + "=" * 80)
        logger.info("--- WORKFLOW COMPLETE ---")
        logger.info("=" * 80)
        logger.info(f"Status: {result.get('status')}")
        logger.info(f"Run ID: {orchestrator.run_id}")
        logger.info(f"Gate Decision: {result.get('gate_decision')}")
        logger.info(f"Duration: {workflow_duration:.1f} seconds")
        print()
        
        if result.get('status') == "SUCCESS":
            logger.info("Files Generated:")
            file_paths = result.get('file_paths', [])
            if isinstance(file_paths, dict):
                for file_type, file_path in file_paths.items():
                    logger.info(f"  - {file_type}: {file_path}")
            elif isinstance(file_paths, list):
                for file_path in file_paths:
                    logger.info(f"  - {file_path}")
            print()
        else:
            logger.info(f"Termination Reason: {result.get('reason')}")
            print()
            
        logger.info(f"Run Directory: {orchestrator.run_path}")
        logger.info(f"Log File: {result.get('log_file_path')}")
        logger.info("=" * 80)
        
        # Exit with appropriate code
        if result.get('status') == "SUCCESS":
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n" + "=" * 80)
        logger.info("--- WORKFLOW INTERRUPTED BY USER ---")
        logger.info("=" * 80)
        logger.info(f"Run ID: {orchestrator.run_id}")
        logger.info(f"Run can be resumed with: python {script_path} --resume-id {orchestrator.run_id}")
        logger.info("=" * 80)
        sys.exit(130)
        
    except Exception as e:
        logger.info("\n" + "=" * 80)
        logger.info("--- WORKFLOW FAILED (UNCAUGHT EXCEPTION) ---")
        logger.info("=" * 80)
        logger.info(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        logger.info("=" * 80)
        if orchestrator:
            logger.info(f"Run ID: {orchestrator.run_id}")
            logger.info(f"Log File: {orchestrator.log_file_path if hasattr(orchestrator, 'log_file_path') else 'N/A'}")
            logger.info("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
