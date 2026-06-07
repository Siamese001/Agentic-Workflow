import sqlite3, glob, os
latest = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
c = sqlite3.connect(latest)
cur = c.cursor()
print(f"Snapshot: {latest}\n")
cur.execute("SELECT category, severity, evidence, COUNT(*) FROM violations WHERE disposition='untriaged' GROUP BY category, severity, evidence ORDER BY COUNT(*) DESC LIMIT 20")
print(f"{'category':<20} {'severity':<10} {'evidence':<40} count")
print("-" * 85)
for cat, sev, ev, cnt in cur.fetchall():
    print(f"{cat:<20} {sev:<10} {(ev or '')[:38]:<40} {cnt}")

print()
# Files with most new untriaged
cur.execute("SELECT file_path, COUNT(*) FROM violations WHERE disposition='untriaged' GROUP BY file_path ORDER BY COUNT(*) DESC LIMIT 15")
print("Top files:")
for fp, cnt in cur.fetchall():
    print(f"  {cnt:>4d}  {fp}")

# Specifically check files Wave 2/3 modified
print("\nViolations in Wave 2/3 modified files:")
modified_files = [
    "agentic_core/config/constants_config.py",
    "agentic_core/L0_routing/config/path_constants.py",
    ".claude/governance/scripts/_legacy_windsurf/post_cursor_agent_deferred_scope_capture.py",
    ".claude/governance/scripts/_legacy_windsurf/_notion_constants.py",
]
for f in modified_files:
    cur.execute("SELECT COUNT(*) FROM violations WHERE file_path=? AND disposition='untriaged'", (f,))
    n = cur.fetchone()[0]
    print(f"  {n:>4d}  {f}")
