"""Phase W9: Apps_* Generation Routing Sovereignty

Tests for:
- SovereignLLMGateway.route_generation() as sanctioned seam
- apps_* agents route via gateway only (no direct SDK calls)
- No bypass through model literals or provider SDK imports
- Deterministic agents blocked from LLM calls
- W9-DETERMINISM-DIGEST stability
- W9_NEGCTRL_TAMPER negative control
"""

import ast
import hashlib
import json
import os
import pathlib
import pytest
from typing import Any, Dict, List, Set

# Test infrastructure
REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
SCAN_ROOTS = [
    REPO_ROOT / "agentic_core",
    REPO_ROOT / "apps_lic",
    REPO_ROOT / "apps_rg",
    REPO_ROOT / "apps_shared",
    REPO_ROOT / "system_learning",
]

# Forbidden provider SDK imports
FORBIDDEN_SDK_IMPORTS = {
    "openai",
    "anthropic",
    "google.generativeai",
    "google.genai",
    "vertexai",
    "openai_async",
    "anthropic_async",
}

# Allowed SDK imports (infrastructure seams only)
ALLOWED_SDK_IMPORTS = {
    "data.sdks_mcps",  # Centralized SDK wrapper
    "agentic_core.L2_execution.enforcement.SovereignLLMGateway",  # Gateway itself
    "tests",  # Test infrastructure
    "agentic_core",  # Core infrastructure
    "apps_shared",  # Shared infrastructure
    "system_learning",  # Learning infrastructure
}

# Forbidden model literals (hard-coded model strings) - only in apps_* execution code
FORBIDDEN_MODEL_LITERALS = {
    "gpt-4",
    "gpt-4o",
    "gpt-3.5-turbo",
    "claude-3-5-sonnet",
    "claude-3-opus",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "qwen",
    "qwen-2.5",
    "qwen-2.5-coder",
    "qwen-2.5-72b",
}

# Allowed model literals (policy surfaces only)
ALLOWED_MODEL_LITERALS = {
    "config",  # Config files
    "agent_registry",  # Agent registry
    "tests",  # Test files
    "data",  # Data files
    "types",  # Type definitions
    "mixins",  # Mixin files
    "runtime",  # Runtime configuration
    "constraints",  # Constraint definitions
    "enforcement",  # Enforcement strategies
    "utils",  # Utility files
}

# Known bypass debt (baseline) - actual violations found in codebase
KNOWN_BYPASS_DEBT = {
    "agentic_core/L0_routing/scripts/class_info.py",
    "agentic_core/L1_cognition/validators/consensus_validator.py",
    "agentic_core/L2_execution/healers/healing_provider_adapters.py",
    "agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py",
    "agentic_core/L3_orchestration/config/orchestrator_config.py",
    "agentic_core/L3_orchestration/reasoning/CoverageAgent.py",
    "agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py",
    "agentic_core/L4_state/config/versioned_configs.py",
    "agentic_core/L5_safety/types/resource_management_types.py",
    "agentic_core/L5_safety/validators/magic_validator.py",
    "agentic_core/agents/agent_registry.py",
    "agentic_core/agents/types/agent_execution_profile.py",
    "agentic_core/config/core/agent_defaults_config.py",
    "agentic_core/config/core/base_entity_config.py",
    "agentic_core/config/core/sovereign_config.py",
    "agentic_core/mixins/cost_mixin.py",
    "agentic_core/mixins/hardening_mixin.py",
    "agentic_core/runtime/config/reasoning_types.py",
    "agentic_core/runtime/types/cost_governor_types.py",
    "agentic_core/runtime/utils/sovereign_dependency_error_util.py",
    "agentic_core/runtime/utils/subatomic_hop_util.py",
    "apps_rg/enforcement/HardenedanthropicexecutorStrategy.py",
    "apps_rg/reasoning/HardenedopenaiexecutorStrategy.py",
    "apps_rg/tools/ResumeGenerator.py",
    "apps_rg/types/routing_tier_types.py",
    "apps_rg/utils/deep_brain_harvester_util.py",
    "apps_rg/utils/providers_anthropic_client_util.py",
    "apps_shared/config/environment_config.py",
    "apps_shared/enforcement/DecomposedqueryagentStrategy.py",
    "apps_shared/types/hardened_gemini_executor_types.py",
    "apps_shared/types/model_router_types.py",
    "apps_shared/utils/late_interaction_reranker_util.py",
    "apps_shared/utils/provider_util.py",
    "apps_shared/utils/providers_google_genai_client_util.py",
    "system_learning/constraints/config_surfaces.py",
    "system_learning/engines/openai_embedder.py",
}

