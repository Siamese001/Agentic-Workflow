"""Run AST audit only - no purge, no tests."""
from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent

agent = PascalSovereigntyEnforcerAgent(ctx=None, dry_run=True, _allow_mock=True)
audit = agent._ast_audit()

print("=" * 70)
print("ULTRA AST AUDIT RESULTS")
print("=" * 70)
print(f"Files with snake_case: {len(audit['files'])}")
print(f"Snake_case classes: {audit['snake_classes']}")
print(f"Backward-compat aliases: {audit['aliases']}")
print()
print(f"Summary: {audit['summary']}")
print()

# Show first 30 files
print("Sample files:")
for f in audit['files'][:30]:
    print(f"  - {f}")
if len(audit['files']) > 30:
    print(f"  ... and {len(audit['files']) - 30} more")
