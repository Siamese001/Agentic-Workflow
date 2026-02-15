"""Minimal integration test for YAML functionality without complex imports."""

import sys
from pathlib import Path

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_yaml_loader_standalone():
    """Test YAML loader as a standalone component."""

    try:
        from agentic_core.config.core.yaml_injection_loader import YamlInjectionLoader

        loader = YamlInjectionLoader()
        patterns = loader.load_all_patterns()

        total_patterns = sum(len(p) for p in patterns.values())

        print(f"✓ YAML loader: {total_patterns} patterns from {len(patterns)} layers")

        # Verify we have patterns from different layers
        expected_layers = ["framing", "safety", "reasoning", "tooling", "output", "context"]
        found_layers = [layer for layer in expected_layers if layer in patterns and patterns[layer]]

        print(f"✓ Found patterns from layers: {found_layers}")

        # Test layer filtering
        if "framing" in patterns and patterns["framing"]:
            framing_patterns = loader.load_by_layer("framing")
            print(f"✓ Layer filtering: {len(framing_patterns)} framing patterns")

        return True

    except Exception as e:
        print(f"✗ YAML loader test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_yaml_pattern_structure():
    """Test that loaded patterns have correct structure."""

    try:
        from agentic_core.config.core.injection_layer_config import InstructionalPattern
        from agentic_core.config.core.yaml_injection_loader import YamlInjectionLoader

        loader = YamlInjectionLoader()
        patterns = loader.load_all_patterns()

        # Find a pattern to inspect
        test_pattern = None
        for layer_patterns in patterns.values():
            if layer_patterns:
                test_pattern = layer_patterns[0]
                break

        if test_pattern:
            assert isinstance(test_pattern, InstructionalPattern)
            assert hasattr(test_pattern, "id")
            assert hasattr(test_pattern, "name")
            assert hasattr(test_pattern, "layer")
            assert hasattr(test_pattern, "description")
            assert hasattr(test_pattern, "template")
            assert isinstance(test_pattern.id, int)
            assert isinstance(test_pattern.name, str)
            assert isinstance(test_pattern.template, str)

            print(f"✓ Pattern structure validated: {test_pattern.name}")
            return True
        else:
            print("✗ No patterns found to validate structure")
            return False

    except Exception as e:
        print(f"✗ Pattern structure test failed: {e}")
        return False


def test_yaml_error_handling():
    """Test YAML loader error handling."""

    try:
        from tempfile import NamedTemporaryFile

        from agentic_core.config.core.yaml_injection_loader import YamlInjectionLoader, YamlValidationError

        # Test with invalid YAML
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            invalid_file = f.name

        try:
            loader = YamlInjectionLoader(Path(invalid_file).parent)
            loader.load_all_patterns()
            print("✗ Should have raised validation error")
            return False
        except YamlValidationError as e:
            print(f"✓ YAML validation error handled correctly: {e}")
            return True
        finally:
            import os

            os.unlink(invalid_file)

    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False


if __name__ == "__main__":
    print("Running YAML standalone integration tests...")

    tests = [
        test_yaml_loader_standalone,
        test_yaml_pattern_structure,
        test_yaml_error_handling,
    ]

    passed = 0
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        if test():
            passed += 1

    print(f"\n{passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("✓ All YAML integration tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
