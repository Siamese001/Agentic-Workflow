"""Tier 3 Runtime Gates cluster static reference modules.

Each sibling module declares the static gate contract for one Tier 3
Runtime Gates row:
  - STEP1_REQ_ID
  - EXPECTED_FAIL_REASON
  - GATE_RANGE or GATE_FAMILY
  - GATE_IDS (tuple)
  - SPAN_NAMES (tuple)
  - NEGATIVE_CONTROL_NAME
  - REQUIRED_ARTIFACT_FIELDS (tuple)
  - validate_gate_contract(payload) -> (bool, list[str])

Static metadata only. No runtime services, no tool execution, no OTEL
emission, no OTEL exporter import, no runtime state mutation.
"""
