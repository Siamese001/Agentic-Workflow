# File: run_workflow_RES.py
# Version: 16.32 - Centralized Path Management
# Smart launcher with resume capability and argparse interface

import argparse
import json
import os
import sys
from datetime import datetime

# Import the main components from the refactored modules
try:
    from workflow_RES import (
        WorkflowOrchestrator, 
        MASTER_RESUME_DATA, 
        __version__
    )
    from config_RES import CONFIG, OUTPUT_DIR, DATA_DIR
except ImportError as e:
    print(f"Error: Could not import from refactored modules (workflow_RES.py, config_RES.py)")
    print(f"Details: {e}")
    print("Please ensure workflow_RES.py, config_RES.py, and all other modules are in the same directory.")
    sys.exit(1)


def load_job_input(filename: str) -> dict:
    """Loads the job input JSON file with error handling."""
    if not os.path.exists(filename):
        print("=" * 80)
        print(f"⚠️  FATAL ERROR: {filename} not found.")
        print(f"Please create a '{filename}' file in this directory.")
        print("=" * 80)
        sys.exit(1)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print("=" * 80)
        print(f"⚠️  FATAL ERROR: Failed to parse {filename}.")
        print(f"   Please check the JSON for errors (e.g., missing comma, extra comma).")
        print(f"   Details: {e}")
        print("=" * 80)
        sys.exit(1)
    except Exception as e:
        print("=" * 80)
        print(f"⚠️  FATAL ERROR: An unexpected error occurred loading {filename}: {e}")
        print("=" * 80)
        sys.exit(1)


