"""Wave 3 regression tests for the deprecated _ssot_routing shim.

Validates:
  - Module emits DeprecationWarning on import (P3.3)
  - `compute_routing_decision` is now the SSOT for tier + model (P3.1)
  - Broken lazy seams raise or return safe defaults instead of silent magic (P3.2)
  - `ConfidenceScore.is_{high,medium,low}_confidence` properties work
    (previously ImportError'd due to missing healing_tier_config module)
"""

from __future__ import annotations

import importlib
import sys
import warnings

import pytest

pytestmark = pytest.mark.unit


# ==========================================================================
# P3.3 — DeprecationWarning on import
# ==========================================================================


def test_module_emits_deprecation_warning_on_import():
    """Force reimport and assert DeprecationWarning is raised."""
    module_name = "ops_scripts.dev_tools.L0_routing_scripts._ssot_routing"
    sys.modules.pop(module_name, None)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.import_module(module_name)
    deprecation_msgs = [str(w.message) for w in caught if issubclass(w.category, DeprecationWarning)]
    assert any("_ssot_routing is deprecated" in msg for msg in deprecation_msgs), (
        f"Expected deprecation warning, got: {deprecation_msgs}"
    )


# ==========================================================================
# P3.1 — SovereignDecisionEngine trusts compute_routing_decision
# ==========================================================================


def test_duplicate_tier_override_block_removed():
    """The duplicate block at lines 666-677 that silently re-bucketed tier
    based on raw confidence.value should be gone. Verify by asserting the
    comment marker is present.
    """
    from pathlib import Path  # noqa: PLC0415

    src = Path("ops_scripts/dev_tools/L0_routing_scripts/_ssot_routing.py").read_text(encoding="utf-8")
    assert "Wave 3 P3.1" in src
    assert "removed duplicate tier-override block" in src
    # Verify the hardcoded gemini-2.5-pro assignment is gone from the override path
    assert '_GEMINI_MODEL_ID = "gemini-2.5-pro"' not in src


# ==========================================================================
# P3.2 — Broken lazy seams fixed
# ==========================================================================


def test_bmg_cosine_similarity_raises_import_error_explicitly():
    """Was: silently ImportError from missing module → hidden Jaccard fallback.
    Now: raises ImportError with explicit message so callers can handle.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from ops_scripts.dev_tools.L0_routing_scripts._ssot_routing import (  # noqa: PLC0415
            SovereignDecisionEngine,
        )

    with pytest.raises(ImportError, match="bmg_embedding_similarity is not implemented"):
        SovereignDecisionEngine._get_bmg_cosine_similarity()


def test_bmg_embedding_agent_keys_returns_empty_frozenset():
    """Was: ImportError. Now: returns empty frozenset (safe default)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from ops_scripts.dev_tools.L0_routing_scripts._ssot_routing import (  # noqa: PLC0415
            SovereignDecisionEngine,
        )

    result = SovereignDecisionEngine._get_bmg_embedding_agent_keys()
    assert isinstance(result, frozenset)
    assert len(result) == 0


def test_qwen_14b_routing_config_uses_model_registry():
    """Was: ImportError. Now: (empty frozenset, model_registry.QWEN_LOCAL_MODEL_ID)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from ops_scripts.dev_tools.L0_routing_scripts._ssot_routing import (  # noqa: PLC0415
            SovereignDecisionEngine,
        )
    from agentic_core.L0_routing.config.model_registry import (  # noqa: PLC0415
        QWEN_LOCAL_MODEL_ID,
    )

    agent_keys, model_id = SovereignDecisionEngine._get_qwen_14b_routing_config()
    assert agent_keys == frozenset()
    assert model_id == QWEN_LOCAL_MODEL_ID


# ==========================================================================
# P3.2 — ConfidenceScore confidence-band properties work again
# ==========================================================================


def test_confidence_score_is_high_confidence_works():
    """Previously raised ImportError on access (missing healing_tier_config)."""
    from ops_scripts.dev_tools.L0_routing_scripts._ssot_types import (  # noqa: PLC0415
        ConfidenceScore,
    )

    high = ConfidenceScore(value=0.90, reasoning="t")
    assert high.is_high_confidence is True
    assert high.is_medium_confidence is False
    assert high.is_low_confidence is False


def test_confidence_score_is_medium_confidence_works():
    from ops_scripts.dev_tools.L0_routing_scripts._ssot_types import (  # noqa: PLC0415
        ConfidenceScore,
    )

    med = ConfidenceScore(value=0.65, reasoning="t")
    assert med.is_high_confidence is False
    assert med.is_medium_confidence is True
    assert med.is_low_confidence is False


def test_confidence_score_is_low_confidence_works():
    from ops_scripts.dev_tools.L0_routing_scripts._ssot_types import (  # noqa: PLC0415
        ConfidenceScore,
    )

    low = ConfidenceScore(value=0.20, reasoning="t")
    assert low.is_high_confidence is False
    assert low.is_medium_confidence is False
    assert low.is_low_confidence is True


# ==========================================================================
# Smoke: compute_routing_decision still functional (backward-compat shim)
# ==========================================================================


def test_compute_routing_decision_still_produces_decisions():
    """The shim must remain functional for _ssot_phases.py callers until
    that file is migrated in a future wave.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from ops_scripts.dev_tools.L0_routing_scripts._ssot_routing import (  # noqa: PLC0415
            compute_routing_decision,
        )
    from ops_scripts.dev_tools.L0_routing_scripts._ssot_types import (  # noqa: PLC0415
        FailureType,
        RoutingInputs,
        RoutingTier,
    )

    inputs = RoutingInputs(failure_type=FailureType.UNKNOWN, C=0, B=1, A=0, N=0, F=0)
    decision = compute_routing_decision(inputs)
    assert decision.tier in {
        RoutingTier.DETERMINISTIC,
        RoutingTier.QWEN,
        RoutingTier.GEMINI,
        RoutingTier.FAIL_CLOSED,
    }
    assert decision.model_id  # non-empty
    assert decision.determinism_digest  # non-empty
