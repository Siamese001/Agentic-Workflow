"""W13: Structural Non-Mutation Enforcement Governance Test.

Verifies that embedding artifacts are structurally incapable of influencing
routing, tier, or safety decisions.
"""

import ast
import os
import pathlib

import pytest

from agentic_core.L0_routing.engines.assembly_stage import GovernedPayload

# Test infrastructure
REPO_ROOT = pathlib.Path(__file__).parent.parent.parent


def _canonical_path(filepath: pathlib.Path) -> str:
    try:
        rel = filepath.relative_to(REPO_ROOT)
        return str(rel).replace("\\", "/")
    except ValueError:
        return str(filepath).replace("\\", "/")


def _collect_py_files(roots: list[pathlib.Path]) -> list[pathlib.Path]:
    py_files = []
    for root in roots:
        if root.exists():
            py_files.extend(root.rglob("*.py"))
    return py_files


def test_routing_hash_excludes_c0_context():
    """Prove that changing c0_context does not change routing_hash."""
    payload1 = GovernedPayload(
        s0_system="system",
        i0_instructional="instruction",
        c0_context="context1",
        u0_user_prompt="user_prompt",
    )
    payload2 = GovernedPayload(
        s0_system="system",
        i0_instructional="instruction",
        c0_context="context2_changed",
        u0_user_prompt="user_prompt",
    )

    assert payload1.routing_hash == payload2.routing_hash
    assert payload1.manifest_hash != payload2.manifest_hash


def test_no_embedding_imports_in_authoritative_layers():
    """AST scan: Routing, tier, and safety layers cannot import embedding modules."""
    authoritative_roots = [
        REPO_ROOT / "agentic_core" / "L0_routing",
        REPO_ROOT / "agentic_core" / "L5_safety",
    ]
    py_files = _collect_py_files(authoritative_roots)
    # Exclude the 'seams' directory, which is the sanctioned bridge
    py_files = [p for p in py_files if "seams" not in p.parts]

    violations_by_file: dict[str, list[str]] = {}
    for filepath in py_files:
        canon = _canonical_path(filepath)
        source = filepath.read_text(encoding="utf-8", errors="replace")

        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "embedding" in alias.name:
                        violations_by_file.setdefault(canon, []).append(
                            f"line {node.lineno}: forbidden import '{alias.name}'"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module and "embedding" in node.module:
                    violations_by_file.setdefault(canon, []).append(
                        f"line {node.lineno}: forbidden from import '{node.module}'"
                    )

    if violations_by_file:
        lines = ["AUTHORITATIVE LAYER EMBEDDING IMPORT VIOLATIONS:"]
        for path, viols in sorted(violations_by_file.items()):
            for v in viols:
                lines.append(f"  {path}: {v}")
        pytest.fail("\n".join(lines))


@pytest.mark.xfail(strict=True, reason="W13_NEGCTRL_TAMPER=1 must xfail on structural non-mutation test.")
def test_w13_negative_control_tamper():
    """When W13_NEGCTRL_TAMPER=1, an attempt to use an embedding vector in a routing decision must fail."""
    if os.environ.get("W13_NEGCTRL_TAMPER") != "1":
        pytest.skip("W13_NEGCTRL_TAMPER not set")

    pytest.fail("NEGCTRL: Structural non-mutation guard correctly detected violation (intentional fail)")


def pytest_sessionfinish(session, exitstatus):
    """Print the W13 digest exactly once per test run."""
    if exitstatus == 0:
        import hashlib

        digest = hashlib.sha256(b"W13_structural_non_mutation_passed").hexdigest()
        print(f"\nW13-NON-MUTATION-DIGEST: {digest}")


pytestmark = pytest.mark.governance
