"""Cross-layer integrated-runtime entry points (W2+).

This package hosts production entry points that compose intake → L1 →
L0 → Exit. Harnesses (probes, tests, certification scripts) MUST call
only these entry points; they MUST NOT reach into individual layers.
"""
