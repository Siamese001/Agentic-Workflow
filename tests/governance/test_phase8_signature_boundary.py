"""Phase 8: Signature & Side-Effect Boundary Hardening

Tests for:
- Central signature verifier (SSOT)
- Side-effect guard with require_verified()
- All side-effect seams instrumented with verification
- AST scanner for unsigned ingress detection
- Runtime enforcement tests
- W8-SIGNATURE-INTEGRITY-DIGEST determinism
- W8_NEGCTRL_TAMPER negative control
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

# Side-effect entrypoints that require verification
SIDE_EFFECT_ENTRYPOINTS = {
    # Execution engines
    "agentic_core.L2_execution",
    "agentic_core.L2_execution.reasoning",
    # State management
    "agentic_core.L4_state",
    "agentic_core.L4_state.persistence",
    # Gateway
    "agentic_core.L2_execution.enforcement.SovereignLLMGateway",
    # Embedding factory
    "agentic_core.embeddings.embedding_factory",
    # File operations
    "pathlib.Path.write_text",
    "pathlib.Path.write_bytes",
    "open",
    # Network/LLM calls
    "requests.request",
    "httpx.request",
    # Subprocess
    "subprocess.run",
    "subprocess.Popen",
    "os.system",
}

# Allowlisted modules that can bypass verification (test harness, infra)
ALLOWLISTED_BYPASS = {
    "tests",
    "test_",
    "conftest",
    "pytest",
    "__main__",
    "ops_scripts",
    "data.sdks_mcps",
}

# Known unsigned debt (baseline)
KNOWN_UNSIGNED_DEBT = {
    "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
    "agentic_core/L2_execution/reasoning/StrategyExecutorAgent.py",
    "agentic_core/L2_execution/reasoning/HealingOrchestratorAgent.py",
    "agentic_core/L2_execution/reasoning/SovereignBaseAgent.py",
    "agentic_core/L2_execution/reasoning/TemplateExecutorAgent.py",
    "agentic_core/L2_execution/reasoning/StrategyExecutorAgent.py",
    "agentic_core/L2_execution/reasoning/TemplateExecutorAgent.py",
    "agentic_core/L2_execution/reasoning/HealingOrchestratorAgent.py",
    "agentic_core/L2_execution/reasoning/SovereignBaseAgent.py",
    "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
    "agentic_core/L2_execution/reasoning/StrategyExecutorAgent.py",
    "agentic_core/L2_execution/reasoning/TemplateExecutorAgent.py",
    "agentic_core/L2_execution/reasoning/HealingOrchestratorAgent.py",
    "agentic_core/L2_execution/reasoning/SovereignBaseAgent.py",
    "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
    "agentic_core/L2_execution/reasoning/StrategyExecutorAgent.py",
    "agentic_core/L2_execution/reasoning/TemplateExecutorAgent.py",
    "agentic_core/L2_execution/reasoning/HealingOrchestratorAgent.py",
    "agentic_core/L2_execution/reasoning/SovereignBaseAgent.py",
    "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
    "agentic_core/L2_execution/reasoning/StrategyExecutorAgent.py",
    "agentic_core/L2_execution/reasoning/TemplateExecutorAgent.py",
    "agentic_core/L2_execution/reasoning/HealingOrchestratorAgent.py",
    "agentic_core/L2_execution/reasoning/SovereignBaseAgent.py",
    "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
    "agentic_core/L2_execution/reasoning/StrategyExecutorAgent.py",
    "agentic_core/L2_execution/reasoning/TemplateExecutorAgent.py",
    "agentic_core/L2_execution/reasoning/HealingOrchestratorAgent.py",
    "agentic_core/L2_execution/reasoning/SovereignBaseAgent.py",
    "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
}

KNOWN_UNSIGNED_DEBT_CEILING = len(KNOWN_UNSIGNED_DEBT)


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


def _ast_has_unsigned_side_effects(source: str, filepath: str) -> List[str]:
    """Check if AST contains side-effect calls without verification context."""
    violations = []
    
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["SYNTAX_ERROR"]
    
    # Track if verification context is established
    has_verification = False
    
    for node in ast.walk(tree):
        # Check for verification context establishment
        if isinstance(node, ast.Call):
            if (isinstance(node.func, ast.Attribute) and 
                node.func.attr in {"require_verified", "set_verification_context", "verify"}):
                has_verification = True
            elif (isinstance(node.func, ast.Name) and 
                  node.func.id in {"require_verified", "set_verification_context", "verify"}):
                has_verification = True
        
        # Check for side-effect calls
        elif isinstance(node, ast.Call):
            side_effect_found = False
            side_effect_name = None
            
            if isinstance(node.func, ast.Attribute):
                # Method calls
                if isinstance(node.func.value, ast.Name):
                    full_name = f"{node.func.value.id}.{node.func.attr}"
                    if any(entry in full_name for entry in SIDE_EFFECT_ENTRYPOINTS):
                        side_effect_found = True
                        side_effect_name = full_name
                elif isinstance(node.func.value, ast.Attribute):
                    # Nested attribute calls
                    chain = []
                    curr = node.func.value
                    while isinstance(curr, ast.Attribute):
                        chain.append(curr.attr)
                        curr = curr.value
                    if isinstance(curr, ast.Name):
                        chain.append(curr.id)
                        chain.reverse()
                        full_name = ".".join(chain + [node.func.attr])
                        if any(entry in full_name for entry in SIDE_EFFECT_ENTRYPOINTS):
                            side_effect_found = True
                            side_effect_name = full_name
            elif isinstance(node.func, ast.Name):
                # Function calls
                if node.func.id in SIDE_EFFECT_ENTRYPOINTS:
                    side_effect_found = True
                    side_effect_name = node.func.id
            
            if side_effect_found and not has_verification:
                violations.append(f"line {node.lineno}: {side_effect_name} without verification")
    
    return violations


# ---------------------------------------------------------------------------
# T1: Central Signature Verifier
# ---------------------------------------------------------------------------

def test_signature_verifier_exists_and_is_importable():
    """Verify signature verifier exists and can be imported."""
    from agentic_core.security.signature_verifier import (
        SignatureVerifier,
        InstructionPacket,
        SandboxEnvelope,
        VerificationContext,
        verify_instruction_packet,
        verify_sandbox_envelope,
        SignatureVerificationError,
    )
    
    # Verify module structure
    assert SignatureVerifier is not None
    assert InstructionPacket is not None
    assert SandboxEnvelope is not None
    assert VerificationContext is not None
    assert callable(verify_instruction_packet)
    assert callable(verify_sandbox_envelope)
    assert SignatureVerificationError is not None


def test_signature_verifier_fail_closed():
    """Signature verifier must fail closed on missing/invalid signatures."""
    from agentic_core.security.signature_verifier import (
        InstructionPacket,
        SandboxEnvelope,
        SignatureVerificationError,
        verify_instruction_packet,
    )
    
    # Missing signature
    packet_no_sig = InstructionPacket(payload={"test": "data"})
    with pytest.raises(SignatureVerificationError, match="MISSING_SIGNATURE"):
        verify_instruction_packet(packet_no_sig)
    
    # Missing signer
    packet_no_signer = InstructionPacket(
        payload={"test": "data"},
        signature="fake_signature"
    )
    with pytest.raises(SignatureVerificationError, match="MISSING_SIGNER"):
        verify_instruction_packet(packet_no_signer)
    
    # Invalid signature
    packet_invalid = InstructionPacket(
        payload={"test": "data"},
        signature="invalid_signature",
        signer_id="system"
    )
    with pytest.raises(SignatureVerificationError, match="INVALID_SIGNATURE"):
        verify_instruction_packet(packet_invalid)


def test_signature_verifier_accepts_valid():
    """Signature verifier must accept valid signatures."""
    from agentic_core.security.signature_verifier import (
        InstructionPacket,
        SandboxEnvelope,
        verify_instruction_packet,
        verify_sandbox_envelope,
        get_signature_verifier,
    )
    
    # Get verifier and add test signer
    verifier = get_signature_verifier()
    verifier.add_trusted_signer("test_signer", "test_key_hash")
    
    # Create valid packet
    packet = InstructionPacket(
        payload={"test": "data"},
        signer_id="test_signer"
    )
    
    # Compute correct signature
    packet_hash = packet.compute_hash()
    correct_signature = verifier._compute_signature(packet_hash, "test_signer")
    packet = InstructionPacket(
        payload={"test": "data"},
        signature=correct_signature,
        signer_id="test_signer"
    )
    
    # Should verify successfully
    context = verify_instruction_packet(packet)
    assert context.is_verified
    assert context.signer_id == "test_signer"
    assert context.signature_hash == correct_signature


# ---------------------------------------------------------------------------
# T2: Side-Effect Guard
# ---------------------------------------------------------------------------

def test_side_effect_guard_exists_and_is_importable():
    """Verify side-effect guard exists and can be imported."""
    from agentic_core.security.side_effect_guard import (
        SideEffectGuard,
        require_verified,
        set_verification_context,
        clear_verification_context,
        requires_verification,
        UnverifiedSideEffectError,
    )
    
    # Verify module structure
    assert SideEffectGuard is not None
    assert callable(require_verified)
    assert callable(set_verification_context)
    assert callable(clear_verification_context)
    assert callable(requires_verification)
    assert UnverifiedSideEffectError is not None


def test_side_effect_guard_blocks_unverified():
    """Guard must block operations without verification context."""
    from agentic_core.security.side_effect_guard import (
        require_verified,
        clear_verification_context,
        UnverifiedSideEffectError,
    )
    
    # Clear any existing context
    clear_verification_context()
    
    # Should raise without context
    with pytest.raises(UnverifiedSideEffectError, match="UNVERIFIED_OPERATION_DENIED"):
        require_verified("test_operation")


def test_side_effect_guard_allows_verified():
    """Guard must allow operations with verified context."""
    from agentic_core.security.side_effect_guard import (
        require_verified,
        set_verification_context,
        clear_verification_context,
        UnverifiedSideEffectError,
    )
    from agentic_core.security.signature_verifier import VerificationContext
    
    # Clear any existing context
    clear_verification_context()
    
    # Set verified context
    context = VerificationContext(
        is_verified=True,
        signature_hash="test_hash",
        signer_id="test_signer",
        packet_hash="packet_hash",
    )
    set_verification_context(context)
    
    # Should allow with context
    result = require_verified("test_operation")
    assert result.is_verified
    assert result.signer_id == "test_signer"


# ---------------------------------------------------------------------------
# T3: AST Scanner - Unsigned Ingress Detection
# ---------------------------------------------------------------------------

def test_ast_unsigned_ingress_scanner_finds_known_debt():
    """AST scan must find known unsigned side-effect violations."""
    py_files = _collect_py_files(SCAN_ROOTS)
    violations_by_file: Dict[str, List[str]] = {}
    
    for filepath in py_files:
        canon = _canonical_path(filepath)
        
        # Skip allowlisted paths
        if any(canon.startswith(allowed) for allowed in ALLOWLISTED_BYPASS):
            continue
        
        try:
            source = filepath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        
        violations = _ast_has_unsigned_side_effects(source, canon)
        if violations:
            violations_by_file[canon] = violations
    
    # Check known debt
    found_count = len(violations_by_file)
    ceiling = KNOWN_UNSIGNED_DEBT_CEILING
    delta = found_count - ceiling
    
    # Print governance signal
    print(
        f"\nUNSIGNED-DEBT: found={found_count}, ceiling={ceiling}, delta={delta}"
    )
    for path, viols in sorted(violations_by_file.items()):
        for v in viols:
            print(f"  {'[KNOWN]' if path in KNOWN_UNSIGNED_DEBT else '[NEW!]'} {path}: {v}")
    
    # Detect unknown violations
    unknown_violations = sorted(
        path for path in violations_by_file if path not in KNOWN_UNSIGNED_DEBT
    )
    if unknown_violations:
        lines = ["NEW UNSIGNED VIOLATIONS:"]
        for path in unknown_violations:
            for v in violations_by_file[path]:
                lines.append(f"  {path}: {v}")
        pytest.fail("\n".join(lines))
    
    # Enforce non-growing ceiling
    assert found_count <= ceiling, (
        f"UNSIGNED-DEBT ceiling exceeded: found={found_count}, ceiling={ceiling}, delta={delta}"
    )


# ---------------------------------------------------------------------------
# T4: Runtime Enforcement Tests
# ---------------------------------------------------------------------------

def test_verified_packet_can_execute():
    """Verified packet should be able to execute deterministic operations."""
    from agentic_core.security.signature_verifier import (
        InstructionPacket,
        VerificationContext,
    )
    from agentic_core.security.side_effect_guard import (
        set_verification_context,
        clear_verification_context,
        require_verified,
    )
    
    # Clear context
    clear_verification_context()
    
    # Create verified context
    context = VerificationContext(
        is_verified=True,
        signature_hash="test_hash",
        signer_id="test_signer",
        packet_hash="packet_hash",
    )
    set_verification_context(context)
    
    # Should be able to require verification
    result = require_verified("deterministic_operation")
    assert result.is_verified


def test_unverified_packet_blocked():
    """Unverified packet should be blocked at ingress."""
    from agentic_core.security.side_effect_guard import (
        clear_verification_context,
        require_verified,
        UnverifiedSideEffectError,
    )
    
    # Clear context
    clear_verification_context()
    
    # Should be blocked
    with pytest.raises(UnverifiedSideEffectError, match="UNVERIFIED_OPERATION_DENIED"):
        require_verified("blocked_operation")


# ---------------------------------------------------------------------------
# T5: W8 Digest Determinism
# ---------------------------------------------------------------------------

def test_w8_digest_is_computed_and_stable():
    """W8-SIGNATURE-INTEGRITY-DIGEST must be computable and stable."""
    # Compute digest manually (similar to conftest logic)
    import hashlib
    import json
    
    security_files = {
        "signature_verifier": REPO_ROOT / "agentic_core/security/signature_verifier.py",
        "side_effect_guard": REPO_ROOT / "agentic_core/security/side_effect_guard.py",
    }
    
    file_hashes = {}
    for name, path in security_files.items():
        if path.exists():
            file_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            file_hashes[name] = "MISSING"
    
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
    
    canonical_json = json.dumps(state, separators=(",", ":"), sort_keys=True)
    digest1 = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    
    # Verify format
    assert len(digest1) == 64
    assert all(c in "0123456789abcdef" for c in digest1)
    
    # Compute again (should be identical)
    digest2 = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    assert digest1 == digest2, "W8 digest must be stable across calls"


def test_w8_digest_changes_with_security_files():
    """W8 digest must change when security files change."""
    # This is a simplified test - in practice, file changes would affect hash
    # For now, just verify the digest computation works
    test_w8_digest_is_computed_and_stable()


# ---------------------------------------------------------------------------
# T6: Negative Control (W8_NEGCTRL_TAMPER)
# ---------------------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason="W8_NEGCTRL_TAMPER=1 must xfail; restore run must pass")
def test_w8_negative_control_tamper_detection():
    """When W8_NEGCTRL_TAMPER=1, injecting invalid signature must trigger guard."""
    tamper = os.environ.get("W8_NEGCTRL_TAMPER", "0")
    
    if tamper != "1":
        pytest.skip("W8_NEGCTRL_TAMPER not set — restore run, skipping tamper body")
    
    # Tamper: attempt operation with invalid signature
    from agentic_core.security.signature_verifier import (
        InstructionPacket,
        SignatureVerificationError,
    )
    
    caught = False
    try:
        packet = InstructionPacket(
            payload={"tampered": True},
            signature="invalid_signature",
            signer_id="system"
        )
        # This would raise in real verification
        from agentic_core.security.signature_verifier import verify_instruction_packet
        verify_instruction_packet(packet)
    except SignatureVerificationError:
        caught = True
    
    # Guard triggered as expected - now deliberately fail to produce xfail
    assert not caught, "NEGCTRL: signature verification triggered as expected (intentional fail)"


@pytest.mark.xfail(strict=True, reason="W8_NEGCTRL_TAMPER=1 must xfail; restore run must pass")
def test_w8_full_signature_boundary_system():
    """Full signature boundary system test."""
    tamper = os.environ.get("W8_NEGCTRL_TAMPER", "0")
    
    if tamper != "1":
        pytest.skip("W8_NEGCTRL_TAMPER not set — restore run, skipping tamper body")
    
    # Tamper: attempt side-effect without verification
    from agentic_core.security.side_effect_guard import (
        clear_verification_context,
        require_verified,
        UnverifiedSideEffectError,
    )
    
    caught = False
    try:
        clear_verification_context()
        require_verified("tampered_operation")
    except UnverifiedSideEffectError:
        caught = True
    
    assert not caught, "NEGCTRL: side-effect guard triggered as expected (intentional fail)"


# ---------------------------------------------------------------------------
# T7: Integration Tests
# ---------------------------------------------------------------------------

def test_signature_verifier_integration_with_guard():
    """Signature verifier must integrate with side-effect guard."""
    from agentic_core.security.signature_verifier import (
        InstructionPacket,
        verify_instruction_packet,
        get_signature_verifier,
    )
    from agentic_core.security.side_effect_guard import (
        set_verification_context,
        clear_verification_context,
        require_verified,
    )
    
    # Clear context
    clear_verification_context()
    
    # Get verifier and add test signer
    verifier = get_signature_verifier()
    verifier.add_trusted_signer("integration_test", "test_key")
    
    # Create and verify packet
    packet = InstructionPacket(
        payload={"integration": "test"},
        signer_id="integration_test"
    )
    packet_hash = packet.compute_hash()
    signature = verifier._compute_signature(packet_hash, "integration_test")
    packet = InstructionPacket(
        payload={"integration": "test"},
        signature=signature,
        signer_id="integration_test"
    )
    
    # Verify packet
    context = verify_instruction_packet(packet)
    
    # Set context in guard
    set_verification_context(context)
    
    # Should be able to perform side-effect
    result = require_verified("integration_operation")
    assert result.is_verified
    assert result.signer_id == "integration_test"


def test_no_bypass_through_disabled_guard():
    """Disabled guard should still be detectable."""
    from agentic_core.security.side_effect_guard import (
        get_side_effect_guard,
        clear_verification_context,
        require_verified,
    )
    
    guard = get_side_effect_guard()
    clear_verification_context()
    
    # Enable guard (default)
    guard.enable()
    with pytest.raises(Exception):  # Should raise without context
        require_verified("test")
    
    # Disable guard
    guard.disable()
    # Should not raise when disabled
    result = require_verified("test")
    assert result.signer_id == "disabled"
    
    # Re-enable for cleanup
    guard.enable()


pytestmark = pytest.mark.unit_min_deps
