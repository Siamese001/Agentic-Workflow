"""Base class + small result contract for document parsers.

All concrete parsers return a :class:`ParsedDocument` instance. Parsers
accept either ``bytes`` (already-read file contents) or ``pathlib.Path``
(parser reads the file). Parsers MUST be deterministic and MUST NOT raise
on well-formed input; malformed input raises :class:`DocumentParseError`.

Skeleton-stage scope: text-only content extraction + structured-field
extraction (JSON, CSV). Image-PDF OCR + prompt-injection defence are
deferred per plan ``apps-underwriting-feature-complete-aa79a7`` scope
boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class DocumentParseError(ValueError):
    """Raised when a parser cannot process its input.

    Distinct from :class:`FileNotFoundError` (caller's fault) and from
    :class:`ImportError` (optional dependency missing — parser raises
    its own subclass for that).
    """


class OptionalDependencyMissing(DocumentParseError):
    """Parser requires an optional dependency that is not installed."""


@dataclass(frozen=True)
class ParsedDocument:
    """Output contract shared by every concrete parser.

    Attributes:
        document_id: Stable identifier for the parsed document. Caller
            supplies this; parsers never fabricate one.
        parser_name: Short identifier of the parser that produced this
            result (e.g., ``"json"``, ``"csv"``, ``"pdf_text"``).
        text: Plain-text extraction (may be empty for non-text parsers).
        fields: Structured-field extraction (dict of scalar / list
            values; may be empty for text-only parsers).
        page_count: Best-effort page count (0 for single-page formats).
        notes: Parser-emitted diagnostic notes (never error messages —
            those raise :class:`DocumentParseError`).
    """

    document_id: str
    parser_name: str
    text: str = ""
    fields: dict[str, Any] = field(default_factory=dict)
    page_count: int = 0
    notes: tuple[str, ...] = field(default_factory=tuple)


class DocumentParser:
    """Abstract base: every parser implements :meth:`parse`.

    Subclasses set :attr:`name` (short identifier) and :attr:`extensions`
    (lowercase extensions with leading dot, e.g. ``(".json",)``). The
    parser registry dispatches by extension (see :func:`resolve_parser`).

    Concrete parsers MUST be stateless at the instance level — construct
    new parser objects per call rather than sharing mutable state.
    """

    name: str = ""
    extensions: tuple[str, ...] = ()

    def parse(
        self,
        source: bytes | Path,
        *,
        document_id: str,
    ) -> ParsedDocument:
        """Parse source into a :class:`ParsedDocument`.

        Args:
            source: File bytes or filesystem path.
            document_id: Caller-supplied stable identifier.

        Returns:
            A :class:`ParsedDocument`.

        Raises:
            DocumentParseError: source is malformed.
            OptionalDependencyMissing: required optional dep absent.
            FileNotFoundError: source is a Path that does not exist.
        """
        raise NotImplementedError("subclass must override parse()")

    def _read_bytes(self, source: bytes | Path) -> bytes:
        """Normalize source → bytes. Raises FileNotFoundError for Path."""
        if isinstance(source, (bytes, bytearray)):
            return bytes(source)
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"parser source not found: {path}")
        return path.read_bytes()


# -- Registry ----------------------------------------------------------------
# Populated by `apps_underwriting_ai.parsers.__init__` when concrete parsers
# are imported. Keeping the registry here (not in __init__) avoids a circular
# import between this module and concrete parsers.

_PARSER_REGISTRY: dict[str, DocumentParser] = {}


def register_parser(parser: DocumentParser) -> None:
    """Register a parser against each of its declared extensions.

    Later registrations override earlier ones for the same extension.
    """
    if not parser.name:
        raise ValueError("parser must declare a non-empty name")
    for ext in parser.extensions:
        if not ext.startswith("."):
            raise ValueError(f"extensions must start with '.', got {ext!r}")
        _PARSER_REGISTRY[ext.lower()] = parser


def resolve_parser(extension: str) -> DocumentParser | None:
    """Return a registered parser for an extension, or None."""
    return _PARSER_REGISTRY.get(extension.lower())


def registered_extensions() -> tuple[str, ...]:
    """Return the sorted tuple of all registered extensions."""
    return tuple(sorted(_PARSER_REGISTRY))
