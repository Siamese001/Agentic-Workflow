"""Diagnose AUDIT_3: which exact violations is the gate matching?"""
import sqlite3, glob, os
latest = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
print(f"Snapshot: {latest}\n")
c = sqlite3.connect(latest)
cur = c.cursor()

PATTERNS = ("NOTION_API_VERSION", "NOTION_BASE", "WAVE_PHASE_DATA_SOURCE_ID",
            "_DATA_SOURCE_ID", "_PAGE_ID", "anthropic.com", "openai.com", "api.notion.com")
SSOT_ALLOWLIST = (
    ".cursor/scripts/_legacy_windsurf/_notion_constants.py",
    "apps_shared/config/environment_config.py",
    "agentic_core/L0_routing/config/path_constants.py",
    "agentic_core/L0_routing/config/external_apis_config.py",
)

seen = set()
print(f"{'pattern':<28} {'file_path':<55} {'line':<6} evidence")
print("-" * 130)
for pat in PATTERNS:
    cur.execute("SELECT file_path, line_no, evidence FROM violations WHERE evidence LIKE ? AND file_path NOT LIKE 'tests/%' AND file_path NOT LIKE 'archives/%' AND file_path NOT LIKE '%scratch%'", (f"%{pat}%",))
    for fp, ln, ev in cur.fetchall():
        if any(fp == ok or fp.endswith("/"+ok) for ok in SSOT_ALLOWLIST):
            continue
        key = (fp, ln, ev)
        if key in seen:
            continue
        seen.add(key)
        print(f"{pat:<28} {fp[:54]:<55} {ln:<6} {(ev or '')[:55]}")

print(f"\nTotal: {len(seen)}")
