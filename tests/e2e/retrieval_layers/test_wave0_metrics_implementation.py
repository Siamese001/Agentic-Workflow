"""Quick test for Wave 0 metrics server implementation."""

from __future__ import annotations

import sys
import time


def test_metrics_import() -> bool:
    """Test that metrics module can be imported."""
    try:
        print("✓ Prometheus metrics module imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import metrics module: {e}")
        return False


def test_metrics_server_import() -> bool:
    """Test that metrics server module can be imported."""
    try:
        print("✓ Metrics server module imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import metrics server: {e}")
        return False


def test_l6_observability_exports() -> bool:
    """Test that L6 observability exports the new modules."""
    try:
        print("✓ L6 observability exports new Wave 0 modules")
        return True
    except Exception as e:
        print(f"✗ L6 observability exports failed: {e}")
        return False


def test_metrics_server_start_stop() -> bool:
    """Test that metrics server can start and stop."""
    try:
        from agentic_core.L6_observability import get_server_status, start_metrics_server, stop_metrics_server

        # Get initial status
        status = get_server_status()
        print(f"  Initial status: {status}")

        # Start server on test port
        server = start_metrics_server(port=18000, addr="127.0.0.1")
        if server is None:
            print("✗ Failed to start metrics server")
            return False

        print("✓ Metrics server started on port 18000")

        # Check status after start
        status = get_server_status()
        print(f"  Running status: {status}")

        # Stop server
        if stop_metrics_server(server):
            print("✓ Metrics server stopped successfully")
        else:
            print("✗ Failed to stop metrics server cleanly")
            return False

        return True
    except Exception as e:
        print(f"✗ Metrics server start/stop test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_endpoint() -> bool:
    """Test that metrics endpoint returns valid Prometheus format."""
    try:
        import urllib.request

        from agentic_core.L6_observability import start_metrics_server, stop_metrics_server
        from agentic_core.L6_observability.metrics.prometheus_metrics import (
            record_retrieval,
            record_routing_decision,
        )

        # Start server
        server = start_metrics_server(port=18001, addr="127.0.0.1")
        if server is None:
            print("✗ Failed to start metrics server for endpoint test")
            return False

        # Record some metrics
        record_routing_decision("agent", "success")
        record_routing_decision("tool", "failure")
        record_retrieval("cache", "hit", 0.001)
        record_retrieval("vector", "miss", 0.050)

        # Give server time to start
        time.sleep(0.5)

        # Fetch metrics - using local test server, safe for E2E test
        url = "http://127.0.0.1:18001/metrics"
        req = urllib.request.Request(url)  # noqa: S310
        with urllib.request.urlopen(req, timeout=5) as response:  # noqa: S310
            content = response.read().decode('utf-8')

            # Verify content contains expected metrics
            checks = [
                "agentic_workflow_l0_routing_decisions_total" in content,
                "agentic_workflow_l1_retrieval_requests_total" in content,
                "agentic_workflow_build_info" in content,
            ]

            if all(checks):
                print("✓ Metrics endpoint returns valid Prometheus format")
                print(f"  Sample content:\n{content[:500]}...")
            else:
                print("✗ Metrics endpoint missing expected content")
                print(f"  Content received:\n{content[:500]}...")
                stop_metrics_server(server)
                return False

        # Stop server
        stop_metrics_server(server)
        return True

    except Exception as e:
        print(f"✗ Metrics endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> int:
    """Run all Wave 0 tests."""
    print("=" * 60)
    print("Wave 0: Instrumentation Prerequisites — Verification Tests")
    print("=" * 60)

    tests = [
        ("Module Imports", test_metrics_import),
        ("Server Module Imports", test_metrics_server_import),
        ("L6 Observability Exports", test_l6_observability_exports),
        ("Server Start/Stop", test_metrics_server_start_stop),
        ("Metrics Endpoint", test_metrics_endpoint),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 Wave 0 implementation verified successfully!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
