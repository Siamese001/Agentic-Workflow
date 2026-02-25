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
    """Print phase-specific DETERMINISM-DIGEST exactly once per test run.
    
    - Phase 5 tests: print only W5-DETERMINISM-DIGEST
    - Phase 6 tests: print only W6-DETERMINISM-DIGEST
    """
    try:
        from agentic_core.agents.agent_registry import AGENT_REGISTRY

        # Determine which phase is running based on collected test files
        collected_nodeids = [item.nodeid for item in session.items]
        is_phase5 = any("test_phase5_gap_closure_policy_enforcement.py" in nid for nid in collected_nodeids)
        is_phase6 = any("test_phase6_agent_fleet_conformance.py" in nid for nid in collected_nodeids)
        is_phase7 = any("test_phase7_embedding_sovereignty.py" in nid for nid in collected_nodeids)
        is_phase8 = any("test_phase8_signature_boundary.py" in nid for nid in collected_nodeids)
        is_phase9 = any("test_phase9_apps_generation_routing_sovereignty.py" in nid for nid in collected_nodeids)

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

        if is_phase5:
            # Compute W5 deterministic digest
            canonical_json = json.dumps(registry_data, separators=(",", ":"), sort_keys=True)
            w5_digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
            print(f"W5-DETERMINISM-DIGEST: {w5_digest}")
        elif is_phase6:
            # Compute W6 deterministic digest (includes gateway config)
            w6_data = {**registry_data, "gateway_config": {"timeout": 30.0, "max_retries": 3, "rate_limit": 100}}
            w6_canonical_json = json.dumps(w6_data, separators=(",", ":"), sort_keys=True)
            w6_digest = hashlib.sha256(w6_canonical_json.encode("utf-8")).hexdigest()
            print(f"W6-DETERMINISM-DIGEST: {w6_digest}")
        elif is_phase7:
            # Compute W7 embedding sovereignty digest
            try:
                from agentic_core.embeddings.embedding_factory import compute_w7_sovereignty_digest
                w7_digest = compute_w7_sovereignty_digest()
                print(f"W7-EMBEDDING-SOVEREIGNTY-DIGEST: {w7_digest}")
            except Exception as e:
                print(f"W7-EMBEDDING-SOVEREIGNTY-DIGEST: ERROR - {e}")
        elif is_phase8:
            # Compute W8 signature integrity digest
            try:
                # Compute digest over security infrastructure
                import hashlib
                import json
                import pathlib
                
                repo_root = pathlib.Path(__file__).parent.parent.parent
                
                # Hash critical security files
                security_files = {
                    "signature_verifier": repo_root / "agentic_core/security/signature_verifier.py",
                    "side_effect_guard": repo_root / "agentic_core/security/side_effect_guard.py",
                }
                
                file_hashes = {}
                for name, path in security_files.items():
                    if path.exists():
                        file_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
                    else:
                        file_hashes[name] = "MISSING"
                
                # Build canonical state
                state = {
                    "security_file_hashes": file_hashes,
                    "guarded_modules": [
                        "agentic_core.L2_execution",
                        "agentic_core.L4_state",
                        "agentic_core.L2_execution.enforcement.SovereignLLMGateway",
                        "agentic_core.embeddings.embedding_factory",
                    ],
                    "enforcement_ordering": ["verify", "guard", "execute"],
                    "phase": "8",
                }
                
                # Compute deterministic hash
                canonical_json = json.dumps(state, separators=(",", ":"), sort_keys=True)
                w8_digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
                print(f"W8-SIGNATURE-INTEGRITY-DIGEST: {w8_digest}")
            except Exception as e:
                print(f"W8-SIGNATURE-INTEGRITY-DIGEST: ERROR - {e}")
        elif is_phase9:
            # Compute W9 apps generation routing determinism digest
            try:
                import hashlib
                import json
                import pathlib
                
                repo_root = pathlib.Path(__file__).parent.parent.parent
                
                # Hash critical routing files
                routing_files = {
                    "sovereign_llm_gateway": repo_root / "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
                    "agent_registry": repo_root / "agentic_core/agents/agent_registry.py",
                }
                
                file_hashes = {}
                for name, path in routing_files.items():
                    if path.exists():
                        file_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
                    else:
                        file_hashes[name] = "MISSING"
                
                # Build canonical state for apps_* routing
                state = {
                    "routing_file_hashes": file_hashes,
                    "sanctioned_seam": "SovereignLLMGateway.route_generation",
                    "allowed_providers": ["openai", "anthropic", "google"],
                    "allowed_models": ["qwen", "gemini-2.5-pro"],
                    "routing_enforcement": [
                        "agent_id_required",
                        "temperature_enforced",
                        "model_policy_enforced",
                        "no_direct_sdk_calls",
                    ],
                    "phase": "9",
                }
                
                # Compute deterministic hash
                canonical_json = json.dumps(state, separators=(",", ":"), sort_keys=True)
                w9_digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
                print(f"W9-DETERMINISM-DIGEST: {w9_digest}")
            except Exception as e:
                print(f"W9-DETERMINISM-DIGEST: ERROR - {e}")
        else:
            # Default: print both for other governance test runs
            canonical_json = json.dumps(registry_data, separators=(",", ":"), sort_keys=True)
            w5_digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
            w6_data = {**registry_data, "gateway_config": {"timeout": 30.0, "max_retries": 3, "rate_limit": 100}}
            w6_canonical_json = json.dumps(w6_data, separators=(",", ":"), sort_keys=True)
            w6_digest = hashlib.sha256(w6_canonical_json.encode("utf-8")).hexdigest()
            print(f"W5-DETERMINISM-DIGEST: {w5_digest}")
            print(f"W6-DETERMINISM-DIGEST: {w6_digest}")

    except Exception as e:
        # Fail gracefully - if we can't compute digest, print error but don't crash
        if is_phase5:
            print(f"W5-DETERMINISM-DIGEST: ERROR - {e}")
        elif is_phase6:
            print(f"W6-DETERMINISM-DIGEST: ERROR - {e}")
        elif is_phase7:
            print(f"W7-EMBEDDING-SOVEREIGNTY-DIGEST: ERROR - {e}")
        elif is_phase8:
            print(f"W8-SIGNATURE-INTEGRITY-DIGEST: ERROR - {e}")
        elif is_phase9:
            print(f"W9-DETERMINISM-DIGEST: ERROR - {e}")
        else:
            print(f"W5-DETERMINISM-DIGEST: ERROR - {e}")
            print(f"W6-DETERMINISM-DIGEST: ERROR - {e}")
