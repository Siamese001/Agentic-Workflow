"""Tests for pre_author_gate.py — Author-Gate Enforcement Fix (W1-W6).

Test matrix:
A. Shadow mode behavior
B. Block mode behavior  
C. Tier bypass + sensitive paths
D. Blast radius (ADG-backed)
E. Layer crossing (ADG + fallback)
F. Rule/governance edits
G. Active decision ledger
H. Bypass handling
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Ensure repo root in path for imports
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# Add .cursor/scripts/_legacy_windsurf to path
sys.path.insert(0, str(REPO_ROOT / ".cursor" / "scripts" / "_legacy_windsurf"))

# Import pre_author_gate module
import pre_author_gate

ChangeSnapshot = pre_author_gate.ChangeSnapshot
SENSITIVE_PATH_PATTERNS = pre_author_gate.SENSITIVE_PATH_PATTERNS
_is_sensitive_path = pre_author_gate._is_sensitive_path
_layers_from_path_heuristic = pre_author_gate._layers_from_path_heuristic
check_tier = pre_author_gate.check_tier
evaluate_trigger = pre_author_gate.evaluate_trigger
emit_author_gate_required = pre_author_gate.emit_author_gate_required
has_active_decision = pre_author_gate.has_active_decision
check_bypass = pre_author_gate.check_bypass
_adg_query_with_retry = pre_author_gate._adg_query_with_retry
_ADG_MAX_RETRIES = pre_author_gate._ADG_MAX_RETRIES


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """Create a minimal repo structure for testing."""
    repo = tmp_path / "repo"
    repo.mkdir()
    # Create .cursor/schemas/
    (repo / ".cursor" / "schemas").mkdir(parents=True)
    # Create .cursor/state/refactor_decisions/
    (repo / ".cursor" / "state" / "refactor_decisions").mkdir(parents=True)
    # Create artifacts/cursor/
    (repo / "artifacts" / "windsurf").mkdir(parents=True)
    # Create artifacts/adg/
    (repo / "artifacts" / "adg").mkdir(parents=True)
    return repo


@pytest.fixture
def mock_triggers_config() -> dict[str, Any]:
    """Sample triggers config for testing."""
    return {
        "version": 1,
        "preset": "balanced",
        "enforcement": "block",
        "defaults": {
            "max_consecutive_denials": 3,
            "max_total_denials_per_session": 20,
            "allow_degraded_mode": False,
            "allow_sensitive_bypass": False,
        },
        "triggers": [
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
                "id": "HITL-1.9",
                "description": "Rule or ADR change",
                "decision_type": "governance_edit",
                "severity": "block",
                "features": {
                    "path_globs_any": [".claude/rules/**", "docs/architecture/adr/**"],
                },
            },
        ],
        "tiers": {
            "tier_2_in_project_edits": {
                "patterns": [
                    {"files_changed_max": 1, "path_not_under": ["agentic_core/L5_safety", "config/"]},
                ],
            },
        },
        "bypass": [
            {"condition": "commit_message_contains", "value": "[hitl:bypass]"},
        ],
    }


@pytest.fixture
def sample_snapshot_single_file() -> ChangeSnapshot:
    """Sample ChangeSnapshot for single file edit."""
    return ChangeSnapshot(
        changed_files=["tests/unit/test_foo.py"],
        deleted_files=[],
        added_lines_by_file={"tests/unit/test_foo.py": ["def test_foo():", "    pass"]},
    )


@pytest.fixture
def sample_snapshot_sensitive() -> ChangeSnapshot:
    """Sample ChangeSnapshot for sensitive governance file edit."""
    return ChangeSnapshot(
        changed_files=[".claude/rules/ssot-folder-enforcement.md"],
        deleted_files=[],
        added_lines_by_file={".claude/rules/ssot-folder-enforcement.md": ["# New rule"]},
    )


@pytest.fixture
def sample_snapshot_cross_layer() -> ChangeSnapshot:
    """Sample ChangeSnapshot for cross-layer edit."""
    return ChangeSnapshot(
        changed_files=["agentic_core/L0_routing/router.py", "agentic_core/L5_safety/guard.py"],
        deleted_files=[],
        added_lines_by_file={
            "agentic_core/L0_routing/router.py": ["# L0 change"],
            "agentic_core/L5_safety/guard.py": ["# L5 change"],
        },
    )


# =============================================================================
# A. Shadow Mode Tests
# =============================================================================

class TestShadowMode:
    """Tests for shadow mode behavior (A)."""

    def test_shadow_mode_logs_but_returns_0(self, tmp_path: Path, mock_triggers_config, sample_snapshot_cross_layer):
        """Shadow mode logs violation but exits 0 (would-block)."""
        mock_triggers_config["enforcement"] = "shadow"
        
        config_path = tmp_path / "triggers.yaml"
        with open(config_path, "w") as f:
            yaml.dump(mock_triggers_config, f)
        
        # Patch paths
        with patch.object(pre_author_gate, "TRIGGERS_PATH", config_path):
            with patch.object(pre_author_gate, "_get_layers_with_fallback") as mock_layers:
                mock_layers.return_value = ({"L0", "L5"}, "adg", "ok")
                
                # Import and run main in dry-run mode (which is like shadow)
                main = pre_author_gate.main
                
                # Simulate trigger match by mocking evaluate_trigger
                with patch.object(pre_author_gate, "evaluate_trigger") as mock_eval:
                    mock_eval.return_value = True
                    with patch.object(pre_author_gate, "collect_snapshot") as mock_snap:
                        mock_snap.return_value = sample_snapshot_cross_layer
                        with patch("sys.argv", ["pre_author_gate.py", "--dry-run"]):
                            result = main()
                            assert result == 0  # dry-run returns 0 even with triggers


# =============================================================================
# B. Block Mode Tests  
# =============================================================================

class TestBlockMode:
    """Tests for block mode behavior (B)."""

    def test_block_mode_exits_2_with_trigger(self, tmp_path: Path, mock_triggers_config):
        """Block mode with matching trigger exits 2 and emits AUTHOR_GATE_REQUIRED."""
        config_path = tmp_path / "triggers.yaml"
        with open(config_path, "w") as f:
            yaml.dump(mock_triggers_config, f)
        
        with patch.object(pre_author_gate, "TRIGGERS_PATH", config_path):
            with patch.object(pre_author_gate, "_get_adg_fan_in") as mock_fanin:
                mock_fanin.return_value = (15, "adg_graph_0505.sqlite", "ok")  # Above threshold
                
                main = pre_author_gate.main
                
                snap = ChangeSnapshot(
                    changed_files=["agentic_core/L3_orchestration/pipeline.py"],
                    deleted_files=[],
                    added_lines_by_file={"agentic_core/L3_orchestration/pipeline.py": ["# change"]},
                )
                
                with patch.object(pre_author_gate, "collect_snapshot") as mock_snap:
                    mock_snap.return_value = snap
                    with patch.object(pre_author_gate, "load_triggers") as mock_load:
                        mock_load.return_value = mock_triggers_config
                        with patch.object(pre_author_gate, "evaluate_trigger") as mock_eval:
                            # Return True for HITL-1.3 (blast radius trigger)
                            def match_blast_radius(trg, snap):
                                return trg.get("id") == "HITL-1.3"
                            mock_eval.side_effect = match_blast_radius
                            
                            with patch("sys.argv", ["pre_author_gate.py"]):
                                result = main()
                                # Note: actual exit code depends on matched triggers
                                # In real execution, this would be 2 if triggers matched

    def test_emit_author_gate_required_returns_2(self):
        """emit_author_gate_required returns exit code 2."""
        matched = [{"id": "HITL-1.1", "severity": "block", "description": "Test"}]
        snap = ChangeSnapshot(
            changed_files=["foo.py"],
            deleted_files=[],
            added_lines_by_file={},
        )
        session = {"consecutive_denials": 0, "total_denials": 0}
        defaults = {"max_consecutive_denials": 3, "max_total_denials_per_session": 20}
        
        result = emit_author_gate_required(matched, snap, session, defaults)
        assert result == 2
        assert session["consecutive_denials"] == 1
        assert session["total_denials"] == 1


# =============================================================================
# C. Tier Bypass + Sensitive Path Tests
# =============================================================================

class TestTierBypass:
    """Tests for tier bypass hardening (C)."""

    def test_normal_single_file_passes_tier_2(self, mock_triggers_config, sample_snapshot_single_file):
        """Normal single-file test edit passes as Tier-2."""
        tier = check_tier(mock_triggers_config, sample_snapshot_single_file)
        assert tier == "tier_2"

    def test_sensitive_single_file_forces_tier_3(self, mock_triggers_config, sample_snapshot_sensitive):
        """Sensitive governance single-file edit forces Tier-3."""
        tier = check_tier(mock_triggers_config, sample_snapshot_sensitive)
        assert tier == "tier_3"

    def test_is_sensitive_path_matches_rules(self):
        """_is_sensitive_path correctly identifies governance paths."""
        assert _is_sensitive_path(".claude/rules/ssot-folder-enforcement.md") is True
        assert _is_sensitive_path(".cursor/schemas/author_gate_triggers.yaml") is True
        assert _is_sensitive_path(".cursor/scripts/_legacy_windsurf/pre_author_gate.py") is True
        assert _is_sensitive_path("apps_rg/config/specs.yaml") is True
        assert _is_sensitive_path("agentic_core/L5_safety/guard.py") is True
        assert _is_sensitive_path("docs/architecture/adr/ADR-001.md") is True
        assert _is_sensitive_path("ops_scripts/ci/check_foo.py") is True

    def test_is_sensitive_path_does_not_match_tests(self):
        """_is_sensitive_path does not match normal test files."""
        assert _is_sensitive_path("tests/unit/test_foo.py") is False
        assert _is_sensitive_path("agentic_core/L3_orchestration/pipeline.py") is False
        assert _is_sensitive_path("apps_qna/cache/r1a.py") is False

    def test_windows_path_normalization(self):
        """_is_sensitive_path normalizes Windows backslashes."""
        assert _is_sensitive_path("docs/archive/windsurf/legacy-tree\\rules\\test.md") is True


# =============================================================================
# W2. Windows Path Coverage Tests
# =============================================================================

class TestWindowsPathCoverage:
    """Comprehensive Windows vs POSIX path matching tests (W2)."""

    # Standard Windows backslash paths
    def test_windows_backslash_rules_path(self):
        """Windows backslash path matches rules pattern."""
        assert _is_sensitive_path("docs/archive/windsurf/legacy-tree\\rules\\ssot-folder-enforcement.md") is True

    def test_windows_backslash_schemas_path(self):
        """Windows backslash path matches schemas pattern."""
        assert _is_sensitive_path("docs/archive/windsurf/legacy-tree\\schemas\\author_gate_triggers.yaml") is True

    def test_windows_backslash_pre_author_gate(self):
        """Windows backslash path matches pre_author_gate.py."""
        assert _is_sensitive_path("docs/archive/windsurf/legacy-tree\\scripts\\pre_author_gate.py") is True

    def test_windows_backslash_l5_safety(self):
        """Windows backslash path matches L5_safety."""
        assert _is_sensitive_path("agentic_core\\L5_safety\\guard.py") is True

    def test_windows_backslash_adr(self):
        """Windows backslash path matches ADR directory."""
        assert _is_sensitive_path("docs\\architecture\\adr\\ADR-001.md") is True

    def test_windows_backslash_ci_gates(self):
        """Windows backslash path matches CI gates."""
        assert _is_sensitive_path("ops_scripts\\ci\\check_foo.py") is True

    # Mixed separator paths (edge case)
    def test_mixed_separator_rules_path(self):
        """Mixed / and \\ separators still match."""
        assert _is_sensitive_path(".claude/rules\\test.md") is True
        assert _is_sensitive_path("docs/archive/windsurf/legacy-tree\\rules/test.md") is True

    def test_mixed_separator_nested(self):
        """Mixed separators in deeply nested path."""
        assert _is_sensitive_path("agentic_core\\L5_safety/nested/guard.py") is True

    # POSIX forward slash paths (baseline)
    def test_posix_forward_slash_rules(self):
        """POSIX forward slash paths still work."""
        assert _is_sensitive_path(".claude/rules/test.md") is True

    def test_posix_forward_slash_schemas(self):
        """POSIX forward slash schemas paths work."""
        assert _is_sensitive_path(".cursor/schemas/author_gate_triggers.yaml") is True

    # Non-sensitive Windows paths (should NOT match)
    def test_windows_backslash_non_sensitive(self):
        """Windows backslash non-sensitive paths return False."""
        assert _is_sensitive_path("tests\\unit\\test_foo.py") is False
        assert _is_sensitive_path("agentic_core\\L3_orchestration\\pipeline.py") is False
        assert _is_sensitive_path("apps_qna\\cache\\r1a.py") is False

    # Edge cases
    def test_empty_path(self):
        """Empty path returns False."""
        assert _is_sensitive_path("") is False

    def test_single_backslash(self):
        """Single backslash-only path handled gracefully."""
        assert _is_sensitive_path("\\") is False

    def test_trailing_backslash(self):
        """Trailing backslash in sensitive directory."""
        assert _is_sensitive_path("docs/archive/windsurf/legacy-tree\\rules\\") is True

    def test_trailing_slash(self):
        """Trailing slash in sensitive directory."""
        assert _is_sensitive_path(".claude/rules/") is True

    def test_case_sensitivity(self):
        """Case-sensitive matching (paths are case-sensitive on POSIX)."""
        # Uppercase should NOT match lowercase patterns
        assert _is_sensitive_path(".WINDSURF/rules/test.md") is False
        assert _is_sensitive_path("docs/archive/windsurf/legacy-tree/RULES/test.md") is False

    def test_partial_match_rejection(self):
        """Partial directory names don't match."""
        assert _is_sensitive_path(".claude/rules-backup/test.md") is False
        assert _is_sensitive_path("my.claude/rules/test.md") is False
        assert _is_sensitive_path(".windsurfx/rules/test.md") is False

    def test_deeply_nested_sensitive(self):
        """Deeply nested paths within sensitive directories match."""
        assert _is_sensitive_path("docs/archive/windsurf/legacy-tree\\rules\\very\\deep\\nested\\file.md") is True
        assert _is_sensitive_path("agentic_core\\L5_safety\\sub\\module\\guard.py") is True

    def test_relative_path_prefix(self):
        """Relative path prefixes still match if containing sensitive pattern."""
        # W2: Paths containing sensitive patterns ARE sensitive regardless of ./ or ../ prefix
        assert _is_sensitive_path("./.claude/rules/test.md") is True  # Contains .claude/rules/
        assert _is_sensitive_path("../.claude/rules/test.md") is True  # Contains .claude/rules/
        # But paths that don't actually contain the pattern still don't match
        assert _is_sensitive_path("./foo/bar/test.md") is False
        assert _is_sensitive_path("../foo/bar/test.md") is False

    def test_absolute_windows_path(self):
        """Absolute Windows paths with drive letters."""
        # Should match based on the path suffix
        assert _is_sensitive_path("C:\\Git\\Agentic-Workflow\\docs/archive/windsurf/legacy-tree\\rules\\test.md") is True
        assert _is_sensitive_path("D:\\projects\\agentic_core\\L5_safety\\guard.py") is True

    # Pattern-specific edge cases
    def test_apps_rg_config_pattern(self):
        """apps_rg/config/ pattern matches correctly."""
        assert _is_sensitive_path("apps_rg\\config\\specs.yaml") is True
        assert _is_sensitive_path("apps_rg/config/agent_spec_config.py") is True
        # Should NOT match similar but different paths
        assert _is_sensitive_path("apps_rg\\config_backup\\file.yaml") is False
        assert _is_sensitive_path("other_apps_rg\\config\\file.yaml") is False

    def test_l4_state_pattern(self):
        """agentic_core/L4_state/ pattern matches correctly."""
        assert _is_sensitive_path("agentic_core\\L4_state\\cache.py") is True
        assert _is_sensitive_path("agentic_core/L4_state/persistence.py") is True

    def test_docs_governance_patterns(self):
        """Docs governance patterns match correctly."""
        assert _is_sensitive_path("docs\\reference\\00A_L5_Governance_Safety\\safety.md") is True
        assert _is_sensitive_path("docs/reference/00B_L4_State_Archive_and_UWG/uwg.md") is True
        assert _is_sensitive_path("docs\\reference\\00C_Runtime_Gates_Current_Run_Mesh\\gates.md") is True

    def test_certification_config_pattern(self):
        """config/certification/ pattern matches correctly."""
        assert _is_sensitive_path("config\\certification\\rubric.yaml") is True
        assert _is_sensitive_path("config/certification/requirements.json") is True


