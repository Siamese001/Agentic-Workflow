"""
Enforcement Sub-Package — Modular structural rule enforcement.

Each module exposes a single `check()` function returning an EnforcementResult.
`_verify.py` orchestrates all modules and emits a unified JSON artifact.

Modules:
    types.py            - Shared result types (EnforcementResult)
    import_graph.py     - Cached import graph builder (shared across rules)
    territory_diff.py   - Layer 1+7: territory auto-diff + strict subfolder enforcement
    leaf_node.py        - Layer 2: root .py prohibition
    volatile_rules.py   - Layer 3: volatile territory safeguards
    mixin_ast.py        - Layer 4: AST-based mixin structural validation
    import_verifier.py  - Layer 5: general import path verification
    blueprint_hash.py   - Layer 6: blueprint immutability hash
    cross_layer.py      - Layer 8: cross-layer import law
"""

from __future__ import annotations
