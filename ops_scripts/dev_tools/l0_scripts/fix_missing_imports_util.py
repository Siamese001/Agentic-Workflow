"""
scripts/fix_missing_imports_util.py
Fix missing SovereignBaseAgent imports
"""
from pathlib import Path


files_to_fix = ['apps_lic/engines/LicReflectionAgent.py', 'apps_lic/engines/LicTemplateOptimizerAgent.py', 'apps_lic/engines/MessageComplianceAgent.py', 'apps_lic/engines/MessageDiversityValidator.py', 'apps_lic/engines/OutreachLearningAgent.py', 'apps_lic/engines/OutreachProactiveAgent.py', 'apps_lic/engines/OutreachSignalRouterAgent.py', 'apps_lic/engines/OutreachValidationExecutorAgent.py', 'apps_lic/engines/k1_routing_agent.py']
for file_path in files_to_fix:
    path = Path(file_path)
    if path.exists():
        content = path.read_text(encoding='utf-8')
        if 'SovereignBaseAgent' not in content and 'from agentic_core.mixins.healer_mixin import HealerMixin' in content:
            content = content.replace('from agentic_core.mixins.healer_mixin import HealerMixin', 'from agentic_core.mixins.healer_mixin import HealerMixin\nfrom agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent')
            path.write_text(content, encoding='utf-8')
            print(f'Fixed: {file_path}')
print('Regenerating certificate...')
import subprocess
import sys

result = subprocess.run([sys.executable, 'scripts/generate_certificate.py'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print('Errors:', result.stderr)
