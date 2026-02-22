"""Cross-app contract test for spine adapters."""

from unittest.mock import MagicMock, patch

import pytest

from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
from apps_rg.engines.rg_spine_adapter import RgSpineAdapter


@pytest.mark.unit_min_deps
def test_cross_app_cid_prefixes():
    """Given same semantic payload, LIC CID starts with 'lic-' and RG CID starts with 'rg-'."""
    payload = {"s0_system": "test", "i0_instructional": "instruction"}

    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_lic_orch, \
         patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_rg_orch:

        # Return fresh dicts to avoid mutation
        mock_lic_orch.return_value.execute.return_value = {"status": "ok"}
        mock_rg_orch.return_value.execute.return_value = {"status": "ok"}

        lic_adapter = LicSpineAdapter()
        rg_adapter = RgSpineAdapter()

        lic_result = lic_adapter.execute(payload)
        rg_result = rg_adapter.execute(payload)

        assert lic_result["cid"].startswith("lic-")
        assert rg_result["cid"].startswith("rg-")


@pytest.mark.unit_min_deps
def test_cross_app_cid_hash_bodies_identical():
    """Given same semantic payload, CID hash bodies (without prefix) are identical."""
    payload = {"s0_system": "test", "i0_instructional": "instruction"}

    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_lic_orch, \
         patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_rg_orch:

        # Return fresh dicts to avoid mutation
        mock_lic_orch.return_value.execute.return_value = {"status": "ok"}
        mock_rg_orch.return_value.execute.return_value = {"status": "ok"}

        lic_adapter = LicSpineAdapter()
        rg_adapter = RgSpineAdapter()

        lic_result = lic_adapter.execute(payload)
        rg_result = rg_adapter.execute(payload)

        # Extract hash bodies (remove prefixes)
        lic_hash_body = lic_result["cid"][4:]  # Remove "lic-"
        rg_hash_body = rg_result["cid"][3:]    # Remove "rg-"

        assert lic_hash_body == rg_hash_body


@pytest.mark.unit_min_deps
def test_cross_app_cid_determinism():
    """Running twice with identical canonicalized payload yields identical CID each time."""
    payload = {"s0_system": "test", "i0_instructional": "instruction"}

    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_lic_orch, \
         patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_rg_orch:

        # Return fresh dicts to avoid mutation
        mock_lic_orch.return_value.execute.return_value = {"status": "ok"}
        mock_rg_orch.return_value.execute.return_value = {"status": "ok"}

        lic_adapter = LicSpineAdapter()
        rg_adapter = RgSpineAdapter()

        # Run twice
        lic_result1 = lic_adapter.execute(payload)
        lic_result2 = lic_adapter.execute(payload)
        rg_result1 = rg_adapter.execute(payload)
        rg_result2 = rg_adapter.execute(payload)

        # Check determinism
        assert lic_result1["cid"] == lic_result2["cid"]
        assert rg_result1["cid"] == rg_result2["cid"]


@pytest.mark.unit_min_deps
def test_cross_app_cid_difference():
    """Minimally different semantic payload yields different hash body."""
    payload1 = {"s0_system": "test", "i0_instructional": "instruction"}
    payload2 = {"s0_system": "test", "i0_instructional": "different"}

    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_lic_orch, \
         patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_rg_orch:

        # Return fresh dicts to avoid mutation
        mock_lic_orch.return_value.execute.return_value = {"status": "ok"}
        mock_rg_orch.return_value.execute.return_value = {"status": "ok"}

        lic_adapter = LicSpineAdapter()
        rg_adapter = RgSpineAdapter()

        lic_result1 = lic_adapter.execute(payload1)
        lic_result2 = lic_adapter.execute(payload2)
        rg_result1 = rg_adapter.execute(payload1)
        rg_result2 = rg_adapter.execute(payload2)

        # Extract hash bodies
        lic_hash_body1 = lic_result1["cid"][4:]
        lic_hash_body2 = lic_result2["cid"][4:]
        rg_hash_body1 = rg_result1["cid"][3:]
        rg_hash_body2 = rg_result2["cid"][3:]

        # Check that different payloads produce different hash bodies
        assert lic_hash_body1 != lic_hash_body2
        assert rg_hash_body1 != rg_hash_body2

        # But same payload across apps should produce same hash body
        assert lic_hash_body1 == rg_hash_body1
        assert lic_hash_body2 == rg_hash_body2


@pytest.mark.unit_min_deps
def test_cross_app_call_order_invariant():
    """new_cycle called before orchestrator.execute for both apps."""
    payload = {"s0_system": "test", "i0_instructional": "instruction"}

    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_lic_orch, \
         patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_rg_orch, \
         patch("apps_lic.engines.lic_spine_adapter.CIDRegistry") as mock_lic_registry, \
         patch("apps_rg.engines.rg_spine_adapter.CIDRegistry") as mock_rg_registry:

        # Setup mocks
        mock_cycle = MagicMock()
        mock_cycle.attempt = 1
        mock_lic_registry.return_value.new_cycle.return_value = mock_cycle
        mock_rg_registry.return_value.new_cycle.return_value = mock_cycle

        mock_lic_orch.return_value.execute.return_value = {"status": "ok"}
        mock_rg_orch.return_value.execute.return_value = {"status": "ok"}

        lic_adapter = LicSpineAdapter()
        rg_adapter = RgSpineAdapter()

        # Execute adapters
        lic_adapter.execute(payload)
        rg_adapter.execute(payload)

        # Verify call order: new_cycle called before execute
        assert mock_lic_registry.return_value.new_cycle.called
        assert mock_rg_registry.return_value.new_cycle.called
        assert mock_lic_orch.return_value.execute.called
        assert mock_rg_orch.return_value.execute.called

        # Check that new_cycle was called exactly once for each adapter
        assert mock_lic_registry.return_value.new_cycle.call_count == 1
        assert mock_rg_registry.return_value.new_cycle.call_count == 1