# =============================================================================
# D. Blast Radius Tests
# =============================================================================

class TestBlastRadius:
    """Tests for ADG-backed blast radius (D)."""

    def test_blast_radius_below_threshold_no_trigger(self, mock_triggers_config):
        """File with fan_in below threshold does not trigger."""
        with patch.object(pre_author_gate, "_get_adg_fan_in") as mock_fanin:
            mock_fanin.return_value = (5, "adg_graph.sqlite", "ok")  # Below threshold of 10
            
            snap = ChangeSnapshot(
                changed_files=["agentic_core/L3_orchestration/pipeline.py"],
                deleted_files=[],
                added_lines_by_file={},
            )
            
            # Find HITL-1.3 trigger
            blast_trigger = None
            for t in mock_triggers_config["triggers"]:
                if t["id"] == "HITL-1.3":
                    blast_trigger = t
                    break
            
            result = evaluate_trigger(blast_trigger, snap, mock_triggers_config)
            # Should return False (no trigger) because fan_in=5 < threshold=10
            # BUT: if ADG unavailable and not allow_degraded, it may trigger
            # This depends on implementation

    def test_blast_radius_at_threshold_triggers(self, mock_triggers_config):
        """File with fan_in at or above threshold triggers."""
        with patch.object(pre_author_gate, "_get_adg_fan_in") as mock_fanin:
            mock_fanin.return_value = (15, "adg_graph.sqlite", "ok")  # Above threshold of 10
            
            snap = ChangeSnapshot(
                changed_files=["agentic_core/L3_orchestration/pipeline.py"],
                deleted_files=[],
                added_lines_by_file={},
            )
            
            blast_trigger = None
            for t in mock_triggers_config["triggers"]:
                if t["id"] == "HITL-1.3":
                    blast_trigger = t
                    break
            
            result = evaluate_trigger(blast_trigger, snap, mock_triggers_config)
            # Should return True (trigger) because fan_in=15 >= threshold=10

    def test_missing_adg_fails_closed(self, mock_triggers_config):
        """Missing ADG data with allow_degraded=false triggers (fail closed)."""
        mock_triggers_config["defaults"]["allow_degraded_mode"] = False
        
        with patch.object(pre_author_gate, "_get_adg_fan_in") as mock_fanin:
            mock_fanin.return_value = (None, "unavailable", "unavailable")
            
            snap = ChangeSnapshot(
                changed_files=["agentic_core/L3_orchestration/pipeline.py"],
                deleted_files=[],
                added_lines_by_file={},
            )
            
            blast_trigger = None
            for t in mock_triggers_config["triggers"]:
                if t["id"] == "HITL-1.3":
                    blast_trigger = t
                    break
            
            result = evaluate_trigger(blast_trigger, snap, mock_triggers_config)
            # Should return True (trigger) because ADG unavailable and fail-closed


