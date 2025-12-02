"""
Semantic Lineage Schema for Phase 0.5 Cache Rebuild

Provides core data structures for semantic caching across Resume Engine (RG) 
and Outreach Engine (LIC) archives with strict engine separation and zero-loss guarantee.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any
import hashlib
from datetime import datetime


class EngineType(Enum):
    """Engine type classification for strict separation"""
    RESUME_ENGINE = "RG"
    OUTREACH_ENGINE = "LIC"


class ResponsibilityLevel(Enum):
    """L1-L5 responsibility tagging system"""
    L1_CORE = "L1"
    L2_COMPONENT = "L2"
    L3_INTERFACE = "L3"
    L4_IMPLEMENTATION = "L4"
    L5_UTILITY = "L5"


class FileExtension(Enum):
    """Supported file types for semantic processing"""
    PYTHON = ".py"
    JSON = ".json"
    MARKDOWN = ".md"
    TEXT = ".txt"
    YAML = ".yaml"
    CONFIG = ".cfg"


@dataclass
class FileSignature:
    """Unique file identification and integrity"""
    file_path: Path
    file_hash: str
    size_bytes: int
    last_modified: datetime
    engine: EngineType
    archive_version: str
    file_extension: FileExtension
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": str(self.file_path),
            "file_hash": self.file_hash,
            "size_bytes": self.size_bytes,
            "last_modified": self.last_modified.isoformat(),
            "engine": self.engine.value,
            "archive_version": self.archive_version,
            "file_extension": self.file_extension.value
        }


@dataclass
class ASTNode:
    """AST node representation with semantic metadata"""
    node_type: str
    name: str
    line_number: int
    docstring: Optional[str]
    imports: List[str]
    dependencies: List[str]
    responsibility_level: ResponsibilityLevel
    children: List[ASTNode] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": self.node_type,
            "name": self.name,
            "line_number": self.line_number,
            "docstring": self.docstring,
            "imports": self.imports,
            "dependencies": self.dependencies,
            "responsibility_level": self.responsibility_level.value,
            "children": [child.to_dict() for child in self.children]
        }


@dataclass
class ASTSignature:
    """Complete AST signature for a file"""
    signature: FileSignature
    root_nodes: List[ASTNode]
    import_graph: Dict[str, List[str]]
    function_signatures: Dict[str, str]
    class_signatures: Dict[str, str]
    complexity_metrics: Dict[str, Union[int, float]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signature": self.signature.to_dict(),
            "root_nodes": [node.to_dict() for node in self.root_nodes],
            "import_graph": self.import_graph,
            "function_signatures": self.function_signatures,
            "class_signatures": self.class_signatures,
            "complexity_metrics": self.complexity_metrics
        }


@dataclass
class EmbeddingVector:
    """Semantic embedding representation"""
    vector_hash: str
    embedding_model: str
    vector_dimensions: int
    embedding_data: List[float]  # Actual embedding values
    confidence_score: float
    semantic_tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "vector_hash": self.vector_hash,
            "embedding_model": self.embedding_model,
            "vector_dimensions": self.vector_dimensions,
            "embedding_data": self.embedding_data,
            "confidence_score": self.confidence_score,
            "semantic_tags": self.semantic_tags
        }


@dataclass
class ToolUsageSignature:
    """Tool usage extraction for retry/backoff/API shapes"""
    api_calls: List[Dict[str, Any]]
    retry_patterns: List[str]
    backoff_strategies: List[str]
    error_handling: List[str]
    external_dependencies: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "api_calls": self.api_calls,
            "retry_patterns": self.retry_patterns,
            "backoff_strategies": self.backoff_strategies,
            "error_handling": self.error_handling,
            "external_dependencies": self.external_dependencies
        }


@dataclass
class SafetySignature:
    """Safety and policy lineage tracking"""
    safety_checks: List[str]
    policy_compliance: List[str]
    security_patterns: List[str]
    data_handling: List[str]
    access_controls: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "safety_checks": self.safety_checks,
            "policy_compliance": self.policy_compliance,
            "security_patterns": self.security_patterns,
            "data_handling": self.data_handling,
            "access_controls": self.access_controls
        }


@dataclass
class SemanticDiff:
    """Function-level semantic diffs"""
    added_functions: List[str]
    removed_functions: List[str]
    modified_functions: List[str]
    signature_changes: Dict[str, Tuple[str, str]]
    behavior_changes: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "added_functions": self.added_functions,
            "removed_functions": self.removed_functions,
            "modified_functions": self.modified_functions,
            "signature_changes": self.signature_changes,
            "behavior_changes": self.behavior_changes
        }


@dataclass
class GoldenProjection:
    """Golden canonical projections"""
    canonical_form: str
    normalized_signature: str
    core_functionality: str
    interface_contract: str
    test_coverage: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "canonical_form": self.canonical_form,
            "normalized_signature": self.normalized_signature,
            "core_functionality": self.core_functionality,
            "interface_contract": self.interface_contract,
            "test_coverage": self.test_coverage
        }


@dataclass
class IntegritySignals:
    """Integrity and verification signals"""
    content_hash: str
    structure_hash: str
    semantic_hash: str
    version_id: str
    lineage_chain: List[str]
    verification_status: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_hash": self.content_hash,
            "structure_hash": self.structure_hash,
            "semantic_hash": self.semantic_hash,
            "version_id": self.version_id,
            "lineage_chain": self.lineage_chain,
            "verification_status": self.verification_status
        }


@dataclass
class SemanticCacheEntry:
    """Complete semantic cache entry for a single file"""
    file_signature: FileSignature
    ast_signature: ASTSignature
    embedding: EmbeddingVector
    tool_usage: ToolUsageSignature
    safety: SafetySignature
    semantic_diff: Optional[SemanticDiff]
    golden_projection: GoldenProjection
    integrity: IntegritySignals
    processing_timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_signature": self.file_signature.to_dict(),
            "ast_signature": self.ast_signature.to_dict(),
            "embedding": self.embedding.to_dict(),
            "tool_usage": self.tool_usage.to_dict(),
            "safety": self.safety.to_dict(),
            "semantic_diff": self.semantic_diff.to_dict() if self.semantic_diff else None,
            "golden_projection": self.golden_projection.to_dict(),
            "integrity": self.integrity.to_dict(),
            "processing_timestamp": self.processing_timestamp.isoformat()
        }
    
    def get_file_hash(self) -> str:
        """Get primary file hash for artifact naming"""
        return self.file_signature.file_hash


@dataclass
class ArchiveManifest:
    """Manifest for an entire archive version"""
    engine: EngineType
    archive_version: str
    archive_path: Path
    total_files: int
    processed_files: int
    failed_files: List[str]
    file_hashes: Set[str]
    completeness_score: float
    processing_start: datetime
    processing_end: Optional[datetime]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine": self.engine.value,
            "archive_version": self.archive_version,
            "archive_path": str(self.archive_path),
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files,
            "file_hashes": list(self.file_hashes),
            "completeness_score": self.completeness_score,
            "processing_start": self.processing_start.isoformat(),
            "processing_end": self.processing_end.isoformat() if self.processing_end else None
        }


@dataclass
class GlobalCacheReport:
    """Global cache status and integrity report"""
    resume_engine_manifests: Dict[str, ArchiveManifest]
    outreach_engine_manifests: Dict[str, ArchiveManifest]
    global_integrity: Dict[str, Any]
    drift_report: Dict[str, Any]
    orphan_report: Dict[str, Any]
    completeness_report: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "resume_engine_manifests": {
                version: manifest.to_dict() 
                for version, manifest in self.resume_engine_manifests.items()
            },
            "outreach_engine_manifests": {
                version: manifest.to_dict() 
                for version, manifest in self.outreach_engine_manifests.items()
            },
            "global_integrity": self.global_integrity,
            "drift_report": self.drift_report,
            "orphan_report": self.orphan_report,
            "completeness_report": self.completeness_report
        }


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash for file integrity"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def determine_engine_from_path(file_path: Path) -> EngineType:
    """Determine engine type from file path"""
    path_str = str(file_path).upper()
    if "RESUME ENGINE ARCHIVE" in path_str:
        return EngineType.RESUME_ENGINE
    elif "REACHOUT ENGINE ARCHIVE" in path_str:
        return EngineType.OUTREACH_ENGINE
    else:
        raise ValueError(f"Cannot determine engine type for path: {file_path}")


def extract_archive_version(archive_path: Path) -> str:
    """Extract archive version from path"""
    return archive_path.name


def validate_file_extension(file_path: Path) -> Optional[FileExtension]:
    """Validate and return file extension"""
    suffix = file_path.suffix.lower()
    for ext_type in FileExtension:
        if ext_type.value == suffix:
            return ext_type
    return None


class SemanticLineageValidator:
    """Validator for semantic lineage data integrity"""
    
    @staticmethod
    def validate_cache_entry(entry: SemanticCacheEntry) -> List[str]:
        """Validate a complete cache entry"""
        errors = []
        
        # Check file signature integrity
        if not entry.file_signature.file_hash:
            errors.append("Missing file hash in signature")
        
        # Check AST signature
        if not entry.ast_signature.root_nodes:
            errors.append("Empty AST signature")
        
        # Check embedding
        if not entry.embedding.embedding_data:
            errors.append("Empty embedding data")
        
        # Check integrity signals
        if not entry.integrity.verification_status:
            errors.append("Integrity verification failed")
        
        return errors
    
    @staticmethod
    def validate_manifest(manifest: ArchiveManifest) -> List[str]:
        """Validate archive manifest"""
        errors = []
        
        if manifest.total_files == 0:
            errors.append("Zero total files in manifest")
        
        if manifest.processed_files > manifest.total_files:
            errors.append("Processed files exceeds total files")
        
        if manifest.completeness_score < 0.0 or manifest.completeness_score > 1.0:
            errors.append("Invalid completeness score")
        
        return errors
