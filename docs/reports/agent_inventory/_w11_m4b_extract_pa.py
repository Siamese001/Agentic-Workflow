#!/usr/bin/env python3
"""W11-M4B — copy dispatch *_pa.py to sections/ and leave dispatch shims."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PA_FILES = [
    "headline_pa.py",
    "competencies_pa.py",
    "ibm_bullets_pa.py",
    "ibm_narrative_pa.py",
    "unify_bullets_pa.py",
    "unify_narrative_pa.py",
    "executive_summary_pa.py",
]
SECTION_PA_MODULES = [p.replace(".py", "") for p in PA_FILES]


def _rewrite_imports(text: str) -> str:
    for mod in SECTION_PA_MODULES:
        text = text.replace(
            f"apps_rg.runtime.dispatch.{mod}",
            f"apps_rg.runtime.sections.{mod}",
        )
    return text


def _add_ssot_marker(text: str, sym: str) -> str:
    marker = f"W11-M4B SSOT: apps_rg.runtime.sections.{sym}."
    if marker in text:
        return text
    if text.startswith('"""'):
        end = text.find('"""', 3)
        if end != -1:
            old_doc = text[3:end]
            new_doc = old_doc.rstrip() + f"\n\n{marker}"
            return f'"""{new_doc}"""' + text[end + 3 :]
    return f'"""{marker}"""\n\n' + text


def main() -> None:
    for name in PA_FILES:
        src = REPO / "apps_rg/runtime/dispatch" / name
        sym = name.replace(".py", "")
        dst = REPO / "apps_rg/runtime/sections" / name
        text = _rewrite_imports(src.read_text(encoding="utf-8"))
        if "Compatibility re-export" in text[:80]:
            raise RuntimeError(f"dispatch {name} already shimmed; restore full module first")
        text = _add_ssot_marker(text, sym)
        dst.write_text(text, encoding="utf-8")
        compile_fns = re.findall(r"^def (compile_\w+)", text, re.M)
        shim = [
            f'"""Compatibility re-export — SSOT: apps_rg.runtime.sections.{sym}."""',
            "",
        ]
        for fn in compile_fns:
            shim.append(f"from apps_rg.runtime.sections.{sym} import {fn}")
        shim.append("")
        shim.append(f"__all__ = {compile_fns!r}")
        shim.append("")
        src.write_text("\n".join(shim), encoding="utf-8")
        print(name, "->", dst.relative_to(REPO))


if __name__ == "__main__":
    main()
