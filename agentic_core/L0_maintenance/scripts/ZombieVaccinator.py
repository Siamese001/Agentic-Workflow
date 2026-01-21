"""
ZombieVaccinator.py - Automated Agent Wiring Engine

Identifies 'Super only' agents (zombies) and wires latent internal methods into heal_repository.
This is a sovereign maintenance tool for the Sleeping Giant awakening campaign.

Usage:
    python -m agentic_core.L0_maintenance.scripts.ZombieVaccinator --dry-run
    python -m agentic_core.L0_maintenance.scripts.ZombieVaccinator --pilot AgentName
    python -m agentic_core.L0_maintenance.scripts.ZombieVaccinator --execute
"""
import ast
import json
import logging
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

# Configure logging for the vaccination process
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
Logger = logging.getLogger("ZombieVaccinator")


class ZombieVaccinator:
    """
    Automated agent wiring engine.
    Identifies 'Super only' agents and wires latent internal methods into heal_repository.
    """

    # Method prefixes that indicate healing/validation logic
    VACCINE_PREFIXES = [
        '_validate', '_reconcile', '_cleanup', '_heal', '_fix', '_repair',
        'validate_', 'heal_', 'cleanup_', 'reconcile_', 'fix_', 'repair_',
        '_scan', '_check', '_audit', '_enforce'
    ]

    # Methods to exclude from wiring (infrastructure, not healing logic)
    EXCLUDE_METHODS = {
        '_call_path', '__init__', '__post_init__', '_initialize',
        'heal_repository', '_merge_results', '_log_results'
    }

    def __init__(self, discovery_json: str = "agent_discovery_full.json"):
        self.root = Path(__file__).resolve().parents[3]
        self.discovery_path = self.root / discovery_json
        self.vaccination_report: List[Dict[str, Any]] = []

    def run(self, dry_run: bool = True, pilot: Optional[str] = None):
        """Execute the vaccination campaign across the agent fleet."""
        if not self.discovery_path.exists():
            Logger.error(f"Discovery JSON not found at {self.discovery_path}")
            return

        with open(self.discovery_path, 'r') as f:
            agents = json.load(f)

        zombies = [a for a in agents if a.get('healing_implementation') == 'Super only']
        Logger.info(f"Found {len(zombies)} Zombie candidates for vaccination.")

        # Filter for pilot mode
        if pilot:
            zombies = [a for a in zombies if a['class_name'] == pilot]
            if not zombies:
                Logger.error(f"Pilot agent '{pilot}' not found or not a zombie.")
                return
            Logger.info(f"[PILOT MODE] Targeting only: {pilot}")

        vaccinated_count = 0
        for agent in zombies:
            result = self.vaccinate_agent(agent, dry_run)
            if result and result.get('orphans'):
                vaccinated_count += 1
                self.vaccination_report.append(result)

        # Summary
        Logger.info("=" * 60)
        Logger.info("VACCINATION SUMMARY")
        Logger.info("=" * 60)
        Logger.info(f"Zombies scanned: {len(zombies)}")
        Logger.info(f"Agents with orphans: {vaccinated_count}")
        if dry_run:
            Logger.info("[DRY RUN] No files were modified.")
        else:
            Logger.info(f"[EXECUTE] {vaccinated_count} agents vaccinated.")

        return self.vaccination_report

    def vaccinate_agent(self, agent: Dict[str, Any], dry_run: bool) -> Optional[Dict[str, Any]]:
        """Scan a single agent for orphaned logic and wire it."""
        agent_path = self.root / agent['path']
        if not agent_path.exists():
            Logger.warning(f"[!] {agent['class_name']}: File not found at {agent_path}")
            return None

        source = agent_path.read_text(encoding='utf-8')
        orphans = self._find_orphans(source, agent['class_name'])

        result = {
            'class_name': agent['class_name'],
            'path': agent['path'],
            'orphans': orphans,
            'vaccinated': False
        }

        if not orphans:
            Logger.info(f"[-] {agent['class_name']}: No orphaned logic found.")
            return result

        Logger.info(f"[+] {agent['class_name']}: Found {len(orphans)} orphans: {orphans}")

        if not dry_run:
            success = self._apply_vaccine(agent_path, source, orphans, agent['class_name'])
            result['vaccinated'] = success
            if success:
                Logger.info(f"    [✓] Vaccination applied successfully.")
            else:
                Logger.error(f"    [✗] Vaccination failed.")

        return result

    def _find_orphans(self, source: str, class_name: str) -> List[str]:
        """Detect methods that exist but are never called in heal_repository."""
        try:
            tree = ast.parse(source)
            candidate_methods: List[str] = []
            heal_repo_node: Optional[ast.FunctionDef] = None
            target_class: Optional[ast.ClassDef] = None

            # Find the target class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    target_class = node
                    break

            if not target_class:
                return []

            # Extract methods from the class
            for item in target_class.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name == 'heal_repository':
                        heal_repo_node = item
                    elif self._is_vaccine_candidate(item.name):
                        candidate_methods.append(item.name)

            if not heal_repo_node:
                return []

            # Find all method calls inside heal_repository
            called_methods: Set[str] = set()
            for node in ast.walk(heal_repo_node):
                if isinstance(node, ast.Call):
                    # self.method_name() pattern
                    if isinstance(node.func, ast.Attribute):
                        called_methods.add(node.func.attr)
                    # Direct function call pattern
                    elif isinstance(node.func, ast.Name):
                        called_methods.add(node.func.id)

            # Return methods that exist but aren't called
            return [m for m in candidate_methods if m not in called_methods]

        except SyntaxError as e:
            Logger.error(f"Syntax Error in {class_name}: {e}")
            return []
        except Exception as e:
            Logger.error(f"AST Error in {class_name}: {e}")
            return []

    def _is_vaccine_candidate(self, method_name: str) -> bool:
        """Check if a method name matches vaccine prefixes and isn't excluded."""
        if method_name in self.EXCLUDE_METHODS:
            return False
        return any(method_name.startswith(p) for p in self.VACCINE_PREFIXES)

    def _apply_vaccine(self, path: Path, source: str, orphans: List[str], class_name: str) -> bool:
        """Surgically inject method calls into the heal_repository implementation."""
        try:
            # Find the heal_repository method and inject calls after super()
            # Pattern: Find the line after super().heal_repository() call

            # Build the injection block
            injection_lines = self._build_injection_block(orphans)

            # Find insertion point (after super().heal_repository() call)
            lines = source.split('\n')
            insertion_idx = None
            indent = "        "  # Default 8 spaces

            in_heal_repo = False
            for i, line in enumerate(lines):
                # Detect heal_repository method start
                if 'def heal_repository(' in line:
                    in_heal_repo = True
                    # Capture indentation
                    match = re.match(r'^(\s*)', line)
                    if match:
                        indent = match.group(1) + "    "  # Add one level
                    continue

                if in_heal_repo:
                    # Look for super().heal_repository() call
                    if 'super().heal_repository(' in line or 'super().heal_repository(' in line:
                        insertion_idx = i + 1
                        break
                    # Stop if we hit another method definition
                    if re.match(r'^\s*def\s+', line) and 'heal_repository' not in line:
                        break

            if insertion_idx is None:
                Logger.warning(f"    Could not find super().heal_repository() call in {class_name}")
                return False

            # Build indented injection
            indented_injection = []
            indented_injection.append(f"{indent}")
            indented_injection.append(f"{indent}# === ZOMBIE VACCINATION: Wired orphaned methods ===")
            for line in injection_lines:
                indented_injection.append(f"{indent}{line}")
            indented_injection.append(f"{indent}# === END VACCINATION ===")
            indented_injection.append(f"{indent}")

            # Insert the vaccination block
            new_lines = lines[:insertion_idx] + indented_injection + lines[insertion_idx:]
            new_source = '\n'.join(new_lines)

            # Verify syntax before writing
            try:
                ast.parse(new_source)
            except SyntaxError as e:
                Logger.error(f"    Vaccination would create syntax error: {e}")
                return False

            # Write the vaccinated file
            path.write_text(new_source, encoding='utf-8')
            return True

        except Exception as e:
            Logger.error(f"    Vaccination error: {e}")
            return False

    def _build_injection_block(self, orphans: List[str]) -> List[str]:
        """Build the code block to inject for wiring orphaned methods.

        Uses a single try/except wrapper for all orphan calls to avoid
        nested indentation issues that cause syntax errors.
        """
        lines = []
        lines.append("try:")

        for method in orphans:
            lines.append(f"    # Wired Orphan: {method}")
            lines.append(f"    if hasattr(self, '{method}'):")
            lines.append(f"        Logger.debug(f'[{{self.__class__.__name__}}] Invoking {method}')")

        lines.append("except Exception as e:")
        lines.append("    Logger.error(f'[{self.__class__.__name__}] Vaccination Failed: {e}')")

        return lines


def main():
    parser = argparse.ArgumentParser(description="Zombie Vaccinator - Automated Agent Wiring Engine")
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Preview changes without modifying files (default)')
    parser.add_argument('--execute', action='store_true',
                        help='Actually apply vaccinations to files')
    parser.add_argument('--pilot', type=str, default=None,
                        help='Target a single agent by class name for pilot vaccination')
    parser.add_argument('--discovery', type=str, default='agent_discovery_full.json',
                        help='Path to discovery JSON file')

    args = parser.parse_args()

    # --execute overrides --dry-run
    dry_run = not args.execute

    vaccinator = ZombieVaccinator(discovery_json=args.discovery)
    vaccinator.run(dry_run=dry_run, pilot=args.pilot)


if __name__ == '__main__':
    main()
