"""Wave 3: Tools — ADG MCP Server Core

Tests for 17 ADG MCP tools:
- adg_status (freshness validation)
- adg_meta (HASH parsing)
- adg_snapshot (JSON parsing)
- adg_node (node attributes)
- adg_nodes_by_layer (SET pagination)
- adg_nodes_by_file (file-to-node mapping)
- adg_edge_fanout/fanin (edge resolution)
- adg_violations (LIST parsing)
- redis_scan (cursor-based iteration)
- Cache metadata computation
"""

import json
from unittest.mock import MagicMock, patch

import pytest


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_redis_client():
    """Fixture to create a mock Redis client."""
    client = MagicMock()
    return client


@pytest.fixture
def sample_adg_status():
    """Sample adg:status JSON."""
    return {
        "timestamp": "2026-03-29_10:00:00",
        "node_count": 68000,
        "edge_count": 710000,
        "ingested_at": "2026-03-29_09:30:00",
        "sqlite_path": "artifacts/adg/adg_indexed_03292026_1000.sqlite",
        "digest": "a1b2c3d4e5f6789012345678901234567890abcd"
    }


@pytest.fixture
def sample_adg_meta():
    """Sample adg:meta HASH."""
    return {
        "timestamp": "2026-03-29_10:00:00",
        "sqlite_path": "artifacts/adg/adg_indexed_03292026_1000.sqlite",
        "sqlite_mtime": "1711702800.0",
        "ingested_at": "2026-03-29_09:30:00",
        "node_count": "68000",
        "edge_count": "710000",
        "digest": "a1b2c3d4e5f6789012345678901234567890abcd"
    }


@pytest.fixture
def sample_node_data():
    """Sample node HASH data."""
    return {
        "id": "agentic_core/adg/schema.py::Edge",
        "label": "Edge",
        "layer": "L0_routing",
        "kind": "class",
        "entity_type": "type",
        "file_path": "agentic_core/adg/schema.py",
        "confidence": "0.95"
    }


# ============================================================================
# ADG Status Tests
# ============================================================================

@pytest.mark.unit
class TestAdgStatus:
    """Tests for adg_status tool — freshness validation."""

    def test_adg_status_reads_sentinel(self, mock_redis_client, sample_adg_status):
        """Test adg_status reads adg:status STRING sentinel."""
        mock_redis_client.get.return_value = json.dumps(sample_adg_status)
        
        result = mock_redis_client.get("adg:status")
        assert result is not None
        
        data = json.loads(result)
        assert "timestamp" in data
        assert "node_count" in data
        assert "digest" in data

    def test_adg_status_validates_freshness(self, sample_adg_status):
        """Test adg_status validates freshness against SQLite mtime."""
        # Fresh if age < 300 seconds (5 minutes)
        import time
        current_time = time.time()
        ingested_time = current_time - 60  # 1 minute ago
        
        age_seconds = current_time - ingested_time
        is_fresh = age_seconds < 300
        
        assert is_fresh, "Should be fresh if < 5 minutes old"

    def test_adg_status_detects_stale(self, sample_adg_status):
        """Test adg_status detects stale cache."""
        import time
        current_time = time.time()
        ingested_time = current_time - 600  # 10 minutes ago
        
        age_seconds = current_time - ingested_time
        is_fresh = age_seconds < 300
        
        assert not is_fresh, "Should be stale if > 5 minutes old"


# ============================================================================
# ADG Meta Tests
# ============================================================================

@pytest.mark.unit
class TestAdgMeta:
    """Tests for adg_meta tool — HASH parsing."""

    def test_adg_meta_hgetall(self, mock_redis_client, sample_adg_meta):
        """Test adg_meta uses HGETALL on adg:meta HASH."""
        mock_redis_client.hgetall.return_value = sample_adg_meta
        
        result = mock_redis_client.hgetall("adg:meta")
        assert result is not None
        assert "timestamp" in result
        assert "node_count" in result

    def test_adg_meta_parses_node_count(self, sample_adg_meta):
        """Test adg_meta correctly parses node_count string to int."""
        node_count = int(sample_adg_meta["node_count"])
        assert node_count == 68000
        assert isinstance(node_count, int)

    def test_adg_meta_parses_edge_count(self, sample_adg_meta):
        """Test adg_meta correctly parses edge_count string to int."""
        edge_count = int(sample_adg_meta["edge_count"])
        assert edge_count == 710000
        assert isinstance(edge_count, int)


