# File: main.py
# Zero-Loss Consolidation - Execution Entry Point
# Merges: workflow_RES_v5_2.py → run_workflow_RES_v5_2.py
# Version: 6.1 (Batch Processing Harness)
# REFACTORED: main() is now importable via `if __name__ == "__main__":` guard
# This allows WorkflowV62 to be safely imported by batch processing scripts.
# All configuration is now read from the central CONFIG object.

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
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import from consolidated modules
from core_v6_2 import (
    # Config
    CONFIG, DATA_DIR, OUTPUT_DIR, CACHE_DIR,
    # Models
    ImmutableStagingBuffer, ThematicAnalysis, ValidationResult,
    HopResult, ValidationSeverity, ResumeSection,
    # v6.1 Models
    WorkflowBlackboard, ConductorDecision
)

from validation_stack_v6_2 import (
    ValidationContext, ValidationEngine, calculate_signal_score
)

from agent_swarm_v6_2 import (
    CrewOrchestrator, CrewConfiguration, Governor,
    ConductorAgent
)

# ============================================================================
# STRUCTURED LOGGING
# ============================================================================

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

# Version info
__version__ = "6.2.0-core-quality"

# ============================================================================
# WORKFLOW CLASS
# ============================================================================

class WorkflowV62:
    """
    Main workflow class for v6.1 Batch Harness.
    REFACTORED: Reads defaults from CONFIG. Class is now importable for batch processing.
    """
    
    def __init__(self, config_overrides: Optional[Dict] = None):
        """
        Initialize workflow with configuration.
        REFACTORED: Merges config overrides with CONFIG defaults.
        """
        self.logger = logging.getLogger(__name__)
        self.config_overrides = config_overrides or {}
        
        # Load defaults from CONFIG
        defaults = CONFIG.crew_config_defaults
        
        # Create CrewConfiguration by merging defaults with overrides
        crew_config = CrewConfiguration(
            enable_conductor=self.config_overrides.get('enable_conductor', defaults.enable_conductor),
            enable_reflection=self.config_overrides.get('enable_reflection', defaults.enable_reflection),
            enable_react=self.config_overrides.get('enable_react', defaults.enable_react),
            enable_moe=self.config_overrides.get('enable_moe', defaults.enable_moe),
            max_retries=self.config_overrides.get('max_retries', CONFIG.llm_config.defaults.max_retries),
            timeout_seconds=self.config_overrides.get('timeout_seconds', 300), # 300 was the previous hard-coded value
            max_complexity=self.config_overrides.get('max_complexity', defaults.max_complexity),
            parallel_execution=self.config_overrides.get('parallel_execution', defaults.parallel_execution),
            validation_threshold=self.config_overrides.get('validation_threshold', defaults.validation_threshold),
            enable_caching=self.config_overrides.get('enable_caching', defaults.enable_caching),
            debug_mode=self.config_overrides.get('debug_mode', defaults.debug_mode)
        )
        
        self.orchestrator = CrewOrchestrator(config=crew_config)
        
        self.logger.info(f"Workflow v6.2 initialized (version: {__version__})")
        self.logger.debug(f"Crew Configuration: {crew_config}")
    
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
        """
        self.logger.info("=" * 80)
        self.logger.info(f"Starting Workflow v6.2 for {company_name} - {job_title}")
        self.logger.info("=" * 80)
        
        start_time = datetime.now()
        workflow_id = str(uuid.uuid4())
        
        # Add workflow_id to the logging context (if using a more advanced logger)
        # For stdlib logging, we can pass it in extra
        
        try:
            # Load master resume
            master_resume = self._load_master_resume(master_resume_path)
            
            # Process job application through crew
            results = self.orchestrator.process_job_application(
                job_description=job_description,
                company_name=company_name,
                job_title=job_title,
                master_resume=master_resume,
                workflow_id=workflow_id
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
                'workflow_id': workflow_id
            }
            
            # Determine overall status
            workflow_status = results.get('workflow_results', {})
            if workflow_status.get('status') == 'COMPLETED':
                self.logger.info(f"✅ Workflow completed successfully [workflow_id: {workflow_id}]")
                results['overall_status'] = 'SUCCESS'
            elif workflow_status.get('status') == 'FAILED' and 'validation' in results:
                self.logger.warning(f"⚠️ Workflow completed with validation issues [workflow_id: {workflow_id}]")
                results['overall_status'] = 'PARTIAL'
            else:
                self.logger.error(f"❌ Workflow failed [workflow_id: {workflow_id}]")
                results['overall_status'] = 'FAILED'
            
            return results
            
        except Exception as e:
            self.logger.critical(f"❌ Workflow failed with unhandled exception [workflow_id: {workflow_id}]", exc_info=True)
            
            return {
                'overall_status': 'FAILED',
                'error': str(e),
                'execution_metadata': {
                    'start_time': start_time.isoformat(),
                    'execution_time_seconds': (datetime.now() - start_time).total_seconds(),
                    'version': __version__,
                    'workflow_id': workflow_id
                }
            }
        
        finally:
            self.logger.info("=" * 80)
            self.logger.info(f"Workflow v6.2 execution finished [workflow_id: {workflow_id}]")
            self.logger.info("=" * 80)
    
    def _load_master_resume(self, master_resume_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load master resume from file or use default.
        REFACTORED: Reads fallback paths from CONFIG.
        """
        search_paths = []
        
        # 1. Try provided path first
        if master_resume_path:
            search_paths.append(Path(master_resume_path))
            
        # 2. Add default paths from CONFIG
        for path_str in CONFIG.file_paths.fallback_search_paths:
            search_paths.append(Path(path_str))
        
        # 3. Add paths relative to DATA_DIR
        search_paths.append(DATA_DIR / "master_resume.json")
        
        for path in search_paths:
            if path.exists():
                self.logger.info(f"Loading master resume from: {path}")
                try:
                    with open(path, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    self.logger.warning(f"Failed to load master resume from {path}: {e}")
        
        # Return empty template from CONFIG if no master resume found
        self.logger.warning("No master resume found, using empty template from config")
        # Convert namespace back to dict for consistency
        return vars(CONFIG.file_paths.empty_master_resume_template)
    
    def _create_empty_master_resume(self) -> Dict[str, Any]:
        """
        DEPRECATED: Left for compatibility, but _load_master_resume now handles this.
        REFACTORED: Reads empty template from CONFIG.
        """
        self.logger.warning("Using empty master resume template from config.")
        return vars(CONFIG.file_paths.empty_master_resume_template)
    
    def _save_artifacts(self, results: Dict[str, Any], output_dir: str, 
                       company_name: str, job_title: str):
        """Save workflow artifacts to output directory."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create safe filename
        safe_company = re.sub(r'[^a-zA-Z0-9_-]', '_', company_name)
        safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', job_title)
        base_filename = f"{safe_company}_{safe_title}"
        
        # Save complete results
        results_file = output_path / f"{base_filename}_results.json"
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            self.logger.info(f"Saved results to: {results_file}")
        except Exception as e:
            self.logger.error(f"Failed to save results file: {e}")
        
        # Save individual artifacts
        artifacts = results.get('artifacts', {})
        for artifact_name, artifact_content in artifacts.items():
            artifact_file = output_path / f"{base_filename}_{artifact_name}"
            
            try:
                if isinstance(artifact_content, dict) or isinstance(artifact_content, list):
                    with open(f"{artifact_file}.json", 'w') as f:
                        json.dump(artifact_content, f, indent=2, default=str)
                else:
                    with open(f"{artifact_file}.txt", 'w') as f:
                        f.write(str(artifact_content))
            except Exception as e:
                 self.logger.error(f"Failed to save artifact {artifact_name}: {e}")
        
        self.logger.info(f"Saved {len(artifacts)} artifacts to: {output_path}")

# ============================================================================
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

def load_master_resume(filepath: str) -> Dict[str, Any]:
    """Load master resume from JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load master resume: {e}")
        raise

def setup_logging(debug_mode: bool):
    """
    Configure structured logging based on CONFIG.
    REFACTORED: Reads all settings from CONFIG.
    """
    log_config = CONFIG.logging_config
    
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

    # Add Console Handler (Human-readable)
    try:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        root_logger.addHandler(console_handler)
    except Exception as e:
        print(f"Error setting up console logger: {e}", file=sys.stderr)

    logger.info(f"Logging configured. Level: {log_level}, File: {log_config.log_file}")


def print_summary(results: Dict[str, Any]):
    """Print workflow execution summary."""
    print("\n" + "=" * 80)
    print("WORKFLOW EXECUTION SUMMARY")
    print("=" * 80)
    
    # Overall status
    status = results.get('overall_status', 'UNKNOWN')
    status_emoji = {
        'SUCCESS': '✅',
        'PARTIAL': '⚠️',
        'FAILED': '❌',
        'UNKNOWN': '❓'
    }
    print(f"\nStatus: {status_emoji.get(status, '❓')} {status}")
    
    # Execution metadata
    metadata = results.get('execution_metadata', {})
    if metadata:
        print(f"\nExecution Time: {metadata.get('execution_time_seconds', 0):.2f}s")
        print(f"Version: {metadata.get('version', 'unknown')}")
        print(f"Workflow ID: {metadata.get('workflow_id', 'N/A')}")
    
    # Validation results
    validation = results.get('validation', {})
    if validation:
        print(f"\nValidation Passed: {validation.get('passed', False)}")
        failures = results.get('critical_failures', []) # From validation engine
        if failures:
            print(f"Critical Failures: {len(failures)}")
            for fail in failures:
                print(f"  - {fail.get('rule_id')}: {fail.get('message')}")

    # Artifacts
    artifacts = results.get('artifacts', {})
    if artifacts:
        print(f"\nArtifacts Generated: {len(artifacts)}")
        for name in artifacts.keys():
            print(f"  - {name}")
    
    # Conductor decision (v6.1)
    if 'conductor_decision' in results:
        conductor = results['conductor_decision']
        print(f"\nConductor Decision:")
        print(f"  Winning Strategy: {conductor.get('winning_branch', {}).get('strategy_description', 'N/A')}")
        print(f"  Branches Evaluated: {len(conductor.get('all_branches', []))}")
    
    # Errors
    if 'error' in results:
        print(f"\nError: {results['error']}")
    
    print("\n" + "=" * 80)

# ============================================================================
# MAIN ENTRY POINT
# REFACTORED: main() is now wrapped in `if __name__ == "__main__":`
# This allows `WorkflowV62` to be safely imported
# by other scripts, like `run_batch_v6_1.py`.
# ============================================================================

def main():
    """
    Main entry point for V6.1 Batch Harness Workflow.
    REFACTORED: Reads defaults from CONFIG. Now importable for batch processing.
    """
    script_path = os.path.relpath(__file__) if "__file__" in globals() else "main_v5_8.py"
    
    # REFACTORED: Load defaults from CONFIG
    try:
        default_job_input = CONFIG.file_paths.default_job_input
        default_master_resume = CONFIG.file_paths.default_master_resume
    except Exception as e:
        print(f"FATAL: Could not load file_paths from config: {e}", file=sys.stderr)
        default_job_input = "job_input.json"
        default_master_resume = "master_resume.json"
    
    parser = argparse.ArgumentParser(
        description=f'V6.2 MoE + Reflection + ReAct + Conductor System (Version: {__version__})',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python {script_path}                           # Run with default {default_job_input}
  python {script_path} -j custom_job.json        # Use custom job input file
  python {script_path} -m custom_master.json     # Use custom master resume
  python {script_path} -o /path/to/output        # Specify output directory
  python {script_path} --debug                   # Enable debug mode
  python {script_path} --test                    # Run with test data
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
        '--test',
        action='store_true',
        help='Run with test data (no files required)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration override JSON file (merges with master_config.json)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'V6.2 MoE + Reflection + ReAct + Conductor System - Version {__version__}'
    )
    
    args = parser.parse_args()
    
    # Configure Structured Logging
    # REFACTORED: Use config-driven setup function
    setup_logging(args.debug)
    
    if args.debug:
        logger.debug("Debug mode enabled")
    
    config_overrides = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config_overrides = json.load(f)
            logger.info(f"Loaded config overrides from: {args.config}")
        except Exception as e:
            logger.error(f"Failed to load config override file {args.config}: {e}")
    
    try:
        if args.test:
            # Use test data
            logger.info("🧪 Running in TEST mode with sample data")
            job_input = {
                'company_name': 'Neo4j',
                'job_title': 'Vice President, Growth & Strategic Partnerships',
                'job_description': """
                Vice President, Growth & Strategic Partnerships at Neo4j.
                Responsible for driving inorganic growth through strategic partnerships
                and leading M&A activities. Must have 15+ years experience in enterprise
                software, strategic partnerships, and corporate development.
                """,
                'jd_url': 'https://example.com/job/neo4j'
            }
            # Master resume is loaded by _load_master_resume, which will use the empty template
        else:
            # Load real data
            job_input = load_job_input(args.job_input)
        
        # Initialize workflow
        workflow = WorkflowV62(config_overrides=config_overrides)
        
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
        logger.critical(f"❌ Fatal error in main execution: {e}", exc_info=args.debug)
        sys.exit(1)

if __name__ == "__main__":
    # This block now acts as the guard
    main()