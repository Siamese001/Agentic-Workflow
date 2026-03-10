"""Unit tests for RLHF Optimizer - deterministic DPO-driven threshold adjustments."""

import json

import pytest

from system_learning.engines.change_package_impl import ChangePackage
from system_learning.engines.rlhf_optimizer import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    DefaultDeterministicRLHFOptimizer,
)

pytestmark = pytest.mark.unit_min_deps


class TestRLHFOptimizer:
    """Test suite for RLHF Optimizer deterministic behavior."""

    def test_approve_relaxes_within_bounds(self):
        """APPROVE decisions should relax thresholds within bounds."""
        optimizer = DefaultDeterministicRLHFOptimizer(
            min_threshold=THRESHOLD,
            max_threshold=THRESHOLD,
            approve_relax_delta=0.1,
            reject_tighten_delta=-0.1,
        )

        # Create DPO batch with APPROVE decisions
        dpo_batch = {
            "pairs": [
                {
                    "example_id": {
                        "control_hash": "control1_hash",
                        "candidate_hash": "candidate1_hash",
                    },
                    "control_output_hash": "control1_hash",
                    "candidate_output_hash": "candidate1_hash",
                    "human_decision": "APPROVE",
                    "reasons": ["good_quality"],
                },
                {
                    "example_id": {
                        "control_hash": "control2_hash",
                        "candidate_hash": "candidate2_hash",
                    },
                    "control_output_hash": "control2_hash",
                    "candidate_output_hash": "candidate2_hash",
                    "human_decision": "APPROVE",
                    "reasons": ["meets_requirements"],
                },
            ]
        }

        current_config = {
            "threshold_a": 0.5,
            "threshold_b": 1.0,
        }

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        # Should be a valid proposal
        assert isinstance(proposal, ChangePackage)
        assert proposal.source == "rlhf_optimizer"
        assert proposal.target == "threshold_config"

        # Should have relaxed thresholds
        final_config = json.loads(proposal.changes.decode("utf-8"))
        assert final_config["threshold_a"] > current_config["threshold_a"]
        assert final_config["threshold_b"] > current_config["threshold_b"]

        # Should be within bounds
        assert 0.2 <= final_config["threshold_a"] <= 1.8
        assert 0.2 <= final_config["threshold_b"] <= 1.8

        # Should have appropriate confidence
        assert proposal.confidence > 0.0
        assert "approve_relax_0.100000" in proposal.reason

    def test_reject_tightens_within_bounds(self):
        """REJECT decisions should tighten thresholds within bounds."""
        optimizer = DefaultDeterministicRLHFOptimizer(
            min_threshold=THRESHOLD,
            max_threshold=THRESHOLD,
            approve_relax_delta=0.15,
            reject_tighten_delta=-0.05,  # Smaller delta to avoid clamping
        )

        # Create DPO batch with REJECT decisions
        dpo_batch = {
            "pairs": [
                {
                    "example_id": {
                        "control_hash": "control1_hash",
                        "candidate_hash": "candidate1_hash",
                    },
                    "control_output_hash": "control1_hash",
                    "candidate_output_hash": "candidate1_hash",
                    "human_decision": "REJECT",
                    "reasons": ["poor_quality"],
                },
            ]
        }

        current_config = {
            "threshold_x": 1.2,
            "threshold_y": 0.8,
        }

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        # Should have tightened thresholds (negative delta applied)
        final_config = json.loads(proposal.changes.decode("utf-8"))
        # REJECT adds negative delta, so values should be lower than original
        assert final_config["threshold_x"] < current_config["threshold_x"]
        assert final_config["threshold_y"] < current_config["threshold_y"]

        # Should be within bounds
        assert 0.3 <= final_config["threshold_x"] <= 1.7
        assert 0.3 <= final_config["threshold_y"] <= 1.7

        # Should have reject reasons
        assert "reject_tighten_-0.050000" in proposal.reason

    def test_multiple_pairs_deterministic_application_order(self):
        """Multiple pairs should be applied in deterministic order."""
        optimizer = DefaultDeterministicRLHFOptimizer()

        # Create DPO batch with mixed decisions
        dpo_batch = {
            "pairs": [
                {
                    "example_id": {
                        "control_hash": "z_control",  # Will be sorted last
                        "candidate_hash": "z_candidate",
                    },
                    "control_output_hash": "z_control",
                    "candidate_output_hash": "z_candidate",
                    "human_decision": "APPROVE",
                    "reasons": ["z_reason"],
                },
                {
                    "example_id": {
                        "control_hash": "a_control",  # Will be sorted first
                        "candidate_hash": "a_candidate",
                    },
                    "control_output_hash": "a_control",
                    "candidate_output_hash": "a_candidate",
                    "human_decision": "REJECT",
                    "reasons": ["a_reason"],
                },
                {
                    "example_id": {
                        "control_hash": "m_control",  # Will be sorted middle
                        "candidate_hash": "m_candidate",
                    },
                    "control_output_hash": "m_control",
                    "candidate_output_hash": "m_candidate",
                    "human_decision": "APPROVE",
                    "reasons": ["m_reason"],
                },
            ]
        }

        current_config = {"threshold": 1.0}

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        # Should apply in sorted order: a_control (REJECT), m_control (APPROVE), z_control (APPROVE)
        # Net effect: 1.0 - 0.1 + 0.1 + 0.1 = 1.1
        final_config = json.loads(proposal.changes.decode("utf-8"))
        assert final_config["threshold"] == 1.1

        # Should have all reasons in order
        assert "reject_tighten_-0.100000" in proposal.reason
        assert "approve_relax_0.100000" in proposal.reason

    def test_bounds_clamping(self):
        """Thresholds should be clamped to min/max bounds."""
        optimizer = DefaultDeterministicRLHFOptimizer(
            min_threshold=THRESHOLD,
            max_threshold=THRESHOLD,
            approve_relax_delta=1.0,  # Large delta that would exceed bounds
            reject_tighten_delta=-1.0,  # Large delta that would exceed bounds
        )

        # Test APPROVE with clamping
        approve_dpo = {
            "pairs": [
                {
                    "example_id": {"control_hash": "c", "candidate_hash": "x"},
                    "control_output_hash": "c",
                    "candidate_output_hash": "x",
                    "human_decision": "APPROVE",
                    "reasons": ["test"],
                },
            ]
        }

        current_config = {"threshold": 1.4}  # Close to upper bound

        dpo_bytes = json.dumps(approve_dpo, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        final_config = json.loads(proposal.changes.decode("utf-8"))
        assert final_config["threshold"] <= 1.5  # Clamped to max

        # Test REJECT with clamping
        reject_dpo = {
            "pairs": [
                {
                    "example_id": {"control_hash": "c", "candidate_hash": "x"},
                    "control_output_hash": "c",
                    "candidate_output_hash": "x",
                    "human_decision": "REJECT",
                    "reasons": ["test"],
                },
            ]
        }

        current_config = {"threshold": 0.6}  # Close to lower bound

        dpo_bytes = json.dumps(reject_dpo, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        final_config = json.loads(proposal.changes.decode("utf-8"))
        assert final_config["threshold"] >= 0.5  # Clamped to min

    def test_malformed_dpo_batch_handled_gracefully(self):
        """Malformed DPO batch should be handled gracefully."""
        optimizer = DefaultDeterministicRLHFOptimizer()

        current_config = {"threshold": 1.0}
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        # Test invalid JSON
        malformed_bytes = b"invalid json"

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=malformed_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        # Should return empty proposal
        assert proposal.confidence == 0.0
        assert "malformed_dpo_batch" in proposal.reason
        assert proposal.changes == b"{}"

    def test_malformed_config_handled_gracefully(self):
        """Malformed threshold config should be handled gracefully."""
        optimizer = DefaultDeterministicRLHFOptimizer()

        dpo_batch = {"pairs": []}
        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")

        # Test invalid config
        malformed_config = b"invalid config"

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=malformed_config,
        )

        # Should return empty proposal
        assert proposal.confidence == 0.0
        assert "malformed_threshold_config" in proposal.reason
        assert proposal.changes == b"{}"

    def test_empty_dpo_batch_no_adjustments(self):
        """Empty DPO batch should result in no adjustments."""
        optimizer = DefaultDeterministicRLHFOptimizer()

        dpo_batch = {"pairs": []}
        current_config = {"threshold": 1.0}

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        # Should have no adjustments but still be a valid proposal
        assert proposal.confidence == 0.0  # No pairs processed
        assert "no_adjustments" in proposal.reason

        # Config should remain unchanged
        final_config = json.loads(proposal.changes.decode("utf-8"))
        assert final_config == current_config

    def test_deterministic_rounding(self):
        """Floating point values should be deterministically rounded to 6 decimals."""
        optimizer = DefaultDeterministicRLHFOptimizer(approve_relax_delta=0.123456789)

        dpo_batch = {
            "pairs": [
                {
                    "example_id": {"control_hash": "c", "candidate_hash": "x"},
                    "control_output_hash": "c",
                    "candidate_output_hash": "x",
                    "human_decision": "APPROVE",
                    "reasons": ["test"],
                },
            ]
        }

        current_config = {"threshold": 1.0}

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        final_config = json.loads(proposal.changes.decode("utf-8"))

        # Should be rounded to 6 decimal places
        assert final_config["threshold"] == 1.123457  # 1.0 + 0.123456789 rounded to 6 decimals
