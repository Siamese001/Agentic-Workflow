#!/usr/bin/env python3
"""Baseline test to verify current OpenTelemetry installation status."""

import sys
import traceback
from pathlib import Path

def test_opentelemetry_availability():
    """Test current OpenTelemetry installation and availability."""
    print("=" * 60)
    print("OPENTELEMETRY BASELINE TEST")
    print("=" * 60)

    results = {}

    # Test 1: Direct import attempts
    print("\n1. Testing direct imports...")
    try:
        import opentelemetry
        results['otel_import'] = True
        print("✅ opentelemetry imported successfully")
        try:
            print(f"   Version: {opentelemetry.__version__}")
        except AttributeError:
            print("   Version: Not available in __version__")
    except ImportError as e:
        results['otel_import'] = False
        print(f"❌ opentelemetry import failed: {e}")

    try:
        from opentelemetry import trace
        results['trace_import'] = True
        print("✅ opentelemetry.trace imported successfully")
    except ImportError as e:
        results['trace_import'] = False
        print(f"❌ opentelemetry.trace import failed: {e}")

    try:
        from opentelemetry.sdk.trace import TracerProvider
        results['sdk_import'] = True
        print("✅ opentelemetry.sdk.trace.TracerProvider imported successfully")
    except ImportError as e:
        results['sdk_import'] = False
        print(f"❌ opentelemetry.sdk.trace.TracerProvider import failed: {e}")

    # Test 2: Test the adapter's OTEL_AVAILABLE flag
    print("\n2. Testing OpenTelemetryTracingAdapter OTEL_AVAILABLE flag...")
    try:
        # Add the project root to sys.path to ensure we can import the module
        project_root = Path(__file__).parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from apps_shared.utils.open_telemetry_tracing_adapter_util import OTEL_AVAILABLE
        results['otel_available_flag'] = OTEL_AVAILABLE
        if OTEL_AVAILABLE:
            print("✅ OTEL_AVAILABLE = True")
        else:
            print("❌ OTEL_AVAILABLE = False - OpenTelemetry not available to adapter")
    except Exception as e:
        results['otel_available_flag'] = f"ERROR: {e}"
        print(f"❌ Failed to check OTEL_AVAILABLE flag: {e}")
        traceback.print_exc()

    # Test 3: Test adapter initialization
    print("\n3. Testing OpenTelemetryTracingAdapter initialization...")
    try:
        from apps_shared.utils.open_telemetry_tracing_adapter_util import OpenTelemetryTracingAdapter
        adapter = OpenTelemetryTracingAdapter(service_name="test-service")
        results['adapter_init'] = True
        results['adapter_enabled'] = adapter.is_enabled()
        print(f"✅ Adapter initialized successfully")
        print(f"   Enabled: {adapter.is_enabled()}")
    except Exception as e:
        results['adapter_init'] = False
        results['adapter_enabled'] = False
        print(f"❌ Adapter initialization failed: {e}")
        traceback.print_exc()

    # Test 4: Test basic tracing functionality
    print("\n4. Testing basic tracing functionality...")
    try:
        from apps_shared.utils.open_telemetry_tracing_adapter_util import OpenTelemetryTracingAdapter
        adapter = OpenTelemetryTracingAdapter(service_name="test-trace")

        # Test context manager
        with adapter.trace_orchestrator("test-mission", {"test": "baseline"}) as span:
            results['tracing_context'] = True
            print("✅ Tracing context manager works")

        # Check if spans were generated
        spans = adapter.drain_completed_spans()
        results['spans_generated'] = len(spans) > 0
        print(f"✅ Generated {len(spans)} spans")

        if spans:
            print(f"   Sample span: {spans[0].get('name', 'unknown')}")
    except Exception as e:
        results['tracing_context'] = False
        results['spans_generated'] = False
        print(f"❌ Basic tracing failed: {e}")
        traceback.print_exc()

    # Test 5: Check installed packages
    print("\n5. Checking installed packages...")
    try:
        import pkg_resources
        installed_packages = [pkg.project_name for pkg in pkg_resources.working_set]

        otel_packages = [pkg for pkg in installed_packages if 'opentelemetry' in pkg.lower()]
        results['installed_otel_packages'] = otel_packages
        print(f"✅ Found {len(otel_packages)} OpenTelemetry packages:")
        for pkg in sorted(otel_packages):
            print(f"   - {pkg}")
    except Exception as e:
        results['installed_otel_packages'] = f"ERROR: {e}"
        print(f"❌ Failed to check installed packages: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("BASELINE TEST SUMMARY")
    print("=" * 60)

    success_count = sum(1 for v in results.values() if v is True)
    total_tests = len([k for k in results.keys() if not k.endswith('packages')])

    print(f"Tests passed: {success_count}/{total_tests}")

    if results.get('otel_available_flag') is True:
        print("🎉 OpenTelemetry is AVAILABLE and working!")
    else:
        print("🚨 OpenTelemetry is NOT available - this is the critical issue!")

    print(f"\nDetailed results:")
    for key, value in results.items():
        if key == 'installed_otel_packages':
            continue
        status = "✅" if value is True else "❌" if value is False else "⚠️"
        print(f"  {status} {key}: {value}")

    return results

if __name__ == "__main__":
    results = test_opentelemetry_availability()

    # Exit with error code if OpenTelemetry is not available
    if not results.get('otel_available_flag'):
        print("\n🚨 CRITICAL: OpenTelemetry is not available!")
        sys.exit(1)
    else:
        print("\n✅ OpenTelemetry is available!")
        sys.exit(0)
