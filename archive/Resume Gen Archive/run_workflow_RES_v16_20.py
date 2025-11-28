# File: run_workflow.py
# Version: 16.21 (Data-Driven)
# This file executes the main workflow by loading job_input.json

import json
import os
import sys
from datetime import datetime

# Import the main components from the refactored modules
try:
    # Import from the new refactored modules
    from workflow_RES import (
        WorkflowOrchestrator, 
        MASTER_RESUME_DATA, 
        __version__
    )
    from config_RES import CONFIG
except ImportError as e:
    print(f"Error: Could not import from refactored modules (workflow.py, config.py)")
    print(f"Details: {e}")
    print("Please ensure workflow.py, config.py, and all other modules are in the same directory.")
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

def main():
    """
    Runs the resume workflow using data from job_input.json.
    """
    print("=" * 80)
    print(f"--- Resume Workflow Launcher v{__version__} (Data-Driven Mode) ---")
    print("=" * 80)
    print()
    
    # --- 1. LOAD JOB DETAILS FROM JSON ---
    JOB_INPUT_FILE = "job_input.json"
    print(f"Loading job details from {JOB_INPUT_FILE}...")
    job_data = load_job_input(JOB_INPUT_FILE)
    
    company_name = job_data.get("company_name", "").strip()
    job_title = job_data.get("job_title", "").strip()
    jd_url = job_data.get("jd_url", "").strip()
    job_description = job_data.get("job_description", "").strip()

    # --- Validation ---
    if not job_description:
        print("=" * 80)
        print(f"⚠️  ERROR: 'job_description' in {JOB_INPUT_FILE} is empty.")
        print(f"Please paste the job description into {JOB_INPUT_FILE} and retry.")
        print("=" * 80)
        sys.exit(1)
        
    if not company_name or not job_title:
        print("=" * 80)
        print(f"⚠️  ERROR: 'company_name' or 'job_title' in {JOB_INPUT_FILE} is empty.")
        print(f"Please set these variables in {JOB_INPUT_FILE} and retry.")
        print("=" * 80)
        sys.exit(1)

    print("Workflow Inputs:")
    print(f"  Company: {company_name}")
    print(f"  Title: {job_title}")
    print(f"  URL: {jd_url if jd_url else 'Not provided'}")
    print(f"  Job Description: {len(job_description)} characters")
    
    print()
    print("=" * 80)
    print("Starting workflow...")
    print("=" * 80)
    print()
    
    # --- 2. Initialize and run the workflow ---
    try:
        # Initialize the Orchestrator
        # Set test_mode=False to create real log files
        orchestrator = WorkflowOrchestrator(
            master_resume=MASTER_RESUME_DATA,
            config=CONFIG,
            test_mode=False
        )

        # Execute the workflow by passing the data from the loaded JSON
        result = orchestrator.execute_workflow(
            job_description=job_description,
            company_name=company_name,
            job_title=job_title,
            jd_url=jd_url
        )

        # --- 3. Print the final result ---
        print("\n" + "=" * 80)
        print("--- Workflow Complete ---")
        print(f"Status: {result.get('status')}")
        print(f"Gate Decision: {result.get('gate_decision')}")
        
        if result.get('status') == "SUCCESS":
            print(f"Files Generated: {list(result.get('file_paths', {}).keys())}")
        else:
            print(f"Reason: {result.get('reason')}")
            
        print(f"Detailed Log File: {result.get('log_file_path')}")
        print("=" * 80)

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"--- WORKFLOW FAILED (UNCAUGHT EXCEPTION) ---")
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 80)

if __name__ == "__main__":
    main()