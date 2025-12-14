"""
Schemas Module - Connectivity-Hardened Canon Validator

Pydantic models for the Unified Semantic Element containing
embedding vectors, AST structures, and meta-learning metadata.
"""

import ast
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class CanonMetadata(BaseModel):
    """Metadata for Canon entries."""
    failure_count: int = Field(default=0, ge=0, description="Number of failures for this pattern")
    success_count: int = Field(default=0, ge=0, description="Number of successes for this pattern")
    last_validated: datetime = Field(default_factory=datetime.utcnow, description="Last validation timestamp")
    project_context: str = Field(default="default", description="Project or context identifier")
    canon_rule_id: str = Field(default="unknown", description="Canon rule identifier")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.failure_count + self.success_count
        return self.success_count / total if total > 0 else 0.0
    
    @property
    def is_golden_pattern(self) -> bool:
        """Check if this is a golden pattern (high success)."""
        return self.success_count >= 10 and self.success_rate > 0.8


class CanonEntry(BaseModel):
    """
    The Unified Semantic Element.
    
    Contains embedding vector, AST structure, and meta-learning metadata
    in a single retrieval unit for the hybrid semantic cache.
    """
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    code_snippet: str = Field(..., description="The raw code snippet")
    ast_structure: Dict[str, Any] = Field(..., description="JSON-serialized AST structure")
    embedding: List[float] = Field(..., min_items=768, max_items=768, description="768-dimensional embedding vector")
    metadata: CanonMetadata = Field(..., description="Meta-learning metadata")
    
    @validator('ast_structure')
    def validate_ast_structure(cls, v):
        """Validate AST structure is valid."""
        if isinstance(v, dict) and "error" in v:
            raise ValueError(f"Invalid AST: {v['error']}")
        return v
    
    @validator('embedding')
    def validate_embedding(cls, v):
        """Validate embedding dimensions."""
        if len(v) != 768:
            raise ValueError(f"Embedding must have 768 dimensions, got {len(v)}")
        return v
    
    def to_redis_fields(self) -> Dict[str, Any]:
        """
        Convert to Redis field format for redisvl.
        
        Returns:
            Dictionary with flattened fields for Redis storage
        """
        return {
            "id": str(self.id),
            "code_snippet": self.code_snippet,
            "ast_structure": json.dumps(self.ast_structure),
            "embedding": self.embedding,
            "failure_count": self.metadata.failure_count,
            "success_count": self.metadata.success_count,
            "last_validated": self.metadata.last_validated.isoformat(),
            "project_context": self.metadata.project_context,
            "canon_rule_id": self.metadata.canon_rule_id,
            "success_rate": self.metadata.success_rate,
            "is_golden": self.metadata.is_golden_pattern
        }
    
    @classmethod
    def from_redis_fields(cls, fields: Dict[str, Any]) -> "CanonEntry":
        """
        Create CanonEntry from Redis fields.
        
        Args:
            fields: Dictionary from Redis
            
        Returns:
            CanonEntry instance
        """
        metadata = CanonMetadata(
            failure_count=fields.get("failure_count", 0),
            success_count=fields.get("success_count", 0),
            last_validated=datetime.fromisoformat(fields.get("last_validated")),
            project_context=fields.get("project_context", "default"),
            canon_rule_id=fields.get("canon_rule_id", "unknown")
        )
        
        return cls(
            id=UUID(fields["id"]),
            code_snippet=fields["code_snippet"],
            ast_structure=json.loads(fields["ast_structure"]),
            embedding=fields["embedding"],
            metadata=metadata
        )
    
    def to_pinecone_vector(self) -> Dict[str, Any]:
        """
        Convert to Pinecone vector format.
        
        Returns:
            Dictionary for Pinecone upsert
        """
        return {
            "id": str(self.id),
            "values": self.embedding,
            "metadata": {
                "code_snippet": self.code_snippet,
                "ast_structure": json.dumps(self.ast_structure),
                "failure_count": self.metadata.failure_count,
                "success_count": self.metadata.success_count,
                "last_validated": self.metadata.last_validated.isoformat(),
                "project_context": self.metadata.project_context,
                "canon_rule_id": self.metadata.canon_rule_id,
                "success_rate": self.metadata.success_rate,
                "is_golden": self.metadata.is_golden_pattern
            }
        }
    
    def update_failure(self):
        """Increment failure count."""
        self.metadata.failure_count += 1
        self.metadata.last_validated = datetime.utcnow()
    
    def update_success(self):
        """Increment success count."""
        self.metadata.success_count += 1
        self.metadata.last_validated = datetime.utcnow()
    
    def get_ast_hash(self) -> str:
        """Generate hash of AST structure."""
        ast_str = json.dumps(self.ast_structure, sort_keys=True)
        return hashlib.sha256(ast_str.encode()).hexdigest()[:16]


class QueryResult(BaseModel):
    """Result from a semantic search query."""
    id: str
    score: float
    entry: CanonEntry
    source: str  # "redis" or "pinecone"


class CanonQuery(BaseModel):
    """Query for Canon search."""
    text: str = Field(..., description="Query text")
    filter_failures: bool = Field(default=True, description="Filter out high-failure patterns")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum results")
    threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold")
    project_context: Optional[str] = Field(default=None, description="Filter by project")


def generate_ast_structure(code_str: str) -> Dict[str, Any]:
    """
    Generate AST structure from Python code.
    
    Args:
        code_str: Python code string
        
    Returns:
        AST structure as dictionary
    """
    try:
        tree = ast.parse(code_str)
        return {
            "type": "Module",
            "body": ast.dump(tree, include_attributes=True),
            "valid": True
        }
    except SyntaxError as e:
        return {
            "type": "Error",
            "error": str(e),
            "line": e.lineno,
            "offset": e.offset,
            "valid": False
        }


def validate_ast_integrity(ast_structure: Dict[str, Any]) -> bool:
    """
    Validate AST structure integrity.
    
    Args:
        ast_structure: AST dictionary
        
    Returns:
        True if valid
    """
    return ast_structure.get("valid", False)
