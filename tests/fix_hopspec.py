import re

# Read the test file
with open('tests/integration/test_hardened_orchestrator_comprehensive.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all HopSpec instantiations with name= to use script= and description=
# Pattern: HopSpec(id="...", name="...")
content = re.sub(
    r'HopSpec\(id="([^"]+)", name="([^"]+)"',
    r'HopSpec(id="\1", script="test_script.py", description="\2"',
    content
)

# Pattern: HopSpec(id=f"...", name=f"...")
content = re.sub(
    r'HopSpec\(id=f"([^"]+)", name=f"([^"]+)"',
    r'HopSpec(id=f"\1", script="test_script.py", description=f"\2"',
    content
)

# Write back
with open('tests/integration/test_hardened_orchestrator_comprehensive.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all HopSpec instantiations")
