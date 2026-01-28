from pathlib import Path

test_file = Path(__file__).resolve()
print(f"This file: {test_file}")
print(f"Parent: {test_file.parent}")
print(f"Parents[0]: {test_file.parents[0]}")
print(f"Parents[1]: {test_file.parents[1]}")

# Simulate the test file location
test_location = Path("c:/Git/Agentic-Workflow/tests/migration/test_map_v2_logic.py")
print(f"\nTest file: {test_location}")
print(f"Resolved: {test_location.resolve()}")
print(f"Parents[0]: {test_location.resolve().parents[0]}")
print(f"Parents[1]: {test_location.resolve().parents[1]}")
print(f"Parents[2]: {test_location.resolve().parents[2]}")

map_file = test_location.resolve().parents[2] / "migration_map_v2.md"
print(f"\nMap file path: {map_file}")
print(f"Map file exists: {map_file.exists()}")

# Check actual location
actual = Path("c:/Git/Agentic-Workflow/migration_map_v2.md")
print(f"\nActual path: {actual}")
print(f"Actual exists: {actual.exists()}")
