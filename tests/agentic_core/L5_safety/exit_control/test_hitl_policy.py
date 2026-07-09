"""Unit tests for L5 runtime HITL policy classifier.

Covers ADR-023 §3.1 classification precedence, timeout/fallback resolution,
approver-pool resolution, and policy YAML load/validation paths.

Scope: runtime HITL (v30 step [5]) — NOT developer-loop Author-Gate.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from agentic_core.L5_safety.exit_control import (
    HitlClass,
    HitlPolicy,
    PolicyLoadError,
    classify_escalation_class,
    load_policy,
    resolve_approver_pool,
    set_fallback,
    set_timeout,
)
from agentic_core.L5_safety.exit_control.hitl_classes import (
    ALL_CLASSES,
    CLASS_NAMES,
    is_valid_class,
)
from agentic_core.L5_safety.exit_control.hitl_policy import (
    DEFAULT_POLICY_PATH,
    ClassPolicy,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_YAML = """
version: 1
thresholds:
  novelty_min: 0.72
  confidence_max: 0.60
classes:
  financial:
    timeout_s: 3600
    fallback: DENY
    approver_pool: finance_oncall
  safety:
    timeout_s: 1800
    fallback: DENY
    approver_pool: safety_oncall
  regulated:
    timeout_s: 7200
    fallback: DENY
    approver_pool: compliance_oncall
  novel_context:
    timeout_s: 900
    fallback: DENY
    approver_pool: ops_oncall
  low_confidence:
    timeout_s: 600
    fallback: DENY
    approver_pool: ops_oncall
  policy_override:
    timeout_s: 86400
    fallback: DENY
    approver_pool: policy_board
precedence:
  - policy_override
  - regulated
  - safety
  - financial
  - novel_context
  - low_confidence
