"""chunk_apps_rg_corpus.py — apps_rg corpus chunker.

Converts PDF/DOCX/YAML/JSON/MD source files to a .jsonl file suitable for
ingestion into ChromaDB via chroma_ingest_pipeline.py.

Each output line is a JSON object with:
  - "id": sha256 of text[:200]  (unique; duplicate → ChunkValidationError)
  - "text": chunk text           (empty string → ChunkValidationError)
  - "metadata": dict with all 8 required fields

Required metadata fields (all must be present and non-empty except citation_anchor):
  source_id        file_path:chunk_index
  source_class     one of SOURCE_CLASS_VOCAB
  authority_class  one of AUTHORITY_CLASS_VOCAB
  freshness        ISO8601 string (defaults to file mtime or --freshness arg)
  citation_anchor  readable cite key (empty → WARNING + exclusion-list entry)
  chunk_digest     sha256 of full chunk text
  app              hard-coded "apps_rg"
  ACL              one of ACL_VOCAB

Safety invariants:
  - candidate_profile source_class requires a PII scrub receipt at
    artifacts/apps_rg/retrieval/pii_scrub_receipts/candidate_profile.json
    before any chunk is written.  Absence → PIIScrubReceiptMissingError.
  - Validation runs over the FULL output set before any file is written.
    Failure → no partial output.
  - --execute is never issued by this script (pure read + write .jsonl only).

Usage::

    python tools/ingestion/chunk_apps_rg_corpus.py \\
        --source-class governance_docs \\
        --input-dir .cursor/rules \\
        --output artifacts/apps_rg/retrieval/ingestion_input/governance_docs.jsonl

    python tools/ingestion/chunk_apps_rg_corpus.py \\
        --input-jsonl artifacts/apps_rg/retrieval/ingestion_input/governance_docs.jsonl \\
        --validate-only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Vocabulary constants (fail-closed validation)
# ---------------------------------------------------------------------------

SOURCE_CLASS_VOCAB: frozenset[str] = frozenset({
    "candidate_profile",
    "project_evidence",
    "approved_examples",
    "rubrics",
    "governance_docs",
    "receipts",
    "prior_outputs",
})

ACL_VOCAB: frozenset[str] = frozenset({
    "apps_rg:private",
    "apps_rg:shared",
})

AUTHORITY_CLASS_VOCAB: frozenset[str] = frozenset({
    "PRIMARY",
    "SUPPORTING",
    "REFERENCE",
    "UNVETTED",
})

# Default ACL and authority_class per source_class
_DEFAULT_ACL: dict[str, str] = {
    "candidate_profile": "apps_rg:private",
    "project_evidence": "apps_rg:private",
    "approved_examples": "apps_rg:shared",
    "rubrics": "apps_rg:shared",
    "governance_docs": "apps_rg:shared",
    "receipts": "apps_rg:shared",
    "prior_outputs": "apps_rg:private",
}

_DEFAULT_AUTHORITY: dict[str, str] = {
    "candidate_profile": "PRIMARY",
    "project_evidence": "PRIMARY",
    "approved_examples": "SUPPORTING",
    "rubrics": "REFERENCE",
    "governance_docs": "REFERENCE",
    "receipts": "SUPPORTING",
    "prior_outputs": "UNVETTED",
}

PII_SCRUB_RECEIPT_PATH = Path(
    "artifacts/apps_rg/retrieval/pii_scrub_receipts/candidate_profile.json"
)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class ChunkValidationError(ValueError):
    """Raised when a chunk fails validation (fail-closed)."""


class PIIScrubReceiptMissingError(RuntimeError):
    """Raised when candidate_profile is processed without a PII scrub receipt."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _id_for_chunk(text: str, source_id: str = "", source_class: str = "") -> str:
    """Stable id = sha256 of source_class + source_id + text[:200].

    Including source_class prevents cross-corpus id collisions when the same
    source file is indexed under multiple corpora (e.g. rubrics and project_evidence
    both chunking domain_contract YAML files).
    """
    return _sha256(f"{source_class}\x00{source_id}\x00{text[:200]}")


def _chunk_digest(text: str) -> str:
    return _sha256(text)


def _file_freshness(path: Path) -> str:
    """Return ISO8601 UTC mtime for the file, or now() if unavailable."""
    try:
        mtime = path.stat().st_mtime
        return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
    except OSError:
        return datetime.now(timezone.utc).isoformat()


def _citation_anchor(source_class: str, file_path: Path, chunk_index: int) -> str:
    """Generate a readable citation anchor from source_class + file stem + index."""
    stem = file_path.stem.replace("_", "-").replace(" ", "-")
    return f"{source_class}:{stem}:chunk{chunk_index}"


