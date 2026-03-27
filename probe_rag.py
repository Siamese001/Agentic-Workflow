from pathlib import Path
from agentic_core.knowledge.engine.rag_orchestrator import SovereignRagOrchestrator

# Test 1: Happy path
print("=== HAPPY PATH TEST ===")
p = Path('test_happy.txt')
p.write_text('test content')
o = SovereignRagOrchestrator(Path.cwd())
result = o.ingest(p)
print(f"Result: {result[:50] if result else 'None'}")
p.unlink()

# Test 2: Failure path - nonexistent file
print("\n=== FAILURE PATH TEST ===")
p2 = Path('nonexistent.txt')
try:
    o.ingest(p2)
    print("ERROR: Should have failed")
except (FileNotFoundError, ValueError) as e:
    print(f"PASS: Correctly failed with {type(e).__name__}")

# Test 3: Edge case - empty file
print("\n=== EDGE CASE TEST ===")
p3 = Path('test_empty.txt')
p3.write_text('')
result2 = o.ingest(p3)
print(f"Empty file result: {result2}")
p3.unlink()
