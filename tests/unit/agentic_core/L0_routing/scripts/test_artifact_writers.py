"""
Tests for E6 and E7 artifact writers (run_manifest, decision_summary, artifact_integrity).

Per .windsurfrules §1.1: Zero-tolerance testing - all changed logic tested.
Per .windsurfrules §1.7: Deterministic decision surfaces - identical input → identical output.
Per hostile audit Section E6: run_manifest.json and decision_summary.json.
Per hostile audit Section E7: artifact_integrity.json as final step.
"""

import hashlib
import json

import pytest


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def test_write_run_manifest_json_structure(tmp_path):
    """
    PASS: run_manifest.json has required fields and correct structure.
    FAIL: Missing fields or invalid structure.

    Per .windsurfrules §1.5: Edge cases - field presence.
    Per hostile audit Section E6: run_manifest provides high-level metadata.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_run_manifest_json

    trace_id = "TEST-TRACE-001"
    execution_mode = "heal"
    territories = ["apps_core", APPS_SHARED_DIR]
    agents_executed = ["AgentA", "AgentB", "AgentC"]

    _write_run_manifest_json(
        trace_id=trace_id,
        execution_mode=execution_mode,
        territories=territories,
        agents_executed=agents_executed,
        output_dir=tmp_path,
    )

    manifest_path = tmp_path / "run_manifest.json"
    assert manifest_path.exists(), "run_manifest.json should be created"

    with open(manifest_path) as f:
        data = json.load(f)

    # Verify required fields
    assert data["trace_id"] == trace_id
    assert data["execution_mode"] == execution_mode
    assert data["territories"] == territories
    assert data["agents_executed"] == agents_executed
    assert data["agent_count"] == 3
    assert data["territory_count"] == 2
    assert "timestamp_utc" in data

    # Verify timestamp format
    assert data["timestamp_utc"].endswith("Z"), "timestamp should be UTC with Z suffix"


def test_write_run_manifest_json_empty_lists(tmp_path):
    """
    PASS: run_manifest.json handles empty territories and agents lists.
    FAIL: Crashes or produces invalid output.

    Per .windsurfrules §1.5: Edge cases - empty input.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_run_manifest_json

    _write_run_manifest_json(
        trace_id="TEST-TRACE-002",
        execution_mode="scan",
        territories=[],
        agents_executed=[],
        output_dir=tmp_path,
    )

    manifest_path = tmp_path / "run_manifest.json"
    with open(manifest_path) as f:
        data = json.load(f)

    assert data["agent_count"] == 0
    assert data["territory_count"] == 0
    assert data["territories"] == []
    assert data["agents_executed"] == []


def test_write_decision_summary_json_structure(tmp_path):
    """
    PASS: decision_summary.json has required fields and aggregates decisions correctly.
    FAIL: Missing fields or incorrect aggregation.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E6: decision_summary provides routing audit trail.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_decision_summary_json

    trace_id = "TEST-TRACE-003"
    decisions = [
        {"tier": "DETERMINISTIC", "agent": "AgentA", "confidence": 0.95},
        {"tier": "TIER_1", "agent": "AgentB", "confidence": 0.75},
        {"tier": "DETERMINISTIC", "agent": "AgentA", "confidence": 0.90},
        {"tier": "TIER_2", "agent": "AgentC", "confidence": 0.55},
    ]

    _write_decision_summary_json(
        trace_id=trace_id,
        decisions_made=decisions,
        output_dir=tmp_path,
    )

    summary_path = tmp_path / "decision_summary.json"
    assert summary_path.exists(), "decision_summary.json should be created"

    with open(summary_path) as f:
        data = json.load(f)

    # Verify required fields
    assert data["trace_id"] == trace_id
    assert data["total_decisions"] == 4
    assert "timestamp_utc" in data

    # Verify tier distribution
    assert data["tier_distribution"]["DETERMINISTIC"] == 2
    assert data["tier_distribution"]["TIER_1"] == 1
    assert data["tier_distribution"]["TIER_2"] == 1

    # Verify agent distribution
    assert data["agent_distribution"]["AgentA"] == 2
    assert data["agent_distribution"]["AgentB"] == 1
    assert data["agent_distribution"]["AgentC"] == 1

    # Verify decisions are preserved
    assert data["decisions"] == decisions


def test_write_decision_summary_json_empty_decisions(tmp_path):
    """
    PASS: decision_summary.json handles empty decisions list.
    FAIL: Crashes or produces invalid output.

    Per .windsurfrules §1.5: Edge cases - empty input.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_decision_summary_json

    _write_decision_summary_json(
        trace_id="TEST-TRACE-004",
        decisions_made=[],
        output_dir=tmp_path,
    )

    summary_path = tmp_path / "decision_summary.json"
    with open(summary_path) as f:
        data = json.load(f)

    assert data["total_decisions"] == 0
    assert data["tier_distribution"] == {}
    assert data["agent_distribution"] == {}
    assert data["decisions"] == []