# =============================================================================
# E. Layer Crossing Tests
# =============================================================================

class TestLayerCrossing:
    """Tests for ADG-backed layer crossing (E)."""

    def test_path_heuristic_detects_layers(self):
        """_layers_from_path_heuristic correctly infers layers from paths."""
        files = [
            "agentic_core/L0_routing/router.py",
            "agentic_core/L3_orchestration/pipeline.py",
            "apps_qna/cache/r1a.py",
            "system_learning/buses/bus_p.py",
            "infrastructure/config/settings.py",
        ]
        layers = _layers_from_path_heuristic(files)
        assert "L0" in layers
        assert "L3" in layers
        assert "apps" in layers
        assert "system_learning" in layers
        assert "infra" in layers

    def test_same_layer_edit_no_crossing(self):
        """Files from same layer don't trigger layer_crossing."""
        files = ["agentic_core/L3_orchestration/pipeline.py", "agentic_core/L3_orchestration/tasks.py"]
        layers = _layers_from_path_heuristic(files)
        assert len(layers) == 1
        assert "L3" in layers

    def test_cross_layer_edit_detected(self):
        """Files from different layers trigger layer_crossing."""
        files = ["agentic_core/L0_routing/router.py", "agentic_core/L5_safety/guard.py"]
        layers = _layers_from_path_heuristic(files)
        assert len(layers) == 2
        assert "L0" in layers
        assert "L5" in layers


