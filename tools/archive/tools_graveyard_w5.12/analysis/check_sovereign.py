import ast

fp = r"agentic_core/L2_execution/enforcement/SovereignLLMGateway.py"
src = open(fp, encoding="utf-8").read()
try:
    ast.parse(src)
    print("OK")
# guardian: allow-silent-swallow - acceptable exception handling
except SyntaxError as e:
    print(f"Error: {e}")
    lines = src.splitlines()
    if e.lineno:
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        for i in range(start, end):
            marker = ">>>" if i == e.lineno - 1 else "   "
            print(f"{marker} {i + 1}: {lines[i]}")
