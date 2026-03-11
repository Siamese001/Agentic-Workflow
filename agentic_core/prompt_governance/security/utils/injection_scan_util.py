"""
injection_scan_util.py - Canonical injection scan helper.

Thin wrapper around InjectionDetector.scan() to standardize scanning calls
across all prompt joinpoints. Logs source context for audit trail without
logging raw text.
"""

from __future__ import annotations

import logging

from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)

_detector = InjectionDetector()


def scan_untrusted_text(text: str, *, source: str) -> None:
    """Scan *text* for injection signatures using the canonical detector.

    Args:
        text: The untrusted text to scan.
        source: Audit label describing the origin (e.g. "tool_output",
                "user_input", "full_prompt"). Never logged with raw text.

    Raises:
        SecurityViolationError: If an injection signature is detected.
    """
    if not text:
        return
    Logger.debug("Injection scan invoked: source=%s, length=%d", source, len(text))
    _detector.scan(text)
