# Test the validator's whitelist check logic
content = """import time

# Search for the current price of Bitcoin
search_query = "current price of Bitcoin"
search_result = search_web(search_query)

# Log the result
print(f"Search Query: {search_query}")
print(f"Search Result: {search_result}")
"""

allowed_tools = {"search_web", "print"}
has_imports = False
uses_only_allowed = True

print("Testing whitelist check...")
print(f"Content:\n{content}\n")

# Simple parsing to detect imports and function calls
for line in content.split('\n'):
    line = line.strip()
    print(f"Line: {line}")
    if line.startswith('import ') or line.startswith('from '):
        # Has imports - needs full validation
        has_imports = True
        print("  -> Has import, needs full validation")
        break
    elif '(' in line and ')' in line and not line.startswith('#'):
        # Extract function name before first parenthesis
        # Skip variable assignments (contains '=' before function name)
        if '=' not in line.split('(')[0]:
            func_name = line.split('(')[0].strip().split()[-1]
            print(f"  -> Function call: {func_name}")
            if func_name and func_name.isidentifier() and func_name not in allowed_tools:
                uses_only_allowed = False
                print(f"  -> NOT ALLOWED: {func_name}")
                break

print(f"\nResults:")
print(f"has_imports: {has_imports}")
print(f"uses_only_allowed: {uses_only_allowed}")
print(f"Should skip validation: {not has_imports and uses_only_allowed}")
