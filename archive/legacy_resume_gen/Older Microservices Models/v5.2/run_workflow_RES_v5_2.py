# File: run_workflow_RES_v5_2.py
# Version: 5.2.0 - Recovery System Launcher
# Smart launcher for v5.2 workflow with v3.8 logic integration

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, Any, Optional

# Configure logging for the launcher
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Version info
__version__ = "5.2.0-recovery"

# Import the main components from v5.2 modules
try:
    from workflow_RES_v5_2 import WorkflowV52
    from config_RES import CONFIG, OUTPUT_DIR, DATA_DIR
    logger.info(f"✅ Successfully imported v5.2 modules (version: {__version__})")
except ImportError as e:
    logger.critical(f"Error: Could not import v5.2 modules")
    logger.critical(f"Details: {e}")
    logger.critical("Please ensure all required v5.2 files are in the same directory:")
    logger.critical("  - workflow_RES_v5_2.py")
    logger.critical("  - advisory_crew_v5_2.py")
    logger.critical("  - execution_specialists_v5_2.py")
    logger.critical("  - validation_rules.py, validation_context.py, validation_engine.py")
    logger.critical("  - models_RES.py, config_RES.py, utils_RES.py")
    sys.exit(1)


def load_job_input(filename: str) -> Dict[str, Any]:
    """Loads the job input JSON file with error handling."""
    if not os.path.exists(filename):
        logger.critical("=" * 80)
        logger.critical(f"⚠️ FATAL ERROR: {filename} not found.")
        logger.critical(f"Please create a '{filename}' file in this directory.")
        logger.critical("Example format:")
        logger.critical(json.dumps({
            "company_name": "TechCorp",
            "job_title": "Senior Software Engineer",
            "job_description": "Full job description text...",
            "jd_url": "https://example.com/job"
        }, indent=2))
        logger.critical("=" * 80)
        sys.exit(1)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required fields
        required_fields = ['company_name', 'job_title', 'job_description']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.critical(f"⚠️ ERROR: Missing required fields in {filename}: {missing_fields}")
            sys.exit(1)
        
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