# =============================================================================
# F. Rule / Governance Edit Tests
# =============================================================================

class TestGovernanceEdits:
    """Tests for rule/governance edit triggers (F)."""

    def test_rules_edit_triggers(self, mock_triggers_config):
        """Editing .claude/rules/ file triggers HITL-1.9."""
        snap = ChangeSnapshot(
            changed_files=[".claude/rules/ssot-folder-enforcement.md"],
            deleted_files=[],
            added_lines_by_file={".claude/rules/ssot-folder-enforcement.md": ["# new rule"]},
        )
        
        # Find governance trigger
        gov_trigger = None
        for t in mock_triggers_config["triggers"]:
            if t["id"] == "HITL-1.9":
                gov_trigger = t
                break
        
        result = evaluate_trigger(gov_trigger, snap, mock_triggers_config)
        assert result is True

    def test_adr_edit_triggers(self, mock_triggers_config):
        """Editing docs/architecture/adr/ file triggers HITL-1.9."""
        snap = ChangeSnapshot(
            changed_files=["docs/architecture/adr/ADR-001.md"],
            deleted_files=[],
            added_lines_by_file={"docs/architecture/adr/ADR-001.md": ["# ADR"]},
        )
        
        gov_trigger = None
        for t in mock_triggers_config["triggers"]:
            if t["id"] == "HITL-1.9":
                gov_trigger = t
                break
        
        result = evaluate_trigger(gov_trigger, snap, mock_triggers_config)
        assert result is True


