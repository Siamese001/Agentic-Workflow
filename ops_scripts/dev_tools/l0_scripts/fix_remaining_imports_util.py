"\nFix remaining imports\n"

files = [
    "apps_lic/engines/MessageDiversityValidator.py",
    "apps_lic/engines/OutreachLearningAgent.py",
    "apps_lic/engines/OutreachProactiveAgent.py",
    "apps_lic/engines/OutreachSignalRouterAgent.py",
    "apps_lic/engines/OutreachValidationExecutorAgent.py",
    "apps_lic/engines/k1_routing_agent.py",
]
from pathlib import Path

for file_path in files:
    path = Path(file_path)
    if path.exists():
        content = path.read_text(encoding="utf-8")
        lines = content.split("\n")
        first_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                first_import_idx = i
                break
        lines.insert(
            first_import_idx, "from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent"
        )
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Fixed: {file_path}")
print("Done")
