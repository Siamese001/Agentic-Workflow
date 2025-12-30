"""
ComplianceOrchestrator: Coordinates all canon compliance agents.
Replaces void_compliance.py.
"""
import logging
import time
import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Sovereign Agent Imports
from agentic_core.L5_safety.validators.location_agent import location_agent as LocationAgent
from agentic_core.utils.naming.naming_agent import naming_agent as NamingAgent
from agentic_core.L5_safety.validators.hierarchy_agent import hierarchy_agent as HierarchyAgent
from agentic_core.L5_safety.validators.filesystem_agent import filesystem_agent as FileSystemAgent
from agentic_core.L5_safety.validators.key_mapping_agent import key_mapping_agent as KeyMappingAgent
from agentic_core.L5_safety.gravity.import_agent import import_agent as ImportAgent
from agentic_core.L5_safety.guardrails.healer_agent import healer_agent as HealerAgent
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    HEALING_CONFIG,
    MISSION_CONFIG
)

# Observability agents
try:
    from agentic_core.observability.tracing.tracing_agent import tracing_agent as TracingAgent
    from agentic_core.observability.telemetry.telemetry_agent import telemetry_agent as TelemetryAgent
    from agentic_core.observability.metrics.metrics_agent import metrics_agent as MetricsAgent
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False

# Fission threshold from Canon Law
MAX_LINES = 800

logger = logging.getLogger(__name__)