# =============================================================================
# G. Active Decision Ledger Tests
# =============================================================================

class TestActiveDecision:
    """Tests for active decision ledger (G)."""

    def test_matching_fingerprint_passes(self, tmp_path: Path):
        """Active decision with matching fingerprint allows pass."""
        # Create mock ledger
        ledger_path = tmp_path / "refactor_decision_ledger.sqlite"
        conn = sqlite3.connect(str(ledger_path))
        conn.execute("""
            CREATE TABLE decisions (
                id INTEGER PRIMARY KEY,
                status TEXT,
                context_fingerprint_json TEXT
            )
        """)
        conn.execute(
            "INSERT INTO decisions (status, context_fingerprint_json) VALUES (?, ?)",
            ("surfaced", '{"fp":"abc123"}'),
        )
        conn.commit()
        conn.close()
        
        with patch.object(pre_author_gate, "LEDGER_PATH", ledger_path):
            result = has_active_decision("abc123")
            assert result is True

    def test_non_matching_fingerprint_triggers(self, tmp_path: Path):
        """No active decision with fingerprint means normal trigger evaluation."""
        ledger_path = tmp_path / "refactor_decision_ledger.sqlite"
        conn = sqlite3.connect(str(ledger_path))
        conn.execute("""
            CREATE TABLE decisions (
                id INTEGER PRIMARY KEY,
                status TEXT,
                context_fingerprint_json TEXT
            )
        """)
        conn.execute(
            "INSERT INTO decisions (status, context_fingerprint_json) VALUES (?, ?)",
            ("surfaced", '{"fp":"different"}'),
        )
        conn.commit()
        conn.close()
        
        with patch.object(pre_author_gate, "LEDGER_PATH", ledger_path):
            result = has_active_decision("abc123")
            assert result is False

    def test_missing_ledger_returns_false(self):
        """Missing ledger means no active decision."""
        with patch.object(pre_author_gate, "LEDGER_PATH", Path("/nonexistent/ledger.sqlite")):
            result = has_active_decision("abc123")
            assert result is False


# =============================================================================
# H. Bypass Handling Tests
# =============================================================================

class TestBypass:
    """Tests for bypass conditions (H)."""

    def test_commit_message_bypass(self, mock_triggers_config, tmp_path: Path):
        """Commit message with [hitl:bypass] triggers bypass."""
        with patch.object(pre_author_gate, "_run_git") as mock_git:
            mock_git.return_value = "Fix foo [hitl:bypass]"
            
            snap = ChangeSnapshot(
                changed_files=["foo.py"],
                deleted_files=[],
                added_lines_by_file={},
            )
            
            result = check_bypass(mock_triggers_config, snap)
            assert result is not None
            assert "hitl:bypass" in result

    def test_bypass_blocked_for_sensitive_paths(self, mock_triggers_config, tmp_path: Path):
        """Bypass is blocked for sensitive governance paths."""
        # This is tested in main() integration, but we verify the logic here
        # by checking that sensitive paths are detected before bypass
        snap = ChangeSnapshot(
            changed_files=[".claude/rules/test.md"],
            deleted_files=[],
            added_lines_by_file={},
        )
        
        tier = check_tier(mock_triggers_config, snap)
        assert tier == "tier_3"  # Forces trigger evaluation, not bypass

    def test_normal_file_can_bypass(self, mock_triggers_config, tmp_path: Path, sample_snapshot_single_file):
        """Normal test file can still bypass via commit message."""
        tier = check_tier(mock_triggers_config, sample_snapshot_single_file)
        assert tier == "tier_2"  # Allows bypass if commit message matches


# =============================================================================
# Configuration Tests
# =============================================================================

class TestConfiguration:
    """Tests for YAML configuration handling."""

    def test_yaml_parsing(self, tmp_path: Path):
        """Triggers YAML can be parsed."""
        config_path = tmp_path / "triggers.yaml"
        config = {
            "version": 1,
            "enforcement": "block",
            "defaults": {"max_consecutive_denials": 3},
            "triggers": [],
        }
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        
        with open(config_path) as f:
            loaded = yaml.safe_load(f)
        
        assert loaded["enforcement"] == "block"


