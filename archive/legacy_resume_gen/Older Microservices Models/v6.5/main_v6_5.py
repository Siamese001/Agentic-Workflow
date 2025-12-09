# File: main_v6.5.py
# Zero-Loss Consolidation - Execution Entry Point
# Overwrites: main_v6_4.py
# Version: 6.5 (Monolithic Agent Architecture)
#
# v6.5 (Based on v7.0 Architecture) CHANGES:
# - Updated all imports from v6_4 to v6_5.
# - Imports 'CrewOrchestrator' from the new monolithic 'agent_swarm_v6.5'.
# - Removed all imports and references to 'validation_stack_v6_4' as those
#   agents are now integrated into 'agent_swarm_v6.5'.
# - Updated version number to 6.5.0.
# - Renamed WorkflowV64 to WorkflowV65.

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

# Import from consolidated modules (v6.5)
from core_v6_5 import (
    # Config
    CONFIG, DATA_DIR, OUTPUT_DIR, CACHE_DIR,
    # Models
    ImmutableStagingBuffer, ThematicAnalysis, ValidationResult,
    HopResult, ValidationSeverity, ResumeSection,
    # v6.1+ Models
    WorkflowBlackboard, ConductorDecision
)

# v6.5: ValidationEngine is no longer imported here. It's encapsulated
# within the agent_swarm_v6.5.py file (specifically, in the QA agents).