"""


@pytest.fixture
def policy_file(tmp_path: Path) -> Path:
    p = tmp_path / "runtime_hitl_policy.yaml"
    p.write_text(VALID_YAML, encoding="utf-8")
    logging.info("C3 write receipt: tests/agentic_core/L5_safety/exit_control/test_hitl_policy.py write side effect recorded")
    return p


@pytest.fixture
def policy(policy_file: Path) -> HitlPolicy:
    return load_policy(policy_file, policy_snapshot="test-snap")


# ---------------------------------------------------------------------------
# Class taxonomy
# ---------------------------------------------------------------------------


def test_class_names_match_enum():
    assert CLASS_NAMES == {c.value for c in HitlClass}
    assert len(ALL_CLASSES) == 6


@pytest.mark.parametrize("name", sorted(CLASS_NAMES))
def test_is_valid_class_true(name: str):
    assert is_valid_class(name)


def test_is_valid_class_false():
    assert not is_valid_class("unknown")
    assert not is_valid_class("")


# ---------------------------------------------------------------------------
# load_policy — happy + error paths
# ---------------------------------------------------------------------------


def test_load_policy_happy(policy: HitlPolicy):
    assert policy.version == 1
    assert policy.novelty_min == 0.72
    assert policy.confidence_max == 0.60
    assert set(policy.classes) == set(HitlClass)
    assert policy.precedence[0] == HitlClass.POLICY_OVERRIDE
    assert policy.policy_snapshot == "test-snap"


def test_load_policy_default_path_constant():
    assert DEFAULT_POLICY_PATH == Path("config/runtime_hitl_policy.yaml")


def test_load_policy_missing_file(tmp_path: Path):
    with pytest.raises(PolicyLoadError, match="Cannot read"):
        load_policy(tmp_path / "missing.yaml")


def test_load_policy_malformed_yaml(tmp_path: Path):
    p = tmp_path / "bad.yaml"
    p.write_text("version: 1\nclasses: [unterminated", encoding="utf-8")
    with pytest.raises(PolicyLoadError, match="Malformed YAML"):
        load_policy(p)


def test_load_policy_non_mapping_root(tmp_path: Path):
    p = tmp_path / "list.yaml"
    p.write_text("- one\n- two\n", encoding="utf-8")
    with pytest.raises(PolicyLoadError, match="must be a mapping"):
        load_policy(p)


def test_load_policy_wrong_version(tmp_path: Path):
    p = tmp_path / "v2.yaml"
    p.write_text("version: 2\n", encoding="utf-8")
    with pytest.raises(PolicyLoadError, match="Unsupported policy version"):
        load_policy(p)


def test_load_policy_bad_thresholds(tmp_path: Path):
    p = tmp_path / "bad_thr.yaml"
    p.write_text(
        "version: 1\nthresholds:\n  novelty_min: not_a_number\n  confidence_max: 0.5\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyLoadError, match="Invalid thresholds"):
        load_policy(p)


def test_load_policy_empty_classes(tmp_path: Path):
    p = tmp_path / "empty.yaml"
    p.write_text(
        "version: 1\nthresholds:\n  novelty_min: 0.7\n  confidence_max: 0.6\nclasses: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyLoadError, match="non-empty mapping"):
        load_policy(p)


def test_load_policy_unknown_class(tmp_path: Path):
    p = tmp_path / "unknown.yaml"
    p.write_text(
        "version: 1\n"
        "thresholds: {novelty_min: 0.7, confidence_max: 0.6}\n"
        "classes:\n  bogus: {timeout_s: 1, fallback: DENY, approver_pool: x}\n"
        "precedence: [bogus]\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyLoadError, match="Unknown HITL class"):
        load_policy(p)


def test_load_policy_non_mapping_class_entry(tmp_path: Path):
    p = tmp_path / "nonmap.yaml"
    p.write_text(
        "version: 1\n"
        "thresholds: {novelty_min: 0.7, confidence_max: 0.6}\n"
        "classes:\n  financial: 42\n"
        "precedence: [financial]\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyLoadError, match="must be a mapping"):
        load_policy(p)


def test_load_policy_class_missing_required_key(tmp_path: Path):
    p = tmp_path / "missing_key.yaml"
    p.write_text(
        "version: 1\n"
        "thresholds: {novelty_min: 0.7, confidence_max: 0.6}\n"
        "classes:\n  financial: {fallback: DENY, approver_pool: x}\n"
        "precedence: [financial]\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyLoadError, match="financial"):
        load_policy(p)


def test_load_policy_missing_class_policies(tmp_path: Path):
    p = tmp_path / "partial.yaml"
    p.write_text(
        "version: 1\n"
        "thresholds: {novelty_min: 0.7, confidence_max: 0.6}\n"
        "classes:\n  financial: {timeout_s: 10, fallback: DENY, approver_pool: x}\n"
        "precedence: [financial]\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyLoadError, match="Missing class policies"):
        load_policy(p)


def test_load_policy_empty_precedence(tmp_path: Path):
    body = VALID_YAML.replace(
        "precedence:\n  - policy_override\n  - regulated\n  - safety\n"
        "  - financial\n  - novel_context\n  - low_confidence\n",
        "precedence: []\n",
    )
    p = tmp_path / "nopre.yaml"
    p.write_text(body, encoding="utf-8")
    with pytest.raises(PolicyLoadError, match="non-empty list"):
        load_policy(p)


# ---------------------------------------------------------------------------
# classify_escalation_class — precedence
# ---------------------------------------------------------------------------


def test_classify_no_match_returns_none(policy: HitlPolicy):
    env = {"novelty_score": 0.1, "confidence_score": 0.99}
    assert classify_escalation_class(env, policy) is None


def test_classify_policy_override_wins(policy: HitlPolicy):
    env = {
        "requires_policy_override": True,
        "is_regulated": True,
        "is_safety_impacting": True,
        "is_financial": True,
        "novelty_score": 0.99,
        "confidence_score": 0.0,
    }
    assert classify_escalation_class(env, policy) == HitlClass.POLICY_OVERRIDE


def test_classify_regulated_beats_safety(policy: HitlPolicy):
    env = {"is_regulated": True, "is_safety_impacting": True, "is_financial": True}
    assert classify_escalation_class(env, policy) == HitlClass.REGULATED


def test_classify_safety_beats_financial(policy: HitlPolicy):
    env = {"is_safety_impacting": True, "is_financial": True}
    assert classify_escalation_class(env, policy) == HitlClass.SAFETY


def test_classify_financial(policy: HitlPolicy):
    assert classify_escalation_class({"is_financial": True}, policy) == HitlClass.FINANCIAL


def test_classify_novel_context_threshold_boundary(policy: HitlPolicy):
    # At threshold (>=) → match
    assert classify_escalation_class({"novelty_score": 0.72}, policy) == HitlClass.NOVEL_CONTEXT
    # Just below → no match
    assert classify_escalation_class({"novelty_score": 0.7199}, policy) is None


def test_classify_low_confidence_threshold_boundary(policy: HitlPolicy):
    # At threshold (<=) → match
    assert classify_escalation_class({"confidence_score": 0.60}, policy) == HitlClass.LOW_CONFIDENCE
    # Just above → no match
    assert classify_escalation_class({"confidence_score": 0.6001}, policy) is None


def test_classify_novel_beats_low_confidence(policy: HitlPolicy):
    env = {"novelty_score": 0.9, "confidence_score": 0.1}
    assert classify_escalation_class(env, policy) == HitlClass.NOVEL_CONTEXT


def test_classify_non_numeric_scores_ignored(policy: HitlPolicy):
    env = {"novelty_score": "high", "confidence_score": None}
    assert classify_escalation_class(env, policy) is None


def test_classify_rejects_non_mapping(policy: HitlPolicy):
    with pytest.raises(TypeError, match="mapping"):
        classify_escalation_class(["not", "a", "mapping"], policy)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Resolvers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hc,expected_timeout",
    [
        (HitlClass.FINANCIAL, 3600),
        (HitlClass.SAFETY, 1800),
        (HitlClass.REGULATED, 7200),
        (HitlClass.NOVEL_CONTEXT, 900),
        (HitlClass.LOW_CONFIDENCE, 600),
        (HitlClass.POLICY_OVERRIDE, 86400),
    ],
)
def test_set_timeout(policy: HitlPolicy, hc: HitlClass, expected_timeout: int):
    assert set_timeout(hc, policy) == expected_timeout


def test_set_fallback_defaults_deny(policy: HitlPolicy):
    for hc in HitlClass:
        assert set_fallback(hc, policy) == "DENY"


def test_resolve_approver_pool(policy: HitlPolicy):
    assert resolve_approver_pool(HitlClass.FINANCIAL, policy) == "finance_oncall"
    assert resolve_approver_pool(HitlClass.POLICY_OVERRIDE, policy) == "policy_board"
    # tenant/time_of_day currently ignored; API-stable for future overlay
    assert (
        resolve_approver_pool(HitlClass.SAFETY, policy, tenant="acme", time_of_day="02:00") == "safety_oncall"
    )


def test_class_policy_lookup_missing_raises():
    # Construct a policy manually that lacks a class, then query it.
    bogus = HitlPolicy(
        version=1,
        novelty_min=0.7,
        confidence_max=0.6,
        classes={HitlClass.FINANCIAL: ClassPolicy(1, "DENY", "x", "")},
        precedence=(HitlClass.FINANCIAL,),
    )
    with pytest.raises(PolicyLoadError, match="not in policy"):
        set_timeout(HitlClass.SAFETY, bogus)


# ---------------------------------------------------------------------------
# Shipped SSOT sanity check
# ---------------------------------------------------------------------------


def test_shipped_policy_yaml_loads():
    """The repo-shipped policy file must load and validate cleanly."""
    shipped = DEFAULT_POLICY_PATH
    if not shipped.exists():
        pytest.skip("shipped policy not present in this checkout")
    p = load_policy(shipped, policy_snapshot="shipped")
    assert p.version == 1
    assert set(p.classes) == set(HitlClass)