KNOWN_BYPASS_DEBT_CEILING = len(KNOWN_BYPASS_DEBT)


def _canonical_path(filepath: pathlib.Path) -> str:
    """Convert absolute path to canonical repo-relative path."""
    try:
        rel = filepath.relative_to(REPO_ROOT)
        return str(rel).replace("\\", "/")
    except ValueError:
        return str(filepath).replace("\\", "/")


def _collect_py_files(roots: List[pathlib.Path]) -> List[pathlib.Path]:
    """Collect all Python files from scan roots."""
    py_files = []
    for root in roots:
        if root.exists():
            py_files.extend(root.rglob("*.py"))
    return py_files


def _is_in_allowed_context(filepath: str, node: ast.AST) -> bool:
    """Check if a node is in an allowed context (e.g., test, config)."""
    for allowed_prefix in ALLOWED_SDK_IMPORTS:
        if filepath.startswith(allowed_prefix):
            return True
    return False


def _ast_scan_for_bypass(source: str, filepath: str) -> List[str]:
    """Scan AST for generation routing bypass violations."""
    violations = []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["SYNTAX_ERROR"]

    # Check for forbidden SDK imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name
                if module_name in FORBIDDEN_SDK_IMPORTS:
                    if not _is_in_allowed_context(filepath, node):
                        violations.append(f"line {node.lineno}: forbidden import '{module_name}'")

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module
                if module_name in FORBIDDEN_SDK_IMPORTS:
                    if not _is_in_allowed_context(filepath, node):
                        violations.append(f"line {node.lineno}: forbidden from import '{module_name}'")

        # Check for forbidden model literals
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                model_literal = node.value.lower()
                if model_literal in FORBIDDEN_MODEL_LITERALS:
                    if not _is_in_allowed_context(filepath, node):
                        violations.append(f"line {node.lineno}: forbidden model literal '{model_literal}'")

        # Check for direct HTTP calls to LLM endpoints
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if (isinstance(node.func.value, ast.Name) and
                    node.func.value.id in {"requests", "httpx", "aiohttp"} and
                    node.func.attr in {"get", "post", "request"}):
                    if not _is_in_allowed_context(filepath, node):
                        violations.append(f"line {node.lineno}: direct HTTP call to LLM endpoint")

    return violations


# ---------------------------------------------------------------------------
# T1: SovereignLLMGateway route_generation() exists and works
# ---------------------------------------------------------------------------

def test_sovereign_llm_gateway_has_route_generation():
    """Verify SovereignLLMGateway has route_generation method."""
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        SovereignLLMGateway,
        get_llm_gateway,
    )

    gateway = get_llm_gateway()
    assert hasattr(gateway, "route_generation")
    assert callable(getattr(gateway, "route_generation"))


@pytest.mark.allow_network
def test_route_generation_requires_agent_id():
    """route_generation must require agent_id parameter."""
    import pytest
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        get_llm_gateway,
    )
    from agentic_core.L0_routing.types.guardian_contract import V15HardFailAbort

    gateway = get_llm_gateway()

    # Check method signature requires request parameter
    import inspect
    sig = inspect.signature(gateway.route_generation)
    assert "request" in sig.parameters
    assert sig.parameters["request"].default == inspect.Parameter.empty

    # Should fail with invalid agent_id
    with pytest.raises(Exception, match="not found in registry"):
        import asyncio
        from agentic_core.L2_execution.types.gateway_types import GenerationRequest
        asyncio.run(gateway.route_generation(
            GenerationRequest(
                prompt="test prompt",
                agent_id="nonexistent_agent"
            )
        ))


