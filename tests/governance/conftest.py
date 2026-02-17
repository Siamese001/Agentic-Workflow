"""
Governance test configuration and fixtures.

Phase 3: Network-call tripwire to ensure heal paths make no outbound calls.
"""

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
