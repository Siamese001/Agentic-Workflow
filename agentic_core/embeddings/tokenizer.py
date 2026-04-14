"""B1 Tokenizer Stage - Tokenization for embedding.

10C-REQ-100: Tokenizer load tokenize text to IDs attention mask padding truncation
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


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
    LOCAL_FILES_ONLY = os.environ.get("EMBEDDING_LOCAL_FILES_ONLY", "true").lower() == "true"

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or self.DEFAULT_MODEL
        self._max_length = self.DEFAULT_MAX_LENGTH
        self._tokenizer: Any | None = None

    def load(self) -> bool:
        """Load tokenizer from HuggingFace."""
        try:
            from transformers import AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(
                self._model_name,
                local_files_only=self.LOCAL_FILES_ONLY,
                trust_remote_code=False,
                use_fast=True,
            )
            return True
        except (ImportError, OSError, ValueError) as exc:
            self._tokenizer = None
            logger.warning("Falling back to whitespace tokenizer for %s: %s", self._model_name, exc)
            return False

    @staticmethod
    def _stable_token_id(token: str) -> int:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        return int.from_bytes(digest[:4], "big") % 50000

    def tokenize(
        self,
        text: str,
        max_length: int | None = None,
        truncation: bool = True,
        padding: bool = True,
    ) -> TokenizedOutput:
        """Tokenize text to IDs with attention mask."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        max_len = max_length or self._max_length
        if max_len <= 0:
            raise ValueError("max_length must be > 0")

        if self._tokenizer:
            original = self._tokenizer(
                text,
                truncation=False,
                padding=False,
                return_attention_mask=False,
            )
            result = self._tokenizer(
                text,
                max_length=max_len,
                truncation=truncation,
                padding="max_length" if padding else False,
                return_attention_mask=True,
            )
            token_count = int(sum(result["attention_mask"]))

            return TokenizedOutput(
                input_ids=result["input_ids"],
                attention_mask=result["attention_mask"],
                token_count=token_count,
                truncated=truncation and len(original["input_ids"]) > max_len,
                padded=padding and token_count < len(result["input_ids"]),
            )
        else:
            words = text.split()
            tokens = words[:max_len] if truncation else words
            token_count = len(tokens)

            input_ids = [self._stable_token_id(t) for t in tokens]

            if padding and len(input_ids) < max_len:
                input_ids.extend([0] * (max_len - len(input_ids)))
                attention_mask = [1] * token_count + [0] * (max_len - token_count)
            else:
                attention_mask = [1] * token_count

            return TokenizedOutput(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_count=token_count,
                truncated=truncation and len(words) > max_len,
                padded=padding and len(input_ids) < max_len,
            )

    def get_stats(self) -> dict[str, Any]:
        """Get tokenizer statistics."""
        return {
            "model": self._model_name,
            "max_length": self._max_length,
            "loaded": self._tokenizer is not None,
        }
