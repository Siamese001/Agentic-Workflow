#!/usr/bin/env python3
"""
Phase 0.5 Semantic Cache Rebuild - Common Data Structures

Shared data structures and constants used across all Phase 0.5 modules.
Eliminates circular dependencies by providing centralized type definitions.

ZERO-LOSS CONSTRAINTS:
- Centralized data structures to prevent circular imports
- Docker-safe paths only
- Type safety for all Phase 0.5 operations
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Project constants
PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
SEMANTIC_CACHE_ROOT = PROJECT_ROOT / "06_data" / "semantic_cache"
UNIFIED_STRUCTURE_YAML = PROJECT_ROOT / "unified_structure_subatomic.yaml"
UNIFIED_META_YAML = PROJECT_ROOT / "unified_structure_subatomic_meta.yaml"

# Archive paths
RESUME_ENGINE_ARCHIVES = [
    "C:/Git/Resume Engine Archive/Agentic-Workflow-10_11",
    "C:/Git/Resume Engine Archive/Agentic_Workflow-10_10", 
    "C:/Git/Resume Engine Archive/Agentic-Workflow-10_9",
    "C:/Git/Resume Engine Archive/Agentic-Workflow-10_8_core",
    "C:/Git/Resume Engine Archive/Agentic-Workflow-10_7_main",
    "C:/Git/Resume Engine Archive/Microservices Model",
    "C:/Git/Resume Engine Archive/Monolith",
    "C:/Git/Resume Engine Archive/Monolithic",
    "C:/Git/Resume Engine Archive/v2",
    "C:/Git/Resume Engine Archive/v6.0"
]

OLD_RESUME_GEN_FILES = [
    "C:/Git/Resume Engine Archive/Old Resume Gen Python/Resume_Generation_v14_19.py",
    "C:/Git/Resume Engine Archive/Old Resume Gen Python/Resume_Generation_v11.40.py", 
    "C:/Git/Resume Engine Archive/Old Resume Gen Python/Resume_Generation_v9_82.py",
    "C:/Git/Resume Engine Archive/Old Resume Gen Python/Resume_Generation_v5_44.py"
]

OUTREACH_ENGINE_ARCHIVES = [
    "C:/Git/Reachout Engine Archive/Agentic-LIC",
    "C:/Git/Reachout Engine Archive/Agentic LIC",
    "C:/Git/Reachout Engine Archive/Monolithic",
    "C:/Git/Reachout Engine Archive/Old LIC",
    "C:/Git/Reachout Engine Archive/deprecated in v13"
]

# File processing constants
ELIGIBLE_EXTENSIONS = {'.py', '.json', '.yaml', '.yml', '.md', '.txt'}
EXCLUDED_DIRECTORIES = {
    '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '.git', '.venv', '.idea', '.vscode', 'node_modules', '.DS_Store'
}
MAX_DEPTH = 7

# Canonical root mappings
CANONICAL_ROOTS = {
    "01_agentic_core": "agentic_core",
    "02_schemas": "schemas", 
    "03_runtime": "runtime",
    "04_prompt_governance": "prompt_governance",
    "05_config": "config",
    "06_data": "data_source",
    "07_observability": "observability",
    "08_scripts": "scripts",
    "09_apps": "apps",
    "10_tests": "tests"
}

@dataclass
class FileInfo:
    """Information about a scanned file"""
    archive_root: str
    archive_name: str  # e.g., "Agentic-Workflow-10_10"
    relative_path: str
    absolute_path: str
    file_size: int
    file_extension: str
    is_eligible: bool
    sha256_hash: str
    scan_timestamp: str

@dataclass
class ScanResult:
    """Result of scanning an archive"""
    archive_name: str
    archive_root: str
    total_files: int
    eligible_files: int
    non_eligible_files: int
    scan_duration_seconds: float
    files: List[FileInfo]

@dataclass
class ValidationResult:
    """Represents a validation result with K-key status"""
    key: str
    status: str  # "PASS" or "FAIL"
    message: str
    details: Optional[Dict] = None
    timestamp: str = ""

@dataclass
class PipelineStep:
    """Represents a pipeline step with status and metadata"""
    step_id: str
    step_name: str
    status: str  # "PENDING", "RUNNING", "COMPLETED", "FAILED"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None
    artifacts_created: List[str] = None
    
    def __post_init__(self):
        if self.artifacts_created is None:
            self.artifacts_created = []

@dataclass
class TransactionManifest:
    """Transaction manifest for pipeline state tracking"""
    pipeline_id: str
    start_time: str
    status: str  # "RUNNING", "COMPLETED", "FAILED", "RESUMED"
    dry_run: bool
    steps: List[PipelineStep]
    current_step: int
    total_files_processed: int
    artifacts_generated: int

@dataclass
class SSoTMetadata:
    """Metadata structure for loaded SSoT"""
    structure_version: str
    description: str
    domains: Dict[str, str]
    layers: Dict[str, str]
    phases: Dict[str, str]
    intents: List[str]
    axes: List[str]
    protected_paths: List[str]
    verb_groups: List[str]

@dataclass
class GlobalArtifactRecord:
    """Record for a global artifact"""
    hash: str
    artifact_type: str
    global_path: str
    size_bytes: int
    created_timestamp: str

@dataclass
class CanonicalPointerRecord:
    """Record for a canonical pointer"""
    target_root: str
    canonical_relative: str
    pointer_type: str
    global_hash: str
    global_path: str
    created_timestamp: str

@dataclass
class UnmappedFileRecord:
    """Record for an unmappable file"""
    file_info: FileInfo
    reason: str
    attempted_mappings: List[str]
    timestamp: str

@dataclass
class ArtifactMetadata:
    """Metadata for generated artifacts"""
    hash: str
    artifact_type: str
    file_info: FileInfo
    generation_timestamp: str
    artifact_path: str
    size_bytes: int

@dataclass
class FilesystemMonitor:
    """Monitors filesystem operations for sandbox validation"""
    writes_outside_cache: List[str] = None
    archive_files_modified: List[str] = None
    repo_files_modified: List[str] = None
    
    def __post_init__(self):
        if self.writes_outside_cache is None:
            self.writes_outside_cache = []
        if self.archive_files_modified is None:
            self.archive_files_modified = []
        if self.repo_files_modified is None:
            self.repo_files_modified = []

# Version lineage tracking
VersionLineageMap = Dict[str, List[Tuple[str, FileInfo]]]  # logical_path -> [(version, file_info)]

# Validation K-keys constants
SSOT_KEYS = ["K1", "K1b", "K1c", "K1d"]
CANONICAL_KEYS = ["KX_CANONICAL_GRAMMAR", "KX_META_INTENTS", "KX_META_AXES", "KX_META_DRIVES_MAPPING"]
GLOBAL_ARTIFACT_KEYS = ["K21", "K22", "K23", "K24", "K25", "K26", "K27"]
HASH_KEYS = ["K28", "K29"]
ROOT_VALIDATION_KEYS = ["K17", "K18", "K19", "K20"]
SANDBOX_KEYS = ["K30", "K31", "K32", "K33", "K34"]
QUALITY_KEYS = ["K35", "K36", "K37", "K38"]
COMPLETION_KEYS = ["K39", "K40"]

ALL_VALIDATION_KEYS = (
    SSOT_KEYS + CANONICAL_KEYS + GLOBAL_ARTIFACT_KEYS + 
    HASH_KEYS + ROOT_VALIDATION_KEYS + SANDBOX_KEYS + 
    QUALITY_KEYS + COMPLETION_KEYS
)

# Utility functions
def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of file content"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception:
        return ""

def is_eligible_file(file_path: Path) -> bool:
    """Check if file is eligible for semantic processing"""
    if file_path.suffix.lower() not in ELIGIBLE_EXTENSIONS:
        return False
    
    non_semantic_patterns = {
        '*.pyc', '*.pyo', '*.pyd', '*.db', '*.sqlite', 
        '*.log', '*.bin', '*.exe', '*.dll', '*.so', '*.dylib'
    }
    
    for pattern in non_semantic_patterns:
        if file_path.match(pattern):
            return False
    
    return True

def should_exclude_directory(dir_path: Path) -> bool:
    """Check if directory should be excluded from scanning"""
    return dir_path.name in EXCLUDED_DIRECTORIES

def build_logical_path(file_info: FileInfo) -> str:
    """Build logical path for lineage tracking"""
    relative_path = file_info.relative_path.replace('\\', '/')
    
    prefixes_to_remove = [
        'plan-layer/', 'exec-layer/', 'safe-layer/', 'mem-layer/',
        'orc-layer/', 'observer-microagent-layer/', 'executor-microagent-layer/',
        'planner-microagent-layer/', 'retriever-microagent-layer/', 
        'router-microagent-layer/', 'budget-manager-layer/'
    ]
    
    for prefix in prefixes_to_remove:
        if relative_path.startswith(prefix):
            relative_path = relative_path[len(prefix):]
            break
    
    return relative_path