def _split_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping character-level chunks.

    Uses double-newline paragraph boundaries when available, otherwise
    falls back to character sliding window.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            # Para itself may be longer than chunk_size — split by chars
            if len(para) > chunk_size:
                for i in range(0, len(para), chunk_size - overlap):
                    piece = para[i : i + chunk_size]
                    if piece.strip():
                        chunks.append(piece.strip())
            else:
                current = para
    if current:
        chunks.append(current)
    return chunks or [""]


def _read_text(path: Path) -> str:
    """Read text from .txt, .md, .py, .yaml, .yml, .json, .jsonl files.

    PDF and DOCX require optional dependencies; absence produces a clear
    error rather than silent empty text.
    """
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".py", ".yaml", ".yml", ".json", ".jsonl",
                  ".rst", ".toml", ".cfg", ".ini"}:
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        try:
            import pypdf  # type: ignore[import]
            reader = pypdf.PdfReader(str(path))
            return "\n\n".join(
                page.extract_text() or "" for page in reader.pages
            )
        except ImportError:
            raise ImportError(
                f"PDF extraction requires pypdf: pip install pypdf\n"
                f"  File: {path}"
            )
    if suffix in {".docx", ".doc"}:
        try:
            import docx  # type: ignore[import]
            doc = docx.Document(str(path))
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            raise ImportError(
                f"DOCX extraction requires python-docx: pip install python-docx\n"
                f"  File: {path}"
            )
    # Fallback: try UTF-8 text read for unknown extensions
    _log.warning("Unknown file extension %s — attempting UTF-8 text read", suffix)
    return path.read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Core chunking
# ---------------------------------------------------------------------------


def chunk_file(
    file_path: Path,
    source_class: str,
    acl: str,
    authority_class: str,
    freshness_override: str | None = None,
    chunk_size: int = 800,
    overlap: int = 100,
) -> list[dict[str, Any]]:
    """Chunk a single file into a list of chunk dicts.

    Args:
        file_path: Path to the source file.
        source_class: One of SOURCE_CLASS_VOCAB.
        acl: One of ACL_VOCAB.
        authority_class: One of AUTHORITY_CLASS_VOCAB.
        freshness_override: ISO8601 string; if None, derived from file mtime.
        chunk_size: Target character length per chunk.
        overlap: Character overlap between consecutive chunks.

    Returns:
        List of chunk dicts ready for validation and JSONL writing.
    """
    text = _read_text(file_path)
    pieces = _split_text(text, chunk_size=chunk_size, overlap=overlap)
    freshness = freshness_override or _file_freshness(file_path)
    chunks = []
    for i, piece in enumerate(pieces):
        if not piece.strip():
            continue
        chunk_text = piece.strip()
        source_id = f"{file_path}:{i}"
        chunk_id = _id_for_chunk(chunk_text, source_id, source_class)
        anchor = _citation_anchor(source_class, file_path, i)
        meta: dict[str, Any] = {
            "source_id": source_id,
            "source_class": source_class,
            "authority_class": authority_class,
            "freshness": freshness,
            "citation_anchor": anchor,
            "chunk_digest": _chunk_digest(chunk_text),
            "app": "apps_rg",
            "ACL": acl,
        }
        # Negative control #2: prior_outputs are never normative evidence.
        # Flag is set here so the C0 binding can route them to excluded_evidence_refs.
        if source_class == "prior_outputs":
            meta["invalid_for_normative_use"] = True
        chunks.append({"id": chunk_id, "text": chunk_text, "metadata": meta})
    return chunks


def chunk_directory(
    input_dir: Path,
    source_class: str,
    acl: str,
    authority_class: str,
    freshness_override: str | None = None,
    chunk_size: int = 800,
    overlap: int = 100,
    extensions: list[str] | None = None,
    max_files: int | None = None,
) -> list[dict[str, Any]]:
    """Walk input_dir and chunk all matching files.

    Args:
        input_dir: Directory to walk recursively.
        source_class: Applied to all chunks.
        acl: Applied to all chunks.
        authority_class: Applied to all chunks.
        freshness_override: Applied to all chunks if set.
        chunk_size: Target character length per chunk.
        overlap: Overlap between chunks.
        extensions: File suffixes to include (e.g. [".md", ".yaml"]).
                    None → include all readable files.
        max_files: Cap on number of files to process (for large dirs).

    Returns:
        Flat list of all chunks from all files.
    """
    _SKIP_DIRS = {".git", "__pycache__", "node_modules", "xet",
                  "docs/archive/windsurf/legacy-tree/plans", ".cursor/schemas",
                  "artifacts/apps_rg/runs", "artifacts/adg",
                  "artifacts/cursor"}
    all_chunks: list[dict[str, Any]] = []
    files: list[Path] = []
    for p in sorted(input_dir.rglob("*")):
        # Skip directories that would produce noise
        if any(skip in str(p) for skip in _SKIP_DIRS):
            continue
        if not p.is_file():
            continue
        if extensions and p.suffix.lower() not in extensions:
            continue
        files.append(p)
    if max_files:
        files = files[:max_files]
    for fp in files:
        try:
            chunks = chunk_file(
                fp, source_class, acl, authority_class,
                freshness_override, chunk_size, overlap,
            )
            all_chunks.extend(chunks)
        except (ImportError, OSError) as exc:
            _log.warning("Skipping %s: %s", fp, exc)
    return all_chunks


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

