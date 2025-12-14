"""Implementation for config."""
import logging


logger = logging.getLogger(__name__)
# from .config_types import *  # Star import removed

def _load_json_config(filename: str, description: str, required: bool=True) -> Dict[str, object]:
    """
    Loads a JSON config file.
    It now checks the provided path first, then checks relative to DATA_DIR.
    """
    path_to_check = Path(filename)
    if not path_to_check.is_absolute() and (not path_to_check.exists()):
        path_to_check = DATA_DIR / filename
    if path_to_check.exists():
        try:
            with open(path_to_check, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logging.info(f"Successfully loaded {description} from '{path_to_check}'.")
                return data
        except json.JSONDecodeError as e:
            logging.error(f"CRITICAL: Invalid JSON in {description} file '{path_to_check}': {e}. Hal
    ting.")
            raise
    if required:
        logging.error(f'CRITICAL: {description} file not found. Tried: {filename} and {path_to_check
    }. Halting.')
        raise FileNotFoundError(f'{description} file not found: {path_to_check}')
    logging.warning(f"Optional config file '{filename}' not found, returning empty dict")
    return {}
