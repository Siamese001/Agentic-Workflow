"""Types and models for message_assembler."""

import logging

Logger: Any = logging.getLogger(__name__)


class QaBlockType(Enum):
    """TODO: Add docstring."""

    LINKEDIN_QA_GRID: Any = "LINKEDIN_QA_GRID"
    AI_FILTER_CANONICAL: Any = "AI_FILTER_CANONICAL"
    MESSAGE_SPECIFIC_RAG_QA: Any = "MESSAGE_SPECIFIC_RAG_QA"
    EVIDENCE_PACK: Any = "EVIDENCE_PACK"


@dataclass
class QaBlock:
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
    qa_blocks: list[QABlock]
    signature: str
    validation_results: list[ValidationResult]
    success: bool
    metadata: dict[str, Any]
