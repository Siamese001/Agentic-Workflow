"""
ComplianceOrchestrator: Coordinates all canon compliance agents.
Replaces void_compliance.py.
"""
from pathlib import Path
from typing import List, Tuple, Dict, Any
import logging

# Sovereign Agent Imports
from agentic_core.L5_safety.validators.location_agent import location_agent as LocationAgent
from agentic_core.L5_safety.validators.naming_agent import naming_agent as NamingAgent
from agentic_core.L5_safety.validators.hierarchy_agent import hierarchy_agent as HierarchyAgent
from agentic_core.L5_safety.validators.key_mapping_agent import key_mapping_agent as KeyMappingAgent
from agentic_core.L5_safety.gravity.import_agent import import_agent as ImportAgent
from agentic_core.L5_safety.guardrails.healer_agent import healer_agent as HealerAgent
from agentic_core.config.blueprint_sovereign.structure_blueprint import MISSION_CONFIG

# Fission threshold from Canon Law
MAX_LINES = 800

logger = logging.getLogger(__name__)


class compliance_orchestrator:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.key_agent = key_mapping_agent(self.project_root)
        self.location_agent = location_agent(self.project_root)
        self.hierarchy_agent = hierarchy_agent(self.project_root)
        self.naming_agent = naming_agent(self.project_root)
        self.import_agent = import_agent(self.project_root)
        self.healer = healer_agent(self.project_root)

    def run_full_compliance(self, auto_heal: bool = False) -> List[Tuple[Path, str]]:
        all_violations: List[Tuple[Path, str]] = []
        large_files: List[Path] = []
        logger.info("[ORCHESTRATOR] Starting compliance mission")

        py_files = list(self.project_root.rglob("*.py"))

        # [NEW] Line Count Scan for Fission Trigger
        for file_path in py_files:
            try:
                with open(file_path, 'rb') as f:
                    line_count = sum(1 for _ in f)
                if line_count > MAX_LINES and file_path.name != "__init__.py":
                    large_files.append(file_path)
                    all_violations.append((file_path, f"FISSION VIOLATION: {line_count} lines (> {MAX_LINES})"))
            except Exception as e:
                logger.warning(f"Failed to count lines for {file_path.name}: {e}")

        # Key mapping (fast)
        self.key_agent.run_on_files(py_files)

        # Location
        all_violations.extend(self.location_agent.run(py_files))
        valid_files, _ = self.location_agent.enforce_void_compliance(py_files)

        # Hierarchy
        all_violations.extend(self.hierarchy_agent.run())

        # Naming
        all_violations.extend(self.naming_agent.run(valid_files))

        # Import & Gravity
        for file_path, msgs in self.import_agent.run(valid_files):
            all_violations.extend((file_path, msg) for msg in msgs)

        # Autonomous Healing (if enabled)
        if auto_heal and (all_violations or large_files):
            healing_results = self.healer.heal_all(all_violations, large_files=large_files)
            logger.info(f"[HEALED] {healing_results['total_actions']} structural fixes applied.")
            logger.info(f"[BACKUP] Safety seal at: {healing_results['backup_dir']}")

        total = len(all_violations)
        logger.info(f"[ORCHESTRATOR] Mission complete: {total} violations" if total else "[ORCHESTRATOR] Fully compliant")
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
