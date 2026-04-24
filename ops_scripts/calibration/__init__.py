"""Calibration operations scripts (W4 — plan l0-routing-calibration-gap-audit-b3c9d4).

Runtime-side calibration jobs that read the W0 threshold-sweep reports
and compare them against the currently-deployed
``config/routing_thresholds.yaml`` — emitting a drift report that
operators can review before promoting new thresholds.
"""
