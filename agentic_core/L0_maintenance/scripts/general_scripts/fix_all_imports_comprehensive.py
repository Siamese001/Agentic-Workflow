"""
scripts/fix_all_imports_comprehensive.py
Fix all missing SovereignBaseAgent imports
"""

from pathlib import Path

files_to_fix = [
    "apps_lic/engines/LicTemplateOptimizerAgent.py",
    "apps_lic/engines/MessageComplianceAgent.py",
    "apps_lic/engines/MessageDiversityValidator.py",
    "apps_lic/engines/OutreachLearningAgent.py",
    "apps_lic/engines/OutreachProactiveAgent.py",
    "apps_lic/engines/OutreachSignalRouterAgent.py",
    "apps_lic/engines/OutreachValidationExecutorAgent.py",
    "apps_lic/engines/k1_routing_agent.py",
]

for file_path in files_to_fix:
    path = Path(file_path)
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if "SovereignBaseAgent" not in content:
            # Find the last import line and add after it
            lines = content.split("\n")
            import_lines = []
            other_lines = []
            in_imports = True

            for line in lines:
                if line.startswith("from ") or line.startswith("import "):
                    import_lines.append(line)
                else:
                    if in_imports and line.strip() and not line.startswith("#"):
                        in_imports = False
                    if not in_imports:
                        other_lines.append(line)
                    else:
                        import_lines.append(line)

            # Add the import
            import_lines.append("from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent")

            # Reconstruct
            new_content = "\n".join(import_lines + other_lines)
            path.write_text(new_content, encoding="utf-8")
            print(f"Fixed: {file_path}")

print("Regenerating certificate...")
import subprocess
import sys

result = subprocess.run([sys.executable, "scripts/generate_certificate.py"], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)
