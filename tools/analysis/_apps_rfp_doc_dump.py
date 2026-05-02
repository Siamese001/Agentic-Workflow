from pathlib import Path
for f in ["README.md", "RUNBOOK.md", "SLO.md", "SVP_ENGINEERING_REVIEW.md"]:
    p = Path("apps_rfp") / f
    if not p.exists():
        print(f"== MISSING {f} ==")
        continue
    print(f"\n\n========== {f} ({p.stat().st_size}B) ==========")
    print(p.read_text(encoding="utf-8"))
