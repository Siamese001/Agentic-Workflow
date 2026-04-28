"""Tier 2 OTEL span reference modules.

Static metadata only. These modules declare the canonical span names
that Tier 2 evidence rows reference for the OTEL surface. They do NOT
emit spans, do NOT import an OTEL exporter, and do NOT mutate runtime
state. They exist purely to satisfy the Tier 2 ``OTEL_SPAN_REFERENCES``
mapping with deterministic, lint-stable references.
"""
