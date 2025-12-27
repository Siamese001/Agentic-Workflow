"""Shared fixtures for integration tests - Zero-Loss Merge & Transactional Sovereignty."""
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock
from contextlib import contextmanager
import pytest


@pytest.fixture
def tmp_sovereign_workspace(tmp_path):
    """Create temporary workspace with sovereign directory structure."""
    workspace = tmp_path / "sovereign_workspace"
    workspace.mkdir()
    
    # Create canonical structure
    (workspace / "agentic_core").mkdir()
    (workspace / "agentic_core" / "L1_cognition").mkdir(parents=True)
    (workspace / "agentic_core" / "L2_execution").mkdir(parents=True)
    (workspace / "agentic_core" / "L3_orchestration").mkdir(parents=True)
    (workspace / "schemas").mkdir()
    (workspace / "data").mkdir()
    
    return workspace


@pytest.fixture
def file_hash_tracker():
    """Track file content hashes for zero-loss verification with context manager support."""
    @contextmanager
    def _track_before_after(paths: List[Path]):
        """Context manager to verify files unchanged after operations."""
        def _hash_file(path: Path) -> str:
            # Handle non-existent files gracefully for creation tests
            if not path.exists():
                return "NON_EXISTENT"
            return hashlib.sha256(path.read_bytes()).hexdigest()
        
        before = {p: _hash_file(p) for p in paths}
        yield
        after = {p: _hash_file(p) for p in paths}
        
        # Explicit delta reporting for easier debugging
        if before != after:
            diff = {k: (before.get(k), after.get(k)) for k in before.keys() | after.keys() if before.get(k) != after.get(k)}
            pytest.fail(f"Zero-loss violation! State changed unexpectedly. Diff: {diff}")
    
    # Also provide simple hash function for direct use
    def compute_hash(file_path: Path) -> str:
        """Compute SHA256 hash of file content."""
        if not file_path.exists():
            return None
        return hashlib.sha256(file_path.read_bytes()).hexdigest()
    
    compute_hash.track = _track_before_after
    return compute_hash


@pytest.fixture
def healing_transaction_mock():
    """Mock healing transaction with backup/commit/rollback."""
    class MockHealingTransaction:
        def __init__(self):
            self.backups = {}
            self.committed = False
            self.rolled_back = False
            self.operations = []
        
        def backup(self, file_path: Path):
            """Backup file before modification."""
            try:
                if hasattr(file_path, 'exists') and file_path.exists():
                    self.backups[str(file_path)] = file_path.read_text()
                    self.operations.append(("backup", str(file_path)))
            except (OSError, RecursionError):
                pass
        
        def commit(self):
            """Commit transaction - clear backups."""
            self.committed = True
            self.backups.clear()
            self.operations.append(("commit", None))
        
        def rollback(self):
            """Rollback transaction - restore from backups."""
            self.rolled_back = True
            try:
                for file_path_str, content in self.backups.items():
                    file_path = Path(file_path_str)
                    if file_path.exists():
                        file_path.write_text(content)
            except (OSError, RecursionError):
                pass
            self.operations.append(("rollback", None))
        
        def get_operations(self):
            return self.operations
    
    return MockHealingTransaction()


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for API calls."""
    mock = MagicMock()
    mock.generate_content.return_value = Mock(
        text="Stub Gemini response",
        candidates=[Mock(finish_reason="STOP")]
    )
    return mock


@pytest.fixture
def mock_pinecone_index():
    """Mock Pinecone index for vector operations."""
    mock = MagicMock()
    mock.upsert.return_value = {"upserted_count": 1}
    mock.query.return_value = {
        "matches": [
            {"id": "vec-1", "score": 0.95, "metadata": {"source": "test"}}
        ]
    }
    mock.describe_index_stats.return_value = {"total_vector_count": 100}
    return mock


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for cache operations."""
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    mock.ping.return_value = True
    return mock


@pytest.fixture
def audit_log_tracker():
    """Track audit log entries during operations."""
    class AuditLogTracker:
        def __init__(self):
            self.entries = []
        
        def log(self, event_type: str, details: Dict[str, Any]):
            """Log an audit event."""
            self.entries.append({
                "event_type": event_type,
                "details": details
            })
        
        def get_entries(self, event_type: str = None):
            """Get all entries or filter by type."""
            if event_type:
                return [e for e in self.entries if e["event_type"] == event_type]
            return self.entries
        
        def clear(self):
            self.entries.clear()
    
    return AuditLogTracker()


@pytest.fixture
def sovereign_policy_enforcer_mock():
    """Mock sovereign policy enforcer for conflict resolution."""
    class MockPolicyEnforcer:
        def __init__(self):
            self.ssot_rank = {
                "gravity_law": 100,
                "naming_law": 90,
                "structural_drift": 80,
                "import_fix": 70
            }
        
        def resolve_conflict(self, proposals: list) -> dict:
            """Resolve conflicting proposals by SSOT rank."""
            if not proposals:
                return None
            
            # Sort by authority rank
            sorted_proposals = sorted(
                proposals,
                key=lambda p: self.ssot_rank.get(p.get("source", ""), 0),
                reverse=True
            )
            
            return sorted_proposals[0]
    
    return MockPolicyEnforcer()


@pytest.fixture
def fission_blueprint():
    """Mock fission blueprint for large file splitting."""
    return {
        "trigger_threshold": 10000,
        "target_modules": [
            {"name": "core_logic", "pattern": "class.*Core"},
            {"name": "utilities", "pattern": "def.*util"},
            {"name": "models", "pattern": "class.*Model"}
        ],
        "import_strategy": "relative",
        "preserve_order": True
    }


@pytest.fixture
def concurrent_lock_manager():
    """Mock lock manager for concurrent healing coordination."""
    import threading
    
    class MockLockManager:
        def __init__(self):
            self.locks = {}
        
        def acquire(self, resource_id: str, timeout: float = 5.0) -> bool:
            """Acquire lock on resource."""
            if resource_id not in self.locks:
                self.locks[resource_id] = threading.Lock()
            return self.locks[resource_id].acquire(timeout=timeout)
        
        def release(self, resource_id: str):
            """Release lock on resource."""
            if resource_id in self.locks:
                self.locks[resource_id].release()
        
        def is_locked(self, resource_id: str) -> bool:
            """Check if resource is locked."""
            if resource_id not in self.locks:
                return False
            return self.locks[resource_id].locked()
    
    return MockLockManager()
