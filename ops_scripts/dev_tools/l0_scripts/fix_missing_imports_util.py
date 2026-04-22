"""
scripts/fix_missing_imports_util.py
Fix missing SovereignBaseAgent imports
"""

import subprocess
import sys
from pathlib import Path

from tqdm import tqdm


FILES_TO_FIX = [
    "apps_lic/engines/LicReflectionAgent.py",
    "apps_lic/engines/LicTemplateOptimizerAgent.py",
    "apps_lic/engines/MessageComplianceAgent.py",
    "apps_lic/engines/MessageDiversityValidator.py",
    "apps_lic/engines/OutreachLearningAgent.py",
    "apps_lic/engines/OutreachProactiveAgent.py",
    "apps_lic/engines/OutreachSignalRouterAgent.py",
    "apps_lic/engines/OutreachValidationExecutorAgent.py",
    "apps_lic/engines/k1_routing_agent.py",
]


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists():
            return candidate
    return current


def main() -> int:
    project_root = _find_project_root()
    fixed_count = 0

    for file_path in tqdm(FILES_TO_FIX, desc="Processing", unit="item"):
        path = project_root / file_path
        if not path.exists():
            print(f"Skipped missing file: {file_path}")
            continue

        content = path.read_text(encoding="utf-8")
        if (
            "SovereignBaseAgent" not in content
            and "from agentic_core.mixins.healer_mixin import HealerMixin" in content
        ):
            content = content.replace(
                "from agentic_core.mixins.healer_mixin import HealerMixin",
                "from agentic_core.mixins.healer_mixin import HealerMixin\nfrom agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent",
            )
            path.write_text(content, encoding="utf-8")
            fixed_count += 1
            print(f"Fixed: {file_path}")

    print(f"Regenerating certificate after {fixed_count} fixes...")
    certificate_script = project_root / "scripts" / "generate_certificate.py"
    if not certificate_script.exists():
        print(f"Certificate generator not found: {certificate_script}")
        return 1 if fixed_count else 0

    result = subprocess.run(
        [sys.executable, str(certificate_script)],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr, file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