def list_available_runs():
    """Lists all available run directories for resume."""
    # --- FIX: Use OUTPUT_DIR constant ---
    workflow_outputs_dir = str(OUTPUT_DIR)
    if not os.path.exists(workflow_outputs_dir):
        print("No workflow_outputs directory found. No runs available to resume.")
        return
    
    run_dirs = [d for d in os.listdir(workflow_outputs_dir) 
                if os.path.isdir(os.path.join(workflow_outputs_dir, d))]
    
    if not run_dirs:
        print("No runs found in workflow_outputs directory.")
        return
    
    print("\nAvailable runs:")
    print("-" * 80)
    for run_id in sorted(run_dirs):
        manifest_path = os.path.join(workflow_outputs_dir, run_id, "run_manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                company = manifest.get('job_input', {}).get('company_name', 'Unknown')
                title = manifest.get('job_input', {}).get('job_title', 'Unknown')
                start_time = manifest.get('start_time_utc', 'Unknown')
                print(f"  {run_id}: {company} - {title} (Started: {start_time})")
            except:
                print(f"  {run_id}: (manifest unreadable)")
        else:
            print(f"  {run_id}: (no manifest)")
    print("-" * 80)

def main():
    """
    Smart launcher for Resume Workflow Engine with resume capability.
    """
    # --- FIX: Get the script's own path for examples ---
    script_path = os.path.relpath(__file__) if "__file__" in globals() else "run_workflow_RES.py"
    
    parser = argparse.ArgumentParser(
        description=f"Resume Workflow Engine v{__version__} - Resumable Data-Driven Execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # --- FIX: Use DATA_DIR for example path ---
        epilog=f"""
Examples:
  # Start a new run (assuming job_input.json is in the data dir)
  python {script_path} --job-input "{DATA_DIR / 'job_input.json'}"
  
  # Resume an existing run
  python {script_path} --resume-id a6be50ce
  
  # Resume and start from a specific hop
  python {script_path} --resume-id a6be50ce --start-hop 3
  
  # Force rerun from a specific hop (deletes downstream cache)
  python {script_path} --resume-id a6be50ce --force-rerun-from-hop 3
  
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
    
    # Optional controls
    parser.add_argument(
        '--start-hop', 
        type=int, 
        default=0,
        metavar='N',
        help="Start execution at this hop number (e.g., 3). Default: 0."
    )
    parser.add_argument(
        '--force-rerun-from-hop', 
        type=int,
        metavar='N',
        help="Delete cached files and force re-execution from this hop onwards."
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
        print("=" * 80)
        print("Error: You must provide either --job-input or --resume-id.")
        print("=" * 80)
        parser.print_help()
        sys.exit(1)
    
    if args.resume_id and args.job_input:
        print("=" * 80)
        print("Error: Cannot specify both --resume-id and --job-input.")
        print("Use --resume-id to resume an existing run, or --job-input to start a new one.")
        print("=" * 80)
        sys.exit(1)
    
    print("=" * 80)
    print(f"--- Resume Workflow Engine v{__version__} ---")
    print("=" * 80)
    print()
    
    # --- 1. Validate Args and Initialize Orchestrator ---
    orchestrator = None
    try:
        if args.resume_id:
            print(f"Mode: RESUME")
            print(f"Attempting to resume workflow for run_id: {args.resume_id}")
            print()
            
            orchestrator = WorkflowOrchestrator(
                config=CONFIG,
                master_resume=MASTER_RESUME_DATA,
                run_id=args.resume_id
            )
            
            # Print resume context
            print(f"Run Directory: {orchestrator.run_path}")
            print(f"Job: {orchestrator.job_input.get('company_name')} - {orchestrator.job_input.get('job_title')}")
            print()
            
        elif args.job_input:
            print(f"Mode: NEW RUN")
            print(f"Starting new workflow from: {args.job_input}")
            print()
            
            job_input_data = load_job_input(args.job_input)
            
            # Validate job input
            company_name = job_input_data.get("company_name", "").strip()
            job_title = job_input_data.get("job_title", "").strip()
            job_description = job_input_data.get("job_description", "").strip()
            jd_url = job_input_data.get("jd_url", "").strip()
            
            if not job_description:
                print("=" * 80)
                print(f"⚠️  ERROR: 'job_description' in {args.job_input} is empty.")
                print(f"Please paste the job description into {args.job_input} and retry.")
                print("=" * 80)
                sys.exit(1)
                
            if not company_name or not job_title:
                print("=" * 80)
                print(f"⚠️  ERROR: 'company_name' or 'job_title' in {args.job_input} is empty.")
                print(f"Please set these variables in {args.job_input} and retry.")
                print("=" * 80)
                sys.exit(1)
            
            print("Workflow Inputs:")
            print(f"  Company: {company_name}")
            print(f"  Title: {job_title}")
            print(f"  URL: {jd_url if jd_url else 'Not provided'}")
            print(f"  Job Description: {len(job_description)} characters")
            print()
            
            orchestrator = WorkflowOrchestrator(
                config=CONFIG,
                master_resume=MASTER_RESUME_DATA,
                job_input=job_input_data
            )
            
            print(f"Created new run with ID: {orchestrator.run_id}")
            print(f"Run Directory: {orchestrator.run_path}")
            print()
            
    except FileNotFoundError as e:
        print("=" * 80)
        print(f"⚠️  ERROR: {e}")
        print("=" * 80)
        sys.exit(1)
    except ValueError as e:
        print("=" * 80)
        print(f"⚠️  ERROR: {e}")
        print("=" * 80)
        sys.exit(1)
    except Exception as e:
        print("=" * 80)
        print(f"⚠️  FATAL ERROR during initialization: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # --- 2. Execute the workflow ---
    print("=" * 80)
    print("Starting workflow execution...")
    if args.start_hop > 0:
        print(f"  Starting from HOP-{args.start_hop}")
    if args.force_rerun_from_hop is not None:
        print(f"  Force rerun from HOP-{args.force_rerun_from_hop} (will delete downstream cache)")
    print("=" * 80)
    print()
    
    try:
        workflow_start_time = datetime.now()
        
        result = orchestrator.execute_workflow(
            start_hop=args.start_hop,
            force_rerun_from_hop=args.force_rerun_from_hop
        )
        
        workflow_end_time = datetime.now()
        workflow_duration = (workflow_end_time - workflow_start_time).total_seconds()
        
        # --- 3. Print final summary ---
        print("\n" + "=" * 80)
        print("--- WORKFLOW COMPLETE ---")
        print("=" * 80)
        print(f"Status: {result.get('status')}")
        print(f"Run ID: {orchestrator.run_id}")
        print(f"Gate Decision: {result.get('gate_decision')}")
        print(f"Duration: {workflow_duration:.1f} seconds")
        print()
        
        if result.get('status') == "SUCCESS":
            print("Files Generated:")
            file_paths = result.get('file_paths', {})
            for file_type, file_path in file_paths.items():
                print(f"  - {file_type}: {file_path}")
            print()
        else:
            print(f"Termination Reason: {result.get('reason')}")
            print()
            
        print(f"Run Directory: {orchestrator.run_path}")
        print(f"Log File: {result.get('log_file_path')}")
        print("=" * 80)
        
        # Exit with appropriate code
        if result.get('status') == "SUCCESS":
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("--- WORKFLOW INTERRUPTED BY USER ---")
        print("=" * 80)
        print(f"Run ID: {orchestrator.run_id}")
        print(f"Run can be resumed with: python {script_path} --resume-id {orchestrator.run_id}")
        print("=" * 80)
        sys.exit(130)
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("--- WORKFLOW FAILED (UNCAUGHT EXCEPTION) ---")
        print("=" * 80)
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        if orchestrator:
            print(f"Run ID: {orchestrator.run_id}")
            print(f"Log File: {orchestrator.log_file_path if hasattr(orchestrator, 'log_file_path') else 'N/A'}")
            print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()