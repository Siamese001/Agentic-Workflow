"""
Simplified Final Integrity Audit - Direct testing of core components.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_canon_key_purification():
    """
    [CRITICAL] Verify structure_blueprint.py is physically scrubbed of deprecated variables.
    """
    blueprint_path = (
        project_root / "agentic_core" / "L5_safety" / "validators" / "structure_blueprint.py"
    )

    with open(blueprint_path, encoding="utf-8") as f:
        content = f.read()

    forbidden = ["CANON_KEY_EXCEPTIONS", "ACTIVE_CANON_KEYS", "CANON_KEY_TO_FOLDER_MAP"]
    for f in forbidden:
        assert f not in content, f"GHOST GRAVITY DETECTED: {f} still exists in SSOT."


def test_root_directory_constants():
    """
    [SSOT] Verify root directory constants are present and correctly typed.
    """
    blueprint_path = (
        project_root / "agentic_core" / "L5_safety" / "validators" / "structure_blueprint.py"
    )

    with open(blueprint_path, encoding="utf-8") as f:
        content = f.read()

    required_constants = [
        'AGENTIC_CORE_DIR: Final[str] = "agentic_core"',
        'APPS_RG_DIR: Final[str] = "apps_rg"',
        'APPS_LIC_DIR: Final[str] = "apps_lic"',
        'APPS_SHARED_DIR: Final[str] = "apps_shared"',
    ]

    for const in required_constants:
        assert const in content, f"Missing or incorrect constant: {const}"


def test_metadata_immutability():
    """
    [HARDENING] Verify discovery_parser implements immutable Mapping.
    """
    parser_path = project_root / "agentic_core" / "utils" / "discovery_parser.py"

    with open(parser_path, encoding="utf-8") as f:
        content = f.read()

    # Check for immutable Mapping implementation
    assert "class AgentListMapping(Mapping[str, Any]):" in content
    assert "def __getitem__(self, key: str) -> Any:" in content
    assert "def __len__(self) -> int:" in content
    assert "def __iter__(self):" in content
    assert "AGENT_METADATA: Final[Mapping[str, Any]]" in content


def test_location_agent_purge():
    """
    [LOGIC PURGE] Verify LocationAgent has no deprecated key-bypass logic.
    """
    location_path = project_root / "agentic_core" / "L5_safety" / "validators" / "LocationAgent.py"

    with open(location_path, encoding="utf-8") as f:
        content = f.read()

    # Ensure deprecated method is completely removed
    assert "is_excepted_from_key" not in content, (
        "LocationAgent still retains deprecated key exception logic"
    )


def test_discovery_parser_final_annotations():
    """
    [FINAL ANNOTATIONS] Verify proper Final type annotations.
    """
    parser_path = project_root / "agentic_core" / "utils" / "discovery_parser.py"

    with open(parser_path, encoding="utf-8") as f:
        content = f.read()

    # Check for Final annotations
    assert "from typing import Mapping, Dict, Any, Final" in content
    assert "AGENT_METADATA: Final[Mapping[str, Any]]" in content


def test_structure_blueprint_completeness():
    """
    [SSOT COMPLETENESS] Verify all required components are present.
    """
    blueprint_path = (
        project_root / "agentic_core" / "L5_safety" / "validators" / "structure_blueprint.py"
    )

    with open(blueprint_path, encoding="utf-8") as f:
        content = f.read()

    required_components = [
        "SOVEREIGN_REGISTRY",
        "CANON_VALIDATION_REGISTRY",
        "CORE_SUBFOLDER_MAP",
        "VARIABLE_DEPTH_SUBFOLDERS",
    ]

    for component in required_components:
        assert component in content, f"Missing SSOT component: {component}"


def test_no_ghost_variables():
    """
    [GHOST CLEANUP] Comprehensive scan for deprecated variables.
    """
    blueprint_path = (
        project_root / "agentic_core" / "L5_safety" / "validators" / "structure_blueprint.py"
    )

    with open(blueprint_path, encoding="utf-8") as f:
        content = f.read()

    # Scan for any ghost patterns
    ghost_patterns = ["canon_key", "CANON_KEY", "key_exception", "KEY_EXCEPTION"]

    for pattern in ghost_patterns:
        # Skip comments and docstrings
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if pattern in line.upper() and not line.strip().startswith("#") and '"""' not in line:
                # Allow certain legitimate uses
                if "CANON_VALIDATION_REGISTRY" in line or "canon_validator" in line:
                    continue
                assert False, f"POTENTIAL GHOST VARIABLE DETECTED at line {i + 1}: {line.strip()}"


def test_utf8_encoding_enforcement():
    """
    [ENCODING STABILITY] Verify UTF-8 encoding is enforced.
    """
    parser_path = project_root / "agentic_core" / "utils" / "discovery_parser.py"

    with open(parser_path, encoding="utf-8") as f:
        content = f.read()

    # Check for UTF-8 encoding specification
    assert "encoding='utf-8'" in content, "UTF-8 encoding not enforced in discovery parser"


if __name__ == "__main__":
    print("Executing Final Integrity Audit: 100% PASS required.")
    pytest.main([__file__, "-v"])
