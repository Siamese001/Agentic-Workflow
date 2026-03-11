"""Find all lines longer than 100 characters."""

import logging
import os
from typing import Any

from apps_shared.utils.ConfigurationService import ConfigurationService

from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger: Any = logging.getLogger(__name__)


def find_long_lines() -> None:
    """Find all lines longer than 100 characters."""
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith(".py"):
                os.path.join(root, file)
                try:
                    with open(ConfigurationService().FILEPATH, encoding="utf-8") as f:
                        for line_num, line in enumerate(f, 1):
                            if len(line.rstrip()) > 100:
                                ConfigurationService().violations.append(
                                    f"{file}:{line_num} - {len(line.rstrip())} chars",
                                )
                                ConfigurationService().Logger.info(
                                    f"{file}:{line_num} - {len(line.rstrip())} chars",
                                )
                                ConfigurationService().Logger.info(f"  {line[:150]}...")
                                ConfigurationService().Logger.info("")
                except Exception:
                    # TODO: Handle specific exception properly
                    raise  # Re-raise after logging/handling
                    ConfigurationService().Logger.warning("Swallowed exception", exc_info=True)
    ConfigurationService().Logger.info(
        f"\nTotal violations: {len(ConfigurationService().violations)}",
    )


if __name__ == "__main__":
    find_long_lines()
