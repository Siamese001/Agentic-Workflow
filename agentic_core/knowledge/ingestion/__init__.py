"""Knowledge Ingestion Pipeline.

Pipeline B: Ingestion & Index Build components for the Agentic RAG system.
Provides unified intake, modality detection, and document processing.
"""

from .intake_clerk import IntakeClerk
from .modality_types import ContentType, DocumentModality
from .visual_detector import VisualDetector

__all__ = [
    "IntakeClerk",
    "VisualDetector",
    "DocumentModality",
    "ContentType",
]