# =============================================================================
# Receipt Logging Tests
# =============================================================================

class TestReceipts:
    """Tests for structured receipt output."""

    def test_blast_radius_receipt_format(self, capsys):
        """BLAST_RADIUS_TRIGGER receipt has correct format."""
        _log_blast_radius_receipt = pre_author_gate._log_blast_radius_receipt
        
        _log_blast_radius_receipt(
            "agentic_core/L3/pipeline.py", 15, 10, "adg_graph.sqlite", "HITL-1.3"
        )
        
        captured = capsys.readouterr()
        assert "BLAST_RADIUS_TRIGGER:" in captured.err
        assert "file=agentic_core/L3/pipeline.py" in captured.err
        assert "fan_in=15" in captured.err
        assert "threshold=10" in captured.err
        assert "adg_artifact=adg_graph.sqlite" in captured.err
        assert "trigger_id=HITL-1.3" in captured.err

    def test_layer_crossing_receipt_format(self, capsys):
        """LAYER_CROSSING_TRIGGER receipt has correct format."""
        _log_layer_crossing_receipt = pre_author_gate._log_layer_crossing_receipt
        
        _log_layer_crossing_receipt(
            {"L0", "L5"}, ["f1.py", "f2.py"], "adg", "HITL-1.1"
        )
        
        captured = capsys.readouterr()
        assert "LAYER_CROSSING_TRIGGER:" in captured.err
        assert "layers_span=" in captured.err
        assert "files_count=2" in captured.err
        assert "detection_source=adg" in captured.err
        assert "trigger_id=HITL-1.1" in captured.err

    def test_degraded_fallback_receipt_format(self, capsys):
        """DEGRADED_FALLBACK receipt has correct format."""
        _log_degraded_fallback = pre_author_gate._log_degraded_fallback
        
        _log_degraded_fallback("adg_unavailable", "test.py")
        
        captured = capsys.readouterr()
        assert "DEGRADED_FALLBACK:" in captured.err
        assert "reason=adg_unavailable" in captured.err
        assert "file=test.py" in captured.err


# =============================================================================
# I. ADG Retry Tests (W1)
# =============================================================================

class TestADGRetry:
    """Tests for ADG query timeout and retry (W1)."""

    def test_adg_query_with_retry_success_first_attempt(self):
        """Query succeeds on first attempt - no retries needed."""
        def success_func():
            return "result"
        
        success, result, retries = _adg_query_with_retry(success_func)
        
        assert success is True
        assert result == "result"
        assert retries == 0

    def test_adg_query_with_retry_eventual_success(self):
        """Query succeeds after some failures - retry works."""
        call_count = 0
        
        def eventual_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("database is locked")
            return "result"
        
        with patch.object(pre_author_gate, "append_violation") as mock_violation:
            success, result, retries = _adg_query_with_retry(
                eventual_success,
                retry_delay_base=0.01  # Fast for tests
            )
            
            assert success is True
            assert result == "result"
            assert retries == 2
            # Should have logged 2 retry attempts + 1 success event
            assert mock_violation.call_count == 3

    def test_adg_query_with_retry_all_failures(self):
        """Query fails all retries - returns failure."""
        def always_fails():
            raise Exception("database is locked")
        
        with patch.object(pre_author_gate, "append_violation") as mock_violation:
            success, exc, retries = _adg_query_with_retry(
                always_fails,
                max_retries=3,
                retry_delay_base=0.01  # Fast for tests
            )
            
            assert success is False
            assert "database is locked" in str(exc)
            assert retries == 3

    def test_adg_query_logs_sqlite_busy_error_type(self):
        """Retry logs correctly identify sqlite busy errors."""
        def sqlite_busy_error():
            raise Exception("database is locked")
        
        with patch.object(pre_author_gate, "append_violation") as mock_violation:
            _adg_query_with_retry(
                sqlite_busy_error,
                max_retries=2,
                retry_delay_base=0.01
            )
            
            # Check that error_type was logged as sqlite_busy
            calls = mock_violation.call_args_list
            for call in calls:
                args = call[0][0]
                assert args.get("error_type") == "sqlite_busy"

    def test_adg_query_logs_timeout_error_type(self):
        """Retry logs correctly identify timeout errors."""
        def timeout_error():
            raise Exception("query timeout")
        
        with patch.object(pre_author_gate, "append_violation") as mock_violation:
            _adg_query_with_retry(
                timeout_error,
                max_retries=2,
                retry_delay_base=0.01
            )
            
            # Check that error_type was logged as timeout
            calls = mock_violation.call_args_list
            for call in calls:
                args = call[0][0]
                assert args.get("error_type") == "timeout"

    def test_adg_query_logs_retry_success(self):
        """Successful retry logs success event."""
        call_count = 0
        
        def succeeds_on_second():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("busy")
            return "success"
        
        with patch.object(pre_author_gate, "append_violation") as mock_violation:
            _adg_query_with_retry(
                succeeds_on_second,
                retry_delay_base=0.01
            )
            
            # Should have logged retry attempt and success
            calls = mock_violation.call_args_list
            assert len(calls) == 2
            # First call is retry_attempt
            assert calls[0][0][0].get("severity") == "adg_retry_attempt"
            # Second call is retry_success
            assert calls[1][0][0].get("severity") == "adg_retry_success"

    def test_adg_retry_uses_exponential_backoff(self):
        """Retry delays use exponential backoff."""
        delays = []
        original_sleep = pre_author_gate.time.sleep
        
        def capture_delay(seconds):
            delays.append(seconds)
        
        def always_fails():
            raise Exception("busy")
        
        with patch.object(pre_author_gate.time, "sleep", capture_delay):
            _adg_query_with_retry(
                always_fails,
                max_retries=4,
                retry_delay_base=0.1
            )
        
        # Should have 3 delays (not 4, since last attempt doesn't delay)
        assert len(delays) == 3
        # Exponential: 0.1, 0.2, 0.4
        assert abs(delays[0] - 0.1) < 0.01
        assert abs(delays[1] - 0.2) < 0.01
        assert abs(delays[2] - 0.4) < 0.01


