"""Set postgres password and verify connection string used by mcp_config.json."""

import os
import subprocess
from pathlib import Path

PG_BIN = Path(r"C:\Program Files\PostgreSQL\16\bin")
ENV = {**os.environ, "PGPASSWORD": "postgres"}


def run(args, **kwargs):
    # guardian: allow-magic-config
    return subprocess.run(args, capture_output=True, text=True, timeout=15, env=ENV, **kwargs)


# 1. Set password
# guardian: allow-magic-config
r = run(
    [
        str(PG_BIN / "psql.exe"),
        "-U",
        "postgres",
        "-h",
        "localhost",
        "-p",
        "5432",
        "-c",
        "ALTER USER postgres WITH PASSWORD 'postgres';",
    ],
)
print("set password rc:", r.returncode, r.stdout.strip(), r.stderr.strip())

# 2. Show pg_hba.conf auth method
pg_data = Path(r"C:\Program Files\PostgreSQL\16\data")
hba = pg_data / "pg_hba.conf"
if hba.exists():
    lines = [l for l in hba.read_text().splitlines() if l.strip() and not l.startswith("#")]
    print("pg_hba.conf (active lines):")
    for l in lines:
        print(" ", l)

# 3. Verify connection with psycopg2-style URL
# guardian: allow-magic-config
r2 = run(
    [
        str(PG_BIN / "psql.exe"),
        "-U",
        "postgres",
        "-h",
        "localhost",
        "-p",
        "5432",
        "-d",
        "mcp_db",
        "-c",
        "SELECT current_database(), current_user;",
    ],
)
print("verify rc:", r2.returncode, r2.stdout[:200].strip(), r2.stderr.strip())

# 4. Add pg bin to user PATH permanently
import winreg

key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_ALL_ACCESS)
try:
    current_path, _ = winreg.QueryValueEx(key, "PATH")
except FileNotFoundError:    # guardian: File operations should check existence before access
    current_path = ""
pg_bin_str = str(PG_BIN)
if pg_bin_str not in current_path:
    new_path = current_path + ";" + pg_bin_str if current_path else pg_bin_str
    winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
    print(f"Added {pg_bin_str} to user PATH")
else:
    print("pg bin already in PATH")
winreg.CloseKey(key)
print("Done.")
