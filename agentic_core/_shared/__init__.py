"""Neutral-layer shared types and constants.

This package is the canonical home for type definitions and path constants
that are consumed across multiple architectural layers (L0..L6) and whose
presence in a specific layer would create gravity violations.

Per ADR-081 (L6 Observability Dependency Hygiene), this layer exists to
break the L6 -> L0/L3 import cycles that arose from type modules living
inside L0_routing/types/ and L3_orchestration/types/ being consumed by
L6_observability files for observability-event typing.

Inclusion criteria (enforced via review, no CI gate yet):
- Types (frozen dataclasses, enums, Protocols, TypedDict, NewType)
- Constants (paths, thresholds, well-known strings)
- Pure pydantic-style validators over the above
- NO behavior, NO I/O, NO enforcement, NO business logic
- NO imports from agentic_core.L[0-6]_*

ADG layer classification: this package is classified as ``L_SHARED`` by
``tools/generate/generate_static_adg.py::_infer_layer``. Edges of the form
``L6 -> agentic_core._shared`` are NOT counted as gravity violations.
"""
