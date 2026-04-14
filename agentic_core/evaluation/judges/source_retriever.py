"""Source Retriever — reads source code at ADG-provided coordinates.

Bridges the gap between ADG edge metadata (file_path, line_no, symbol)
and actual source code content that an LLM judge needs for nuanced verdicts.

Usage::

    retriever = SourceRetriever("c:/Git/Agentic-Workflow")
    snippet = retriever.get_context("agentic_core/L2_execution/providers.py", 142, window=10)
    print(snippet.content)
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from agentic_core.evaluation.judges.types import SourceSnippet
from tqdm import tqdm

_log = logging.getLogger(__name__)

_DEFAULT_WINDOW = 10
_MAX_WINDOW = 100
_MAX_FILE_LINES = 50_000


class SourceRetriever:
    """Reads source code at ADG-provided file:line coordinates.

    All paths are resolved relative to ``repo_root``.
    Returns ``SourceSnippet`` instances with content and line range.
    """

    def __init__(self, repo_root: str) -> None:
        self._root = Path(repo_root)
        if not self._root.is_dir():
            raise ValueError(f"repo_root is not a directory: {repo_root}")

    def _resolve(self, file_path: str) -> Path:
        """Resolve a relative or absolute path to the repo root."""
        p = Path(file_path)
        if p.is_absolute():
            return p
        return self._root / p

    def _read_lines(self, path: Path) -> list[str] | None:
        """Read file lines, returning None on failure."""
        if not path.is_file():
            _log.warning("[SourceRetriever] File not found: %s", path)
            return None
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()
            if len(lines) > _MAX_FILE_LINES:
                _log.warning(
                    "[SourceRetriever] File too large (%d lines): %s",
                    len(lines),
                    path,
                )
                return None
            return lines
        # guardian: allow-silent-swallow - acceptable exception handling
        except OSError as exc:
            _log.warning("[SourceRetriever] Cannot read %s: %s", path, exc)
            return None

    def get_context(
        self,
        file_path: str,
        line_no: int,
        window: int = _DEFAULT_WINDOW,
    ) -> SourceSnippet | None:
        """Read source code around a specific file:line.

        Args:
            file_path: Relative or absolute path to the source file.
            line_no: 1-indexed line number (center of the window).
            window: Number of lines above and below to include.

        Returns:
            SourceSnippet or None if the file cannot be read.
        """
        window = min(max(window, 1), _MAX_WINDOW)
        path = self._resolve(file_path)
        lines = self._read_lines(path)
        if lines is None:
            return None

        total = len(lines)
        start = max(0, line_no - 1 - window)
        end = min(total, line_no + window)
        content = "\n".join(lines[start:end])

        return SourceSnippet(
            file_path=str(path.relative_to(self._root)) if path.is_relative_to(self._root) else str(path),
            start_line=start + 1,
            end_line=end,
            content=content,
        )

    def get_function(
        self,
        file_path: str,
        function_name: str,
    ) -> SourceSnippet | None:
        """Read the full body of a named function or method.

        Uses AST parsing to find the exact line range of the function.

        Args:
            file_path: Relative or absolute path to the source file.
            function_name: Name of the function/method to extract.

        Returns:
            SourceSnippet or None if not found.
        """
        path = self._resolve(file_path)
        lines = self._read_lines(path)
        if lines is None:
            return None

        source = "\n".join(lines)
        try:
            # guardian: allow-silent-swallow - acceptable exception handling
            tree = ast.parse(source, filename=str(path))
        except SyntaxError:
            _log.warning("[SourceRetriever] Syntax error parsing %s", path)
            return None

        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == function_name:
                    start = node.lineno - 1
                    end = node.end_lineno or (start + 1)
                    content = "\n".join(lines[start:end])
                    rel = str(path.relative_to(self._root)) if path.is_relative_to(self._root) else str(path)
                    return SourceSnippet(
                        file_path=rel,
                        start_line=start + 1,
                        end_line=end,
                        content=content,
                        symbol=function_name,
                    )

        _log.debug(
            "[SourceRetriever] Function '%s' not found in %s",
            function_name,
            path,
        )
        return None

    def get_class(
        self,
        file_path: str,
        class_name: str,
    ) -> SourceSnippet | None:
        """Read the full body of a named class.

        Args:
            file_path: Relative or absolute path to the source file.
            class_name: Name of the class to extract.

        Returns:
            SourceSnippet or None if not found.
        """
        path = self._resolve(file_path)
        lines = self._read_lines(path)
        if lines is None:
            return None

        source = "\n".join(lines)
        # guardian: allow-silent-swallow - acceptable exception handling
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError:
            _log.warning("[SourceRetriever] Syntax error parsing %s", path)
            return None

        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                start = node.lineno - 1
                end = node.end_lineno or (start + 1)
                content = "\n".join(lines[start:end])
                rel = str(path.relative_to(self._root)) if path.is_relative_to(self._root) else str(path)
                return SourceSnippet(
                    file_path=rel,
                    start_line=start + 1,
                    end_line=end,
                    content=content,
                    symbol=class_name,
                )

        _log.debug(
            "[SourceRetriever] Class '%s' not found in %s",
            class_name,
            path,
        )
        return None

    def get_lines(
        self,
        file_path: str,
        start_line: int,
        end_line: int,
    ) -> SourceSnippet | None:
        """Read an exact line range from a file.

        Args:
            file_path: Relative or absolute path.
            start_line: 1-indexed start line (inclusive).
            end_line: 1-indexed end line (inclusive).

        Returns:
            SourceSnippet or None if the file cannot be read.
        """
        path = self._resolve(file_path)
        lines = self._read_lines(path)
        if lines is None:
            return None

        total = len(lines)
        s = max(0, start_line - 1)
        e = min(total, end_line)
        content = "\n".join(lines[s:e])

        return SourceSnippet(
            file_path=str(path.relative_to(self._root)) if path.is_relative_to(self._root) else str(path),
            start_line=s + 1,
            end_line=e,
            content=content,
        )


__all__ = ["SourceRetriever"]
