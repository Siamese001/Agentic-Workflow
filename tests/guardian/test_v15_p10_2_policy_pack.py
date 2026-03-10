"""V15 P10.2 — Policy Pack + Validator Tests.

Validates schema enforcement, duplicate detection, enum checks,
forward-compat (unknown fields), and the real committed policy pack.
"""

from __future__ import annotations

import json
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
)
from ops_scripts.policy.validate_v15_policy_pack import validate_policy_pack

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REAL_PACK = REPO_ROOT / L0_ROUTING_DIR / "policy" / "v15_policy_pack.json"


def _valid_rule(rule_id: str = "TEST_001", **overrides):
    """Return a minimal valid rule dict."""
    base = {
        "rule_id": rule_id,
        "applies_to": "PIPE",
        "severity": "WARN",
        "description": "Test rule",
        "enabled": True,
    }
    base.update(overrides)
    return base


def _valid_pack(**overrides):
    """Return a minimal valid policy pack dict."""
    base = {
        "version": "1.0.0",
        "rules": [_valid_rule()],
    }
    base.update(overrides)
    return base


# ===========================================================================
# A) Valid Pack
# ===========================================================================


class TestValidPack:
    """Valid policy packs must pass."""

    def test_minimal_valid(self):
        code, errors, warnings = validate_policy_pack(_valid_pack())
        assert code == 0
        assert errors == []

    def test_multiple_rules(self):
        pack = _valid_pack(
            rules=[
                _valid_rule("R1"),
                _valid_rule("R2", applies_to="POLICY"),
                _valid_rule("R3", severity="HARD_FAIL", applies_to="HASH"),
            ],
        )
        code, errors, _ = validate_policy_pack(pack)
        assert code == 0
        assert errors == []

    def test_all_applies_to_values(self):
        rules = [
            _valid_rule(f"R_{at}", applies_to=at) for at in ["PIPE", "POLICY", "HASH", "CLOCK", "GENERAL"]
        ]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=rules))
        assert code == 0

    def test_all_severity_values(self):
        rules = [_valid_rule(f"R_{s}", severity=s) for s in ["WARN", "SOFT_FAIL", "HARD_FAIL"]]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=rules))
        assert code == 0

    def test_metadata_optional(self):
        rule = _valid_rule(metadata={"key": "value"})
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 0

    def test_real_committed_pack(self):
        """The actual committed policy pack must pass validation."""
        assert REAL_PACK.is_file(), f"Real pack not found: {REAL_PACK}"
        data = json.loads(REAL_PACK.read_text(encoding="utf-8"))
        code, errors, _ = validate_policy_pack(data)
        assert code == 0, f"Real pack validation failed: {errors}"


# ===========================================================================
# B) Missing Required Fields (exit 2)
# ===========================================================================


class TestMissingFields:
    """Missing required fields must fail with exit 2."""

    def test_missing_version(self):
        pack = _valid_pack()
        del pack["version"]
        code, errors, _ = validate_policy_pack(pack)
        assert code == 2
        assert any("version" in e for e in errors)

    def test_missing_rules(self):
        pack = _valid_pack()
        del pack["rules"]
        code, errors, _ = validate_policy_pack(pack)
        assert code == 2
        assert any("rules" in e for e in errors)

    def test_empty_rules(self):
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[]))
        assert code == 2
        assert any("at least one" in e for e in errors)

    def test_missing_rule_id(self):
        rule = _valid_rule()
        del rule["rule_id"]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("rule_id" in e for e in errors)

    def test_missing_applies_to(self):
        rule = _valid_rule()
        del rule["applies_to"]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("applies_to" in e for e in errors)

    def test_missing_severity(self):
        rule = _valid_rule()
        del rule["severity"]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("severity" in e for e in errors)

    def test_missing_description(self):
        rule = _valid_rule()
        del rule["description"]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("description" in e for e in errors)

    def test_missing_enabled(self):
        rule = _valid_rule()
        del rule["enabled"]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("enabled" in e for e in errors)


# ===========================================================================
# C) Bad Enum Values (exit 2)
# ===========================================================================


class TestBadEnums:
    """Invalid enum values must fail with exit 2."""

    def test_bad_applies_to(self):
        rule = _valid_rule(applies_to="INVALID")
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("applies_to" in e and "INVALID" in e for e in errors)

    def test_bad_severity(self):
        rule = _valid_rule(severity="CRITICAL")
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("severity" in e and "CRITICAL" in e for e in errors)

    def test_bad_enabled_type(self):
        rule = _valid_rule(enabled="yes")
        code, errors, _ = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 2
        assert any("enabled" in e and "boolean" in e for e in errors)


# ===========================================================================
# D) Duplicate rule_id (exit 3)
# ===========================================================================


class TestDuplicateRuleId:
    """Duplicate rule_ids must fail with exit 3."""

    def test_duplicate_detected(self):
        rules = [_valid_rule("DUP_001"), _valid_rule("DUP_001")]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=rules))
        assert code == 3
        assert any("Duplicate" in e and "DUP_001" in e for e in errors)

    def test_three_duplicates(self):
        rules = [_valid_rule("A"), _valid_rule("B"), _valid_rule("A")]
        code, errors, _ = validate_policy_pack(_valid_pack(rules=rules))
        assert code == 3


# ===========================================================================
# E) Forward Compatibility (unknown fields -> warn, not fail)
# ===========================================================================


class TestForwardCompat:
    """Unknown fields must produce warnings but not errors."""

    def test_unknown_top_level_field(self):
        pack = _valid_pack()
        pack["future_field"] = "something"
        code, errors, warnings = validate_policy_pack(pack)
        assert code == 0
        assert any("future_field" in w for w in warnings)

    def test_unknown_rule_field(self):
        rule = _valid_rule()
        rule["new_feature"] = 42
        code, errors, warnings = validate_policy_pack(_valid_pack(rules=[rule]))
        assert code == 0
        assert any("new_feature" in w for w in warnings)

    def test_updated_at_not_warned(self):
        """updated_at is a known optional field — no warning."""
        pack = _valid_pack()
        pack["updated_at"] = "2026-02-10"
        code, _, warnings = validate_policy_pack(pack)
        assert code == 0
        assert not any("updated_at" in w for w in warnings)


# ===========================================================================
# F) Ordering Warning
# ===========================================================================


class TestOrderingWarning:
    """Unsorted rule_ids should produce a warning (not an error)."""

    def test_sorted_no_warning(self):
        rules = [_valid_rule("A_001"), _valid_rule("B_002"), _valid_rule("C_003")]
        _, _, warnings = validate_policy_pack(_valid_pack(rules=rules))
        assert not any("sorted" in w.lower() for w in warnings)

    def test_unsorted_warns(self):
        rules = [_valid_rule("Z_001"), _valid_rule("A_002")]
        code, _, warnings = validate_policy_pack(_valid_pack(rules=rules))
        assert code == 0
        assert any("sorted" in w.lower() for w in warnings)
