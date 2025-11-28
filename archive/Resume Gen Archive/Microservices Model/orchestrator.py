# orchestrator.py
"""
Main orchestrator for the decoupled resume generation pipeline (v16.0-WINNER).
A spec-driven, DAG-aware, and cryptographically-verified engine.
Manages workflow execution by calling individual hop scripts via subprocess
and coordinating data flow through files in a run directory.
"""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import time
import uuid
from pathlib import Path
import argparse
from datetime import datetime
from typing import (
    Any, Dict, List, Optional, Set, Tuple
)

# Use networkx for DAG creation and topological sort
# This is a hard requirement for a "world-class" orchestrator
try:
    import networkx as nx
except ImportError:
    print("FATAL: networkx is required. Please 'pip install networkx'", file=sys.stderr)
    sys.exit(1)

# Import all canonical definitions from our winning helper file
from helpers import (
    setup_workflow_logging, default_serializer, hash_file,
    HopCheckpoint, HopStatus, HopExecutionError, GateDecision,
    ValidationResult, WorkflowSpecError,
    WorkflowSpec, HopSpec, HopInput, HopOutput, RetryPolicy, Artifact,
    ThematicAnalysis, ImmutableStagingBuffer, ResumeSection
)

from dotenv import load_dotenv
load_dotenv()

__version__ = "16.0-WINNER"

# Configure Gemini API
try:
    import google.generativeai as genai
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        logging.info("✓ Gemini API configured successfully at module initialization")
    else:
        logging.warning("⚠️ GEMINI_API_KEY not found in environment. API calls will fail.")
except ImportError:
    logging.warning("Warning: google-generativeai package not installed.")