# v6.5: Import from the new monolithic agent swarm
from agent_swarm_v6_5 import (
    CrewOrchestrator, CrewConfiguration
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
__version__ = "6.5.0-monolithic-v7"

# ============================================================================
# WORKFLOW CLASS
# ============================================================================

class WorkflowV65:
    """
    Main workflow class for v6.5.
    REFACTORED: Reads defaults from CONFIG. Class is importable for batch processing.
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
            timeout_seconds=self.config_overrides.get('timeout_seconds', 300),
            max_complexity=self.config_overrides.get('max_complexity', defaults.max_complexity),
            parallel_execution=self.config_overrides.get('parallel_execution', defaults.parallel_execution),
            validation_threshold=self.config_overrides.get('validation_threshold', defaults.validation_threshold),
            enable_caching=self.config_overrides.get('enable_caching', defaults.enable_caching),
            debug_mode=self.config_overrides.get('debug_mode', defaults.debug_mode)
        )
        
        # v6.5: CrewOrchestrator now comes from agent_swarm_v6_5
        self.orchestrator = CrewOrchestrator(config=crew_config)
        
        self.logger.info(f"Workflow v6.5 initialized (version: {__version__})")
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
        self.logger.info(f"Starting Workflow v6.5 for {company_name} - {job_title}")
        self.logger.info("=" * 80)
        
        start_time = datetime.now()
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
            else:
                self.logger.error(f"❌ Workflow failed [workflow_id: {workflow_id}]")
                # v6.5: Use the 'validation' block for status
                validation_results = results.get('validation', {})
                if validation_results and not validation_results.get('overall_passed', False):
                    results['overall_status'] = 'FAILED_QA'
                    results['error'] = f"QA Failed: {validation_results.get('failed_checks_count', 0)} checks failed."
                else:
                    results['overall_status'] = 'FAILED_FATAL'
            
            return results
            
        except Exception as e:
            self.logger.critical(f"❌ Workflow failed with unhandled exception [workflow_id: {workflow_id}]", exc_info=True)
            
            return {
                'overall_status': 'FAILED_FATAL',
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
            self.logger.info(f"Workflow v6.5 execution finished [workflow_id: {workflow_id}]")
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
            
        # 2. Add default path from CONFIG (v6.5 update)
        if CONFIG.file_paths.default_master_resume:
             search_paths.append(Path(CONFIG.file_paths.default_master_resume))
            
        # 3. Add fallback paths from CONFIG
        for path_str in CONFIG.file_paths.fallback_search_paths:
            search_paths.append(Path(path_str))
        
        # 4. Add paths relative to DATA_DIR
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
        results_file = output_path / f"{base_filename}_results_v6.5.json"
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            self.logger.info(f"Saved results to: {results_file}")
        except Exception as e:
            self.logger.error(f"Failed to save results file: {e}")
        
        # Save final draft
        final_draft = results.get('artifacts', {}).get('final_draft')
        if final_draft:
            draft_file = output_path / f"{base_filename}_final_draft_v6.5.txt"
            try:
                with open(draft_file, 'w') as f:
                    f.write(str(final_draft))
                self.logger.info(f"Saved final draft to: {draft_file}")
            except Exception as e:
                self.logger.error(f"Failed to save final draft: {e}")

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

def setup_logging(debug_mode: bool):
    """
    Configure structured logging based on CONFIG.
    REFACTORED: Reads all settings from CONFIG.
    """
    # v6.5: Need to re-import core_v6_5 for CONFIG if this file is run directly
    try:
        from core_v6_5 import CONFIG as LOG_CONFIG
    except ImportError:
        print("CRITICAL: core_v6_5.py not found. Logging setup failed.", file=sys.stderr)
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
    print("WORKFLOW EXECUTION SUMMARY (v6.5)")
    print("=" * 80)
    
    # Overall status
    status = results.get('overall_status', 'UNKNOWN')
    status_emoji = {
        'SUCCESS': '✅',
        'FAILED_QA': '⚠️',
        'FAILED_FATAL': '❌',
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
        print(f"\nValidation Passed: {validation.get('overall_passed', False)}")
        failures = validation.get('failed_checks', [])
        if failures:
            print(f"Failed Checks ({len(failures)}):")
            for fail in failures[:5]: # Print top 5
                agent = fail.get('agent_name', fail.get('check_name', 'N/A'))
                details = fail.get('error', fail.get('details', 'No details'))
                print(f"  - {agent}: {details}")
            if len(failures) > 5:
                print(f"  ... and {len(failures) - 5} more.")

    # Artifacts
    artifacts = results.get('artifacts', {})
    if artifacts:
        print(f"\nArtifacts Generated: {len(artifacts)}")
        print(f"  - strategy_brief: {'OK' if 'strategy_brief' in artifacts else 'MISSING'}")
        print(f"  - rag_search_results: {'OK' if 'rag_search_results' in artifacts else 'MISSING'}")
        print(f"  - final_draft: {'OK' if 'final_draft' in artifacts else 'MISSING'}")
    
    # Errors
    if 'error' in results and status == 'FAILED_FATAL':
        print(f"\nFatal Error: {results['error']}")
    
    print("\n" + "=" * 80)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """
    Main entry point for V6.5 Workflow.
    """
    script_path = os.path.relpath(__file__) if "__file__" in globals() else "main_v6_5.py"
    
    try:
        default_job_input = CONFIG.file_paths.default_job_input
        default_master_resume = CONFIG.file_paths.default_master_resume
    except Exception as e:
        print(f"FATAL: Could not load file_paths from config: {e}", file=sys.stderr)
        default_job_input = "job_input.json"
        default_master_resume = "master_resume.json"
    
    parser = argparse.ArgumentParser(
        description=f'V6.5 Monolithic Agent Architecture (Version: {__version__})',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python {script_path}                           # Run with default {default_job_input}
  python {script_path} -j custom_job.json        # Use custom job input file
  python {script_path} -m custom_master.json     # Use custom master resume
  python {script_path} -o /path/to/output        # Specify output directory
  python {script_path} --debug                   # Enable debug mode
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
        '--config',
        type=str,
        default=None,
        help='Path to configuration override JSON file (merges with master_config.json)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'V6.5 Monolithic Agent Architecture - Version {__version__}'
    )
    
    args = parser.parse_args()
    
    # Configure Structured Logging
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
        # Load real data
        job_input = load_job_input(args.job_input)
        
        # Initialize workflow
        workflow = WorkflowV65(config_overrides=config_overrides)
        
        # Run workflow
        results = workflow.run(
            job_description=job_input['job_description'],
            company_name=job_input['company_name'],
            job_title=job_input['job_title'],
            master_resume_path=args.master_resume,
            output_dir=args.output_dir
        )
        
        # Print summary
        print_summary(results)
        
        # Exit based on results
        if results.get('overall_status') == 'SUCCESS':
            logger.info("✅ Workflow completed successfully!")
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
    main()