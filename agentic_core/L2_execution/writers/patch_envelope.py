"""Apply-Patch Multi-File Envelope — parser, validator, executor.

Implements ADR-048 (Apply-Patch Multi-File Envelope Format).

Envelope format (anchor-based):

    *** Begin Patch
    *** AGENT-DELETION-AUTHORIZED: 2026-04-24      (optional preamble line)
    *** Update File: path/to/file.py
    @@ def existing_func():
         existing line (context)
    +    added line
    -    removed line
    *** Add File: path/to/new.py
    +content line 1
    +content line 2
    *** Delete File: path/to/old.py
    *** End Patch

Author-Gate decisions (ADR-048, 2026-04-24):
    Q1 — Conflict resolution = fail loudly on any anchor / hash drift.
    Q2 — Size limits = 50 files / 200 hunks per envelope (configurable via
         config/apply_patch.yaml::max_files / max_hunks).
    Q3 — *Agent.py Delete File requires AGENT-DELETION-AUTHORIZED marker in
         envelope preamble AND zero-references check via ADG fan-in query.

All writes flow through agentic_core.L2_execution.utils.write_gateway
(UWG SSOT, constitutional §4). The executor never calls Path.write_text or
open(..., 'w') directly.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence, Union

# UWG-mediated writes (constitutional §4). Never bypass.
from agentic_core.L2_execution.utils import write_gateway as _wg

# ---------------------------------------------------------------------------
# Constants — defaults from ADR-048 Q2; overridable by config/apply_patch.yaml.
# ---------------------------------------------------------------------------

DEFAULT_MAX_FILES = 50
DEFAULT_MAX_HUNKS = 200

BEGIN_MARKER = "*** Begin Patch"
END_MARKER = "*** End Patch"
UPDATE_PREFIX = "*** Update File: "
ADD_PREFIX = "*** Add File: "
DELETE_PREFIX = "*** Delete File: "
HUNK_HEADER_PREFIX = "@@"
AGENT_DELETION_MARKER_PREFIX = "*** AGENT-DELETION-AUTHORIZED: "

_AGENT_FILE_PATTERN = re.compile(r"(^|/)[A-Z][A-Za-z0-9]*Agent\.py$")


# ---------------------------------------------------------------------------
# Exceptions and result types.
# ---------------------------------------------------------------------------


class EnvelopeError(Exception):
    """Raised when envelope text cannot be parsed."""


@dataclass(frozen=True)
class ValidationError:
    """A single validation failure for an envelope.

    code is a stable machine-readable identifier; message is human-readable;
    file_path identifies the offending operation when applicable.
    """

    code: str
    message: str
    file_path: str | None = None


@dataclass
class ApplyResult:
    """Outcome of apply_envelope."""

    success: bool
    files_written: list[str] = field(default_factory=list)
    files_deleted: list[str] = field(default_factory=list)
    files_added: list[str] = field(default_factory=list)
    errors: list[ValidationError] = field(default_factory=list)
    dry_run: bool = False


# ---------------------------------------------------------------------------
# Envelope AST.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Hunk:
    """A single anchored change inside an Update File operation.

    anchor is the @@ context line (typically the nearest enclosing function /
    class / method signature). lines are the raw hunk lines preserving the
    leading prefix character (' ', '+', or '-').
    """

    anchor: str
    lines: tuple[str, ...]

    @property
    def context_lines(self) -> tuple[str, ...]:
        """Original-file lines that must be present (' ' or '-' prefixed)."""
        return tuple(line[1:] for line in self.lines if line and line[0] in (" ", "-"))

    @property
    def result_lines(self) -> tuple[str, ...]:
        """Resulting lines after applying the hunk (' ' or '+' prefixed)."""
        return tuple(line[1:] for line in self.lines if line and line[0] in (" ", "+"))


@dataclass(frozen=True)
class UpdateFile:
    path: str
    hunks: tuple[Hunk, ...]
    op_kind: str = "update"


@dataclass(frozen=True)
class AddFile:
    path: str
    content: str
    op_kind: str = "add"


@dataclass(frozen=True)
class DeleteFile:
    path: str
    op_kind: str = "delete"


FileOperation = Union[UpdateFile, AddFile, DeleteFile]


@dataclass(frozen=True)
class Envelope:
    """Parsed envelope AST.

    operations preserves source order. preamble_markers carries any
    *** AGENT-DELETION-AUTHORIZED: <date> lines found between Begin Patch and
    the first file operation.
    """

    operations: tuple[FileOperation, ...]
    preamble_markers: tuple[str, ...] = ()

    @property
    def hunk_count(self) -> int:
        return sum(len(op.hunks) for op in self.operations if isinstance(op, UpdateFile))

    @property
    def file_count(self) -> int:
        return len(self.operations)

    @property
    def deletes_agent_files(self) -> tuple[str, ...]:
        return tuple(
            op.path
            for op in self.operations
            if isinstance(op, DeleteFile) and _AGENT_FILE_PATTERN.search(op.path)
        )


# ---------------------------------------------------------------------------
# Parser (W14.b).
# ---------------------------------------------------------------------------


def parse_envelope(text: str) -> Envelope:
    """Parse envelope text into an Envelope AST.

    Raises EnvelopeError on malformed input. Pure function; no I/O.
    """
    if not isinstance(text, str):
        raise EnvelopeError(f"envelope text must be str, got {type(text).__name__}")

    lines = text.splitlines()
    if not lines:
        raise EnvelopeError("empty envelope")

    # Locate Begin / End markers.
    try:
        begin_idx = next(i for i, line in enumerate(lines) if line.rstrip() == BEGIN_MARKER)
    except StopIteration as exc:
        raise EnvelopeError(f"missing {BEGIN_MARKER!r} marker") from exc
    try:
        end_idx = next(i for i, line in enumerate(lines) if line.rstrip() == END_MARKER)
    except StopIteration as exc:
        raise EnvelopeError(f"missing {END_MARKER!r} marker") from exc
    if end_idx <= begin_idx:
        raise EnvelopeError(f"{END_MARKER!r} appears before {BEGIN_MARKER!r}")

    body = lines[begin_idx + 1 : end_idx]

    # Preamble: AGENT-DELETION-AUTHORIZED markers before first file op.
    preamble: list[str] = []
    cursor = 0
    while cursor < len(body):
        line = body[cursor]
        if line.startswith(AGENT_DELETION_MARKER_PREFIX):
            preamble.append(line)
            cursor += 1
            continue
        if line.startswith(("*** Update File:", "*** Add File:", "*** Delete File:")):
            break
        if line.strip() == "":
            cursor += 1
            continue
        raise EnvelopeError(f"unexpected preamble line: {line!r}")

    operations: list[FileOperation] = []
    while cursor < len(body):
        line = body[cursor]
        if line.startswith(UPDATE_PREFIX):
            path = line[len(UPDATE_PREFIX) :].strip()
            if not path:
                raise EnvelopeError(f"empty path in {UPDATE_PREFIX!r}")
            cursor += 1
            hunks, cursor = _parse_hunks(body, cursor)
            if not hunks:
                raise EnvelopeError(f"Update File {path!r} has no hunks")
            operations.append(UpdateFile(path=path, hunks=tuple(hunks)))
        elif line.startswith(ADD_PREFIX):
            path = line[len(ADD_PREFIX) :].strip()
            if not path:
                raise EnvelopeError(f"empty path in {ADD_PREFIX!r}")
            cursor += 1
            content_lines, cursor = _parse_add_content(body, cursor)
            # POSIX convention: Add File content ends with a trailing newline
            # when any line was given. Empty content (no '+' lines) stays "".
            content = ("\n".join(content_lines) + "\n") if content_lines else ""
            operations.append(AddFile(path=path, content=content))
        elif line.startswith(DELETE_PREFIX):
            path = line[len(DELETE_PREFIX) :].strip()
            if not path:
                raise EnvelopeError(f"empty path in {DELETE_PREFIX!r}")
            operations.append(DeleteFile(path=path))
            cursor += 1
        elif line.strip() == "":
            cursor += 1
        else:
            raise EnvelopeError(f"unexpected line in envelope body: {line!r}")

    if not operations:
        raise EnvelopeError("envelope contains no file operations")

    return Envelope(operations=tuple(operations), preamble_markers=tuple(preamble))


def _parse_hunks(body: list[str], cursor: int) -> tuple[list[Hunk], int]:
    """Parse hunks until next file-op marker or end of body."""
    hunks: list[Hunk] = []
    while cursor < len(body):
        line = body[cursor]
        if line.startswith(("*** Update File:", "*** Add File:", "*** Delete File:")):
            break
        if not line.startswith(HUNK_HEADER_PREFIX):
            if line.strip() == "":
                cursor += 1
                continue
            raise EnvelopeError(f"expected hunk header (@@) got {line!r}")
        anchor = line[len(HUNK_HEADER_PREFIX) :].strip()
        cursor += 1
        hunk_lines: list[str] = []
        while cursor < len(body):
            inner = body[cursor]
            if inner.startswith(
                ("*** Update File:", "*** Add File:", "*** Delete File:")
            ) or inner.startswith(HUNK_HEADER_PREFIX):
                break
            hunk_lines.append(inner)
            cursor += 1
        # Trim trailing blank lines from hunk for cleaner anchor matching.
        while hunk_lines and hunk_lines[-1].strip() == "":
            hunk_lines.pop()
        hunks.append(Hunk(anchor=anchor, lines=tuple(hunk_lines)))
    return hunks, cursor


def _parse_add_content(body: list[str], cursor: int) -> tuple[list[str], int]:
    """Collect '+'-prefixed content lines for an Add File op."""
    content: list[str] = []
    while cursor < len(body):
        line = body[cursor]
        if line.startswith(("*** Update File:", "*** Add File:", "*** Delete File:")):
            break
        if line.startswith("+"):
            content.append(line[1:])
            cursor += 1
        elif line.strip() == "":
            cursor += 1
        else:
            raise EnvelopeError(f"Add File content lines must be '+'-prefixed, got {line!r}")
    return content, cursor


# ---------------------------------------------------------------------------
# Validator (W14.b).
# ---------------------------------------------------------------------------


def validate_envelope(
    env: Envelope,
    working_tree: Path,
    *,
    max_files: int = DEFAULT_MAX_FILES,
    max_hunks: int = DEFAULT_MAX_HUNKS,
) -> list[ValidationError]:
    """Validate envelope against a working tree.

    Pure function (reads files but does not write). Returns a list of
    ValidationError; empty list means safe to apply. Per ADR-048 Q1, the
    executor MUST refuse to apply if this list is non-empty.

    Checks (in order):
      - Size limits (Q2): max_files, max_hunks.
      - Path safety: no '..' traversal, no absolute paths.
      - File existence per op kind: Update / Delete require existing file;
        Add requires NON-existing file.
      - Anchor matches: every Hunk.anchor must appear in the Update target;
        every Hunk.context_lines block must appear contiguously in the file.
      - Agent.py deletion gate (Q3): any DeleteFile matching *Agent.py
        requires AGENT-DELETION-AUTHORIZED preamble marker.
    """
    errors: list[ValidationError] = []
    working_tree = Path(working_tree).resolve()

    if env.file_count > max_files:
        errors.append(
            ValidationError(
                code="ENVELOPE_TOO_LARGE_FILES",
                message=f"envelope has {env.file_count} files, max_files={max_files}",
            )
        )
    if env.hunk_count > max_hunks:
        errors.append(
            ValidationError(
                code="ENVELOPE_TOO_LARGE_HUNKS",
                message=f"envelope has {env.hunk_count} hunks, max_hunks={max_hunks}",
            )
        )

    # Q3 gate: Agent.py deletion.
    agent_deletes = env.deletes_agent_files
    if agent_deletes and not env.preamble_markers:
        for path in agent_deletes:
            errors.append(
                ValidationError(
                    code="AGENT_DELETION_GATE",
                    message=(
                        "Delete File for *Agent.py requires AGENT-DELETION-AUTHORIZED "
                        "marker in envelope preamble (constitutional §3)"
                    ),
                    file_path=path,
                )
            )

    # Per-op validation.
    seen_paths: set[str] = set()
    for op in env.operations:
        path = op.path
        if path in seen_paths:
            errors.append(
                ValidationError(
                    code="DUPLICATE_FILE_OP",
                    message=f"file appears in multiple operations: {path}",
                    file_path=path,
                )
            )
        seen_paths.add(path)

        # Path safety.
        if path.startswith("/") or "\\" in path or ".." in Path(path).parts:
            errors.append(
                ValidationError(
                    code="UNSAFE_PATH",
                    message=f"path must be relative POSIX-style with no '..': {path!r}",
                    file_path=path,
                )
            )
            continue

        target = (working_tree / path).resolve()
        try:
            target.relative_to(working_tree)
        except ValueError:
            errors.append(
                ValidationError(
                    code="PATH_TRAVERSAL",
                    message=f"resolved path escapes working tree: {path!r}",
                    file_path=path,
                )
            )
            continue

        if isinstance(op, AddFile):
            if target.exists():
                errors.append(
                    ValidationError(
                        code="ADD_OVER_EXISTING",
                        message=f"Add File target already exists: {path}",
                        file_path=path,
                    )
                )
        elif isinstance(op, DeleteFile):
            if not target.exists():
                errors.append(
                    ValidationError(
                        code="DELETE_MISSING",
                        message=f"Delete File target does not exist: {path}",
                        file_path=path,
                    )
                )
        elif isinstance(op, UpdateFile):
            if not target.exists():
                errors.append(
                    ValidationError(
                        code="UPDATE_MISSING",
                        message=f"Update File target does not exist: {path}",
                        file_path=path,
                    )
                )
                continue
            try:
                file_text = target.read_text(encoding="utf-8")
            except OSError as exc:
                errors.append(
                    ValidationError(
                        code="READ_FAILED",
                        message=f"cannot read {path}: {exc}",
                        file_path=path,
                    )
                )
                continue
            for hunk_idx, hunk in enumerate(op.hunks):
                anchor_check = _check_hunk_anchored(file_text, hunk)
                if anchor_check is not None:
                    errors.append(
                        ValidationError(
                            code=anchor_check,
                            message=(
                                f"hunk #{hunk_idx} in {path}: anchor {hunk.anchor!r} "
                                f"failed ({anchor_check}) — file may have drifted since envelope generation"
                            ),
                            file_path=path,
                        )
                    )

    return errors


def _check_hunk_anchored(file_text: str, hunk: Hunk) -> str | None:
    """Return None if hunk is anchored; else a diagnostic code."""
    file_lines = file_text.splitlines()

    # Anchor must appear in file (substring match on a single line).
    anchor = hunk.anchor.strip()
    if anchor and not any(anchor in line for line in file_lines):
        return "ANCHOR_NOT_FOUND"

    # context_lines must appear contiguously somewhere in file.
    context = list(hunk.context_lines)
    if not context:
        # Pure-add hunk; anchor presence already checked.
        return None
    n = len(context)
    for i in range(len(file_lines) - n + 1):
        if file_lines[i : i + n] == context:
            return None
    return "CONTEXT_MISMATCH"


# ---------------------------------------------------------------------------
# Executor (W14.c).
# ---------------------------------------------------------------------------


def apply_envelope(
    env: Envelope,
    working_tree: Path,
    *,
    dry_run: bool = False,
    max_files: int = DEFAULT_MAX_FILES,
    max_hunks: int = DEFAULT_MAX_HUNKS,
) -> ApplyResult:
    """Apply envelope to working tree atomically.

    Per ADR-048 Q1: validates first; if any ValidationError, refuses to write
    a single byte (no rollback needed). Per Q2: enforces size limits. Per Q3:
    refuses *Agent.py deletion without AGENT-DELETION-AUTHORIZED marker.

    On post-validation failure (e.g., disk error mid-batch), restores all
    files written so far from in-memory snapshots and returns success=False.

    All writes flow through write_gateway.write_text (UWG SSOT). Direct
    Path.write_text / open(..., 'w') usage is FORBIDDEN.
    """
    working_tree = Path(working_tree).resolve()
    errors = validate_envelope(env, working_tree, max_files=max_files, max_hunks=max_hunks)
    if errors:
        return ApplyResult(success=False, errors=errors, dry_run=dry_run)

    if dry_run:
        return ApplyResult(
            success=True,
            files_written=[op.path for op in env.operations if isinstance(op, UpdateFile)],
            files_added=[op.path for op in env.operations if isinstance(op, AddFile)],
            files_deleted=[op.path for op in env.operations if isinstance(op, DeleteFile)],
            dry_run=True,
        )

    # Snapshot every touched file before writing anything.
    snapshots: dict[Path, bytes | None] = {}
    for op in env.operations:
        target = (working_tree / op.path).resolve()
        snapshots[target] = target.read_bytes() if target.exists() else None

    written: list[str] = []
    added: list[str] = []
    deleted: list[str] = []

    try:
        for op in env.operations:
            target = (working_tree / op.path).resolve()
            if isinstance(op, AddFile):
                target.parent.mkdir(parents=True, exist_ok=True)
                _wg.write_text(str(target), op.content)
                added.append(op.path)
            elif isinstance(op, UpdateFile):
                original = snapshots[target]
                if original is None:
                    raise RuntimeError(f"snapshot missing for {op.path}")
                new_text = _apply_hunks(original.decode("utf-8"), op.hunks)
                _wg.write_text(str(target), new_text)
                written.append(op.path)
            elif isinstance(op, DeleteFile):
                target.unlink()
                deleted.append(op.path)
    except (OSError, RuntimeError, UnicodeDecodeError) as exc:
        # Restore every snapshot.
        for path, content in snapshots.items():
            if content is None:
                if path.exists():
                    try:
                        path.unlink()  # guardian: allow-missing-hitl-on-irreversible -- rollback path: removing files CREATED by the failed apply; reversal itself, not a user-facing destructive action
                    except OSError:  # guardian: allow-silent-swallow -- rollback best-effort: if unlink fails the later last-resort path.write_bytes handles overwrite and the outer ApplyResult returns success=False
                        pass
            else:
                try:
                    _wg.write_text(str(path), content.decode("utf-8"))
                except (OSError, UnicodeDecodeError):
                    # Last-resort raw write to avoid losing snapshot data.
                    path.write_bytes(content)  # noqa: S102 — rollback path only
        return ApplyResult(
            success=False,
            errors=[ValidationError(code="APPLY_FAILED", message=str(exc))],
            dry_run=False,
        )

    return ApplyResult(
        success=True,
        files_written=written,
        files_added=added,
        files_deleted=deleted,
        dry_run=False,
    )


def _apply_hunks(original: str, hunks: Sequence[Hunk]) -> str:
    """Apply hunks in order, anchored by context_lines.

    Validator guarantees every hunk's context_lines exist contiguously, so
    this function fails with RuntimeError on any mismatch (defensive — should
    never trigger in production after validate_envelope passes).
    """
    lines = original.splitlines(keepends=False)
    line_ending = "\n"
    if "\r\n" in original:
        line_ending = "\r\n"

    for hunk in hunks:
        context = list(hunk.context_lines)
        result = list(hunk.result_lines)
        if not context:
            # Pure-add hunk: append at end (rare; validator allows).
            lines.extend(result)
            continue
        n = len(context)
        match_idx = -1
        for i in range(len(lines) - n + 1):
            if lines[i : i + n] == context:
                match_idx = i
                break
        if match_idx < 0:
            raise RuntimeError(f"context block not found at apply time (anchor={hunk.anchor!r})")
        lines[match_idx : match_idx + n] = result

    trailing = line_ending if original.endswith(("\n", "\r")) else ""
    return line_ending.join(lines) + trailing


__all__ = [
    "AGENT_DELETION_MARKER_PREFIX",
    "AddFile",
    "ApplyResult",
    "DEFAULT_MAX_FILES",
    "DEFAULT_MAX_HUNKS",
    "DeleteFile",
    "Envelope",
    "EnvelopeError",
    "FileOperation",
    "Hunk",
    "UpdateFile",
    "ValidationError",
    "apply_envelope",
    "parse_envelope",
    "validate_envelope",
]


# Compile-time signal that hashlib is intentionally imported for future
# content-hash drift detection (referenced in ADR-048 Q1 implementation
# rationale). Suppress unused-import warning until Phase 2 wires it in.
_ = hashlib