REQUIRED_METADATA_FIELDS: tuple[str, ...] = (
    "source_id", "source_class", "authority_class", "freshness",
    "citation_anchor", "chunk_digest", "app", "ACL",
)


def validate_chunks(chunks: list[dict[str, Any]]) -> list[str]:
    """Validate all chunks.  Returns list of exclusion-list ids (empty citation_anchor).

    Raises:
        ChunkValidationError: on any hard violation (fail-closed).
    """
    seen_ids: set[str] = set()
    exclusion_list: list[str] = []

    for i, chunk in enumerate(chunks):
        chunk_id = chunk.get("id")
        text = chunk.get("text", "")
        meta = chunk.get("metadata", {})

        # 1. id present
        if not chunk_id:
            raise ChunkValidationError(
                f"Chunk {i}: missing 'id' field"
            )

        # 2. text non-empty
        if not text or not text.strip():
            raise ChunkValidationError(
                f"Chunk {i} (id={chunk_id}): 'text' is empty"
            )

        # 3. all 8 metadata fields present
        for field in REQUIRED_METADATA_FIELDS:
            if field not in meta:
                raise ChunkValidationError(
                    f"Chunk {i} (id={chunk_id}): missing metadata field '{field}'"
                )

        # 4. duplicate ids
        if chunk_id in seen_ids:
            raise ChunkValidationError(
                f"Chunk {i}: duplicate id='{chunk_id}' — text prefix may be identical"
            )
        seen_ids.add(chunk_id)

        # 5. source_class vocab
        sc = meta.get("source_class", "")
        if sc not in SOURCE_CLASS_VOCAB:
            raise ChunkValidationError(
                f"Chunk {i} (id={chunk_id}): source_class='{sc}' not in SOURCE_CLASS_VOCAB "
                f"{sorted(SOURCE_CLASS_VOCAB)}"
            )

        # 6. ACL vocab
        acl = meta.get("ACL", "")
        if acl not in ACL_VOCAB:
            raise ChunkValidationError(
                f"Chunk {i} (id={chunk_id}): ACL='{acl}' not in ACL_VOCAB {sorted(ACL_VOCAB)}"
            )

        # 7. authority_class vocab
        ac = meta.get("authority_class", "")
        if ac not in AUTHORITY_CLASS_VOCAB:
            raise ChunkValidationError(
                f"Chunk {i} (id={chunk_id}): authority_class='{ac}' not in "
                f"AUTHORITY_CLASS_VOCAB {sorted(AUTHORITY_CLASS_VOCAB)}"
            )

        # 8. citation_anchor — WARNING only, adds to exclusion list
        if not meta.get("citation_anchor", "").strip():
            _log.warning(
                "Chunk %d (id=%s): citation_anchor is empty — added to exclusion list",
                i, chunk_id,
            )
            exclusion_list.append(chunk_id)

    return exclusion_list


def check_pii_receipt(repo_root: Path) -> None:
    """Raise PIIScrubReceiptMissingError if PII scrub receipt is absent."""
    receipt_path = repo_root / PII_SCRUB_RECEIPT_PATH
    if not receipt_path.exists():
        raise PIIScrubReceiptMissingError(
            f"candidate_profile requires a PII scrub receipt before chunking.\n"
            f"Expected: {receipt_path}\n"
            f"Create the receipt confirming PII scrub is complete, then re-run."
        )


# ---------------------------------------------------------------------------
# JSONL writer
# ---------------------------------------------------------------------------


