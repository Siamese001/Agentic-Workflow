"""Tier 3 non-RuntimeGates subsystem reference modules.

Each sibling module declares the static contract for one batch of
Tier 3 non-RuntimeGates rows:
  - l0_l1_u0_refs: Batch 1 (7 rows)
  - c0_pa_exit_refs: Batch 2 (5 rows)
  - l5_l6_uwg_e2e_refs: Batch 3 (5 rows)

Static metadata only. No runtime services, no tool execution, no OTEL
emission, no OTEL exporter import, no runtime state mutation.
"""
