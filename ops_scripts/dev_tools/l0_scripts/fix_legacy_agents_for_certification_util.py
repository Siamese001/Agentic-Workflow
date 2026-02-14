"""
scripts/fix_legacy_agents_for_certification_util.py
Fix all legacy agents to inherit from SovereignBaseAgent for final certification
"""

import re
import sys
from pathlib import Path

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent))


def fix_agent_file(file_path: Path) -> bool:
    """Fix a single agent file to use SovereignBaseAgent"""
    try:
        content = file_path.read_text(encoding="utf-8")

        # Skip if already uses SovereignBaseAgent
        if "SovereignBaseAgent" in content:
            print(f"Skipping {file_path}: already uses SovereignBaseAgent")
            return False

        # Skip if not an agent file
        if not any(
            re.search(pattern, content, re.MULTILINE | re.DOTALL)
            for pattern in [r"class\s+\w*Agent", r"class\s+\w*Specialist", r"class\s+\w*Architect"]
        ):
            print(f"Skipping {file_path}: no agent class found")
            return False

        # Check if it uses MCPHardenedMixin
        if "MCPHardenedMixin" not in content:
            print(f"Skipping {file_path}: no MCPHardenedMixin found")
            return False

        print(f"Processing {file_path}: found agent with MCPHardenedMixin")

        # Replace MCPHardenedMixin with SovereignBaseAgent in inheritance
        content = re.sub(
            r"class\s+(\w+(?:Agent|Specialist|Architect))\s*\([^)]*MCPHardenedMixin[^)]*\)",
            lambda m: f"class {m.group(1)}(SovereignBaseAgent)",
            content,
            flags=re.MULTILINE | re.DOTALL,
        )

        # Add SovereignBaseAgent import if not present
        if "SovereignBaseAgent" not in content:
            # Find the imports section and add it
            import_line = "from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent\n"
            # Add after the last import from agentic_core, or after other imports
            if "from agentic_core" in content:
                # Find all agentic_core imports and add after the last one
                agentic_imports = re.findall(r"from agentic_core[^\n]*\n", content)
                if agentic_imports:
                    last_import = agentic_imports[-1]
                    content = content.replace(last_import, last_import + import_line)
                else:
                    # guardian: allow-path-string
                    content = re.sub(r"(from agentic_core.*?\n)", r"\1" + import_line, content, count=1)
            else:
                # Add after other imports
                # guardian: allow-path-string
                content = re.sub(r"(import.*?\n)", r"\1\n" + import_line, content, count=1)

        # Write back
        file_path.write_text(content, encoding="utf-8")
        print(f"Fixed: {file_path}")
        return True

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    print("Fixing legacy agents for certification...")

    # Find all agent files in apps_lic and apps_rg
    domains = ["apps_lic/engines", "apps_rg/engines"]
    fixed_count = 0

    for domain in domains:
        domain_path = Path(domain)
        if not domain_path.exists():
            continue

        for file_path in domain_path.glob("*Agent.py"):
            if fix_agent_file(file_path):
                fixed_count += 1

    print(f"\nFixed {fixed_count} legacy agents")

    # Regenerate certificate
    print("\nRegenerating certificate...")
    import subprocess

    result = subprocess.run(
        [sys.executable, "scripts/generate_certificate.py"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)


if __name__ == "__main__":
    main()
