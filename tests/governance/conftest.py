"""
Governance test configuration and fixtures.

Phase 3: Network-call tripwire to ensure heal paths make no outbound calls.
Phase 5-H: Single W5-DETERMINISM-DIGEST print per run.
"""

import hashlib
import json
from unittest import mock

import pytest


class NetworkTripwireError(Exception):
    """Raised when heal tests attempt unauthorized network calls."""

    pass


@pytest.fixture(autouse=True)
def block_network_in_governance_tests(request):
    """Block all network calls in governance tests.

    This fixture ensures heal paths never make outbound network calls
    unless explicitly marked with @pytest.mark.allow_network.
    """
    # Skip if test is marked to allow network
    if request.node.get_closest_marker("allow_network"):
        yield
        return

    def blocked_socket(*args, **kwargs):
        raise NetworkTripwireError(
            "Network call attempted in governance test! "
            "Heal paths must not make outbound calls. "
            "Use @pytest.mark.allow_network to exempt integration tests."
        )

    with mock.patch("socket.socket", blocked_socket):
        yield


@pytest.fixture
def mock_requests_block(monkeypatch):
    """Block requests library calls."""

    def blocked_request(*args, **kwargs):
        raise NetworkTripwireError("requests library call blocked in governance test!")

    try:
        import requests

        monkeypatch.setattr(requests, "request", blocked_request)
        monkeypatch.setattr(requests, "get", blocked_request)
        monkeypatch.setattr(requests, "post", blocked_request)
    except ImportError:
        pass  # requests not installed


@pytest.fixture
def mock_httpx_block(monkeypatch):
    """Block httpx library calls."""

    def blocked_request(*args, **kwargs):
        raise NetworkTripwireError("httpx library call blocked in governance test!")

    try:
        import httpx

        monkeypatch.setattr(httpx, "request", blocked_request)
        monkeypatch.setattr(httpx, "get", blocked_request)
        monkeypatch.setattr(httpx, "post", blocked_request)
    except ImportError:
        pass  # httpx not installed


def pytest_sessionfinish(session, exitstatus):
    """Print W5 and W6 DETERMINISM-DIGEST exactly once per test run."""
    try:
        from agentic_core.agents.agent_registry import AGENT_REGISTRY

        # Create canonical JSON of registry + policy thresholds
        registry_data = {
            "registry": sorted(
                [
                    {
                        "agent_id": agent_id,
                        "execution_mode": profile.execution_mode.value,
                        "reasoning_intensity": profile.reasoning_intensity.value,
                        "allowed_models": sorted(profile.allowed_models),
                    }
                    for agent_id, profile in AGENT_REGISTRY.items()
                ],
                key=lambda x: x["agent_id"],
            ),
            "policy_thresholds": {
                "heal_confidence_x": 0.80,
                "heal_confidence_y": 0.60,
                "max_heal_retries": 3,
            },
        }

        # Compute W5 deterministic digest
        canonical_json = json.dumps(registry_data, separators=(",", ":"), sort_keys=True)
        w5_digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

        # Compute W6 deterministic digest (includes gateway config)
        w6_data = {**registry_data, "gateway_config": {"timeout": 30.0, "max_retries": 3, "rate_limit": 100}}
        w6_canonical_json = json.dumps(w6_data, separators=(",", ":"), sort_keys=True)
        w6_digest = hashlib.sha256(w6_canonical_json.encode("utf-8")).hexdigest()

        print(f"W5-DETERMINISM-DIGEST: {w5_digest}")
        print(f"W6-DETERMINISM-DIGEST: {w6_digest}")

    except Exception as e:
        # Fail gracefully - if we can't compute digest, print error but don't crash
        print(f"W5-DETERMINISM-DIGEST: ERROR - {e}")
        print(f"W6-DETERMINISM-DIGEST: ERROR - {e}")