def write_jsonl(chunks: list[dict[str, Any]], output_path: Path) -> None:
    """Write chunks to a .jsonl file (one JSON object per line)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        for chunk in chunks:
            fh.write(json.dumps(chunk, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chunk_apps_rg_corpus",
        description=(
            "Chunk apps_rg source corpora into .jsonl for ChromaDB ingestion. "
            "Enforces fail-closed validation on all 8 required metadata fields."
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--input-dir",
        type=Path,
        help="Directory to walk and chunk. Requires --source-class and --output.",
    )
    mode.add_argument(
        "--input-file",
        type=Path,
        help="Single file to chunk. Requires --source-class and --output.",
    )
    mode.add_argument(
        "--input-jsonl",
        type=Path,
        help="Existing .jsonl to validate only (use with --validate-only).",
    )

    parser.add_argument(
        "--source-class",
        choices=sorted(SOURCE_CLASS_VOCAB),
        help="Source class for all chunks.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output .jsonl path.",
    )
    parser.add_argument(
        "--acl",
        default=None,
        help="ACL override. Defaults to source_class default.",
    )
    parser.add_argument(
        "--authority-class",
        default=None,
        help="authority_class override. Defaults to source_class default.",
    )
    parser.add_argument(
        "--freshness",
        default=None,
        help="ISO8601 freshness override. Defaults to file mtime.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=800,
        help="Target character length per chunk (default: 800).",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=100,
        help="Character overlap between chunks (default: 100).",
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=None,
        help="File extensions to include (e.g. .md .yaml). None = all readable.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Cap on number of files to process.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        default=False,
        help="Only validate an existing .jsonl (use with --input-jsonl). No write.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repo root for locating PII scrub receipt (default: current dir).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = build_parser()
    args = parser.parse_args(argv)

    # ── validate-only mode ──────────────────────────────────────────────────
    if args.validate_only:
        if args.input_jsonl is None:
            print("ERROR: --validate-only requires --input-jsonl", file=sys.stderr)
            return 2
        if not args.input_jsonl.exists():
            print(f"ERROR: file not found: {args.input_jsonl}", file=sys.stderr)
            return 2
        chunks: list[dict[str, Any]] = []
        with args.input_jsonl.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    chunks.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    print(f"ERROR: malformed JSON on line {lineno}: {exc}", file=sys.stderr)
                    return 1
        try:
            exclusions = validate_chunks(chunks)
        except ChunkValidationError as exc:
            print(f"VALIDATION ERROR: {exc}", file=sys.stderr)
            return 1
        print(f"[validate-only] {len(chunks)} chunks — PASS")
        if exclusions:
            print(f"[validate-only] {len(exclusions)} chunks with empty citation_anchor "
                  f"(exclusion list): {exclusions[:5]}{'...' if len(exclusions) > 5 else ''}")
        return 0

    # ── chunking mode ────────────────────────────────────────────────────────
    if args.source_class is None:
        print("ERROR: --source-class is required when chunking", file=sys.stderr)
        return 2
    if args.output is None:
        print("ERROR: --output is required when chunking", file=sys.stderr)
        return 2

    source_class = args.source_class
    acl = args.acl or _DEFAULT_ACL.get(source_class, "apps_rg:shared")
    authority_class = args.authority_class or _DEFAULT_AUTHORITY.get(source_class, "REFERENCE")
    freshness = args.freshness

    # PII receipt gate — must check before any file read
    if source_class == "candidate_profile":
        try:
            check_pii_receipt(args.repo_root)
        except PIIScrubReceiptMissingError as exc:
            print(f"PII RECEIPT ERROR: {exc}", file=sys.stderr)
            return 3

    # Chunk
    chunks = []
    if args.input_dir is not None:
        if not args.input_dir.exists():
            print(f"ERROR: --input-dir does not exist: {args.input_dir}", file=sys.stderr)
            return 2
        chunks = chunk_directory(
            input_dir=args.input_dir,
            source_class=source_class,
            acl=acl,
            authority_class=authority_class,
            freshness_override=freshness,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            extensions=args.extensions,
            max_files=args.max_files,
        )
    elif args.input_file is not None:
        if not args.input_file.exists():
            print(f"ERROR: --input-file does not exist: {args.input_file}", file=sys.stderr)
            return 2
        chunks = chunk_file(
            file_path=args.input_file,
            source_class=source_class,
            acl=acl,
            authority_class=authority_class,
            freshness_override=freshness,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
        )

    if not chunks:
        print("WARNING: no chunks produced — check source files and extensions", file=sys.stderr)

    # Validate (fail-closed over full set before any write)
    try:
        exclusions = validate_chunks(chunks)
    except ChunkValidationError as exc:
        print(f"VALIDATION ERROR: {exc}", file=sys.stderr)
        return 1

    # Write
    write_jsonl(chunks, args.output)
    print(
        f"[chunk_apps_rg_corpus] wrote {len(chunks)} chunks to {args.output} "
        f"(source_class={source_class}, exclusions={len(exclusions)})"
    )
    if exclusions:
        print(f"  WARNING: {len(exclusions)} chunks with empty citation_anchor — "
              f"will be added to excluded_evidence_refs at retrieval time")
    return 0


if __name__ == "__main__":
    sys.exit(main())