class compliance_orchestrator:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        
        # Core agents
        self.key_agent = key_mapping_agent(self.project_root)
        self.location_agent = location_agent(self.project_root)
        self.hierarchy_agent = hierarchy_agent(self.project_root)
        self.naming_agent = naming_agent(self.project_root)
        self.fs_agent = filesystem_agent(self.project_root)
        self.import_agent = import_agent(self.project_root)
        self.healer = healer_agent(self.project_root, dry_run=False)

        # Observability agents (optional)
        if OBSERVABILITY_AVAILABLE:
            self.tracing = TracingAgent(self.project_root)
            self.telemetry = TelemetryAgent(self.project_root)
            self.metrics = MetricsAgent(self.project_root)
        else:
            self.tracing = self.telemetry = self.metrics = None

    def run_full_compliance(self, auto_heal: bool = False) -> List[Tuple[Path, str]]:
        """
        [L5 CONDUCTOR] Orchestrates the multi-phase compliance mission.
        """
        all_violations: List[Tuple[Path, str]] = []
        large_files: List[Path] = []
        mission_id = f"compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = time.time()

        # 1. Observability: Mission Start
        if self.telemetry:
            self.telemetry.compliance_scan_started(mission_id)
        if self.metrics:
            self.metrics.increment("compliance.missions_started")

        # 2. Tracing: Root Span Initialization
        trace_ctx = self.tracing.trace_compliance_mission(mission_id) if self.tracing else None
        root_span = None

        try:
            # Note: We enter the tracing context if available
            with (trace_ctx if trace_ctx else open(os.devnull, "w")) as span_or_file:
                if trace_ctx:
                    root_span = span_or_file
                    root_span.set_attribute("orchestrator_version", "v3")
                    root_span.set_attribute("auto_heal", auto_heal)

                all_py_files = list(self.project_root.rglob("*.py"))
                
                # Detect candidates for sub-atomic healing (Fission/Fusion)
                # RATIONALE: Logic moved to Orchestrator to prevent redundant I/O
                dust_files: List[Path] = []
                for file_path in all_py_files:
                    try:
                        with open(file_path, 'rb') as f:
                            line_count = sum(1 for _ in f)
                        
                        if line_count > MAX_LINES and file_path.name != "__init__.py":
                            large_files.append(file_path)
                            all_violations.append((file_path, f"FISSION VIOLATION: {line_count} lines (> {MAX_LINES})"))
                        elif 0 < line_count < MIN_LINES_PER_FILE:
                            dust_files.append(file_path)
                    except Exception as e:
                        logger.warning(f"Failed to count lines for {file_path.name}: {e}")

                # PHASE A: Territorial Enforcement (Gatekeeper)
                location_violations = self.location_agent.run(all_py_files)
                all_violations.extend(location_violations)

                if location_violations:
                    logger.warning(f"[LOCATION] {len(location_violations)} territorial violations")
                    # ADAPTIVE EXIT: If critical (forbidden roots), abort expensive checks
                    critical = any("VOID VIOLATION" in msg or "Forbidden" in msg for _, msg in location_violations)
                    if critical and not auto_heal:
                        logger.error("[ORCHESTRATOR] Critical location violations - aborting mission check")
                        return all_violations

                valid_files, _ = self.location_agent.enforce_void_compliance(py_files)

                # PHASE B: Parallel Signal & Structural Checks
                def run_naming(): 
                    return self.naming_agent.run(valid_files)
                
                def run_hierarchy(): 
                    return self.hierarchy_agent.run()
                
                def run_filesystem():
                    return self.fs_agent.run()

                with ThreadPoolExecutor(max_workers=3) as executor:
                    futures = {
                        executor.submit(run_naming): "naming",
                        executor.submit(run_hierarchy): "hierarchy",
                        executor.submit(run_filesystem): "filesystem"
                    }
                    for future in as_completed(futures):
                        agent_type = futures[future]
                        try:
                            res = future.result()
                            all_violations.extend(res)
                        except Exception as e:
                            logger.error(f"[ORCHESTRATOR] Parallel agent '{agent_type}' failed: {e}")

                # PHASE C: Gravity & Semantic Enforcement (Expensive)
                import_violations = self.import_agent.run(valid_files)
                for file_path, msgs in import_violations:
                    all_violations.extend((file_path, msg) for msg in msgs)

                # PHASE D: Autonomous Healing (Key 15)
                if auto_heal and (all_violations or large_files or dust_files):
                    logger.info(f"[HEALING PHASE] Auto-healing {len(all_violations)} violations + {len(large_files)} fission candidates + {len(dust_files)} fusion candidates")
                    
                    healing_results = self.healer.heal_all(
                        all_violations, 
                        large_files=large_files, 
                        dust_files=dust_files
                    )
                    
                    logger.info(f"[HEALING COMPLETE] {healing_results['total_actions']} actions recorded.")
                    if healing_results.get('backup_dir'):
                        logger.info(f"[BACKUP] Safety seal at: {healing_results['backup_dir']}")

        finally:
            # 3. Observability: Mission Wrap-up
            duration = time.time() - start_time
            total = len(all_violations)
            compliant = total == 0

            if self.telemetry:
                self.telemetry.compliance_scan_completed(total, duration, compliant)
            if self.metrics:
                self.metrics.record_compliance_scan(all_violations)
                # Explicitly trigger infrastructure probe for Key 17
                self.metrics.check_redis_monitor()

            if root_span:
                root_span.set_attribute("total_violations", total)
                root_span.set_attribute("compliant", compliant)
                root_span.set_status("ERROR" if not compliant else "SUCCESS")

            logger.info(f"[ORCHESTRATOR] Mission complete: {total} violations in {duration:.2f}s" if total else f"[ORCHESTRATOR] Fully compliant in {duration:.2f}s")

        return all_violations

    def get_summary(self) -> Dict[str, Any]:
        violations = self.run_full_compliance()
        return {
            "total_violations": len(violations),
            "violations": violations,
            "fully_compliant": len(violations) == 0,
        }


# Uppercase alias for backward compatibility
ComplianceOrchestrator = compliance_orchestrator


def run_full_compliance(project_root: Path) -> List[Tuple[Path, str]]:
    """Recommended new entrypoint."""
    return compliance_orchestrator(project_root).run_full_compliance()


# Temporary bridge — delete after migration
def enforce_void_compliance(files: List[Path], project_root: Path) -> Tuple[List[Path], List[Tuple[Path, str]]]:
    orchestrator = compliance_orchestrator(project_root)
    all_violations = orchestrator.run_full_compliance()
    violation_set = {p for p, _ in all_violations}
    valid = [f for f in files if f not in violation_set]
    file_violations = [(p, m) for p, m in all_violations if p in files]
    return valid, file_violations