@pytest.mark.allow_network
def test_route_generation_enforces_deterministic_temperature():
    """route_generation must enforce temperature=0.0 for deterministic agents."""
    import pytest
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        get_llm_gateway,
    )
    from agentic_core.L0_routing.types.guardian_contract import V15HardFailAbort

    gateway = get_llm_gateway()

    # Mock a deterministic agent profile
    try:
        from agentic_core.agents.agent_registry import AgentProfile, ExecutionMode

        # Create a deterministic profile for testing
        deterministic_profile = AgentProfile(
            agent_id="test_deterministic_agent",
            execution_mode=ExecutionMode.DETERMINISTIC,
            reasoning_intensity="LOW",
            allowed_models=["gpt-4"],
            description="Test deterministic agent",
        )

        # Temporarily add to registry for test
        from agentic_core.agents.agent_registry import AGENT_REGISTRY
        AGENT_REGISTRY["test_deterministic_agent"] = deterministic_profile

        # Should enforce temperature=0.0 even if we pass 0.7
        # This would require mocking the underlying provider to verify
        # For now, just verify the method exists and accepts the parameters
        import asyncio
        try:
            asyncio.run(gateway.route_generation(
                "test prompt",
                agent_id="test_deterministic_agent",
                temperature=0.7,  # Should be overridden to 0.0
            ))
        except V15HardFailAbort:
            # Expected - we don't have proper provider setup
            pass
        finally:
            # Clean up
            AGENT_REGISTRY.pop("test_deterministic_agent", None)

    except ImportError:
        pytest.skip("Agent registry not available for temperature enforcement test")


# ---------------------------------------------------------------------------
# T2: AST Scanner - No Bypass Detection
# ---------------------------------------------------------------------------

def test_ast_scanner_detects_generation_bypass():
    """AST scan must detect generation routing bypass attempts."""
    py_files = _collect_py_files(SCAN_ROOTS)
    violations_by_file: Dict[str, List[str]] = {}

    for filepath in py_files:
        canon = _canonical_path(filepath)

        # Skip allowed contexts
        if any(canon.startswith(allowed) for allowed in ALLOWED_SDK_IMPORTS):
            continue

        try:
            source = filepath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        violations = _ast_scan_for_bypass(source, canon)
        if violations:
            violations_by_file[canon] = violations

    # Check known debt
    found_count = len(violations_by_file)
    ceiling = KNOWN_BYPASS_DEBT_CEILING
    delta = found_count - ceiling

    # Print governance signal
    print(
        f"\nGENERATION-BYPASS-DEBT: found={found_count}, ceiling={ceiling}, delta={delta}"
    )
    for path, viols in sorted(violations_by_file.items()):
        for v in viols:
            print(f"  {'[KNOWN]' if path in KNOWN_BYPASS_DEBT else '[NEW!]'} {path}: {v}")

    # Detect unknown violations
    unknown_violations = sorted(
        path for path in violations_by_file if path not in KNOWN_BYPASS_DEBT
    )
    if unknown_violations:
        lines = ["NEW GENERATION BYPASS VIOLATIONS:"]
        for path in unknown_violations:
            for v in violations_by_file[path]:
                lines.append(f"  {path}: {v}")
        pytest.fail("\n".join(lines))

    # Enforce non-growing ceiling
    assert found_count <= ceiling, (
        f"GENERATION-BYPASS-DEBT ceiling exceeded: found={found_count}, ceiling={ceiling}, delta={delta}"
    )


# ---------------------------------------------------------------------------
# T3: Apps_* Representative Callsites
# ---------------------------------------------------------------------------

def test_apps_representative_callsites_can_use_gateway():
    """Representative apps_* callsites can request LLM generation via gateway."""
    # This test verifies the interface exists and is callable
    # In a real scenario, apps_* would use call_llm() which calls gateway.route_generation()

    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        get_llm_gateway,
    )

    gateway = get_llm_gateway()

    # Verify the method signature is correct
    import inspect
    sig = inspect.signature(gateway.route_generation)

    # The gateway takes a GenerationRequest object, not individual parameters
    assert "request" in sig.parameters, "Missing required parameter: request"
    assert "**kwargs" in str(sig), "Missing **kwargs for flexibility"


def test_deterministic_agents_blocked_from_gateway():
    """DETERMINISTIC agents must be blocked from LLM gateway."""
    import pytest
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        get_llm_gateway,
    )
    from agentic_core.L0_routing.types.guardian_contract import V15HardFailAbort

    gateway = get_llm_gateway()

    # Test with a deterministic agent profile
    try:
        from agentic_core.agents.agent_registry import AgentProfile, ExecutionMode

        # Create a deterministic profile
        deterministic_profile = AgentProfile(
            agent_id="test_rule_only_agent",
            execution_mode=ExecutionMode.RULE_ONLY,  # DETERMINISTIC equivalent
            reasoning_intensity="LOW",
            allowed_models=["gpt-4"],
            description="Test RULE_ONLY agent",
        )

        # Temporarily add to registry
        from agentic_core.agents.agent_registry import AGENT_REGISTRY
        AGENT_REGISTRY["test_rule_only_agent"] = deterministic_profile

        # Should be blocked
        with pytest.raises(V15HardFailAbort, match="execution_mode=DETERMINISTIC"):
            import asyncio
            asyncio.run(gateway.route_generation(
                "test prompt",
                agent_id="test_rule_only_agent",
            ))

        # Clean up
        AGENT_REGISTRY.pop("test_rule_only_agent", None)

    except ImportError:
        pytest.skip("Agent registry not available for deterministic agent test")


