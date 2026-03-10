"""
Wave 15.1 — Layer Inventory + Deterministic Scanner.

Deterministic AST-based scanner for layer discovery and file classification.
No enforcement yet — inventory only.
"""

import re
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
)

AGENTIC_CORE_ROOT = Path(__file__).parent.parent.parent / AGENTIC_CORE_DIR
LAYER_PATTERN = re.compile(r"^L(\d+)_")


def layer_of_path(path: Path) -> int | None:
    """Extract layer number from a path.

    Args:
        path: Path to a file or directory.

    Returns:
        Layer number (0-6) if path is within a layer directory, None otherwise.
    """
    try:
        rel = path.relative_to(AGENTIC_CORE_ROOT)
    except ValueError:
        return None

    parts = rel.parts
    if not parts:
        return None

    match = LAYER_PATTERN.match(parts[0])
    if match:
        return int(match.group(1))
    return None


def classify_file(path: Path) -> dict:
    """Classify a Python file by layer, utils status, and seam status.

    Args:
        path: Path to a Python file.

    Returns:
        Dict with keys: layer, is_utils, is_seam
    """
    layer = layer_of_path(path)

    try:
        rel = path.relative_to(AGENTIC_CORE_ROOT)
        parts = rel.parts
    except ValueError:
        parts = ()

    is_utils = "utils" in parts
    is_seam = "seam" in path.stem.lower() or "seams" in parts

    return {
        "layer": layer,
        "is_utils": is_utils,
        "is_seam": is_seam,
    }


def discover_layers() -> list[int]:
    """Dynamically discover all layer directories in agentic_core.

    Returns:
        Sorted list of layer numbers found.
    """
    layers = []
    for item in AGENTIC_CORE_ROOT.iterdir():
        if item.is_dir():
            match = LAYER_PATTERN.match(item.name)
            if match:
                layers.append(int(match.group(1)))
    return sorted(layers)


def enumerate_python_files() -> list[Path]:
    """Enumerate all Python files under agentic_core deterministically.

    Returns:
        Sorted list of all .py files.
    """
    files = sorted(AGENTIC_CORE_ROOT.rglob("*.py"))
    return files


def enumerate_layer_files(layer: int) -> list[Path]:
    """Enumerate all Python files in a specific layer.

    Args:
        layer: Layer number (0-6).

    Returns:
        Sorted list of .py files in that layer.
    """
    layer_dir = None
    for item in AGENTIC_CORE_ROOT.iterdir():
        if item.is_dir() and item.name.startswith(f"L{layer}_"):
            layer_dir = item
            break

    if layer_dir is None:
        return []

    return sorted(layer_dir.rglob("*.py"))


@pytest.mark.governance
class TestLayerInventory:
    """Test suite for layer inventory and deterministic scanning."""

    def test_exactly_seven_layers_exist(self):
        """Assert exactly 7 layers exist (L0–L6)."""
        layers = discover_layers()
        assert layers == [0, 1, 2, 3, 4, 5, 6], f"Expected L0-L6, got {layers}"

    def test_layer_ordering_is_monotonic(self):
        """Assert layer ordering is monotonic (strictly increasing)."""
        layers = discover_layers()
        for i in range(len(layers) - 1):
            assert layers[i] < layers[i + 1], f"Non-monotonic at index {i}"

    def test_file_enumeration_count_is_stable(self):
        """Assert file enumeration produces consistent count across calls."""
        count1 = len(enumerate_python_files())
        count2 = len(enumerate_python_files())
        count3 = len(enumerate_python_files())

        assert count1 == count2 == count3, "File enumeration not deterministic"
        assert count1 > 0, "No Python files found in agentic_core"

    def test_layer_of_path_returns_correct_layer(self):
        """Test layer_of_path returns correct layer numbers."""
        # Test each layer
        for layer in range(7):
            files = enumerate_layer_files(layer)
            if files:
                result = layer_of_path(files[0])
                assert result == layer, f"Expected layer {layer}, got {result}"

    def test_layer_of_path_returns_none_for_non_layer(self):
        """Test layer_of_path returns None for non-layer paths."""
        utils_path = AGENTIC_CORE_ROOT / "utils" / "some_file.py"
        assert layer_of_path(utils_path) is None

        config_path = AGENTIC_CORE_ROOT / "config" / "some_file.py"
        assert layer_of_path(config_path) is None

    def test_classify_file_identifies_utils(self):
        """Test classify_file correctly identifies utils files."""
        utils_path = AGENTIC_CORE_ROOT / "utils" / "test.py"
        result = classify_file(utils_path)
        assert result["is_utils"] is True
        assert result["layer"] is None

    def test_classify_file_identifies_layer_files(self):
        """Test classify_file correctly identifies layer files."""
        for layer in range(7):
            files = enumerate_layer_files(layer)
            if files:
                result = classify_file(files[0])
                assert result["layer"] == layer

    def test_all_layer_directories_have_files(self):
        """Assert all layer directories contain Python files."""
        for layer in range(7):
            files = enumerate_layer_files(layer)
            assert len(files) > 0, f"Layer L{layer} has no Python files"

    def test_enumerate_python_files_is_sorted(self):
        """Assert enumeration returns sorted paths."""
        files = enumerate_python_files()
        assert files == sorted(files), "File enumeration not sorted"

    def test_inventory_summary(self):
        """Print inventory summary for evidence."""
        layers = discover_layers()
        all_files = enumerate_python_files()

        print("\n=== LAYER INVENTORY SUMMARY ===")
        print(f"Total layers discovered: {len(layers)}")
        print(f"Layers: {layers}")
        print(f"Total Python files in agentic_core: {len(all_files)}")

        for layer in layers:
            layer_files = enumerate_layer_files(layer)
            print(f"  L{layer}: {len(layer_files)} files")

        # Count non-layer files
        non_layer_files = [f for f in all_files if layer_of_path(f) is None]
        print(f"  Non-layer (utils/config/etc): {len(non_layer_files)} files")

        # This test always passes - it's for evidence output
        assert True
