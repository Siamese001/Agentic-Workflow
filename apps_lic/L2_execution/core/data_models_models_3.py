"""Dataclass models for data_models."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .data_models_enums import *

@dataclass
class QAReport:
    """
    DEPRECATED v13.0: Logic moved to HOP8_QAReportAgent.
    Output is now a persistent .md file.
    This class is kept for type hinting in legacy models if needed.
    """
    mission_id: str
    validation_results: List[ValidationResult]
    passed: bool
    timestamp: str