def load_master_resume(filename: str = "master_resume.json") -> Dict[str, Any]:
    """Loads the master resume JSON file."""
    master_path = Path(filename)
    
    # Check current directory first
    if not master_path.exists():
        # Check data directory
        master_path = Path(DATA_DIR) / filename
    
    # Check v3_8 directory
    if not master_path.exists():
        master_path = Path("/home/claude/v3_8") / filename
    
    if not master_path.exists():
        logger.warning(f"Master resume not found at {filename}, using empty template")
        return {
            "personal_info": {
                "name": "[Your Name]",
                "email": "[your.email@example.com]",
                "phone": "[Your Phone]",
                "location": "[City, State]"
            },
            "professional_summary": "",
            "experience": [],
            "skills": [],
            "education": [],
            "certifications": []
        }
    
    try:
        with open(master_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load master resume: {e}")
        return {}


def run_workflow(
    job_input: Dict[str, Any],
    master_resume: Dict[str, Any],
    output_dir: Optional[str] = None,
    config_overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run the v5.2 workflow for a single job application.
    
    Args:
        job_input: Job input dictionary with company_name, job_title, job_description
        master_resume: Master resume data
        output_dir: Directory to save output files
        config_overrides: Optional configuration overrides
        
    Returns:
        Workflow results dictionary
    """
    logger.info("=" * 80)
    logger.info(f"🚀 Starting V5.2 Recovery Workflow (Version: {__version__})")
    logger.info("=" * 80)
    
    # Initialize workflow
    workflow = WorkflowV52(config_path=None)
    
    # Apply config overrides if provided
    if config_overrides:
        workflow.config_overrides = config_overrides
    
    # Run workflow
    results = workflow.run(
        job_description=job_input['job_description'],
        company_name=job_input['company_name'],
        job_title=job_input['job_title'],
        master_resume_path=None,  # We'll pass the loaded master_resume directly
        output_dir=output_dir or str(OUTPUT_DIR)
    )
    
    # Override to use passed master_resume
    workflow.orchestrator.crew.master_resume = master_resume
    
    return results


def print_summary(results: Dict[str, Any]):
    """Print a summary of the workflow results."""
    print("\n" + "=" * 80)
    print("WORKFLOW SUMMARY - V5.2 Recovery System")
    print("=" * 80)
    
    status = results.get('overall_status', 'UNKNOWN')
    status_emoji = "✅" if status == "SUCCESS" else ("⚠️" if status == "PARTIAL" else "❌")
    print(f"{status_emoji} Overall Status: {status}")
    
    if 'workflow_results' in results:
        workflow = results['workflow_results']
        phases = workflow.get('phases', {})
        
        print("\nPhase Results:")
        for phase_name, phase_data in phases.items():
            phase_status = phase_data.get('status', 'UNKNOWN')
            phase_emoji = "✅" if phase_status == "COMPLETED" else "❌"
            print(f"  {phase_emoji} {phase_name.upper()}: {phase_status}")
            
            # Show phase-specific details
            if phase_name == 'rag' and 'signal_quality' in phase_data:
                print(f"     Signal Quality: {phase_data['signal_quality']:.1%}")
            elif phase_name == 'validation' and 'pass_rate' in phase_data:
                print(f"     Pass Rate: {phase_data['pass_rate']:.1%}")
                print(f"     Production Ready: {phase_data.get('production_ready', False)}")
            elif phase_name == 'assembly' and 'total_artifacts' in phase_data:
                print(f"     Artifacts Created: {phase_data['total_artifacts']}")
            elif phase_name == 'audit' and 'overall_status' in phase_data:
                print(f"     QA Status: {phase_data['overall_status']}")
    
    if 'artifacts' in results:
        print(f"\n📁 Artifacts Generated: {len(results['artifacts'])}")
        for artifact_name in results['artifacts'].keys():
            print(f"  - {artifact_name}")
    
    if 'execution_metadata' in results:
        metadata = results['execution_metadata']
        exec_time = metadata.get('execution_time_seconds', 0)
        print(f"\n⏱️ Execution Time: {exec_time:.2f} seconds")
        print(f"📅 Timestamp: {metadata.get('start_time', 'N/A')}")
        print(f"🔧 Version: {metadata.get('version', __version__)}")
    
    print("=" * 80)


def main():
    """
    Main entry point for V5.2 Recovery Workflow Launcher.
    """
    script_path = os.path.relpath(__file__) if "__file__" in globals() else "run_workflow_RES_v5_2.py"
    
    parser = argparse.ArgumentParser(
        description=f'V5.2 Recovery System - Resume Workflow Engine (Version: {__version__})',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python {script_path}                           # Run with default job_input.json
  python {script_path} -j custom_job.json        # Use custom job input file
  python {script_path} -m custom_master.json     # Use custom master resume
  python {script_path} -o /path/to/output        # Specify output directory
  python {script_path} --debug                   # Enable debug mode
  python {script_path} --test                    # Run with test data
  
Required Files:
  - job_input.json (or specified with -j)
  - master_resume.json (or specified with -m)
  - All v5.2 module files (11 required files)
  
V5.2 Recovery Features:
  - ChromaDB persistent memory (Library_Specialist)
  - Circuit breaker protection (Web_Specialist)
  - 4-phase RAG analysis (RAG_Synthesizer)
  - 25+ validation rules from v3.8
  - Deterministic rendering logic
  - Comprehensive QA auditing
        """
    )
    
    parser.add_argument(
        '-j', '--job-input',
        type=str,
        default='job_input.json',
        help='Path to job input JSON file (default: job_input.json)'
    )
    
    parser.add_argument(
        '-m', '--master-resume',
        type=str,
        default='master_resume.json',
        help='Path to master resume JSON file (default: master_resume.json)'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default=None,
        help='Output directory for generated files (default: workflow_outputs/)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with verbose logging'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run with test data (no files required)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'V5.2 Recovery System - Version {__version__}'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    try:
        if args.test:
            # Use test data
            logger.info("🧪 Running in TEST mode with sample data")
            job_input = {
                'company_name': 'TechCorp',
                'job_title': 'Senior Software Engineer',
                'job_description': """
                We are looking for a Senior Software Engineer with expertise in:
                - Python and Java programming
                - AWS cloud services
                - Docker and Kubernetes
                - Machine Learning and AI
                - Agile development methodologies
                
                Responsibilities:
                - Lead technical initiatives
                - Design system architecture
                - Mentor junior developers
                - Collaborate with cross-functional teams
                
                Requirements:
                - 5+ years of software development experience
                - Strong problem-solving skills
                - Excellent communication abilities
                """,
                'jd_url': 'https://example.com/job/12345'
            }
            master_resume = {
                "personal_info": {
                    "name": "Test User",
                    "email": "test@example.com",
                    "phone": "555-1234",
                    "location": "San Francisco, CA"
                },
                "professional_summary": "Experienced software engineer with 10+ years in tech.",
                "experience": [],
                "skills": ["Python", "Java", "AWS", "Docker", "Kubernetes"],
                "education": [],
                "certifications": []
            }
        else:
            # Load real data
            job_input = load_job_input(args.job_input)
            master_resume = load_master_resume(args.master_resume)
        
        # Prepare config overrides
        config_overrides = {
            'debug': args.debug,
            'version': __version__
        }
        
        # Run workflow
        results = run_workflow(
            job_input=job_input,
            master_resume=master_resume,
            output_dir=args.output_dir,
            config_overrides=config_overrides
        )
        
        # Print summary
        print_summary(results)
        
        # Exit based on results
        if results.get('overall_status') == 'SUCCESS':
            logger.info("✅ Workflow completed successfully!")
            sys.exit(0)
        elif results.get('overall_status') == 'PARTIAL':
            logger.warning("⚠️ Workflow completed with warnings")
            sys.exit(0)
        else:
            logger.error("❌ Workflow failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Workflow interrupted by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}", exc_info=args.debug)
        sys.exit(1)


if __name__ == "__main__":
    main()
