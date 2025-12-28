"""Types and models for message_assembler."""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol

LOGGER = logging.getLogger(__name__)
class QABlockType(Enum):
    """TODO: Add docstring."""

    LINKEDIN_QA_GRID = 'LINKEDIN_QA_GRID'
    AI_FILTER_CANONICAL = 'AI_FILTER_CANONICAL'
    MESSAGE_SPECIFIC_RAG_QA = 'MESSAGE_SPECIFIC_RAG_QA'
    EVIDENCE_PACK = 'EVIDENCE_PACK'

@dataclass
class QABlock:
    """Docstring."""
    block_type: QABlockType
    title: str
    content: str
    order: int

@dataclass
class MessageAssemblerConfig:
    """Docstring."""
    canonical_signature_lines: int = 4
    required_qa_blocks: int = 4


@dataclass
class MessageAssemblerResult:
    """Docstring."""
    final_message: str
    qa_blocks: List[QABlock]
    signature: str
    validation_results: List[ValidationResult]
    success: bool
    metadata: Dict[str, Any]