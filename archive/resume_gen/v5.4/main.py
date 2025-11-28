# File: main.py
# Zero-Loss Consolidation - Execution Entry Point
# Merges: workflow_RES_v5_2.py → run_workflow_RES_v5_2.py
# Version: Consolidated 5.4

# ============================================================================
# EXTERNAL IMPORTS (Consolidated)
# ============================================================================
import argparse
import json
import logging
import logging.handlers
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import from consolidated modules
from core import (
    # Config
    CONFIG, DATA_DIR, OUTPUT_DIR, CACHE_DIR,
    # Models
    ImmutableStagingBuffer, ThematicAnalysis, ValidationResult,
    HopResult, ValidationSeverity, ResumeSection
)

from validation_stack import (
    ValidationContext, PreFlightValidator, calculate_signal_score
)

from agent_swarm import (
    CrewOrchestrator, CrewConfiguration, Governor,
    GeminiService, get_gemini_service
)

# --- PRIORITY #2: Structured, Centralized Logging ---
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
        return json.dumps(log_record)

logger = logging.getLogger(__name__)

# Version info
__version__ = "5.4.0-consolidated"

# ============================================================================
# PART 1: WORKFLOW CLASS (from workflow_RES_v5_2.py)
# ============================================================================

class WorkflowV52:
    """
    Main workflow class for v5.4 recovery system.
    Integrates v3.8 deterministic logic with v5.1 agent architecture.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize workflow with configuration."""
        self.logger = logging.getLogger(__name__)
        
        # Load configuration overrides if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config_overrides = json.load(f)
        else:
            self.config_overrides = {}
        
        # Initialize crew orchestrator
        crew_config = CrewConfiguration(
            max_complexity=self.config_overrides.get('max_complexity', 100),
            parallel_execution=self.config_overrides.get('parallel', False),
            validation_threshold=self.config_overrides.get('validation_threshold', 0.8),
            enable_caching=self.config_overrides.get('enable_caching', True),
            debug_mode=self.config_overrides.get('debug', False)
        )
        
        self.orchestrator = CrewOrchestrator(config=crew_config)
        
        self.logger.info(f"Workflow v5.4 initialized with recovery system (version: {__version__})")
    
    def run(
        self,
        job_description: str,
        company_name: str,
        job_title: str,
        master_resume_path: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the complete workflow for a single job application.
        
        Args:
            job_description: Full job description text
            company_name: Target company name
            job_title: Target job title
            master_resume_path: Path to master resume JSON file
            output_dir: Directory to save output files
            
        Returns:
            Dictionary containing workflow results and artifacts
        """
        self.logger.info("=" * 80)
        self.logger.info(f"Starting Workflow v5.4 for {company_name} - {job_title}")
        self.logger.info("=" * 80)
        
        start_time = datetime.now()
        
        # --- PRIORITY #1: Correlation ID ---
        workflow_id = str(uuid.uuid4())
        
        try:
            # Load master resume
            master_resume = self._load_master_resume(master_resume_path)
            
            # Process job application through crew
            results = self.orchestrator.process_job_application(
                job_description=job_description,
                company_name=company_name,
                job_title=job_title,
                master_resume=master_resume,
                workflow_id=workflow_id  # Pass ID to orchestrator
            )
            
            # Save artifacts if output directory provided
            if output_dir:
                self._save_artifacts(results, output_dir, company_name, job_title)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Add execution metadata
            results['execution_metadata'] = {
                'start_time': start_time.isoformat(),
                'execution_time_seconds': execution_time,
                'version': __version__,
                'config_overrides': self.config_overrides,
                'workflow_id': workflow_id # Add ID to final output
            }
            
            # Determine overall status
            workflow_status = results.get('workflow_results', {})
            if workflow_status.get('status') == 'COMPLETED':
                self.logger.info("✅ Workflow completed successfully")
                results['overall_status'] = 'SUCCESS'
            elif workflow_status.get('status') == 'FAILED' and 'validation' in results:
                self.logger.warning("⚠️ Workflow completed with validation issues")
                results['overall_status'] = 'PARTIAL'
            else:
                self.logger.error("❌ Workflow failed")
                results['overall_status'] = 'FAILED'
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Workflow failed: {e}", exc_info=True)
            
            return {
                'overall_status': 'FAILED',
                'error': str(e),
                'execution_metadata': {
                    'start_time': start_time.isoformat(),
                    'execution_time_seconds': (datetime.now() - start_time).total_seconds(),
                    'version': __version__
                }
            }
        
        finally:
            self.logger.info("=" * 80)
            self.logger.info("Workflow v5.4 execution completed")
            self.logger.info("=" * 80)
    
    def _load_master_resume(self, master_resume_path: Optional[str] = None) -> Dict[str, Any]:
        """Load master resume from file or use default."""
        # Try provided path first
        if master_resume_path and os.path.exists(master_resume_path):
            self.logger.info(f"Loading master resume from: {master_resume_path}")
            with open(master_resume_path, 'r') as f:
                return json.load(f)
        
        # Try default paths
        default_paths = [
            Path("master_resume.json"),
            DATA_DIR / "master_resume.json",
            Path("/home/claude/v3_8/master_resume.json")
        ]
        
        for path in default_paths:
            if path.exists():
                self.logger.info(f"Loading master resume from default: {path}")
                with open(path, 'r') as f:
                    return json.load(f)
        
        # Return empty template if no master resume found
        self.logger.warning("No master resume found, using empty template")
        return self._create_empty_master_resume()
    
    def _create_empty_master_resume(self) -> Dict[str, Any]:
        """Create an empty master resume template."""
        return {
            "owner": {
                "name": "[Your Name]",
                "contact": {
                    "email": "[your.email@example.com]",
                    "phone": "[Your Phone]",
                    "linkedin": "[Your LinkedIn]"
                }
            },
            "professional_experience": [],
            "skills": [],
            "education": [],
            "certifications": [],
            "strategic_and_technical_competencies": []
        }
    
    def _save_artifacts(
        self,
        results: Dict[str, Any],
        output_dir: str,
        company_name: str,
        job_title: str
    ) -> None:
        """Save workflow artifacts to files."""
        self.logger.info(f"Saving artifacts to: {output_dir}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate base filename from company and job title
        safe_company = re.sub(r'[^\w\s-]', '', company_name.lower()).strip().replace(' ', '_')
        safe_title = re.sub(r'[^\w\s-]', '', job_title.lower()).strip().replace(' ', '_')
        base_filename = f"{safe_company}_{safe_title}"
        
        # Save complete results as JSON
        results_path = Path(output_dir) / f"{base_filename}_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        self.logger.info(f"Saved complete results to: {results_path}")
        
        # Save individual artifacts if present
        if 'artifacts' in results:
            for artifact_name, artifact_data in results['artifacts'].items():
                if isinstance(artifact_data, str):
                    # Save text artifact
                    artifact_path = Path(output_dir) / f"{base_filename}_{artifact_name}.txt"
                    with open(artifact_path, 'w') as f:
                        f.write(artifact_data)
                    self.logger.info(f"Saved artifact: {artifact_path}")
                elif isinstance(artifact_data, dict):
                    # Save JSON artifact
                    artifact_path = Path(output_dir) / f"{base_filename}_{artifact_name}.json"
                    with open(artifact_path, 'w') as f:
                        json.dump(artifact_data, f, indent=2, default=str)
                    self.logger.info(f"Saved artifact: {artifact_path}")

# ============================================================================
# PART 2: RUNNER FUNCTIONS (from run_workflow_RES_v5_2.py)
# ============================================================================

def load_job_input(file_path: str) -> Dict[str, Any]:
    """Load job input from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Job input file not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in job input file: {e}")
        raise

def load_master_resume(file_path: str) -> Dict[str, Any]:
    """Load master resume from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Master resume file not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in master resume file: {e}")
        raise

def print_summary(results: Dict[str, Any]) -> None:
    """Print a comprehensive summary of workflow results."""
    print("\n" + "=" * 80)
    print("WORKFLOW EXECUTION SUMMARY")
    print("=" * 80)
    
    # Overall status
    status = results.get('overall_status', 'UNKNOWN')
    status_icon = {
        'SUCCESS': '✅',
        'PARTIAL': '⚠️',
        'FAILED': '❌',
        'UNKNOWN': '❓'
    }.get(status, '❓')
    
    print(f"\n{status_icon} Overall Status: {status}")
    
    # Error information if present
    if 'error' in results:
        print(f"\n❌ Error: {results['error']}")
    
    # Workflow results
    if 'workflow_results' in results:
        workflow = results['workflow_results']
        print(f"\n📋 Workflow Status: {workflow.get('status', 'N/A')}")
        
        # Phase results
        if 'phases' in workflow:
            print("\n🔄 Phase Results:")
            for phase_name, phase_data in workflow['phases'].items():
                print(f"\n  {phase_name.upper()}:")
                if phase_name == 'validation' and isinstance(phase_data, dict):
                    print(f"     Total Checks: {phase_data.get('total_checks', 0)}")
                    print(f"     Pass Rate: {phase_data['pass_rate']:.1%}")
                    print(f"     Production Ready: {phase_data.get('production_ready', False)}")
                elif phase_name == 'assembly' and 'artifacts' in phase_data:
                    print(f"     Artifacts Created: {len(phase_data['artifacts'])}")
                elif phase_name == 'audit' and 'signal_score' in phase_data:
                    print(f"     Signal Score: {phase_data['signal_score']:.1%}")
                    print(f"     QA Status: {'PASSED' if phase_data.get('passed') else 'FAILED'}")
    
    if 'artifacts' in results:
        print(f"\n📄 Artifacts Generated: {len(results['artifacts'])}")
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
    Main entry point for V5.4 Consolidated Workflow.
    """
    script_path = os.path.relpath(__file__) if "__file__" in globals() else "main.py"
    
    parser = argparse.ArgumentParser(
        description=f'V5.4 Consolidated System - Resume Workflow Engine (Version: {__version__})',
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
  
Consolidated Features:
  - ChromaDB persistent memory (Library_Specialist)
  - Circuit breaker protection (Web_Specialist)
  - 4-phase RAG analysis (RAG_Synthesizer)
  - 25+ validation rules from v3.8 (PreFlightValidator)
  - Dynamic template mapping (Governor)
  - HIL escalation with json.dump persistence
  - Comprehensive QA auditing
  
This is the consolidated 4-file version merging:
  - core.py: models + config + utils + prompts
  - validation_stack.py: all validation modules
  - agent_swarm.py: gemini service + all specialists + crew
  - main.py: workflow orchestration + runner
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
        default=str(OUTPUT_DIR),
        help=f'Output directory for generated files (default: {OUTPUT_DIR})'
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
        '--config',
        type=str,
        default=None,
        help='Path to configuration override JSON file'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'V5.4 Consolidated System - Version {__version__}'
    )
    
    args = parser.parse_args()
    
    # --- PRIORITY #2: Configure Structured Logging ---
    root_logger = logging.getLogger()
    if args.debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)

    # Remove default handler
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add File Handler (JSON)
    file_handler = logging.handlers.RotatingFileHandler("workflow.log.jsonl", maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(JsonFormatter())
    root_logger.addHandler(file_handler)

    # Add Console Handler (Human-readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(console_handler)
    
    if args.debug:
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
                - Bachelor's degree in Computer Science or related field
                """,
                'jd_url': 'https://example.com/job/12345'
            }
            master_resume = {
                "owner": {
                    "name": "Test User",
                    "contact": {
                        "email": "test@example.com",
                        "phone": "555-1234",
                        "linkedin": "https://linkedin.com/in/testuser"
                    }
                },
                "professional_experience": [
                    {
                        "company": "Previous Corp",
                        "title": "Software Engineer",
                        "dates": {"start": "2018", "end": "2023"},
                        "bullet_pool": [
                            "Developed microservices using Python and Java",
                            "Deployed applications on AWS using Docker and Kubernetes",
                            "Led team of 5 engineers on critical projects"
                        ]
                    }
                ],
                "skills": ["Python", "Java", "AWS", "Docker", "Kubernetes", "Machine Learning"],
                "education": [
                    {
                        "degree": "Bachelor of Science in Computer Science",
                        "institution": "Tech University",
                        "year": "2018"
                    }
                ],
                "certifications": ["AWS Solutions Architect", "Certified Kubernetes Administrator"]
            }
        else:
            # Load real data
            job_input = load_job_input(args.job_input)
            master_resume = load_master_resume(args.master_resume)
        
        # Initialize workflow
        workflow = WorkflowV52(config_path=args.config)
        
        # Run workflow
        results = workflow.run(
            job_description=job_input['job_description'],
            company_name=job_input['company_name'],
            job_title=job_input['job_title'],
            master_resume_path=args.master_resume if not args.test else None,
            output_dir=args.output_dir
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
