"""Find all lines longer than 100 characters."""

import logging
import os
from pathlib import Path
from typing import Any

from apps_shared.utils.ConfigurationService import ConfigurationService

from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "find_long_lines")
_emit_applies_guardrail("p0", "find_long_lines", "p0_governance")
_emit_reads_policy_state("p0", "find_long_lines", "policy_binding")
_emit_snapshots_state("p0", "find_long_lines", "state_snapshot")
emit_replay_key("p0", "find_long_lines")
emit_determinism_digest("p0", "find_long_lines")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger: Any = logging.getLogger(__name__)


def find_long_lines() -> None:
    """Find all lines longer than 100 characters."""
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith(".py"):
                Path(root) / file
                try:
                    with open(ConfigurationService().FILEPATH, encoding="utf-8") as f:
                        for line_num, line in enumerate(f, 1):
                            if len(line.rstrip()) > 100:
                                ConfigurationService().violations.append(
                                    f"{file}:{line_num} - {len(line.rstrip())} chars"
                                )
                                ConfigurationService().Logger.info(
                                    f"{file}:{line_num} - {len(line.rstrip())} chars"
                                )
                                ConfigurationService().Logger.info(f"  {line[:150]}...")
                                ConfigurationService().Logger.info("")
                except Exception:
                    raise
                    ConfigurationService().Logger.warning("Swallowed exception", exc_info=True)
    ConfigurationService().Logger.info(f"\nTotal violations: {len(ConfigurationService().violations)}")


if __name__ == "__main__":
    find_long_lines()
