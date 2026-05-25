"""Prompt Governance Security - Injection detection and PII scrubbing."""

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

from .assembly_injection_neutralizer import AssemblyInjectionNeutralizer
from .detectors.injection_detector import InjectionDetector
from .detectors.pii_scrubber import PIIScrubber
from .validators import (
    validate_against_schema,
    validate_context_contract,
    validate_healer_reentry,
)

__all__ = [
    "AssemblyInjectionNeutralizer",
    "InjectionDetector",
    "PIIScrubber",
    "scan_untrusted_text",
    "validate_against_schema",
    "validate_context_contract",
    "validate_healer_reentry",
]


def scan_untrusted_text(text: str, *, source: str) -> None:
    """Lazy wrapper — avoids import cycle via utils ↔ detectors."""
    from .utils.injection_scan_util import scan_untrusted_text as _scan

    return _scan(text, source=source)
