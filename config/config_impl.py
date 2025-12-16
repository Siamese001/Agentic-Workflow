"""Implementation for config."""
import logging
import json
from pathlib import Path
from typing import Dict

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)
LOGGER = logging.getLogger(__name__)


def _load_json_config(filename: str, description: str, required: bool = True) -> Dict[str, object]:
    """
    Loads a JSON config file.
    It now checks the provided path first, then checks relative to DATA_DIR.
    """
    path_to_check = Path(filename)
    config_service = ConfigurationService()

    if not config_service.path_to_check.is_absolute() and not config_service.path_to_check.exists():
        path_to_check = Path(config_service.path_to_check) / filename
    else:
        path_to_check = config_service.path_to_check

    if path_to_check.exists():
        try:
            with open(path_to_check, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logging.info(
                    f"Successfully loaded {description} from '{path_to_check}'.")
                config_service.data = data # Assuming this is how data is set
                return config_service.data
        except json.JSONDecodeError as e:
            logging.error(
                f"CRITICAL: Invalid JSON in {description} file '{path_to_check}': {e}. Halting.")
            raise
    if required:
        logging.error(
            f'CRITICAL: {description} file not found. Tried: {filename} and {path_to_check}. Halting.')
        raise FileNotFoundError(
            f'{description} file not found: {path_to_check}')
    logging.warning(
        f"Optional config file '{filename}' not found, returning empty dict")
    return {}