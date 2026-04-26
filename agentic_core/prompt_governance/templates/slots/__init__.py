"""Jinja slot templates for 10-slot prompt assembly.

Each template corresponds to one slot in the Zero-Loss Taxonomy:

  S0 — SYSTEM/STATE       (ABSOLUTE authority)
  D0 — INJECTIONS/FENCES   (BINDING authority)
  I0 — INSTRUCTIONAL       (GOVERNED authority)
  E0 — EXEMPLARS           (GUIDING authority)
  C0 — GROUNDED CONTEXT    (INFORMATIONAL authority)
  M0 — META-COGNITIVE      (PRIVATE authority)
  U0 — USER PROMPT         (ZERO authority)
  H0 — HEALING PROPOSAL    (PROPOSED authority)
  Y0 — SYNTHESIS           (ANALYTIC authority)
  R0 — OUTPUT FORMAT       (SCHEMA authority)

Load via ``TemplateRegistry.get_slot_template(slot_key)`` or read directly.
Render via ``jinja2.Template(content).render(**variables)``.
"""

import pathlib

_SLOT_DIR = pathlib.Path(__file__).parent

_SLOT_TEMPLATE_MAP = {
    "S0": "S0_system_state.jinja",
    "D0": "D0_injections.jinja",
    "I0": "I0_instructional.jinja",
    "E0": "E0_exemplars.jinja",
    "C0": "C0_grounded_context.jinja",
    "M0": "M0_meta_cognitive.jinja",
    "U0": "U0_user_prompt.jinja",
    "H0": "H0_healing_proposal.jinja",
    "Y0": "Y0_synthesis.jinja",
    "R0": "R0_output_format.jinja",
}

__all__ = ["_SLOT_DIR", "_SLOT_TEMPLATE_MAP"]
