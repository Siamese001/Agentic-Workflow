# File: main.py
# Zero-Loss Consolidation - Execution Entry Point
# Merges: workflow_RES_v5_2.py → run_workflow_RES_v5_2.py
# Version: Consolidated 5.2

# ============================================================================
# EXTERNAL IMPORTS (Consolidated)
# ============================================================================
import argparse
import json
import logging
import os
import sys
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Version info
__version__ = "5.2.0-consolidated"

# ============================================================================
# PART 1: WORKFLOW CLASS (from workflow_RES_v5_2.py)
# ============================================================================

class WorkflowV52:
    """
    Main workflow class for v5.2 recovery system.
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
        
        self.logger.info(f"Workflow v5.2 initialized with recovery system (version: {__version__})")
    
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
        self.logger.info(f"Starting Workflow v5.2 for {company_name} - {job_title}")
        self.logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # Load master resume
            master_resume = self._load_master_resume(master_resume_path)
            
            # Process job application through crew
            results = self.orchestrator.process_job_application(
                job_description=job_description,
                company_name=company_name,
                job_title=job_title,
                master_resume=master_resume
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
                'config_overrides': self.config_overrides
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
            self.logger.info("Workflow v5.2 execution completed")
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
        """Save generated artifacts to output directory."""
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectory for this application
        safe_company = company_name.replace(' ', '_').replace('/', '_')[:50]
        safe_title = job_title.replace(' ', '_').replace('/', '_')[:50]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        app_dir = output_path / f"{safe_company}_{safe_title}_{timestamp}"
        app_dir.mkdir(parents=True, exist_ok=True)
        
        artifacts = results.get('artifacts', {})
        
        # Save resume
        if 'resume' in artifacts:
            resume_path = app_dir / "resume.md"
            with open(resume_path, 'w', encoding='utf-8') as f:
                f.write(artifacts['resume'])
            self.logger.info(f"✅ Saved resume to: {resume_path}")
        
        # Save cover letter
        if 'cover_letter' in artifacts:
            cover_letter_path = app_dir / "cover_letter.txt"
            with open(cover_letter_path, 'w', encoding='utf-8') as f:
                f.write(artifacts['cover_letter'])
            self.logger.info(f"✅ Saved cover letter to: {cover_letter_path}")
        
        # Save QA report
        if 'qa_report' in artifacts:
            qa_report_path = app_dir / "qa_report.md"
            with open(qa_report_path, 'w', encoding='utf-8') as f:
                f.write(artifacts['qa_report'])
            self.logger.info(f"✅ Saved QA report to: {qa_report_path}")
        
        # Save tracker entry
        if 'tracker' in artifacts:
            tracker_path = app_dir / "tracker_entry.json"
            with open(tracker_path, 'w', encoding='utf-8') as f:
                json.dump(artifacts['tracker'], f, indent=2)
            self.logger.info(f"✅ Saved tracker entry to: {tracker_path}")
        
        # Save complete results JSON
        results_path = app_dir / "workflow_results.json"
        
        # Custom JSON serializer for non-serializable objects
        def json_serializer(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            elif hasattr(obj, '_asdict'):
                return obj._asdict()
            elif isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return str(obj)
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=json_serializer)
        self.logger.info(f"✅ Saved workflow results to: {results_path}")
        
        self.logger.info(f"📁 All artifacts saved to: {app_dir}")

# ============================================================================
# PART 2: WORKFLOW RUNNER (from run_workflow_RES_v5_2.py)
# ============================================================================

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
    
    # Check multiple locations
    search_paths = [
        master_path,
        DATA_DIR / filename,
        Path("/home/claude/v3_8") / filename
    ]
    
    for path in search_paths:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    logger.info(f"Loaded master resume from: {path}")
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load master resume from {path}: {e}")
    
    logger.warning(f"Master resume not found at any location, using empty template")
    return {
        "owner": {
            "name": "[Your Name]",
            "contact": {
                "email": "[your.email@example.com]",
                "phone": "[Your Phone]"
            }
        },
        "professional_experience": [],
        "skills": [],
        "education": [],
        "certifications": []
    }

def print_summary(results: Dict[str, Any]):
    """Print a summary of the workflow results."""
    print("\n" + "=" * 80)
    print("WORKFLOW SUMMARY - V5.2 Consolidated System")
    print("=" * 80)
    
    status = results.get('overall_status', 'UNKNOWN')
    status_emoji = "✅" if status == "SUCCESS" else ("⚠️" if status == "PARTIAL" else "❌")
    print(f"{status_emoji} Overall Status: {status}")
    
    if 'workflow_results' in results:
        workflow = results['workflow_results']
        phases = workflow.get('phases', {})
        
        if phases:
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
    Main entry point for V5.2 Consolidated Workflow.
    """
    script_path = os.path.relpath(__file__) if "__file__" in globals() else "main.py"
    
    parser = argparse.ArgumentParser(
        description=f'V5.2 Consolidated System - Resume Workflow Engine (Version: {__version__})',
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
        version=f'V5.2 Consolidated System - Version {__version__}'
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
