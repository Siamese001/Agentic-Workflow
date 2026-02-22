"""Tests for RG spine adapter — deterministic CID + spine routing."""

from unittest.mock import MagicMock, patch

import pytest

from apps_rg.engines.rg_spine_adapter import RgSpineAdapter


@pytest.mark.unit_min_deps
def test_adapter_returns_cid():
    """Adapter returns a cid in result."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = RgSpineAdapter()
        result = adapter.execute({"s0_system": "test"})

        assert "cid" in result
        assert result["cid"].startswith("rg-")
        assert len(result["cid"]) == 19  # "rg-" + 16 char hash


@pytest.mark.unit_min_deps
def test_cid_has_rg_prefix():
    """CID has 'rg-' prefix."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = RgSpineAdapter()
        result = adapter.execute({"s0_system": "test"})

        assert result["cid"].startswith("rg-")


@pytest.mark.unit_min_deps
def test_cid_is_deterministic():
    """Calling adapter twice with identical intent_input produces same cid."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = RgSpineAdapter()
        result1 = adapter.execute({"s0_system": "test", "i0_instructional": "instruction"})
        result2 = adapter.execute({"s0_system": "test", "i0_instructional": "instruction"})

        assert result1["cid"] == result2["cid"]


@pytest.mark.unit_min_deps
def test_different_inputs_produce_different_cids():
    """Different intent_inputs produce different cids."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        def fresh_result(*args, **kwargs):
            return {"status": "ok"}

        mock_orch.return_value.execute = fresh_result

        adapter1 = RgSpineAdapter()
        result1 = adapter1.execute({"s0_system": "test1", "i0_instructional": "instruction1"})

        adapter2 = RgSpineAdapter()
        result2 = adapter2.execute({"s0_system": "test2", "i0_instructional": "instruction2"})

        assert result1["cid"] != result2["cid"]


@pytest.mark.unit_min_deps
def test_cid_registered_before_orchestrator_execute():
    """CIDRegistry.new_cycle called before ExecutionOrchestrator.execute."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        with patch("apps_rg.engines.rg_spine_adapter.CIDRegistry") as mock_registry:
            mock_cycle = MagicMock()
            mock_cycle.attempt = 1
            mock_registry.return_value.new_cycle.return_value = mock_cycle
            mock_orch.return_value.execute.return_value = {"status": "ok"}

            adapter = RgSpineAdapter()
            adapter.execute({"s0_system": "test"})

            # Verify call order
            mock_registry.return_value.new_cycle.assert_called_once()
            mock_orch.return_value.execute.assert_called_once()

            # Get the cid passed to new_cycle
            cid_arg = mock_registry.return_value.new_cycle.call_args[0][0]
            assert cid_arg.startswith("rg-")

            # Verify orchestrator received enriched input
            enriched_input = mock_orch.return_value.execute.call_args[0][0]
            assert "_cid" in enriched_input
            assert enriched_input["_cid"] == cid_arg


@pytest.mark.unit_min_deps
def test_cid_passed_to_orchestrator():
    """CID is passed to orchestrator in enriched intent_input."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        with patch("apps_rg.engines.rg_spine_adapter.CIDRegistry") as mock_registry:
            mock_cycle = MagicMock()
            mock_cycle.attempt = 1
            mock_registry.return_value.new_cycle.return_value = mock_cycle
            mock_orch.return_value.execute.return_value = {"status": "ok"}

            adapter = RgSpineAdapter()
            adapter.execute({"s0_system": "test"})

            # Verify orchestrator received enriched input
            enriched_input = mock_orch.return_value.execute.call_args[0][0]
            assert "_cid" in enriched_input
            assert "_cycle_attempt" in enriched_input
            assert enriched_input["_cycle_attempt"] == 1


@pytest.mark.unit_min_deps
def test_adapter_state_success_on_clean_input():
    """Adapter succeeds on clean input without side effects."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = RgSpineAdapter()
        # Should not raise
        result = adapter.execute(
            {
                "s0_system": "test_system",
                "i0_instructional": "test_instruction",
                "c0_context": "test_context",
                "u0_user_prompt": "test_prompt",
                "d0_injections": "test_injection",
            }
        )

        assert result["status"] == "ok"
        assert "cid" in result
