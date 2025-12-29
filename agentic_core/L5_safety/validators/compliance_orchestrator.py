"""
ComplianceOrchestrator: Coordinates all canon compliance agents.
Replaces void_compliance.py.
"""
from pathlib import Path
from typing import List, Tuple, Dict, Any
import logging

from agentic_core.L5_safety.validators.location_agent import location_agent
from agentic_core.L5_safety.validators.hierarchy_agent import hierarchy_agent
from agentic_core.L5_safety.validators.key_mapping_agent import key_mapping_agent
from agentic_core.utils.naming.naming_agent import naming_agent
from agentic_core.L5_safety.gravity.import_agent import import_agent

logger = logging.getLogger(__name__)


class compliance_orchestrator:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.key_agent = key_mapping_agent(self.project_root)
        self.location_agent = location_agent(self.project_root)
        self.hierarchy_agent = hierarchy_agent(self.project_root)
        self.naming_agent = naming_agent(self.project_root)
        self.import_agent = import_agent(self.project_root)

    def run_full_compliance(self) -> List[Tuple[Path, str]]:
        all_violations: List[Tuple[Path, str]] = []
        logger.info("[ORCHESTRATOR] Starting compliance mission")

        py_files = list(self.project_root.rglob("*.py"))

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
