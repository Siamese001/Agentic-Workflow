# File: workflow_RES_v5_2.py
# Version: 5.2.0 - Recovery Workflow
# Main workflow orchestration with v3.8 logic integrated into v5.1 architecture

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

# Import advisory crew and orchestrator
from advisory_crew_v5_2 import CrewOrchestrator, CrewConfiguration

# Import models and config
from models_RES import (
    ImmutableStagingBuffer, ValidationResult, ValidationSeverity
)
from config_RES import CONFIG, DATA_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkflowV52:
    """
    Main workflow class for v5.2 recovery system.
    Integrates v3.8 deterministic logic with v5.1 agent architecture.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize workflow with configuration."""
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config_overrides = json.load(f)
        else:
            self.config_overrides = {}
        
        # Initialize crew orchestrator
        crew_config = CrewConfiguration(
            max_complexity=100,
            parallel_execution=False,
            validation_threshold=0.8,
            enable_caching=True,
            debug_mode=self.config_overrides.get('debug', False)
        )
        
        self.orchestrator = CrewOrchestrator(config=crew_config)
        
        self.logger.info("Workflow v5.2 initialized with recovery system")
    
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
                'version': 'v5.2-recovery',
                'config_overrides': self.config_overrides
            }
            
            # Determine overall status
            workflow_status = results.get('workflow_results', {})
            if workflow_status.get('status') == 'COMPLETED':
                self.logger.info("✅ Workflow completed successfully")
                results['overall_status'] = 'SUCCESS'
            else:
                self.logger.warning("⚠️ Workflow completed with issues")
                results['overall_status'] = 'PARTIAL'
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Workflow failed: {e}", exc_info=True)
            
            return {
                'overall_status': 'FAILED',
                'error': str(e),
                'execution_metadata': {
                    'start_time': start_time.isoformat(),
                    'execution_time_seconds': (datetime.now() - start_time).total_seconds(),
                    'version': 'v5.2-recovery'
                }
            }
        
        finally:
            self.logger.info("=" * 80)
            self.logger.info("Workflow v5.2 execution completed")
            self.logger.info("=" * 80)
    
    def _load_master_resume(self, master_resume_path: Optional[str] = None) -> Dict[str, Any]:
        """Load master resume from file or use default."""
        if master_resume_path and os.path.exists(master_resume_path):
            self.logger.info(f"Loading master resume from: {master_resume_path}")
            with open(master_resume_path, 'r') as f:
                return json.load(f)
        else:
            # Check for default master resume in v3_8 directory
            default_path = "/home/claude/v3_8/master_resume.json"
            if os.path.exists(default_path):
                self.logger.info(f"Loading default master resume from: {default_path}")
                with open(default_path, 'r') as f:
                    return json.load(f)
            else:
                self.logger.warning("No master resume found, using empty template")
                return self._create_empty_master_resume()
    
    def _create_empty_master_resume(self) -> Dict[str, Any]:
        """Create an empty master resume template."""
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
        safe_company = company_name.replace(' ', '_').replace('/', '_')
        safe_title = job_title.replace(' ', '_').replace('/', '_')
        app_dir = output_path / f"{safe_company}_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        app_dir.mkdir(parents=True, exist_ok=True)
        
        artifacts = results.get('artifacts', {})
        
        # Save resume
        if 'resume' in artifacts:
            resume_path = app_dir / "resume.md"
            with open(resume_path, 'w') as f:
                f.write(artifacts['resume'])
            self.logger.info(f"✅ Saved resume to: {resume_path}")
        
        # Save cover letter
        if 'cover_letter' in artifacts:
            cover_letter_path = app_dir / "cover_letter.txt"
            with open(cover_letter_path, 'w') as f:
                f.write(artifacts['cover_letter'])
            self.logger.info(f"✅ Saved cover letter to: {cover_letter_path}")
        
        # Save QA report
        if 'qa_report' in artifacts:
            qa_report_path = app_dir / "qa_report.md"
            with open(qa_report_path, 'w') as f:
                f.write(artifacts['qa_report'])
            self.logger.info(f"✅ Saved QA report to: {qa_report_path}")
        
        # Save tracker entry
        if 'tracker' in artifacts:
            tracker_path = app_dir / "tracker_entry.json"
            with open(tracker_path, 'w') as f:
                json.dump(artifacts['tracker'], f, indent=2)
            self.logger.info(f"✅ Saved tracker entry to: {tracker_path}")
        
        # Save complete results JSON
        results_path = app_dir / "workflow_results.json"
        
        # Convert any non-serializable objects
        def json_serializer(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            elif hasattr(obj, '_asdict'):
                return obj._asdict()
            else:
                return str(obj)
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=json_serializer)
        self.logger.info(f"✅ Saved workflow results to: {results_path}")
        
        self.logger.info(f"📁 All artifacts saved to: {app_dir}")


def main():
    """Main entry point for testing the workflow."""
    # Test configuration
    test_job = {
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
        """
    }
    
    # Initialize workflow
    workflow = WorkflowV52()
    
    # Run workflow
    results = workflow.run(
        job_description=test_job['job_description'],
        company_name=test_job['company_name'],
        job_title=test_job['job_title'],
        output_dir='/mnt/user-data/outputs'
    )
    
    # Print summary
    print("\n" + "=" * 80)
    print("WORKFLOW SUMMARY")
    print("=" * 80)
    print(f"Status: {results.get('overall_status', 'UNKNOWN')}")
    
    if 'workflow_results' in results:
        phases = results['workflow_results'].get('phases', {})
        for phase_name, phase_data in phases.items():
            status = phase_data.get('status', 'UNKNOWN')
            print(f"  {phase_name}: {status}")
    
    if 'artifacts' in results:
        print(f"\nArtifacts generated: {len(results['artifacts'])}")
        for artifact_name in results['artifacts'].keys():
            print(f"  - {artifact_name}")
    
    if 'execution_metadata' in results:
        exec_time = results['execution_metadata'].get('execution_time_seconds', 0)
        print(f"\nExecution time: {exec_time:.2f} seconds")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
