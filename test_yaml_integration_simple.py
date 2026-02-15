"""Simple integration test for YAML-backed PromptInjectionLoader."""

import sys
from pathlib import Path

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_yaml_loader_basic_functionality():
    """Test basic YAML loader functionality without complex imports."""

    # Test YAML loader directly
    try:
        from agentic_core.config.core.yaml_injection_loader import YamlInjectionLoader

        # Try to load from actual YAML corpus
        loader = YamlInjectionLoader()

        # This should work if YAML corpus exists
        yaml_files = loader.enumerate_yaml_files()
        print(f"Found {len(yaml_files)} YAML files")

        if yaml_files:
            patterns = loader.load_all_patterns()
            total_patterns = sum(len(p) for p in patterns.values())
            print(f"Loaded {total_patterns} patterns from {len(patterns)} layers")

            # Show a sample pattern
            if patterns:
                first_layer = list(patterns.keys())[0]
                first_pattern = patterns[first_layer][0]
                print(f"Sample pattern: {first_pattern.name} ({first_pattern.layer})")

        print("✓ YAML loader test passed")
        return True

    except Exception as e:
        print(f"✗ YAML loader test failed: {e}")
        return False


def test_prompt_injection_loader_import():
    """Test that PromptInjectionLoader can be imported with YAML support."""

    try:
        # This tests the import chain
        from agentic_core.runtime.config.prompt_injection_loader_config import (
            InjectionConfig,
            PromptInjectionLoader,
        )

        # Test basic instantiation with YAML disabled (should always work)
        config = InjectionConfig(enable_yaml_loader=False)
        loader = PromptInjectionLoader(config)

        print(f"✓ PromptInjectionLoader imported and instantiated with {len(loader.injections)} patterns")
        return True

    except Exception as e:
        print(f"✗ PromptInjectionLoader test failed: {e}")
        return False


def test_yaml_toggle_behavior():
    """Test that YAML toggle doesn't break basic functionality."""

    try:
        from agentic_core.runtime.config.prompt_injection_loader_config import (
            InjectionConfig,
            PromptInjectionLoader,
        )

        # Test with YAML disabled
        config_disabled = InjectionConfig(enable_yaml_loader=False)
        loader_disabled = PromptInjectionLoader(config_disabled)

        # Test with YAML enabled (may fallback to markdown)
        config_enabled = InjectionConfig(enable_yaml_loader=True)
        loader_enabled = PromptInjectionLoader(config_enabled)

        # Both should have patterns
        disabled_count = len(loader_disabled.injections)
        enabled_count = len(loader_enabled.injections)

        print(f"✓ YAML disabled: {disabled_count} patterns")
        print(f"✓ YAML enabled: {enabled_count} patterns")

        # Both should have at least some patterns
        assert disabled_count > 0, "Should have patterns with YAML disabled"
        assert enabled_count > 0, "Should have patterns with YAML enabled"

        return True

    except Exception as e:
        print(f"✗ YAML toggle test failed: {e}")
        return False


if __name__ == "__main__":
    print("Running YAML integration tests...")

    tests = [
        test_yaml_loader_basic_functionality,
        test_prompt_injection_loader_import,
        test_yaml_toggle_behavior,
    ]

    passed = 0
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        if test():
            passed += 1

    print(f"\n{passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("✓ All integration tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
