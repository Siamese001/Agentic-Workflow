"""L5 Governance & Safety v4/v5 — engines spec'd in
``docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md`` and ``v5.md``.

This subpackage is intentionally thin. Each engine is a leaf module so that
upstream import shims and lazy-loading paths can pick exactly what they need
without dragging the whole governance plane into a test context.
"""
