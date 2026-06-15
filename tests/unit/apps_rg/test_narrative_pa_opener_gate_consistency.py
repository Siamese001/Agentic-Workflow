"""Prompt↔gate consistency for narrative openers (typed-edge guardrails, W2.3).

A narrative PA prompt MUST NOT *suggest* an opener that the deterministic
``check_narrative_forbidden_opener`` gate forbids. The unify_narrative prompt previously
recommended "Scaled" and "Productized" as substantive openers while the gate's
``EXEC_SUMMARY_MECHANICAL_OPENERS`` set forbids both — so the model followed the prompt and
the lane blocked at X3 on ``x2_unify_narrative_forbidden_opener`` ("Productized"). This guards
the whole class: any future PA prompt that suggests a forbidden opener fails here.
"""
from __future__ import annotations

import re
from pathlib import Path

from apps_rg.runtime.sections import ibm_narrative_pa, unify_narrative_pa
from apps_rg.runtime.validators.narrative_mechanical_x2 import EXEC_SUMMARY_MECHANICAL_OPENERS

_FORBIDDEN = {w.lower() for w in EXEC_SUMMARY_MECHANICAL_OPENERS}


def _suggested_openers(source_text: str) -> set[str]:
    """Capitalized opener words in any 'openers instead:' / 'prefer ...' suggestion clause."""
    suggested: set[str] = set()
    for m in re.finditer(r"(?:openers instead:|prefer)\s*([^.\n]*)", source_text, re.IGNORECASE):
        suggested.update(w.lower() for w in re.findall(r"\b[A-Z][a-z]+\b", m.group(1)))
    return suggested


def test_narrative_pa_prompts_do_not_suggest_forbidden_openers() -> None:
    for module in (unify_narrative_pa, ibm_narrative_pa):
        text = Path(module.__file__).read_text(encoding="utf-8")
        suggested = _suggested_openers(text)
        assert suggested, f"{Path(module.__file__).name}: no suggested-opener clause found"
        bad = sorted(suggested & _FORBIDDEN)
        assert not bad, (
            f"{Path(module.__file__).name} suggests gate-forbidden opener(s): {bad} "
            f"(forbidden set: {sorted(_FORBIDDEN)})"
        )
