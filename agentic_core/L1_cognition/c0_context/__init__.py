"""C0 Context Engine — full implementation of the C0 spec.

Spec: ``docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md``

Submodules:
    types          — enums, dataclasses, closed vocabularies (every C0 named constant)
    safety         — invariants C0.I1..C0.I12, quality gates C0.G0..C0.G10, failure-mode catalog
    preflight      — C0.0 grounding eligibility + C0.1 retrieval plan builder
    shape_and_scan — C0.4 dedupe/rerank/stratify/compress + C0.4A contradiction/gap scan
    contract       — C0.5 verify + 11-dimension score + status decision
    refine         — C0.6 refinement loop with allowed/disallowed enforcement
"""