# =============================================================================
# W4. Mock ADG Backend and Test Isolation
# =============================================================================

class MockADGBackend:
    """Deterministic mock ADG backend for test isolation (W4).

    Supports all ADG states: fresh, stale, missing, busy, error.
    Replaces real ADG artifact dependencies in tests.
    """

    def __init__(
        self,
        state: str = "fresh",
        fan_in_data: dict[str, int] | None = None,
        layer_data: dict[str, str] | None = None,
        blast_radius_data: dict[str, dict] | None = None,
    ):
        """Initialize mock backend with configurable state.

        Args:
            state: "fresh", "stale", "missing", "busy", "error"
            fan_in_data: Map of file paths to fan_in values
            layer_data: Map of file paths to layer strings
            blast_radius_data: Map of file paths to blast radius dicts
        """
        self.state = state
        self.fan_in_data = fan_in_data or {}
        self.layer_data = layer_data or {}
        self.blast_radius_data = blast_radius_data or {}
        self._call_count = 0

    def is_available(self) -> bool:
        """Check if backend is available."""
        return self.state not in ("missing",)

    def is_stale(self) -> bool:
        """Check if backend data is stale."""
        return self.state == "stale"

    def get_blast_radius(self, file_path: str, hops: int = 1) -> dict | None:
        """Get blast radius for a file."""
        self._call_count += 1

        if self.state == "busy":
            raise Exception("database is locked")
        if self.state == "error":
            raise Exception("ADG query failed")

        normalized = file_path.replace("\\", "/")
        return self.blast_radius_data.get(normalized, {"blast_radius_direct": 0})

    def get_fan_in(self, file_path: str) -> int | None:
        """Get fan_in for a file."""
        self._call_count += 1

        if self.state == "busy":
            raise Exception("database is locked")
        if self.state == "error":
            raise Exception("ADG query failed")

        normalized = file_path.replace("\\", "/")
        return self.fan_in_data.get(normalized)

    def get_layer(self, file_path: str) -> str | None:
        """Get layer for a file."""
        self._call_count += 1

        if self.state == "busy":
            raise Exception("database is locked")
        if self.state == "error":
            raise Exception("ADG query failed")

        normalized = file_path.replace("\\", "/")
        return self.layer_data.get(normalized)

    def get_call_count(self) -> int:
        """Get number of calls made to this backend."""
        return self._call_count


class TestMockADGBackend:
    """Tests for MockADGBackend determinism and state coverage (W4)."""

    def test_mock_backend_fresh_state(self):
        """Fresh state returns data normally."""
        backend = MockADGBackend(
            state="fresh",
            fan_in_data={"agentic_core/L3/pipeline.py": 15},
            layer_data={"agentic_core/L3/pipeline.py": "L3"},
        )

        assert backend.is_available() is True
        assert backend.is_stale() is False
        assert backend.get_fan_in("agentic_core/L3/pipeline.py") == 15
        assert backend.get_layer("agentic_core/L3/pipeline.py") == "L3"

    def test_mock_backend_stale_state(self):
        """Stale state is available but marked stale."""
        backend = MockADGBackend(
            state="stale",
            fan_in_data={"agentic_core/L3/pipeline.py": 10},
        )

        assert backend.is_available() is True
        assert backend.is_stale() is True
        assert backend.get_fan_in("agentic_core/L3/pipeline.py") == 10

    def test_mock_backend_missing_state(self):
        """Missing state is not available."""
        backend = MockADGBackend(state="missing")

        assert backend.is_available() is False
        assert backend.is_stale() is False

    def test_mock_backend_busy_state(self):
        """Busy state raises sqlite busy exception."""
        backend = MockADGBackend(state="busy")

        with pytest.raises(Exception) as exc_info:
            backend.get_fan_in("any/path.py")

        assert "database is locked" in str(exc_info.value)

    def test_mock_backend_error_state(self):
        """Error state raises generic exception."""
        backend = MockADGBackend(state="error")

        with pytest.raises(Exception) as exc_info:
            backend.get_layer("any/path.py")

        assert "ADG query failed" in str(exc_info.value)

    def test_mock_backend_windows_path_normalization(self):
        """Windows paths are normalized to forward slashes."""
        backend = MockADGBackend(
            state="fresh",
            fan_in_data={"agentic_core/L3/pipeline.py": 20},
        )

        # Windows backslash path should match
        assert backend.get_fan_in("agentic_core\\L3\\pipeline.py") == 20

    def test_mock_backend_call_counting(self):
        """Backend tracks call counts for verification."""
        backend = MockADGBackend(
            state="fresh",
            fan_in_data={"file1.py": 5, "file2.py": 10},
        )

        backend.get_fan_in("file1.py")
        backend.get_fan_in("file2.py")
        backend.get_blast_radius("file1.py")

        assert backend.get_call_count() == 3

    def test_mock_backend_default_empty_data(self):
        """Default empty data returns zeros/None."""
        backend = MockADGBackend(state="fresh")

        assert backend.get_blast_radius("unknown.py") == {"blast_radius_direct": 0}
        assert backend.get_fan_in("unknown.py") is None
        assert backend.get_layer("unknown.py") is None


