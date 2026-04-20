"""Verify postgres connection string used by mcp_config.json works via psycopg2."""

import subprocess
import sys

# guardian: allow-magic-config
CONN = "postgresql://postgres:postgres@localhost:5432/mcp_db"

# Try psycopg2 first
try:
    import psycopg2

    conn = psycopg2.connect(CONN)
    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user, version();")
    row = cur.fetchone()
    print(f"psycopg2 OK: db={row[0]} user={row[1]}")
    print(f"  version: {row[2][:60]}")
    conn.close()
except ImportError:  # guardian: allow-silent-swallow - optional dependency
    print("psycopg2 not installed - installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
    import psycopg2

    conn = psycopg2.connect(CONN)
    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user;")
    row = cur.fetchone()
    print(f"psycopg2 OK (after install): db={row[0]} user={row[1]}")
    conn.close()
except Exception as e:  # guardian: allow-silent-swallow
    print(f"psycopg2 FAIL: {e}")

# Test npx postgres MCP server can reach the DB by checking node-postgres via node
node_test = """
const { Client } = require('pg');
const c = new Client({ connectionString: 'postgresql://postgres:postgres@localhost:5432/mcp_db' });
c.connect().then(() => c.query('SELECT current_database()').then(r => {
  console.log('node-postgres OK: db=' + r.rows[0].current_database);
  c.end();
})).catch(e => { console.log('node-postgres FAIL: ' + e.message); process.exit(1); });
"""
# Write temp js file
import tempfile

with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
    f.write(node_test)
    tmp = f.name

# guardian: allow-magic-config
r = subprocess.run(["node", "-e", node_test], capture_output=True, text=True, timeout=10)
print(f"node-postgres rc={r.returncode}: {r.stdout.strip() or r.stderr.strip()[:200]}")
