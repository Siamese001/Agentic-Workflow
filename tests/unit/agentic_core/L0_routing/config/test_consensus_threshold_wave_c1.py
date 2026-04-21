"""Wave C1 tests — consensus_majority_threshold SSOT helper.

Plan: `.windsurf/plans/consensus-validator-unification-5e9f3a.md` Wave C1.

Covers:
  - 3-juror formula matches legacy MAJORITY_THRESHOLD=0.66 within epsilon
  - 4/5/7-juror counts produce mathematically correct strict-majority cuts
  - juror_count < 1 raises ValueError
  - ConsensusEngine.__init__ wires threshold from helper for default + custom
    juror lists
"""

from __future__ import annotations

import math
import warnings

import pytest

from agentic_core.L0_routing.config.path_constants import (
    consensus_majority_threshold,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Helper math
# ---------------------------------------------------------------------------


def test_three_juror_matches_legacy_066():
    assert math.isclose(consensus_majority_threshold(3), 2 / 3, rel_tol=1e-9)


def test_four_juror_is_075():
    assert consensus_majority_threshold(4) == 0.75


def test_five_juror_is_06():
    assert consensus_majority_threshold(5) == 0.6


def test_seven_juror_is_four_sevenths():
    assert math.isclose(consensus_majority_threshold(7), 4 / 7, rel_tol=1e-9)


def test_single_juror_is_one():
    assert consensus_majority_threshold(1) == 1.0


def test_zero_juror_raises():
    with pytest.raises(ValueError, match="juror_count must be >= 1"):
        consensus_majority_threshold(0)


def test_negative_juror_raises():
    with pytest.raises(ValueError, match="juror_count must be >= 1"):
        consensus_majority_threshold(-3)


# ---------------------------------------------------------------------------
# ConsensusEngine wiring
# ---------------------------------------------------------------------------


def test_consensus_engine_default_threshold_from_helper():
    # Suppress any deprecation warnings from L2 heal_classifier import chain.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from agentic_core.L1_cognition.enforcement.consensus_validator import (  # noqa: PLC0415
            ConsensusEngine,
        )

    engine = ConsensusEngine()
    # Default juror set is 3 models; threshold must equal helper(3).
    assert math.isclose(engine.threshold, consensus_majority_threshold(3), rel_tol=1e-9)
    assert engine.threshold == consensus_majority_threshold(len(engine.providers))


def test_consensus_engine_five_juror_threshold_auto_adjusts():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from agentic_core.L1_cognition.enforcement.consensus_validator import (  # noqa: PLC0415
            ConsensusEngine,
        )

    jurors = ["openai/o3", "anthropic/claude-opus", "google/gemini-pro", "j4", "j5"]
    engine = ConsensusEngine(providers=jurors)
    assert engine.threshold == 0.6
    assert engine.threshold != ConsensusEngine.MAJORITY_THRESHOLD  # legacy 0.66 mismatches


def test_majority_threshold_class_constant_preserved_as_back_compat():
    """Back-compat sentinel: old consumers reading the class attribute still
    see a 3-juror strict majority. Must be 2/3 exactly (not legacy 0.66 float)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from agentic_core.L1_cognition.enforcement.consensus_validator import (  # noqa: PLC0415
            ConsensusEngine,
        )

    assert math.isclose(ConsensusEngine.MAJORITY_THRESHOLD, 2 / 3, rel_tol=1e-9)
