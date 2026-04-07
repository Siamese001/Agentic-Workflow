"""Query ADG for antipattern breakdown."""

import sqlite3
from pathlib import Path

adg_dir = Path("artifacts") / "adg"
dbs = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
if not dbs:
    print("No ADG SQLite found")
    raise SystemExit(1)
db = dbs[-1]
print(f"Using: {db}")

conn = sqlite3.connect(db)
cur = conn.cursor()

print("\n=== Antipattern edge_kind breakdown ===")
cur.execute(
    "SELECT edge_kind, COUNT(*) FROM edges WHERE relation_type='antipattern' "
    "GROUP BY edge_kind ORDER BY COUNT(*) DESC",
)
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\n=== Antipattern symbol breakdown (top 30) ===")
cur.execute(
    "SELECT symbol, COUNT(*) FROM edges WHERE relation_type='antipattern' "
    "GROUP BY symbol ORDER BY COUNT(*) DESC LIMIT 30",
)
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\n=== 'except Exception' broad catches (not detected by scanner) ===")
print("  Searching codebase for 'except Exception' patterns...")

# Count how many except Exception patterns exist in real source (non-archive, non-backup)
import ast
import pathlib

repo = pathlib.Path(".")
broad_catches = []
log_and_swallow = []
return_none_swallow = []

BROAD_TYPES = {"Exception", "BaseException"}

for pyfile in sorted(repo.rglob("*.py")):
    rel = str(pyfile).replace("\\", "/")
    # Skip archives, backups, .git
    if any(skip in rel for skip in ["archives/", ".healing_backups/", ".backup/", ".git/", "__pycache__"]):
        continue
    try:
        source = pyfile.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(pyfile))
    except (SyntaxError, OSError):    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling
        continue

    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        # Get exception type name
        exc_name = ""
        if node.type is None:
            exc_name = "bare"
        elif isinstance(node.type, ast.Name):
            exc_name = node.type.id
        elif isinstance(node.type, ast.Attribute):
            exc_name = node.type.attr

        if exc_name in BROAD_TYPES:
            broad_catches.append((rel, node.lineno, exc_name))

            # Check if body has re-raise
            has_raise = False
            has_log_only = False
            has_return_none = False
            body = node.body
            for stmt in body:
                if isinstance(stmt, ast.Raise):
                    has_raise = True
                    break

            if not has_raise:
                # Check for log-and-swallow (body has only logging calls, no raise)
                all_logging = True
                for stmt in body:
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                        sym = ""
                        func = stmt.value.func
                        if isinstance(func, ast.Attribute):
                            sym = func.attr
                        elif isinstance(func, ast.Name):
                            sym = func.id
                        if sym in (
                            "debug",
                            "info",
                            "warning",
                            "error",
                            "critical",
                            "exception",
                            "warn",
                            "log",
                            "print",
                        ):
                            continue
                    elif isinstance(stmt, ast.Pass):
                        continue
                    all_logging = False
                    break

                if all_logging and body:
                    log_and_swallow.append((rel, node.lineno, exc_name))

                # Check for return None swallow
                if len(body) == 1:
                    stmt = body[0]
                    if isinstance(stmt, ast.Return):
                        if stmt.value is None:
                            return_none_swallow.append((rel, node.lineno, "return (bare)"))
                        elif isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
                            return_none_swallow.append((rel, node.lineno, "return None"))
                        elif isinstance(stmt.value, ast.Constant) and stmt.value.value in (
                            "",
                            [],
                            {},
                            0,
                            False,
                        ):
                            return_none_swallow.append((rel, node.lineno, f"return {stmt.value.value!r}"))
                        elif isinstance(stmt.value, (ast.List, ast.Dict, ast.Set, ast.Tuple)):
                            if not (stmt.value.elts if hasattr(stmt.value, "elts") else stmt.value.keys):
                                return_none_swallow.append((rel, node.lineno, "return empty_collection"))

print(f"\n  Total 'except Exception/BaseException' (broad catches): {len(broad_catches)}")
print(f"  Of those, log-and-swallow (no re-raise, only logging): {len(log_and_swallow)}")
print(f"  Of those, return-None/empty swallow: {len(return_none_swallow)}")

if log_and_swallow:
    print("\n  === Top log-and-swallow sites (first 20) ===")
    for f, line, exc in log_and_swallow[:20]:
        print(f"    {f}:{line} except {exc}")

if return_none_swallow:
    print("\n  === Top return-None swallow sites (first 20) ===")
    for f, line, kind in return_none_swallow[:20]:
        print(f"    {f}:{line} {kind}")

# Count bare except (no type specified)
bare_count = sum(1 for f, l, e in broad_catches if False)  # already tracked above
cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='antipattern' AND symbol LIKE 'except:bare'")
bare_detected = cur.fetchone()[0]
print(f"\n  Bare except detected by scanner: {bare_detected}")

# Check how many broad 'except Exception' are NOT detected by scanner
cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='antipattern' AND symbol LIKE 'except:Exception'")
exception_detected = cur.fetchone()[0]
print(f"  'except Exception' silent swallows detected by scanner: {exception_detected}")
print(f"  'except Exception' TOTAL in codebase: {len([x for x in broad_catches if x[2] == 'Exception'])}")
print(
    f"  GAP (broad catches NOT detected): {len([x for x in broad_catches if x[2] == 'Exception']) - exception_detected}",
)

conn.close()
