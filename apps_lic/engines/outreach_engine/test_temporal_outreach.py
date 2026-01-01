"""
Phase 2: Test L4 Temporal Layer with Outreach Engine
Tests the temporal compliance gate and governed outreach sequence
"""
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
Logger = logging.getLogger("TemporalOutreachTest")


def test_temporal_vetting():
    """Test the temporal vetting function"""
    Logger.info("\n=== Testing Temporal Vetting (L4) ===")

    try:
        from action_registry import ActionRegistry
        from temporal_vetting import vet_lead_optimal_time

        registry = ActionRegistry()
        tools = registry.get_tool_map()

        # Test cases with different timezones
        test_cases = [
            ("America/New_York", "14:00", True),   # Should be 10:00 AM (SEND)
            ("Asia/Shanghai", "14:00", False),    # Should be 10:00 PM (DELAY)
            ("Europe/London", "14:00", True),     # Should be 2:00 PM (SEND)
            ("Australia/Sydney", "14:00", False),  # Should be 1:00 AM (DELAY)
        ]

        all_passed = True

        for tz, utc_time, expected_send in test_cases:
            result = vet_lead_optimal_time(tz, utc_time, tools, Logger)
            actual_send = result['send_now']

            if actual_send == expected_send:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
                all_passed = False

            Logger.info(
                f"{status} {tz}: UTC {utc_time} -> Local {result['lead_local_time']} -> {result['decision']}")

        if all_passed:
            Logger.info("✅ Temporal vetting works correctly")
            return True
        else:
            Logger.error("❌ Temporal vetting has issues")
            return False

    except Exception as e:
        Logger.error(f"❌ Temporal vetting test failed: {e}")
        return False


def test_governed_outreach():
    """Test the governed outreach sequence"""
    Logger.info("\n=== Testing Governed Outreach Sequence ===")

    try:
        from action_registry import ActionRegistry
        from governed_outreach import execute_governed_outreach_sequence

        registry = ActionRegistry()
        tools = registry.get_tool_map()

        # Mock get_current_time to return a fixed time for testing
        original_get_time = tools.get('get_current_time')

        def mock_get_current_time(timezone="UTC"):
            # Return 14:00 UTC (10:00 AM New York) for consistent testing
            return "2025-12-15T14:00:00Z"

        # Replace the tool temporarily
        tools['get_current_time'] = mock_get_current_time

        try:
            # Test case 1: Should send (business hours)
            result1 = execute_governed_outreach_sequence(
                lead_timezone="America/New_York",
                pitch_content="Test outreach message",
                recipient_email="test@example.com",
                tools=tools,
                Logger=Logger
            )

            if result1['status'] == "SENT_COMPLIANT":
                Logger.info(
                    "✅ Test 1 PASSED: Email sent during business hours")
            else:
                Logger.error(
                    f"❌ Test 1 FAILED: Expected SENT_COMPLIANT, got {result1['status']}")

            # Test case 2: Should delay (off hours)
            result2 = execute_governed_outreach_sequence(
                lead_timezone="Asia/Shanghai",
                pitch_content="Test outreach message",
                recipient_email="test@example.com",
                tools=tools,
                Logger=Logger
            )

            if result2['status'] == "TEMPORAL_DELAY":
                Logger.info("✅ Test 2 PASSED: Email delayed for off-hours")
                Logger.info(
                    f"   Next optimal send time: {result2.get('next_optimal_send_time', 'N/A')}")
            else:
                Logger.error(
                    f"❌ Test 2 FAILED: Expected TEMPORAL_DELAY, got {result2['status']}")

        finally:
            # Restore original tool
            if original_get_time:
                tools['get_current_time'] = original_get_time

        # Overall result
        if (result1['status'] == "SENT_COMPLIANT" and
                result2['status'] == "TEMPORAL_DELAY"):
            Logger.info("✅ Governed outreach sequence works correctly")
            return True
        else:
            Logger.error("❌ Governed outreach sequence has issues")
            return False

    except Exception as e:
        Logger.error(f"❌ Governed outreach test failed: {e}")
        return False


def test_time_bound_benchmarking():
    """Test time-bound salary benchmarking"""
    Logger.info("\n=== Testing Time-Bound Salary Benchmarking ===")

    try:
        from action_registry import ActionRegistry
        from time_bound_benchmarking import execute_time_bound_salary_benchmarking

        registry = ActionRegistry()
        tools = registry.get_tool_map()

        # Test salary benchmarking
        result = execute_time_bound_salary_benchmarking(
            job_title="Software Engineer",
            location="San Francisco",
            tools=tools,
            Logger=Logger
        )

        if result['status'] == "success":
            Logger.info("✅ Salary benchmarking completed")
            Logger.info(f"   Salary data: {result.get('salary_data', 'N/A')}")
            Logger.info(f"   Source: {result.get('source', 'N/A')}")
            Logger.info(
                f"   Time window: {result.get('time_window_start', 'N/A')}")
            return True
        else:
            Logger.error(
                f"❌ Salary benchmarking failed: {result.get('message', 'Unknown error')}")
            return False

    except Exception as e:
        Logger.error(f"❌ Time-bound benchmarking test failed: {e}")
        return False


def main():
    """Run all L4 Temporal Layer tests"""
    Logger.info("="*60)
    Logger.info("PHASE 2: L4 TEMPORAL LAYER TESTING")
    Logger.info("="*60)

    results = []

    # Run tests
    results.append(("Temporal Vetting", test_temporal_vetting()))
    results.append(("Governed Outreach", test_governed_outreach()))
    results.append(("Time-Bound Benchmarking", test_time_bound_benchmarking()))

    # Summary
    Logger.info("\n" + "="*60)
    Logger.info("PHASE 2 TEST SUMMARY")
    Logger.info("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        Logger.info(f"{name}: {status}")

    Logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        Logger.info("\n🎉 L4 Temporal Layer is fully functional!")
        Logger.info("   - Temporal compliance gate working")
        Logger.info("   - Governed outreach sequence operational")
        Logger.info("   - Time-bound salary benchmarking active")
        return True
    else:
        Logger.error(f"\n💥 {total - passed} component(s) need attention")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)