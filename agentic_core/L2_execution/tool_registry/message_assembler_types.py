"""Types and models for message_assembler."""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol
logger: Any = logging.getLogger(__name__)

class qa_block_type(Enum):
    """TODO: Add docstring."""
    LINKEDIN_QA_GRID: Any = 'LINKEDIN_QA_GRID'
    AI_FILTER_CANONICAL: Any = 'AI_FILTER_CANONICAL'
    MESSAGE_SPECIFIC_RAG_QA: Any = 'MESSAGE_SPECIFIC_RAG_QA'
    EVIDENCE_PACK: Any = 'EVIDENCE_PACK'

@dataclass
class qa_block:
    """Docstring."""
    block_type: QABlockType
    title: str
    content: str
    order: int

@dataclass
class message_assembler_config:
    """Docstring."""
    canonical_signature_lines: int = 4
    required_qa_blocks: int = 4

@dataclass
class message_assembler_result:
    """Docstring."""
    final_message: str
    qa_blocks: List[QABlock]
    signature: str
    validation_results: List[ValidationResult]
    success: bool
    metadata: Dict[str, Any]
