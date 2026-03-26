"""End-to-end integration test: ADG generate_full_adg.py persistence path.


"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

import pytest








@dataclass


@dataclass


def _make_scan_result(n_modules: int = 10, n_edges: int = 5) -> _MockScanResult:
    """Build a realistic mock ScanResult with N modules and E edges."""




@pytest.fixture()
def memory_env(tmp_path, monkeypatch):
    """Provide (adapter, db_path) with a fresh temp SQLite store."""







def _counts(db):




    def test_ingest_populates_sqlite(self, memory_env):
                """Full pipeline: ingest_snapshot must produce non-zero entity count in SQLite."""




    def test_snapshot_entity_written(self, memory_env):
        """ADGSnapshot entity must be the anchor node after ingest."""



    def test_layer_entities_written(self, memory_env):
        """At least one ADGLayer entity must exist — layers are the structural backbone."""



    def test_observations_written(self, memory_env):
        """Observations (the descriptive content) must be written, not just entity stubs."""


    def test_data_survives_bridge_reset(self, tmp_path, monkeypatch):
        """Data written via ingest must survive a GraphMemoryBridge singleton reset.

        """







    def test_repeated_ingest_is_idempotent(self, memory_env):
        """Calling ingest_snapshot twice with the same ts must not duplicate entities."""





    def test_violation_edges_written(self, memory_env):
        """Violation edges (GV_violates) must be persisted as ADGViolation entities."""


