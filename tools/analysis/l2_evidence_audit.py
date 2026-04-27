"""L2 Coverage-Matrix Evidence Audit.

Surfaces seven classes of weak evidence the matrix builder masks:

    G1  shared-evidence collisions — N rows latch onto same file:line
    G2  generic-identifier matches — identifier too short or stop-listed
    G3  FAIL_CLOSED rows with no test evidence
    G4  TEST rows whose named function is missing
    G5  STATE rows without a legal-transition test
    G6  SPAN rows registered but never emitted (no producer in code)
    G7  DOC_ONLY rows that should bind to code (OWNERSHIP_NEG, etc.)

Output: docs/reference/04_L2_Execute/EVIDENCE_AUDIT.md.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.analysis.l2_coverage_matrix import (  # noqa: E402
    CODE_DIR,
    SPEC_DIR,
    _code_files,
    _dominant_ident,
    _test_files,
    extract_requirements,
    map_evidence,
    search_literal,
)

OUT_PATH = SPEC_DIR / "EVIDENCE_AUDIT.md"

_GENERIC_TOKENS = frozenset({
    "must", "should", "shall", "True", "False", "None", "class", "self",
    "type", "name", "data", "value", "args", "kwargs", "test", "tests",
    "case", "result", "input", "output", "with", "from", "into", "kind",
    "items", "execution", "Execute", "execute", "phase", "stage", "step",
    "Step", "ITEM", "ITEMS",
})

_BUILTIN_LIKE = frozenset({
    "list", "dict", "tuple", "set", "frozenset", "str", "int", "float",
    "bool", "bytes", "object", "property", "callable", "Callable",
    "Sequence", "Mapping", "Iterable", "Optional", "Union", "Any",
    "TypeVar", "TypedDict", "Enum", "dataclass", "field", "frozen",
})


def _is_generic(needle: str) -> bool:
    if not needle or len(needle) <= 4:
        return True
    if needle in _GENERIC_TOKENS or needle in _BUILTIN_LIKE:
        return True
    if needle.islower() and "_" not in needle and len(needle) <= 7:
        return True
    return False


def _evidence_lines(req) -> list[str]:
    return list(req.code_evidence) + list(req.test_evidence)


def _short(s: str, n: int = 90) -> str:
    s = s.replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def main() -> int:
    code = _code_files()
    tests = _test_files()
    spec_files = sorted(SPEC_DIR.glob("*.md"))
    spec_files = [
        p for p in spec_files
        if p.name not in {"COVERAGE_MATRIX.md", "EVIDENCE_AUDIT.md", "MANIFEST.md"}
    ]

    all_reqs = []
    for sp in spec_files:
        for r in extract_requirements(sp):
            map_evidence(r, code, tests)
            all_reqs.append(r)
    print(f"[evidence-audit] total reqs: {len(all_reqs)}")

    # G1: shared evidence — a single line "covers" many reqs
    line_to_reqs: dict[str, list[str]] = defaultdict(list)
    for r in all_reqs:
        for ln in _evidence_lines(r):
            line_to_reqs[ln].append(r.req_id)
    G1 = sorted(
        ((ln, ids) for ln, ids in line_to_reqs.items() if len(ids) >= 5),
        key=lambda x: -len(x[1]),
    )

    # G2: generic-identifier PASS rows
    G2: list[tuple[str, str, str]] = []
    for r in all_reqs:
        if r.runtime_status != "PASS":
            continue
        if r.kind in {"TEST", "SPAN"}:
            continue  # those rely on full literal names, low risk
        ident = _dominant_ident(r.text)
        if _is_generic(ident):
            G2.append((r.req_id, ident or "(none)", _short(r.text)))

    # G3: FAIL_CLOSED rows with no test evidence
    G3: list[tuple[str, str]] = []
    for r in all_reqs:
        if r.kind != "FAIL_CLOSED":
            continue
        if not r.test_evidence:
            G3.append((r.req_id, _short(r.text)))

    # G4: TEST rows that are UNMAPPED (named function not found)
    G4: list[tuple[str, str]] = []
    for r in all_reqs:
        if r.kind == "TEST" and r.runtime_status == "UNMAPPED":
            G4.append((r.req_id, _short(r.text)))

    # G5: STATE rows without test evidence containing the state name
    G5: list[tuple[str, str]] = []
    for r in all_reqs:
        if r.kind != "STATE":
            continue
        if not r.test_evidence:
            G5.append((r.req_id, _short(r.text)))

    # G6: SPAN rows registered in `l2_spans.py` vocabulary but never
    # emitted by a producer. Reported directly by the matrix as
    # runtime_status = SHADOW_ONLY (see l2_coverage_matrix.py SPAN block).
    # We re-surface the same signal here for backwards-compat consumers
    # that read EVIDENCE_AUDIT.md instead of COVERAGE_MATRIX.md.
    G6: list[tuple[str, str, str]] = []
    import re as _re
    for r in all_reqs:
        if r.kind != "SPAN":
            continue
        if r.runtime_status != "SHADOW_ONLY":
            continue
        m = _re.search(r"[a-z][a-z0-9_\.]+\.[a-z0-9_\.]+", r.text)
        span = m.group(0) if m else ""
        G6.append((r.req_id, span, _short(r.text)))

    # G7: DOC_ONLY rows that look code-bindable
    # OWNERSHIP_NEG and POLICY_DENY both encode invariants that SHOULD have
    # an enforcement gate or guardian assertion in code.
    G7: list[tuple[str, str, str]] = []
    for r in all_reqs:
        if r.runtime_status != "DOC_ONLY":
            continue
        if r.kind not in {"OWNERSHIP_NEG", "POLICY_DENY"}:
            continue
        ident = _dominant_ident(r.text)
        if not ident or _is_generic(ident):
            continue
        # If there's any literal hit at all, flag — matrix should re-route
        hits = search_literal(ident, code, max_hits=1)
        if hits:
            G7.append((r.req_id, ident, _short(r.text)))

    # ------------------------------------------------------------------ writeout
    out: list[str] = []
    out.append("# L2 Coverage Matrix — Evidence Audit\n")
    out.append("Cross-checks every PASS / DOC_ONLY classification in "
               "`COVERAGE_MATRIX.md` against seven weak-evidence patterns. "
               "A flagged row is not necessarily wrong — it is a row whose "
               "PASS verdict the matrix builder cannot defend rigorously.\n")
    out.append("## Summary\n")
    out.append("| Gap class | Count | Severity | Meaning |")
    out.append("|---|---:|:---:|---|")
    out.append(f"| G1 shared-evidence collision | {len(G1)} | medium | one line covers ≥5 reqs |")
    out.append(f"| G2 generic-identifier match | {len(G2)} | high | PASS via stop-listed token |")
    out.append(f"| G3 FAIL_CLOSED no test | {len(G3)} | high | invariant has no exercising test |")
    out.append(f"| G4 TEST function missing | {len(G4)} | high | spec demands a named test, missing |")
    out.append(f"| G5 STATE without test | {len(G5)} | medium | state-machine req has no test binding |")
    out.append(f"| G6 SPAN registered but unemitted | {len(G6)} | medium | declared in registry, no producer |")
    out.append(f"| G7 DOC_ONLY but code-bindable | {len(G7)} | low | matrix downgraded a real binding |")
    out.append("")

    out.append("## G1 — Shared-evidence collisions (≥5 reqs per line)\n")
    if not G1:
        out.append("_None._\n")
    else:
        out.append("| Evidence line | Req count | First few req_ids |")
        out.append("|---|---:|---|")
        for ln, ids in G1[:25]:
            out.append(f"| `{ln}` | {len(ids)} | {', '.join(f'`{i}`' for i in ids[:3])}{', …' if len(ids) > 3 else ''} |")
        if len(G1) > 25:
            out.append(f"\n_Showing first 25 of {len(G1)}._\n")

    out.append("\n## G2 — Generic-identifier PASS matches (high severity)\n")
    if not G2:
        out.append("_None._\n")
    else:
        out.append("| req_id | identifier | bullet |")
        out.append("|---|---|---|")
        for rid, ident, txt in G2[:50]:
            out.append(f"| `{rid}` | `{ident}` | {txt} |")
        if len(G2) > 50:
            out.append(f"\n_Showing first 50 of {len(G2)}._\n")

    out.append("\n## G3 — FAIL_CLOSED requirements without test evidence (high severity)\n")
    if not G3:
        out.append("_None._\n")
    else:
        out.append("| req_id | bullet |")
        out.append("|---|---|")
        for rid, txt in G3[:60]:
            out.append(f"| `{rid}` | {txt} |")
        if len(G3) > 60:
            out.append(f"\n_Showing first 60 of {len(G3)}._\n")

    out.append("\n## G4 — TEST requirements with no matching test function (high severity)\n")
    if not G4:
        out.append("_None._\n")
    else:
        out.append("| req_id | bullet |")
        out.append("|---|---|")
        for rid, txt in G4:
            out.append(f"| `{rid}` | {txt} |")

    out.append("\n## G5 — STATE requirements without test binding (medium severity)\n")
    if not G5:
        out.append("_None._\n")
    else:
        out.append("| req_id | bullet |")
        out.append("|---|---|")
        for rid, txt in G5[:40]:
            out.append(f"| `{rid}` | {txt} |")
        if len(G5) > 40:
            out.append(f"\n_Showing first 40 of {len(G5)}._\n")

    out.append("\n## G6 — OTEL spans registered but never emitted (medium severity)\n")
    if not G6:
        out.append("_None._\n")
    else:
        out.append("| req_id | span | bullet |")
        out.append("|---|---|---|")
        for rid, span, txt in G6:
            out.append(f"| `{rid}` | `{span}` | {txt} |")

    out.append("\n## G7 — DOC_ONLY rows that should bind to code (low severity)\n")
    if not G7:
        out.append("_None._\n")
    else:
        out.append("| req_id | identifier | bullet |")
        out.append("|---|---|---|")
        for rid, ident, txt in G7[:40]:
            out.append(f"| `{rid}` | `{ident}` | {txt} |")
        if len(G7) > 40:
            out.append(f"\n_Showing first 40 of {len(G7)}._\n")

    OUT_PATH.write_text("\n".join(out), encoding="utf-8")
    print(f"[evidence-audit] wrote {OUT_PATH}")
    print(f"[evidence-audit] gap counts: "
          f"G1={len(G1)} G2={len(G2)} G3={len(G3)} G4={len(G4)} "
          f"G5={len(G5)} G6={len(G6)} G7={len(G7)}")
    # Exit 0 always — this is an audit, not a gate (yet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