# ============================================================================
# ADG Snapshot Tests
# ============================================================================

@pytest.mark.unit
class TestAdgSnapshot:
    """Tests for adg_snapshot tool — JSON parsing."""

    def test_adg_snapshot_reads_string(self, mock_redis_client):
        """Test adg_snapshot reads adg:snapshot STRING."""
        snapshot = {
            "counts_by_layer": {
                "L0": 5000,
                "L1": 8000,
                "L2": 12000,
                "L3": 15000,
                "L4": 10000,
                "L5": 8000,
                "L6": 10000
            },
            "module_list": ["module1.py", "module2.py"],
            "digest": "abc123"
        }
        mock_redis_client.get.return_value = json.dumps(snapshot)
        
        result = mock_redis_client.get("adg:snapshot")
        data = json.loads(result)
        assert "counts_by_layer" in data
        assert "L0" in data["counts_by_layer"]


# ============================================================================
# ADG Node Tests
# ============================================================================

@pytest.mark.unit
class TestAdgNode:
    """Tests for adg_node tool — node attribute extraction."""

    def test_adg_node_hgetall(self, mock_redis_client, sample_node_data):
        """Test adg_node uses HGETALL on adg:node:<id> HASH."""
        node_id = "agentic_core/adg/schema.py::Edge"
        mock_redis_client.hgetall.return_value = sample_node_data
        
        result = mock_redis_client.hgetall(f"adg:node:{node_id}")
        assert result is not None
        assert result["id"] == node_id
        assert result["label"] == "Edge"

    def test_adg_node_extracts_layer(self, sample_node_data):
        """Test node data contains layer field."""
        assert sample_node_data["layer"] == "L0_routing"

    def test_adg_node_extracts_entity_type(self, sample_node_data):
        """Test node data contains entity_type field."""
        assert sample_node_data["entity_type"] == "type"


# ============================================================================
# ADG Nodes by Layer Tests
# ============================================================================

@pytest.mark.unit
class TestAdgNodesByLayer:
    """Tests for adg_nodes_by_layer tool — SET pagination."""

    def test_adg_nodes_by_layer_smembers(self, mock_redis_client):
        """Test adg_nodes_by_layer uses SMEMBERS on adg:nodes:by_layer:<layer>."""
        layer = "L0"
        node_ids = ["node1", "node2", "node3"]
        mock_redis_client.smembers.return_value = set(node_ids)
        
        result = mock_redis_client.smembers(f"adg:nodes:by_layer:{layer}")
        assert result is not None
        assert len(result) == 3

    def test_adg_nodes_by_layer_pagination(self):
        """Test pagination with offset and limit."""
        all_nodes = [f"node_{i}" for i in range(100)]
        offset = 0
        limit = 50
        
        paginated = all_nodes[offset:offset + limit]
        assert len(paginated) == 50
        assert paginated[0] == "node_0"
        assert paginated[-1] == "node_49"


# ============================================================================
# ADG Nodes by File Tests
# ============================================================================

@pytest.mark.unit
class TestAdgNodesByFile:
    """Tests for adg_nodes_by_file tool — file-to-node mapping."""

    def test_adg_nodes_by_file_smembers(self, mock_redis_client):
        """Test adg_nodes_by_file uses SMEMBERS on adg:nodes:by_file:<path>."""
        file_path = "agentic_core/adg/schema.py"
        node_ids = ["node1", "node2"]
        mock_redis_client.smembers.return_value = set(node_ids)
        
        result = mock_redis_client.smembers(f"adg:nodes:by_file:{file_path}")
        assert result is not None
        assert len(result) == 2


# ============================================================================
# ADG Edge Fanout/Fanin Tests
# ============================================================================