class WorkflowOrchestrator:
    """
    A spec-driven orchestrator that executes a workflow as a 
    Directed Acyclic Graph (DAG), ensuring cryptographic provenance
    for all data artifacts.
    """

    def __init__(self, workflow_spec_path: Path, test_mode: bool = False):
        self.workflow_id = str(uuid.uuid4())[:8]
        self.logger = logging.getLogger(__name__) # Temp, will be reset
        self.log_file_path = None
        self.run_dir = None
        self.hop_script_dir = Path(__file__).parent / "hops"
        self.run_base_dir = Path("./pipeline_runs")

        self.master_resume: Dict = {} # Will be loaded in execute_workflow
        self.hop_checkpoints: List[HopCheckpoint] = []
        self.final_validation_results: List[ValidationResult] = []
        self.rendered_output_files: Dict[str, Path] = {}

        # The core of the new engine
        self.spec: WorkflowSpec = self._load_workflow_spec(workflow_spec_path)
        self.dag: nx.DiGraph = self._build_dag(self.spec)
        self.artifacts: Dict[str, Artifact] = {} # State of all files

    def _load_workflow_spec(self, spec_path: Path) -> WorkflowSpec:
        """Loads and validates the workflow spec JSON."""
        if not spec_path.exists():
            raise WorkflowSpecError(f"Workflow spec not found: {spec_path}")
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec_data = json.load(f)
            
            # Reconstruct the spec using our dataclasses
            hops = []
            for hop_data in spec_data.get("hops", []):
                hops.append(HopSpec(
                    id=hop_data["id"],
                    script=hop_data["script"],
                    description=hop_data["description"],
                    inputs=[HopInput(**inp) for inp in hop_data.get("inputs", [])],
                    outputs=[HopOutput(**out) for out in hop_data.get("outputs", [])],
                    retry_policy=RetryPolicy(**hop_data.get("retry_policy", {})),
                    extra_args=hop_data.get("extra_args", [])
                ))
            return WorkflowSpec(
                name=spec_data["name"],
                version=spec_data["version"],
                hops=hops
            )
        except Exception as e:
            raise WorkflowSpecError(f"Failed to parse workflow spec {spec_path}: {e}")

    def _build_dag(self, spec: WorkflowSpec) -> nx.DiGraph:
        """Builds a networkx DiGraph from the workflow spec."""
        dag = nx.DiGraph()
        artifact_to_hop_map: Dict[str, str] = {} # Maps artifact_id -> hop_id that *creates* it

        # First pass: Add all hops as nodes and map outputs
        for hop in spec.hops:
            if hop.id in dag:
                raise WorkflowSpecError(f"Duplicate hop ID found: {hop.id}")
            dag.add_node(hop.id, spec=hop)
            for output in hop.outputs:
                if output.artifact_id in artifact_to_hop_map:
                    raise WorkflowSpecError(f"Duplicate artifact output: {output.artifact_id} is created by both {artifact_to_hop_map[output.artifact_id]} and {hop.id}")
                artifact_to_hop_map[output.artifact_id] = hop.id
        
        # Second pass: Add edges based on inputs
        for hop in spec.hops:
            for input_spec in hop.inputs:
                artifact_id = input_spec.artifact_id
                if artifact_id.startswith("static_"):
                    continue # Static inputs don't create dependencies
                
                producer_hop_id = artifact_to_hop_map.get(artifact_id)
                if not producer_hop_id:
                    raise WorkflowSpecError(f"Unresolved dependency: Hop '{hop.id}' requires artifact '{artifact_id}', which is not produced by any hop.")
                
                dag.add_edge(producer_hop_id, hop.id)
        
        if not nx.is_directed_acyclic_graph(dag):
            cycles = list(nx.simple_cycles(dag))
            raise WorkflowSpecError(f"Workflow is not a DAG! Circular dependencies found: {cycles}")
            
        return dag

    def _setup_run_dir_and_logging(self, company_name: str, job_title: str) -> None:
        """Creates the run directory and initializes logging into it."""
        self.run_dir = self.run_base_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.workflow_id}_{company_name.replace(' ', '_')}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger, self.log_file_path = setup_workflow_logging(
            self.workflow_id, test_mode=False, log_file_dir=self.run_dir
        )
        self.logger.info("=" * 80)
        self.logger.info(f"RESUME GENERATION ENGINE v{__version__}")
        self.logger.info(f"Workflow Spec: {self.spec.name} v{self.spec.version}")
        self.logger.info("=" * 80)
        self.logger.info(f"WORKFLOW_START - ID: {self.workflow_id}")
        self.logger.info(f"WORKFLOW_START - Run Directory: {self.run_dir}")
        self.logger.info(f"Company: {company_name}, Position: {job_title}")
        self.logger.info("=" * 80)

    def _init_static_artifacts(
        self,
        master_resume_path: Path,
        job_description_path: Path,
        config_snapshot_path: Path,
        artist_specs_path: Path
    ) -> None:
        """
        Initializes the artifact state dictionary with all known artifacts,
        marking static inputs as "ready".
        """
        self.artifacts = {}
        
        # 1. Define static artifacts
        static_artifacts = {
            "static_master_resume": master_resume_path,
            "static_jd": job_description_path,
            "static_config": config_snapshot_path,
            "static_artist_specs": artist_specs_path # From hop_3/hop_4 spec
        }

        for artifact_id, path in static_artifacts.items():
            if not path.exists():
                raise FileNotFoundError(f"Static input artifact missing: {artifact_id} at {path}")
            file_hash = hash_file(path)
            self.artifacts[artifact_id] = Artifact(
                id=artifact_id,
                path=path,
                hash=file_hash,
                is_ready=True,
                is_static=True
            )
            self.logger.info(f"Registered static artifact: {artifact_id} (Hash: {file_hash[:12]}...)")

        # 2. Define dynamic (hop-generated) artifacts
        for hop in self.spec.hops:
            for output in hop.outputs:
                artifact_id = output.artifact_id
                # Create a deterministic path inside the run_dir
                file_path = self.run_dir / f"{hop.id}_{artifact_id}.json"
                
                # Special cases for non-json files
                if artifact_id == "final_resume_md":
                    file_path = file_path.with_suffix(".md")
                
                self.artifacts[artifact_id] = Artifact(
                    id=artifact_id,
                    path=file_path,
                    is_ready=False,
                    is_static=False
                )
        self.logger.info(f"Initialized {len(self.artifacts)} total artifacts for tracking.")


    def _run_hop(self, hop_id: str, dynamic_args: Dict[str, str]) -> None:
        """
        Executes a single hop with retry logic and cryptographic verification.
        This is the core execution worker.
        """
        hop_spec = self.spec.get_hop_by_id(hop_id)
        if not hop_spec:
            raise HopExecutionError(f"Could not find spec for hop_id: {hop_id}")

        self.logger.info(f"--- Preparing Hop: {hop_id} ({hop_spec.description}) ---")

        script_path = self.hop_script_dir / hop_spec.script
        if not script_path.is_file():
            raise FileNotFoundError(f"Hop script not found: {script_path}")

        # 1. Build Command
        cmd = ["python", str(script_path)]
        cmd.extend(["--workflow-id", self.workflow_id])
        cmd.extend(["--run-dir", str(self.run_dir)])
        
        # Add config path (assuming it's a static arg for all)
        cmd.extend(["--config-path", str(self.artifacts["static_config"].path)])
        
        input_hashes = {}

        # 2. Add Input Artifacts to Command
        for input_spec in hop_spec.inputs:
            artifact_id = input_spec.artifact_id
            artifact = self.artifacts.get(artifact_id)
            
            if not artifact or not artifact.is_ready:
                raise HopExecutionError(f"DAG Error: Hop '{hop_id}' started but input '{artifact_id}' is not ready.")
            
            # Use arg_name for the CLI flag, e.g., --input-path-thematic-analysis
            arg_name = f"--{input_spec.arg_name}"
            cmd.extend([arg_name, str(artifact.path)])
            input_hashes[artifact_id] = artifact.hash
            
        # 3. Add Output Artifacts to Command
        for output_spec in hop_spec.outputs:
            artifact_id = output_spec.artifact_id
            artifact = self.artifacts.get(artifact_id)
            
            if not artifact:
                raise HopExecutionError(f"DAG Error: Hop '{hop_id}' has undefined output artifact '{artifact_id}'")
            
            # Use arg_name for the CLI flag, e.g., --output-path-artist-output
            arg_name = f"--output-path-{output_spec.arg_name}"
            cmd.extend([arg_name, str(artifact.path)])

        # 4. Add Extra Static Arguments (and format dynamic ones)
        for arg in hop_spec.extra_args:
            # Replace placeholders like {company_name}
            try:
                cmd.append(arg.format(**dynamic_args))
            except KeyError as e:
                self.logger.warning(f"Skipping arg for {hop_id}: missing dynamic key {e} in '{arg}'")
        
        # 5. Execute with Retry Logic
        start_time = datetime.now()
        api_calls_this_hop = 0
        policy = hop_spec.retry_policy
        
        for attempt in range(policy.attempts):
            if attempt > 0:
                delay = policy.delay_seconds * (policy.backoff_multiplier ** (attempt - 1))
                self.logger.warning(f"Retrying {hop_id} (Attempt {attempt + 1}/{policy.attempts}) after {delay:.1f}s...")
                time.sleep(delay)

            self.logger.info(f"Executing {hop_id} (Attempt {attempt + 1})...")
            self.logger.debug(f"Command: {' '.join(cmd)}")
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=False)
                
                # Always log stdout/stderr
                if result.stdout:
                    self.logger.debug(f"{hop_id} STDOUT:\n{result.stdout.strip()}")
                if result.stderr:
                    self.logger.warning(f"{hop_id} STDERR:\n{result.stderr.strip()}")
                
                # Find API calls
                match = re.search(r"API Calls Made: (\d+)", result.stdout)
                api_calls_this_hop = int(match.group(1)) if match else 0
                
                # Check for success
                if result.returncode == 0:
                    self.logger.info(f"✓ Hop {hop_id} SUCCEEDED (Attempt {attempt + 1}).")
                    
                    # 6. SUCCESS: Verify, Hash, and Register Outputs
                    output_hashes = {}
                    for output_spec in hop_spec.outputs:
                        artifact_id = output_spec.artifact_id
                        artifact = self.artifacts[artifact_id]
                        
                        if not artifact.path.exists():
                            # This is a critical, non-retriable failure.
                            raise HopExecutionError(f"Hop {hop_id} succeeded (exit 0) but FAILED to create output: {artifact.path}")
                        
                        # CRYPTOGRAPHIC VERIFICATION
                        file_hash = hash_file(artifact.path)
                        output_hashes[artifact_id] = file_hash
                        
                        # Update global artifact state
                        artifact.is_ready = True
                        artifact.hash = file_hash
                        self.logger.info(f"  > Verified output: {artifact_id} (Hash: {file_hash[:12]}...)")
                        
                        # Store final rendered file paths
                        if hop_id == "hop_7_rendering":
                            self.rendered_output_files[artifact_id] = artifact.path

                    # 7. Create Checkpoint
                    checkpoint = HopCheckpoint(
                        hop_id=hop_id,
                        hop_name=hop_spec.script,
                        status=HopStatus.PASS,
                        timestamp_start=start_time.isoformat(),
                        timestamp_end=datetime.now().isoformat(),
                        input_artifact_hashes=input_hashes,
                        output_artifact_hashes=output_hashes,
                        metadata={"api_calls": api_calls_this_hop},
                        retry_count=attempt
                    )
                    self.hop_checkpoints.append(checkpoint)
                    return # Successful execution, exit the retry loop
                
                # 8. FAILURE (Non-zero exit code)
                self.logger.error(f"Hop {hop_id} FAILED (Attempt {attempt + 1}) with exit code {result.returncode}.")
                if attempt == policy.attempts - 1:
                    # This was the last attempt
                    raise HopExecutionError(f"Hop {hop_id} failed after {policy.attempts} attempts. Exit Code: {result.returncode}.\nSTDERR: {result.stderr.strip()}")

            except Exception as e:
                # Catch exceptions from subprocess.run itself or our verification
                self.logger.error(f"Hop {hop_id} raised exception on attempt {attempt + 1}: {e}", exc_info=True)
                if attempt == policy.attempts - 1:
                    raise HopExecutionError(f"Hop {hop_id} failed after {policy.attempts} attempts due to exception: {e}")

        # This should not be reachable, but as a fallback
        raise HopExecutionError(f"Hop {hop_id} failed unexpectedly after all retries.")


    def _handle_workflow_termination(
        self,
        status: str, # "HALTED" or "FAILED"
        exception: Exception,
        workflow_start: datetime,
        total_api_calls: int
    ) -> Dict:
        """Builds the final result dictionary upon workflow failure."""
        workflow_end = datetime.now()
        duration = (workflow_end - workflow_start).total_seconds()
        self.logger.error(f"\nWORKFLOW {status}: {exception}", exc_info=True)
        self.logger.error(f"Terminated at: {workflow_end.isoformat()}")
        self.logger.error(f"WORKFLOW_END - Status: {status}, Duration: {duration:.1f}s, Reason: {str(exception)}")
        self.logger.error(f"WORKFLOW_END - Log file: {self.log_file_path}")
        
        # Find the failed hop
        failed_hop_id = None
        if isinstance(exception, HopExecutionError) and "Hop " in str(exception):
            failed_hop_id = str(exception).split("'")[1]
            
        # Create a final checkpoint for the failed hop
        if failed_hop_id and not any(c.hop_id == failed_hop_id for c in self.hop_checkpoints):
             checkpoint = HopCheckpoint(
                 hop_id=failed_hop_id,
                 hop_name=self.spec.get_hop_by_id(failed_hop_id).script,
                 status=HopStatus.FAIL,
                 timestamp_start=datetime.now().isoformat(), # Placeholder
                 timestamp_end=datetime.now().isoformat(),
                 error_message=str(exception)
             )
             self.hop_checkpoints.append(checkpoint)

        coc_ledger = self._build_coc_ledger(
            workflow_start, workflow_end, total_api_calls, status_override=HopStatus.FAIL
        )

        return {
            "status": status,
            "gate_decision": GateDecision.HALT.value,
            "reason": str(exception),
            "error_type": type(exception).__name__,
            "file_paths": {name: str(path) for name, path in self.rendered_output_files.items()},
            "file_contents": {}, # No contents, as render hop may not have run
            "coc_ledger": coc_ledger,
            "hop_checkpoints": [default_serializer(hc) for hc in self.hop_checkpoints],
            "workflow_duration_seconds": duration,
            "total_api_calls": total_api_calls,
            "log_file_path": str(self.log_file_path)
        }

    def _build_coc_ledger(
        self, 
        workflow_start: datetime, 
        workflow_end: datetime, 
        total_api_calls: int,
        status_override: Optional[HopStatus] = None
    ) -> Dict:
        """Builds the final Chain of Custody ledger."""
        self.logger.info("Building final Chain of Custody (CoC) ledger...")
        
        # Get hash for final thematic analysis, if it was created
        thematic_analysis_hash = self.artifacts.get("hop_0_thematic_analysis", Artifact(id="", path="")).hash
        
        overall_status = HopStatus.PASS
        if status_override:
            overall_status = status_override
        elif any(c.status == HopStatus.FAIL for c in self.hop_checkpoints):
            overall_status = HopStatus.FAIL
            
        # Compile all *final* artifact hashes
        final_artifact_state = {
            artifact.id: artifact.hash
            for artifact in self.artifacts.values()
            if artifact.is_ready
        }

        return {
            "workflow_id": self.workflow_id,
            "workflow_spec_name": self.spec.name,
            "workflow_spec_version": self.spec.version,
            "orchestrator_version": __version__,
            "timestamp_start": workflow_start.isoformat(),
            "timestamp_end": workflow_end.isoformat(),
            "duration_seconds": (workflow_end - workflow_start).total_seconds(),
            "overall_status": overall_status.value,
            "total_gemini_api_calls": total_api_calls,
            "master_resume_hash": self.artifacts["static_master_resume"].hash,
            "job_description_hash": self.artifacts["static_jd"].hash,
            "final_thematic_analysis_hash": thematic_analysis_hash,
            "hop_checkpoints_summary": [
                {"id": c.hop_id, "status": c.status.value, "start": c.timestamp_start, "end": c.timestamp_end}
                for c in self.hop_checkpoints
            ],
            "final_artifact_hashes": final_artifact_state
        }
        
    def _load_static_inputs(
        self,
        master_resume_path: Path,
        job_description: str,
        config_path: Path,
        artist_specs_path: Path
    ) -> Dict[str, Path]:
        """Writes/copies static inputs to the run_dir and returns their paths."""
        
        # 1. Master Resume
        run_mr_path = self.run_dir / "static_master_resume.json"
        shutil.copy2(master_resume_path, run_mr_path)
        self.master_resume = json.loads(run_mr_path.read_text(encoding='utf-8'))
        
        # 2. Job Description
        run_jd_path = self.run_dir / "static_job_description.txt"
        run_jd_path.write_text(job_description, encoding='utf-8')
        
        # 3. Config
        run_config_path = self.run_dir / "static_config_snapshot.json"
        if config_path.exists():
            shutil.copy2(config_path, run_config_path)
        else:
            run_config_path.write_text(json.dumps({"error": "Config file not found", "path": str(config_path)}), encoding='utf-8')

        # 4. Artist Specs
        run_artist_specs_path = self.run_dir / "static_artist_specs.json"
        if artist_specs_path.exists():
            shutil.copy2(artist_specs_path, run_artist_specs_path)
        else:
            # hop_3 and hop_4 require this, this is a fatal error
            raise FileNotFoundError(f"Artist specs file not found at: {artist_specs_path}")

        return {
            "master_resume_path": run_mr_path,
            "job_description_path": run_jd_path,
            "config_snapshot_path": run_config_path,
            "artist_specs_path": run_artist_specs_path
        }

    def execute_workflow(
        self,
        master_resume_path: Path,
        job_description: str,
        company_name: str,
        job_title: str,
        jd_url: str = "",
        config_path: Path = Path("./config.json"), # Default paths
        artist_specs_path: Path = Path("./artist_specs.json") # Default paths
    ) -> Dict:
        """
        Executes the entire resume generation workflow based on the loaded spec.
        """
        workflow_start = datetime.now()
        total_api_calls = 0
        
        try:
            # 1. Setup Run Environment
            company_name_safe = re.sub(r'[^\w\s\-]+', '', company_name).strip() or "Target_Company"
            job_title_safe = re.sub(r'[^\w\s\-]+', '', job_title).strip() or "Target_Role"
            
            self._setup_run_dir_and_logging(company_name_safe, job_title_safe)

            # 2. Write/Copy static inputs into the run_dir
            static_paths = self._load_static_inputs(
                master_resume_path=master_resume_path,
                job_description=job_description,
                config_path=config_path,
                artist_specs_path=artist_specs_path
            )
            
            # 3. Initialize Artifact State Tracker
            self._init_static_artifacts(
                master_resume_path=static_paths["master_resume_path"],
                job_description_path=static_paths["job_description_path"],
                config_snapshot_path=static_paths["config_snapshot_path"],
                artist_specs_path=static_paths["artist_specs_path"]
            )
            
            # 4. Get Deterministic Execution Order
            # This is the "safer" sequential execution path.
            try:
                sorted_hop_ids = list(nx.topological_sort(self.dag))
                self.logger.info(f"DAG topological sort complete. Execution order: {', '.join(sorted_hop_ids)}")
            except Exception as e:
                raise WorkflowSpecError(f"Failed to topologically sort DAG: {e}")

            # 5. Execute Hops Sequentially
            dynamic_args = {
                "company_name": company_name,
                "job_title": job_title,
                "jd_url": jd_url
            }
            
            for hop_id in sorted_hop_ids:
                # _run_hop will raise HopExecutionError on failure
                self._run_hop(hop_id, dynamic_args)

            # 6. Workflow Success
            workflow_end = datetime.now()
            duration = (workflow_end - workflow_start).total_seconds()
            
            # Sum API calls from all successful checkpoints
            total_api_calls = sum(c.metadata.get("api_calls", 0) for c in self.hop_checkpoints)

            # Load final files to return contents
            file_contents = {}
            for artifact_id, path in self.rendered_output_files.items():
                try:
                    file_contents[artifact_id] = path.read_text(encoding='utf-8')
                except Exception as e:
                    self.logger.error(f"Failed to read final file content for {artifact_id}: {e}")
                    file_contents[artifact_id] = f"[Error reading file: {e}]"
            
            # Build final CoC
            coc_ledger = self._build_coc_ledger(
                workflow_start, workflow_end, total_api_calls
            )

            self.logger.info("\n" + "=" * 80)
            self.logger.info("WORKFLOW COMPLETE (v16.0-WINNER)")
            self.logger.info(f"Finished: {workflow_end.isoformat()}")
            self.logger.info(f"Total Duration: {duration:.3f} seconds")
            self.logger.info(f"Total Gemini API Calls: {total_api_calls}")
            self.logger.info(f"Final Status: SUCCESS")
            self.logger.info(f"Output files written to: {self.run_dir}")
            self.logger.info(f"WORKFLOW_END - Status: SUCCESS, Duration: {duration:.1f}s")
            self.logger.info(f"WORKFLOW_END - Log file: {self.log_file_path}")
            self.logger.info("=" * 80)

            return {
                "status": "SUCCESS",
                "gate_decision": GateDecision.PROCEED.value, # Assumed, as hop_6 must have passed
                "file_paths": {name: str(path) for name, path in self.rendered_output_files.items()},
                "file_contents": file_contents,
                "coc_ledger": coc_ledger,
                "hop_checkpoints": [default_serializer(hc) for hc in self.hop_checkpoints],
                "workflow_duration_seconds": duration,
                "total_api_calls": total_api_calls,
                "log_file_path": str(self.log_file_path),
                "run_dir": str(self.run_dir)
            }

        except (HopExecutionError, WorkflowSpecError, FileNotFoundError) as e:
            total_api_calls = sum(c.metadata.get("api_calls", 0) for c in self.hop_checkpoints)
            return self._handle_workflow_termination(
                status="HALTED", exception=e, workflow_start=workflow_start,
                total_api_calls=total_api_calls
            )
        except Exception as e:
            total_api_calls = sum(c.metadata.get("api_calls", 0) for c in self.hop_checkpoints)
            return self._handle_workflow_termination(
                status="FAILED", exception=e, workflow_start=workflow_start,
                total_api_calls=total_api_calls
            )

