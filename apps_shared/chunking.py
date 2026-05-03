"""Token-aware chunker with overlap (plan §P3.2).

Splits text into chunks of up to ``chunk_tokens`` with ``overlap_tokens``
of overlap between adjacent chunks. Uses ``tiktoken`` when available for
accurate GPT-style tokenization; falls back to whitespace splitting
otherwise. Whitespace fallback is NOT cryptographically accurate but is
sufficient for chunk-boundary determination and keeps offline test
runs independent of the ``tiktoken`` dep.
"""

from __future__ import annotations


def _encode_tiktoken(text: str) -> list[int]:
    import tiktoken

    enc = tiktoken.get_encoding("cl100k_base")
    return enc.encode(text)


def _decode_tiktoken(tokens: list[int]) -> str:
    import tiktoken

    enc = tiktoken.get_encoding("cl100k_base")
    return enc.decode(tokens)


def _tiktoken_available() -> bool:
    try:
        import tiktoken  # noqa: F401

        return True
    except ImportError:
        return False


def chunk_text(
    text: str,
    chunk_tokens: int = 512,
    overlap_tokens: int = 50,
) -> list[str]:
    """Split ``text`` into overlapping chunks.

    Args:
        text: source text.
        chunk_tokens: maximum tokens per chunk (default 512).
        overlap_tokens: overlap between adjacent chunks (default 50).

    Returns:
        List of chunk strings. Empty input → empty list.

    Raises:
        ValueError: if ``chunk_tokens <= overlap_tokens`` or either is
            non-positive.
    """
    if chunk_tokens <= 0 or overlap_tokens < 0:
        raise ValueError("chunk_tokens must be > 0 and overlap_tokens >= 0")
    if chunk_tokens <= overlap_tokens:
        raise ValueError("chunk_tokens must be > overlap_tokens")
    if not text:
        return []

    if _tiktoken_available():
        tokens = _encode_tiktoken(text)
        if len(tokens) <= chunk_tokens:
            return [text]
        stride = chunk_tokens - overlap_tokens
        chunks: list[str] = []
        i = 0
        while i < len(tokens):
            window = tokens[i : i + chunk_tokens]
            chunks.append(_decode_tiktoken(window))
            if i + chunk_tokens >= len(tokens):
                break
            i += stride
        return chunks

    # Whitespace fallback: treat each whitespace-separated word as one token.
    words = text.split()
    if len(words) <= chunk_tokens:
        return [text]
    stride = chunk_tokens - overlap_tokens
    chunks = []
    i = 0
    while i < len(words):
        window = words[i : i + chunk_tokens]
        chunks.append(" ".join(window))
        if i + chunk_tokens >= len(words):
            break
        i += stride
    return chunks
