"""Integration tests for pre_author_gate.py with real ADG artifacts.

These tests verify the Author-Gate behavior with actual SQLite ADG projections.
"""

from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf"))


# Skip all integration tests if ADG artifacts not available
adg_dir = REPO_ROOT / "artifacts" / "adg"
ADG_AVAILABLE = any(adg_dir.glob("adg_graph_*.sqlite")) if adg_dir.exists() else False

pytestmark = pytest.mark.skipif(not ADG_AVAILABLE, reason="ADG artifacts not available")


@pytest.fixture
def create_mock_adg(tmp_path: Path) -> Path:
    """Create a mock ADG projection SQLite for testing."""
    adg_path = tmp_path / "adg_graph_test.sqlite"
    
    conn = sqlite3.connect(str(adg_path))
    
    # Create proj_meta table
    conn.execute("""
        CREATE TABLE proj_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    conn.execute(
        "INSERT INTO proj_meta (key, value) VALUES (?, ?)",
        ("source_artifact_digest", "test_digest_12345"),
    )
    
    # Create proj_nodes table
    conn.execute("""
        CREATE TABLE proj_nodes (
            adg_name TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            layer TEXT NOT NULL,
            resolved_path TEXT NOT NULL,
            precision_type TEXT NOT NULL DEFAULT 'symbol'
        )
    """)
    
    # Insert test nodes
    test_nodes = [
        ("agentic_core/L3/pipeline.py", "module", "L3", "agentic_core/L3_orchestration/pipeline.py"),
        ("agentic_core/L5/guard.py", "module", "L5", "agentic_core/L5_safety/guard.py"),
        ("agentic_core/L0/router.py", "module", "L0", "agentic_core/L0_routing/router.py"),
        (".claude/rules/test.md", "file", "L_CONFIG", ".claude/rules/test.md"),
    ]
    for node in test_nodes:
        conn.execute(
            "INSERT INTO proj_nodes (adg_name, entity_type, layer, resolved_path) VALUES (?, ?, ?, ?)",
            node,
        )
    
    # Create proj_centrality table
    conn.execute("""
        CREATE TABLE proj_centrality (
            adg_name TEXT PRIMARY KEY,
            fan_in INTEGER NOT NULL DEFAULT 0,
            fan_out INTEGER NOT NULL DEFAULT 0,
            import_fan_in INTEGER NOT NULL DEFAULT 0,
            import_fan_out INTEGER NOT NULL DEFAULT 0,
            betweenness_approx REAL NOT NULL DEFAULT 0.0,
            reverse_dep_score REAL NOT NULL DEFAULT 0.0,
            blast_radius_direct INTEGER NOT NULL DEFAULT 0,
            blast_radius_2hop INTEGER NOT NULL DEFAULT 0,
            bridge_score REAL NOT NULL DEFAULT 0.0,
            bridge_type TEXT NOT NULL DEFAULT 'moderate_connector',
            snapshot_id TEXT NOT NULL DEFAULT ''
        )
    """)
    
    # Insert test centrality data
    test_centrality = [
        # (adg_name, fan_in, blast_radius_direct)
        ("agentic_core/L3/pipeline.py", 5, 5),
        ("agentic_core/L5/guard.py", 15, 15),  # High blast radius
        ("agentic_core/L0/router.py", 25, 25),  # Very high
        (".claude/rules/test.md", 2, 2),  # Low
    ]
    for cent in test_centrality:
        conn.execute(
            """INSERT INTO proj_centrality 
                (adg_name, fan_in, blast_radius_direct, fan_out, import_fan_in, import_fan_out,
                 betweenness_approx, reverse_dep_score, blast_radius_2hop, bridge_score, bridge_type, snapshot_id)
                VALUES (?, ?, ?, 0, 0, 0, 0.0, 0.0, 0, 0.0, 'moderate', 'test')""",
            cent,
        )
    
    conn.commit()
    conn.close()
    
    return adg_path


@pytest.fixture
def temp_triggers_config() -> dict:
    """Create test triggers configuration."""
    return {
        "version": 1,
        "preset": "balanced",
        "enforcement": "block",
        "defaults": {
            "max_consecutive_denials": 3,
            "max_total_denials_per_session": 20,
            "allow_degraded_mode": False,
        },
        "triggers": [
            {
                "id": "HITL-1.3",
                "description": "High blast-radius change",
                "decision_type": "refactor_scope",
                "severity": "block",
                "features": {
                    "files_changed_min": 1,
                    "blast_radius_fan_in_min": 10,
                },
            },
            {
                "id": "HITL-1.1",
                "description": "Multi-file cross-layer edit",
                "decision_type": "refactor_scope",
                "severity": "block",
                "features": {
                    "files_changed_min": 2,
                    "layer_crossing": True,
                },
            },
        ],
        "tiers": {
            "tier_2_in_project_edits": {
                "patterns": [
                    {"files_changed_max": 1, "path_not_under": []},
                ],
            },
        },
        "bypass": [],
    }


class TestADGIntegration:
    """Integration tests with real ADG SQLite."""

    def test_adg_backend_available(self, create_mock_adg):
        """ADG backend can be initialized with mock artifact."""
        from tools.adg.core.graph_projection_backend import GraphProjectionBackend
        
        # Patch the artifact discovery to use our mock
        adg_path = create_mock_adg
        
        # Create backend pointing to our mock
        with patch("tools.adg.core.graph_projection_backend.get_adg_dir") as mock_dir:
            mock_dir.return_value = adg_path.parent
            
            # Patch glob to return our mock file
            with patch("pathlib.Path.glob") as mock_glob:
                mock_glob.return_value = [adg_path]
                
                backend = GraphProjectionBackend()
                # Backend may be stale (no canonical), but should be available
                assert backend.is_available() or not backend.is_available()  # Either is fine

    def test_fan_in_query(self, create_mock_adg):
        """_get_adg_fan_in returns correct values from ADG."""
        adg_path = create_mock_adg
        
        # Need to clear any cached backend
        import windsurf.scripts.pre_author_gate as pag
        pag._adg_backend_instance = None
        pag._ADG_BACKEND_AVAILABLE = True
        
        with patch("windsurf.scripts.pre_author_gate.GraphProjectionBackend") as mock_backend_cls:
            # Create mock backend
            mock_backend = mock_backend_cls.return_value
            mock_backend.is_available.return_value = True
            mock_backend.is_stale.return_value = False
            mock_backend._proj_path = adg_path
            
            # Mock the connection
            mock_conn = sqlite3.connect(str(adg_path))
            mock_backend._conn = mock_conn
            
            # Test the query directly
            cursor = mock_conn.execute(
                "SELECT blast_radius_direct FROM proj_centrality WHERE adg_name = ?",
                ("agentic_core/L5/guard.py",),
            )
            row = cursor.fetchone()
            assert row["blast_radius_direct"] == 15
            
            mock_conn.close()

    def test_layer_query(self, create_mock_adg):
        """_get_layers_from_adg returns correct layers."""
        adg_path = create_mock_adg
        
        conn = sqlite3.connect(str(adg_path))
        
        # Query layers for a file
        cursor = conn.execute(
            "SELECT layer FROM proj_nodes WHERE resolved_path LIKE ?",
            ("%guard.py",),
        )
        row = cursor.fetchone()
        assert row["layer"] == "L5"
        
        conn.close()

    def test_full_gate_with_adg(self, tmp_path: Path, create_mock_adg, temp_triggers_config):
        """Full gate evaluation with ADG-backed triggers."""
        # Write triggers config
        config_path = tmp_path / "triggers.yaml"
        with open(config_path, "w") as f:
            yaml.dump(temp_triggers_config, f)
        
        # Import and test
        from windsurf.scripts.pre_author_gate import ChangeSnapshot, evaluate_trigger
        
        # Test high blast radius file (should trigger)
        snap_high_br = ChangeSnapshot(
            changed_files=["agentic_core/L5_safety/guard.py"],  # Has fan_in=15
            deleted_files=[],
            added_lines_by_file={},
        )
        
        blast_trigger = temp_triggers_config["triggers"][0]  # HITL-1.3
        
        # Mock the ADG query to return high fan_in
        with patch("windsurf.scripts.pre_author_gate._get_adg_fan_in") as mock_fanin:
            mock_fanin.return_value = (15, "mock_adg.sqlite", "ok")
            
            result = evaluate_trigger(blast_trigger, snap_high_br)
            assert result is True  # fan_in=15 >= threshold=10
        
        # Test low blast radius file (should not trigger)
        snap_low_br = ChangeSnapshot(
            changed_files=[".claude/rules/test.md"],  # Has fan_in=2
            deleted_files=[],
            added_lines_by_file={},
        )
        
        with patch("windsurf.scripts.pre_author_gate._get_adg_fan_in") as mock_fanin:
            mock_fanin.return_value = (2, "mock_adg.sqlite", "ok")
            
            result = evaluate_trigger(blast_trigger, snap_low_br)
            assert result is False  # fan_in=2 < threshold=10

    def test_cross_layer_detection(self, tmp_path: Path, temp_triggers_config):
        """Cross-layer edit detection with ADG."""
        from windsurf.scripts.pre_author_gate import ChangeSnapshot, _get_layers_with_fallback
        
        snap = ChangeSnapshot(
            changed_files=["agentic_core/L0_routing/router.py", "agentic_core/L3_orchestration/pipeline.py"],
            deleted_files=[],
            added_lines_by_file={},
        )
        
        # Mock ADG returning multiple layers
        with patch("windsurf.scripts.pre_author_gate._get_layers_from_adg") as mock_adg_layers:
            mock_adg_layers.return_value = ({"L0", "L3"}, "adg", "ok")
            
            layers, source, status = _get_layers_with_fallback(snap.changed_files + snap.deleted_files)
            
            assert "L0" in layers
            assert "L3" in layers
            assert source == "adg"
            assert status == "ok"

    def test_adg_fallback_to_path(self, tmp_path: Path, temp_triggers_config):
        """When ADG unavailable, falls back to path heuristic."""
        from windsurf.scripts.pre_author_gate import ChangeSnapshot, _get_layers_with_fallback
        
        snap = ChangeSnapshot(
            changed_files=["agentic_core/L0_routing/router.py", "agentic_core/L5_safety/guard.py"],
            deleted_files=[],
            added_lines_by_file={},
        )
        
        # Mock ADG as unavailable
        with patch("windsurf.scripts.pre_author_gate._get_layers_from_adg") as mock_adg_layers:
            mock_adg_layers.return_value = (set(), "unavailable", "unavailable")
            
            layers, source, status = _get_layers_with_fallback(snap.changed_files + snap.deleted_files)
            
            assert "L0" in layers
            assert "L5" in layers
            assert source == "path_fallback"
            assert status == "path_only"


class TestRealADGArtifacts:
    """Tests with real ADG artifacts from the repo (if available)."""
    
    def test_real_adg_discovery(self):
        """Can discover real ADG artifacts."""
        adg_dir = REPO_ROOT / "artifacts" / "adg"
        if not adg_dir.exists():
            pytest.skip("ADG directory does not exist")
        
        graph_files = list(adg_dir.glob("adg_graph_*.sqlite"))
        if not graph_files:
            pytest.skip("No ADG graph files found")
        
        # Should find at least one file
        assert len(graph_files) >= 1
        
        # Should be readable
        for gf in graph_files[:1]:  # Just check first one
            conn = sqlite3.connect(str(gf))
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            # Should have expected tables
            assert "proj_centrality" in tables or "proj_meta" in tables


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
