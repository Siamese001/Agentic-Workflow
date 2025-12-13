"""Types and models for message_assembler."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class QABlockType(Enum):
    LINKEDIN_QA_GRID = 'LINKEDIN_QA_GRID'
    AI_FILTER_CANONICAL = 'AI_FILTER_CANONICAL'
    MESSAGE_SPECIFIC_RAG_QA = 'MESSAGE_SPECIFIC_RAG_QA'
    EVIDENCE_PACK = 'EVIDENCE_PACK'

@dataclass
class QABlock:
    block_type: QABlockType
    title: str
    content: str
    order: int

@dataclass
class MessageAssemblerConfig:
    canonical_signature_lines: int = 4
    required_qa_blocks: int = 4

@dataclass
class MessageAssemblerResult:
    final_message: str
    qa_blocks: List[QABlock]
    signature: str
    validation_results: List[ValidationResult]
    success: bool
    metadata: Dict[str, Any]
