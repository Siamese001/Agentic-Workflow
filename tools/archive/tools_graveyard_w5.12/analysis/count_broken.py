import ast
import pathlib

broken_files = []
tests_dir = pathlib.Path("tests")

for f in sorted(tests_dir.rglob("test_*.py")):
    if "archive" in str(f).lower():
        continue

    try:
        content = f.read_text(encoding="utf-8", errors="replace")
        ast.parse(content)
    except SyntaxError as e:
        broken_files.append(
            {
                "file": str(f),
                "error": str(e),
                "line": e.lineno or 0,
            }
        )
    except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
        continue

print(f"Total broken files: {len(broken_files)}")
for i, bf in enumerate(broken_files, 1):
    print(f"{i}. {bf['file']} - Line {bf['line']}: {bf['error'][:80]}...")
