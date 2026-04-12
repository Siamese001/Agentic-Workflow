import sqlite3

conn = sqlite3.connect("artifacts/adg/adg_indexed_03242026_1825.sqlite")
cursor = conn.cursor()

# Look at actual import statements causing violations
cursor.execute("""
SELECT n1.adg_name as src_module, e.source_file, e.line_no, e.symbol
FROM edges e
JOIN nodes n1 ON e.src_id = n1.id
WHERE e.relation_type = "violates" AND e.edge_kind = "import"
LIMIT 10
""")
violations = cursor.fetchall()

print("Sample violation details:")
for src, file, line, symbol in violations:
    print(f"\n{src}")
    print(f"  File: {file}:{line}")
    print(f"  Symbol: {symbol}")

    # Show the actual import line
    try:
        with open(file, encoding="utf-8") as f:
            lines = f.readlines()
            if line <= len(lines):
                print(f"  Code: {lines[line - 1].strip()}")
    except (ValueError, TypeError, RuntimeError) as e:
        print(f"  Could not read file: {e}")

# Check what layers these imports should go to
print("\n" + "=" * 60)
print("Layer hierarchy check:")
cursor.execute('SELECT DISTINCT adg_name FROM nodes WHERE adg_name LIKE "ADG::Layer::L%" ORDER BY adg_name')
layers = cursor.fetchall()
for layer in layers:
    print(f"  {layer[0]}")

# Check if there are any legitimate runtime imports
print("\n" + "=" * 60)
print("Checking if runtime imports are legitimate...")
sample_file = violations[0][1]
print(f"Examining: {sample_file}")

try:
    with open(sample_file, encoding="utf-8") as f:
        content = f.read()

    # Look for runtime-related imports
    import re

    runtime_imports = re.findall(
        r"from (agentic_core\.runtime\.\w+)|import (agentic_core\.runtime\.\w+)", content
    )
    if runtime_imports:
        print("Runtime imports found:")
        for imp in runtime_imports:
            print(f"  {imp[0] or imp[1]}")
    else:
        print("No obvious runtime imports found")

except (ValueError, TypeError, RuntimeError) as e:
    print(f"Error analyzing file: {e}")

conn.close()