# --- Main Execution ---
def main(args):
    """Main entry point for running the orchestrator from the CLI."""
    
    # 1. Validate paths
    spec_path = Path(args.workflow_spec)
    mr_path = Path(args.master_resume)
    config_path = Path(args.config)
    artist_specs_path = Path(args.artist_specs)
    
    if not spec_path.exists():
        print(f"FATAL: Workflow spec not found at {spec_path}", file=sys.stderr)
        sys.exit(1)
    if not mr_path.exists():
        print(f"FATAL: Master resume not found at {mr_path}", file=sys.stderr)
        sys.exit(1)
    if not config_path.exists():
        print(f"Warning: Config file not found at {config_path}. Using empty default.", file=sys.stderr)
    if not artist_specs_path.exists():
        print(f"FATAL: Artist specs not found at {artist_specs_path}. Hops 3 & 4 will fail.", file=sys.stderr)
        sys.exit(1)

    # 2. Load JD
    try:
        jd_path = Path(args.jd_file)
        job_description = jd_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"FATAL: Could not read job description file at {args.jd_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Instantiate and run orchestrator
    print(f"Initializing orchestrator v{__version__} with spec: {spec_path}")
    orchestrator = WorkflowOrchestrator(workflow_spec_path=spec_path)
    
    result = orchestrator.execute_workflow(
        master_resume_path=mr_path,
        job_description=job_description,
        company_name=args.company,
        job_title=args.title,
        jd_url=args.url,
        config_path=config_path,
        artist_specs_path=artist_specs_path
    )

    # 4. Print final summary
    print("\n" + "="*80)
    print("ORCHESTRATION COMPLETE")
    print(f"Status: {result.get('status')}")
    print(f"Run Directory: {result.get('run_dir')}")
    print(f"Log File: {result.get('log_file_path')}")
    print(f"Duration: {result.get('workflow_duration_seconds', 0):.2f}s")
    print(f"Total API Calls: {result.get('total_api_calls', 0)}")
    
    if result.get('status') != "SUCCESS":
        print(f"Error: {result.get('reason')}")
        print("="*80)
        sys.exit(1)
    
    print("\nGenerated Files:")
    for name, path in result.get('file_paths', {}).items():
        print(f"  - {name}: {path}")
    print("="*80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Resume Pipeline Orchestrator v{__version__}")
    
    # Core Inputs
    parser.add_argument("jd_file", help="Path to the job description text file.")
    parser.add_argument("-c", "--company", required=True, help="Target company name.")
    parser.add_argument("-t", "--title", required=True, help="Target job title.")
    parser.add_argument("-u", "--url", default="", help="URL of the job description.")
    
    # Config Paths
    parser.add_argument("-m", "--master-resume", default="./master_resume.json", help="Path to the master resume JSON.")
    parser.add_argument("-w", "--workflow-spec", default="./workflow_spec.json", help="Path to the workflow spec JSON.")
    parser.add_argument("--config", default="./config.json", help="Path to the general config file snapshot.")
    parser.add_argument("--artist-specs", default="./artist_specs.json", help="Path to the artist specs JSON file.")
    
    args = parser.parse_args()
    main(args)