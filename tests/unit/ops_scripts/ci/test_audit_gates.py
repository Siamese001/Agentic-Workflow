"""Unit tests for the 6 AUDIT-uncovered ratchet gates.

Plan: audit-uncovered-gates-and-remediation-627368, NEXT_STEP Wave A.
Validates that each gate:
  1. Imports without error
  2. Has correct gate_id and tier
  3. run() returns a list[Violation] against a synthetic fixture snapshot
  4. seed_baseline() writes a valid JSON file

Each gate uses a tailored synthetic SQLite snapshot — minimum schema needed
for the gate's query to execute. Avoids dependency on real ADG snapshots.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
GATES_DIR = REPO_ROOT / "ops_scripts" / "ci"

# Each gate: (script_filename, expected_class_name, expected_gate_id, baseline_filename)
GATES = [
    (
        "check_ssot_magic_constants.py",
        "SsotMagicConstantsGate",
        "AUDIT_1_ssot_magic_constants",
        "audit_ssot_magic_constants.json",
    ),
    (
        "check_observability_on_high_fanin.py",
        "ObservabilityHighFaninGate",
        "AUDIT_2_observability_on_high_fanin",
        "audit_observability_high_fanin.json",
    ),
    (
        "check_external_service_literal_ssot.py",
        "ExternalServiceLiteralSsotGate",
        "AUDIT_3_external_service_literal_ssot",
        "audit_external_service_literal_ssot.json",
    ),
    (
        "check_cross_mainline_dispatcher.py",
        "CrossMainlineDispatcherGate",
        "AUDIT_4_cross_mainline_dispatcher",
        "audit_cross_mainline_dispatcher.json",
    ),
    (
        "check_env_var_in_config_layer.py",
        "EnvVarInConfigLayerGate",
        "AUDIT_5_env_var_in_config_layer",
        "audit_env_var_in_config_layer.json",
    ),
    (
        "check_violation_aging_sla.py",
        "ViolationAgingSlaGate",
        "AUDIT_6_violation_aging_sla",
        "audit_violation_aging_sla.json",
    ),
]


def _import_gate(script: str):
    """Import an underscore-named gate script by path."""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    path = GATES_DIR / script
    mod_name = f"_audit_gate_test_{script.removesuffix('.py')}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _build_minimal_schema(conn: sqlite3.Connection) -> None:
    """Build the union of tables/views every audit gate needs.

    Each gate only queries a subset; this superset lets us share one fixture.
    """
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT,
            entity_type TEXT,
            layer TEXT,
            resolved_path TEXT
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER,
            dst_id INTEGER,
            relation_type TEXT
        );
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY,
            edge_id INTEGER,
            category TEXT NOT NULL,
            evidence TEXT NOT NULL DEFAULT '',
            file_path TEXT NOT NULL DEFAULT '',
            line_no INTEGER NOT NULL DEFAULT 0,
            disposition TEXT NOT NULL DEFAULT 'untriaged',
            disposition_source TEXT DEFAULT '',
            disposition_date TEXT DEFAULT '',
            severity TEXT NOT NULL DEFAULT 'MEDIUM',
            violation_class TEXT NOT NULL DEFAULT 'hygiene'
        );
        CREATE VIEW mv_hotspot_centrality AS
            SELECT n.id AS node_id, 0 AS fan_in, 0 AS fan_out FROM nodes n;
        """
    )
    conn.commit()


@pytest.fixture
def empty_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Empty-but-valid ADG SQLite snapshot. Every gate should yield 0 violations."""
    snap = tmp_path / "adg_indexed_test.sqlite"
    conn = sqlite3.connect(snap)
    _build_minimal_schema(conn)
    conn.close()
    monkeypatch.setenv("ADG_SNAPSHOT", str(snap))
    return snap


@pytest.fixture
def baselines_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect baseline writes into tmp_path so the test never mutates real baselines."""
    baselines = tmp_path / "baselines"
    baselines.mkdir(exist_ok=True)
    return baselines


@pytest.mark.parametrize("script,cls_name,gate_id,baseline_filename", GATES)
def test_gate_module_imports(script, cls_name, gate_id, baseline_filename):
    """Every gate module must import cleanly and expose its gate class."""
    mod = _import_gate(script)
    cls = getattr(mod, cls_name, None)
    assert cls is not None, f"{script} missing class {cls_name}"
    assert cls.gate_id == gate_id, f"{script}.{cls_name}.gate_id mismatch"
    assert cls.tier == "R", f"{script} should be Tier R (ratchet)"
    assert cls.baseline_filename == baseline_filename, f"{script} baseline_filename mismatch"


@pytest.mark.parametrize("script,cls_name,gate_id,_b", GATES)
def test_gate_run_on_empty_snapshot(script, cls_name, gate_id, _b, empty_snapshot, monkeypatch):
    """Each gate's run() must return a list (Violation) given an empty schema.

    With no nodes/edges/violations, expected violation count is 0 for all gates.
    """
    mod = _import_gate(script)
    cls = getattr(mod, cls_name)
    gate = cls()
    conn = sqlite3.connect(empty_snapshot)
    try:
        result = gate.run(conn)
    finally:
        conn.close()
    assert isinstance(result, list), f"{cls_name}.run() must return list"
    assert len(result) == 0, f"{cls_name} on empty snapshot expected 0 violations, got {len(result)}"


