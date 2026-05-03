"""One-shot: append Wave 5 closeout note to the duplication report.

Plan: apps-cross-app-precursors-c94c71 Wave 5.
"""
from pathlib import Path

CLOSEOUT = """
## Wave 5 Closeout (no-op)

Wave 5 of plan `apps-cross-app-precursors-c94c71` is gated on the Wave 1
verdict above. **All 4 families DIVERGE.** No chassis extraction to
`apps_common/` is justified by the evidence; the wave closes with zero code
changes. The 4 duplicated-surface families remain per-app, by design,
because their per-app divergence is load-bearing domain logic (not copy-paste
drift).

Wave 5 success criterion becomes: "Wave 1 verdict consulted; no extraction
performed because no family met the PASS rule."
"""


def main() -> int:
    p = Path("docs/reports/apps_common_duplication_report.md")
    text = p.read_text(encoding="utf-8")
    if "Wave 5 Closeout" in text:
        print("closeout already present; nothing to do")
        return 0
    p.write_text(text + CLOSEOUT, encoding="utf-8")
    print(f"appended Wave 5 closeout to {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