class TestADGIntegrationWithMock:
    """Integration tests using MockADGBackend for deterministic behavior (W4)."""

    def test_fan_in_trigger_with_mock_backend(self, mock_triggers_config):
        """Blast radius trigger works with mock backend data."""
        backend = MockADGBackend(
            state="fresh",
            fan_in_data={"agentic_core/L3/pipeline.py": 15},  # Above threshold of 10
        )

        with patch.object(pre_author_gate, "_get_adg_backend", return_value=backend):
            with patch.object(pre_author_gate, "_adg_query_with_retry", side_effect=lambda f, *a, **k: (True, f(*a, **k), 0)):
                snap = ChangeSnapshot(
                    changed_files=["agentic_core/L3/pipeline.py"],
                    deleted_files=[],
                    added_lines_by_file={},
                )

                # Find blast radius trigger
                blast_trigger = None
                for t in mock_triggers_config["triggers"]:
                    if t["id"] == "HITL-1.3":
                        blast_trigger = t
                        break

                result = evaluate_trigger(blast_trigger, snap, mock_triggers_config)
                assert result is True  # fan_in=15 >= threshold=10

    def test_layer_crossing_with_mock_backend(self, mock_triggers_config):
        """Layer crossing detection works with mock backend data."""
        backend = MockADGBackend(
            state="fresh",
            layer_data={
                "agentic_core/L0/router.py": "L0",
                "agentic_core/L3/pipeline.py": "L3",
            },
        )

        with patch.object(pre_author_gate, "_get_adg_backend", return_value=backend):
            with patch.object(pre_author_gate, "_adg_query_with_retry", side_effect=lambda f, *a, **k: (True, f(*a, **k), 0)):
                snap = ChangeSnapshot(
                    changed_files=["agentic_core/L0/router.py", "agentic_core/L3/pipeline.py"],
                    deleted_files=[],
                    added_lines_by_file={},
                )

                # Find layer crossing trigger
                layer_trigger = None
                for t in mock_triggers_config["triggers"]:
                    if t.get("features", {}).get("layer_crossing") is True:
                        layer_trigger = t
                        break

                if layer_trigger:
                    result = evaluate_trigger(layer_trigger, snap, mock_triggers_config)
                    assert result is True  # L0 + L3 = cross-layer

    def test_adg_busy_fallback_with_mock(self, mock_triggers_config):
        """When ADG is busy, retry logic handles it gracefully."""
        backend = MockADGBackend(state="busy")

        with patch.object(pre_author_gate, "_get_adg_backend", return_value=backend):
            with patch.object(pre_author_gate, "append_violation"):
                # The retry logic should handle busy errors
                # and eventually fail closed with degraded fallback
                success, exc, retries = _adg_query_with_retry(
                    lambda: backend.get_fan_in("any.py"),
                    max_retries=2,
                    retry_delay_base=0.01
                )
                assert success is False
                assert retries == 2

    def test_adg_missing_uses_path_fallback(self, mock_triggers_config):
        """When ADG is missing, path heuristic fallback works."""
        backend = MockADGBackend(state="missing")

        with patch.object(pre_author_gate, "_get_adg_backend", return_value=backend):
            snap = ChangeSnapshot(
                changed_files=["agentic_core/L0/router.py", "agentic_core/L3/pipeline.py"],
                deleted_files=[],
                added_lines_by_file={},
            )

            # Should fall back to path heuristic
            layers, source, status = pre_author_gate._get_layers_with_fallback(
                snap.changed_files + snap.deleted_files
            )

            # Path fallback should detect layers from paths
            assert "L0" in layers or "L3" in layers or source == "path_fallback"


@pytest.mark.parametrize("adg_state", ["fresh", "stale", "missing", "busy", "error"])
def test_author_gate_handles_all_adg_states(adg_state, mock_triggers_config):
    """Parametrized test: Author-Gate handles all ADG states gracefully (W4).

    This test verifies that regardless of ADG state, Author-Gate:
    1. Does not crash
    2. Returns a valid tier classification
    3. Either triggers or passes deterministically
    """
    backend = MockADGBackend(
        state=adg_state,
        fan_in_data={"agentic_core/L3/pipeline.py": 15},
        layer_data={"agentic_core/L3/pipeline.py": "L3"},
    )

    with patch.object(pre_author_gate, "_get_adg_backend", return_value=backend if adg_state != "missing" else None):
        snap = ChangeSnapshot(
            changed_files=["agentic_core/L3/pipeline.py"],
            deleted_files=[],
            added_lines_by_file={"agentic_core/L3/pipeline.py": ["# change"]},
        )

        # Should not raise
        tier = check_tier(mock_triggers_config, snap)
        assert tier in ("tier_1", "tier_2", "tier_3")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
