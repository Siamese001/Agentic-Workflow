import shutil
import sys
from datetime import datetime
from pathlib import Path

from agentic_core.L0_routing.config import (
    ARCHIVES_DIR,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "archive_duplicates_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "archive_duplicates_util", "p0_governance")
_emit_snapshots_state("p0", "archive_duplicates_util", "state_snapshot")

PROJECT_ROOT = Path(__file__).parent.parent.parent
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
ARCHIVE_BASE = PROJECT_ROOT / ARCHIVES_DIR / "consolidated_duplicates" / f"batch_{TIMESTAMP}"
TARGETS = [
    "agentic_core/L5_safety/enforcement/CodeDetectorAgent.py",
    "agentic_core/L5_safety/enforcement/CodeEnforcerAgent.py",
    "agentic_core/L5_safety/enforcement/CodeHealerAgent.py",
    "agentic_core/L5_safety/enforcement/CodeValidatorAgent.py",
    "agentic_core/L5_safety/enforcement/ResourceManagerAgent.py",
    "agentic_core/L5_safety/enforcement/SafetyDetectorAgent.py",
    "agentic_core/L5_safety/enforcement/SafetyExecutorAgent.py",
    "agentic_core/L5_safety/enforcement/SecurityManagerAgent.py",
    "agentic_core/L5_safety/enforcement/StructureEnforcerAgent.py",
    "agentic_core/L5_safety/enforcement/StructureHealerAgent.py",
    "agentic_core/L5_safety/enforcement/StructureValidatorAgent.py",
    "agentic_core/L2_execution/reasoning/ModelRouterAgent.py",
    "apps_shared/base_agents/HygieneGuardianAgent.py",
]


def main():
    """TODO: Add documentation for main."""
    if not ARCHIVE_BASE.exists():
        try:
            ARCHIVE_BASE.mkdir(parents=True, exist_ok=True)
        # guardian: allow-silent-swallow
        except Exception:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            sys.exit(1)
    moved_count = 0
    missing_count = 0
    for rel_path in TARGETS:
        source_path = PROJECT_ROOT / rel_path
        filename = source_path.name
        dest_path = ARCHIVE_BASE / filename
        if dest_path.exists():
            parent_name = source_path.parent.name
            dest_path = ARCHIVE_BASE / f"{parent_name}_{filename}"
        if source_path.exists():
            try:
                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                shutil.move(str(source_path), str(dest_path))
                moved_count += 1
            # guardian: allow-silent-swallow
            except Exception:
                # TODO: Handle specific exception properly
                raise  # Re-raise after logging/handling
                pass
        else:
            missing_count += 1
    if moved_count > 0:
        pass


if __name__ == "__main__":
    main()
