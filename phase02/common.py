#!/usr/bin/env python3
"""
Phase 2 Semantic Structural & Code Diff Planning - Common Data Structures

Shared data structures and constants used across all Phase 2 modules.
Eliminates circular dependencies by providing centralized type definitions.

ZERO-LOSS CONSTRAINTS:
- Centralized data structures to prevent circular imports
- Docker-safe paths only
- Type safety for all Phase 2 operations
- Read-only operations for FS and semantic cache
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Project constants
PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
SEMANTIC_CACHE_ROOT = PROJECT_ROOT / "06_data" / "semantic_cache"
UNIFIED_STRUCTURE_YAML = PROJECT_ROOT / "unified_structure_subatomic.yaml"
UNIFIED_META_YAML = PROJECT_ROOT / "unified_structure_subatomic_meta.yaml"
TARGET_ROOT = "01_agentic_core/"
SCHEMAS_ROOT = PROJECT_ROOT / "02_schemas"

# Phase 2 specific paths
PHASE02_OUTPUT_PLAN = SCHEMAS_ROOT / "01_agentic_core_migration_and_rewrite_plan.json"
SEMANTIC_CACHE_BUCKET = SEMANTIC_CACHE_ROOT / "agentic_core"
GLOBAL_CACHE_ROOT = SEMANTIC_CACHE_ROOT

# Validation K-keys constants for Phase 2
PRECONDITION_KEYS = ["K1", "K2", "K3", "K4", "K5", "K6", "K7"]
SSOT_LOADING_KEYS = ["K8", "K8b", "K8c", "K9"]
FILESYSTEM_LOADING_KEYS = ["K10"]
SEMANTIC_CACHE_LOADING_KEYS = ["K11", "K12", "K13", "K14", "K15", "K16"]
STRUCTURAL_DIFF_KEYS = ["K17", "K18", "K19", "K20", "K21", "K22", "K23", "K24"]
SEMANTIC_DIFF_LOADING_KEYS = ["K25", "K26", "K27", "K28", "K29"]
SEMANTIC_DIFF_COMPUTATION_KEYS = ["K30", "K31", "K32", "K33", "K34", "K35", "K34b", "K34c", "K34d", "K36"]
INTENT_KEYS = ["K37", "K38", "K39", "K40", "K41", "K42", "K43"]
PLAN_GENERATION_KEYS = ["K44", "K45", "K46", "K47", "K48", "K49", "K50", "K51", "K52", "K53", "K54", "K55"]
OPERATION_RULES_KEYS = ["K56", "K57", "K58"]
OPERATION_PATHS_KEYS = ["K59", "K60", "K61", "K62", "K63"]
PROTECTED_PATHS_KEYS = ["K64", "K65", "K66", "K67", "K68"]
IMMUTABILITY_KEYS = ["K69", "K70", "K71", "K72", "K73"]
DETERMINISM_KEYS = ["K74", "K75", "K76", "K77", "K78", "K79"]
SUMMARY_KEYS = ["K80", "K81", "K82", "K83"]
COMPLETION_KEYS = ["K84", "K85", "K86", "K87", "K88"]

ALL_PHASE2_VALIDATION_KEYS = (
    PRECONDITION_KEYS + SSoT_LOADING_KEYS + FILESYSTEM_LOADING_KEYS +
    SEMANTIC_CACHE_LOADING_KEYS + STRUCTURAL_DIFF_KEYS + SEMANTIC_DIFF_LOADING_KEYS +
    SEMANTIC_DIFF_COMPUTATION_KEYS + INTENT_KEYS + PLAN_GENERATION_KEYS +
    OPERATION_RULES_KEYS + OPERATION_PATHS_KEYS + PROTECTED_PATHS_KEYS +
    IMMUTABILITY_KEYS + DETERMINISM_KEYS + SUMMARY_KEYS + COMPLETION_KEYS
)

# Operation types for Phase 2
STRUCTURAL_OPERATIONS = {
    "create_dir", "create_file", "delete_dir", "delete_file", "move_path", "rename_path"
}

SEMANTIC_OPERATIONS = {
    "rewrite_file_from_cache", "merge_file_from_cache", "patch_region_from_cache",
    "insert_semantic_block", "delete_semantic_block", "canonical_rewrite"
}

ALLOWED_OPERATIONS = STRUCTURAL_OPERATIONS | SEMANTIC_OPERATIONS

class OperationType(Enum):
    """Enumeration of allowed operation types"""
    CREATE_DIR = "create_dir"
    CREATE_FILE = "create_file"
    DELETE_DIR = "delete_dir"
    DELETE_FILE = "delete_file"
    MOVE_PATH = "move_path"
    RENAME_PATH = "rename_path"
    REWRITE_FILE_FROM_CACHE = "rewrite_file_from_cache"
    MERGE_FILE_FROM_CACHE = "merge_file_from_cache"
    PATCH_REGION_FROM_CACHE = "patch_region_from_cache"
    INSERT_SEMANTIC_BLOCK = "insert_semantic_block"
    DELETE_SEMANTIC_BLOCK = "delete_semantic_block"
    CANONICAL_REWRITE = "canonical_rewrite"

class DiffType(Enum):
    """Enumeration of semantic diff types"""
    AST_DIFF = "ast_diff"
    EMBEDDING_DISTANCE = "embedding_distance"
    GOLDEN_DIFF = "golden_diff"
    TOOL_USAGE_DIFF = "tool_usage_diff"
    BEHAVIOR_DIFF = "behavior_diff"
    LAYER_MISMATCH = "layer_mismatch"

@dataclass
class ValidationResult:
    """Single validation result entry for Phase 2 K-keys"""
    key: str
    status: str  # "PASS" or "FAIL"
    message: str
    details: Optional[Dict] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class Phase2Step:
    """Represents a Phase 2 pipeline step with status and metadata"""
    step_id: str
    step_name: str
    status: str  # "PENDING", "RUNNING", "COMPLETED", "FAILED"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None
    validation_results: List[ValidationResult] = None
    
    def __post_init__(self):
        if self.validation_results is None:
            self.validation_results = []

@dataclass
class Phase2TransactionManifest:
    """Transaction manifest for Phase 2 pipeline state tracking"""
    pipeline_id: str
    start_time: str
    status: str  # "RUNNING", "COMPLETED", "FAILED", "RESUMED"
    dry_run: bool
    target_root: str
    steps: List[Phase2Step]
    current_step: int
    total_files_processed: int
    semantic_artifacts_loaded: int
    operations_generated: int

@dataclass
class SSoTState:
    """Loaded SSoT state for Phase 2"""
    structure_data: Dict
    meta_data: Dict
    combined_ssot: Dict
    target_root_subtree: Dict
    validation_summary: Dict

@dataclass
class FilesystemState:
    """Loaded filesystem state for Phase 2"""
    target_root_path: Path
    directory_structure: Dict
    file_list: List[Path]
    file_metadata: Dict[str, Dict]  # relative_path -> metadata
    normalized_paths: Dict[str, str]  # path -> normalized form

@dataclass
class SemanticCacheState:
    """Loaded semantic cache state for Phase 2"""
    bucket_path: Path
    global_objects: Dict
    target_root_objects: Dict
    ast_data: Dict[str, Dict]
    embedding_data: Dict[str, Dict]
    diff_data: Dict[str, Dict]
    golden_data: Dict[str, Dict]
    integrity_data: Dict[str, Dict]
    path_mappings: Dict[str, str]  # cache_path -> fs_path

@dataclass
class StructuralDiff:
    """Represents a structural difference between SSoT and filesystem"""
    yaml_only_dirs: Set[str]
    yaml_only_files: Set[str]
    fs_only_dirs: Set[str]
    fs_only_files: Set[str]
    misplaced_paths: Set[str]
    name_mismatches: Set[str]
    is_empty: bool

@dataclass
class SemanticDiff:
    """Represents a semantic difference between cache and live code"""
    file_path: str
    ast_diff: Optional[Dict]
    embedding_distance: Optional[float]
    golden_diff: Optional[Dict]
    tool_usage_diffs: List[str]
    behavior_diffs: List[str]
    layer_mismatches: List[str]
    diff_type: DiffType
    confidence_score: float

@dataclass
class CompositeIntent:
    """Represents composite intent for structural and semantic operations"""
    structural_repair_intent: Dict
    code_rewrite_intent: Dict
    code_merge_intent: Dict
    code_patch_region_intent: Dict
    code_delete_intent: Dict
    code_create_intent: Dict
    is_deterministic: bool

@dataclass
class Operation:
    """Represents a single operation in the migration plan"""
    operation_type: OperationType
    target_path: str
    source_path: Optional[str] = None
    semantic_cache_hash: Optional[str] = None
    metadata: Optional[Dict] = None
    priority: str = "medium"  # "high", "medium", "low"

@dataclass
class MigrationPlan:
    """Complete migration and rewrite plan for Phase 2"""
    schema_version: str
    target_root: str
    mode: str
    operations: List[Operation]
    summary: Dict
    metadata: Dict
    validation_keys: List[str]
    timestamp: str

@dataclass
class Phase2Config:
    """Configuration for Phase 2 execution"""
    target_root: str = "01_agentic_core/"
    semantic_cache_bucket: str = "06_data/semantic_cache/agentic_core/"
    write_target: str = "02_schemas/01_agentic_core_migration_and_rewrite_plan.json"
    dry_run: bool = False
    resume_from: Optional[str] = None
    validate_only: bool = False
    verbose: bool = False

# Protected paths for Phase 2
PROTECTED_PATHS = {
    "__init__.py",
    "01_agentic_core/__init__.py",
    "01_agentic_core/**/__init__.py"
}

# Utility functions
def normalize_path(path: Union[str, Path]) -> str:
    """Normalize path to forward slash format relative to project root"""
    if isinstance(path, Path):
        path = str(path)
    
    # Convert to forward slashes
    path = path.replace("\\", "/")
    
    # Remove leading slash if present
    if path.startswith("/"):
        path = path[1:]
    
    return path

def is_protected_path(path: str) -> bool:
    """Check if a path is protected"""
    normalized = normalize_path(path)
    
    for protected in PROTECTED_PATHS:
        if "**" in protected:
            # Handle wildcard patterns
            pattern = protected.replace("**", "*")
            if normalized.endswith(pattern.replace("*", "")):
                return True
        elif normalized == protected or normalized.endswith("/" + protected):
            return True
    
    return False

def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file content"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception:
        return ""

def validate_operation_path(path: str) -> bool:
    """Validate that operation path follows Phase 2 rules"""
    # Must be relative to target root
    if not path.startswith("01_agentic_core/"):
        return False
    
    # Must use forward slashes
    if "\\" in path:
        return False
    
    # Must not contain absolute or host paths
    if ":" in path or path.startswith("/"):
        return False
    
    # Must not contain timestamp or randomness
    if any(pattern in path.lower() for pattern in ["temp", "tmp", "random", "timestamp"]):
        return False
    
    return True

def create_validation_result(key: str, status: str, message: str, details: Optional[Dict] = None) -> ValidationResult:
    """Create a validation result with timestamp"""
    return ValidationResult(
        key=key,
        status=status,
        message=message,
        details=details,
        timestamp=datetime.now().isoformat()
    )

def print_validation_status(result: ValidationResult):
    """Print validation status as required by Phase 2 spec"""
    print(f"{result.key} = {result.status}")

# Phase 2 specific constants
PHASE02_SCHEMA_VERSION = "v1"
PHASE02_MODE = "semantic_structural_unified"

# File processing constants for Phase 2
ELIGIBLE_EXTENSIONS = {'.py', '.json', '.yaml', '.yml', '.md', '.txt'}
EXCLUDED_DIRECTORIES = {
    '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '.git', '.venv', '.idea', '.vscode', 'node_modules', '.DS_Store'
}

# Semantic artifact types for Phase 2
SEMANTIC_ARTIFACT_TYPES = {
    "ast", "diffs", "embeddings", "golden", "integrity", "meta", "safety"
}

# Diff computation thresholds
EMBEDDING_SIMILARITY_THRESHOLD = 0.8
AST_DIFF_THRESHOLD = 0.1
GOLDEN_RECORD_THRESHOLD = 0.9
