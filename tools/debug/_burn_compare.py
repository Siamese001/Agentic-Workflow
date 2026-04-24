import sqlite3
for snap in ["adg_indexed_04242026_0620.sqlite", "adg_indexed_04242026_0618.sqlite"]:
    c = sqlite3.connect(f"artifacts/adg/{snap}")
    print(snap)
    for sev, n in c.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity"):
        print(f"  {sev}: {n}")
    # Also show ratchet mv exemption count
    try:
        row = c.execute("SELECT value FROM meta WHERE key='guardian_exemptions'").fetchone()
        if row:
            print(f"  guardian_exemptions: {row[0]}")
    except sqlite3.OperationalError:
        pass
    c.close()
