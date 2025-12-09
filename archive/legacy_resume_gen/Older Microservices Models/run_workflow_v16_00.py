# File: run_workflow.py
# (This file executes the main workflow)

import json
import os
import sys
from datetime import datetime

# Import the main components from your stable script name
try:
    from resume_workflow import (
        WorkflowOrchestrator, 
        MASTER_RESUME_DATA, 
        CONFIG, 
        __version__
    )
except ImportError as e:
    print(f"Error: Could not import from resume_workflow.py")
    print(f"Details: {e}")
    print("Please ensure resume_workflow.py is in the same directory.")
    sys.exit(1)

# Define the input file name
INPUT_JSON_FILE = "job_input.json"

def main():
    """
    Reads the input JSON, runs the resume workflow, and prints the result.
    """
    print("=" * 80)
    print(f"--- Resume Workflow Launcher v{__version__} ---")
    
    # --- 1. Read and parse the input JSON ---
    try:
        with open(INPUT_JSON_FILE, 'r', encoding='utf-8') as f:
            job_data = json.load(f)
    except FileNotFoundError:
        print(f"FATAL: Input file not found: {INPUT_JSON_FILE}")
        print("Please create it using the template.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"FATAL: Error parsing {INPUT_JSON_FILE}: {e}")
        print("Please ensure the JSON is valid (e.g., check for trailing commas).")
        sys.exit(1)
    
    # --- 2. Extract data and validate keys (UPDATED) ---
    try:
        # Join the array of strings into a single string with newlines
        manual_job_description = "\n".join(job_data['job_description'])
        manual_company_name = job_data['company_name']
        manual_job_title = job_data['job_title']
        manual_jd_url = job_data.get('jd_url', "") # Optional
        
        if not manual_job_description.strip():
            raise KeyError("job_description array is empty or missing")
            
    except KeyError as e:
        print(f"FATAL: Input JSON is missing a required key or is empty: {e}")
        sys.exit(1)
    except TypeError as e:
        print(f"FATAL: Error in input JSON. Is 'job_description' an array of strings? Error: {e}")
        sys.exit(1)

    print(f"Loaded Job: {manual_company_name} - {manual_job_title}")
    
    # --- 3. Initialize and run the workflow ---
    try:
        # Initialize the Orchestrator
        # Set test_mode=False to create real log files
        orchestrator = WorkflowOrchestrator(
            master_resume=MASTER_RESUME_DATA,
            config=CONFIG,
            test_mode=False
        )

        # Execute the workflow by passing the data from the JSON
        result = orchestrator.execute_workflow(
            job_description=manual_job_description,
            company_name=manual_company_name,
            job_title=manual_job_title,
            jd_url=manual_jd_url
        )

        # --- 4. Print the final result ---
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