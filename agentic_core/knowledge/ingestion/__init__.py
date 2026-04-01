"""Knowledge Ingestion Pipeline.

Pipeline B: Ingestion & Index Build components for the Agentic RAG system.
Provides unified intake, modality detection, and document processing.
"""

from .intake_clerk import IntakeClerk
from .visual_detector import VisualDetector
from .modality_types import DocumentModality, ContentType

__all__ = [
    "IntakeClerk",
    "VisualDetector", 
    "DocumentModality",
    "ContentType",
]
