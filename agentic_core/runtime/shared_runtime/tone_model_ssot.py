"""Advanced Tone Model - Emotional Brain for AI Communication.

This module provides tone analysis and adaptation capabilities to humanize AI
generation by analyzing recipient communication styles and calibrating the agent's
voice to match, preventing the "Generic AI" voice.

Models migrated to SSOT: agentic_core/schemas/models/core_contracts.py
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

from agentic_core.schemas.models.core_contracts import (
    ToneType,
    StyleProfile,
    GenerationConfig,
)

LOGGER = logging.getLogger(__name__)

# All Pydantic models (ToneType, StyleProfile, GenerationConfig) have been migrated to core_contracts.py
# This file now only contains the analyzer and adapter logic
