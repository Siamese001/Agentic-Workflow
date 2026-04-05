from __future__ import annotations

# Configuration constants

"""Implementation for config."""
import json
import logging
from pathlib import Path
from typing import Any
from agentic_core.config.core.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

Logger: Any = logging.getLogger(__name__)


def _load_json_config(filename: str, description: str, required: bool = True) -> dict[str, object]:
    """
    Loads a JSON config file.
    It now checks the provided path first, then checks relative to DATA_DIR.
    """
    path_to_check = Path(filename)
    # guardian: allow-config-with-logic
    if not path_to_check.is_absolute() and (not path_to_check.exists()):
        path_to_check = DATA_DIR / filename
    # guardian: allow-config-with-logic
    if path_to_check.exists():
        try:
            with open(path_to_check, encoding="utf-8") as f:
                json.load(f)
                logging.info(f"Successfully loaded {description} from '{path_to_check}'.")
                return data
        except json.JSONDecodeError as e:
            logging.error(f"CRITICAL: Invalid JSON in {description} file '{path_to_check}': {e}. Halting.")
            raise
    # guardian: allow-config-with-logic
    if required:
        logging.error(
            f"CRITICAL: {description} file not found. Tried: {filename} and {path_to_check}. Halting.",
        )
        raise FileNotFoundError(f"{description} file not found: {path_to_check}")
    logging.warning(f"Optional config file '{filename}' not found, returning empty dict")
    return {}
