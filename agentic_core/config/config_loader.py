from __future__ import annotations

"""Implementation for config."""

import json
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)
DATA_DIR = Path(__file__).resolve().parent


def _load_json_config(filename: str, description: str, required: bool = True) -> dict[str, object]:
    """Load a JSON config file from an absolute path or from this config directory."""
    candidate_path = Path(filename).expanduser()
    search_paths = [candidate_path]
    if not candidate_path.is_absolute():
        search_paths.append(DATA_DIR / candidate_path)

    for path_to_check in search_paths:  # progress_bar: search config file paths
        if not path_to_check.exists():
            continue
        try:
            with path_to_check.open(encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            LOGGER.error(
                "CRITICAL: Invalid JSON in %s file '%s': %s. Halting.", description, path_to_check, exc
            )
            raise

        if not isinstance(data, dict):
            raise ValueError(f"{description} file must contain a JSON object: {path_to_check}")

        LOGGER.info("Successfully loaded %s from '%s'.", description, path_to_check)
        return data

    if required:
        tried = ", ".join(str(path) for path in search_paths)
        LOGGER.error("CRITICAL: %s file not found. Tried: %s. Halting.", description, tried)
        raise FileNotFoundError(f"{description} file not found. Tried: {tried}")

    LOGGER.warning("Optional config file '%s' not found, returning empty dict", filename)
    return {}
