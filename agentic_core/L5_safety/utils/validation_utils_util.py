from __future__ import annotations
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
'\nValidation Utilities\n\nCluster: Email, URL, and filename validation/sanitization\nLines: 317-336 from core_utils.py\n'

def validate_email(email: str) -> bool:
    """Simple email validation."""
    return '@' in email and '.' in email.split('@')[1]

def validate_url(url: str) -> bool:
    """Simple URL validation."""
    return url.startswith(('http://', 'https://'))

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem operations."""
    invalid_chars: Any = '<>:"/\\|?*'
    for char in invalid_chars:
        filename: Any = filename.replace(char, '_')
    return filename