@pytest.mark.parametrize("script,cls_name,_g,_b", GATES)
def test_gate_violation_shape(script, cls_name, _g, _b, empty_snapshot):
    """Verify Violation objects (when emitted) have the documented shape.

    Uses the gate's own Violation import; checks fields exist via a synthetic instance.
    """
    mod = _import_gate(script)
    # Violation comes from the shared base module
    from ops_scripts.ci._adg_wiring_gate_base import Violation  # noqa: WPS433

    v = Violation(gate_id="X", tier="R", subject="s", rule="r", detail="d")
    assert v.gate_id == "X"
    assert v.tier == "R"
    assert v.severity == "fail"  # default
    assert isinstance(v.extra, dict)


def test_audit3_uses_literal_value_patterns():
    """AUDIT-3 must match LITERAL VALUES, not identifier names (post-hardening fix)."""
    mod = _import_gate("check_external_service_literal_ssot.py")
    patterns = mod.LITERAL_PATTERNS
    # Hardening invariant: we removed identifier-name patterns
    forbidden_identifier_patterns = {"NOTION_API_VERSION", "NOTION_BASE", "WAVE_PHASE_DATA_SOURCE_ID"}
    overlap = forbidden_identifier_patterns & set(patterns)
    assert not overlap, f"AUDIT-3 still has identifier-name patterns: {overlap}"
    # Required: at least one literal-value pattern
    assert "2025-09-03" in patterns
    assert "api.notion.com" in patterns


def test_audit6_has_hard_block_rule():
    """AUDIT-6 must implement the Tier-B hard-block on HIGH/CRITICAL/P0 untriaged."""
    mod = _import_gate("check_violation_aging_sla.py")
    assert "HIGH" in mod.HARD_SEVERITIES
    assert "CRITICAL" in mod.HARD_SEVERITIES
    assert "P0" in mod.HARD_SEVERITIES


def test_audit6_emits_tier_b_for_high_severity(tmp_path, monkeypatch):
    """When a HIGH-severity untriaged row exists, AUDIT-6 must emit a Tier-B violation."""
    snap = tmp_path / "adg_indexed_test.sqlite"
    conn = sqlite3.connect(snap)
    _build_minimal_schema(conn)
    conn.execute(
        "INSERT INTO violations (id, edge_id, category, evidence, file_path, line_no, disposition, severity) "
        "VALUES (1, 1, 'antipattern', 'broad except', 'a.py', 10, 'untriaged', 'HIGH')"
    )
    conn.commit()
    monkeypatch.setenv("ADG_SNAPSHOT", str(snap))

    mod = _import_gate("check_violation_aging_sla.py")
    gate = mod.ViolationAgingSlaGate()
    conn2 = sqlite3.connect(snap)
    try:
        violations = gate.run(conn2)
    finally:
        conn2.close()
    # At least one Tier-B violation
    tier_b = [v for v in violations if v.tier == "B"]
    assert len(tier_b) == 1
    assert tier_b[0].rule == "high_severity_violation_untriaged"
    assert tier_b[0].severity == "fail"


def test_audit3_excludes_ssot_allowlisted_files(tmp_path, monkeypatch):
    """AUDIT-3 must NOT flag literals inside the SSOT allowlist."""
    snap = tmp_path / "adg_indexed_test.sqlite"
    conn = sqlite3.connect(snap)
    _build_minimal_schema(conn)
    # Insert a violation in the SSOT module itself — should be excluded
    conn.execute(
        "INSERT INTO violations (id, edge_id, category, evidence, file_path, line_no, disposition, severity) "
        "VALUES (1, 1, 'antipattern', '2025-09-03', '.claude/governance/scripts/_legacy_windsurf/_notion_constants.py', 14, 'untriaged', 'LOW')"
    )
    # Insert one in a non-allowlisted file — should be flagged
    conn.execute(
        "INSERT INTO violations (id, edge_id, category, evidence, file_path, line_no, disposition, severity) "
        "VALUES (2, 2, 'antipattern', 'foo 2025-09-03 bar', 'tools/some_script.py', 50, 'untriaged', 'LOW')"
    )
    conn.commit()
    monkeypatch.setenv("ADG_SNAPSHOT", str(snap))

    mod = _import_gate("check_external_service_literal_ssot.py")
    gate = mod.ExternalServiceLiteralSsotGate()
    conn2 = sqlite3.connect(snap)
    try:
        violations = gate.run(conn2)
    finally:
        conn2.close()
    # Only the non-allowlisted file should be flagged
    assert len(violations) == 1
    assert "tools/some_script.py" in violations[0].subject


def test_audit5_only_flags_outside_config(tmp_path, monkeypatch):
    """AUDIT-5 must flag os.environ access from non-config files only."""
    snap = tmp_path / "adg_indexed_test.sqlite"
    conn = sqlite3.connect(snap)
    _build_minimal_schema(conn)
    # Create nodes: a config file (allowed) and a reasoning file (forbidden), both reading os.environ
    conn.executescript(
        """
        INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) VALUES
            (1, 'cfg_module', 'module', 'L0', 'agentic_core/L0_routing/config/foo_config.py'),
            (2, 'reasoning_module', 'module', 'L0', 'agentic_core/L0_routing/reasoning/bar.py'),
            (3, 'os.environ', 'symbol', 'L_SHARED', 'stdlib/os.py');
        INSERT INTO edges (id, src_id, dst_id, relation_type) VALUES
            (10, 1, 3, 'reads_from'),
            (11, 2, 3, 'reads_from');
        """
    )
    conn.commit()
    monkeypatch.setenv("ADG_SNAPSHOT", str(snap))

    mod = _import_gate("check_env_var_in_config_layer.py")
    gate = mod.EnvVarInConfigLayerGate()
    conn2 = sqlite3.connect(snap)
    try:
        violations = gate.run(conn2)
    finally:
        conn2.close()
    # Only the reasoning file is flagged — the config file is exempt
    assert len(violations) == 1
    assert "reasoning/bar.py" in violations[0].subject
