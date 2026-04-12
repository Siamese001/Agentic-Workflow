"""Code Deduplication Utility - Deterministic duplicate code detection.

This module provides deterministic code deduplication functionality previously
implemented in CodeDeduplicationAgent. Converted from agent to utility script
as part of SCRIPT agent conversion (Micro-wave 8).

Usage:
    from agentic_core.L5_safety.utils.code_deduplication_util import (
        CodeDuplicateDetector, DuplicateGroup, scan_for_duplicates
    )

    # Scan for duplicates
    detector = CodeDuplicateDetector(similarity_threshold=1.0)
    detector.scan_for_duplicates(["file1.py", "file2.py"])
"""

from __future__ import annotations

import ast
import difflib
import hashlib
import logging
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class DuplicateGroup:
    """Represents a group of duplicate code blocks."""

    group_id: str
    members: list[tuple[Path, str, int, str]]  # (file_path, name, line, code)
    hash_signature: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "group_id": self.group_id,
            "member_count": len(self.members),
            "members": [{"file": str(m[0]), "name": m[1], "line": m[2]} for m in self.members],
            "hash": self.hash_signature,
        }


@dataclass
class DedupResult:
    """Result of deduplication scan."""

    duplicate_groups: dict[str, DuplicateGroup] = field(default_factory=dict)
    total_files_scanned: int = 0
    total_blocks_found: int = 0
    duplicates_detected: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_files_scanned": self.total_files_scanned,
            "total_blocks_found": self.total_blocks_found,
            "duplicates_detected": self.duplicates_detected,
            "duplicate_groups": {k: v.to_dict() for k, v in self.duplicate_groups.items()},
        }


def _normalize_code(code: str) -> str:
    """Normalize for hashing: dedent, collapse whitespace, strip comments."""
    code = textwrap.dedent(code)
    lines = _filter_code_lines(code)
    return " ".join(lines.splitlines())


def _filter_code_lines(code: str) -> str:
    """Filter code lines by removing comments and empty lines."""
    lines = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped:
            lines.append(" ".join(stripped.split()))
    return "\n".join(lines)


def _normalize_ast_tree(node: ast.AST) -> str:
    """Anonymize variables and constants in AST for structural comparison."""
    if isinstance(node, ast.Name):
        return "VAR"
    elif isinstance(node, ast.Constant):
        return f"CONST_{type(node.value).__name__}"
    elif isinstance(node, ast.Num | ast.Str):
        return "CONST"
    children = [_normalize_ast_tree(child) for child in ast.iter_child_nodes(node)]
    return f"{type(node).__name__}({'|'.join(children)})"


def _hash_block(code: str, use_ast: bool = True) -> str:
    """Generate AST fingerprint for code block."""
    if use_ast:
        try:
            tree = ast.parse(code)
            norm_tree = _normalize_ast_tree(tree)
            return hashlib.sha256(str(norm_tree).encode()).hexdigest()
        except (SyntaxError, ValueError) as e:
            Logger.debug(f"AST parsing failed, using text normalization: {e}")

    normalized = _normalize_code(code)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _extract_functions_classes(file_path: Path, min_lines: int = 8) -> list[tuple[str, str, int]]:
    """Parse file and extract function/class bodies."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, UnicodeDecodeError, SyntaxError) as e:
        Logger.debug(f"Failed to extract blocks from {file_path.name}: {e}")
        return []

    blocks = []
    source_lines = source.splitlines()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            if node.end_lineno - node.lineno + 1 < min_lines:
                continue
            code_block = "\n".join(source_lines[node.lineno - 1 : node.end_lineno])
            blocks.append((node.name, code_block, node.lineno))
    return blocks


def _block_similarity(norm_a: str, norm_b: str) -> float:
    """Conservative structural/text similarity using difflib."""
    return difflib.SequenceMatcher(None, norm_a, norm_b).ratio()


class CodeDuplicateDetector:
    """Deterministic code duplicate detector."""

    def __init__(self, similarity_threshold: float = 1.0, min_lines: int = 8) -> None:
        """Initialize detector.

        Args:
            similarity_threshold: 1.0 = 100% identity required (SSOT compliance)
            min_lines: Minimum lines for duplicate detection
        """
        self.threshold = similarity_threshold
        self.min_lines = min_lines
        self.duplicate_groups: dict[str, DuplicateGroup] = {}
        self._reset_stats()

    def _reset_stats(self) -> None:
        """Reset detection statistics."""
        self.extracted_count = 0
        self.consolidated_count = 0
        self.errors: list[str] = []

    def scan_for_duplicates(self, python_files: list[str | Path]) -> DedupResult:
        """Scan for duplicate code blocks across files.

        Args:
            python_files: List of Python file paths to scan

        Returns:
            DedupResult with detected duplicate groups
        """
        self._reset_stats()
        result = DedupResult()
        result.total_files_scanned = len(python_files)

        # Collect candidates
        candidates: list[tuple[Path, str, int, str, str, int]] = []

        for file_str in python_files:
            file_path = Path(file_str)
            if not file_path.exists():
                self.errors.append(f"File not found: {file_path}")
                continue

            for name, code, line in _extract_functions_classes(file_path, self.min_lines):
                norm_str = ""
                try:
                    tree = ast.parse(code)
                    norm_str = _normalize_ast_tree(tree)
                except (SyntaxError, ValueError):
                    norm_str = _normalize_code(code)

                if not norm_str or len(code.splitlines()) < self.min_lines:
                    continue

                len_norm = len(norm_str)
                candidates.append((file_path, name, line, code, norm_str, len_norm))
                result.total_blocks_found += 1

        # Group by structural hash
        exact_groups: dict[str, list[tuple[Path, str, int, str, str, int]]] = {}
        for cand in candidates:
            struct_hash = hashlib.sha256(cand[4].encode("utf-8")).hexdigest()
            if struct_hash not in exact_groups:
                exact_groups[struct_hash] = []
            exact_groups[struct_hash].append(cand)

        # Create duplicate groups
        group_id = 0
        for struct_hash, mems in exact_groups.items():
            if len(mems) >= 2:
                members = [(t[0], t[1], t[2], t[3]) for t in mems]
                key = f"exact_group_{group_id}_{struct_hash[:8]}"
                self.duplicate_groups[key] = DuplicateGroup(
                    group_id=key,
                    members=members,
                    hash_signature=struct_hash,
                )
                group_id += 1

        result.duplicates_detected = len(self.duplicate_groups)
        result.duplicate_groups = self.duplicate_groups.copy()

        return result

    def get_duplicate_report(self) -> dict[str, Any]:
        """Get a human-readable report of duplicates."""
        if not self.duplicate_groups:
            return {"status": "ok", "message": "No significant code duplicates detected."}

        groups = []
        for group_id, group in self.duplicate_groups.items():
            groups.append(
                {
                    "group_id": group_id,
                    "copies": len(group.members),
                    "locations": [f"{m[0].name}:{m[2]} ({m[1]})" for m in group.members[:3]],
                }
            )

        return {
            "status": "duplicates_found",
            "total_groups": len(self.duplicate_groups),
            "groups": groups,
        }