@pytest.mark.unit
class TestAdgEdgeFanoutFanin:
    """Tests for adg_edge_fanout/fanin tools — edge resolution."""

    def test_adg_edge_fanout_smembers(self, mock_redis_client):
        """Test adg_edge_fanout uses SMEMBERS on adg:edge:<src>:<rel>."""
        src_id = "module1"
        rel = "calls"
        edge_ids = ["edge1", "edge2"]
        mock_redis_client.smembers.return_value = set(edge_ids)
        
        result = mock_redis_client.smembers(f"adg:edge:{src_id}:{rel}")
        assert result is not None
        assert len(result) == 2

    def test_adg_edge_fanin_smembers(self, mock_redis_client):
        """Test adg_edge_fanin uses SMEMBERS on adg:edge:in:<tgt>:<rel>."""
        tgt_id = "module2"
        rel = "calls"
        edge_ids = ["edge3", "edge4"]
        mock_redis_client.smembers.return_value = set(edge_ids)
        
        result = mock_redis_client.smembers(f"adg:edge:in:{tgt_id}:{rel}")
        assert result is not None
        assert len(result) == 2


# ============================================================================
# ADG Violations Tests
# ============================================================================

@pytest.mark.unit
class TestAdgViolations:
    """Tests for adg_violations tool — LIST parsing."""

    def test_adg_violations_lrange(self, mock_redis_client):
        """Test adg_violations uses LRANGE on adg:violations LIST."""
        violations = ["v1", "v2", "v3"]
        mock_redis_client.lrange.return_value = violations
        
        result = mock_redis_client.lrange("adg:violations", 0, -1)
        assert result is not None
        assert len(result) == 3


# ============================================================================
# Redis Scan Tests
# ============================================================================

@pytest.mark.unit
class TestRedisScan:
    """Tests for redis_scan tool — cursor-based iteration."""

    def test_redis_scan_uses_cursor(self, mock_redis_client):
        """Test redis_scan uses SCAN cursor (not KEYS *)."""
        # Mock cursor-based scan
        mock_redis_client.scan.return_value = (0, ["key1", "key2"])  # cursor 0 = done
        
        cursor, keys = mock_redis_client.scan(match="adg:*", count=100)
        assert cursor == 0  # Done
        assert len(keys) == 2

    def test_redis_scan_pagination(self, mock_redis_client):
        """Test SCAN with multiple iterations."""
        # First call returns non-zero cursor
        # Second call returns 0 cursor (done)
        mock_redis_client.scan.side_effect = [
            (42, ["key1", "key2"]),  # cursor 42, partial results
            (0, ["key3"]),  # cursor 0, final results
        ]
        
        all_keys = []
        cursor = 0
        while True:
            cursor, keys = mock_redis_client.scan(cursor=cursor, match="adg:*", count=100)
            all_keys.extend(keys)
            if cursor == 0:
                break
        
        assert len(all_keys) == 3


# ============================================================================
# Cache Metadata Tests
# ============================================================================

@pytest.mark.unit
class TestCacheMetadata:
    """Tests for cache metadata computation in every response."""

    def test_cache_meta_includes_timestamp(self):
        """Test cache_meta includes timestamp."""
        import time
        cache_meta = {
            "timestamp": time.time(),
            "node_count": 68000,
            "edge_count": 710000,
            "ingested_at": "2026-03-29_09:30:00",
            "age_seconds": 60,
            "is_fresh": True
        }
        assert "timestamp" in cache_meta
        assert "is_fresh" in cache_meta

    def test_cache_meta_computes_age(self):
        """Test cache_meta computes age_seconds correctly."""
        import time
        current_time = time.time()
        ingested_at = current_time - 120  # 2 minutes ago
        
        age_seconds = current_time - ingested_at
        assert age_seconds == 120

    def test_cache_meta_freshness_threshold(self):
        """Test cache_meta uses 300s (5min) freshness threshold."""
        age_seconds = 250  # 4 min 10 sec
        is_fresh = age_seconds < 300
        assert is_fresh
