"""
Unified Dashboard Test Suite
============================

This package contains all dashboard-related tests, consolidated from
the previous scattered test phases.

Test Modules:
- test_telemetry.py      - Phase 1-2: Telemetry and runtime state tests
- test_frontend.py       - Phase 3-4: Frontend component tests
- test_ui_layout.py      - Phase 5: UI layout and styling tests
- test_integration.py    - Phase 6: Integration tests
- test_documentation.py  - Phase 7: Documentation tests
- test_e2e.py            - End-to-end dashboard tests

Usage:
    pytest tests/dashboard/                    # Run all dashboard tests
    pytest tests/dashboard/test_telemetry.py  # Run specific test module
    pytest tests/dashboard/ -k "telemetry"    # Run tests matching pattern
"""
