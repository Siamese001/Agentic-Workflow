"""
Schemas Module - Canon Validator System

Facade module that wraps the existing CanonEntry implementation
to match the master prompt specifications.
"""

import ast
import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from schemas.canon_models import CanonEntry


class UnifiedSemanticElement:
    """
    The Unified Semantic Element containing Embedding, AST, and Meta-Learning Metadata.

    This facade class wraps CanonEntry to provide the exact interface specified
    in the master prompt while leveraging existing implementations.
    """

    def __init__(
        self,
        code_snippet: str,
        ast_structure: Dict[str, Any],
        embedding: List[float],
        metadata: Dict[str, Any],
        id: Optional[str] = None
    ):
        """Initialize the Unified Semantic Element."""
        self.id = id or str(uuid.uuid4())
        self.code_snippet = code_snippet
        self.ast_structure = ast_structure
        self.embedding = embedding
        self.metadata = metadata

        # Convert to CanonEntry for internal storage
        self._canon_entry = self._to_canon_entry()

    def _to_canon_entry(self) -> CanonEntry:
        """Convert to CanonEntry for storage in Redis/Qdrant."""
        # Generate AST hash
        ast_hash = hashlib.sha256(
            json.dumps(self.ast_structure, sort_keys=True).encode()
        ).hexdigest()

        return CanonEntry(
            id=self.id,
            vector=self.embedding,
            ast_json=self.ast_structure,
            ast_hash=ast_hash,
            policy_key=self.metadata.get("canon_rule_id", "unknown"),
            failure_count=self.metadata.get("failure_count", 0),
            success_count=self.metadata.get("success_count", 0),
            latency_ms=self.metadata.get("latency_ms", 0),
            project_tag=self.metadata.get("project_context", "default"),
            metadata={
                **self.metadata,
                "code_snippet": self.code_snippet,
                "last_validated": self.metadata.get("last_validated", datetime.utcnow().isoformat())
            }
        )

    @classmethod
    def from_canon_entry(cls, entry: CanonEntry) -> "UnifiedSemanticElement":
        """Create UnifiedSemanticElement from CanonEntry."""
        return cls(
            code_snippet=entry.metadata.get("code_snippet", ""),
            ast_structure=entry.ast_json,
            vector=entry.vector,
            metadata={
                "failure_count": entry.failure_count,
                "success_count": entry.success_count,
                "last_validated": entry.last_validated.isoformat(),
                "latency_ms": entry.latency_ms,
                "project_context": entry.project_tag,
                "canon_rule_id": entry.policy_key,
                **entry.metadata
            },
            id=str(entry.id)
        )

    def update_failure(self):
        """Increment failure count for meta-learning."""
        self.metadata["failure_count"] = self.metadata.get(
            "failure_count", 0) + 1
        self._canon_entry.update_failure()

    def update_success(self, latency_ms: Optional[int] = None):
        """Increment success count for meta-learning."""
        self.metadata["success_count"] = self.metadata.get(
            "success_count", 0) + 1
        if latency_ms:
            self.metadata["latency_ms"] = latency_ms
        self._canon_entry.update_success(0, latency_ms or 0)

    def get_success_rate(self) -> float:
        """Calculate success rate for this pattern."""
        total = self.metadata.get("failure_count", 0) + \
            self.metadata.get("success_count", 0)
        if total == 0:
            return 0.0
        return self.metadata.get("success_count", 0) / total


# Alias for backward compatibility with prompt naming
CanonEntry = UnifiedSemanticElement


def generate_ast_structure(code_str: str) -> Dict[str, Any]:
    """
    Generate AST structure from Python code string.

    Args:
        code_str: Python code to parse

    Returns:
        AST structure as dictionary

    Raises:
        SyntaxError: If code is invalid Python
    """
    try:
        tree = ast.parse(code_str)
        return ast.dump(tree, include_attributes=True)
    except SyntaxError as e:
# Return error structure for invalid code
        return {
            "error": str(e),
            "type": "SyntaxError",
            "line": e.lineno,
            "offset": e.offset
        }


def validate_ast_integrity(ast_structure: Dict[str, Any]) -> bool:
    """
    Validate that AST structure is intact and parseable.

    Args:
        ast_structure: AST dictionary to validate

    Returns:
        True if AST is valid, False otherwise
    """
    if isinstance(ast_structure, dict) and "error" in ast_structure:
        return False

    try:
        # Try to reconstruct and parse
        if isinstance(ast_structure, str):
            ast.parse(ast_structure)
        return True
    except Exception:
    return False