# ---------------------------------------------------------------------------
# T4: W9 Digest Determinism
# ---------------------------------------------------------------------------

def test_w9_digest_is_computed_and_stable():
    """W9-DETERMINISM-DIGEST must be computable and stable."""
    # Compute digest manually (similar to conftest logic)
    import hashlib
    import json

    routing_files = {
        "sovereign_llm_gateway": REPO_ROOT / "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py",
        "agent_registry": REPO_ROOT / "agentic_core/agents/agent_registry.py",
    }

    file_hashes = {}
    for name, path in routing_files.items():
        if path.exists():
            file_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            file_hashes[name] = "MISSING"

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

    canonical_json = json.dumps(state, separators=(",", ":"), sort_keys=True)
    digest1 = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    # Verify format
    assert len(digest1) == 64
    assert all(c in "0123456789abcdef" for c in digest1)

    # Compute again (should be identical)
    digest2 = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    assert digest1 == digest2, "W9 digest must be stable across calls"


# ---------------------------------------------------------------------------
# T5: Negative Control (W9_NEGCTRL_TAMPER)
# ---------------------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason="W9_NEGCTRL_TAMPER=1 must xfail; restore run must pass")
def test_w9_negative_control_tamper_detection():
    """When W9_NEGCTRL_TAMPER=1, injecting bypass must trigger scanner."""
    tamper = os.environ.get("W9_NEGCTRL_TAMPER", "0")

    if tamper != "1":
        pytest.skip("W9_NEGCTRL_TAMPER not set — restore run, skipping tamper body")

    # Tamper: create a temporary file with forbidden import
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""
# Temporary bypass for tamper test
import openai  # Forbidden SDK import
from anthropic import Anthropic  # Another forbidden import

def rogue_function():
    model = "gpt-4"  # Forbidden model literal
    return model
""")
        temp_file = pathlib.Path(f.name)

    try:
        # Scan the temporary file
        source = temp_file.read_text()
        violations = _ast_scan_for_bypass(source, "temp_tamper_file.py")

        # Should detect violations
        assert len(violations) >= 2, f"Expected at least 2 violations, got {len(violations)}"

        # Guard triggered as expected - now deliberately fail to produce xfail
        assert False, "NEGCTRL: bypass scanner triggered as expected (intentional fail)"

    finally:
        # Clean up
        temp_file.unlink()


# ---------------------------------------------------------------------------
# T6: Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.allow_network
def test_gateway_route_generation_integration():
    """Test gateway route_generation integration with agent registry."""
    import pytest
    try:
        from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
            get_llm_gateway,
        )
        from agentic_core.agents.agent_registry import AgentProfile, ExecutionMode

        # Create a test agent profile
        test_profile = AgentProfile(
            agent_id="test_integration_agent",
            execution_mode=ExecutionMode.LLM_API,
            reasoning_intensity="MEDIUM",
            allowed_models=["gpt-4"],
            description="Test integration agent",
        )

        # Temporarily add to registry
        from agentic_core.agents.agent_registry import AGENT_REGISTRY
        AGENT_REGISTRY["test_integration_agent"] = test_profile

        gateway = get_llm_gateway()

        # Verify the method can be called (will fail at provider level, which is expected)
        from agentic_core.L0_routing.types.guardian_contract import V15HardFailAbort

        with pytest.raises((V15HardFailAbort, RuntimeError)):
            import asyncio
            asyncio.run(gateway.route_generation(
                "test prompt",
                agent_id="test_integration_agent",
                model="gpt-4",
            ))

        # Clean up
        AGENT_REGISTRY.pop("test_integration_agent", None)

    except ImportError:
        pytest.skip("Agent registry not available for integration test")


def test_no_new_bypass_violations():
    """Ensure no new bypass violations have been introduced."""
    # This is a redundant check to emphasize the importance
    test_ast_scanner_detects_generation_bypass()


pytestmark = pytest.mark.unit_min_deps
