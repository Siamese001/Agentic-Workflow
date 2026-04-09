"""B1 Tokenizer Stage - Tokenization for embedding.

10C-REQ-100: Tokenizer load tokenize text to IDs attention mask padding truncation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TokenizedOutput:
    """Output from tokenization."""
    input_ids: list[int]
    attention_mask: list[int]
    token_count: int
    truncated: bool
    padded: bool


class TokenizerStage:
    """B1: Tokenizer load and tokenization.

    10C-REQ-100: Text to token IDs with attention mask, padding, truncation.

    **HITL-10C-001**: bge-m3 tokenizer (multilingual, 8192 ctx).
    """

    DEFAULT_MODEL = "BAAI/bge-m3"  # HITL-10C-001 selection
    DEFAULT_MAX_LENGTH = 8192

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or self.DEFAULT_MODEL
        self._max_length = self.DEFAULT_MAX_LENGTH
        self._tokenizer: Any | None = None

    def load(self) -> bool:
        """Load tokenizer from HuggingFace."""
        try:
            from transformers import AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            return True
        except ImportError:
            # Fallback: simple whitespace tokenization
            self._tokenizer = None
            return False

    def tokenize(
        self,
        text: str,
        max_length: int | None = None,
        truncation: bool = True,
        padding: bool = True,
    ) -> TokenizedOutput:
        """Tokenize text to IDs with attention mask."""
        max_len = max_length or self._max_length

        if self._tokenizer:
            # Use HF tokenizer
            result = self._tokenizer(
                text,
                max_length=max_len,
                truncation=truncation,
                padding="max_length" if padding else False,
                return_attention_mask=True,
            )

            return TokenizedOutput(
                input_ids=result["input_ids"],
                attention_mask=result["attention_mask"],
                token_count=sum(result["attention_mask"]),
                truncated=len(result["input_ids"]) >= max_len,
                padded=padding and len(result["input_ids"]) < max_len,
            )
        else:
            # Fallback: whitespace tokenization
            tokens = text.split()[:max_len]
            token_count = len(tokens)

            # Simple ID mapping (not real, just for structure)
            input_ids = [hash(t) % 50000 for t in tokens]

            # Pad
            if padding and len(input_ids) < max_len:
                input_ids.extend([0] * (max_len - len(input_ids)))
                attention_mask = [1] * token_count + [0] * (max_len - token_count)
            else:
                attention_mask = [1] * token_count

            return TokenizedOutput(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_count=token_count,
                truncated=len(tokens) >= max_len,
                padded=padding and len(input_ids) < max_len,
            )

    def get_stats(self) -> dict[str, Any]:
        """Get tokenizer statistics."""
        return {
            "model": self._model_name,
            "max_length": self._max_length,
            "loaded": self._tokenizer is not None,
        }
