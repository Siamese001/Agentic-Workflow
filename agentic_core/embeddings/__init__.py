"""Embedding Substrate - Token-to-vector transformation pipeline.

Implements 10C GAP-10C-001 with bge-m3 binding:
- TokenizerStage: B1 tokenization
- ModelLoader: B2-B3 checkpoint and weight loading
- ForwardPass: B4-B6 forward pass, pooling, normalization
- EmbeddingPipeline: B7-B8 metadata binding and index write
"""

from .tokenizer import TokenizerStage, TokenizedOutput
from .model_loader import ModelLoader, ModelManifest
from .forward_pass import ForwardPass, EmbeddingOutput
from .pipeline import EmbeddingPipeline, VectorRecord

__all__ = [
    "TokenizerStage",
    "TokenizedOutput",
    "ModelLoader",
    "ModelManifest",
    "ForwardPass",
    "EmbeddingOutput",
    "EmbeddingPipeline",
    "VectorRecord",
]
