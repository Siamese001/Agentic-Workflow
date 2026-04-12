import ast
from pathlib import Path

files = [
    "agentic_core/agents/agent_registry.py",
    "agentic_core/agents/types/agent_registry.py",
]

for f in files:
    p = Path(f)
    print(f"\n=== {f} ===")
    print(f"Size: {p.stat().st_size} bytes")

    try:
        content = p.read_text()
        tree = ast.parse(content)

        # Count definitions
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]

        print(f"Classes: {classes}")
        print(f"Functions: {functions[:10]}")  # limit
        print(f"Imports: {len(imports)}")
        print(f"Has re-exports: {'re-export' in content.lower() or 'shim' in content.lower()}")

        # Show first 3 lines
        lines = content.split("\n")[:5]
        print("First 5 lines:")
        for i, line in enumerate(lines, 1):
            print(f"  {i}: {line[:60]}")

    except SyntaxError as e:
        print(f"Syntax error: {e}")
    except Exception as e:
        print(f"Error: {e}")
