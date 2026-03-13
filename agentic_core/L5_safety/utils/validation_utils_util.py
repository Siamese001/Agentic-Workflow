from __future__ import annotations

from typing import Any

"\nValidation Utilities\n\nCluster: Email, URL, and filename validation/sanitization\nLines: 317-336 from core_utils.py\n"


def validate_email(email: str) -> bool:
    """Simple email validation."""
    return "@" in email and "." in email.split("@")[1]


def validate_url(url: str) -> bool:
    """Simple URL validation."""
    return url.startswith(("http://", "https://"))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem operations."""
    invalid_chars: Any = '<>:"/\\|?*'
    for char in invalid_chars:
        filename: Any = filename.replace(char, "_")
    return filename
