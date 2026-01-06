import sys
sys.path.insert(0, '.')
from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent

agent = PascalSovereigntyEnforcerAgent(ctx=None, dry_run=True, strict_mode=False, _allow_mock=True)

# Test 3: Dataclass + purge
input_content = """
@dataclass
class HardState:
    id: str
HardState = HardState
"""
expected = """
@dataclass
class HardState:
    id: str
"""
result = agent._purge_snake_case(input_content).strip()

print("=== INPUT ===")
print(repr(input_content))
print("\n=== EXPECTED ===")
print(repr(expected.strip()))
print("\n=== ACTUAL ===")
print(repr(result))
print("\n=== MATCH ===")
print(f"Match: {result == expected.strip()}")
print(f"\nExpected length: {len(expected.strip())}")
print(f"Actual length: {len(result)}")