def test_write_artifact_integrity_json_structure(tmp_path):
    """
    PASS: artifact_integrity.json has required fields and hashes all artifacts.
    FAIL: Missing fields or incorrect hashing.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E7: artifact_integrity provides cryptographic proof.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_artifact_integrity_json

    # Create some test artifacts
    artifact1 = tmp_path / "test_artifact_1.json"
    artifact1.write_text('{"test": "data1"}', encoding="utf-8")

    artifact2 = tmp_path / "test_artifact_2.json"
    artifact2.write_text('{"test": "data2"}', encoding="utf-8")

    trace_id = "TEST-TRACE-005"
    _write_artifact_integrity_json(
        trace_id=trace_id,
        output_dir=tmp_path,
    )

    integrity_path = tmp_path / "artifact_integrity.json"
    assert integrity_path.exists(), "artifact_integrity.json should be created"

    with open(integrity_path) as f:
        data = json.load(f)

    # Verify required fields
    assert data["trace_id"] == trace_id
    assert data["artifact_count"] == 2  # Should not count itself
    assert "timestamp_utc" in data

    # Verify artifacts are hashed
    assert "test_artifact_1.json" in data["artifacts"]
    assert "test_artifact_2.json" in data["artifacts"]
    assert "artifact_integrity.json" not in data["artifacts"]

    # Verify hash correctness
    artifact1_hash = hashlib.sha256(artifact1.read_bytes()).hexdigest()
    assert data["artifacts"]["test_artifact_1.json"]["sha256"] == artifact1_hash

    artifact2_hash = hashlib.sha256(artifact2.read_bytes()).hexdigest()
    assert data["artifacts"]["test_artifact_2.json"]["sha256"] == artifact2_hash

    # Verify size tracking
    assert data["artifacts"]["test_artifact_1.json"]["size_bytes"] == len(artifact1.read_bytes())
    assert data["artifacts"]["test_artifact_2.json"]["size_bytes"] == len(artifact2.read_bytes())


def test_write_artifact_integrity_json_no_artifacts(tmp_path):
    """
    PASS: artifact_integrity.json handles directory with no artifacts.
    FAIL: Crashes or produces invalid output.

    Per .windsurfrules §1.5: Edge cases - empty input.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_artifact_integrity_json

    _write_artifact_integrity_json(
        trace_id="TEST-TRACE-006",
        output_dir=tmp_path,
    )

    integrity_path = tmp_path / "artifact_integrity.json"
    with open(integrity_path) as f:
        data = json.load(f)

    assert data["artifact_count"] == 0
    assert data["artifacts"] == {}


def test_write_artifact_integrity_json_deterministic_hash(tmp_path):
    """
    PASS: artifact_integrity.json produces identical hash for identical content.
    FAIL: Hash changes for same content.

    Per .windsurfrules §1.7: Deterministic decision surfaces - identical input → identical output.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import _write_artifact_integrity_json

    # Create artifact with known content
    artifact = tmp_path / "test.json"
    content = '{"deterministic": "content"}'
    artifact.write_text(content, encoding="utf-8")

    # Write integrity file twice
    _write_artifact_integrity_json("TEST-TRACE-007", tmp_path)
    integrity_path = tmp_path / "artifact_integrity.json"
    with open(integrity_path) as f:
        data1 = json.load(f)

    # Remove and recreate
    integrity_path.unlink()
    _write_artifact_integrity_json("TEST-TRACE-007", tmp_path)
    with open(integrity_path) as f:
        data2 = json.load(f)

    # Hashes should be identical
    assert data1["artifacts"]["test.json"]["sha256"] == data2["artifacts"]["test.json"]["sha256"]

    # Verify against expected hash
    expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    assert data1["artifacts"]["test.json"]["sha256"] == expected_hash


def test_artifact_writers_trace_id_correlation(tmp_path):
    """
    PASS: All artifacts contain the same trace_id for correlation.
    FAIL: trace_ids differ across artifacts.

    Per .windsurfrules §1.7: Deterministic decision surfaces.
    Per hostile audit Section E1: trace_id must correlate all artifacts.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import (
        _write_artifact_integrity_json,
        _write_decision_summary_json,
        _write_run_manifest_json,
    )

    trace_id = "TEST-TRACE-CORRELATION"

    # Write all three artifact types
    _write_run_manifest_json(trace_id, "heal", ["apps_core"], ["AgentA"], tmp_path)
    _write_decision_summary_json(trace_id, [{"tier": "DETERMINISTIC", "agent": "AgentA"}], tmp_path)
    _write_artifact_integrity_json(trace_id, tmp_path)

    # Verify all have same trace_id
    with open(tmp_path / "run_manifest.json") as f:
        manifest = json.load(f)
    with open(tmp_path / "decision_summary.json") as f:
        summary = json.load(f)
    with open(tmp_path / "artifact_integrity.json") as f:
        integrity = json.load(f)

    assert manifest["trace_id"] == trace_id
    assert summary["trace_id"] == trace_id
    assert integrity["trace_id"] == trace_id


def test_artifact_writers_ascii_only(tmp_path):
    """
    PASS: All artifacts are written with ASCII-only encoding.
    FAIL: Non-ASCII characters appear in output.

    Per .windsurfrules §2.2: Evidence is deterministic, ASCII-only.
    """
    from agentic_core.L0_routing.scripts.execute_ssot import (
        _write_artifact_integrity_json,
        _write_decision_summary_json,
        _write_run_manifest_json,
    )

    trace_id = "TEST-TRACE-ASCII"

    _write_run_manifest_json(trace_id, "heal", ["apps_core"], ["AgentA"], tmp_path)
    _write_decision_summary_json(trace_id, [], tmp_path)
    _write_artifact_integrity_json(trace_id, tmp_path)

    # Verify all files are ASCII-only
    for artifact_path in tmp_path.glob("*.json"):
        content = artifact_path.read_text(encoding="utf-8")
        try:
            content.encode("ascii")
        except UnicodeEncodeError:
            pytest.fail(f"{artifact_path.name} contains non-ASCII characters")
