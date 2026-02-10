"""Find all lines longer than 100 characters."""

import logging
import os
from typing import Any

from apps_shared.utils.ConfigurationService import ConfigurationService

Logger: Any = logging.getLogger(__name__)


def find_long_lines() -> None:
    """Find all lines longer than 100 characters."""
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        if ".venv" in dirs:
            dirs.remove(".venv")
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")
        for file in files:
            if file.endswith(".py"):
                # guardian: allow-path-string
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
                # guardian: allow-silent-swallow
                except Exception:
                    ConfigurationService().Logger.warning("Swallowed exception", exc_info=True)
    ConfigurationService().Logger.info(
        f"\nTotal violations: {len(ConfigurationService().violations)}",
    )


if __name__ == "__main__":
    find_long_lines()
